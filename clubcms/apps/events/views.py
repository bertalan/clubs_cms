"""
Views for the events app.

Provides Django views for non-HTML endpoints (JSON APIs, ICS exports,
payment webhooks/callbacks).  HTML views have been migrated to
EventsAreaPage (RoutablePageMixin in apps.website.models.pages).
"""

import hashlib
import hmac
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt

try:
    import stripe as stripe_lib
except ImportError:
    stripe_lib = None

from apps.events.models import EventFavorite, EventRegistration
from apps.events.utils import generate_ics, generate_single_ics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper: load EventDetailPage without a hard import
# ---------------------------------------------------------------------------


def _get_event_page(pk):
    """
    Load an EventDetailPage by PK.

    Uses a lazy import to avoid circular dependencies.
    """
    from wagtail.models import Page

    page = get_object_or_404(Page.objects.specific(), pk=pk)
    # Verify the page is actually an EventDetailPage
    from apps.website.models.pages import EventDetailPage

    if not isinstance(page, EventDetailPage):
        raise Http404
    return page


# ---------------------------------------------------------------------------
# ToggleFavoriteView — AJAX POST to add/remove favorite
# ---------------------------------------------------------------------------

class ToggleFavoriteView(LoginRequiredMixin, View):
    """
    Toggle an event as favorite for the authenticated user.

    Accepts only POST requests.  Returns JSON with the new state.
    Includes a server-side debounce (1 second) to prevent spamming.
    """

    def post(self, request, event_pk):
        # Server-side debounce: 1 second between toggles (cache-based)
        cache_key = f"toggle_fav_{request.user.pk}"
        if cache.get(cache_key):
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse(
                    {"error": _("Please wait before toggling again.")},
                    status=429,
                )
            return redirect(request.META.get("HTTP_REFERER", "/"))
        cache.set(cache_key, True, 1)

        event_page = _get_event_page(event_pk)

        favorite, created = EventFavorite.objects.get_or_create(
            user=request.user,
            event=event_page,
        )

        if not created:
            favorite.delete()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"favorited": created, "event_pk": event_pk})

        return redirect(request.META.get("HTTP_REFERER", event_page.url))


# ---------------------------------------------------------------------------
# 7. EventICSView — export single event as ICS
# ---------------------------------------------------------------------------


class EventICSView(View):
    """Export a single event as an ICS file download."""

    def get(self, request, event_pk):
        event_page = _get_event_page(event_pk)

        if not event_page.start_date:
            raise Http404

        ics_content = generate_single_ics(event_page)
        response = HttpResponse(ics_content, content_type="text/calendar")
        date_prefix = event_page.start_date.strftime("%Y-%m-%d")
        slug = slugify(event_page.title)[:60]
        filename = f"{date_prefix}-{slug}.ics"
        response["Content-Disposition"] = (
            f'attachment; filename="{filename}"'
        )
        return response


# ---------------------------------------------------------------------------
# 8. MyEventsICSView — export all favorites as ICS feed (token auth)
# ---------------------------------------------------------------------------


def _generate_user_token(user):
    """
    Generate a token for ICS feed authentication.

    Uses HMAC-SHA256 of user PK with SECRET_KEY so the token is
    stable but not guessable.
    """
    secret = getattr(settings, "SECRET_KEY", "")
    return hmac.new(
        secret.encode(),
        str(user.pk).encode(),
        hashlib.sha256,
    ).hexdigest()[:32]


class MyEventsICSView(View):
    """
    Export all of a user's favorite events as an ICS calendar feed.

    Authentication is via a token query parameter so that calendar
    apps can subscribe without a session cookie.

    Usage: /events/my-events/calendar.ics?uid=<user_pk>&token=<token>
    """

    def get(self, request):
        # Authenticate via token
        uid = request.GET.get("uid")
        token = request.GET.get("token")

        if not uid or not token:
            # Fall back to session auth
            if not request.user.is_authenticated:
                raise Http404
            user = request.user
        else:
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(pk=uid)
            except (User.DoesNotExist, ValueError):
                raise Http404

            expected_token = _generate_user_token(user)
            if not hmac.compare_digest(token, expected_token):
                raise Http404

        # Get all favorite events for this user
        favorites = (
            EventFavorite.objects.filter(user=user)
            .select_related("event")
            .order_by("event__start_date")
        )
        events = [fav.event for fav in favorites if fav.event.start_date]

        ics_content = generate_ics(events)
        response = HttpResponse(ics_content, content_type="text/calendar")
        response["Content-Disposition"] = 'inline; filename="my-events.ics"'
        return response


# ---------------------------------------------------------------------------
# 9. AllEventsICSView — public calendar feed with all upcoming events
# ---------------------------------------------------------------------------


class AllEventsICSView(View):
    """
    Public ICS feed of all upcoming events.

    No authentication required — only exposes public event data.
    """

    def get(self, request):
        from apps.website.models.pages import EventDetailPage

        events = (
            EventDetailPage.objects.live()
            .public()
            .filter(start_date__gte=timezone.now())
            .order_by("start_date")
        )

        cal_name = str(_("All Upcoming Events"))
        ics_content = generate_ics(events, cal_name=cal_name)
        response = HttpResponse(ics_content, content_type="text/calendar")
        response["Content-Disposition"] = 'inline; filename="events.ics"'
        return response


# ---------------------------------------------------------------------------
# StripeWebhookView — handle Stripe webhook events
# ---------------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Handle Stripe webhook events.

    Verifies the webhook signature and processes checkout.session.completed
    events to mark registrations as paid.
    """

    def post(self, request):
        from apps.website.models.settings import PaymentSettings
        from wagtail.models import Site

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            return HttpResponse(status=400)

        payment_settings = PaymentSettings.for_site(site)

        if not payment_settings.stripe_webhook_secret:
            return HttpResponse(status=400)

        try:
            event = stripe_lib.Webhook.construct_event(
                payload, sig_header, payment_settings.stripe_webhook_secret
            )
        except (ValueError, stripe_lib.error.SignatureVerificationError):
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            session_id = session["id"]

            try:
                registration = EventRegistration.objects.get(
                    payment_session_id=session_id,
                    payment_provider="stripe",
                )
                if registration.payment_status != "paid":
                    registration.payment_status = "paid"
                    registration.payment_id = session.get("payment_intent", "")
                    registration.save(
                        update_fields=["payment_status", "payment_id"]
                    )
            except EventRegistration.DoesNotExist:
                logger.warning(
                    "Stripe webhook: no registration found for session %s",
                    session_id,
                )

        return HttpResponse(status=200)


# ---------------------------------------------------------------------------
# 13. PayPalReturnView — handle PayPal redirect after approval
# ---------------------------------------------------------------------------


class PayPalReturnView(LoginRequiredMixin, View):
    """
    Handle PayPal return after user approves the order.

    Captures the PayPal order and redirects to EventsAreaPage
    on success, or payment cancel on failure.
    """

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        from apps.events.utils import events_area_url

        if registration.payment_status == "paid":
            return redirect(events_area_url("payment_success", args=[pk]))

        if (
            registration.payment_provider != "paypal"
            or not registration.payment_session_id
        ):
            return redirect(events_area_url("payment_cancel", args=[pk]))

        from apps.events.payment import capture_paypal_order
        from apps.website.models.settings import PaymentSettings

        payment_settings = PaymentSettings.for_request(request)

        try:
            capture_result = capture_paypal_order(
                registration.payment_session_id, payment_settings
            )
            if capture_result["status"] == "COMPLETED":
                registration.payment_status = "paid"
                registration.payment_id = capture_result["id"]
                registration.save(
                    update_fields=["payment_status", "payment_id"]
                )
                return redirect(
                    events_area_url("payment_success", args=[pk])
                )
        except Exception:
            logger.exception(
                "PayPal capture failed for registration %s", pk
            )

        return redirect(events_area_url("payment_cancel", args=[pk]))

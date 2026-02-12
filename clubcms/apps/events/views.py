"""
Views for the events app.

Provides class-based views for event registration, cancellation,
user registration lists, favorites management, and ICS calendar
export.
"""

import hashlib
import hmac
import logging

from datetime import timedelta

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db import transaction
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DetailView, ListView

try:
    import stripe as stripe_lib
except ImportError:
    stripe_lib = None

from apps.events.forms import EventRegistrationForm, GuestRegistrationForm
from apps.events.models import EventFavorite, EventRegistration
from apps.events.utils import (
    calculate_price,
    generate_ics,
    generate_single_ics,
    promote_from_waitlist,
)

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
# 1. EventRegisterView — POST-based event registration
# ---------------------------------------------------------------------------


class EventRegisterView(CreateView):
    """
    Handle event registration for both authenticated and guest users.

    GET:  display the registration form with pricing info.
    POST: validate and create the EventRegistration record.
    """

    template_name = "events/register.html"

    def dispatch(self, request, *args, **kwargs):
        self.event_page = _get_event_page(kwargs["event_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.request.user.is_authenticated:
            return EventRegistrationForm
        return GuestRegistrationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["event_page"] = self.event_page
        kwargs["user"] = (
            self.request.user if self.request.user.is_authenticated else None
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.event_page
        user = (
            self.request.user if self.request.user.is_authenticated else None
        )
        context["pricing"] = calculate_price(self.event_page, user=user)
        return context

    def form_valid(self, form):
        event = self.event_page

        # Validate registration is open
        if not getattr(event, "is_registration_open", False):
            form.add_error(None, _("Registration is not open for this event."))
            return self.form_invalid(form)

        # Check deadline (uses computed_deadline which includes PricingTier deadlines)
        deadline = getattr(event, "computed_deadline", None) or event.registration_deadline
        if deadline and timezone.now() > deadline:
            form.add_error(None, _("The registration deadline has passed."))
            return self.form_invalid(form)

        # Check member permissions for authenticated users
        user = self.request.user if self.request.user.is_authenticated else None
        if user and hasattr(user, "can_register_events"):
            if not user.can_register_events:
                form.add_error(
                    None,
                    _(
                        "Your membership does not include event registration. "
                        "Please upgrade your membership."
                    ),
                )
                return self.form_invalid(form)

        # Check for duplicate registration
        if user:
            existing = EventRegistration.objects.filter(
                event=event,
                user=user,
                status__in=["registered", "confirmed", "waitlist"],
            ).exists()
            if existing:
                form.add_error(
                    None,
                    _("You are already registered for this event."),
                )
                return self.form_invalid(form)

        # Calculate payment amount
        pricing = calculate_price(event, user=user)
        payment_amount = pricing["final_price"]

        # Determine status based on capacity (atomic to prevent race conditions)
        max_attendees = event.max_attendees or 0
        registration = form.save(commit=False)
        registration.event = event
        registration.payment_amount = payment_amount

        if user:
            registration.user = user

        # Free events skip payment
        if payment_amount <= 0:
            registration.payment_status = "paid"
            registration.payment_provider = "free"

        with transaction.atomic():
            if max_attendees > 0:
                confirmed_count = (
                    EventRegistration.objects.select_for_update()
                    .filter(
                        event=event,
                        status__in=["registered", "confirmed"],
                    )
                    .count()
                )
                if confirmed_count >= max_attendees:
                    registration.status = "waitlist"
                else:
                    registration.status = "registered"
            else:
                registration.status = "registered"

            registration.save()

        # Redirect to payment choice for paid events
        if payment_amount > 0 and user:
            return redirect(reverse("events:payment_choice", args=[registration.pk]))

        if user:
            return redirect(reverse("events:my_registrations"))
        return redirect(event.url)

    def get_success_url(self):
        return reverse("events:my_registrations")


# ---------------------------------------------------------------------------
# 2. EventCancelView — cancel own registration
# ---------------------------------------------------------------------------


class EventCancelView(LoginRequiredMixin, View):
    """
    Cancel an authenticated user's own event registration.

    Only allows cancellation of registrations in 'registered',
    'confirmed', or 'waitlist' status, and only before the event
    start date.
    """

    def post(self, request, pk):
        registration = get_object_or_404(
            EventRegistration,
            pk=pk,
            user=request.user,
        )

        if registration.status == "cancelled":
            return redirect(reverse("events:my_registrations"))

        # Don't allow cancellation of past events
        if (
            registration.event.start_date
            and registration.event.start_date < timezone.now()
        ):
            return redirect(reverse("events:my_registrations"))

        was_active = registration.status in ("registered", "confirmed")
        registration.status = "cancelled"
        registration.save(update_fields=["status"])

        # Promote from waitlist if a spot opened up
        if was_active:
            promote_from_waitlist(registration.event)

        return redirect(reverse("events:my_registrations"))


# ---------------------------------------------------------------------------
# 3. MyRegistrationsView — list user's registrations
# ---------------------------------------------------------------------------


class MyRegistrationsView(LoginRequiredMixin, ListView):
    """List the logged-in user's event registrations."""

    template_name = "events/my_registrations.html"
    context_object_name = "registrations"
    paginate_by = 20

    def get_queryset(self):
        return (
            EventRegistration.objects.filter(user=self.request.user)
            .select_related("event")
            .order_by("-registered_at")
        )


# ---------------------------------------------------------------------------
# 4. MyEventsView — list user's favorite events (upcoming)
# ---------------------------------------------------------------------------


class MyEventsView(LoginRequiredMixin, ListView):
    """List the logged-in user's favorite events (upcoming only)."""

    template_name = "events/my_events.html"
    context_object_name = "favorites"
    paginate_by = 20

    def get_queryset(self):
        now = timezone.now()
        return (
            EventFavorite.objects.filter(
                user=self.request.user,
                event__start_date__gte=now,
            )
            .select_related("event")
            .order_by("event__start_date")
        )


# ---------------------------------------------------------------------------
# 5. MyEventsArchiveView — past favorites
# ---------------------------------------------------------------------------


class MyEventsArchiveView(LoginRequiredMixin, ListView):
    """List the logged-in user's past favorite events, grouped by year."""

    template_name = "events/my_events_archive.html"
    context_object_name = "favorites"
    paginate_by = 30

    def get_queryset(self):
        now = timezone.now()
        return (
            EventFavorite.objects.filter(
                user=self.request.user,
                event__start_date__lt=now,
            )
            .select_related("event")
            .order_by("-event__start_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Group favorites by year for template display
        grouped = {}
        for fav in context["favorites"]:
            year = fav.event.start_date.year
            grouped.setdefault(year, []).append(fav)
        context["favorites_by_year"] = dict(
            sorted(grouped.items(), reverse=True)
        )
        return context


# ---------------------------------------------------------------------------
# 6. ToggleFavoriteView — AJAX POST to add/remove favorite
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
            return JsonResponse(
                {"error": _("Please wait before toggling again.")},
                status=429,
            )
        cache.set(cache_key, True, 1)

        event_page = _get_event_page(event_pk)

        favorite, created = EventFavorite.objects.get_or_create(
            user=request.user,
            event=event_page,
        )

        if not created:
            favorite.delete()
            return JsonResponse({"favorited": False, "event_pk": event_pk})

        return JsonResponse({"favorited": True, "event_pk": event_pk})


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
        response["Content-Disposition"] = (
            f'attachment; filename="event-{event_pk}.ics"'
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
# 9. PaymentChoiceView — select payment provider
# ---------------------------------------------------------------------------


class PaymentChoiceView(LoginRequiredMixin, View):
    """
    Display available payment providers and process the user's choice.

    GET:  show provider buttons (Stripe, PayPal, Bank Transfer).
    POST: create payment session or set up bank transfer.
    """

    template_name = "events/payment_choice.html"

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        if registration.payment_status == "paid":
            return redirect(reverse("events:my_registrations"))

        from apps.website.models.settings import PaymentSettings

        payment_settings = PaymentSettings.for_request(request)
        return self._render(request, registration, payment_settings)

    def post(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        if registration.payment_status == "paid":
            return redirect(reverse("events:my_registrations"))

        from apps.website.models.settings import PaymentSettings

        payment_settings = PaymentSettings.for_request(request)
        provider = request.POST.get("provider", "")

        if provider == "bank_transfer" and payment_settings.bank_transfer_enabled:
            return self._setup_bank_transfer(request, registration, payment_settings)

        if provider == "stripe" and payment_settings.stripe_enabled:
            return self._setup_stripe(request, registration, payment_settings)

        if provider == "paypal" and payment_settings.paypal_enabled:
            return self._setup_paypal(request, registration, payment_settings)

        # Invalid or unsupported provider — re-render
        return self._render(request, registration, payment_settings)

    def _setup_bank_transfer(self, request, registration, payment_settings):
        """Set up bank transfer payment and redirect to instructions."""
        from apps.events.payment import generate_payment_reference

        now = timezone.now()
        expiry_days = payment_settings.bank_transfer_expiry_days or 5
        expires_at = now + timedelta(days=expiry_days)

        # Ensure payment expires before the event starts
        if registration.event.start_date:
            max_expires = registration.event.start_date - timedelta(days=1)
            if expires_at > max_expires:
                expires_at = max_expires

        registration.payment_provider = "bank_transfer"
        registration.payment_reference = generate_payment_reference(registration)
        registration.payment_expires_at = expires_at
        registration.save(
            update_fields=["payment_provider", "payment_reference", "payment_expires_at"]
        )

        # Send bank transfer instructions notification
        if registration.user:
            try:
                from apps.notifications.services import create_notification

                create_notification(
                    notification_type="payment_instructions",
                    title=str(_("Payment instructions: {event}")).format(
                        event=registration.event.title,
                    ),
                    body=str(
                        _("Please complete the bank transfer of \u20ac{amount} "
                          "with reference {ref} by {expires}.")
                    ).format(
                        amount=registration.payment_amount,
                        ref=registration.payment_reference,
                        expires=registration.payment_expires_at.strftime("%d/%m/%Y"),
                    ),
                    url=reverse("events:bank_transfer_instructions", args=[registration.pk]),
                    recipients=[registration.user],
                    channels=["email"],
                    content_object=registration,
                )
            except Exception:
                pass

        return redirect(
            reverse("events:bank_transfer_instructions", args=[registration.pk])
        )

    def _setup_stripe(self, request, registration, payment_settings):
        """Create Stripe Checkout Session and redirect to Stripe."""
        try:
            from apps.events.payment import create_stripe_checkout_session

            session_url = create_stripe_checkout_session(
                registration, payment_settings, request
            )
            return redirect(session_url)
        except Exception:
            logger.exception(
                "Stripe session creation failed for registration %s",
                registration.pk,
            )
            return self._render(
                request, registration, payment_settings,
                error=_("Payment service temporarily unavailable. Please try again."),
            )

    def _setup_paypal(self, request, registration, payment_settings):
        """Create PayPal order and redirect to PayPal approval."""
        try:
            from apps.events.payment import create_paypal_order

            order_id, approval_url = create_paypal_order(
                registration, payment_settings, request
            )
            return redirect(approval_url)
        except Exception:
            logger.exception(
                "PayPal order creation failed for registration %s",
                registration.pk,
            )
            return self._render(
                request, registration, payment_settings,
                error=_("Payment service temporarily unavailable. Please try again."),
            )

    def _render(self, request, registration, payment_settings, error=None):
        from django.shortcuts import render

        context = {
            "registration": registration,
            "event": registration.event,
            "available_providers": payment_settings.available_providers,
            "payment_settings": payment_settings,
        }
        if error:
            context["error"] = error
        return render(request, self.template_name, context)


# ---------------------------------------------------------------------------
# 10. BankTransferInstructionsView — show IBAN and payment reference
# ---------------------------------------------------------------------------


class BankTransferInstructionsView(LoginRequiredMixin, View):
    """Display bank transfer instructions for a pending registration."""

    template_name = "events/payment_bank_transfer.html"

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        if registration.payment_provider != "bank_transfer":
            return redirect(reverse("events:my_registrations"))

        from apps.website.models.settings import PaymentSettings

        payment_settings = PaymentSettings.for_request(request)

        from django.shortcuts import render

        return render(request, self.template_name, {
            "registration": registration,
            "event": registration.event,
            "payment_settings": payment_settings,
        })


# ---------------------------------------------------------------------------
# 11. PaymentSuccessView / PaymentCancelView — post-payment redirects
# ---------------------------------------------------------------------------


class PaymentSuccessView(LoginRequiredMixin, View):
    """Confirm payment success after Stripe/PayPal redirect."""

    template_name = "events/payment_success.html"

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        # For Stripe: verify via API if webhook hasn't arrived yet
        if (
            registration.payment_provider == "stripe"
            and registration.payment_status != "paid"
            and registration.payment_session_id
        ):
            self._verify_stripe_payment(registration)

        from django.shortcuts import render

        return render(request, self.template_name, {
            "registration": registration,
            "event": registration.event,
            "payment_verified": registration.payment_status == "paid",
        })

    def _verify_stripe_payment(self, registration):
        """Poll Stripe to check if the checkout session completed."""
        try:
            from apps.website.models.settings import PaymentSettings
            from wagtail.models import Site

            site = Site.objects.get(is_default_site=True)
            payment_settings = PaymentSettings.for_site(site)
            stripe_lib.api_key = payment_settings.stripe_secret_key

            session = stripe_lib.checkout.Session.retrieve(
                registration.payment_session_id
            )
            if session.payment_status == "paid":
                registration.payment_status = "paid"
                registration.payment_id = session.payment_intent or ""
                registration.save(
                    update_fields=["payment_status", "payment_id"]
                )
        except Exception:
            logger.exception(
                "Stripe payment verification failed for registration %s",
                registration.pk,
            )


class PaymentCancelView(LoginRequiredMixin, View):
    """Handle cancelled payment — offer retry."""

    template_name = "events/payment_cancel.html"

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        from django.shortcuts import render

        return render(request, self.template_name, {
            "registration": registration,
            "event": registration.event,
        })


# ---------------------------------------------------------------------------
# 12. StripeWebhookView — handle Stripe webhook events
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

    Captures the PayPal order and redirects to PaymentSuccessView
    on success, or PaymentCancelView on failure.
    """

    def get(self, request, pk):
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        if registration.payment_status == "paid":
            return redirect(reverse("events:payment_success", args=[pk]))

        if (
            registration.payment_provider != "paypal"
            or not registration.payment_session_id
        ):
            return redirect(reverse("events:payment_cancel", args=[pk]))

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
                    reverse("events:payment_success", args=[pk])
                )
        except Exception:
            logger.exception(
                "PayPal capture failed for registration %s", pk
            )

        return redirect(reverse("events:payment_cancel", args=[pk]))

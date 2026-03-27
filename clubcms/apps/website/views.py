"""
Views for the website app.

Provides views for:
- Newsletter subscription / archive
- Partner member verification (VerifyMemberView)
"""

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView

from apps.website.forms import (
    NewsletterSubscribeForm,
    NewsletterUnsubscribeForm,
    VerificationForm,
)
from apps.website.models.newsletter import (
    NewsletterCategory,
    NewsletterSubscription,
    SentNewsletter,
)
from apps.website.models.partners import PartnerPage
from apps.website.models.verification import VerificationLog


# ═══════════════════════════════════════════════════════════════════════════
# 0. Newsletter views
# ═══════════════════════════════════════════════════════════════════════════


def _get_captcha_context():
    """Return captcha provider/key from SiteSettings for templates."""
    from apps.website.models.settings import SiteSettings
    from wagtail.models import Site

    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        return {}
    try:
        ss = SiteSettings.for_site(site)
    except Exception:
        return {}
    return {
        "captcha_provider": ss.captcha_provider,
        "captcha_site_key": ss.captcha_site_key,
    }


class NewsletterSubscribeView(View):
    """Newsletter signup: GET shows form, POST processes subscription."""

    def get(self, request):
        form = NewsletterSubscribeForm()
        ctx = {"form": form}
        ctx.update(_get_captcha_context())
        return render(request, "website/newsletter_subscribe.html", ctx)

    def post(self, request):
        from django.contrib import messages

        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            categories = form.cleaned_data.get("categories", [])
            sub, created = NewsletterSubscription.objects.get_or_create(
                email=email,
                defaults={"ip_address": _get_client_ip(request)},
            )
            if not created and not sub.is_active:
                sub.is_active = True
                sub.unsubscribed_at = None
                sub.ip_address = _get_client_ip(request)
                sub.save(update_fields=["is_active", "unsubscribed_at", "ip_address"])

            # Set categories (defaults if none selected)
            if categories:
                sub.categories.set(categories)
            elif created:
                # Auto-select default categories for new subscribers
                defaults = NewsletterCategory.objects.filter(is_default=True)
                if defaults.exists():
                    sub.categories.set(defaults)

            messages.success(request, _("Thanks for subscribing!"))
            return redirect("website:newsletter-subscribe")

        ctx = {"form": form}
        ctx.update(_get_captcha_context())
        return render(request, "website/newsletter_subscribe.html", ctx)


class NewsletterUnsubscribeView(View):
    """Newsletter unsubscribe: GET shows form, POST processes removal."""

    def get(self, request):
        form = NewsletterUnsubscribeForm()
        ctx = {"form": form}
        ctx.update(_get_captcha_context())
        return render(request, "website/newsletter_unsubscribe.html", ctx)

    def post(self, request):
        from django.contrib import messages

        form = NewsletterUnsubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                sub = NewsletterSubscription.objects.get(email=email, is_active=True)
                sub.is_active = False
                sub.unsubscribed_at = timezone.now()
                sub.save(update_fields=["is_active", "unsubscribed_at"])
                messages.success(request, _("You have been unsubscribed."))
            except NewsletterSubscription.DoesNotExist:
                messages.info(request, _("This email is not subscribed to our newsletter."))
            return redirect("website:newsletter-unsubscribe")

        ctx = {"form": form}
        ctx.update(_get_captcha_context())
        return render(request, "website/newsletter_unsubscribe.html", ctx)


class NewsletterArchiveView(View):
    """
    Public newsletter archive — lists categories and their sent newsletters.

    Public newsletters are visible to everyone.
    Private newsletters require an authenticated user who is subscribed.
    """

    def get(self, request):
        from apps.website.render_email import render_newsletter_body_html

        category_slug = request.GET.get("category")

        categories = NewsletterCategory.objects.all()
        active_category = None
        if category_slug:
            active_category = NewsletterCategory.objects.filter(
                slug=category_slug
            ).first()

        # Build newsletter queryset — only sent newsletters
        newsletters = SentNewsletter.objects.filter(status="sent")

        # Visibility: public newsletters for everyone; private only for
        # authenticated subscribers
        is_subscriber = False
        if request.user.is_authenticated:
            is_subscriber = NewsletterSubscription.objects.filter(
                email=request.user.email, is_active=True
            ).exists()

        if not is_subscriber:
            newsletters = newsletters.filter(is_public=True)

        if active_category:
            newsletters = newsletters.filter(category=active_category)

        newsletters = newsletters.select_related("category").order_by("-sent_at")[:50]

        # Pre-render body preview (first block only) for listing
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")

        ctx = {
            "categories": categories,
            "active_category": active_category,
            "newsletters": newsletters,
            "is_subscriber": is_subscriber,
        }
        return render(request, "website/newsletter_archive.html", ctx)


class NewsletterDetailView(View):
    """
    Public detail view for a single sent newsletter.

    Public newsletters are readable by everyone.
    Private newsletters are only visible to authenticated subscribers.
    """

    def get(self, request, pk):
        from apps.website.render_email import render_newsletter_body_html

        newsletter = get_object_or_404(SentNewsletter, pk=pk, status="sent")

        # Access control for private newsletters
        if not newsletter.is_public:
            is_subscriber = False
            if request.user.is_authenticated:
                is_subscriber = NewsletterSubscription.objects.filter(
                    email=request.user.email, is_active=True
                ).exists()
            if not is_subscriber:
                from django.http import Http404

                raise Http404

        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
        body_html = render_newsletter_body_html(newsletter, base_url=base_url)

        ctx = {
            "newsletter": newsletter,
            "body_html": body_html,
        }
        return render(request, "website/newsletter_detail.html", ctx)


# ---------------------------------------------------------------------------
# Helper: get client IP
# ---------------------------------------------------------------------------

def _get_client_ip(request):
    """Extract the client IP address from the request."""
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


# ═══════════════════════════════════════════════════════════════════════════
# 1. VerifyMemberView
# ═══════════════════════════════════════════════════════════════════════════


class VerifyMemberView(LoginRequiredMixin, FormView):
    """
    Partner owners (or staff) verify a member by card number + secondary
    factor (display_name, city, or phone).

    Rate limited: max 20 attempts/hour per partner, lockout after 5
    consecutive failures for 15 minutes.
    """

    template_name = "website/verification/verify_member.html"
    form_class = VerificationForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings

            login_url = getattr(django_settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        # Check that the user is a partner owner or staff
        if not request.user.is_staff:
            is_partner_owner = PartnerPage.objects.filter(
                owner=request.user
            ).live().exists()
            if not is_partner_owner:
                return HttpResponseForbidden(
                    _("Access denied. Only partner owners and staff "
                      "can verify members.")
                )

        return super().dispatch(request, *args, **kwargs)

    def _check_rate_limit(self, user):
        """
        Check rate limiting for verification attempts.

        Returns (allowed: bool, message: str).
        """
        now = timezone.now()
        one_hour_ago = now - timezone.timedelta(hours=1)
        fifteen_min_ago = now - timezone.timedelta(minutes=15)

        # Check hourly rate limit (20 attempts/hour)
        hourly_count = VerificationLog.objects.filter(
            partner=user,
            created_at__gte=one_hour_ago,
        ).count()

        if hourly_count >= 20:
            return False, _(
                "Rate limit exceeded. Maximum 20 verification "
                "attempts per hour."
            )

        # Check consecutive failure lockout (5 failures in last 15 min)
        recent_logs = VerificationLog.objects.filter(
            partner=user,
            created_at__gte=fifteen_min_ago,
        ).order_by("-created_at")[:5]

        if recent_logs.count() >= 5:
            all_failures = all(
                log.result != "success" for log in recent_logs
            )
            if all_failures:
                return False, _(
                    "Account temporarily locked. Too many failed "
                    "verification attempts. Please try again in 15 minutes."
                )

        return True, ""

    def form_valid(self, request_form):
        user = self.request.user

        # Rate limit check
        allowed, message = self._check_rate_limit(user)
        if not allowed:
            return render(
                self.request,
                "website/verification/verify_result.html",
                {
                    "result": "rate_limited",
                    "message": message,
                },
            )

        card_number = request_form.cleaned_data["card_number"]
        v_type = request_form.cleaned_data["verification_type"]
        v_value = request_form.cleaned_data["verification_value"]
        ip_address = _get_client_ip(self.request)

        # Look up the member by card number
        from apps.members.models import ClubUser

        try:
            member = ClubUser.objects.get(card_number=card_number)
        except ClubUser.DoesNotExist:
            VerificationLog.objects.create(
                partner=user,
                card_number=card_number,
                verification_type=v_type,
                result="not_found",
                ip_address=ip_address,
            )
            return render(
                self.request,
                "website/verification/verify_result.html",
                {
                    "result": "not_found",
                    "message": _("No member found with this card number."),
                },
            )

        # Check if membership is expired
        if not member.is_active_member:
            VerificationLog.objects.create(
                partner=user,
                card_number=card_number,
                verification_type=v_type,
                result="expired",
                ip_address=ip_address,
            )
            return render(
                self.request,
                "website/verification/verify_result.html",
                {
                    "result": "expired",
                    "message": _("This member's membership has expired."),
                },
            )

        # Verify the secondary factor
        match = False
        if v_type == "display_name":
            match = (
                member.display_name.strip().lower()
                == v_value.strip().lower()
            )
        elif v_type == "city":
            match = (
                member.city.strip().lower()
                == v_value.strip().lower()
            )
        elif v_type == "phone":
            # Normalize phone: strip spaces, dashes, dots
            import re

            normalize = lambda p: re.sub(r"[\s\-\.\(\)]", "", p)
            match = normalize(member.phone) == normalize(v_value)

        if match:
            VerificationLog.objects.create(
                partner=user,
                card_number=card_number,
                verification_type=v_type,
                result="success",
                ip_address=ip_address,
            )
            # Return ONLY safe information: display_name, valid_until,
            # member_since. NEVER expose real name, email, full phone,
            # or address.
            return render(
                self.request,
                "website/verification/verify_result.html",
                {
                    "result": "success",
                    "message": _("Member verified successfully."),
                    "member_display_name": member.display_name or _("N/A"),
                    "member_valid_until": member.membership_expiry,
                    "member_since": member.membership_date,
                },
            )
        else:
            VerificationLog.objects.create(
                partner=user,
                card_number=card_number,
                verification_type=v_type,
                result="wrong_data",
                ip_address=ip_address,
            )
            return render(
                self.request,
                "website/verification/verify_result.html",
                {
                    "result": "wrong_data",
                    "message": _(
                        "Verification failed. The provided information "
                        "does not match our records."
                    ),
                },
            )


"""
Views for the website app.

Provides views for:
- Partner member verification (VerifyMemberView)

Newsletter views are now served by NewsletterPage (RoutablePageMixin)
in apps.website.models.newsletter.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView

from apps.website.forms import VerificationForm
from apps.website.models.partners import PartnerPage
from apps.website.models.verification import VerificationLog


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


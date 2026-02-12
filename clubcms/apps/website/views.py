"""
Views for the website app.

Provides views for:
- Partner member verification (VerifyMemberView)
- Gallery photo upload (PhotoUploadView, MyUploadsView)
- Photo moderation (ModerationQueueView, ApprovePhotoView, RejectPhotoView)
"""

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, ListView

from wagtail.images import get_image_model

from apps.members.decorators import active_member_required
from apps.website.forms import PhotoUploadForm, VerificationForm
from apps.website.models.partners import PartnerPage
from apps.website.models.uploads import PhotoUpload
from apps.website.models.verification import VerificationLog


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


# ═══════════════════════════════════════════════════════════════════════════
# 2. PhotoUploadView
# ═══════════════════════════════════════════════════════════════════════════


@method_decorator(active_member_required, name="dispatch")
class PhotoUploadView(FormView):
    """
    Allow active members with can_upload to upload gallery photos.

    Photos are saved as Wagtail images and linked through PhotoUpload
    records for moderation.
    """

    template_name = "website/uploads/upload_photo.html"
    form_class = PhotoUploadForm

    def dispatch(self, request, *args, **kwargs):
        # active_member_required handles authentication + membership check
        # We also need can_upload check
        if request.user.is_authenticated and not request.user.can_upload:
            return HttpResponseForbidden(
                _("Access denied. Your membership does not include "
                  "gallery upload privileges.")
            )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        ImageModel = get_image_model()

        files = form.cleaned_data["photos"]
        title_prefix = form.cleaned_data.get("title_prefix", "")
        event = form.cleaned_data.get("event")
        tags = form.cleaned_data.get("tags", [])

        uploads_created = 0
        for i, f in enumerate(files):
            # Generate title
            if title_prefix:
                title = f"{title_prefix} - {i + 1}"
            else:
                # Use filename without extension
                name_part = f.name.rsplit(".", 1)[0] if "." in f.name else f.name
                title = name_part

            # Create Wagtail image
            image = ImageModel(
                title=title,
                file=f,
                uploaded_by_user=self.request.user,
            )
            image.save()

            # Create PhotoUpload record
            upload = PhotoUpload.objects.create(
                image=image,
                uploaded_by=self.request.user,
                event=event,
            )

            # Add tags
            if tags:
                upload.tags.set(tags)

            uploads_created += 1

        return render(
            self.request,
            self.template_name,
            {
                "form": self.form_class(),
                "success": True,
                "uploads_count": uploads_created,
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. MyUploadsView
# ═══════════════════════════════════════════════════════════════════════════


class MyUploadsView(LoginRequiredMixin, ListView):
    """List the logged-in user's photo uploads with their status."""

    template_name = "website/uploads/my_uploads.html"
    context_object_name = "uploads"
    paginate_by = 20

    def get_queryset(self):
        return PhotoUpload.objects.filter(
            uploaded_by=self.request.user
        ).select_related("image", "event").order_by("-uploaded_at")


# ═══════════════════════════════════════════════════════════════════════════
# 4. ModerationQueueView (staff only)
# ═══════════════════════════════════════════════════════════════════════════


@method_decorator(staff_member_required, name="dispatch")
class ModerationQueueView(ListView):
    """Staff-only view showing pending photo uploads for moderation."""

    template_name = "website/uploads/moderation_queue.html"
    context_object_name = "uploads"
    paginate_by = 30

    def get_queryset(self):
        return PhotoUpload.objects.filter(
            is_approved=False,
            rejection_reason="",
        ).select_related(
            "image", "uploaded_by", "event"
        ).order_by("-uploaded_at")


# ═══════════════════════════════════════════════════════════════════════════
# 5. ApprovePhotoView (staff only, POST)
# ═══════════════════════════════════════════════════════════════════════════


@method_decorator(staff_member_required, name="dispatch")
class ApprovePhotoView(View):
    """Staff-only POST endpoint to approve a pending photo upload."""

    def post(self, request, pk):
        upload = get_object_or_404(PhotoUpload, pk=pk)

        upload.is_approved = True
        upload.approved_by = request.user
        upload.approved_at = timezone.now()
        upload.rejection_reason = ""
        upload.save(update_fields=[
            "is_approved",
            "approved_by",
            "approved_at",
            "rejection_reason",
        ])

        # If AJAX, return JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "approved", "pk": pk})

        return redirect("website:moderation_queue")


# ═══════════════════════════════════════════════════════════════════════════
# 6. RejectPhotoView (staff only, POST)
# ═══════════════════════════════════════════════════════════════════════════


@method_decorator(staff_member_required, name="dispatch")
class RejectPhotoView(View):
    """Staff-only POST endpoint to reject a pending photo upload."""

    def post(self, request, pk):
        upload = get_object_or_404(PhotoUpload, pk=pk)
        reason = request.POST.get("reason", "").strip()

        if not reason:
            reason = _("Rejected by moderator.")

        upload.is_approved = False
        upload.rejection_reason = reason
        upload.save(update_fields=["is_approved", "rejection_reason"])

        # If AJAX, return JSON
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "status": "rejected",
                "pk": pk,
                "reason": str(reason),
            })

        return redirect("website:moderation_queue")

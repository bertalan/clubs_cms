"""
Views for the members app.

Provides class-based views for member profile management, digital
membership cards, privacy settings, notification preferences,
mutual-aid availability, and the public member directory.
"""

import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView, UpdateView

from apps.members.forms import (
    AidAvailabilityForm,
    NotificationPreferencesForm,
    PrivacySettingsForm,
    ProfileForm,
)


# ---------------------------------------------------------------------------
# 1. ProfileView — edit own profile
# ---------------------------------------------------------------------------


class ProfileView(LoginRequiredMixin, UpdateView):
    """Edit the logged-in user's personal profile."""

    template_name = "account/profile.html"
    form_class = ProfileForm
    success_url = reverse_lazy("account:profile")

    def get_object(self, queryset=None):
        return self.request.user


# ---------------------------------------------------------------------------
# 2. PublicProfileView — read-only public profile
# ---------------------------------------------------------------------------


class PublicProfileView(DetailView):
    """
    Read-only view of a member's public profile.

    Returns 404 if the member has not opted into public_profile.
    """

    template_name = "account/public_profile.html"
    context_object_name = "member"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_queryset(self):
        from apps.members.models import ClubUser

        return ClubUser.objects.filter(public_profile=True, is_active=True)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.public_profile:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member = self.object
        context["visible_name"] = member.get_visible_name(
            viewer=self.request.user if self.request.user.is_authenticated else None
        )
        return context


# ---------------------------------------------------------------------------
# 3. CardView — digital membership card display
# ---------------------------------------------------------------------------


class CardView(LoginRequiredMixin, TemplateView):
    """Display the logged-in user's digital membership card."""

    template_name = "account/card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["club_name"] = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")

        # Check for QR code and barcode images
        if user.card_number:
            safe_name = user.card_number.replace("/", "-").replace("\\", "-")
            qr_path = os.path.join("members", "qr", f"{safe_name}.png")
            barcode_path = os.path.join("members", "barcode", f"{safe_name}.png")

            qr_full = os.path.join(settings.MEDIA_ROOT, qr_path)
            barcode_full = os.path.join(settings.MEDIA_ROOT, barcode_path)

            if os.path.exists(qr_full):
                context["qr_url"] = settings.MEDIA_URL + qr_path
            if os.path.exists(barcode_full):
                context["barcode_url"] = settings.MEDIA_URL + barcode_path

        return context


# ---------------------------------------------------------------------------
# 4. CardPDFView — PDF download of membership card
# ---------------------------------------------------------------------------


class CardPDFView(LoginRequiredMixin, View):
    """
    Download a PDF version of the membership card.

    Uses reportlab if available; otherwise falls back to a simple
    text-based response.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.card_number:
            raise Http404(_("No membership card available."))

        try:
            from io import BytesIO

            from reportlab.lib.pagesizes import A6
            from reportlab.pdfgen import canvas

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A6)
            width, height = A6

            club_name = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
            p.setFont("Helvetica-Bold", 16)
            p.drawCentredString(width / 2, height - 40, club_name)

            p.setFont("Helvetica", 12)
            p.drawCentredString(
                width / 2, height - 70, user.get_full_name() or user.username
            )
            p.drawCentredString(width / 2, height - 90, f"Card: {user.card_number}")

            if user.membership_expiry:
                p.drawCentredString(
                    width / 2,
                    height - 110,
                    f"Expires: {user.membership_expiry.strftime('%Y-%m-%d')}",
                )

            p.showPage()
            p.save()

            buffer.seek(0)
            return FileResponse(
                buffer,
                as_attachment=True,
                filename=f"card-{user.card_number}.pdf",
                content_type="application/pdf",
            )
        except ImportError:
            # Fallback: plain text card
            from django.http import HttpResponse

            content = (
                f"Membership Card\n"
                f"Name: {user.get_full_name() or user.username}\n"
                f"Card: {user.card_number}\n"
            )
            if user.membership_expiry:
                content += f"Expires: {user.membership_expiry}\n"

            response = HttpResponse(content, content_type="text/plain")
            response[
                "Content-Disposition"
            ] = f'attachment; filename="card-{user.card_number}.txt"'
            return response


# ---------------------------------------------------------------------------
# 5. QRCodeView — serve QR code image
# ---------------------------------------------------------------------------


class QRCodeView(LoginRequiredMixin, View):
    """Serve the QR code image for the logged-in user's card."""

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.card_number:
            raise Http404(_("No membership card available."))

        safe_name = user.card_number.replace("/", "-").replace("\\", "-")
        qr_path = os.path.join(settings.MEDIA_ROOT, "members", "qr", f"{safe_name}.png")

        if not os.path.exists(qr_path):
            # Try to generate on the fly
            from apps.members.utils import generate_qr_code

            result = generate_qr_code(user)
            if result is None:
                raise Http404(_("QR code generation not available."))
            qr_path = os.path.join(settings.MEDIA_ROOT, result)

        resolved = os.path.abspath(qr_path)
        if not resolved.startswith(os.path.abspath(settings.MEDIA_ROOT)):
            raise Http404()
        fh = open(resolved, "rb")
        return FileResponse(fh, content_type="image/png")


# ---------------------------------------------------------------------------
# 6. BarcodeView — serve barcode image
# ---------------------------------------------------------------------------


class BarcodeView(LoginRequiredMixin, View):
    """Serve the barcode image for the logged-in user's card."""

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.card_number:
            raise Http404(_("No membership card available."))

        safe_name = user.card_number.replace("/", "-").replace("\\", "-")
        barcode_path = os.path.join(
            settings.MEDIA_ROOT, "members", "barcode", f"{safe_name}.png"
        )

        if not os.path.exists(barcode_path):
            from apps.members.utils import generate_barcode

            result = generate_barcode(user)
            if result is None:
                raise Http404(_("Barcode generation not available."))
            barcode_path = os.path.join(settings.MEDIA_ROOT, result)

        resolved = os.path.abspath(barcode_path)
        if not resolved.startswith(os.path.abspath(settings.MEDIA_ROOT)):
            raise Http404()
        fh = open(resolved, "rb")
        return FileResponse(fh, content_type="image/png")


# ---------------------------------------------------------------------------
# 7. PrivacySettingsView — privacy form
# ---------------------------------------------------------------------------


class PrivacySettingsView(LoginRequiredMixin, UpdateView):
    """Edit the logged-in user's privacy settings."""

    template_name = "account/privacy.html"
    form_class = PrivacySettingsForm
    success_url = reverse_lazy("account:privacy")

    def get_object(self, queryset=None):
        return self.request.user


# ---------------------------------------------------------------------------
# 8. NotificationPrefsView — notification form
# ---------------------------------------------------------------------------


class NotificationPrefsView(LoginRequiredMixin, UpdateView):
    """Edit the logged-in user's notification preferences."""

    template_name = "account/notifications.html"
    form_class = NotificationPreferencesForm
    success_url = reverse_lazy("account:notifications")

    def get_object(self, queryset=None):
        return self.request.user


# ---------------------------------------------------------------------------
# 9. AidAvailabilityView — mutual aid form
# ---------------------------------------------------------------------------


class AidAvailabilityView(LoginRequiredMixin, UpdateView):
    """Edit the logged-in user's mutual-aid availability."""

    template_name = "account/aid.html"
    form_class = AidAvailabilityForm
    success_url = reverse_lazy("account:aid")

    def get_object(self, queryset=None):
        return self.request.user


# ---------------------------------------------------------------------------
# 10. MemberDirectoryView — list of opt-in members
# ---------------------------------------------------------------------------


class MemberDirectoryView(LoginRequiredMixin, ListView):
    """
    List members who have opted into the directory.

    Only shows members with show_in_directory=True and active accounts.
    """

    template_name = "account/directory.html"
    context_object_name = "members"
    paginate_by = 30

    def get_queryset(self):
        from apps.members.models import ClubUser

        return (
            ClubUser.objects.filter(show_in_directory=True, is_active=True)
            .order_by("last_name", "first_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viewer = self.request.user
        # Pre-compute visible names for template use
        for member in context["members"]:
            member.visible_name = member.get_visible_name(viewer=viewer)
        return context


# ---------------------------------------------------------------------------
# 11. MembershipPlansView — public membership products page
# ---------------------------------------------------------------------------


class MembershipPlansView(TemplateView):
    """
    Public page showing available membership products/plans.

    Accessible to everyone; shows the user's current plan if authenticated.
    """

    template_name = "account/membership_plans.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.website.models.snippets import Product

        context["products"] = Product.objects.filter(is_active=True).order_by("order")
        if self.request.user.is_authenticated:
            context["user_products"] = {
                p.pk for p in self.request.user.products.all()
            }
        else:
            context["user_products"] = set()
        return context

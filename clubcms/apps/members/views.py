"""
Views for the members app.

Provides class-based views for member profile management, digital
membership cards, privacy settings, notification preferences,
mutual-aid availability, and the public member directory.
"""

import os

from django.conf import settings
from django.contrib import messages
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

    def form_valid(self, form):
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)


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
    """Display the logged-in user's digital membership card and products."""

    template_name = "account/card.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user"] = user
        context["club_name"] = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")

        # User's products
        if hasattr(user, "products"):
            context["user_products"] = user.products.all()
        else:
            context["user_products"] = []

        # Available products for purchase
        from apps.website.models.snippets import Product
        from wagtail.models import Locale
        locale = Locale.get_active()
        context["available_products"] = Product.objects.filter(
            is_active=True, locale=locale
        ).order_by("order")

        # Contact page URL for membership requests
        from apps.website.models.pages import ContactPage
        contact_page = ContactPage.objects.live().first()
        if contact_page:
            context["contact_page_url"] = contact_page.url
        else:
            context["contact_page_url"] = "/"

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

    Creates a credit card style PDF with club branding, member details,
    and QR code for verification.
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.card_number:
            raise Http404(_("No membership card available."))

        try:
            from io import BytesIO

            from reportlab.lib import colors
            from reportlab.lib.pagesizes import landscape
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            import qrcode

            # Credit card size: 85.6 x 53.98 mm (ISO/IEC 7810 ID-1)
            CARD_WIDTH = 85.6 * mm
            CARD_HEIGHT = 53.98 * mm
            pagesize = (CARD_WIDTH, CARD_HEIGHT)

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=pagesize)

            # Get club settings
            from apps.website.models import SiteSettings
            site_settings = SiteSettings.for_request(request)
            club_name = site_settings.site_name or getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
            club_phone = site_settings.phone or ""
            club_email = site_settings.email or ""
            club_address = site_settings.address or ""

            # ---- FRONT SIDE ----
            # Background gradient (dark)
            p.setFillColor(colors.HexColor("#1a1a1a"))
            p.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=True, stroke=False)

            # Red accent stripe at top
            p.setFillColor(colors.HexColor("#C41E3A"))
            p.rect(0, CARD_HEIGHT - 8*mm, CARD_WIDTH, 8*mm, fill=True, stroke=False)

            # Club name in accent stripe
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(5*mm, CARD_HEIGHT - 6*mm, club_name.upper())

            # Member type badge
            p.setFont("Helvetica", 6)
            p.setFillColor(colors.HexColor("#888888"))
            p.drawRightString(CARD_WIDTH - 5*mm, CARD_HEIGHT - 6*mm, str(_("MEMBERSHIP CARD")))

            # Member name
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 12)
            member_name = user.get_full_name() or user.username
            p.drawString(5*mm, CARD_HEIGHT - 18*mm, member_name)

            # Card number
            p.setFont("Courier-Bold", 10)
            p.setFillColor(colors.HexColor("#cccccc"))
            # Format card number with spaces for readability
            card_display = user.card_number.replace("-", " - ")
            p.drawString(5*mm, CARD_HEIGHT - 26*mm, card_display)

            # Dates section
            p.setFont("Helvetica", 6)
            p.setFillColor(colors.HexColor("#888888"))
            p.drawString(5*mm, CARD_HEIGHT - 34*mm, str(_("MEMBER SINCE")))
            p.drawString(30*mm, CARD_HEIGHT - 34*mm, str(_("EXPIRES")))

            p.setFont("Helvetica-Bold", 8)
            p.setFillColor(colors.white)
            if user.membership_date:
                p.drawString(5*mm, CARD_HEIGHT - 38*mm, user.membership_date.strftime("%d/%m/%Y"))
            else:
                p.drawString(5*mm, CARD_HEIGHT - 38*mm, "-")
            
            if user.membership_expiry:
                p.drawString(30*mm, CARD_HEIGHT - 38*mm, user.membership_expiry.strftime("%d/%m/%Y"))
            else:
                p.drawString(30*mm, CARD_HEIGHT - 38*mm, "-")

            # QR Code
            qr = qrcode.QRCode(version=1, box_size=10, border=1)
            qr_data = user.get_qr_data() if hasattr(user, 'get_qr_data') else f"CARD:{user.card_number}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="white", back_color="#1a1a1a")
            
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format='PNG')
            qr_buffer.seek(0)
            
            qr_size = 18*mm
            p.drawImage(
                ImageReader(qr_buffer),
                CARD_WIDTH - qr_size - 4*mm,
                4*mm,
                width=qr_size,
                height=qr_size
            )

            # Club info at bottom
            p.setFont("Helvetica", 5)
            p.setFillColor(colors.HexColor("#666666"))
            contact_info = []
            if club_phone:
                contact_info.append(club_phone)
            if club_email:
                contact_info.append(club_email)
            if contact_info:
                p.drawString(5*mm, 4*mm, " | ".join(contact_info))

            p.showPage()

            # ---- BACK SIDE ----
            p.setFillColor(colors.HexColor("#f5f5f5"))
            p.rect(0, 0, CARD_WIDTH, CARD_HEIGHT, fill=True, stroke=False)

            # Red accent at top
            p.setFillColor(colors.HexColor("#C41E3A"))
            p.rect(0, CARD_HEIGHT - 6*mm, CARD_WIDTH, 6*mm, fill=True, stroke=False)

            # Barcode placeholder (card number as text)
            p.setFont("Courier", 12)
            p.setFillColor(colors.black)
            p.drawCentredString(CARD_WIDTH / 2, CARD_HEIGHT - 18*mm, user.card_number)

            # Club info
            p.setFont("Helvetica-Bold", 8)
            p.setFillColor(colors.HexColor("#333333"))
            p.drawCentredString(CARD_WIDTH / 2, CARD_HEIGHT - 28*mm, club_name)

            if club_address:
                p.setFont("Helvetica", 6)
                p.setFillColor(colors.HexColor("#666666"))
                # Split address into lines
                address_lines = club_address.strip().split('\n')
                y_pos = CARD_HEIGHT - 34*mm
                for line in address_lines[:3]:  # Max 3 lines
                    p.drawCentredString(CARD_WIDTH / 2, y_pos, line.strip())
                    y_pos -= 3*mm

            # Contact info
            p.setFont("Helvetica", 6)
            p.setFillColor(colors.HexColor("#666666"))
            contact_y = 12*mm
            if club_phone:
                p.drawCentredString(CARD_WIDTH / 2, contact_y, str(_("Tel:")) + f" {club_phone}")
                contact_y -= 3*mm
            if club_email:
                p.drawCentredString(CARD_WIDTH / 2, contact_y, club_email)

            # Terms note
            p.setFont("Helvetica", 4)
            p.setFillColor(colors.HexColor("#999999"))
            p.drawCentredString(CARD_WIDTH / 2, 4*mm, str(_("This card remains property of the club. Present upon request.")))

            p.showPage()
            p.save()

            buffer.seek(0)
            return FileResponse(
                buffer,
                as_attachment=True,
                filename=f"card-{user.card_number}.pdf",
                content_type="application/pdf",
            )
        except ImportError as e:
            # Fallback: plain text card
            from django.http import HttpResponse

            content = (
                str(_("Membership Card")) + "\n"
                + str(_("Name:")) + f" {user.get_full_name() or user.username}\n"
                + str(_("Card:")) + f" {user.card_number}\n"
            )
            if user.membership_expiry:
                content += str(_("Expires:")) + f" {user.membership_expiry}\n"
            content += f"\nError: PDF library not available ({e})"

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

    def form_valid(self, form):
        messages.success(self.request, _("Privacy settings saved."))
        return super().form_valid(form)


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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.conf import settings as django_settings
        vapid = getattr(django_settings, "WEBPUSH_SETTINGS", {})
        ctx["vapid_public_key"] = vapid.get("VAPID_PUBLIC_KEY", "")
        return ctx

    def form_valid(self, form):
        messages.success(self.request, _("Notification preferences saved."))
        return super().form_valid(form)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        coords = self.request.user.aid_coordinates
        if coords and "," in coords:
            parts = coords.split(",", 1)
            try:
                context["initial_lat"] = float(parts[0].strip())
                context["initial_lng"] = float(parts[1].strip())
            except (ValueError, IndexError):
                pass
        return context

    def form_valid(self, form):
        messages.success(self.request, _("Mutual aid availability saved."))
        return super().form_valid(form)


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
# 12. MembershipRequestView — request to purchase a membership product
# ---------------------------------------------------------------------------


class MembershipRequestCreateView(LoginRequiredMixin, View):
    """
    Handle membership purchase requests.

    GET: Show request form with product details
    POST: Create a new membership request
    """

    def get(self, request, product_id):
        from apps.website.models.snippets import Product
        from apps.members.models import MembershipRequest

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            raise Http404(_("Product not found."))

        # Check if user already has this product
        if product in request.user.products.all():
            messages.info(request, _("You already have this membership."))
            return self._redirect_to_card()

        # Check for pending request for this product
        pending = MembershipRequest.objects.filter(
            user=request.user, product=product, status="pending"
        ).exists()
        if pending:
            messages.info(request, _("You already have a pending request for this product."))
            return self._redirect_to_card()

        context = {
            "product": product,
            "user_products": request.user.products.all(),
        }
        return self._render(request, context)

    def post(self, request, product_id):
        from apps.website.models.snippets import Product
        from apps.members.models import MembershipRequest

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            raise Http404(_("Product not found."))

        # Check if user already has this product
        if product in request.user.products.all():
            messages.error(request, _("You already have this membership."))
            return self._redirect_to_card()

        # Check for pending request
        pending = MembershipRequest.objects.filter(
            user=request.user, product=product, status="pending"
        ).exists()
        if pending:
            messages.error(request, _("You already have a pending request for this product."))
            return self._redirect_to_card()

        # Create the request
        notes = request.POST.get("notes", "").strip()
        MembershipRequest.objects.create(
            user=request.user,
            product=product,
            notes=notes,
        )

        messages.success(
            request,
            _("Your membership request has been submitted! The club will contact you shortly.")
        )
        return self._redirect_to_card()

    def _redirect_to_card(self):
        from django.shortcuts import redirect
        return redirect("account:card")

    def _render(self, request, context):
        from django.shortcuts import render
        return render(request, "account/membership_request.html", context)


class MembershipRequestListView(LoginRequiredMixin, ListView):
    """Show user's membership requests history."""

    template_name = "account/membership_requests.html"
    context_object_name = "requests"

    def get_queryset(self):
        from apps.members.models import MembershipRequest
        return MembershipRequest.objects.filter(user=self.request.user).order_by("-created_at")

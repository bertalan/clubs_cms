"""
Views for the members app.

Binary file views (PDF, QR, barcode) remain as Django views because
they serve non-HTML responses.  All HTML member-area views have been
migrated to MembersAreaPage (RoutablePageMixin) in models.py.
"""

import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404
from django.utils.translation import gettext_lazy as _
from django.views import View


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

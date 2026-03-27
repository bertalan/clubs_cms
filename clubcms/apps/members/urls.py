"""
URL patterns for the members app.

Only binary-file views remain here (PDF, QR, barcode).
All HTML views are served by MembersAreaPage via RoutablePageMixin.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.members import views

app_name = "account"

urlpatterns = [
    # Binary file downloads (cannot use RoutablePageMixin rendering)
    path(_("card/pdf/"), views.CardPDFView.as_view(), name="card_pdf"),
    path(_("card/qr/"), views.QRCodeView.as_view(), name="card_qr"),
    path(_("card/barcode/"), views.BarcodeView.as_view(), name="card_barcode"),
]

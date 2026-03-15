"""
URL patterns for the members app.

Registered with app_name="account" and included at /account/ in the
root URL conf.  The public profile pattern is included separately at
/members/<username>/.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.core.views import MyContributionsView, SubmitContributionView
from apps.members import views

app_name = "account"

urlpatterns = [
    # Profile
    path(_("profile/"), views.ProfileView.as_view(), name="profile"),
    # Digital membership card
    path(_("card/"), views.CardView.as_view(), name="card"),
    path(_("card/pdf/"), views.CardPDFView.as_view(), name="card_pdf"),
    path(_("card/qr/"), views.QRCodeView.as_view(), name="card_qr"),
    path(_("card/barcode/"), views.BarcodeView.as_view(), name="card_barcode"),
    # Settings
    path(_("privacy/"), views.PrivacySettingsView.as_view(), name="privacy"),
    path(
        _("notifications/"),
        views.NotificationPrefsView.as_view(),
        name="notifications",
    ),
    path(_("aid/"), views.AidAvailabilityView.as_view(), name="aid"),
    # Membership requests
    path(
        _("membership-request/<int:product_id>/"),
        views.MembershipRequestCreateView.as_view(),
        name="membership_request",
    ),
    path(
        _("membership-requests/"),
        views.MembershipRequestListView.as_view(),
        name="membership_requests",
    ),
    # Directory
    path(_("directory/"), views.MemberDirectoryView.as_view(), name="directory"),
    # Contributions
    path(
        _("contributions/"),
        MyContributionsView.as_view(),
        name="my_contributions",
    ),
    path(
        _("contributions/submit/"),
        SubmitContributionView.as_view(),
        name="submit_contribution",
    ),
]

# Public profile pattern — included separately in root urlconf at
# path("members/<str:username>/", ...)
public_profile_urlpatterns = [
    path("", views.PublicProfileView.as_view(), name="public_profile"),
]

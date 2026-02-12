"""
URL patterns for the members app.

Registered with app_name="account" and included at /account/ in the
root URL conf.  The public profile pattern is included separately at
/members/<username>/.
"""

from django.urls import path

from apps.members import views

app_name = "account"

urlpatterns = [
    # Profile
    path("profile/", views.ProfileView.as_view(), name="profile"),
    # Digital membership card
    path("card/", views.CardView.as_view(), name="card"),
    path("card/pdf/", views.CardPDFView.as_view(), name="card_pdf"),
    path("card/qr/", views.QRCodeView.as_view(), name="card_qr"),
    path("card/barcode/", views.BarcodeView.as_view(), name="card_barcode"),
    # Settings
    path("privacy/", views.PrivacySettingsView.as_view(), name="privacy"),
    path(
        "notifications/",
        views.NotificationPrefsView.as_view(),
        name="notifications",
    ),
    path("aid/", views.AidAvailabilityView.as_view(), name="aid"),
    # Membership plans (public)
    path("become-member/", views.MembershipPlansView.as_view(), name="membership_plans"),
    # Directory
    path("directory/", views.MemberDirectoryView.as_view(), name="directory"),
]

# Public profile pattern — included separately in root urlconf at
# path("members/<str:username>/", ...)
public_profile_urlpatterns = [
    path("", views.PublicProfileView.as_view(), name="public_profile"),
]

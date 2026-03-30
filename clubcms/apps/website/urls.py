"""
URL patterns for the website app.

Registered with app_name="website" and included in the root URL conf
before the Wagtail catch-all.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.website import views

app_name = "website"

urlpatterns = [
    # Partner member verification
    path(
        _("partners/verify-member/"),
        views.VerifyMemberView.as_view(),
        name="verify_member",
    ),
]

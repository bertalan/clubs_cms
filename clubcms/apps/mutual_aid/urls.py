"""
Mutual Aid URL configuration.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.mutual_aid.views import (
    ContactFormView,
    ContactUnlockView,
    HelperDetailView,
    HelpersAPIView,
    MutualAidMapView,
    RequestAccessView,
)

app_name = "mutual_aid"

urlpatterns = [
    path("", MutualAidMapView.as_view(), name="map"),
    path(_("helper/<int:pk>/"), HelperDetailView.as_view(), name="helper_detail"),
    path(_("helper/<int:pk>/contact/"), ContactFormView.as_view(), name="contact_form"),
    path(_("helper/<int:pk>/unlock/"), ContactUnlockView.as_view(), name="unlock_contact"),
    path(_("request-access/"), RequestAccessView.as_view(), name="request_access"),
    path("api/helpers/", HelpersAPIView.as_view(), name="helpers_api"),
]

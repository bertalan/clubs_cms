"""
Federation API URL patterns.

Included at /api/federation/ when FEDERATION_ENABLED is True.
"""

from django.urls import path

from apps.federation.api.views import FederationEventsAPIView, FederationInterestAPIView

app_name = "federation_api"

urlpatterns = [
    path("events/", FederationEventsAPIView.as_view(), name="events"),
    path("interest/", FederationInterestAPIView.as_view(), name="interest"),
]

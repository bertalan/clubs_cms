"""Test URL configuration that always includes federation API URLs."""

from django.urls import include, path

from clubcms.urls import urlpatterns as base_urlpatterns

urlpatterns = base_urlpatterns + [
    path("api/federation/", include("apps.federation.urls_api")),
]

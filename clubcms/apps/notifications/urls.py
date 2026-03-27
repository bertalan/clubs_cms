"""
URL configuration for the notifications app.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "notifications"

urlpatterns = [
    # Unsubscribe (no login required, token-based)
    path(
        _("unsubscribe/<str:token>/"),
        views.UnsubscribeView.as_view(),
        name="unsubscribe",
    ),
    path(
        _("unsubscribe/success/"),
        views.UnsubscribeSuccessView.as_view(),
        name="unsubscribe_success",
    ),
    # Push subscription management (login required)
    path(
        "push/subscribe/",
        views.PushSubscribeView.as_view(),
        name="push_subscribe",
    ),
    path(
        "push/unsubscribe/",
        views.PushUnsubscribeView.as_view(),
        name="push_unsubscribe",
    ),
]

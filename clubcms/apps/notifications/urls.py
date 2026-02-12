"""
URL configuration for the notifications app.
"""

from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    # Unsubscribe (no login required, token-based)
    path(
        "unsubscribe/<str:token>/",
        views.UnsubscribeView.as_view(),
        name="unsubscribe",
    ),
    path(
        "unsubscribe/success/",
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
    # Notification history (login required)
    path(
        "history/",
        views.NotificationHistoryView.as_view(),
        name="history",
    ),
    # Mark notification as read (AJAX, login required)
    path(
        "mark-read/<int:pk>/",
        views.MarkReadView.as_view(),
        name="mark_read",
    ),
]

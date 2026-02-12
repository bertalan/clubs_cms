"""
Wagtail admin registration for notification models.

Uses Wagtail's ModelViewSet to provide list/inspect views inside
the Wagtail admin sidebar.
"""

from wagtail.admin.viewsets.model import ModelViewSet

from .models import NotificationQueue, PushSubscription


class NotificationQueueViewSet(ModelViewSet):
    """Admin viewset for NotificationQueue entries."""

    model = NotificationQueue
    icon = "mail"
    add_to_admin_menu = False  # added via group in wagtail_hooks
    exclude_form_fields = []
    list_display = [
        "title",
        "notification_type",
        "recipient",
        "channel",
        "status",
        "created_at",
        "sent_at",
    ]
    list_filter = ["status", "channel", "notification_type"]
    search_fields = ["title", "body"]
    ordering = ["-created_at"]
    inspect_view_enabled = True
    copy_view_enabled = False


class PushSubscriptionViewSet(ModelViewSet):
    """Admin viewset for PushSubscription entries."""

    model = PushSubscription
    icon = "notification"
    add_to_admin_menu = False
    exclude_form_fields = []
    list_display = [
        "user",
        "is_active",
        "created_at",
        "last_used",
        "user_agent",
    ]
    list_filter = ["is_active"]
    search_fields = ["user__username", "user__email"]
    ordering = ["-created_at"]
    inspect_view_enabled = True
    copy_view_enabled = False

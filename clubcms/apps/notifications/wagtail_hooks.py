"""
Wagtail hooks for the notifications app.

Registers admin viewsets and adds a "Notifications" menu group
to the Wagtail admin sidebar.
"""

from wagtail import hooks
from wagtail.admin.menu import MenuItem, SubmenuMenuItem
from wagtail.admin.viewsets.base import ViewSetGroup

from .admin import NotificationQueueViewSet, PushSubscriptionViewSet


class NotificationsViewSetGroup(ViewSetGroup):
    """
    Groups notification-related viewsets under a single menu entry.
    """

    menu_label = "Notifications"
    menu_icon = "mail"
    menu_order = 700
    items = (
        NotificationQueueViewSet,
        PushSubscriptionViewSet,
    )


@hooks.register("register_admin_viewset")
def register_notifications_viewset_group():
    return NotificationsViewSetGroup()

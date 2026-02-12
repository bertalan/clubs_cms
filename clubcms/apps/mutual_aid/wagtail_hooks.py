"""
Wagtail hooks for the Mutual Aid admin interface.

Registers AidRequest, FederatedAidAccess, and pending access requests
under a "Mutual Aid" menu group in the Wagtail sidebar.
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from apps.mutual_aid.models import (
    AidPrivacySettings,
    AidRequest,
    ContactUnlock,
    FederatedAidAccess,
    FederatedAidAccessRequest,
)


class AidRequestViewSet(SnippetViewSet):
    """Admin interface for aid requests."""

    model = AidRequest
    icon = "help"
    menu_label = "Aid Requests"
    menu_order = 100
    add_to_admin_menu = False
    list_display = [
        "requester_name",
        "helper",
        "issue_type",
        "urgency",
        "status",
        "created_at",
    ]
    list_filter = ["status", "urgency", "issue_type", "is_from_federation"]
    search_fields = ["requester_name", "description"]


class FederatedAidAccessViewSet(SnippetViewSet):
    """Admin interface for federated aid access grants."""

    model = FederatedAidAccess
    icon = "globe"
    menu_label = "Federation Access"
    menu_order = 200
    add_to_admin_menu = False
    list_display = [
        "external_display_name",
        "source_club",
        "access_level",
        "contacts_unlocked",
        "is_active",
        "created_at",
    ]
    list_filter = ["source_club", "access_level", "is_active"]
    search_fields = ["external_display_name", "external_user_id"]


class AccessRequestViewSet(SnippetViewSet):
    """Admin interface for pending access requests."""

    model = FederatedAidAccessRequest
    icon = "mail"
    menu_label = "Access Requests"
    menu_order = 300
    add_to_admin_menu = False
    list_display = [
        "federated_access",
        "status",
        "reviewed_by",
        "created_at",
    ]
    list_filter = ["status"]


class MutualAidViewSetGroup(SnippetViewSetGroup):
    """Groups mutual aid admin panels under a single menu item."""

    items = (AidRequestViewSet, FederatedAidAccessViewSet, AccessRequestViewSet)
    menu_label = "Mutual Aid"
    menu_icon = "help"
    menu_order = 750


register_snippet(MutualAidViewSetGroup)

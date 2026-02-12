"""
Wagtail hooks for the Federation admin interface.

Registers FederatedClub and ExternalEvent admin panels under
a "Federation" menu group in the Wagtail sidebar.
"""

from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from apps.federation.models import ExternalEvent, FederatedClub


class FederatedClubViewSet(SnippetViewSet):
    """Admin interface for managing partner clubs."""

    model = FederatedClub
    icon = "globe"
    menu_label = "Partner Clubs"
    menu_order = 100
    add_to_admin_menu = False
    list_display = [
        "name",
        "short_code",
        "base_url",
        "is_active",
        "is_approved",
        "share_our_events",
        "last_sync",
    ]
    list_filter = ["is_active", "is_approved", "share_our_events"]
    search_fields = ["name", "short_code"]


class ExternalEventViewSet(SnippetViewSet):
    """Admin interface for viewing imported external events."""

    model = ExternalEvent
    icon = "calendar"
    menu_label = "External Events"
    menu_order = 200
    add_to_admin_menu = False
    list_display = [
        "event_name",
        "source_club",
        "start_date",
        "event_status",
        "is_approved",
        "is_hidden",
    ]
    list_filter = ["source_club", "is_approved", "is_hidden", "event_status"]
    search_fields = ["event_name", "location_name"]


class FederationViewSetGroup(SnippetViewSetGroup):
    """Groups federation admin panels under a single menu item."""

    items = (FederatedClubViewSet, ExternalEventViewSet)
    menu_label = "Federation"
    menu_icon = "globe"
    menu_order = 700


register_snippet(FederationViewSetGroup)

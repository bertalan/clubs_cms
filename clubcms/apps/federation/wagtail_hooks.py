"""
Wagtail hooks for the Federation admin interface.

Registers FederatedClub and ExternalEvent admin panels under
a "Federation" menu group in the Wagtail sidebar.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from apps.core.admin_guides import GuidePanel
from apps.federation import views_admin
from apps.federation.admin_guides import FEDERATED_CLUB_GUIDE
from apps.federation.models import ExternalEvent, FederatedClub


class KeyToolsPanel(HelpPanel):
    """Buttons under the key fields: generate a pair, test the connection."""

    def __init__(self, **kwargs):
        kwargs.setdefault("template", "admin/federation/key_tools_panel.html")
        super().__init__(**kwargs)


class FederatedClubViewSet(SnippetViewSet):
    """Admin interface for managing partner clubs."""

    model = FederatedClub
    icon = "globe"
    menu_label = _("Partner Clubs")
    menu_order = 100
    add_to_admin_menu = False
    list_display = [
        "name",
        "short_code",
        "city",
        "base_url",
        "is_active",
        "is_approved",
        "share_our_events",
        "last_sync",
    ]
    list_filter = ["is_active", "is_approved", "share_our_events"]
    search_fields = ["name", "short_code", "city"]

    panels = [
        GuidePanel(FEDERATED_CLUB_GUIDE),
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("short_code"),
                FieldPanel("base_url"),
                FieldPanel("city"),
                FieldPanel("description"),
                FieldPanel("logo_url"),
            ],
            heading=_("Partner club"),
        ),
        MultiFieldPanel(
            [FieldPanel("api_key"), FieldPanel("our_key_for_them"), KeyToolsPanel()],
            heading=_("Link keys (identical on both sites)"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_approved"),
                FieldPanel("is_active"),
                FieldPanel("share_our_events"),
                FieldPanel("auto_import"),
            ],
            heading=_("Status and exchange"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("last_sync", read_only=True),
                FieldPanel("last_error", read_only=True),
                FieldPanel("created_at", read_only=True),
                FieldPanel("created_by", read_only=True),
            ],
            heading=_("Filled in by the system"),
        ),
    ]


class ExternalEventViewSet(SnippetViewSet):
    """Admin interface for viewing imported external events."""

    model = ExternalEvent
    icon = "calendar"
    menu_label = _("External Events")
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
    menu_label = _("Federation")
    menu_icon = "globe"
    menu_order = 700


register_snippet(FederationViewSetGroup)


@hooks.register("register_admin_urls")
def register_federation_admin_urls():
    return [
        path(
            "federation/generate-keys/",
            views_admin.generate_keys,
            name="federation_generate_keys",
        ),
        path(
            "federation/test-connection/<uuid:pk>/",
            views_admin.test_connection,
            name="federation_test_connection",
        ),
    ]


@hooks.register("after_create_snippet")
def set_partner_club_creator(request, instance):
    if isinstance(instance, FederatedClub) and instance.created_by_id is None:
        instance.created_by = request.user
        instance.save(update_fields=["created_by"])

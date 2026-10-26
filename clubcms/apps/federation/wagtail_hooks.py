"""
Wagtail hooks for the Federation admin interface.

Registers FederatedClub and ExternalEvent admin panels under
a "Federation" menu group in the Wagtail sidebar.
"""

from django import forms
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


class _PartnerToolsPanel(HelpPanel):
    """HelpPanel whose template knows whether the club is already saved.

    ``instance.pk`` is not enough: the UUID primary key is set before the
    first save.
    """

    class BoundPanel(HelpPanel.BoundPanel):
        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            context["saved"] = self.instance is not None and not self.instance._state.adding
            return context


class InboundCredentialPanel(_PartnerToolsPanel):
    """The access credential we issued: read-only, copy and regenerate."""

    def __init__(self, **kwargs):
        kwargs.setdefault("template", "admin/federation/inbound_credential_panel.html")
        super().__init__(**kwargs)


class ConnectionTestPanel(_PartnerToolsPanel):
    """"Test connection" button under the partner's credential."""

    def __init__(self, **kwargs):
        kwargs.setdefault("template", "admin/federation/connection_test_panel.html")
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
            [InboundCredentialPanel()],
            heading=_("Access we grant to this partner"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("outbound_key"),
                FieldPanel(
                    "outbound_secret",
                    widget=forms.PasswordInput(render_value=True, attrs={"autocomplete": "off"}),
                ),
                ConnectionTestPanel(),
            ],
            heading=_("Access this partner grants us"),
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
            "federation/regenerate-access/<uuid:pk>/",
            views_admin.regenerate_inbound,
            name="federation_regenerate_inbound",
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

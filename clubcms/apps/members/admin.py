"""
Wagtail admin integration for the members app.

Registers ClubUser via a Wagtail ModelViewSet with full list/filter/search
capabilities, accessible from the Wagtail admin sidebar through wagtail_hooks.
"""

from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.admin.viewsets.model import ModelViewSet

from apps.members.models import ClubUser, MembershipRequest
from apps.members.panels import CardActionsPanel, RequestActionsPanel


class ClubUserViewSet(ModelViewSet):
    """
    Wagtail ModelViewSet for managing ClubUser instances.

    Provides list, create, edit, and delete views within the
    Wagtail admin interface.
    """

    model = ClubUser
    icon = "user"
    menu_label = _("Members")
    menu_order = 200
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_per_page = 30
    exclude_form_fields = []

    list_display = [
        "username",
        "first_name",
        "last_name",
        "card_number",
        "membership_expiry",
        "is_active",
    ]
    list_filter = [
        "is_active",
        "show_in_directory",
        "public_profile",
        "newsletter",
        "aid_available",
        "digest_frequency",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name",
        "email",
        "card_number",
        "city",
    ]
    ordering = ["last_name", "first_name"]

    personal_panels = [
        FieldPanel("username"),
        FieldPanel("email"),
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("display_name"),
        FieldPanel("phone"),
        FieldPanel("mobile"),
        FieldPanel("birth_date"),
        FieldPanel("birth_place"),
        FieldPanel("photo"),
        FieldPanel("bio"),
    ]

    identity_panels = [
        FieldPanel("fiscal_code"),
        FieldPanel("document_type"),
        FieldPanel("document_number"),
        FieldPanel("document_expiry"),
    ]

    address_panels = [
        FieldPanel("address"),
        FieldPanel("city"),
        FieldPanel("province"),
        FieldPanel("postal_code"),
        FieldPanel("country"),
    ]

    membership_panels = [
        CardActionsPanel(),
        FieldPanel("card_number", read_only=True),
        FieldPanel("membership_date", read_only=True),
        FieldPanel("membership_expiry", read_only=True),
        FieldPanel("is_active"),
        FieldPanel("products"),
    ]

    privacy_panels = [
        FieldPanel("show_in_directory"),
        FieldPanel("public_profile"),
        FieldPanel("show_real_name_to_members"),
        FieldPanel("newsletter"),
    ]

    notification_panels = [
        FieldPanel("email_notifications"),
        FieldPanel("push_notifications"),
        FieldPanel("news_updates"),
        FieldPanel("event_updates"),
        FieldPanel("event_reminders"),
        FieldPanel("membership_alerts"),
        FieldPanel("partner_updates"),
        FieldPanel("aid_requests"),
        FieldPanel("partner_events"),
        FieldPanel("partner_event_comments"),
        FieldPanel("digest_frequency"),
    ]

    aid_panels = [
        FieldPanel("aid_available"),
        FieldPanel("aid_radius_km"),
        FieldPanel("aid_location_city"),
        FieldPanel("aid_coordinates"),
        FieldPanel("aid_notes"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(personal_panels, heading=_("Personal")),
            ObjectList(identity_panels, heading=_("Identity")),
            ObjectList(address_panels, heading=_("Address")),
            ObjectList(membership_panels, heading=_("Membership")),
            ObjectList(privacy_panels, heading=_("Privacy")),
            ObjectList(notification_panels, heading=_("Notifications")),
            ObjectList(aid_panels, heading=_("Mutual Aid")),
        ]
    )


clubuser_viewset = ClubUserViewSet("clubusers")


class MembershipRequestViewSet(ModelViewSet):
    """
    Wagtail ModelViewSet for managing membership requests.

    Allows admins to view, approve, and reject membership requests.
    """

    model = MembershipRequest
    icon = "form"
    menu_label = _("Membership Requests")
    menu_order = 210
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_per_page = 30

    list_display = [
        "user",
        "product",
        "status",
        "created_at",
        "processed_at",
    ]
    list_filter = [
        "status",
        "product",
    ]
    search_fields = [
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "product__name",
        "notes",
    ]
    ordering = ["-created_at"]

    panels = [
        RequestActionsPanel(),
        MultiFieldPanel(
            [
                FieldPanel("notes", read_only=True),
                FieldPanel("admin_notes"),
            ],
            heading=_("Notes"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("created_at", read_only=True),
                FieldPanel("processed_at", read_only=True),
                FieldPanel("processed_by", read_only=True),
            ],
            heading=_("Processing info"),
        ),
    ]


membership_request_viewset = MembershipRequestViewSet("membership_requests")

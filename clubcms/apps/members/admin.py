"""
Wagtail admin integration for the members app.

Registers ClubUser via a Wagtail ModelViewSet with full list/filter/search
capabilities, accessible from the Wagtail admin sidebar through wagtail_hooks.
"""

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.admin.viewsets.model import ModelViewSet

from apps.members.models import ClubUser


class ClubUserViewSet(ModelViewSet):
    """
    Wagtail ModelViewSet for managing ClubUser instances.

    Provides list, create, edit, and delete views within the
    Wagtail admin interface.
    """

    model = ClubUser
    icon = "user"
    menu_label = "Members"
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
        FieldPanel("card_number"),
        FieldPanel("membership_date"),
        FieldPanel("membership_expiry"),
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
            ObjectList(personal_panels, heading="Personal"),
            ObjectList(identity_panels, heading="Identity"),
            ObjectList(address_panels, heading="Address"),
            ObjectList(membership_panels, heading="Membership"),
            ObjectList(privacy_panels, heading="Privacy"),
            ObjectList(notification_panels, heading="Notifications"),
            ObjectList(aid_panels, heading="Mutual Aid"),
        ]
    )


clubuser_viewset = ClubUserViewSet("clubusers")

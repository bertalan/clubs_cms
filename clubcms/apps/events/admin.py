"""
Wagtail admin integration for the events app.

Registers EventRegistration via a Wagtail ModelViewSet with
list/filter/search capabilities for the Wagtail admin sidebar.
"""

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TabbedInterface, ObjectList
from wagtail.admin.viewsets.model import ModelViewSet

from apps.events.models import EventRegistration


class EventRegistrationViewSet(ModelViewSet):
    """
    Wagtail ModelViewSet for managing EventRegistration instances.

    Provides list, inspect, and edit views within the Wagtail admin.
    """

    model = EventRegistration
    icon = "calendar"
    menu_label = "Registrations"
    menu_order = 250
    add_to_admin_menu = True
    inspect_view_enabled = True
    list_per_page = 30
    exclude_form_fields = []

    list_display = [
        "event",
        "user",
        "status",
        "payment_status",
        "payment_provider",
        "registered_at",
    ]
    list_filter = [
        "status",
        "payment_status",
        "payment_provider",
    ]
    search_fields = [
        "user__username",
        "user__email",
        "user__first_name",
        "email",
        "first_name",
        "last_name",
        "payment_reference",
    ]
    ordering = ["-registered_at"]

    registration_panels = [
        FieldPanel("event"),
        FieldPanel("user"),
        FieldPanel("status"),
        FieldPanel("guests"),
        FieldPanel("guest_names"),
        FieldPanel("notes"),
    ]

    payment_panels = [
        FieldPanel("payment_status"),
        FieldPanel("payment_provider"),
        FieldPanel("payment_amount"),
        FieldPanel("payment_reference"),
        FieldPanel("payment_id"),
        FieldPanel("payment_session_id"),
        FieldPanel("payment_expires_at"),
    ]

    guest_panels = [
        FieldPanel("first_name"),
        FieldPanel("last_name"),
        FieldPanel("email"),
    ]

    passenger_panels = [
        FieldPanel("has_passenger"),
        FieldPanel("passenger_is_member"),
        FieldPanel("passenger_member"),
        FieldPanel("passenger_first_name"),
        FieldPanel("passenger_last_name"),
        FieldPanel("passenger_email"),
        FieldPanel("passenger_phone"),
        FieldPanel("passenger_fiscal_code"),
        FieldPanel("passenger_birth_date"),
        FieldPanel("passenger_emergency_contact"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(registration_panels, heading="Registration"),
            ObjectList(payment_panels, heading="Payment"),
            ObjectList(guest_panels, heading="Guest Info"),
            ObjectList(passenger_panels, heading="Passenger"),
        ]
    )


event_registration_viewset = EventRegistrationViewSet("eventregistrations")

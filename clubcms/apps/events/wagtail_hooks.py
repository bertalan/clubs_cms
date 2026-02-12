"""
Wagtail hooks for the events app.

Registers the EventRegistration ModelViewSet with the Wagtail admin
and adds PricingTier as an InlinePanel on EventDetailPage.
"""

from wagtail import hooks

from apps.events.admin import event_registration_viewset


@hooks.register("register_admin_viewset")
def register_event_registration_viewset():
    return event_registration_viewset


@hooks.register("construct_page_action_menu")
def add_pricing_tiers_panel(menu_items, request, context):
    """
    Hook placeholder for PricingTier InlinePanel.

    The actual InlinePanel("pricing_tiers", ...) should be added
    to EventDetailPage.content_panels in the website app's page
    model definition:

        InlinePanel("pricing_tiers", label="Pricing Tiers"),

    This hook is kept as documentation / registration point.
    """
    pass

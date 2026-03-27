"""
URL patterns for the events app.

Provides Django-served endpoints for non-HTML responses (webhooks,
JSON APIs, ICS exports) and external payment callbacks.  HTML views
have been migrated to EventsAreaPage (RoutablePageMixin).
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.events import views

app_name = "events"

urlpatterns = [
    # Stripe webhook (csrf_exempt, external)
    path(
        "payment/webhook/stripe/",
        views.StripeWebhookView.as_view(),
        name="stripe_webhook",
    ),
    # PayPal return callback
    path(
        _("payment/<int:pk>/paypal-return/"),
        views.PayPalReturnView.as_view(),
        name="paypal_return",
    ),
    # Favorite toggle (JSON)
    path(
        _("favorite/<int:event_pk>/"),
        views.ToggleFavoriteView.as_view(),
        name="toggle_favorite",
    ),
    # ICS exports (binary)
    path(
        _("ics/<int:event_pk>/"),
        views.EventICSView.as_view(),
        name="event_ics",
    ),
    path(
        _("my-events/calendar.ics"),
        views.MyEventsICSView.as_view(),
        name="my_events_ics",
    ),
    path(
        _("calendar.ics"),
        views.AllEventsICSView.as_view(),
        name="all_events_ics",
    ),
]

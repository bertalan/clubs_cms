"""
URL patterns for the events app.

Registered with app_name="events" and included at /events/ in
the root URL conf.
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.events import views

app_name = "events"

urlpatterns = [
    # Registration
    path(
        _("register/<int:event_pk>/"),
        views.EventRegisterView.as_view(),
        name="register",
    ),
    path(
        _("cancel/<int:pk>/"),
        views.EventCancelView.as_view(),
        name="cancel",
    ),
    # Payment
    path(
        _("payment/<int:pk>/"),
        views.PaymentChoiceView.as_view(),
        name="payment_choice",
    ),
    path(
        _("payment/<int:pk>/bank-transfer/"),
        views.BankTransferInstructionsView.as_view(),
        name="bank_transfer_instructions",
    ),
    path(
        _("payment/<int:pk>/success/"),
        views.PaymentSuccessView.as_view(),
        name="payment_success",
    ),
    path(
        _("payment/<int:pk>/cancel/"),
        views.PaymentCancelView.as_view(),
        name="payment_cancel",
    ),
    path(
        "payment/webhook/stripe/",
        views.StripeWebhookView.as_view(),
        name="stripe_webhook",
    ),
    path(
        _("payment/<int:pk>/paypal-return/"),
        views.PayPalReturnView.as_view(),
        name="paypal_return",
    ),
    # User's registrations
    path(
        _("my-registrations/"),
        views.MyRegistrationsView.as_view(),
        name="my_registrations",
    ),
    # Favorites
    path(
        _("my-events/"),
        views.MyEventsView.as_view(),
        name="my_events",
    ),
    path(
        _("my-events/archive/"),
        views.MyEventsArchiveView.as_view(),
        name="my_events_archive",
    ),
    path(
        _("my-events/calendar.ics"),
        views.MyEventsICSView.as_view(),
        name="my_events_ics",
    ),
    path(
        _("favorite/<int:event_pk>/"),
        views.ToggleFavoriteView.as_view(),
        name="toggle_favorite",
    ),
    # ICS export
    path(
        _("ics/<int:event_pk>/"),
        views.EventICSView.as_view(),
        name="event_ics",
    ),
]

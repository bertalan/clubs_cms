"""
Unit tests for apps/events/signals.py

Tests notification creation on EventRegistration post_save.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.events.models import EventRegistration

User = get_user_model()


def _create_event_page(**kwargs):
    """Create a minimal EventDetailPage for testing."""
    from wagtail.models import Page

    from apps.website.models.pages import EventDetailPage

    defaults = {
        "title": "Signal Test Event",
        "slug": "signal-test-event",
        "start_date": timezone.now() + timedelta(days=30),
    }
    defaults.update(kwargs)

    root = Page.objects.first()
    event = EventDetailPage(**defaults)
    root.add_child(instance=event)
    return event


@pytest.mark.django_db
class TestRegistrationSignals:
    """Tests for EventRegistration post_save signal."""

    @patch("apps.notifications.services.create_notification")
    def test_notification_created_for_authenticated_user(self, mock_notify):
        """Notification is sent when an authenticated user registers."""
        event = _create_event_page()
        user = User.objects.create_user(
            username="sig_test1", password="testpass123456"
        )

        EventRegistration.objects.create(
            event=event,
            user=user,
            payment_status="pending",
            payment_amount=Decimal("0.00"),
        )

        mock_notify.assert_called_once()
        call_kwargs = mock_notify.call_args[1]
        assert call_kwargs["notification_type"] == "event_registered"
        assert user in call_kwargs["recipients"]

    @patch("apps.events.signals._send_guest_confirmation_email")
    def test_guest_email_sent_for_guest_registration(self, mock_email):
        """Guest confirmation email is sent for non-authenticated users."""
        event = _create_event_page(slug="signal-test-event-guest")

        EventRegistration.objects.create(
            event=event,
            user=None,
            email="guest@example.com",
            first_name="Guest",
            last_name="User",
            payment_amount=Decimal("0.00"),
        )

        mock_email.assert_called_once()

    @patch("apps.notifications.services.create_notification")
    def test_signal_not_fired_on_update(self, mock_notify):
        """Signal only fires on created=True, not on updates."""
        event = _create_event_page(slug="signal-test-event-update")
        user = User.objects.create_user(
            username="sig_test2", password="testpass123456"
        )

        reg = EventRegistration.objects.create(
            event=event,
            user=user,
            payment_amount=Decimal("0.00"),
        )
        mock_notify.reset_mock()

        reg.notes = "Updated notes"
        reg.save()

        mock_notify.assert_not_called()

"""
Unit tests for apps/events/tasks.py

Tests expire_pending_bank_transfers using database records.
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.events.models import EventRegistration
from apps.events.tasks import expire_pending_bank_transfers

User = get_user_model()


def _create_event_page(**kwargs):
    """Create a minimal EventDetailPage for testing."""
    from wagtail.models import Page

    from apps.website.models.pages import EventDetailPage

    defaults = {
        "title": "Test Event",
        "slug": "test-event-tasks",
        "start_date": timezone.now() + timedelta(days=30),
    }
    defaults.update(kwargs)

    root = Page.objects.first()
    event = EventDetailPage(**defaults)
    root.add_child(instance=event)
    return event


@pytest.mark.django_db
class TestExpirePendingBankTransfers:
    """Tests for expire_pending_bank_transfers task."""

    @patch("apps.events.tasks.promote_from_waitlist")
    @patch("apps.notifications.services.create_notification")
    def test_expires_overdue_bank_transfers(self, mock_notify, mock_promote):
        """Registrations past payment_expires_at are marked expired+cancelled."""
        event = _create_event_page()
        user = User.objects.create_user(
            username="task_test1", password="testpass123456"
        )

        reg = EventRegistration.objects.create(
            event=event,
            user=user,
            payment_provider="bank_transfer",
            payment_status="pending",
            payment_expires_at=timezone.now() - timedelta(hours=1),
            payment_amount=Decimal("50.00"),
            payment_reference="EVT-00001-ABCD",
        )

        count = expire_pending_bank_transfers()

        reg.refresh_from_db()
        assert count == 1
        assert reg.payment_status == "expired"
        assert reg.status == "cancelled"
        mock_promote.assert_called_once()

    @patch("apps.events.tasks.promote_from_waitlist")
    @patch("apps.notifications.services.create_notification")
    def test_does_not_expire_future_transfers(self, mock_notify, mock_promote):
        """Registrations with future expires_at are left alone."""
        event = _create_event_page(slug="test-event-tasks-future")
        user = User.objects.create_user(
            username="task_test2", password="testpass123456"
        )

        reg = EventRegistration.objects.create(
            event=event,
            user=user,
            payment_provider="bank_transfer",
            payment_status="pending",
            payment_expires_at=timezone.now() + timedelta(days=3),
            payment_amount=Decimal("50.00"),
        )

        count = expire_pending_bank_transfers()

        reg.refresh_from_db()
        assert count == 0
        assert reg.payment_status == "pending"
        assert reg.status == "registered"

    @patch("apps.events.tasks.promote_from_waitlist")
    @patch("apps.notifications.services.create_notification")
    def test_ignores_non_bank_transfer(self, mock_notify, mock_promote):
        """Only bank_transfer provider registrations are expired."""
        event = _create_event_page(slug="test-event-tasks-stripe")
        user = User.objects.create_user(
            username="task_test3", password="testpass123456"
        )

        EventRegistration.objects.create(
            event=event,
            user=user,
            payment_provider="stripe",
            payment_status="pending",
            payment_expires_at=timezone.now() - timedelta(hours=1),
            payment_amount=Decimal("50.00"),
        )

        count = expire_pending_bank_transfers()
        assert count == 0

    @patch("apps.events.tasks.promote_from_waitlist")
    @patch("apps.notifications.services.create_notification")
    def test_ignores_already_paid(self, mock_notify, mock_promote):
        """Already-paid bank transfers are not expired."""
        event = _create_event_page(slug="test-event-tasks-paid")
        user = User.objects.create_user(
            username="task_test4", password="testpass123456"
        )

        reg = EventRegistration.objects.create(
            event=event,
            user=user,
            payment_provider="bank_transfer",
            payment_status="paid",
            payment_expires_at=timezone.now() - timedelta(hours=1),
            payment_amount=Decimal("50.00"),
        )

        count = expire_pending_bank_transfers()

        reg.refresh_from_db()
        assert count == 0
        assert reg.payment_status == "paid"

"""
Shared fixtures for the payment tests (views and Stripe SDK).
"""

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.events.models import EventRegistration

User = get_user_model()


@pytest.fixture
def events_area_page(db):
    """Create an EventsAreaPage under the default site root for URL resolution."""
    from wagtail.models import Page, Site

    from apps.website.models.pages import EventsAreaPage

    # Clear Wagtail's Site root paths cache to avoid stale entries from other test classes
    Site.clear_site_root_paths_cache()

    site = Site.objects.filter(is_default_site=True).first()
    parent = site.root_page if site else Page.objects.first()
    page = EventsAreaPage(title="Events Area", slug="events-area")
    parent.add_child(instance=page)
    return page


def _create_event_page(**kwargs):
    """Create a minimal EventDetailPage for testing."""
    from wagtail.models import Page

    from apps.website.models.pages import EventDetailPage

    defaults = {
        "title": "Paid Event",
        "start_date": timezone.now() + timedelta(days=30),
        "base_fee": Decimal("50.00"),
        "registration_open": True,
        "max_attendees": 100,
    }
    defaults.update(kwargs)

    # Ensure unique slug
    if "slug" not in defaults:
        import uuid

        defaults["slug"] = f"paid-event-{uuid.uuid4().hex[:8]}"

    root = Page.objects.first()
    event = EventDetailPage(**defaults)
    root.add_child(instance=event)
    return event


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="paytest", password="testpass123456", email="pay@test.com"
    )


@pytest.fixture
def event_page(db):
    return _create_event_page()


@pytest.fixture
def registration(db, user, event_page):
    with patch("apps.notifications.services.create_notification"):
        return EventRegistration.objects.create(
            event=event_page,
            user=user,
            payment_amount=Decimal("50.00"),
            payment_status="pending",
        )


@pytest.fixture
def payment_settings(db):
    from wagtail.models import Site

    from apps.website.models.settings import PaymentSettings

    site = Site.objects.get(is_default_site=True)
    ps, _ = PaymentSettings.objects.get_or_create(site=site)
    ps.payment_mode = "test"
    ps.stripe_test_enabled = True
    ps.stripe_test_public_key = "pk_test_xxx"
    ps.stripe_test_secret_key = "sk_test_xxx"
    ps.stripe_test_webhook_secret = "whsec_test_xxx"
    ps.paypal_test_enabled = True
    ps.paypal_test_client_id = "paypal_test_id"
    ps.paypal_test_secret = "paypal_test_secret"
    ps.bank_transfer_enabled = True
    ps.bank_iban = "IT60X0542811101000000123456"
    ps.bank_transfer_expiry_days = 5
    ps.save()
    return ps

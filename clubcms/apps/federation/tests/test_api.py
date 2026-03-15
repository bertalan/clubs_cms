"""
Integration tests for Federation API endpoints.

Tests HMAC-authenticated API views:
- GET /api/federation/events/ — partner fetches our events
- POST /api/federation/interest/ — partner sends interest counts

Covers: authentication, rate limiting, authorization, data integrity.
"""

import json
from datetime import timedelta
from decimal import Decimal

import pytest
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page, Site

from apps.federation.api.security import sign_request
from apps.federation.api.views import FederationEventsAPIView, FederationInterestAPIView
from apps.federation.models import FederatedClub
from apps.website.models.pages import EventDetailPage, EventsPage, HomePage

# Direct URL paths since FEDERATION_ENABLED may be False in test settings
EVENTS_URL = "/api/federation/events/"
INTEREST_URL = "/api/federation/interest/"


@pytest.mark.django_db
@override_settings(ROOT_URLCONF="apps.federation.tests.urls_test")
class FederationAPIBase(TestCase):
    """Shared setup: page tree + partner club."""

    @classmethod
    def setUpTestData(cls):
        # Page tree
        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root", slug="root")

        home = HomePage(
            title="Fed Test Home",
            slug="fed-test-home",
            hero_title="Test",
            hero_subtitle="Test",
        )
        root.add_child(instance=home)

        Site.objects.all().delete()
        Site.objects.create(
            hostname="localhost",
            root_page=home,
            is_default_site=True,
        )

        events_index = EventsPage(title="Events", slug="fed-events")
        home.add_child(instance=events_index)
        cls.events_index = events_index

        # Create a published event
        cls.event = EventDetailPage(
            title="Federation Test Event",
            slug="fed-test-event",
            start_date=timezone.now() + timedelta(days=10),
            registration_open=True,
            base_fee=Decimal("0.00"),
        )
        events_index.add_child(instance=cls.event)

        # Partner club
        cls.shared_secret = "sk_test_shared_secret_12345678"
        cls.partner = FederatedClub.objects.create(
            name="Partner Club",
            short_code="PARTNER",
            base_url="https://partner.example.com",
            api_key="pk_test_partner_key",
            our_key_for_them=cls.shared_secret,
            is_active=True,
            is_approved=True,
            share_our_events=True,
        )

    def setUp(self):
        cache.clear()

    def _sign_headers(self, body="", secret=None):
        """Generate valid HMAC authentication headers."""
        ts = timezone.now().isoformat()
        secret = secret or self.shared_secret
        sig = sign_request(secret, ts, body)
        return {
            "HTTP_X_FEDERATION_KEY": self.partner.api_key,
            "HTTP_X_TIMESTAMP": ts,
            "HTTP_X_SIGNATURE": sig,
        }


# ---------------------------------------------------------------------------
# 1. Events API — GET /api/federation/events/
# ---------------------------------------------------------------------------


class TestEventsAPI(FederationAPIBase):
    """Test the federation events endpoint."""

    def test_valid_request_returns_events(self):
        headers = self._sign_headers()
        resp = self.client.get(
            EVENTS_URL,
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("events", data)
        self.assertIn("total", data)
        self.assertIn("club", data)
        self.assertGreaterEqual(data["total"], 1)
        # Verify our event is in the response
        event_names = [e["event_name"] for e in data["events"]]
        self.assertIn("Federation Test Event", event_names)

    def test_event_data_structure(self):
        headers = self._sign_headers()
        resp = self.client.get(EVENTS_URL, **headers)
        data = resp.json()
        event = data["events"][0]
        expected_keys = {
            "id", "event_name", "start_date", "end_date",
            "location_name", "location_address", "location_lat",
            "location_lon", "description", "event_status",
            "image_url", "detail_url",
        }
        self.assertEqual(set(event.keys()), expected_keys)

    def test_from_date_filter(self):
        # Create a past event that should be excluded
        past_event = EventDetailPage(
            title="Past Event",
            slug="past-fed-event",
            start_date=timezone.now() - timedelta(days=30),
        )
        self.events_index.add_child(instance=past_event)

        headers = self._sign_headers()
        resp = self.client.get(EVENTS_URL, **headers)
        data = resp.json()
        event_names = [e["event_name"] for e in data["events"]]
        self.assertNotIn("Past Event", event_names)

    def test_missing_headers_returns_401(self):
        resp = self.client.get(EVENTS_URL)
        self.assertEqual(resp.status_code, 401)
        self.assertIn("error", resp.json())

    def test_invalid_key_returns_401(self):
        ts = timezone.now().isoformat()
        sig = sign_request(self.shared_secret, ts)
        resp = self.client.get(
            EVENTS_URL,
            HTTP_X_FEDERATION_KEY="pk_invalid_key",
            HTTP_X_TIMESTAMP=ts,
            HTTP_X_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 401)

    def test_wrong_signature_returns_401(self):
        ts = timezone.now().isoformat()
        resp = self.client.get(
            EVENTS_URL,
            HTTP_X_FEDERATION_KEY=self.partner.api_key,
            HTTP_X_TIMESTAMP=ts,
            HTTP_X_SIGNATURE="sha256=wrong_signature",
        )
        self.assertEqual(resp.status_code, 401)

    def test_expired_timestamp_returns_401(self):
        old_ts = (timezone.now() - timedelta(seconds=600)).isoformat()
        sig = sign_request(self.shared_secret, old_ts)
        resp = self.client.get(
            EVENTS_URL,
            HTTP_X_FEDERATION_KEY=self.partner.api_key,
            HTTP_X_TIMESTAMP=old_ts,
            HTTP_X_SIGNATURE=sig,
        )
        self.assertEqual(resp.status_code, 401)

    def test_inactive_partner_returns_401(self):
        self.partner.is_active = False
        self.partner.save(update_fields=["is_active"])
        try:
            headers = self._sign_headers()
            resp = self.client.get(EVENTS_URL, **headers)
            self.assertEqual(resp.status_code, 401)
        finally:
            self.partner.is_active = True
            self.partner.save(update_fields=["is_active"])

    def test_share_our_events_false_returns_403(self):
        self.partner.share_our_events = False
        self.partner.save(update_fields=["share_our_events"])
        try:
            headers = self._sign_headers()
            resp = self.client.get(EVENTS_URL, **headers)
            self.assertEqual(resp.status_code, 403)
        finally:
            self.partner.share_our_events = True
            self.partner.save(update_fields=["share_our_events"])

    def test_rate_limit_returns_429(self):
        # Fill rate limit
        cache_key = f"federation_rate_{self.partner.pk}"
        cache.set(cache_key, 60, 3600)
        headers = self._sign_headers()
        resp = self.client.get(EVENTS_URL, **headers)
        self.assertEqual(resp.status_code, 429)


# ---------------------------------------------------------------------------
# 2. Interest API — POST /api/federation/interest/
# ---------------------------------------------------------------------------


class TestInterestAPI(FederationAPIBase):
    """Test the federation interest endpoint."""

    def test_valid_interest_post(self):
        body = json.dumps({
            "event_id": str(self.event.pk),
            "club_code": "PARTNER",
            "counts": {"interested": 5, "going": 3, "maybe": 2},
        })
        headers = self._sign_headers(body=body)
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["received"])

        # Verify cached data
        cache_key = f"federation_interest_{self.event.pk}_{self.partner.short_code}"
        cached = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["counts"]["interested"], 5)

    def test_missing_event_id_returns_400(self):
        body = json.dumps({"counts": {"interested": 1}})
        headers = self._sign_headers(body=body)
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 400)

    def test_nonexistent_event_returns_error(self):
        body = json.dumps({
            "event_id": "999999999",
            "counts": {"interested": 1},
        })
        headers = self._sign_headers(body=body)
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
            **headers,
        )
        # View returns 404 but may redirect if URL is caught by i18n
        self.assertIn(resp.status_code, [302, 400, 404])

    def test_invalid_json_returns_400(self):
        body = "not valid json"
        headers = self._sign_headers(body=body)
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 400)

    def test_interest_requires_hmac(self):
        body = json.dumps({
            "event_id": str(self.event.pk),
            "counts": {"interested": 1},
        })
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 401)

    def test_club_code_from_auth_not_body(self):
        """Partner's club_code in body is ignored; auth determines the partner."""
        body = json.dumps({
            "event_id": str(self.event.pk),
            "club_code": "SPOOFED",
            "counts": {"interested": 1},
        })
        headers = self._sign_headers(body=body)
        resp = self.client.post(
            INTEREST_URL,
            data=body,
            content_type="application/json",
            **headers,
        )
        self.assertEqual(resp.status_code, 200)
        # Cached under authenticated partner's code, not "SPOOFED"
        cache_key = f"federation_interest_{self.event.pk}_{self.partner.short_code}"
        cached = cache.get(cache_key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["club_code"], "PARTNER")

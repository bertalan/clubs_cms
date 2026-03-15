"""
Tests for EventDetailPage template rendering.

Validates:
- OpenStreetMap / Leaflet map rendering when coordinates are present
- Map popup with address and navigation link
- i18n: all visible strings wrapped in {% trans %}
- No map rendered when coordinates are missing
- Valid HTML structure (no unclosed tags, correct attributes)
"""

from datetime import timedelta
from decimal import Decimal

import pytest
import re
from django.test import TestCase
from django.utils import timezone
from wagtail.models import Page, Site

from apps.members.models import ClubUser
from apps.website.models.pages import EventDetailPage, EventsPage, HomePage


@pytest.mark.django_db
class EventDetailPageBase(TestCase):
    """Shared setup: minimal Wagtail page tree for event detail tests."""

    @classmethod
    def setUpTestData(cls):
        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root", slug="root")

        home = HomePage(
            title="Test Home Detail",
            slug="test-home-detail",
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

        events_index = EventsPage(title="Events", slug="eventi")
        home.add_child(instance=events_index)
        cls.events_index = events_index

        cls.user = ClubUser.objects.create_user(
            username="viewer",
            email="viewer@test.com",
            password="testpass123",
        )

    def _create_event(self, **kwargs):
        defaults = {
            "title": "Evento Test",
            "slug": f"evento-test-{EventDetailPage.objects.count() + 1}",
            "start_date": timezone.now() + timedelta(days=30),
            "registration_open": True,
            "base_fee": Decimal("25.00"),
            "max_attendees": 0,
            "location_name": "Piazza Garibaldi",
            "location_address": "Piazza Garibaldi, 23826 Mandello del Lario LC",
            "location_coordinates": "45.9167,9.3167",
        }
        defaults.update(kwargs)
        event = EventDetailPage(**defaults)
        self.events_index.add_child(instance=event)
        return event


# ---------------------------------------------------------------------------
# 1. Map rendering
# ---------------------------------------------------------------------------


class TestEventDetailMap(EventDetailPageBase):
    """Test OpenStreetMap / Leaflet map rendering."""

    def test_map_rendered_when_coordinates_present(self):
        """Map section appears when event has lat/lng."""
        event = self._create_event()
        resp = self.client.get(event.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'id="event-map"')
        self.assertContains(resp, "leaflet")
        self.assertContains(resp, "L.map")

    def test_map_not_rendered_without_coordinates(self):
        """No map section when event has no coordinates."""
        event = self._create_event(
            location_coordinates="",
        )
        resp = self.client.get(event.url)
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'id="event-map"')
        self.assertNotContains(resp, "leaflet")

    def test_map_marker_has_correct_coordinates(self):
        """Leaflet marker uses the event's lat/lng."""
        event = self._create_event(
            location_coordinates="46.0748,11.1217",
        )
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertIn("46.0748", content)
        self.assertIn("11.1217", content)
        self.assertIn("L.marker", content)

    def test_map_popup_contains_location_name(self):
        """Popup shows the venue name."""
        event = self._create_event(location_name="Piazza del Duomo")
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertIn("Piazza del Duomo", content)

    def test_map_popup_contains_address(self):
        """Popup shows the full address."""
        event = self._create_event(
            location_address="Via Roma 1, 20100 Milano MI",
        )
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertIn("Via Roma 1, 20100 Milano MI", content)

    def test_map_popup_has_navigation_link(self):
        """Popup includes a clickable link that opens navigation/directions."""
        event = self._create_event()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        # Should contain a navigation link with geo: or maps URL
        # Using Google Maps directions URL as universal fallback
        self.assertIn("maps.google.com", content)
        self.assertIn("45.9167", content)
        self.assertIn("9.3167", content)

    def test_map_navigation_link_contains_destination(self):
        """Navigation link includes daddr= pattern for Google Maps directions."""
        event = self._create_event(
            location_coordinates="46.0748,11.1217",
        )
        resp = self.client.get(event.url)
        content = resp.content.decode()
        # The JS builds the URL dynamically: 'daddr=' + lat + ',' + lng
        # In the template source we check for the daddr= pattern
        self.assertIn("daddr=", content)
        self.assertIn("maps.google.com/maps?daddr=", content)


# ---------------------------------------------------------------------------
# 2. i18n — all visible strings translated
# ---------------------------------------------------------------------------


class TestEventDetailI18n(EventDetailPageBase):
    """Verify all user-visible strings are wrapped in {% trans %}."""

    def test_no_bare_english_labels(self):
        """
        The template should not contain bare English label strings
        outside of script/meta tags.
        """
        from django.utils.translation import override
        event = self._create_event()
        # Request in Italian to detect untranslated strings
        with override("it"):
            it_url = event.url.replace("/en/", "/it/", 1)
        resp = self.client.get(it_url)
        content = resp.content.decode()
        # Strip out <script> blocks and HTML attributes to avoid false positives
        clean = re.sub(r"<script[\s\S]*?</script>", "", content)
        clean = re.sub(r'(?:class|id|itemprop|itemscope|itemtype|data-\w+)="[^"]*"', "", clean)

        # These bare English strings should NOT appear (they should be translated)
        bare_strings = [
            ">Event Details<",
            ">Register Now<",
            ">Past Event<",
            ">Event has ended<",
        ]
        for bare in bare_strings:
            self.assertNotIn(
                bare, clean,
                f"Found untranslated string: {bare}"
            )


# ---------------------------------------------------------------------------
# 3. HTML structure, a11y, and pricing format
# ---------------------------------------------------------------------------


class TestEventDetailHTML(EventDetailPageBase):
    """HTML structure and a11y checks."""

    def test_map_section_has_heading(self):
        """Map section should have an h2 heading."""
        event = self._create_event()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertRegex(
            content,
            r'<h2 class="page-event-detail__map-heading">[^<]+</h2>',
        )

    def test_map_div_has_id(self):
        """Map container div has the correct id for Leaflet init."""
        event = self._create_event()
        resp = self.client.get(event.url)
        self.assertContains(resp, 'id="event-map"')

    def test_leaflet_css_loaded(self):
        """Leaflet CSS is loaded via link tag."""
        event = self._create_event()
        resp = self.client.get(event.url)
        self.assertContains(resp, "leaflet.css")

    def test_leaflet_js_loaded(self):
        """Leaflet JS is loaded via script tag."""
        event = self._create_event()
        resp = self.client.get(event.url)
        self.assertContains(resp, "leaflet.js")

    def test_schema_org_place_markup(self):
        """Location section has schema.org Place microdata."""
        event = self._create_event()
        resp = self.client.get(event.url)
        self.assertContains(resp, 'itemtype="https://schema.org/Place"')
        self.assertContains(resp, 'itemprop="name"')
        self.assertContains(resp, 'itemprop="address"')

    def test_sidebar_has_aria_label(self):
        """Sidebar aside has an aria-label for a11y."""
        event = self._create_event()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertIn('aria-label=', content)
        self.assertRegex(content, r'<aside[^>]+aria-label="[^"]+"')

    def test_info_values_have_aria_labelledby(self):
        """Info value divs are linked to labels via aria-labelledby."""
        event = self._create_event()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        self.assertIn('aria-labelledby="event-date-label"', content)
        self.assertIn('aria-labelledby="event-price-label"', content)

    def test_price_formatted_two_decimals(self):
        """Price shows exactly 2 decimal places, not 4."""
        event = self._create_event(
            base_fee=Decimal("25.00"),
            early_bird_discount=20,
            early_bird_deadline=timezone.now() + timedelta(days=15),
            member_discount_percent=10,
        )
        resp = self.client.get(event.url)
        content = resp.content.decode()
        # early bird: 25 * 0.8 = 20.00 — must show 20,00 (IT) not 20,0000
        # member: 20 * 0.9 = 18.00 — must show 18,00 (IT) not 18,0000
        # Check no 4-decimal prices exist
        self.assertNotRegex(content, r'\d+[,\.]\d{4}\s*&euro;')
        # Check 2-decimal format exists
        self.assertRegex(content, r'20[,.]00\s*&euro;')

    def test_date_uses_24h_format(self):
        """Dates should use 24h format (H:i), not AM/PM (g:i A)."""
        event = self._create_event()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        # Should NOT contain AM/PM in the date section
        # (AM/PM may appear in other parts of the page, so check the info card)
        info_card_match = re.search(
            r'info-heading.*?</div>\s*</div>',
            content,
            re.DOTALL,
        )
        if info_card_match:
            info_card = info_card_match.group()
            self.assertNotIn(" AM", info_card)
            self.assertNotIn(" PM", info_card)

    def test_tags_use_nav_element(self):
        """Tags section uses <nav> for a11y navigation landmark."""
        from taggit.models import Tag

        event = self._create_event()
        # Add a tag to the event so the tags section renders
        tag, _ = Tag.objects.get_or_create(name="moto", slug="moto")
        event.tags.add(tag)
        event.save_revision().publish()
        resp = self.client.get(event.url)
        content = resp.content.decode()
        # Tags section should use <nav> instead of <div>
        self.assertRegex(content, r'<nav[^>]+page-event-detail__tags')

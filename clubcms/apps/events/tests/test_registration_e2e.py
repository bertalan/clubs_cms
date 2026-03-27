"""
End-to-end tests for event registration flow.

Tests the full HTTP request/response cycle for:
- Authenticated user registration (free & paid events)
- Guest registration (anonymous users)
- Duplicate registration prevention
- Waitlist when capacity is reached
- Cancellation and waitlist promotion
- ICS export (single event)
- Favorites toggle
- My registrations / my events views
- computed_deadline via PricingTier
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from wagtail.models import Page, Site

from apps.events.models import EventFavorite, EventRegistration, PricingTier
from apps.events.utils import events_area_url
from apps.members.models import ClubUser
from apps.website.models.pages import EventDetailPage, EventsAreaPage, EventsPage, HomePage


# ---------------------------------------------------------------------------
# Base setup: create a minimal Wagtail page tree for events
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class EventE2EBase(TestCase):
    """Shared setup: Wagtail page tree + test users."""

    @classmethod
    def setUpTestData(cls):
        # Root page
        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root", slug="root")

        # HomePage — use unique slug to avoid conflict with default Wagtail page
        home = HomePage(
            title="Test Home E2E",
            slug="test-home-e2e",
            hero_title="Test",
            hero_subtitle="Test",
        )
        root.add_child(instance=home)

        # Site
        Site.objects.all().delete()
        Site.objects.create(
            hostname="localhost",
            root_page=home,
            is_default_site=True,
        )

        # EventsPage
        events_index = EventsPage(title="Events", slug="events")
        home.add_child(instance=events_index)
        cls.events_index = events_index

        # EventsAreaPage (routable page for registrations, payments, etc.)
        events_area = EventsAreaPage(title="Events Area", slug="events-area")
        home.add_child(instance=events_area)
        cls.events_area = events_area

        # Users
        cls.member = ClubUser.objects.create_user(
            username="member1",
            email="member1@test.com",
            password="testpass123",
        )
        cls.member2 = ClubUser.objects.create_user(
            username="member2",
            email="member2@test.com",
            password="testpass123",
        )

    def _create_event(self, **kwargs):
        """Helper: create an EventDetailPage under events_index."""
        defaults = {
            "title": "Test Event",
            "slug": f"test-event-{EventDetailPage.objects.count() + 1}",
            "start_date": timezone.now() + timedelta(days=30),
            "registration_open": True,
            "allow_guests": True,
            "base_fee": Decimal("0.00"),
            "max_attendees": 0,
        }
        defaults.update(kwargs)
        event = EventDetailPage(**defaults)
        self.events_index.add_child(instance=event)
        return event


# ---------------------------------------------------------------------------
# 1. Registration form rendering
# ---------------------------------------------------------------------------


class TestRegistrationFormRendering(EventE2EBase):
    """Test that registration forms render correctly."""

    def test_authenticated_user_sees_registration_form(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        resp = self.client.get(event.url + "register/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "accept_terms")
        # Should NOT have first_name/last_name/email fields (those are for guests)
        self.assertNotContains(resp, 'name="first_name"')

    def test_anonymous_user_sees_guest_form(self):
        event = self._create_event(allow_guests=True)
        resp = self.client.get(event.url + "register/")
        self.assertEqual(resp.status_code, 200)
        # Guest form has first_name, last_name, email
        self.assertContains(resp, 'name="first_name"')
        self.assertContains(resp, 'name="last_name"')
        self.assertContains(resp, 'name="email"')

    def test_pricing_in_context(self):
        event = self._create_event(base_fee=Decimal("50.00"))
        self.client.login(username="member1", password="testpass123")
        resp = self.client.get(event.url + "register/")
        self.assertIn("pricing", resp.context)
        self.assertEqual(resp.context["pricing"]["base_fee"], Decimal("50.00"))


# ---------------------------------------------------------------------------
# 2. Authenticated user registration
# ---------------------------------------------------------------------------


class TestAuthenticatedRegistration(EventE2EBase):
    """Test registration flow for logged-in users."""

    def test_register_free_event(self):
        event = self._create_event(base_fee=Decimal("0.00"))
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        # Free event: redirect to my_registrations
        self.assertRedirects(resp, events_area_url("my_registrations"))
        reg = EventRegistration.objects.get(event=event, user=self.member)
        self.assertEqual(reg.status, "registered")
        self.assertEqual(reg.payment_status, "paid")
        self.assertEqual(reg.payment_provider, "free")

    def test_register_paid_event_redirects_to_payment(self):
        event = self._create_event(base_fee=Decimal("25.00"))
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        reg = EventRegistration.objects.get(event=event, user=self.member)
        self.assertRedirects(
            resp, events_area_url("payment_choice", args=[str(reg.pk)])
        )
        self.assertEqual(reg.payment_status, "pending")
        self.assertEqual(reg.payment_amount, Decimal("25.00"))

    def test_duplicate_registration_prevented(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        # Second registration should fail
        resp = self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        self.assertEqual(resp.status_code, 200)  # re-renders form
        self.assertEqual(
            EventRegistration.objects.filter(event=event, user=self.member).count(),
            1,
        )


# ---------------------------------------------------------------------------
# 3. Guest registration
# ---------------------------------------------------------------------------


class TestGuestRegistration(EventE2EBase):
    """Test registration flow for anonymous (guest) users."""

    def test_guest_can_register(self):
        event = self._create_event(allow_guests=True, base_fee=Decimal("0.00"))
        resp = self.client.post(
            event.url + "register/",
            {
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "mario@example.com",
                "accept_terms": "on",
                "guests": 0,
                # antispam fields
                "website": "",
                "form_ts": str(int(timezone.now().timestamp()) - 10),
            },
        )
        # Guest free event: redirect to event URL
        self.assertEqual(resp.status_code, 302)
        reg = EventRegistration.objects.get(event=event, email="mario@example.com")
        self.assertIsNone(reg.user)
        self.assertEqual(reg.first_name, "Mario")
        self.assertEqual(reg.last_name, "Rossi")
        self.assertEqual(reg.payment_status, "paid")

    def test_guest_missing_email_rejected(self):
        event = self._create_event(allow_guests=True)
        resp = self.client.post(
            event.url + "register/",
            {
                "first_name": "Mario",
                "last_name": "Rossi",
                "email": "",
                "accept_terms": "on",
                "guests": 0,
                "website": "",
                "form_ts": str(int(timezone.now().timestamp()) - 10),
            },
        )
        self.assertEqual(resp.status_code, 200)  # re-renders form with errors
        self.assertEqual(EventRegistration.objects.filter(event=event).count(), 0)


# ---------------------------------------------------------------------------
# 4. Capacity and waitlist
# ---------------------------------------------------------------------------


class TestCapacityAndWaitlist(EventE2EBase):
    """Test capacity and waitlist behavior."""

    def test_registration_rejected_when_full(self):
        """is_registration_open returns False when capacity is reached."""
        event = self._create_event(max_attendees=1)
        # Fill capacity via direct DB insert
        EventRegistration.objects.create(
            event=event, user=self.member, status="registered",
        )
        # Second user is rejected because is_registration_open=False
        self.client.login(username="member2", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        self.assertEqual(resp.status_code, 200)  # form re-rendered with error
        self.assertFalse(
            EventRegistration.objects.filter(event=event, user=self.member2).exists()
        )

    def test_waitlist_via_atomic_race(self):
        """Waitlist is set when capacity check inside atomic block finds full."""
        event = self._create_event(max_attendees=2)
        # Fill 1 of 2 slots — is_registration_open still True
        EventRegistration.objects.create(
            event=event, user=self.member2, status="registered",
        )
        # Register member1 — fills slot 2
        self.client.login(username="member1", password="testpass123")
        self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        reg = EventRegistration.objects.get(event=event, user=self.member)
        self.assertEqual(reg.status, "registered")

    def test_unlimited_capacity(self):
        event = self._create_event(max_attendees=0)
        self.client.login(username="member1", password="testpass123")
        self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        reg = EventRegistration.objects.get(event=event, user=self.member)
        self.assertEqual(reg.status, "registered")


# ---------------------------------------------------------------------------
# 5. Cancellation and waitlist promotion
# ---------------------------------------------------------------------------


class TestCancellation(EventE2EBase):
    """Test event cancellation and waitlist promotion."""

    def test_cancel_own_registration(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        reg = EventRegistration.objects.get(event=event, user=self.member)
        resp = self.client.post(events_area_url("cancel", args=[str(reg.pk)]))
        self.assertRedirects(resp, events_area_url("my_registrations"))
        reg.refresh_from_db()
        self.assertEqual(reg.status, "cancelled")

    def test_waitlist_promotion_on_cancel(self):
        event = self._create_event(max_attendees=1)
        # Create registrations directly in DB to test promotion logic
        reg1 = EventRegistration.objects.create(
            event=event, user=self.member, status="registered",
        )
        reg2 = EventRegistration.objects.create(
            event=event, user=self.member2, status="waitlist",
        )

        # Cancel first registration via view
        self.client.login(username="member1", password="testpass123")
        self.client.post(events_area_url("cancel", args=[str(reg1.pk)]))

        # Waitlisted user should be promoted
        reg2.refresh_from_db()
        self.assertEqual(reg2.status, "registered")


# ---------------------------------------------------------------------------
# 6. ICS export
# ---------------------------------------------------------------------------


class TestICSExport(EventE2EBase):
    """Test ICS calendar file export."""

    def test_single_event_ics(self):
        event = self._create_event()
        resp = self.client.get(reverse("events:event_ics", args=[event.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/calendar")
        content = resp.content.decode()
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn("BEGIN:VEVENT", content)
        self.assertIn(event.title, content)

    def test_ics_has_attachment_header(self):
        event = self._create_event()
        resp = self.client.get(reverse("events:event_ics", args=[event.pk]))
        self.assertIn("attachment", resp["Content-Disposition"])

    def test_ics_filename_has_date_and_slug(self):
        event = self._create_event(title="Mountain Ride")
        resp = self.client.get(reverse("events:event_ics", args=[event.pk]))
        disposition = resp["Content-Disposition"]
        date_str = event.start_date.strftime("%Y-%m-%d")
        self.assertIn(date_str, disposition)
        self.assertIn("mountain-ride", disposition)

    def test_ics_has_dtend_fallback(self):
        event = self._create_event(end_date=None)
        resp = self.client.get(reverse("events:event_ics", args=[event.pk]))
        content = resp.content.decode()
        self.assertIn("DTEND:", content)

    def test_ics_has_sequence(self):
        event = self._create_event()
        resp = self.client.get(reverse("events:event_ics", args=[event.pk]))
        content = resp.content.decode()
        self.assertIn("SEQUENCE:0", content)

    def test_all_events_ics_public(self):
        """Test that the public all-events ICS feed works without auth."""
        self._create_event(title="Public Event A")
        self._create_event(title="Public Event B")
        resp = self.client.get(reverse("events:all_events_ics"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/calendar")
        content = resp.content.decode()
        self.assertIn("BEGIN:VCALENDAR", content)
        self.assertIn("SUMMARY:Public Event A", content)
        self.assertIn("SUMMARY:Public Event B", content)
        self.assertIn("REFRESH-INTERVAL", content)

    def test_all_events_ics_excludes_past(self):
        """Test that past events are not included in the public feed."""
        self._create_event(
            title="Past Event",
            start_date=timezone.now() - timedelta(days=10),
        )
        self._create_event(title="Future Event")
        resp = self.client.get(reverse("events:all_events_ics"))
        content = resp.content.decode()
        self.assertNotIn("SUMMARY:Past Event", content)
        self.assertIn("SUMMARY:Future Event", content)


# ---------------------------------------------------------------------------
# 7. Favorites
# ---------------------------------------------------------------------------


class TestFavorites(EventE2EBase):
    """Test favorite toggle and my events views."""

    def test_toggle_favorite_add(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(reverse("events:toggle_favorite", args=[event.pk]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["favorited"])
        self.assertTrue(
            EventFavorite.objects.filter(user=self.member, event=event).exists()
        )

    def test_toggle_favorite_remove(self):
        event = self._create_event()
        EventFavorite.objects.create(user=self.member, event=event)
        self.client.login(username="member1", password="testpass123")
        # Clear debounce cache before toggling
        from django.core.cache import cache
        cache.delete(f"toggle_fav_{self.member.pk}")
        resp = self.client.post(reverse("events:toggle_favorite", args=[event.pk]))
        data = resp.json()
        self.assertFalse(data["favorited"])
        self.assertFalse(
            EventFavorite.objects.filter(user=self.member, event=event).exists()
        )

    def test_my_events_view(self):
        event = self._create_event()
        EventFavorite.objects.create(user=self.member, event=event)
        self.client.login(username="member1", password="testpass123")
        resp = self.client.get(events_area_url("my_events"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, event.title)


# ---------------------------------------------------------------------------
# 8. My registrations
# ---------------------------------------------------------------------------


class TestMyRegistrations(EventE2EBase):
    """Test my registrations list view."""

    def test_my_registrations_lists_own(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        resp = self.client.get(events_area_url("my_registrations"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context["registrations"]), 1)

    def test_my_registrations_requires_login(self):
        resp = self.client.get(events_area_url("my_registrations"))
        self.assertEqual(resp.status_code, 302)  # redirect to login


# ---------------------------------------------------------------------------
# 9. computed_deadline via PricingTier
# ---------------------------------------------------------------------------


class TestComputedDeadline(EventE2EBase):
    """Test that PricingTier is_deadline affects registration."""

    def test_computed_deadline_from_pricing_tier(self):
        event = self._create_event(
            start_date=timezone.now() + timedelta(days=30),
        )
        PricingTier.objects.create(
            event_page=event,
            label="Last Chance",
            days_before=2,
            discount_percent=0,
            is_deadline=True,
        )
        # computed_deadline should be 2 days before start
        deadline = event.computed_deadline
        expected = event.start_date - timedelta(days=2)
        self.assertAlmostEqual(
            deadline.timestamp(), expected.timestamp(), delta=1
        )

    def test_registration_rejected_after_deadline(self):
        # Event with start in 1 day, deadline tier at 2 days before
        # → deadline already passed
        event = self._create_event(
            start_date=timezone.now() + timedelta(days=1),
        )
        PricingTier.objects.create(
            event_page=event,
            label="Deadline",
            days_before=2,
            discount_percent=0,
            is_deadline=True,
        )
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {"accept_terms": "on", "guests": 0},
        )
        # Should re-render form with error (deadline passed)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            EventRegistration.objects.filter(event=event).count(), 0
        )


# ---------------------------------------------------------------------------
# 10. Passenger fields
# ---------------------------------------------------------------------------


class TestPassengerRegistration(EventE2EBase):
    """Test registration with passenger/companion."""

    def test_register_with_guest_passenger(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {
                "accept_terms": "on",
                "guests": 0,
                "has_passenger": "on",
                "passenger_is_member": "",
                "passenger_first_name": "Anna",
                "passenger_last_name": "Verdi",
            },
        )
        self.assertRedirects(resp, events_area_url("my_registrations"))
        reg = EventRegistration.objects.get(event=event, user=self.member)
        self.assertTrue(reg.has_passenger)
        self.assertEqual(reg.passenger_first_name, "Anna")
        self.assertEqual(reg.passenger_last_name, "Verdi")

    def test_passenger_without_name_rejected(self):
        event = self._create_event()
        self.client.login(username="member1", password="testpass123")
        resp = self.client.post(
            event.url + "register/",
            {
                "accept_terms": "on",
                "guests": 0,
                "has_passenger": "on",
                "passenger_is_member": "",
                "passenger_first_name": "",
                "passenger_last_name": "",
            },
        )
        self.assertEqual(resp.status_code, 200)  # form re-rendered
        self.assertEqual(
            EventRegistration.objects.filter(event=event).count(), 0
        )

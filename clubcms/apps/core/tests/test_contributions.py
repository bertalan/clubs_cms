"""
T18 — Test member contributions: submit story/proposal/announcement,
submit real page types (news, event), my submissions list.

Contributions are Wagtail Pages under their respective parent pages,
all managed through ContributionsPage routes.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from wagtail.models import Page, Site

from apps.core.models import (
    ContributionPage,
    ContributionsPage,
    SUBMITTABLE_PAGE_TYPES,
)

User = get_user_model()


def _setup_contributions_page():
    """Create a ContributionsPage under the root with a working Site."""
    root = Page.objects.filter(depth=1).first()
    home = root.get_children().first()
    if home is None:
        home = root.add_child(instance=Page(title="Home", slug="home"))
    contrib_page = home.add_child(
        instance=ContributionsPage(
            title="Contributions",
            slug="contributions",
        )
    )
    contrib_page.save_revision().publish()
    Site.objects.update_or_create(
        hostname="localhost",
        defaults={
            "root_page": home,
            "is_default_site": True,
            "site_name": "Test",
        },
    )
    return contrib_page


def _create_contribution_page(parent, user, **kwargs):
    """Create a ContributionPage child under parent."""
    defaults = {
        "contribution_type": "story",
        "title": "Test Contribution",
        "slug": "test-contribution",
        "body": [{"type": "rich_text", "value": "<p>Test content</p>"}],
        "author": user,
        "owner": user,
        "live": False,
        "has_unpublished_changes": True,
    }
    defaults.update(kwargs)
    child = parent.add_child(instance=ContributionPage(**defaults))
    child.save_revision()
    return child


class TestContributionAuth(TestCase):
    """Contribution pages require login."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def test_submit_requires_login(self):
        url = self.contrib_page.url + self.contrib_page.reverse_subpage(
            "submit_contribution"
        )
        resp = self.client.get(url)
        self.assertIn(resp.status_code, (302, 403))

    def test_my_contributions_requires_login(self):
        resp = self.client.get(self.contrib_page.url)
        self.assertIn(resp.status_code, (302, 403))


class TestSubmitTypeSelector(TestCase):
    """GET contributions/submit/ shows type selection page."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def setUp(self):
        self.user = User.objects.create_user(
            username="selector_user", password="testpass123"
        )
        self.client.login(username="selector_user", password="testpass123")
        self.url = self.contrib_page.url + self.contrib_page.reverse_subpage(
            "submit_contribution"
        )

    def test_get_shows_type_cards(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        for slug, info in SUBMITTABLE_PAGE_TYPES.items():
            self.assertContains(resp, slug)

    def test_invalid_type_returns_404(self):
        url = self.contrib_page.url + "submit/nonexistent/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class TestSubmitContribution(TestCase):
    """POST contributions/submit/story/ creates a draft ContributionPage."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def setUp(self):
        self.user = User.objects.create_user(
            username="contrib_user", password="testpass123"
        )
        self.client.login(username="contrib_user", password="testpass123")
        self.url = self.contrib_page.url + "submit/story/"

    def test_get_shows_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "form")

    def test_submit_story(self):
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "La mia avventura in moto",
            "body": "Era una bella giornata di primavera..." + " parola" * 50,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(ContributionPage.objects.count(), 1)
        c = ContributionPage.objects.first()
        self.assertEqual(c.author, self.user)
        self.assertEqual(c.contribution_type, "story")
        self.assertEqual(c.moderation_status, "pending")
        self.assertFalse(c.live)

    def test_submit_proposal(self):
        resp = self.client.post(self.url, {
            "contribution_type": "proposal",
            "title": "Proposta gita al lago",
            "body": "Propongo una gita al lago di Garda...",
        })
        self.assertEqual(resp.status_code, 302)
        c = ContributionPage.objects.first()
        self.assertEqual(c.contribution_type, "proposal")

    def test_submit_announcement(self):
        resp = self.client.post(self.url, {
            "contribution_type": "announcement",
            "title": "Vendesi casco",
            "body": "Vendo casco Shoei usato poche volte.",
        })
        self.assertEqual(resp.status_code, 302)
        c = ContributionPage.objects.first()
        self.assertEqual(c.contribution_type, "announcement")

    def test_missing_title_fails(self):
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "",
            "body": "Some content here.",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders form
        self.assertEqual(ContributionPage.objects.count(), 0)

    def test_missing_body_fails(self):
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "Titolo",
            "body": "",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ContributionPage.objects.count(), 0)

    def test_rate_limit_max_pending(self):
        """A user cannot have more than 5 pending draft pages."""
        for i in range(5):
            _create_contribution_page(
                self.contrib_page, self.user,
                title=f"Story {i}", slug=f"story-{i}",
            )
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "One too many",
            "body": "Content here.",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders with error
        self.assertEqual(ContributionPage.objects.count(), 5)


class TestSubmitNews(TestCase):
    """POST contributions/submit/news/ creates a draft NewsPage."""

    @classmethod
    def setUpTestData(cls):
        from apps.website.models.pages import NewsIndexPage

        cls.contrib_page = _setup_contributions_page()
        home = cls.contrib_page.get_parent()
        cls.news_index = home.add_child(
            instance=NewsIndexPage(title="News", slug="news")
        )
        cls.news_index.save_revision().publish()

    def setUp(self):
        self.user = User.objects.create_user(
            username="news_user", password="testpass123"
        )
        self.client.login(username="news_user", password="testpass123")
        self.url = self.contrib_page.url + "submit/news/"

    def test_get_shows_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_submit_news(self):
        from apps.website.models.pages import NewsPage

        resp = self.client.post(self.url, {
            "title": "Big News for the Club",
            "intro": "Something exciting happened.",
            "body": "The full story of what happened.\n\nMore details here.",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(NewsPage.objects.count(), 1)
        n = NewsPage.objects.first()
        self.assertEqual(n.owner, self.user)
        self.assertFalse(n.live)
        self.assertTrue(n.get_parent().specific, self.news_index)


class TestSubmitEvent(TestCase):
    """POST contributions/submit/event/ creates a draft EventDetailPage."""

    @classmethod
    def setUpTestData(cls):
        from apps.website.models.pages import EventsPage

        cls.contrib_page = _setup_contributions_page()
        home = cls.contrib_page.get_parent()
        cls.events_page = home.add_child(
            instance=EventsPage(title="Events", slug="events")
        )
        cls.events_page.save_revision().publish()

    def setUp(self):
        self.user = User.objects.create_user(
            username="event_user", password="testpass123"
        )
        self.client.login(username="event_user", password="testpass123")
        self.url = self.contrib_page.url + "submit/event/"

    def test_get_shows_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_submit_event(self):
        from apps.website.models.pages import EventDetailPage

        resp = self.client.post(self.url, {
            "title": "Spring Rally 2026",
            "intro": "Annual spring rally.",
            "body": "Join us for a scenic ride through the Alps.",
            "start_date": "2026-06-15T10:00",
            "location_name": "Passo dello Stelvio",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(EventDetailPage.objects.count(), 1)
        e = EventDetailPage.objects.first()
        self.assertEqual(e.owner, self.user)
        self.assertFalse(e.live)


class TestMyContributions(TestCase):
    """GET contributions/ shows user's own submissions across all types."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def setUp(self):
        self.user = User.objects.create_user(
            username="mycontrib", password="testpass123"
        )
        self.other = User.objects.create_user(
            username="othercontrib", password="testpass123"
        )
        self.client.login(username="mycontrib", password="testpass123")
        self.url = self.contrib_page.url

        # Own contribution
        _create_contribution_page(
            self.contrib_page, self.user,
            title="My Story", slug="my-story",
        )
        # Other user's contribution
        _create_contribution_page(
            self.contrib_page, self.other,
            title="Other Story", slug="other-story",
        )

    def test_shows_own_contributions(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "My Story")

    def test_hides_other_users_contributions(self):
        resp = self.client.get(self.url)
        self.assertNotContains(resp, "Other Story")


class TestContributionPageModel(TestCase):
    """ContributionPage model fields and defaults."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def test_default_status_is_pending(self):
        user = User.objects.create_user(username="modeltest", password="pass")
        c = _create_contribution_page(
            self.contrib_page, user,
            title="Test", slug="test",
        )
        self.assertEqual(c.moderation_status, "pending")
        self.assertIsNone(c.moderated_by)
        self.assertEqual(c.moderation_note, "")
        self.assertFalse(c.live)

    def test_str_representation(self):
        user = User.objects.create_user(username="strtest", password="pass")
        c = _create_contribution_page(
            self.contrib_page, user,
            contribution_type="proposal",
            title="My Proposal", slug="my-proposal",
        )
        s = str(c)
        self.assertIn("My Proposal", s)

    def test_approved_contribution_is_live(self):
        user = User.objects.create_user(username="approvetest", password="pass")
        c = _create_contribution_page(
            self.contrib_page, user,
            title="Approved Story", slug="approved-story",
            moderation_status="approved",
            live=True,
            has_unpublished_changes=False,
        )
        c.save_revision().publish()
        c.refresh_from_db()
        self.assertTrue(c.live)
        self.assertEqual(c.moderation_status, "approved")

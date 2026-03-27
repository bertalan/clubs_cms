"""
T18 — Test member contributions: submit story/proposal/announcement,
my contributions list, moderation status.
"""

import json

from django.contrib.auth import get_user_model
from django.test import TestCase

from wagtail.models import Page, Site

from apps.core.models import Contribution, ContributionsPage

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


class TestSubmitContribution(TestCase):
    """POST contributions/submit/ creates a pending Contribution."""

    @classmethod
    def setUpTestData(cls):
        cls.contrib_page = _setup_contributions_page()

    def setUp(self):
        self.user = User.objects.create_user(
            username="contrib_user", password="testpass123"
        )
        self.client.login(username="contrib_user", password="testpass123")
        self.url = self.contrib_page.url + self.contrib_page.reverse_subpage(
            "submit_contribution"
        )

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
        self.assertEqual(Contribution.objects.count(), 1)
        c = Contribution.objects.first()
        self.assertEqual(c.user, self.user)
        self.assertEqual(c.contribution_type, "story")
        self.assertEqual(c.status, "pending")

    def test_submit_proposal(self):
        resp = self.client.post(self.url, {
            "contribution_type": "proposal",
            "title": "Proposta gita al lago",
            "body": "Propongo una gita al lago di Garda...",
        })
        self.assertEqual(resp.status_code, 302)
        c = Contribution.objects.first()
        self.assertEqual(c.contribution_type, "proposal")

    def test_submit_announcement(self):
        resp = self.client.post(self.url, {
            "contribution_type": "announcement",
            "title": "Vendesi casco",
            "body": "Vendo casco Shoei usato poche volte.",
        })
        self.assertEqual(resp.status_code, 302)
        c = Contribution.objects.first()
        self.assertEqual(c.contribution_type, "announcement")

    def test_missing_title_fails(self):
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "",
            "body": "Some content here.",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders form
        self.assertEqual(Contribution.objects.count(), 0)

    def test_missing_body_fails(self):
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "Titolo",
            "body": "",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Contribution.objects.count(), 0)

    def test_rate_limit_max_pending(self):
        """A user cannot have more than 5 pending contributions."""
        for i in range(5):
            Contribution.objects.create(
                user=self.user,
                contribution_type="story",
                title=f"Story {i}",
                body="Content",
                status="pending",
            )
        resp = self.client.post(self.url, {
            "contribution_type": "story",
            "title": "One too many",
            "body": "Content here.",
        })
        self.assertEqual(resp.status_code, 200)  # re-renders with error
        self.assertEqual(Contribution.objects.count(), 5)


class TestMyContributions(TestCase):
    """GET contributions/ shows user's own contributions."""

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
        Contribution.objects.create(
            user=self.user,
            contribution_type="story",
            title="My Story",
            body="Content",
        )
        # Other user's contribution
        Contribution.objects.create(
            user=self.other,
            contribution_type="story",
            title="Other Story",
            body="Content",
        )

    def test_shows_own_contributions(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "My Story")

    def test_hides_other_users_contributions(self):
        resp = self.client.get(self.url)
        self.assertNotContains(resp, "Other Story")


class TestContributionModel(TestCase):
    """Contribution model fields and defaults."""

    def test_default_status_is_pending(self):
        user = User.objects.create_user(username="modeltest", password="pass")
        c = Contribution.objects.create(
            user=user,
            contribution_type="story",
            title="Test",
            body="Content",
        )
        self.assertEqual(c.status, "pending")
        self.assertIsNone(c.moderated_by)
        self.assertIsNone(c.moderation_note)

    def test_str_representation(self):
        user = User.objects.create_user(username="strtest", password="pass")
        c = Contribution.objects.create(
            user=user,
            contribution_type="proposal",
            title="My Proposal",
            body="Content",
        )
        s = str(c)
        self.assertIn("My Proposal", s)

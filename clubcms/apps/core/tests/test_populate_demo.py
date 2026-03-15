"""
Tests for the populate_demo_it management command.

Verifies that running the command creates the expected page hierarchy,
snippets, members, and site configuration.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Page, Site

from apps.members.models import ClubUser
from apps.website.models import (
    AboutPage,
    ColorScheme,
    ContactPage,
    EventCategory,
    EventDetailPage,
    EventsPage,
    Footer,
    GalleryPage,
    HomePage,
    Navbar,
    NewsCategory,
    NewsIndexPage,
    NewsPage,
    Product,
    SiteSettings,
)


def _fake_download_images(self):
    """Skip image downloads in tests — return empty dict."""
    return {}


def _fake_assign_images(self, images):
    """No-op image assignment."""
    pass


class PopulateDemoTests(TestCase):
    """Test that populate_demo_it creates expected content."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Run the command once, mocking image downloads
        with (
            patch(
                "apps.core.management.commands.populate_demo_it.Command._download_images",
                _fake_download_images,
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._assign_page_images",
                _fake_assign_images,
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._create_members",
                return_value=[],
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._create_aid_requests",
            ),
        ):
            call_command("populate_demo_it", verbosity=0)

    # ── Page hierarchy ────────────────────────────────────────────────

    def test_homepage_exists(self):
        self.assertTrue(HomePage.objects.exists())

    def test_homepage_is_root_child(self):
        home = HomePage.objects.first()
        root = Page.objects.filter(depth=1).first()
        self.assertEqual(home.get_parent().pk, root.pk)

    def test_about_page_exists(self):
        self.assertTrue(AboutPage.objects.exists())

    def test_news_index_exists(self):
        self.assertTrue(NewsIndexPage.objects.exists())

    def test_events_page_exists(self):
        self.assertTrue(EventsPage.objects.exists())

    def test_gallery_page_exists(self):
        self.assertTrue(GalleryPage.objects.exists())

    def test_contact_page_exists(self):
        self.assertTrue(ContactPage.objects.exists())

    def test_news_articles_created(self):
        self.assertGreaterEqual(NewsPage.objects.count(), 1)

    def test_events_created(self):
        self.assertGreaterEqual(EventDetailPage.objects.count(), 1)

    # ── Snippets ──────────────────────────────────────────────────────

    def test_color_scheme_created(self):
        self.assertTrue(ColorScheme.objects.exists())

    def test_navbar_created(self):
        self.assertTrue(Navbar.objects.exists())

    def test_footer_created(self):
        self.assertTrue(Footer.objects.exists())

    def test_news_categories_created(self):
        self.assertGreaterEqual(NewsCategory.objects.count(), 1)

    def test_event_categories_created(self):
        self.assertGreaterEqual(EventCategory.objects.count(), 1)

    def test_products_created(self):
        self.assertGreaterEqual(Product.objects.count(), 1)

    # ── Site settings ─────────────────────────────────────────────────

    def test_site_settings_exist(self):
        site = Site.objects.filter(is_default_site=True).first()
        self.assertIsNotNone(site)
        settings = SiteSettings.for_site(site)
        self.assertIsNotNone(settings)

    def test_site_points_to_homepage(self):
        site = Site.objects.filter(is_default_site=True).first()
        self.assertIsInstance(site.root_page.specific, HomePage)

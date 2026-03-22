"""
Tests for the demo data loading system.

Verifies that building and loading a demo fixture creates
the expected page hierarchy, snippets, and site configuration.
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


def _noop_images(self):
    return {}


def _noop_assign(self):
    pass


def _noop_members(self):
    return []


def _noop_aid(self, members):
    pass


class PopulateDemoTests(TestCase):
    """Test that load_demo --lang en --primary creates expected content."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        call_command("build_demo_db", lang="en", verbosity=0)
        with (
            patch("apps.core.demo.loader.DemoLoader._download_images", _noop_images),
            patch("apps.core.demo.loader.DemoLoader._assign_page_images", _noop_assign),
            patch("apps.core.demo.loader.DemoLoader._load_members", _noop_members),
            patch("apps.core.demo.loader.DemoLoader._load_aid_requests", _noop_aid),
        ):
            call_command("load_demo", lang="en", primary=True, flush=True, verbosity=0)

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

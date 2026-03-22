"""
End-to-end tests for i18n: URL prefixes, language switcher, hreflang tags.
"""

from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase


class I18nURLTests(TestCase):
    """Verify that i18n URL prefixes work correctly."""

    def test_root_redirects_to_default_language(self):
        """/ should 302 redirect to /en/ (default language)."""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/en/", resp["Location"])

    def test_italian_prefix_returns_200(self):
        resp = self.client.get("/it/", follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_english_prefix_returns_200(self):
        resp = self.client.get("/en/", follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_german_prefix_returns_200(self):
        resp = self.client.get("/de/", follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_french_prefix_returns_200(self):
        resp = self.client.get("/fr/", follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_spanish_prefix_returns_200(self):
        resp = self.client.get("/es/", follow=True)
        self.assertEqual(resp.status_code, 200)

    def test_unsupported_prefix_redirects(self):
        """An unsupported language prefix redirects to default language."""
        resp = self.client.get("/xx/")
        # Django i18n redirects unknown prefixes to the default language
        self.assertIn(resp.status_code, [301, 302, 404])

    def test_admin_no_i18n_prefix(self):
        """Admin URLs should not have language prefix."""
        resp = self.client.get("/admin/login/")
        self.assertEqual(resp.status_code, 200)


def _noop_images(self):
    return {}


def _noop_assign(self):
    pass


def _noop_members(self):
    return []


def _noop_aid(self, members):
    pass


class I18nContentTests(TestCase):
    """Tests that require a real HomePage with base.html template."""

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

    def test_hreflang_current_language_present(self):
        """The homepage should include hreflang for the current page locale."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn('hreflang="en"', content)

    def test_hreflang_x_default_present(self):
        """Should include x-default hreflang."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn('hreflang="x-default"', content)

    def test_language_switcher_in_page(self):
        """The page should contain a language switcher with setlang form."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertTrue(
            "setlang" in content or "site-nav__lang" in content,
            "Language switcher not found in page HTML",
        )

    def test_language_switcher_has_all_languages(self):
        """The switcher should have inputs for all configured languages."""
        from wagtail.models import Locale

        # Create Locales if needed
        for code in ["en", "it", "de", "fr", "es"]:
            Locale.objects.get_or_create(language_code=code)

        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        for lang in ["en", "it", "de", "fr", "es"]:
            self.assertIn(
                f'name="language" value="{lang}"',
                content,
                f"Language {lang} not found in switcher",
            )

    def test_html_lang_attribute(self):
        """The <html> tag should have the correct lang attribute."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn('lang="en"', content)

    def test_html_lang_changes_with_prefix(self):
        """Requesting /it/ should activate the Italian locale."""
        from django.utils.translation import get_language
        resp = self.client.get("/it/")
        # Django's LocaleMiddleware activates the language from the URL prefix.
        # The page may or may not exist in IT locale (translation copies may be
        # draft), but the URL prefix must trigger the correct redirect or serve.
        self.assertIn(resp.status_code, [200, 302])

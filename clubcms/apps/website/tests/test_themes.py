"""
Tests for theme rendering, CSS variables, and dark mode support.
Verifies all 6 themes render correctly and contain required CSS variables.
"""

import os
import re
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Site

from apps.website.models import SiteSettings

THEMES = ["velocity", "heritage", "terra", "zen", "clubs", "tricolore"]

REQUIRED_CSS_VARS = [
    "--color-primary",
    "--color-secondary",
    "--color-accent",
    "--color-surface",
    "--color-surface-alt",
    "--color-text-primary",
    "--color-text-muted",
]

CSS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "static", "css"
)


def _noop_images(self):
    return {}


def _noop_assign(self):
    pass


def _noop_members(self):
    return []


def _noop_aid(self, members):
    pass


class ThemeCSSFileTests(TestCase):
    """Verify that all theme CSS files exist and contain required variables."""

    def test_base_css_exists(self):
        path = os.path.join(CSS_DIR, "base.css")
        self.assertTrue(os.path.isfile(path), "base.css not found")

    def test_all_theme_files_exist(self):
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            self.assertTrue(
                os.path.isfile(path), f"Theme CSS missing: {theme}/main.css"
            )

    def test_required_css_variables_in_each_theme(self):
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            with open(path) as f:
                content = f.read()
            for var in REQUIRED_CSS_VARS:
                self.assertIn(
                    var,
                    content,
                    f"Theme '{theme}' missing CSS variable: {var}",
                )

    def test_dark_mode_in_each_theme(self):
        """Each theme should have .dark-mode or [data-theme='dark'] rules."""
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            with open(path) as f:
                content = f.read()
            self.assertTrue(
                "dark-mode" in content or "dark" in content,
                f"Theme '{theme}' has no dark mode support",
            )


class ThemeRenderTests(TestCase):
    """Test that switching themes changes the CSS file loaded in HTML."""

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

    def _set_theme(self, theme_name):
        site = Site.objects.filter(is_default_site=True).first()
        settings = SiteSettings.for_site(site)
        settings.theme = theme_name
        settings.save()

    def test_default_theme_is_velocity(self):
        """Without explicit setting, velocity CSS should be loaded."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn("velocity/main.css", content)

    def test_each_theme_renders_200(self):
        """Switching to each theme should still render the page."""
        for theme in THEMES:
            self._set_theme(theme)
            resp = self.client.get("/en/", follow=True)
            self.assertEqual(
                resp.status_code, 200, f"Theme '{theme}' returned {resp.status_code}"
            )

    def test_each_theme_loads_correct_css(self):
        """The HTML should reference the correct theme CSS file."""
        for theme in THEMES:
            self._set_theme(theme)
            resp = self.client.get("/en/", follow=True)
            content = resp.content.decode()
            self.assertIn(
                f"{theme}/main.css",
                content,
                f"Theme '{theme}' CSS not found in HTML",
            )

    def test_base_css_always_loaded(self):
        """base.css should be loaded regardless of theme."""
        for theme in THEMES:
            self._set_theme(theme)
            resp = self.client.get("/en/", follow=True)
            content = resp.content.decode()
            self.assertIn("base.css", content)


class A11yBasicTests(TestCase):
    """Basic accessibility checks on rendered pages."""

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

    def test_html_lang_attribute_present(self):
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertRegex(content, r'<html[^>]+lang="[a-z]+"')

    def test_viewport_meta_present(self):
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn("viewport", content)

    def test_skip_to_content_or_main_landmark(self):
        """Page should have a <main> landmark or skip-to-content link."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertTrue(
            "<main" in content or "skip" in content.lower(),
            "No <main> landmark or skip-to-content link found",
        )

    def test_nav_landmark_present(self):
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        self.assertIn("<nav", content)

    def test_no_empty_links(self):
        """Links should not be empty (no text or aria-label)."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        # Find <a> tags with no text content and no aria-label
        empty_links = re.findall(r'<a [^>]*></a>', content)
        # Filter out those with aria-label
        truly_empty = [
            link for link in empty_links if "aria-label" not in link
        ]
        self.assertEqual(
            len(truly_empty),
            0,
            f"Found {len(truly_empty)} empty links without aria-label",
        )

    def test_images_have_alt(self):
        """All <img> tags should have alt attribute."""
        resp = self.client.get("/en/", follow=True)
        content = resp.content.decode()
        imgs_without_alt = re.findall(r'<img(?![^>]*\balt\b)[^>]*>', content)
        self.assertEqual(
            len(imgs_without_alt),
            0,
            f"Found {len(imgs_without_alt)} images without alt attribute",
        )

    def test_contact_page_anonymous_no_error(self):
        """Contact page should render for anonymous users without errors."""
        resp = self.client.get("/en/contact/", follow=True)
        self.assertEqual(resp.status_code, 200)


class ContactPageHeaderTests(TestCase):
    """T32 — Contact page uses shared centered header (no hero)."""

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

    def test_contact_page_has_centered_header(self):
        """Contact page must use shared centered header, not hero."""
        resp = self.client.get("/en/contact/", follow=True)
        content = resp.content.decode()
        self.assertIn('class="page-contact__header"', content)
        self.assertIn('class="page-contact__title"', content)

    def test_contact_page_no_hero_section(self):
        """Contact page must not render a hero section."""
        resp = self.client.get("/it/contatti/", follow=True)
        content = resp.content.decode()
        self.assertNotIn("page-contact__hero", content)

    def test_contact_header_css_centered(self):
        """Shared header CSS must center the contact header."""
        base_path = os.path.join(CSS_DIR, "base.css")
        with open(base_path) as f:
            base_css = f.read()
        self.assertRegex(
            base_css,
            r"\.page-contact__header[^{]*\{[^}]*text-align:\s*center",
            "page-contact__header missing text-align: center in base.css",
        )


class NavbarContrastCSSTests(TestCase):
    """T33 — Verify navbar elements have proper contrast support."""

    def setUp(self):
        base_path = os.path.join(CSS_DIR, "base.css")
        with open(base_path) as f:
            self.base_css = f.read()

    def test_lang_toggle_uses_inherit(self):
        """Lang toggle should use color: inherit (not var(--color-text))
        so it inherits from the nav context, not body."""
        # Should NOT use var(--color-text, inherit) which bypasses nav color
        match = re.search(
            r"\.site-nav__lang-toggle\s*\{[^}]*color:\s*([^;]+);",
            self.base_css,
        )
        self.assertIsNotNone(match, "Missing color on .site-nav__lang-toggle")
        self.assertNotIn(
            "--color-text",
            match.group(1),
            "Lang toggle should not use --color-text (bypasses nav context)",
        )

    def test_search_toggle_uses_inherit(self):
        """Search toggle should use color: inherit (not var(--color-text))."""
        match = re.search(
            r"\.site-nav__search-toggle\s*\{[^}]*color:\s*([^;]+);",
            self.base_css,
        )
        self.assertIsNotNone(match, "Missing color on .site-nav__search-toggle")
        self.assertNotIn(
            "--color-text",
            match.group(1),
            "Search toggle should not use --color-text (bypasses nav context)",
        )

    def test_all_themes_set_nav_link_color(self):
        """Every theme must set color on .site-nav__links (container)
        so buttons and toggles inherit the right color, not just <a> tags."""
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            with open(path) as f:
                content = f.read()
            # .site-nav__links container must have color (for button inheritance)
            self.assertRegex(
                content,
                r"\.site-nav__links\s*\{[^}]*color:",
                f"Theme '{theme}' missing color on .site-nav__links container",
            )

    def test_all_themes_style_dropdown_menu(self):
        """Every theme must define dropdown-menu background."""
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            with open(path) as f:
                content = f.read()
            self.assertRegex(
                content,
                r"\.site-nav__dropdown-menu\s*\{[^}]*background:",
                f"Theme '{theme}' missing dropdown-menu background",
            )

    def test_all_themes_style_lang_menu(self):
        """Every theme must define lang-menu background."""
        for theme in THEMES:
            path = os.path.join(CSS_DIR, "themes", theme, "main.css")
            with open(path) as f:
                content = f.read()
            self.assertRegex(
                content,
                r"\.site-nav__lang-menu\s*\{[^}]*background:",
                f"Theme '{theme}' missing lang-menu background",
            )

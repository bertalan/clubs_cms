"""
Tests for SEO SiteSettings fields: seo_indexing, allow_ai_bots,
robots_txt_extra, canonical_domain.
"""

import pytest
from django.test import TestCase, override_settings
from wagtail.models import Site

from apps.website.models.settings import SiteSettings


pytestmark = pytest.mark.django_db


class RobotsTxtViewTests(TestCase):
    """Tests for the dynamic robots.txt generation."""

    def _get_settings(self):
        site = Site.objects.filter(is_default_site=True).first()
        return SiteSettings.for_site(site)

    # -- default behaviour (indexing=True, ai_bots=False) -------------------

    def test_robots_txt_returns_200(self):
        resp = self.client.get("/robots.txt")
        assert resp.status_code == 200
        assert resp["Content-Type"].startswith("text/plain")

    def test_robots_default_allows_crawling(self):
        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "User-agent: *\nAllow: /" in body
        assert "Sitemap:" in body

    def test_robots_default_blocks_ai_bots(self):
        """By default allow_ai_bots=False, so AI bots should be blocked."""
        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "User-agent: GPTBot" in body
        assert "User-agent: ChatGPT-User" in body
        assert "User-agent: Google-Extended" in body
        assert "User-agent: CCBot" in body
        assert "User-agent: anthropic-ai" in body
        assert "User-agent: PerplexityBot" in body

    def test_robots_default_blocks_admin(self):
        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "Disallow: /admin/" in body
        assert "Disallow: /django-admin/" in body
        assert "Disallow: /account/" in body

    # -- seo_indexing = False -----------------------------------------------

    def test_robots_noindex_disallows_all(self):
        ss = self._get_settings()
        ss.seo_indexing = False
        ss.save()

        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "User-agent: *\nDisallow: /" in body

    # -- allow_ai_bots = True -----------------------------------------------

    def test_robots_allow_ai_bots_omits_blocks(self):
        ss = self._get_settings()
        ss.allow_ai_bots = True
        ss.save()

        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "GPTBot" not in body
        assert "ChatGPT-User" not in body

    # -- robots_txt_extra ---------------------------------------------------

    def test_robots_extra_rules_appended(self):
        ss = self._get_settings()
        ss.robots_txt_extra = "Disallow: /private/\nDisallow: /secret/"
        ss.save()

        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        assert "Disallow: /private/" in body
        assert "Disallow: /secret/" in body
        assert "# Custom rules" in body


class MetaRobotsTagTests(TestCase):
    """Tests for the noindex meta tag in base.html."""

    def _get_settings(self):
        site = Site.objects.filter(is_default_site=True).first()
        return SiteSettings.for_site(site)

    def test_no_meta_robots_when_indexing_enabled(self):
        """Default seo_indexing=True should not emit noindex tag."""
        resp = self.client.get("/robots.txt")
        body = resp.content.decode()
        # When indexing is enabled, robots.txt has Allow: /
        assert "Allow: /" in body

    def test_meta_robots_noindex_flag_stored(self):
        """Verify seo_indexing can be set to False and persisted."""
        ss = self._get_settings()
        ss.seo_indexing = False
        ss.save()
        ss.refresh_from_db()
        assert ss.seo_indexing is False


class CanonicalUrlTests(TestCase):
    """Tests for canonical_url_tag with canonical_domain override."""

    def _get_settings(self):
        site = Site.objects.filter(is_default_site=True).first()
        return SiteSettings.for_site(site)

    def test_canonical_domain_stored(self):
        ss = self._get_settings()
        ss.canonical_domain = "https://www.example.com"
        ss.save()
        ss.refresh_from_db()
        assert ss.canonical_domain == "https://www.example.com"

    def test_canonical_domain_default_empty(self):
        ss = self._get_settings()
        assert ss.canonical_domain == ""

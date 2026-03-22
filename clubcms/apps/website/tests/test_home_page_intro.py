from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Site

from apps.website.models import HomePage, SiteSettings


def _noop_images(self):
    return {}


def _noop_assign(self):
    pass


def _noop_members(self):
    return []


def _noop_aid(self, members):
    pass


class HomePageIntroTests(TestCase):
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

    def test_opening_streamfield_blocks_are_promoted(self):
        page = HomePage.objects.live().first()

        intro = page.home_intro_section

        self.assertTrue(intro["enabled"])
        self.assertEqual(intro["rich_text"].block_type, "rich_text")
        self.assertEqual(intro["stats"].block_type, "stats")
        self.assertEqual(intro["cta"].block_type, "cta")
        self.assertEqual(page.remaining_body_blocks, [])

    def test_homepage_renders_spotlight_section(self):
        response = self.client.get("/en/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "page-home__spotlight")
        self.assertContains(response, 'class="home-body"')
        self.assertContains(response, "Welcome to Moto Club Aquile Rosse")
        self.assertContains(response, "Join Us")
        self.assertContains(response, "250+")

        content = response.content.decode()
        self.assertLess(content.find('class="home-partners'), content.find('page-home__spotlight'))

    def test_spotlight_renders_for_each_theme(self):
        site = Site.objects.filter(is_default_site=True).first()
        settings = SiteSettings.for_site(site)

        for theme in ["velocity", "heritage", "terra", "zen", "clubs", "tricolore"]:
            settings.theme = theme
            settings.save()

            response = self.client.get("/en/", follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "page-home__spotlight")
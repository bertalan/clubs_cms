from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from wagtail.models import Site

from apps.website.models import HomePage, SiteSettings


def _noop(*args, **kwargs):
    return {}


def _noop_method(self, *args, **kwargs):
    return []


class HomePageIntroTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with (
            patch(
                "apps.core.management.commands.populate_demo_it.Command._download_images",
                _noop,
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._assign_page_images",
                _noop,
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._create_members",
                _noop_method,
            ),
            patch(
                "apps.core.management.commands.populate_demo_it.Command._create_aid_requests",
                _noop,
            ),
        ):
            call_command("populate_demo_it", verbosity=0)

    def test_opening_streamfield_blocks_are_promoted(self):
        page = HomePage.objects.live().first()

        intro = page.home_intro_section

        self.assertTrue(intro["enabled"])
        self.assertEqual(intro["rich_text"].block_type, "rich_text")
        self.assertEqual(intro["stats"].block_type, "stats")
        self.assertEqual(intro["cta"].block_type, "cta")
        self.assertEqual(page.remaining_body_blocks, [])

    def test_homepage_renders_spotlight_section(self):
        response = self.client.get("/it/", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "page-home__spotlight")
        self.assertContains(response, 'class="home-body"')
        self.assertContains(response, "Benvenuti nel Moto Club Aquile Rosse")
        self.assertContains(response, "Unisciti a Noi")
        self.assertContains(response, "250+")

        content = response.content.decode()
        self.assertLess(content.find('class="home-partners'), content.find('page-home__spotlight'))

    def test_spotlight_renders_for_each_theme(self):
        site = Site.objects.filter(is_default_site=True).first()
        settings = SiteSettings.for_site(site)

        for theme in ["velocity", "heritage", "terra", "zen", "clubs", "tricolore"]:
            settings.theme = theme
            settings.save()

            response = self.client.get("/it/", follow=True)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "page-home__spotlight")
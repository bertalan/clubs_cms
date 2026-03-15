"""
T10 — Test BlockSettings su tutti i blocchi section-level.

Verifica che:
- Ogni blocco section-level ha un campo 'settings'
- BlockSettings ha i 4 campi richiesti (custom_id, custom_class, background, padding)
- Il template tag block_attrs renderizza correttamente gli attributi HTML
"""

from django.template import Context, Template
from django.test import TestCase

from apps.website.blocks.common import BlockSettings
from apps.website.blocks.content import (
    AlertBlock,
    CardsGridBlock,
    CTABlock,
    NewsletterSignupBlock,
    PartnersGridBlock,
    QuoteBlock,
    StatsBlock,
    TeamGridBlock,
    TimelineBlock,
)
from apps.website.blocks.hero import (
    HeroBannerBlock,
    HeroCountdownBlock,
    HeroSliderBlock,
    HeroVideoBlock,
)
from apps.website.blocks.layout import (
    AccordionBlock,
    DividerBlock,
    SectionBlock,
    SpacerBlock,
    TabsBlock,
    TwoColumnBlock,
)
from apps.website.blocks.media import (
    DocumentListBlock,
    GalleryBlock,
    ImageBlock,
    MapBlock,
    VideoEmbedBlock,
)
from apps.website.blocks.route import RouteBlock


# All section-level blocks that must have settings
SECTION_BLOCKS = [
    # Content
    CardsGridBlock, CTABlock, StatsBlock, QuoteBlock, TimelineBlock,
    TeamGridBlock, NewsletterSignupBlock, AlertBlock, PartnersGridBlock,
    # Hero
    HeroSliderBlock, HeroBannerBlock, HeroCountdownBlock, HeroVideoBlock,
    # Media
    GalleryBlock, VideoEmbedBlock, ImageBlock, DocumentListBlock, MapBlock,
    # Layout
    AccordionBlock, TabsBlock, TwoColumnBlock, SectionBlock,
    DividerBlock, SpacerBlock,
    # Route
    RouteBlock,
]


class TestBlockSettingsFields(TestCase):
    """BlockSettings must have all 4 required fields."""

    def test_has_custom_id(self):
        block = BlockSettings()
        self.assertIn("custom_id", block.child_blocks)

    def test_has_custom_class(self):
        block = BlockSettings()
        self.assertIn("custom_class", block.child_blocks)

    def test_has_background(self):
        block = BlockSettings()
        self.assertIn("background", block.child_blocks)

    def test_has_padding(self):
        block = BlockSettings()
        self.assertIn("padding", block.child_blocks)


class TestAllBlocksHaveSettings(TestCase):
    """Every section-level block must have a 'settings' field."""

    def test_all_section_blocks_have_settings(self):
        missing = []
        for block_class in SECTION_BLOCKS:
            block = block_class()
            if "settings" not in block.child_blocks:
                missing.append(block_class.__name__)
        self.assertEqual(
            missing, [],
            f"Blocks missing 'settings' field: {', '.join(missing)}",
        )

    def test_settings_is_block_settings_type(self):
        for block_class in SECTION_BLOCKS:
            block = block_class()
            settings_block = block.child_blocks.get("settings")
            if settings_block:
                self.assertIsInstance(
                    settings_block, BlockSettings,
                    f"{block_class.__name__}.settings is not BlockSettings",
                )


class TestBlockAttrsTag(TestCase):
    """Template tag block_attrs must render correct HTML attributes."""

    def _render(self, settings, base_class=""):
        tpl = Template(
            '{% load website_tags %}{% block_attrs settings base_class %}'
        )
        ctx = Context({"settings": settings, "base_class": base_class})
        return tpl.render(ctx).strip()

    def test_empty_settings_no_base(self):
        result = self._render(None, "")
        self.assertEqual(result, "")

    def test_empty_settings_with_base(self):
        result = self._render(None, "block-cta")
        self.assertIn('class="block-cta"', result)

    def test_custom_id(self):
        result = self._render(
            {"custom_id": "my-section", "custom_class": "", "background": "default", "padding": "md"},
            "block-cta",
        )
        self.assertIn('id="my-section"', result)

    def test_custom_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": "extra special", "background": "default", "padding": "md"},
            "block-cta",
        )
        self.assertIn("extra", result)
        self.assertIn("special", result)

    def test_background_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": "", "background": "dark", "padding": "md"},
            "block-cta",
        )
        self.assertIn("bg-dark", result)

    def test_default_background_no_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": "", "background": "default", "padding": "md"},
            "block-cta",
        )
        self.assertNotIn("bg-default", result)

    def test_padding_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": "", "background": "default", "padding": "lg"},
            "block-cta",
        )
        self.assertIn("pad-lg", result)

    def test_default_padding_no_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": "", "background": "default", "padding": "md"},
            "block-cta",
        )
        self.assertNotIn("pad-md", result)

    def test_full_settings(self):
        result = self._render(
            {"custom_id": "hero1", "custom_class": "featured", "background": "primary", "padding": "lg"},
            "block-hero",
        )
        self.assertIn('id="hero1"', result)
        self.assertIn("block-hero", result)
        self.assertIn("bg-primary", result)
        self.assertIn("pad-lg", result)
        self.assertIn("featured", result)

    def test_xss_sanitization_id(self):
        result = self._render(
            {"custom_id": 'test"><script>alert(1)</script>', "custom_class": "", "background": "default", "padding": "md"},
            "",
        )
        self.assertNotIn("<script>", result)
        self.assertNotIn('">', result)

    def test_xss_sanitization_class(self):
        result = self._render(
            {"custom_id": "", "custom_class": 'good"><script>bad</script>', "background": "default", "padding": "md"},
            "",
        )
        self.assertNotIn("<script>", result)

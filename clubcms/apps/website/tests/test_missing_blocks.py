"""
T11 — Test blocchi StreamField mancanti.

Verifica che i 7 nuovi blocchi esistano, abbiano settings,
e siano registrati nelle liste CONTENT_BLOCKS.
"""

from pathlib import Path

from django.conf import settings as django_settings
from django.test import TestCase

from apps.website.blocks import (
    CONTENT_BLOCKS,
    CounterUpBlock,
    FAQBlock,
    FeaturedPagesBlock,
    PricingTableBlock,
    SocialFeedBlock,
    TableBlock,
    TestimonialsBlock,
)
from apps.website.blocks.common import BlockSettings


NEW_BLOCKS = [
    TableBlock,
    TestimonialsBlock,
    FeaturedPagesBlock,
    FAQBlock,
    PricingTableBlock,
    CounterUpBlock,
    SocialFeedBlock,
]

NEW_BLOCK_NAMES = [
    "table",
    "testimonials",
    "featured_pages",
    "faq",
    "pricing_table",
    "counter_up",
    "social_feed",
]


class TestNewBlocksExist(TestCase):
    """All 7 new blocks must be importable and have correct structure."""

    def test_blocks_importable(self):
        for block_class in NEW_BLOCKS:
            block = block_class()
            self.assertIsNotNone(block)

    def test_blocks_have_settings(self):
        for block_class in NEW_BLOCKS:
            block = block_class()
            self.assertIn(
                "settings",
                block.child_blocks,
                f"{block_class.__name__} missing settings field",
            )
            self.assertIsInstance(
                block.child_blocks["settings"],
                BlockSettings,
            )

    def test_blocks_have_meta_template(self):
        for block_class in NEW_BLOCKS:
            block = block_class()
            self.assertTrue(
                hasattr(block.meta, "template"),
                f"{block_class.__name__} missing Meta.template",
            )

    def test_blocks_have_meta_label(self):
        for block_class in NEW_BLOCKS:
            block = block_class()
            self.assertTrue(
                hasattr(block.meta, "label"),
                f"{block_class.__name__} missing Meta.label",
            )


class TestNewBlocksRegistered(TestCase):
    """New blocks must appear in CONTENT_BLOCKS list."""

    def test_all_new_blocks_in_content_blocks(self):
        registered_names = [name for name, _ in CONTENT_BLOCKS]
        for name in NEW_BLOCK_NAMES:
            self.assertIn(
                name,
                registered_names,
                f"Block '{name}' not found in CONTENT_BLOCKS",
            )


class TestNewBlockTemplatesExist(TestCase):
    """Each new block must have a corresponding template file."""

    def test_templates_exist(self):
        templates_dir = Path(django_settings.BASE_DIR) / "templates" / "website" / "blocks"
        expected_templates = [
            "table_block.html",
            "testimonials_block.html",
            "featured_pages_block.html",
            "faq_block.html",
            "pricing_table_block.html",
            "counter_up_block.html",
            "social_feed_block.html",
        ]
        for tpl in expected_templates:
            self.assertTrue(
                (templates_dir / tpl).exists(),
                f"Template missing: {tpl}",
            )


class TestTableBlockStructure(TestCase):
    """TableBlock has headers and rows."""

    def test_has_headers(self):
        block = TableBlock()
        self.assertIn("headers", block.child_blocks)

    def test_has_rows(self):
        block = TableBlock()
        self.assertIn("rows", block.child_blocks)

    def test_has_striped(self):
        block = TableBlock()
        self.assertIn("striped", block.child_blocks)


class TestFAQBlockStructure(TestCase):
    """FAQBlock has items with question/answer."""

    def test_has_items(self):
        block = FAQBlock()
        self.assertIn("items", block.child_blocks)

    def test_faq_template_has_schema(self):
        templates_dir = Path(django_settings.BASE_DIR) / "templates" / "website" / "blocks"
        content = (templates_dir / "faq_block.html").read_text()
        self.assertIn("schema.org/FAQPage", content)
        self.assertIn("schema.org/Question", content)


class TestPricingTableStructure(TestCase):
    """PricingTableBlock has plans with features."""

    def test_has_plans(self):
        block = PricingTableBlock()
        self.assertIn("plans", block.child_blocks)


class TestCounterUpStructure(TestCase):
    """CounterUpBlock has counters with value/suffix/label."""

    def test_has_counters(self):
        block = CounterUpBlock()
        self.assertIn("counters", block.child_blocks)

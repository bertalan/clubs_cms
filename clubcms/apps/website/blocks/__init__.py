"""
Website StreamField blocks package.

This module exports all block classes and pre-built block lists used by
the page models in apps.website.models.pages.

Block Lists
-----------
- HERO_BLOCKS: Hero/banner section blocks
- CONTENT_BLOCKS: General content blocks (includes RichTextBlock)
- MEDIA_BLOCKS: Image, video, document, and map blocks
- LAYOUT_BLOCKS: Structural layout blocks
- ROUTE_BLOCKS: Route and waypointblocks

Combined Lists (used by StreamField definitions in page models)
---------------------------------------------------------------
- BODY_BLOCKS: Standard page body (content + media + layout)
- HOME_BLOCKS: Homepage body (body + hero/CTA blocks)
- NEWS_BLOCKS: News article body (body + gallery)
- EVENT_BLOCKS: Event detail body (body + gallery + map + route)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import RichTextBlock

# --- Hero blocks ---
from .hero import (
    HeroBannerBlock,
    HeroCountdownBlock,
    HeroSliderBlock,
    HeroVideoBlock,
)

# --- Content blocks ---
from .content import (
    AlertBlock,
    CardBlock,
    CardsGridBlock,
    CTABlock,
    NewsletterSignupBlock,
    QuoteBlock,
    StatsBlock,
    TeamGridBlock,
    TeamMemberBlock,
    TimelineBlock,
)

# --- Media blocks ---
from .media import (
    DocumentBlock,
    DocumentListBlock,
    GalleryBlock,
    GalleryImageBlock,
    ImageBlock,
    MapBlock,
    VideoEmbedBlock,
)

# --- Layout blocks ---
from .layout import (
    AccordionBlock,
    DividerBlock,
    SectionBlock,
    SpacerBlock,
    TabsBlock,
    TwoColumnBlock,
)

# --- Route blocks ---
from .route import RouteBlock, WaypointBlock


# ═══════════════════════════════════════════════════════════════════════════
# Block list definitions
# Each list is a sequence of (name, block_instance) tuples suitable for
# use as a StreamField argument.
# ═══════════════════════════════════════════════════════════════════════════

HERO_BLOCKS = [
    ("hero_slider", HeroSliderBlock()),
    ("hero_banner", HeroBannerBlock()),
    ("hero_countdown", HeroCountdownBlock()),
    ("hero_video", HeroVideoBlock()),
]

CONTENT_BLOCKS = [
    ("rich_text", RichTextBlock(icon="pilcrow")),
    ("cards_grid", CardsGridBlock()),
    ("cta", CTABlock()),
    ("stats", StatsBlock()),
    ("quote", QuoteBlock()),
    ("timeline", TimelineBlock()),
    ("team_grid", TeamGridBlock()),
    ("newsletter_signup", NewsletterSignupBlock()),
    ("alert", AlertBlock()),
]

MEDIA_BLOCKS = [
    ("image", ImageBlock()),
    ("gallery", GalleryBlock()),
    ("video_embed", VideoEmbedBlock()),
    ("document", DocumentBlock()),
    ("document_list", DocumentListBlock()),
    ("map", MapBlock()),
]

LAYOUT_BLOCKS = [
    ("accordion", AccordionBlock()),
    ("tabs", TabsBlock()),
    ("two_columns", TwoColumnBlock()),
    ("section", SectionBlock()),
    ("divider", DividerBlock()),
    ("spacer", SpacerBlock()),
]

ROUTE_BLOCKS = [
    ("route", RouteBlock()),
]

# ---------------------------------------------------------------------------
# Combined block lists for page StreamField definitions
# ---------------------------------------------------------------------------

BODY_BLOCKS = CONTENT_BLOCKS + MEDIA_BLOCKS + LAYOUT_BLOCKS

HOME_BLOCKS = HERO_BLOCKS + BODY_BLOCKS

NEWS_BLOCKS = BODY_BLOCKS + [
    ("news_gallery", GalleryBlock(label=_("Article gallery"))),
]

EVENT_BLOCKS = BODY_BLOCKS + ROUTE_BLOCKS + [
    ("event_gallery", GalleryBlock(label=_("Event gallery"))),
    ("event_map", MapBlock(label=_("Event location map"))),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # Hero
    "HeroSliderBlock",
    "HeroBannerBlock",
    "HeroCountdownBlock",
    "HeroVideoBlock",
    # Content
    "CardBlock",
    "CardsGridBlock",
    "CTABlock",
    "StatsBlock",
    "QuoteBlock",
    "TimelineBlock",
    "TeamMemberBlock",
    "TeamGridBlock",
    "NewsletterSignupBlock",
    "AlertBlock",
    # Media
    "GalleryImageBlock",
    "GalleryBlock",
    "VideoEmbedBlock",
    "ImageBlock",
    "DocumentBlock",
    "DocumentListBlock",
    "MapBlock",
    # Layout
    "AccordionBlock",
    "TabsBlock",
    "TwoColumnBlock",
    "SectionBlock",
    "DividerBlock",
    "SpacerBlock",
    # Route
    "WaypointBlock",
    "RouteBlock",
    # Block lists
    "HERO_BLOCKS",
    "CONTENT_BLOCKS",
    "MEDIA_BLOCKS",
    "LAYOUT_BLOCKS",
    "ROUTE_BLOCKS",
    "BODY_BLOCKS",
    "HOME_BLOCKS",
    "NEWS_BLOCKS",
    "EVENT_BLOCKS",
]

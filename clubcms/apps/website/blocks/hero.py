"""
Hero section blocks for the Club CMS website.

These blocks provide various hero/banner section layouts for page headers.
Template convention: website/blocks/{block_name_snake_case}.html
CSS class convention: block-{block-name} (kebab-case)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock


# ---------------------------------------------------------------------------
# HeroSliderBlock
# ---------------------------------------------------------------------------


class HeroSlideBlock(StructBlock):
    """A single slide within the hero slider."""

    image = ImageChooserBlock(
        required=True,
        help_text=_("Slide background image."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Slide headline."),
    )
    subtitle = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional subtitle text."),
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("CTA text"),
        help_text=_("Button label."),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("CTA page link"),
    )
    cta_url = URLBlock(
        required=False,
        label=_("CTA external URL"),
        help_text=_("Used only if no internal page is selected."),
    )

    class Meta:
        icon = "image"
        label = _("Slide")


class HeroSliderBlock(StructBlock):
    """
    Full-width hero carousel with multiple slides.
    Supports autoplay, navigation arrows, and dot indicators.
    """

    slides = ListBlock(
        HeroSlideBlock(),
        min_num=1,
        label=_("Slides"),
    )
    autoplay = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Automatically advance slides."),
    )
    interval = IntegerBlock(
        default=5000,
        help_text=_("Time between slides in milliseconds."),
    )
    height = ChoiceBlock(
        choices=[
            ("auto", _("Auto")),
            ("50vh", _("Half screen")),
            ("75vh", _("Three-quarter screen")),
            ("100vh", _("Full screen")),
        ],
        default="75vh",
        help_text=_("Slider height."),
    )
    show_arrows = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Show navigation arrows."),
    )
    show_dots = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Show dot indicators."),
    )

    class Meta:
        template = "website/blocks/hero_slider_block.html"
        icon = "image"
        label = _("Hero slider")


# ---------------------------------------------------------------------------
# HeroBannerBlock
# ---------------------------------------------------------------------------


class HeroBannerBlock(StructBlock):
    """
    Single hero image with text overlay and optional CTA button.
    """

    image = ImageChooserBlock(
        required=True,
        help_text=_("Hero background image."),
    )
    badge = CharBlock(
        max_length=100,
        required=False,
        help_text=_("Small badge text above the title (e.g. 'Est. 2010')."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Main headline."),
    )
    subtitle = TextBlock(
        required=False,
        help_text=_("Supporting text below the title."),
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("CTA text"),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("CTA page link"),
    )
    cta_url = URLBlock(
        required=False,
        label=_("CTA external URL"),
    )
    secondary_cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("Secondary CTA text"),
        help_text=_("Optional secondary button label."),
    )
    secondary_cta_link = PageChooserBlock(
        required=False,
        label=_("Secondary CTA page link"),
    )
    secondary_cta_url = URLBlock(
        required=False,
        label=_("Secondary CTA external URL"),
        help_text=_("Used only if no internal page is selected."),
    )
    overlay = ChoiceBlock(
        choices=[
            ("none", _("None")),
            ("light", _("Light overlay")),
            ("dark", _("Dark overlay")),
            ("gradient", _("Gradient overlay")),
        ],
        default="dark",
        help_text=_("Overlay style over the background image."),
    )
    text_position = ChoiceBlock(
        choices=[
            ("center", _("Center")),
            ("left", _("Left")),
            ("right", _("Right")),
            ("bottom-left", _("Bottom left")),
            ("bottom-right", _("Bottom right")),
        ],
        default="center",
        help_text=_("Position of the text overlay."),
    )
    height = ChoiceBlock(
        choices=[
            ("auto", _("Auto")),
            ("50vh", _("Half screen")),
            ("75vh", _("Three-quarter screen")),
            ("100vh", _("Full screen")),
        ],
        default="75vh",
    )

    class Meta:
        template = "website/blocks/hero_banner_block.html"
        icon = "image"
        label = _("Hero banner")


# ---------------------------------------------------------------------------
# HeroCountdownBlock
# ---------------------------------------------------------------------------


class HeroCountdownBlock(StructBlock):
    """
    Hero section with a countdown timer targeting a specific event page.
    Ideal for promoting upcoming events with urgency.
    """

    event = PageChooserBlock(
        page_type="website.EventDetailPage",
        required=True,
        help_text=_("Select an event to count down to."),
    )
    background_image = ImageChooserBlock(
        required=False,
        help_text=_("Optional background image. Falls back to event cover image."),
    )
    title_override = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Override the event title in the hero."),
    )
    show_registration_button = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Show a registration CTA button if registration is open."),
    )

    class Meta:
        template = "website/blocks/hero_countdown_block.html"
        icon = "date"
        label = _("Hero countdown")


# ---------------------------------------------------------------------------
# HeroVideoBlock
# ---------------------------------------------------------------------------


class HeroVideoBlock(StructBlock):
    """
    Video background hero section with fallback image for mobile
    and accessibility.
    """

    video_url = URLBlock(
        required=True,
        help_text=_("URL to the video file (MP4 recommended)."),
    )
    fallback_image = ImageChooserBlock(
        required=True,
        help_text=_("Displayed on mobile or when video cannot play."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
    )
    subtitle = TextBlock(
        required=False,
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("CTA text"),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("CTA page link"),
    )
    cta_url = URLBlock(
        required=False,
        label=_("CTA external URL"),
    )
    muted = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Mute the video (required for autoplay on most browsers)."),
    )
    loop = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Loop the video."),
    )

    class Meta:
        template = "website/blocks/hero_video_block.html"
        icon = "media"
        label = _("Hero video")

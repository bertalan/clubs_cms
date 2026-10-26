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

from .common import BlockSettings


# ---------------------------------------------------------------------------
# HeroSliderBlock
# ---------------------------------------------------------------------------


class HeroSlideBlock(StructBlock):
    """A single slide within the hero slider."""

    image = ImageChooserBlock(
        required=True,
        label=_("Background image"),
        help_text=_("Cropped to 1920 x 900 pixels, so use a wide landscape image."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
        help_text=_("Also read out by screen readers as the description of the image."),
    )
    subtitle = CharBlock(
        max_length=255,
        required=False,
        label=_("Subtitle"),
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("Button text"),
        help_text=_(
            "The button appears only when you "
            "also choose a page or enter a link."
        ),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("Button link to page"),
        help_text=_("Takes priority over the external link."),
    )
    cta_url = URLBlock(
        required=False,
        label=_("Button external link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
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
        label=_("Autoplay"),
    )
    interval = IntegerBlock(
        default=5000,
        label=_("Time per slide"),
        help_text=_("In milliseconds: 5000 means 5 seconds."),
    )
    height = ChoiceBlock(
        choices=[
            ("auto", _("Auto")),
            ("50vh", _("Half screen")),
            ("75vh", _("Three-quarter screen")),
            ("100vh", _("Full screen")),
        ],
        default="75vh",
        label=_("Height"),
    )
    show_arrows = BooleanBlock(
        default=True,
        required=False,
        label=_("Show arrows"),
    )
    show_dots = BooleanBlock(
        default=True,
        required=False,
        label=_("Show dots"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Background image"),
        help_text=_("Cropped to 1920 x 900 pixels, so use a wide landscape image."),
    )
    badge = CharBlock(
        max_length=100,
        required=False,
        label=_("Badge"),
        help_text=_("Small text above the title, for example Est. 2010."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
        help_text=_("Also read out by screen readers as the description of the image."),
    )
    subtitle = TextBlock(
        required=False,
        label=_("Subtitle"),
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("Button text"),
        help_text=_(
            "The button appears only when you "
            "also choose a page or enter a link."
        ),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("Button link to page"),
        help_text=_("Takes priority over the external link."),
    )
    cta_url = URLBlock(
        required=False,
        label=_("Button external link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
    )
    secondary_cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("Second button text"),
        help_text=_(
            "Shown as an outlined button after the first one. It also needs "
            "a page or a link."
        ),
    )
    secondary_cta_link = PageChooserBlock(
        required=False,
        label=_("Second button link to page"),
        help_text=_("Takes priority over the external link."),
    )
    secondary_cta_url = URLBlock(
        required=False,
        label=_("Second button external link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
    )
    overlay = ChoiceBlock(
        choices=[
            ("none", _("None")),
            ("light", _("Light overlay")),
            ("dark", _("Dark overlay")),
            ("gradient", _("Gradient overlay")),
        ],
        default="dark",
        label=_("Overlay"),
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
        label=_("Text position"),
    )
    height = ChoiceBlock(
        choices=[
            ("auto", _("Auto")),
            ("50vh", _("Half screen")),
            ("75vh", _("Three-quarter screen")),
            ("100vh", _("Full screen")),
        ],
        default="75vh",
        label=_("Height"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Event"),
        help_text=_("The countdown runs to the start date and time of this event."),
    )
    background_image = ImageChooserBlock(
        required=False,
        label=_("Background image"),
        help_text=_("Cropped to 1920 x 700 pixels. If empty, no image is shown."),
    )
    title_override = CharBlock(
        max_length=255,
        required=False,
        label=_("Custom title"),
        help_text=_("If empty, the event title is used."),
    )
    show_registration_button = BooleanBlock(
        default=True,
        required=False,
        label=_("Show registration button"),
        help_text=_(
            "Shows Register now while registration is open. Otherwise the "
            "button reads View details."
        ),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Video file link"),
        help_text=_(
            "Direct link to an MP4 file, for example "
            "https://example.com/ride.mp4. YouTube and Vimeo links do not work here."
        ),
    )
    fallback_image = ImageChooserBlock(
        required=True,
        label=_("Fallback image"),
        help_text=_("Cropped to 1920 x 900 pixels, so use a wide landscape image."),
    )
    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
    )
    subtitle = TextBlock(
        required=False,
        label=_("Subtitle"),
    )
    cta_text = CharBlock(
        max_length=120,
        required=False,
        label=_("Button text"),
        help_text=_(
            "The button appears only when you "
            "also choose a page or enter a link."
        ),
    )
    cta_link = PageChooserBlock(
        required=False,
        label=_("Button link to page"),
        help_text=_("Takes priority over the external link."),
    )
    cta_url = URLBlock(
        required=False,
        label=_("Button external link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
    )
    muted = BooleanBlock(
        default=True,
        required=False,
        label=_("Mute video"),
        help_text=_("Most browsers start a video on their own only when it is muted."),
    )
    loop = BooleanBlock(
        default=True,
        required=False,
        label=_("Loop video"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/hero_video_block.html"
        icon = "media"
        label = _("Hero video")

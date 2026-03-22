"""
Email-safe StreamField blocks for newsletter composition.

These blocks produce content that can be rendered as inline-styled HTML
for email clients. Intentionally limited to elements that work reliably
across all major email clients (Gmail, Outlook, Apple Mail, etc.).
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    RichTextBlock,
    StaticBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock


class NewsletterImageBlock(StructBlock):
    """Single image with optional caption, email-safe."""

    image = ImageChooserBlock(required=True, label=_("Image"))
    caption = CharBlock(
        max_length=255,
        required=False,
        label=_("Caption"),
        help_text=_("Optional caption below the image."),
    )
    alt_text = CharBlock(
        max_length=255,
        required=False,
        label=_("Alt text"),
        help_text=_("Accessibility description of the image."),
    )

    class Meta:
        icon = "image"
        label = _("Image")


class NewsletterButtonBlock(StructBlock):
    """Call-to-action button, rendered as a linked table cell for email."""

    text = CharBlock(max_length=100, label=_("Button text"))
    url = URLBlock(label=_("Link URL"))
    style = ChoiceBlock(
        choices=[
            ("primary", _("Primary (blue)")),
            ("secondary", _("Secondary (grey)")),
        ],
        default="primary",
        label=_("Style"),
    )

    class Meta:
        icon = "link"
        label = _("Button")


class NewsletterQuoteBlock(StructBlock):
    """Blockquote with optional attribution."""

    text = TextBlock(label=_("Quote text"))
    attribution = CharBlock(
        max_length=200,
        required=False,
        label=_("Attribution"),
        help_text=_("Who said this (optional)."),
    )

    class Meta:
        icon = "openquote"
        label = _("Quote")


# ═══════════════════════════════════════════════════════════════════════════
# Block list for newsletter StreamField
# ═══════════════════════════════════════════════════════════════════════════

NEWSLETTER_BLOCKS = [
    (
        "heading",
        CharBlock(
            icon="title",
            max_length=255,
            label=_("Heading"),
            help_text=_("Section heading."),
        ),
    ),
    (
        "text",
        RichTextBlock(
            icon="pilcrow",
            label=_("Text"),
            features=["bold", "italic", "link", "ol", "ul", "hr"],
        ),
    ),
    ("image", NewsletterImageBlock()),
    ("button", NewsletterButtonBlock()),
    ("divider", StaticBlock(admin_text="───", icon="horizontalrule", label=_("Divider"))),
    ("quote", NewsletterQuoteBlock()),
]

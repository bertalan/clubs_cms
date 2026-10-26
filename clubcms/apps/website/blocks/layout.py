"""
Layout blocks for the Club CMS website.

Structural blocks for organising content in sections, columns, tabs, etc.
Template convention: website/blocks/{block_name_snake_case}.html
CSS class convention: block-{block-name} (kebab-case)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    CharBlock,
    ChoiceBlock,
    ListBlock,
    RichTextBlock,
    StructBlock,
)
from wagtail.images.blocks import ImageChooserBlock

from .common import BlockSettings


# ---------------------------------------------------------------------------
# AccordionBlock
# ---------------------------------------------------------------------------


class AccordionItemBlock(StructBlock):
    """A single expandable accordion panel."""

    title = CharBlock(
        max_length=255,
        required=True,
        label=_("Title"),
    )
    content = RichTextBlock(
        required=True,
        label=_("Content"),
        help_text=_("Hidden until the visitor clicks the title."),
    )

    class Meta:
        icon = "list-ul"
        label = _("Accordion item")


class AccordionBlock(StructBlock):
    """
    Expandable / collapsible content sections.
    Ideal for FAQs and detailed information.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Section title"),
    )
    items = ListBlock(
        AccordionItemBlock(),
        min_num=1,
        label=_("Panels"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/accordion_block.html"
        icon = "list-ul"
        label = _("Accordion")


# ---------------------------------------------------------------------------
# TabsBlock
# ---------------------------------------------------------------------------


class TabItemBlock(StructBlock):
    """A single tab with title and content."""

    title = CharBlock(
        max_length=255,
        required=True,
        label=_("Tab title"),
        help_text=_("Keep it short so that all the tabs fit on one row."),
    )
    content = RichTextBlock(
        required=True,
        label=_("Content"),
    )

    class Meta:
        icon = "form"
        label = _("Tab")


class TabsBlock(StructBlock):
    """
    Tabbed content block. Each tab has a title and rich text content.
    """

    tabs = ListBlock(
        TabItemBlock(),
        min_num=2,
        label=_("Tabs"),
        help_text=_("Add at least 2 tabs. The first tab is open when the page loads."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/tabs_block.html"
        icon = "form"
        label = _("Tabs")


# ---------------------------------------------------------------------------
# TwoColumnBlock
# ---------------------------------------------------------------------------


class TwoColumnBlock(StructBlock):
    """
    Two-column layout with configurable split ratio.
    """

    left_column = RichTextBlock(
        required=True,
        label=_("Left column"),
    )
    right_column = RichTextBlock(
        required=True,
        label=_("Right column"),
    )
    split = ChoiceBlock(
        choices=[
            ("50-50", _("50 / 50")),
            ("33-67", _("33 / 67")),
            ("67-33", _("67 / 33")),
            ("25-75", _("25 / 75")),
            ("75-25", _("75 / 25")),
        ],
        default="50-50",
        label=_("Column widths"),
        help_text=_("Share of the width in percent, left column first."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/two_column_block.html"
        icon = "placeholder"
        label = _("Two columns")


# ---------------------------------------------------------------------------
# SectionBlock
# ---------------------------------------------------------------------------


class SectionBlock(StructBlock):
    """
    Full-width section wrapper with background options and padding controls.
    Use this to group content visually.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        label=_("Title"),
    )
    content = RichTextBlock(
        required=True,
        label=_("Content"),
    )
    background = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("secondary", _("Secondary colour")),
            ("dark", _("Dark")),
            ("light", _("Light grey")),
            ("image", _("Image background")),
        ],
        default="default",
        label=_("Background"),
    )
    background_image = ImageChooserBlock(
        required=False,
        label=_("Background image"),
        help_text=_(
            "Cropped to 1920 x 900 pixels and shown faintly behind the "
            "content, whatever background you choose above."
        ),
    )
    padding = ChoiceBlock(
        choices=[
            ("sm", _("Small")),
            ("md", _("Medium")),
            ("lg", _("Large")),
            ("xl", _("Extra large")),
        ],
        default="md",
        label=_("Padding"),
        help_text=_("Empty space above and below the content."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/section_block.html"
        icon = "placeholder"
        label = _("Section")


# ---------------------------------------------------------------------------
# DividerBlock
# ---------------------------------------------------------------------------


class DividerBlock(StructBlock):
    """
    Visual separator between content sections.
    """

    style = ChoiceBlock(
        choices=[
            ("line", _("Horizontal line")),
            ("dots", _("Dots")),
            ("space", _("Blank space")),
        ],
        default="line",
        label=_("Style"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/divider_block.html"
        icon = "horizontalrule"
        label = _("Divider")


# ---------------------------------------------------------------------------
# SpacerBlock
# ---------------------------------------------------------------------------


class SpacerBlock(StructBlock):
    """
    Vertical whitespace block for controlling spacing between sections.
    """

    size = ChoiceBlock(
        choices=[
            ("sm", _("Small (1rem)")),
            ("md", _("Medium (2rem)")),
            ("lg", _("Large (4rem)")),
            ("xl", _("Extra large (6rem)")),
        ],
        default="md",
        label=_("Size"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/spacer_block.html"
        icon = "arrows-up-down"
        label = _("Spacer")

"""
Content blocks for the Club CMS website.

General-purpose content blocks for building rich page layouts.
Template convention: website/blocks/{block_name_snake_case}.html
CSS class convention: block-{block-name} (kebab-case)
"""

from django.utils.translation import gettext_lazy as _

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    EmailBlock,
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
# CardBlock / CardsGridBlock
# ---------------------------------------------------------------------------


class CardBlock(StructBlock):
    """
    A single content card with image, title, text, and link.
    Typically used inside a CardsGridBlock.
    """

    image = ImageChooserBlock(
        required=False,
        help_text=_("Card thumbnail image."),
    )
    badge_text = CharBlock(
        max_length=100,
        required=False,
        help_text=_("Optional badge text (e.g. date, category label)."),
    )
    title = CharBlock(
        max_length=255,
        required=True,
        help_text=_("Card title."),
    )
    text = TextBlock(
        required=False,
        help_text=_("Short description text."),
    )
    link_page = PageChooserBlock(
        required=False,
        label=_("Link to page"),
    )
    link_url = URLBlock(
        required=False,
        label=_("External URL"),
        help_text=_("Used only if no internal page is selected."),
    )
    link_text = CharBlock(
        max_length=120,
        required=False,
        default=_("Read more"),
        help_text=_("Button / link label."),
    )

    class Meta:
        template = "website/blocks/card_block.html"
        icon = "doc-full"
        label = _("Card")


class CardsGridBlock(StructBlock):
    """
    A grid of content cards with configurable columns and style.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional section title above the grid."),
    )
    cards = ListBlock(
        CardBlock(),
        min_num=1,
        label=_("Cards"),
    )
    columns = ChoiceBlock(
        choices=[
            ("2", _("2 columns")),
            ("3", _("3 columns")),
            ("4", _("4 columns")),
        ],
        default="3",
        help_text=_("Number of columns on desktop."),
    )
    style = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("outlined", _("Outlined")),
            ("elevated", _("Elevated / shadow")),
            ("minimal", _("Minimal")),
        ],
        default="default",
        help_text=_("Visual style for the cards."),
    )

    class Meta:
        template = "website/blocks/cards_grid_block.html"
        icon = "grid"
        label = _("Cards grid")


# ---------------------------------------------------------------------------
# CTABlock
# ---------------------------------------------------------------------------


class CTABlock(StructBlock):
    """
    Call-to-action section with title, rich text, and button.
    """

    title = CharBlock(
        max_length=255,
        required=True,
        help_text=_("CTA headline."),
    )
    text = RichTextBlock(
        required=False,
        help_text=_("Supporting text."),
    )
    button_text = CharBlock(
        max_length=120,
        required=True,
        help_text=_("Button label."),
    )
    button_link = PageChooserBlock(
        required=False,
        label=_("Button page link"),
    )
    button_url = URLBlock(
        required=False,
        label=_("Button external URL"),
        help_text=_("Used only if no internal page is selected."),
    )
    background_style = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("dark", _("Dark")),
            ("light", _("Light")),
            ("gradient", _("Gradient")),
            ("image", _("Image background")),
        ],
        default="primary",
        help_text=_("Background style for this section."),
    )
    background_image = ImageChooserBlock(
        required=False,
        help_text=_("Background image (only used with 'Image background' style)."),
    )

    class Meta:
        template = "website/blocks/cta_block.html"
        icon = "pick"
        label = _("Call to action")


# ---------------------------------------------------------------------------
# StatsBlock
# ---------------------------------------------------------------------------


class StatItemBlock(StructBlock):
    """A single statistic item (e.g., '1500+' / 'Members')."""

    value = CharBlock(
        max_length=50,
        required=True,
        help_text=_("The numeric value or short text (e.g. '1500+')."),
    )
    label = CharBlock(
        max_length=100,
        required=True,
        help_text=_("Description of the stat (e.g. 'Members')."),
    )
    icon = CharBlock(
        max_length=50,
        required=False,
        help_text=_("Optional icon class name."),
    )

    class Meta:
        icon = "order"
        label = _("Statistic")


class StatsBlock(StructBlock):
    """
    Statistics / key numbers section showing multiple stat items.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional section title."),
    )
    stats = ListBlock(
        StatItemBlock(),
        min_num=1,
        label=_("Statistics"),
    )
    background_style = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("dark", _("Dark")),
            ("light", _("Light")),
        ],
        default="default",
    )

    class Meta:
        template = "website/blocks/stats_block.html"
        icon = "order"
        label = _("Statistics")


# ---------------------------------------------------------------------------
# QuoteBlock
# ---------------------------------------------------------------------------


class QuoteBlock(StructBlock):
    """
    Blockquote with attribution (author, role, optional image).
    """

    quote = TextBlock(
        required=True,
        help_text=_("The quote text."),
    )
    author = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Name of the person quoted."),
    )
    role = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Role or title of the author (e.g. 'President')."),
    )
    image = ImageChooserBlock(
        required=False,
        help_text=_("Optional portrait of the author."),
    )

    class Meta:
        template = "website/blocks/quote_block.html"
        icon = "openquote"
        label = _("Quote")


# ---------------------------------------------------------------------------
# TimelineBlock
# ---------------------------------------------------------------------------


class TimelineItemBlock(StructBlock):
    """A single entry in a chronological timeline."""

    year = CharBlock(
        max_length=20,
        required=True,
        help_text=_("Year or date label (e.g. '2015')."),
    )
    title = CharBlock(
        max_length=255,
        required=True,
        help_text=_("Event or milestone title."),
    )
    description = RichTextBlock(
        required=False,
        help_text=_("Detailed description of this event."),
    )

    class Meta:
        icon = "date"
        label = _("Timeline entry")


class TimelineBlock(StructBlock):
    """
    Chronological timeline for club history or milestones.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional section title."),
    )
    items = ListBlock(
        TimelineItemBlock(),
        min_num=1,
        label=_("Timeline entries"),
    )

    class Meta:
        template = "website/blocks/timeline_block.html"
        icon = "date"
        label = _("Timeline")


# ---------------------------------------------------------------------------
# TeamMemberBlock / TeamGridBlock
# ---------------------------------------------------------------------------


class TeamMemberBlock(StructBlock):
    """
    A single team or board member profile card.
    """

    name = CharBlock(
        max_length=255,
        required=True,
    )
    role = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Position or title."),
    )
    photo = ImageChooserBlock(
        required=False,
    )
    bio = RichTextBlock(
        required=False,
        help_text=_("Short biography."),
    )
    email = EmailBlock(
        required=False,
    )
    phone = CharBlock(
        max_length=30,
        required=False,
    )

    class Meta:
        template = "website/blocks/team_member_block.html"
        icon = "user"
        label = _("Team member")


class TeamGridBlock(StructBlock):
    """
    Grid of team member cards, designed for board or staff pages.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional section title (e.g. 'Board of Directors')."),
    )
    members = ListBlock(
        TeamMemberBlock(),
        min_num=1,
        label=_("Team members"),
    )
    columns = ChoiceBlock(
        choices=[
            ("2", _("2 columns")),
            ("3", _("3 columns")),
            ("4", _("4 columns")),
        ],
        default="3",
    )

    class Meta:
        template = "website/blocks/team_grid_block.html"
        icon = "group"
        label = _("Team grid")


# ---------------------------------------------------------------------------
# NewsletterSignupBlock
# ---------------------------------------------------------------------------


class NewsletterSignupBlock(StructBlock):
    """
    Newsletter subscription form block.
    The form action should be handled by the site's newsletter integration.
    """

    heading = CharBlock(
        max_length=255,
        default=_("Stay updated"),
        help_text=_("Form heading."),
    )
    description = TextBlock(
        required=False,
        help_text=_("Short text explaining what subscribers will receive."),
    )
    button_text = CharBlock(
        max_length=120,
        default=_("Subscribe"),
    )
    background = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("dark", _("Dark")),
            ("light", _("Light")),
        ],
        default="primary",
    )

    class Meta:
        template = "website/blocks/newsletter_signup_block.html"
        icon = "mail"
        label = _("Newsletter signup")


# ---------------------------------------------------------------------------
# AlertBlock
# ---------------------------------------------------------------------------


class AlertBlock(StructBlock):
    """
    Notification or alert banner for important announcements.
    """

    message = RichTextBlock(
        required=True,
        help_text=_("Alert message content."),
    )
    alert_type = ChoiceBlock(
        choices=[
            ("info", _("Info")),
            ("success", _("Success")),
            ("warning", _("Warning")),
            ("danger", _("Danger")),
        ],
        default="info",
        help_text=_("Visual style and severity of the alert."),
    )
    dismissible = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Allow users to dismiss this alert."),
    )

    class Meta:
        template = "website/blocks/alert_block.html"
        icon = "warning"
        label = _("Alert")

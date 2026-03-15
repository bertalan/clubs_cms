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

from .common import BlockSettings


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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

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
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/alert_block.html"
        icon = "warning"
        label = _("Alert")


# ---------------------------------------------------------------------------
# PartnerBlock / PartnersGridBlock
# ---------------------------------------------------------------------------


class PartnerBlock(StructBlock):
    """A single partner or sponsor card."""

    name = CharBlock(
        max_length=255,
        required=True,
        label=_("Partner name"),
    )
    description = CharBlock(
        max_length=255,
        required=False,
        label=_("Description"),
        help_text=_("Short description or partner type."),
    )
    logo = ImageChooserBlock(
        required=False,
        label=_("Logo"),
    )
    url = URLBlock(
        required=False,
        label=_("Website URL"),
    )

    class Meta:
        icon = "globe"
        label = _("Partner")


class PartnersGridBlock(StructBlock):
    """
    Grid of partner / sponsor cards for the homepage or content pages.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional section title (e.g. 'Our Partners')."),
    )
    subtitle = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional subtitle text."),
    )
    partners = ListBlock(
        PartnerBlock(),
        min_num=1,
        label=_("Partners"),
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
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/partners_grid_block.html"
        icon = "globe"
        label = _("Partners grid")


# ---------------------------------------------------------------------------
# TableBlock
# ---------------------------------------------------------------------------


class TableRowBlock(StructBlock):
    """A single row of table cells."""

    cells = ListBlock(
        CharBlock(max_length=500),
        min_num=1,
        label=_("Cells"),
    )

    class Meta:
        icon = "list-ul"
        label = _("Row")


class TableBlock(StructBlock):
    """
    Data table with header row and body rows.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Optional table caption."),
    )
    headers = ListBlock(
        CharBlock(max_length=255),
        min_num=1,
        label=_("Column headers"),
    )
    rows = ListBlock(
        TableRowBlock(),
        min_num=1,
        label=_("Rows"),
    )
    striped = BooleanBlock(
        default=True,
        required=False,
        help_text=_("Alternate row background colours."),
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/table_block.html"
        icon = "list-ul"
        label = _("Table")


# ---------------------------------------------------------------------------
# TestimonialsBlock
# ---------------------------------------------------------------------------


class TestimonialBlock(StructBlock):
    """A single testimonial."""

    quote = TextBlock(
        required=True,
        help_text=_("Testimonial text."),
    )
    name = CharBlock(
        max_length=255,
        required=True,
    )
    role = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Title or role."),
    )
    avatar = ImageChooserBlock(
        required=False,
    )

    class Meta:
        icon = "openquote"
        label = _("Testimonial")


class TestimonialsBlock(StructBlock):
    """
    Testimonials carousel or grid.
    """

    title = CharBlock(
        max_length=255,
        required=False,
    )
    testimonials = ListBlock(
        TestimonialBlock(),
        min_num=1,
        label=_("Testimonials"),
    )
    layout = ChoiceBlock(
        choices=[
            ("carousel", _("Carousel")),
            ("grid", _("Grid")),
        ],
        default="carousel",
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/testimonials_block.html"
        icon = "openquote"
        label = _("Testimonials")


# ---------------------------------------------------------------------------
# FeaturedPagesBlock
# ---------------------------------------------------------------------------


class FeaturedPageBlock(StructBlock):
    """A single featured page selection."""

    page = PageChooserBlock(required=True)
    override_title = CharBlock(
        max_length=255,
        required=False,
        help_text=_("Override the page title."),
    )
    override_image = ImageChooserBlock(
        required=False,
        help_text=_("Override the page's default image."),
    )

    class Meta:
        icon = "doc-full"
        label = _("Featured page")


class FeaturedPagesBlock(StructBlock):
    """
    Manual selection of pages to highlight in a card grid.
    """

    title = CharBlock(
        max_length=255,
        required=False,
    )
    pages = ListBlock(
        FeaturedPageBlock(),
        min_num=1,
        max_num=12,
        label=_("Pages"),
    )
    columns = ChoiceBlock(
        choices=[
            ("2", _("2 columns")),
            ("3", _("3 columns")),
            ("4", _("4 columns")),
        ],
        default="3",
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/featured_pages_block.html"
        icon = "doc-full"
        label = _("Featured pages")


# ---------------------------------------------------------------------------
# FAQBlock
# ---------------------------------------------------------------------------


class FAQItemBlock(StructBlock):
    """A single question/answer pair."""

    question = CharBlock(
        max_length=500,
        required=True,
    )
    answer = RichTextBlock(
        required=True,
    )

    class Meta:
        icon = "help"
        label = _("FAQ item")


class FAQBlock(StructBlock):
    """
    FAQ section with accordion and schema.org FAQPage markup.
    """

    title = CharBlock(
        max_length=255,
        required=False,
        default=_("Frequently asked questions"),
    )
    items = ListBlock(
        FAQItemBlock(),
        min_num=1,
        label=_("Questions"),
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/faq_block.html"
        icon = "help"
        label = _("FAQ")


# ---------------------------------------------------------------------------
# PricingTableBlock
# ---------------------------------------------------------------------------


class PricingPlanBlock(StructBlock):
    """A single pricing plan."""

    name = CharBlock(
        max_length=100,
        required=True,
    )
    price = CharBlock(
        max_length=50,
        required=True,
        help_text=_("Price text (e.g. '€50/year')."),
    )
    description = TextBlock(
        required=False,
    )
    features = ListBlock(
        CharBlock(max_length=255),
        label=_("Features"),
    )
    cta_text = CharBlock(
        max_length=120,
        default=_("Choose plan"),
    )
    cta_link = PageChooserBlock(
        required=False,
    )
    cta_url = URLBlock(
        required=False,
    )
    highlighted = BooleanBlock(
        default=False,
        required=False,
        help_text=_("Highlight this plan as recommended."),
    )

    class Meta:
        icon = "tag"
        label = _("Pricing plan")


class PricingTableBlock(StructBlock):
    """
    Side-by-side pricing plans comparison.
    """

    title = CharBlock(
        max_length=255,
        required=False,
    )
    plans = ListBlock(
        PricingPlanBlock(),
        min_num=1,
        max_num=4,
        label=_("Plans"),
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/pricing_table_block.html"
        icon = "tag"
        label = _("Pricing table")


# ---------------------------------------------------------------------------
# CounterUpBlock
# ---------------------------------------------------------------------------


class CounterItemBlock(StructBlock):
    """A single animated counter."""

    value = IntegerBlock(
        required=True,
        help_text=_("Target number to count up to."),
    )
    suffix = CharBlock(
        max_length=20,
        required=False,
        help_text=_("Text after number (e.g. '+', '%', 'k')."),
    )
    label = CharBlock(
        max_length=100,
        required=True,
    )
    icon = CharBlock(
        max_length=50,
        required=False,
    )

    class Meta:
        icon = "order"
        label = _("Counter")


class CounterUpBlock(StructBlock):
    """
    Animated count-up counters section.
    """

    title = CharBlock(
        max_length=255,
        required=False,
    )
    counters = ListBlock(
        CounterItemBlock(),
        min_num=1,
        label=_("Counters"),
    )
    background_style = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("dark", _("Dark")),
        ],
        default="default",
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/counter_up_block.html"
        icon = "order"
        label = _("Animated counters")


# ---------------------------------------------------------------------------
# SocialFeedBlock
# ---------------------------------------------------------------------------


class SocialFeedBlock(StructBlock):
    """
    Embed social media feed or posts.
    """

    title = CharBlock(
        max_length=255,
        required=False,
    )
    platform = ChoiceBlock(
        choices=[
            ("instagram", _("Instagram")),
            ("facebook", _("Facebook")),
            ("twitter", _("X / Twitter")),
            ("youtube", _("YouTube")),
        ],
        default="instagram",
    )
    embed_url = URLBlock(
        required=True,
        help_text=_("URL of the social profile or post to embed."),
    )
    max_posts = IntegerBlock(
        default=6,
        min_value=1,
        max_value=12,
        help_text=_("Maximum number of posts to display."),
    )
    settings = BlockSettings(required=False)

    class Meta:
        template = "website/blocks/social_feed_block.html"
        icon = "site"
        label = _("Social feed")

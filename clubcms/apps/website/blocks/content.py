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
        label=_("Image"),
        help_text=_("Cropped to 400 x 250 pixels, so use a landscape image."),
    )
    badge_text = CharBlock(
        max_length=100,
        required=False,
        label=_("Badge"),
    )
    title = CharBlock(
        max_length=255,
        required=True,
        label=_("Title"),
        help_text=_("Also read out by screen readers as the description of the image."),
    )
    text = TextBlock(
        required=False,
        label=_("Text"),
        help_text=_("Plain text shown under the title, without formatting."),
    )
    link_page = PageChooserBlock(
        required=False,
        label=_("Link to page"),
        help_text=_("Takes priority over the external link."),
    )
    link_url = URLBlock(
        required=False,
        label=_("External link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
    )
    link_text = CharBlock(
        max_length=120,
        required=False,
        default=_("Read more"),
        label=_("Link text"),
        help_text=_("If empty, only the image links to the page."),
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
        label=_("Section title"),
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
        label=_("Columns"),
        help_text=_("Cards per row on wide screens. Phones show fewer per row."),
    )
    style = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("outlined", _("Outlined")),
            ("elevated", _("Elevated / shadow")),
            ("minimal", _("Minimal")),
        ],
        default="default",
        label=_("Card style"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Headline"),
    )
    text = RichTextBlock(
        required=False,
        label=_("Text"),
    )
    button_text = CharBlock(
        max_length=120,
        required=True,
        label=_("Button text"),
        help_text=_(
            "The button appears only when you "
            "also choose a page or enter a link."
        ),
    )
    button_link = PageChooserBlock(
        required=False,
        label=_("Button link to page"),
        help_text=_("Takes priority over the external link."),
    )
    button_url = URLBlock(
        required=False,
        label=_("Button external link"),
        help_text=_("Used only when no page is selected. Opens in a new tab."),
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
        label=_("Background"),
    )
    background_image = ImageChooserBlock(
        required=False,
        label=_("Background image"),
        help_text=_(
            "Cropped to 1920 x 600 pixels. If set, it is shown whatever "
            "background you choose above."
        ),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Value"),
        help_text=_("Number or short text, for example 1500+."),
    )
    label = CharBlock(
        max_length=100,
        required=True,
        label=_("Label"),
        help_text=_("Text shown with the value, for example Members."),
    )
    icon = CharBlock(
        max_length=50,
        required=False,
        label=_("Icon"),
        help_text=_(
            "Font Awesome class, for example fa-solid fa-users. "
            "If empty, no icon is shown."
        ),
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
        label=_("Section title"),
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
        label=_("Background"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Quote"),
    )
    author = CharBlock(
        max_length=255,
        required=False,
        label=_("Author"),
        help_text=_("If empty, the author role is not shown either."),
    )
    role = CharBlock(
        max_length=255,
        required=False,
        label=_("Author role"),
        help_text=_("For example President or Founding member."),
    )
    image = ImageChooserBlock(
        required=False,
        label=_("Author photo"),
        help_text=_("Cropped to a small 80 x 80 pixel square, so centre the face."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Year or date"),
        help_text=_("Short text, for example 2015 or May 2020."),
    )
    title = CharBlock(
        max_length=255,
        required=True,
        label=_("Title"),
    )
    description = RichTextBlock(
        required=False,
        label=_("Description"),
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
        label=_("Section title"),
    )
    items = ListBlock(
        TimelineItemBlock(),
        min_num=1,
        label=_("Timeline entries"),
        help_text=_("Entries appear in the order listed here, so sort them yourself."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Name"),
    )
    role = CharBlock(
        max_length=255,
        required=False,
        label=_("Role"),
        help_text=_("For example President or Treasurer."),
    )
    photo = ImageChooserBlock(
        required=False,
        label=_("Photo"),
        help_text=_("Cropped to a 300 x 300 pixel square."),
    )
    bio = RichTextBlock(
        required=False,
        label=_("Short biography"),
    )
    email = EmailBlock(
        required=False,
        label=_("Email"),
        help_text=_("Not shown on the public page."),
    )
    phone = CharBlock(
        max_length=30,
        required=False,
        label=_("Phone"),
        help_text=_("Not shown on the public page."),
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
        label=_("Section title"),
        help_text=_("For example Board of directors."),
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
        label=_("Columns"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Heading"),
    )
    description = TextBlock(
        required=False,
        label=_("Description"),
        help_text=_("Tell visitors what they will receive and how often."),
    )
    button_text = CharBlock(
        max_length=120,
        default=_("Subscribe"),
        label=_("Button text"),
    )
    background = ChoiceBlock(
        choices=[
            ("default", _("Default")),
            ("primary", _("Primary colour")),
            ("dark", _("Dark")),
            ("light", _("Light")),
        ],
        default="primary",
        label=_("Background"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    def get_context(self, value, parent_context=None):
        ctx = super().get_context(value, parent_context=parent_context)
        from apps.website.models.newsletter import NewsletterPage

        page = NewsletterPage.objects.live().first()
        if page:
            ctx["newsletter_subscribe_url"] = page.url + page.reverse_subpage(
                "subscribe"
            )
        else:
            ctx["newsletter_subscribe_url"] = "#"
        return ctx

    class Meta:
        template = "website/blocks/newsletter_signup_block.html"
        icon = "mail"
        label = _("Newsletter signup")
        help_text = _(
            "Sign-ups go to the newsletter page. If no newsletter page is "
            "published, the form does not work."
        )


# ---------------------------------------------------------------------------
# AlertBlock
# ---------------------------------------------------------------------------


class AlertBlock(StructBlock):
    """
    Notification or alert banner for important announcements.
    """

    message = RichTextBlock(
        required=True,
        label=_("Message"),
    )
    alert_type = ChoiceBlock(
        choices=[
            ("info", _("Info")),
            ("success", _("Success")),
            ("warning", _("Warning")),
            ("danger", _("Danger")),
        ],
        default="info",
        label=_("Alert type"),
    )
    dismissible = BooleanBlock(
        default=True,
        required=False,
        label=_("Can be closed"),
        help_text=_(
            "Adds a close button. The alert comes back when the visitor "
            "reloads the page."
        ),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        help_text=_("Short line under the name, for example Official sponsor."),
    )
    logo = ImageChooserBlock(
        required=False,
        label=_("Logo"),
        help_text=_(
            "Cropped to a 160 x 160 pixel square, "
            "so leave space around the logo."
        ),
    )
    url = URLBlock(
        required=False,
        label=_("Website"),
        help_text=_("The partner name links here and opens in a new tab."),
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
        label=_("Section title"),
        help_text=_("For example Our partners."),
    )
    subtitle = CharBlock(
        max_length=255,
        required=False,
        label=_("Subtitle"),
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
        label=_("Columns"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        CharBlock(max_length=500, label=_("Cell")),
        min_num=1,
        label=_("Cells"),
        help_text=_("One cell per column, in the same order as the column headers."),
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
        label=_("Title"),
        help_text=_("Shown as a heading above the table."),
    )
    headers = ListBlock(
        CharBlock(max_length=255, label=_("Column header")),
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
        label=_("Striped rows"),
        help_text=_(
            "Alternates the row background colour "
            "to make long tables easier to read."
        ),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Testimonial"),
    )
    name = CharBlock(
        max_length=255,
        required=True,
        label=_("Name"),
    )
    role = CharBlock(
        max_length=255,
        required=False,
        label=_("Role"),
        help_text=_("For example Member since 2012."),
    )
    avatar = ImageChooserBlock(
        required=False,
        label=_("Photo"),
        help_text=_("Cropped to a small 80 x 80 pixel square."),
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
        label=_("Section title"),
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
        label=_("Layout"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/testimonials_block.html"
        icon = "openquote"
        label = _("Testimonials")


# ---------------------------------------------------------------------------
# FeaturedPagesBlock
# ---------------------------------------------------------------------------


class FeaturedPageBlock(StructBlock):
    """A single featured page selection."""

    page = PageChooserBlock(required=True, label=_("Page"))
    override_title = CharBlock(
        max_length=255,
        required=False,
        label=_("Custom title"),
        help_text=_("If empty, the title of the chosen page is used."),
    )
    override_image = ImageChooserBlock(
        required=False,
        label=_("Image"),
        help_text=_("Cropped to 400 x 250 pixels. If empty, the card has no image."),
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
        label=_("Section title"),
    )
    pages = ListBlock(
        FeaturedPageBlock(),
        min_num=1,
        max_num=12,
        label=_("Pages"),
        help_text=_("You can add up to 12 pages."),
    )
    columns = ChoiceBlock(
        choices=[
            ("2", _("2 columns")),
            ("3", _("3 columns")),
            ("4", _("4 columns")),
        ],
        default="3",
        label=_("Columns"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Question"),
    )
    answer = RichTextBlock(
        required=True,
        label=_("Answer"),
        help_text=_("Hidden until the visitor clicks the question."),
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
        label=_("Section title"),
    )
    items = ListBlock(
        FAQItemBlock(),
        min_num=1,
        label=_("Questions"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Plan name"),
    )
    price = CharBlock(
        max_length=50,
        required=True,
        label=_("Price"),
        help_text=_("Shown exactly as written, for example €50/year."),
    )
    description = TextBlock(
        required=False,
        label=_("Description"),
    )
    features = ListBlock(
        CharBlock(max_length=255, label=_("Feature")),
        label=_("Features"),
        help_text=_("Shown as a bulleted list, one item per feature."),
    )
    cta_text = CharBlock(
        max_length=120,
        default=_("Choose plan"),
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
        help_text=_("Used only when no page is selected."),
    )
    highlighted = BooleanBlock(
        default=False,
        required=False,
        label=_("Recommended plan"),
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
        label=_("Section title"),
    )
    plans = ListBlock(
        PricingPlanBlock(),
        min_num=1,
        max_num=4,
        label=_("Plans"),
        help_text=_("You can add up to 4 plans."),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Number"),
        help_text=_("Whole number without dots or spaces, for example 1500."),
    )
    suffix = CharBlock(
        max_length=20,
        required=False,
        label=_("Suffix"),
        help_text=_("Text right after the number, for example + or %."),
    )
    label = CharBlock(
        max_length=100,
        required=True,
        label=_("Label"),
        help_text=_("Text shown with the number, for example Members."),
    )
    icon = CharBlock(
        max_length=50,
        required=False,
        label=_("Icon"),
        help_text=_(
            "Font Awesome class, for example fa-solid fa-users. "
            "If empty, no icon is shown."
        ),
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
        label=_("Section title"),
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
        label=_("Background"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

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
        label=_("Section title"),
    )
    platform = ChoiceBlock(
        choices=[
            ("instagram", _("Instagram")),
            ("facebook", _("Facebook")),
            ("twitter", _("X / Twitter")),
            ("youtube", _("YouTube")),
        ],
        default="instagram",
        label=_("Platform"),
    )
    embed_url = URLBlock(
        required=True,
        label=_("Profile or post link"),
        help_text=_("Full address, for example https://www.instagram.com/yourclub/."),
    )
    max_posts = IntegerBlock(
        default=6,
        min_value=1,
        max_value=12,
        label=_("Maximum posts"),
    )
    settings = BlockSettings(required=False, label=_("Advanced settings"))

    class Meta:
        template = "website/blocks/social_feed_block.html"
        icon = "site"
        label = _("Social feed")

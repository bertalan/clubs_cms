"""
Wagtail Snippet models for the Club CMS website.

All snippet models are registered with @register_snippet and managed
through the Wagtail admin Snippets menu.

Template access: snippets assigned via SiteSettings are available as
    {{ settings.website.SiteSettings.navbar }}
    {{ settings.website.SiteSettings.footer }}
    {{ settings.website.SiteSettings.color_scheme }}

See 42-SNIPPETS.md for full documentation.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


# ---------------------------------------------------------------------------
# 1. ColorScheme
# ---------------------------------------------------------------------------


@register_snippet
class ColorScheme(models.Model):
    """
    Reusable colour palette that can be assigned to a site via SiteSettings.

    Editors create named schemes; the active one is injected as CSS custom
    properties through the ``get_css_variables()`` helper.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    primary = models.CharField(
        max_length=7, default="#0F172A", verbose_name=_("Primary colour"),
        help_text=_("Main brand colour (hex)."),
    )
    secondary = models.CharField(
        max_length=7, default="#F59E0B", verbose_name=_("Secondary colour"),
        help_text=_("Secondary/accent brand colour (hex)."),
    )
    accent = models.CharField(
        max_length=7, default="#8B5CF6", verbose_name=_("Accent colour"),
        help_text=_("Accent highlight colour (hex)."),
    )
    surface = models.CharField(
        max_length=7, default="#F8FAFC", verbose_name=_("Surface colour"),
        help_text=_("Card/panel background colour (hex)."),
    )
    surface_alt = models.CharField(
        max_length=7, default="#FFFFFF", verbose_name=_("Surface alt colour"),
        help_text=_("Alternate surface colour (hex)."),
    )
    text_primary = models.CharField(
        max_length=7, default="#111111", verbose_name=_("Text primary"),
        help_text=_("Main body text colour (hex)."),
    )
    text_muted = models.CharField(
        max_length=7, default="#666666", verbose_name=_("Text muted"),
        help_text=_("Secondary/lighter text colour (hex)."),
    )
    is_dark_mode = models.BooleanField(
        default=False, verbose_name=_("Dark mode"),
        help_text=_("Enable if this is a dark colour scheme."),
    )

    panels = [
        FieldPanel("name"),
        MultiFieldPanel(
            [
                FieldPanel("primary"),
                FieldPanel("secondary"),
                FieldPanel("accent"),
            ],
            heading=_("Brand colours"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("surface"),
                FieldPanel("surface_alt"),
            ],
            heading=_("Surface colours"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("text_primary"),
                FieldPanel("text_muted"),
            ],
            heading=_("Text colours"),
        ),
        FieldPanel("is_dark_mode"),
    ]

    class Meta:
        verbose_name = _("colour scheme")
        verbose_name_plural = _("colour schemes")

    def __str__(self) -> str:
        return self.name

    def get_css_variables(self) -> dict[str, str]:
        """Return a mapping of CSS custom-property names to hex values."""
        return {
            "--color-primary": self.primary,
            "--color-secondary": self.secondary,
            "--color-accent": self.accent,
            "--color-surface": self.surface,
            "--color-surface-alt": self.surface_alt,
            "--color-text-primary": self.text_primary,
            "--color-text-muted": self.text_muted,
        }


# ---------------------------------------------------------------------------
# 2. Navbar  +  NavbarItem (inline child)
# ---------------------------------------------------------------------------


@register_snippet
class Navbar(ClusterableModel):
    """
    Main navigation menu. Editors may create several navbars and assign one
    to the site through SiteSettings.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )
    show_search = models.BooleanField(
        default=True, verbose_name=_("Show search"),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("logo"),
        FieldPanel("show_search"),
        InlinePanel("items", label=_("Menu items")),
    ]

    class Meta:
        verbose_name = _("navbar")
        verbose_name_plural = _("navbars")

    def __str__(self) -> str:
        return self.name

    def top_level_items(self):
        """Return only items without a parent (top-level navigation)."""
        return self.items.filter(parent__isnull=True)


class NavbarItem(Orderable):
    """A single link inside a Navbar, with optional one-level nesting."""

    navbar = ParentalKey(
        Navbar, on_delete=models.CASCADE, related_name="items",
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("Parent item"),
        help_text=_("Leave empty for top-level items. Select a parent for dropdown sub-items."),
    )
    label = models.CharField(max_length=100, verbose_name=_("Label"))
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Link page"),
    )
    link_url = models.URLField(
        blank=True, verbose_name=_("External URL"),
        help_text=_("Used only when no page is selected."),
    )
    open_new_tab = models.BooleanField(
        default=False, verbose_name=_("Open in new tab"),
    )
    is_cta = models.BooleanField(
        default=False, verbose_name=_("Is CTA"),
        help_text=_("Render as a highlighted call-to-action button."),
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("parent"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
        FieldPanel("open_new_tab"),
        FieldPanel("is_cta"),
    ]

    def __str__(self) -> str:
        return self.label


# ---------------------------------------------------------------------------
# 3. Footer  +  FooterMenuItem  +  FooterSocialLink (inline children)
# ---------------------------------------------------------------------------

SOCIAL_PLATFORM_CHOICES = [
    ("facebook", _("Facebook")),
    ("instagram", _("Instagram")),
    ("twitter", _("Twitter / X")),
    ("youtube", _("YouTube")),
    ("linkedin", _("LinkedIn")),
    ("tiktok", _("TikTok")),
]


@register_snippet
class Footer(ClusterableModel):
    """
    Site footer content. Multiple footers may be created; the active one is
    selected through SiteSettings.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    description = RichTextField(
        blank=True, verbose_name=_("Description"),
        help_text=_("Short 'about' text displayed in the footer."),
    )
    copyright_text = models.CharField(
        max_length=255, blank=True, verbose_name=_("Copyright text"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Address"))

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("copyright_text"),
        MultiFieldPanel(
            [
                FieldPanel("phone"),
                FieldPanel("email"),
                FieldPanel("address"),
            ],
            heading=_("Contact details"),
        ),
        InlinePanel("menu_items", label=_("Menu items")),
        InlinePanel("social_links", label=_("Social links")),
    ]

    class Meta:
        verbose_name = _("footer")
        verbose_name_plural = _("footers")

    def __str__(self) -> str:
        return self.name


class FooterMenuItem(Orderable):
    """A single link inside a Footer menu section."""

    footer = ParentalKey(
        Footer, on_delete=models.CASCADE, related_name="menu_items",
    )
    label = models.CharField(max_length=100, verbose_name=_("Label"))
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Link page"),
    )
    link_url = models.URLField(
        blank=True, verbose_name=_("External URL"),
        help_text=_("Used only when no page is selected."),
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
    ]

    def __str__(self) -> str:
        return self.label


class FooterSocialLink(Orderable):
    """A social-media link inside a Footer."""

    footer = ParentalKey(
        Footer, on_delete=models.CASCADE, related_name="social_links",
    )
    platform = models.CharField(
        max_length=20,
        choices=SOCIAL_PLATFORM_CHOICES,
        verbose_name=_("Platform"),
    )
    url = models.URLField(verbose_name=_("URL"))

    panels = [
        FieldPanel("platform"),
        FieldPanel("url"),
    ]

    def __str__(self) -> str:
        return f"{self.get_platform_display()} ({self.url})"


# ---------------------------------------------------------------------------
# 4. FAQ
# ---------------------------------------------------------------------------


@register_snippet
class FAQ(models.Model):
    """Frequently-asked-question item for accordion/listing display."""

    question = models.CharField(max_length=255, verbose_name=_("Question"))
    answer = RichTextField(verbose_name=_("Answer"))
    category = models.CharField(
        max_length=100, blank=True, verbose_name=_("Category"),
        help_text=_("Optional grouping label for the FAQ."),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first."),
    )

    panels = [
        FieldPanel("question"),
        FieldPanel("answer"),
        FieldPanel("category"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self) -> str:
        return self.question


# ---------------------------------------------------------------------------
# 5. Testimonial
# ---------------------------------------------------------------------------


@register_snippet
class Testimonial(models.Model):
    """Member/supporter testimonial quote."""

    quote = models.TextField(verbose_name=_("Quote"))
    author_name = models.CharField(max_length=100, verbose_name=_("Author name"))
    author_role = models.CharField(
        max_length=100, blank=True, verbose_name=_("Author role"),
    )
    author_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Author photo"),
    )
    date = models.DateField(
        null=True, blank=True, verbose_name=_("Date"),
    )
    featured = models.BooleanField(
        default=False, verbose_name=_("Featured"),
        help_text=_("Show this testimonial more prominently."),
    )

    panels = [
        FieldPanel("quote"),
        MultiFieldPanel(
            [
                FieldPanel("author_name"),
                FieldPanel("author_role"),
                FieldPanel("author_photo"),
            ],
            heading=_("Author"),
        ),
        FieldPanel("date"),
        FieldPanel("featured"),
    ]

    class Meta:
        verbose_name = _("testimonial")
        verbose_name_plural = _("testimonials")

    def __str__(self) -> str:
        return f"{self.author_name}: {self.quote[:50]}"


# ---------------------------------------------------------------------------
# 6. NewsCategory
# ---------------------------------------------------------------------------


@register_snippet
class NewsCategory(models.Model):
    """Category for NewsPage grouping/filtering."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    color = models.CharField(
        max_length=7, default="#000000", verbose_name=_("Colour"),
        help_text=_("Badge/label colour (hex)."),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("color"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("news category")
        verbose_name_plural = _("news categories")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 7. EventCategory
# ---------------------------------------------------------------------------

EVENT_ICON_CHOICES = [
    ("motorcycle", _("Motorcycle")),
    ("rally", _("Rally")),
    ("meeting", _("Meeting")),
    ("social", _("Social")),
    ("charity", _("Charity")),
    ("race", _("Race")),
]


@register_snippet
class EventCategory(models.Model):
    """Category for EventDetailPage grouping/filtering."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    icon = models.CharField(
        max_length=20,
        choices=EVENT_ICON_CHOICES,
        blank=True,
        verbose_name=_("Icon"),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("icon"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("event category")
        verbose_name_plural = _("event categories")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 8. PhotoTag
# ---------------------------------------------------------------------------


@register_snippet
class PhotoTag(models.Model):
    """Tag for gallery photos, used in batch uploads."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = _("photo tag")
        verbose_name_plural = _("photo tags")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 9. PartnerCategory
# ---------------------------------------------------------------------------


@register_snippet
class PartnerCategory(models.Model):
    """Category for Partner grouping (Main Sponsor, Technical, etc.)."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(
        max_length=50, blank=True, verbose_name=_("Icon"),
        help_text=_("Optional icon class name."),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first."),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("partner category")
        verbose_name_plural = _("partner categories")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 10. PressRelease
# ---------------------------------------------------------------------------


@register_snippet
class PressRelease(models.Model):
    """Press release managed by the press office."""

    title = models.CharField(max_length=255, verbose_name=_("Title"))
    date = models.DateField(verbose_name=_("Date"))
    body = RichTextField(verbose_name=_("Body"))
    attachment = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Attachment"),
        help_text=_("PDF or document attachment."),
    )
    is_archived = models.BooleanField(
        default=False, verbose_name=_("Archived"),
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("date"),
        FieldPanel("body"),
        FieldPanel("attachment"),
        FieldPanel("is_archived"),
    ]

    class Meta:
        ordering = ["-date"]
        verbose_name = _("press release")
        verbose_name_plural = _("press releases")

    def __str__(self) -> str:
        return f"{self.title} ({self.date})"


# ---------------------------------------------------------------------------
# 11. BrandAsset
# ---------------------------------------------------------------------------

BRAND_ASSET_CATEGORY_CHOICES = [
    ("logo", _("Logo")),
    ("font", _("Font")),
    ("photo", _("Photo")),
    ("template", _("Template")),
]


@register_snippet
class BrandAsset(models.Model):
    """Downloadable brand asset (logo, font, template, etc.)."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    category = models.CharField(
        max_length=20,
        choices=BRAND_ASSET_CATEGORY_CHOICES,
        verbose_name=_("Category"),
    )
    file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("File"),
    )
    preview = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Preview image"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first."),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("category"),
        FieldPanel("file"),
        FieldPanel("preview"),
        FieldPanel("description"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("brand asset")
        verbose_name_plural = _("brand assets")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 12. AidSkill
# ---------------------------------------------------------------------------

AID_SKILL_CATEGORY_CHOICES = [
    ("mechanics", _("Mechanics")),
    ("transport", _("Transport")),
    ("logistics", _("Logistics")),
    ("emergency", _("Emergency")),
    ("other", _("Other")),
]


@register_snippet
class AidSkill(models.Model):
    """Skill category for the mutual-aid system."""

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(
        max_length=50, blank=True, verbose_name=_("Icon"),
        help_text=_("Optional icon class name."),
    )
    category = models.CharField(
        max_length=20,
        choices=AID_SKILL_CATEGORY_CHOICES,
        default="other",
        verbose_name=_("Category"),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first."),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("icon"),
        FieldPanel("category"),
        FieldPanel("order"),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("aid skill")
        verbose_name_plural = _("aid skills")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# 13. Product
# ---------------------------------------------------------------------------


@register_snippet
class Product(models.Model):
    """
    Purchasable product / membership tier.

    The ``grants_*`` flags determine which member privileges are unlocked
    when a member purchases this product.
    """

    name = models.CharField(max_length=200, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_("Price"),
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active"),
        help_text=_("Inactive products are hidden from the storefront."),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first."),
    )

    # Privilege flags
    grants_vote = models.BooleanField(
        default=False, verbose_name=_("Grants voting rights"),
    )
    grants_upload = models.BooleanField(
        default=False, verbose_name=_("Grants gallery upload"),
    )
    grants_events = models.BooleanField(
        default=False, verbose_name=_("Grants event access"),
    )
    grants_discount = models.BooleanField(
        default=False, verbose_name=_("Grants discount"),
    )
    discount_percent = models.IntegerField(
        default=0, verbose_name=_("Discount percent"),
        help_text=_("Percentage discount on events when grants_discount is on."),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("slug"),
                FieldPanel("description"),
                FieldPanel("price"),
                FieldPanel("is_active"),
                FieldPanel("order"),
            ],
            heading=_("Product info"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("grants_vote"),
                FieldPanel("grants_upload"),
                FieldPanel("grants_events"),
                FieldPanel("grants_discount"),
                FieldPanel("discount_percent"),
            ],
            heading=_("Member privileges"),
        ),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self) -> str:
        return self.name

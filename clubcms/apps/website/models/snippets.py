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
from wagtail.models import Orderable, TranslatableMixin, Locale
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

    name = models.CharField(
        max_length=100, verbose_name=_("Name"),
    )
    primary = models.CharField(
        max_length=7, default="#0F172A", verbose_name=_("Primary colour"),
    )
    secondary = models.CharField(
        max_length=7, default="#F59E0B", verbose_name=_("Secondary colour"),
    )
    accent = models.CharField(
        max_length=7, default="#8B5CF6", verbose_name=_("Accent colour"),
    )
    surface = models.CharField(
        max_length=7, default="#F8FAFC", verbose_name=_("Surface colour"),
    )
    surface_alt = models.CharField(
        max_length=7, default="#FFFFFF", verbose_name=_("Surface alt colour"),
    )
    text_primary = models.CharField(
        max_length=7, default="#111111", verbose_name=_("Text primary"),
    )
    text_muted = models.CharField(
        max_length=7, default="#666666", verbose_name=_("Text muted"),
    )
    is_dark_mode = models.BooleanField(
        default=False, verbose_name=_("Dark mode"),
        help_text=_(
            "Turn on for palettes with a dark background. The public site "
            "then uses the theme's dark mode styles."
        ),
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
            help_text=_(
                "Enter every colour as a hex code, for example #0F172A. "
                "They replace the theme colours on the public site."
            ),
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

    name = models.CharField(
        max_length=100, verbose_name=_("Name"),
        help_text=_(
            "Seen only in the admin. The navbar used on the site is chosen "
            "in Settings > Site settings > Navigation."
        ),
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
        help_text=_("If set, replaces the site logo in the navigation bar."),
    )
    show_search = models.BooleanField(
        default=True, verbose_name=_("Show search"),
        help_text=_("Adds a search button to the navigation bar."),
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
        verbose_name=_("Navbar"),
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
        verbose_name=_("Parent item"),
        help_text=_(
            "Leave empty for a top-level item. Choose another item to show "
            "this one in its dropdown menu."
        ),
    )
    label = models.CharField(
        max_length=100, verbose_name=_("Label"),
        help_text=_(
            "Used only when no page is chosen: links to a page always show "
            "the page title."
        ),
    )
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
        help_text=_(
            "Full address starting with https://. Used only when no page is chosen."
        ),
    )
    open_new_tab = models.BooleanField(
        default=False, verbose_name=_("Open in new tab"),
    )
    is_cta = models.BooleanField(
        default=False, verbose_name=_("Highlight as button"),
        help_text=_(
            "Top-level items only: the link appears as a highlighted button, "
            "for example for Join us."
        ),
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

    name = models.CharField(
        max_length=100, verbose_name=_("Name"),
        help_text=_(
            "Seen only in the admin. The footer used on the site is chosen "
            "in Settings > Site settings > Navigation."
        ),
    )
    description = RichTextField(
        blank=True, verbose_name=_("Description"),
        help_text=_(
            "Short text under the site name in the footer. If empty, the "
            "site tagline is shown."
        ),
    )
    copyright_text = models.CharField(
        max_length=255, blank=True, verbose_name=_("Copyright text"),
        help_text=_(
            "Shown in the bottom bar. If empty, the footer shows the current "
            "year, the site name and All rights reserved."
        ),
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
            help_text=_("Leave empty to show the contact details from Site settings."),
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
        verbose_name=_("Footer"),
    )
    label = models.CharField(
        max_length=100, verbose_name=_("Label"),
        help_text=_(
            "Used only when no page is chosen: links to a page always show "
            "the page title."
        ),
    )
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
        help_text=_(
            "Full address starting with https://. Used only when no page is "
            "chosen, and it opens in a new tab."
        ),
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
        verbose_name=_("Footer"),
    )
    platform = models.CharField(
        max_length=20,
        choices=SOCIAL_PLATFORM_CHOICES,
        verbose_name=_("Platform"),
    )
    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_(
            "Full profile address, for example https://www.instagram.com/yourclub."
        ),
    )

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
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))

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
    date = models.DateField(null=True, blank=True, verbose_name=_("Date"))
    featured = models.BooleanField(default=False, verbose_name=_("Featured"))

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
    slug = models.SlugField(
        unique=True, verbose_name=_("Slug"),
        help_text=_(
            "Appears in the address of the filtered list, for example "
            "?category=club-news. Use lowercase letters, numbers and hyphens."
        ),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    color = models.CharField(
        max_length=7, default="#000000", verbose_name=_("Colour"),
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
    slug = models.SlugField(
        unique=True, verbose_name=_("Slug"),
        help_text=_(
            "Appears in the address of the filtered list, for example "
            "?category=rally. Use lowercase letters, numbers and hyphens."
        ),
    )
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

    name = models.CharField(
        max_length=100, verbose_name=_("Name"),
        help_text=_("Members choose from these tags when they upload photos."),
    )
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
    slug = models.SlugField(
        unique=True, verbose_name=_("Slug"),
        help_text=_(
            "Appears in the address of the filtered list, for example "
            "?category=sponsors. Use lowercase letters, numbers and hyphens."
        ),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon"))
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_(
            "Sets the order of the category filters on the partner list. Lower numbers "
            "come first."
        ),
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
    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_(
            "The press page lists releases from newest to oldest by this date."
        ),
    )
    body = RichTextField(verbose_name=_("Body"))
    attachment = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Attachment"),
        help_text=_(
            "Offered as a download button under the release, for example a PDF."
        ),
    )
    is_archived = models.BooleanField(
        default=False, verbose_name=_("Archived"),
        help_text=_("If on, the release no longer appears on the press page."),
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
        help_text=_("The file visitors download from the press page."),
    )
    preview = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Preview image"),
        help_text=_("Thumbnail shown on the asset card on the press page."),
    )
    description = models.TextField(
        blank=True, verbose_name=_("Description"),
        help_text=_(
            "Shown on the asset card on the press page, cut to the first 20 words."
        ),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first on the press page."),
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
    icon = models.CharField(max_length=50, blank=True, verbose_name=_("Icon"))
    category = models.CharField(
        max_length=20,
        choices=AID_SKILL_CATEGORY_CHOICES,
        default="other",
        verbose_name=_("Category"),
    )
    order = models.IntegerField(default=0, verbose_name=_("Order"))

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
class Product(TranslatableMixin, models.Model):
    """
    Purchasable product / membership tier.

    The ``grants_*`` flags determine which member privileges are unlocked
    when a member purchases this product.
    
    Uses TranslatableMixin for multilingual support:
    - name, description: translated per locale
    - all other fields: synchronized across locales
    """

    name = models.CharField(
        max_length=200, verbose_name=_("Name"),
        help_text=_("Shown on the membership plans page and in the member area."),
    )
    slug = models.SlugField(verbose_name=_("Slug"))  # unique per locale via Meta
    description = models.TextField(
        blank=True, verbose_name=_("Description"),
        help_text=_("Shown under the price on the membership plans page."),
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_("Price"),
        help_text=_("In euros, with a dot for decimals, for example 50.00."),
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Active"),
        help_text=_(
            "If off, the product disappears from the membership plans page "
            "and members can no longer request it."
        ),
    )
    order = models.IntegerField(
        default=0, verbose_name=_("Order"),
        help_text=_("Lower numbers appear first on the membership plans page."),
    )

    # Privilege flags
    grants_vote = models.BooleanField(
        default=False, verbose_name=_("Grants voting rights"),
        help_text=_("Listed as a benefit on the membership plans page."),
    )
    grants_upload = models.BooleanField(
        default=False, verbose_name=_("Grants gallery upload"),
        help_text=_("Members with this product can upload photos to the gallery."),
    )
    grants_events = models.BooleanField(
        default=False, verbose_name=_("Grants event access"),
        help_text=_(
            "Members with this product can register for events. Members whose "
            "products all lack it cannot register."
        ),
    )
    grants_discount = models.BooleanField(
        default=False, verbose_name=_("Grants discount"),
        help_text=_("If on, the discount percent below is applied to event fees."),
    )
    discount_percent = models.IntegerField(
        default=0, verbose_name=_("Discount percent"),
        help_text=_(
            "Example: 10 means 10 percent off event fees. If the event offers a higher "
            "member discount, or the member has a better product, that one is used."
        ),
    )

    # Validity configuration
    validity_days = models.IntegerField(
        default=365,
        verbose_name=_("Validity days"),
        help_text=_(
            "Days added to the membership expiry when staff approve a request "
            "for this product, counted from the current expiry if still valid, "
            "otherwise from today."
        ),
    )
    available_from = models.DateField(
        null=True, blank=True,
        verbose_name=_("Available from"),
        help_text=_(
            "Before this date, staff see a warning when approving a request "
            "for this product. Leave empty for no limit."
        ),
    )
    available_until = models.DateField(
        null=True, blank=True,
        verbose_name=_("Available until"),
        help_text=_(
            "After this date, staff see a warning when approving a request "
            "for this product. Leave empty for no limit."
        ),
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
        MultiFieldPanel(
            [
                FieldPanel("validity_days"),
                FieldPanel("available_from"),
                FieldPanel("available_until"),
            ],
            heading=_("Validity settings"),
        ),
    ]

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("product")
        verbose_name_plural = _("products")
        unique_together = [("translation_key", "locale"), ("locale", "slug")]

    def __str__(self) -> str:
        return self.name

    @property
    def is_purchasable(self):
        """Check if product can be purchased (active and within date range)."""
        from django.utils import timezone
        today = timezone.localdate()
        if not self.is_active:
            return False
        if self.available_from and self.available_from > today:
            return False
        if self.available_until and self.available_until < today:
            return False
        return True

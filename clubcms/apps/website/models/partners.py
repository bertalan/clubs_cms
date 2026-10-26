"""
Wagtail Page models for Partner pages.

PartnerIndexPage: listing page for all partners, filterable by category.
PartnerPage: individual partner with contact, social, ownership, display fields.
"""

from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail.search import index

from apps.website.blocks import BODY_BLOCKS


# ═══════════════════════════════════════════════════════════════════════════
# PartnerIndexPage
# ═══════════════════════════════════════════════════════════════════════════


class PartnerIndexPage(Page):
    """
    Listing page for all partner organisations.  Supports category filtering
    and pagination of child PartnerPages.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Shown at the top of the page, above the list of partners."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Extra content shown below the list of partners."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = ["website.PartnerPage"]
    template = "website/pages/partner_index_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Partner index page")
        verbose_name_plural = _("Partner index pages")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        partners = (
            PartnerPage.objects.live()
            .descendant_of(self)
            .order_by("display_order", "title")
        )

        # Category filtering
        category_slug = request.GET.get("category")
        if category_slug:
            partners = partners.filter(category__slug=category_slug)
            context["current_category"] = category_slug

        # Pagination
        paginator = Paginator(partners, 12)
        page_number = request.GET.get("page")
        try:
            partner_items = paginator.page(page_number)
        except PageNotAnInteger:
            partner_items = paginator.page(1)
        except EmptyPage:
            partner_items = paginator.page(paginator.num_pages)

        context["partner_items"] = partner_items
        context["paginator"] = paginator

        # Categories for filter navigation
        from apps.website.models.snippets import PartnerCategory

        context["categories"] = PartnerCategory.objects.all()

        return context


# ═══════════════════════════════════════════════════════════════════════════
# PartnerPage
# ═══════════════════════════════════════════════════════════════════════════


class PartnerPage(Page):
    """
    Individual partner organisation page with detailed contact, social,
    ownership, and display information.
    """

    # --- Content fields ---
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
        help_text=_(
            "Shown on the partner card in the list, on the home page and on the partner"
            " page."
        ),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
        help_text=_("Wide image between the title and the content, cropped to 16:9."),
    )
    category = models.ForeignKey(
        "website.PartnerCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="partner_pages",
        verbose_name=_("Category"),
        help_text=_(
            "Used to filter the partner list and shown as a ribbon on the partner card."
        ),
    )
    intro = models.TextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_(
            "Shown under the title and on the partner card in the list, cut to 20 "
            "words."
        ),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
    )

    # --- Contact fields ---
    website = models.URLField(
        blank=True,
        verbose_name=_("Website"),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email"),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Phone"),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Address"),
    )
    contact_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
        help_text=_("Shown with the address and on the partner card in the list."),
    )
    country = models.CharField(
        max_length=2,
        default="IT",
        verbose_name=_("Country"),
        help_text=_("Two-letter country code, for example IT or DE."),
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
    )

    # --- Social fields ---
    facebook_url = models.URLField(
        blank=True,
        verbose_name=_("Facebook URL"),
    )
    instagram_url = models.URLField(
        blank=True,
        verbose_name=_("Instagram URL"),
    )
    linkedin_url = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn URL"),
    )
    youtube_url = models.URLField(
        blank=True,
        verbose_name=_("YouTube URL"),
    )
    twitter_url = models.URLField(
        blank=True,
        verbose_name=_("Twitter / X URL"),
    )

    # --- Ownership fields ---
    partner_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_partner_pages",
        verbose_name=_("Partner owner"),
    )
    owner_email = models.EmailField(
        blank=True,
        verbose_name=_("Owner email"),
    )

    # --- Display fields ---
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_(
            "Adds a Featured badge on the partner page and a star on the "
            "partner card. Used on the home page when no partner has Show on "
            "homepage turned on."
        ),
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_(
            "Lower numbers appear first in the partner list and on the home page."
        ),
    )
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name=_("Show on homepage"),
        help_text=_(
            "Shows the partner in the partner section of the home page, up to 6 "
            "partners."
        ),
    )
    partnership_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Partnership start"),
        help_text=_("Shown on the partner page as month and year."),
    )
    partnership_end = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Partnership end"),
        help_text=_(
            "Shown on the partner page. Leave empty for an ongoing partnership."
        ),
    )

    # --- Wagtail config ---
    parent_page_types = ["website.PartnerIndexPage"]
    subpage_types = []
    template = "website/pages/partner_page.html"

    # --- Panels ---
    content_panels = Page.content_panels + [
        FieldPanel("logo"),
        FieldPanel("cover_image"),
        FieldPanel("category"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    contact_panels = [
        MultiFieldPanel(
            [
                FieldPanel("website"),
                FieldPanel("email"),
                FieldPanel("phone"),
                FieldPanel("address"),
                FieldPanel("contact_city"),
                FieldPanel("country"),
                FieldRowPanel(
                    [
                        FieldPanel("latitude"),
                        FieldPanel("longitude"),
                    ],
                    help_text=_(
                        "Fill in both to show the partner on a map, for "
                        "example 45.6950 and 9.6700."
                    ),
                ),
            ],
            heading=_("Contact information"),
        ),
    ]

    social_panels = [
        MultiFieldPanel(
            [
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("youtube_url"),
                FieldPanel("twitter_url"),
            ],
            heading=_("Social media"),
            help_text=_(
                "Full addresses starting with https://. Each one becomes an "
                "icon on the partner page."
            ),
        ),
    ]

    ownership_panels = [
        MultiFieldPanel(
            [
                FieldPanel("partner_owner"),
                FieldPanel("owner_email"),
            ],
            heading=_("Ownership"),
        ),
    ]

    display_panels = [
        MultiFieldPanel(
            [
                FieldPanel("is_featured"),
                FieldPanel("display_order"),
                FieldPanel("show_on_homepage"),
                FieldRowPanel(
                    [
                        FieldPanel("partnership_start"),
                        FieldPanel("partnership_end"),
                    ]
                ),
            ],
            heading=_("Display settings"),
        ),
    ]

    promote_panels = Page.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(contact_panels, heading=_("Contact")),
            ObjectList(social_panels, heading=_("Social")),
            ObjectList(ownership_panels, heading=_("Ownership")),
            ObjectList(display_panels, heading=_("Display")),
            ObjectList(promote_panels, heading=_("Promote")),
            ObjectList(Page.settings_panels, heading=_("Settings")),
        ]
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.SearchField("contact_city"),
        index.RelatedFields("category", [index.SearchField("name")]),
    ]

    class Meta:
        verbose_name = _("Partner page")
        verbose_name_plural = _("Partner pages")
        ordering = ["display_order", "title"]

    @property
    def is_active(self) -> bool:
        """Return True if the partnership is currently active."""
        if self.partnership_end is None:
            return True
        return self.partnership_end >= timezone.now().date()

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
        help_text=_("Testo introduttivo sopra l'elenco dei partner."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto aggiuntivo sotto l'introduzione."),
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
        help_text=_("Logo del partner, mostrato nei listing e nella pagina."),
    )
    category = models.ForeignKey(
        "website.PartnerCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="partner_pages",
        verbose_name=_("Category"),
        help_text=_("Categoria del partner (es. Sponsor, Tecnico)."),
    )
    intro = models.TextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Short description shown in listings."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Descrizione completa del partner."),
    )

    # --- Contact fields ---
    website = models.URLField(
        blank=True,
        verbose_name=_("Website"),
        help_text=_("Sito web del partner."),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email"),
        help_text=_("Email di contatto del partner."),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Phone"),
        help_text=_("Numero di telefono del partner."),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Address"),
        help_text=_("Indirizzo fisico del partner."),
    )
    contact_city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
        help_text=_("Città di riferimento del partner."),
    )
    country = models.CharField(
        max_length=2,
        default="IT",
        verbose_name=_("Country"),
        help_text=_("ISO 3166-1 alpha-2 country code."),
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
        help_text=_("Latitudine per la mappa (es. 45.6950)."),
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
        help_text=_("Longitudine per la mappa (es. 9.6700)."),
    )

    # --- Social fields ---
    facebook_url = models.URLField(
        blank=True,
        verbose_name=_("Facebook URL"),
        help_text=_("URL pagina Facebook del partner."),
    )
    instagram_url = models.URLField(
        blank=True,
        verbose_name=_("Instagram URL"),
        help_text=_("URL profilo Instagram del partner."),
    )
    linkedin_url = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn URL"),
        help_text=_("URL pagina LinkedIn del partner."),
    )
    youtube_url = models.URLField(
        blank=True,
        verbose_name=_("YouTube URL"),
        help_text=_("URL canale YouTube del partner."),
    )
    twitter_url = models.URLField(
        blank=True,
        verbose_name=_("Twitter / X URL"),
        help_text=_("URL profilo Twitter/X del partner."),
    )

    # --- Ownership fields ---
    partner_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="owned_partner_pages",
        verbose_name=_("Partner owner"),
        help_text=_("User account that manages this partner page."),
    )
    owner_email = models.EmailField(
        blank=True,
        verbose_name=_("Owner email"),
        help_text=_("Contact email for the partner owner."),
    )

    # --- Display fields ---
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Show this partner prominently."),
    )
    display_order = models.IntegerField(
        default=0,
        verbose_name=_("Display order"),
        help_text=_("Lower numbers appear first."),
    )
    show_on_homepage = models.BooleanField(
        default=False,
        verbose_name=_("Show on homepage"),
        help_text=_("Mostra il logo del partner nella homepage."),
    )
    partnership_start = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Partnership start"),
        help_text=_("Data di inizio della partnership."),
    )
    partnership_end = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Partnership end"),
        help_text=_("Leave blank for ongoing partnerships."),
    )

    # --- Wagtail config ---
    parent_page_types = ["website.PartnerIndexPage"]
    subpage_types = []
    template = "website/pages/partner_page.html"

    # --- Panels ---
    content_panels = Page.content_panels + [
        FieldPanel("logo"),
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
                    ]
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

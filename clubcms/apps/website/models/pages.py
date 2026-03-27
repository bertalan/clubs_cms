"""
Wagtail Page models for the Club CMS website.

All page models follow the hierarchy defined in 10-PAGE-MODELS.md.
Template convention: website/pages/{model_name_snake_case}.html
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase

from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Collection, Page
from wagtail.search import index
from wagtail.contrib.routable_page.models import RoutablePageMixin, route

# ---------------------------------------------------------------------------
# StreamField block imports from apps.website.blocks (created by AG-3)
# ---------------------------------------------------------------------------
from apps.website.blocks import BODY_BLOCKS, EVENT_BLOCKS, HOME_BLOCKS, NEWS_BLOCKS


# ---------------------------------------------------------------------------
# Tagged-item through models (required by django-taggit + modelcluster)
# ---------------------------------------------------------------------------

class NewsPageTag(TaggedItemBase):
    """Through model for NewsPage tags."""

    content_object = ParentalKey(
        "website.NewsPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class EventPageTag(TaggedItemBase):
    """Through model for EventDetailPage tags."""

    content_object = ParentalKey(
        "website.EventDetailPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. HomePage
# ═══════════════════════════════════════════════════════════════════════════

class HomePage(Page):
    """
    Main landing page.  Only one instance is allowed per site.
    Hero section + StreamField body + optional featured event.
    """

    # --- Hero section ---
    hero_badge = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Hero badge"),
        help_text=_("Pre-title text displayed above hero title, e.g. 'Since 1985'."),
    )
    hero_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Hero title"),
        help_text=_("Main headline displayed in the hero section."),
    )
    hero_subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Hero subtitle"),
        help_text=_("Testo secondario mostrato sotto il titolo hero."),
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Hero background image"),
        help_text=_("Immagine di sfondo della hero section."),
    )
    primary_cta_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Primary CTA text"),
        help_text=_("Testo del pulsante principale (es. 'Scopri di più')."),
    )
    primary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Primary CTA link"),
        help_text=_("Pagina interna per il pulsante principale."),
    )
    primary_cta_url = models.URLField(
        blank=True,
        verbose_name=_("Primary CTA external URL"),
        help_text=_("Used only if no internal page is selected."),
    )
    secondary_cta_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Secondary CTA text"),
        help_text=_("Testo del pulsante secondario (es. 'Contattaci')."),
    )
    secondary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Secondary CTA link"),
        help_text=_("Pagina interna per il pulsante secondario."),
    )
    secondary_cta_url = models.URLField(
        blank=True,
        verbose_name=_("Secondary CTA external URL"),
        help_text=_("Used only if no internal page is selected."),
    )

    # --- StreamField body ---
    body = StreamField(
        HOME_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto principale della homepage sotto la hero section."),
    )

    # --- Featured content ---
    featured_event = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Featured event"),
        help_text=_("Select an EventDetailPage to highlight on the homepage."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    parent_page_types = ["wagtailcore.Page"]
    template = "website/pages/home_page.html"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_badge"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_image"),
            ],
            heading=_("Hero section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_cta_text"),
                FieldPanel("primary_cta_link"),
                FieldPanel("primary_cta_url"),
                FieldPanel("secondary_cta_text"),
                FieldPanel("secondary_cta_link"),
                FieldPanel("secondary_cta_url"),
            ],
            heading=_("Call-to-action buttons"),
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("featured_event"),
            ],
            heading=_("Featured content"),
        ),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("hero_title"),
        index.SearchField("hero_subtitle"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Home page")
        verbose_name_plural = _("Home pages")

    def __str__(self) -> str:
        return self.title

    def _split_intro_body_blocks(self):
        opening_block_types = {"rich_text", "stats", "cta"}
        promoted_blocks = {}
        promoted_indices = []
        promoted_raw_values = {}

        for index, block in enumerate(self.body):
            if block.block_type not in opening_block_types:
                break
            if block.block_type in promoted_blocks:
                break

            promoted_blocks[block.block_type] = block
            promoted_indices.append(index)
            promoted_raw_values[block.block_type] = self.body.raw_data[index].get("value", {})

            if len(promoted_blocks) == len(opening_block_types):
                break

        enabled = "rich_text" in promoted_blocks and (
            "stats" in promoted_blocks or "cta" in promoted_blocks
        )
        if not enabled:
            promoted_indices = []
            promoted_blocks = {}

        remaining_blocks = [
            block for index, block in enumerate(self.body) if index not in promoted_indices
        ]

        stats_items = []
        raw_stats_value = promoted_raw_values.get("stats") or {}
        for item in raw_stats_value.get("stats", []):
            if isinstance(item, dict):
                # ListBlock wraps items: {"type": "item", "value": {...}}
                inner = item.get("value", item) if "type" in item else item
                if isinstance(inner, dict):
                    stats_items.append(
                        {
                            "value": inner.get("value", ""),
                            "label": inner.get("label", ""),
                            "icon": inner.get("icon", ""),
                        }
                    )
                else:
                    stats_items.append({"value": inner, "label": "", "icon": ""})
        for item in raw_stats_value.get("items", []):
            if isinstance(item, dict):
                inner = item.get("value", item) if "type" in item else item
                if isinstance(inner, dict):
                    stats_items.append(
                        {
                            "value": inner.get("number", ""),
                            "label": inner.get("label", ""),
                            "icon": inner.get("icon", ""),
                        }
                    )
                else:
                    stats_items.append({"value": inner, "label": "", "icon": ""})

        return {
            "enabled": enabled,
            "rich_text": promoted_blocks.get("rich_text"),
            "stats": promoted_blocks.get("stats"),
            "cta": promoted_blocks.get("cta"),
            "stats_title": raw_stats_value.get("title", ""),
            "stats_items": [item for item in stats_items if item["value"] or item["label"]],
            "remaining": remaining_blocks,
        }

    @cached_property
    def home_intro_section(self):
        return self._split_intro_body_blocks()

    @cached_property
    def remaining_body_blocks(self):
        return self.home_intro_section["remaining"]


# ═══════════════════════════════════════════════════════════════════════════
# 2. AboutPage
# ═══════════════════════════════════════════════════════════════════════════

class AboutPage(Page):
    """
    Main 'About Us' page.  Allows BoardPage as only child type.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Displayed below the page title."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
        help_text=_("Immagine di copertina mostrata in alto nella pagina."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto principale della pagina Chi Siamo."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = ["website.BoardPage"]
    template = "website/pages/about_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("cover_image"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("About page")
        verbose_name_plural = _("About pages")


# ═══════════════════════════════════════════════════════════════════════════
# 3. BoardPage
# ═══════════════════════════════════════════════════════════════════════════

class BoardPage(Page):
    """
    Board of directors / team members page.
    Must be a child of AboutPage.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo per la pagina del direttivo."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Use team-member blocks here."),
    )

    # --- Wagtail config ---
    parent_page_types = ["website.AboutPage"]
    subpage_types = []
    template = "website/pages/board_page.html"

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
        verbose_name = _("Board page")
        verbose_name_plural = _("Board pages")


# ═══════════════════════════════════════════════════════════════════════════
# 4. NewsIndexPage
# ═══════════════════════════════════════════════════════════════════════════

class NewsIndexPage(Page):
    """
    Listing page for all news articles, with filtering and pagination.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo mostrato sopra l'elenco delle notizie."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Optional content displayed above the article listing."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = ["website.NewsPage"]
    template = "website/pages/news_index_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = _("News index page")
        verbose_name_plural = _("News index pages")

    # --- Context / pagination ---

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        all_news = (
            NewsPage.objects.live()
            .descendant_of(self)
            .order_by("-display_date", "-first_published_at")
        )

        # Filtering
        category_slug = request.GET.get("category")
        tag = request.GET.get("tag")

        if category_slug:
            all_news = all_news.filter(category__slug=category_slug)
        if tag:
            all_news = all_news.filter(tags__slug=tag)

        # Pagination
        paginator = Paginator(all_news, 12)
        page_number = request.GET.get("page")
        try:
            news_pages = paginator.page(page_number)
        except PageNotAnInteger:
            news_pages = paginator.page(1)
        except EmptyPage:
            news_pages = paginator.page(paginator.num_pages)

        # Provide categories for the filter bar
        from apps.website.models.snippets import NewsCategory
        context["news_pages"] = news_pages
        context["paginator"] = paginator
        context["categories"] = NewsCategory.objects.all()
        context["current_category"] = category_slug
        return context


# ═══════════════════════════════════════════════════════════════════════════
# 5. NewsPage
# ═══════════════════════════════════════════════════════════════════════════

class NewsPage(Page):
    """
    Individual news article / blog post.
    """

    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
        help_text=_("Immagine di copertina per l'articolo, usata anche nelle anteprime."),
    )
    intro = models.TextField(
        blank=True,
        verbose_name=_("Introduction / excerpt"),
        help_text=_("Short summary shown in listings."),
    )
    body = StreamField(
        NEWS_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto completo dell'articolo."),
    )
    display_date = models.DateField(
        default=timezone.now,
        verbose_name=_("Display date"),
        help_text=_("Publication date shown to readers."),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_articles",
        verbose_name=_("Author"),
        help_text=_("Autore dell'articolo, mostrato nella pagina e nei listing."),
    )

    # Tags and categories
    tags = ClusterTaggableManager(
        through="website.NewsPageTag",
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Tag per classificare e filtrare l'articolo."),
    )
    category = models.ForeignKey(
        "website.NewsCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_pages",
        verbose_name=_("Category"),
        help_text=_("Categoria principale dell'articolo."),
    )

    # --- Wagtail config ---
    parent_page_types = ["website.NewsIndexPage"]
    subpage_types = []
    template = "website/pages/news_page.html"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("display_date"),
                FieldPanel("author"),
            ],
            heading=_("Article metadata"),
        ),
        FieldPanel("cover_image"),
        FieldPanel("intro"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("tags"),
            ],
            heading=_("Categorisation"),
        ),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.RelatedFields("category", [index.SearchField("name")]),
        index.RelatedFields("author", [index.SearchField("get_full_name")]),
    ]

    class Meta:
        verbose_name = _("News page")
        verbose_name_plural = _("News pages")
        ordering = ["-display_date"]

    @cached_property
    def reading_time(self) -> int:
        """Estimated reading time in minutes based on body content."""
        word_count = len(self.intro.split()) if self.intro else 0
        for block in self.body:
            if hasattr(block.value, "source"):
                word_count += len(str(block.value.source).split())
            else:
                word_count += len(str(block.value).split())
        minutes = max(1, round(word_count / 200))
        return minutes


# ═══════════════════════════════════════════════════════════════════════════
# 6. EventsPage (Index)
# ═══════════════════════════════════════════════════════════════════════════

class EventsPage(Page):
    """
    Listing page for upcoming and past events with filtering and pagination.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo mostrato sopra l'elenco degli eventi."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Optional content above the event listing."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = ["website.EventDetailPage"]
    template = "website/pages/events_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = _("Events page")
        verbose_name_plural = _("Events pages")

    # --- Context / pagination ---

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        now = timezone.now()

        events_qs = (
            EventDetailPage.objects.live()
            .descendant_of(self)
        )

        # Determine which view: upcoming (default) or past
        show = request.GET.get("show", "upcoming")

        if show == "past":
            events_qs = events_qs.filter(start_date__lt=now).order_by("-start_date")
        else:
            events_qs = events_qs.filter(start_date__gte=now).order_by("start_date")

        # Text search
        search_query = request.GET.get("q", "").strip()
        if search_query:
            events_qs = events_qs.search(search_query)

        # Filtering
        category_slug = request.GET.get("category")
        tag = request.GET.get("tag")

        if category_slug:
            events_qs = events_qs.filter(category__slug=category_slug)
        if tag:
            events_qs = events_qs.filter(tags__slug=tag)

        # Pagination
        paginator = Paginator(events_qs, 12)
        page_number = request.GET.get("page")
        try:
            events = paginator.page(page_number)
        except PageNotAnInteger:
            events = paginator.page(1)
        except EmptyPage:
            events = paginator.page(paginator.num_pages)

        # Categories for filter UI
        from apps.website.models.snippets import EventCategory
        categories = EventCategory.objects.all()

        context["event_pages"] = events
        context["paginator"] = paginator
        context["show"] = show
        context["categories"] = categories
        context["current_category"] = category_slug
        context["search_query"] = search_query
        return context


# ═══════════════════════════════════════════════════════════════════════════
# 7. EventDetailPage
# ═══════════════════════════════════════════════════════════════════════════

class EventDetailPage(RoutablePageMixin, Page):
    """
    Individual event with details, location, registration, and pricing.

    Uses RoutablePageMixin so that sub-routes like ``register/`` are
    served by the same Wagtail page, keeping URLs human-friendly.
    """

    # --- Core Fields ---
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
        help_text=_("Immagine di copertina per l'evento, usata anche nei listing."),
    )
    intro = models.TextField(
        blank=True,
        verbose_name=_("Introduction / excerpt"),
        help_text=_("Short description shown in listings."),
    )
    body = StreamField(
        EVENT_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Descrizione completa dell'evento con blocchi multimediali."),
    )

    # --- Date/Time ---
    start_date = models.DateTimeField(
        verbose_name=_("Start date & time"),
        help_text=_("Data e ora di inizio dell'evento."),
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("End date & time"),
        help_text=_("Data e ora di fine. Lasciare vuoto per eventi di un giorno."),
    )

    # --- Location ---
    location_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Venue name"),
        help_text=_("Nome del luogo o struttura che ospita l'evento."),
    )
    location_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Address"),
        help_text=_("Indirizzo completo del luogo dell'evento."),
    )
    location_coordinates = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Coordinates"),
        help_text=_("Latitude,Longitude (e.g. '45.4642,9.1900')"),
    )
    latitude = models.FloatField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Latitude"),
        help_text=_("Auto-populated from coordinates."),
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_("Longitude"),
        help_text=_("Auto-populated from coordinates."),
    )

    # --- Registration ---
    registration_open = models.BooleanField(
        default=False,
        verbose_name=_("Registration open"),
        help_text=_("Attiva per accettare le iscrizioni all'evento."),
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration deadline"),
        help_text=_("Termine ultimo per le iscrizioni."),
    )
    max_attendees = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Max attendees"),
        help_text=_("0 = unlimited."),
    )

    # --- Pricing ---
    base_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_("Base fee"),
        help_text=_("Event participation cost in EUR.  0 = free."),
    )
    early_bird_discount = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Early-bird discount (%)"),
        help_text=_("Sconto percentuale per le iscrizioni anticipate."),
    )
    early_bird_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Early-bird deadline"),
        help_text=_("Termine per usufruire dello sconto early-bird."),
    )
    member_discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Member discount (%)"),
        help_text=_("Percentage discount for active members."),
    )

    # --- Guest & Passenger ---
    allow_guests = models.BooleanField(
        default=True,
        verbose_name=_("Allow guest registration"),
        help_text=_("If checked, non-logged-in users can register via the guest form."),
    )
    passenger_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_("Passenger fee"),
        help_text=_("Additional cost for a passenger/companion. 0 = same as base."),
    )
    passenger_member_discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Passenger member discount (%)"),
        help_text=_("Percentage discount on passenger fee for active members."),
    )
    passenger_included = models.BooleanField(
        default=False,
        verbose_name=_("Passenger included in base fee"),
        help_text=_("If checked, passenger rides for free with the main registrant."),
    )

    # --- Route / Logistics ---
    meeting_point = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Meeting point"),
        help_text=_("Where participants should gather before the event start."),
    )
    difficulty_level = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ("easy", _("Easy")),
            ("moderate", _("Moderate")),
            ("hard", _("Hard")),
            ("expert", _("Expert")),
        ],
        verbose_name=_("Difficulty level"),
        help_text=_("Livello di difficoltà del percorso."),
    )

    # --- Tags and categories ---
    tags = ClusterTaggableManager(
        through="website.EventPageTag",
        blank=True,
        verbose_name=_("Tags"),
    )
    category = models.ForeignKey(
        "website.EventCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="events",
        verbose_name=_("Category"),
        help_text=_("Categoria principale dell'evento."),
    )

    # --- Organizer ---
    organizer_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Organizer name"),
        help_text=_("Nome del Club o ente organizzatore dell'evento."),
    )
    organizer_url = models.URLField(
        blank=True,
        verbose_name=_("Organizer URL"),
        help_text=_("Sito web del Club federato dove l'evento è pubblicato."),
    )

    # --- Wagtail config ---
    parent_page_types = ["website.EventsPage"]
    subpage_types = []
    template = "website/pages/event_detail_page.html"

    # --- Panels ---
    content_panels = Page.content_panels + [
        FieldPanel("cover_image"),
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("end_date"),
                    ]
                ),
            ],
            heading=_("Schedule"),
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("tags"),
            ],
            heading=_("Categorisation"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("organizer_name"),
                FieldPanel("organizer_url"),
            ],
            heading=_("Organizer"),
        ),
    ]

    registration_panels = [
        MultiFieldPanel(
            [
                FieldPanel("registration_open"),
                FieldPanel("registration_deadline"),
                FieldPanel("max_attendees"),
                FieldPanel("allow_guests"),
            ],
            heading=_("Registration settings"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("base_fee"),
                FieldPanel("member_discount_percent"),
                FieldPanel("early_bird_discount"),
                FieldPanel("early_bird_deadline"),
            ],
            heading=_("Pricing"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("passenger_fee"),
                FieldPanel("passenger_member_discount_percent"),
                FieldPanel("passenger_included"),
            ],
            heading=_("Passenger pricing"),
        ),
        InlinePanel("pricing_tiers", label=_("Pricing tiers")),
    ]

    map_panels = [
        MultiFieldPanel(
            [
                FieldPanel("location_name"),
                FieldPanel("location_address"),
                FieldPanel("location_coordinates"),
                FieldPanel("meeting_point"),
                FieldPanel("difficulty_level"),
            ],
            heading=_("Location"),
        ),
    ]

    promote_panels = Page.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(map_panels, heading=_("Location")),
            ObjectList(registration_panels, heading=_("Registration")),
            ObjectList(promote_panels, heading=_("Promote")),
            ObjectList(Page.settings_panels, heading=_("Settings")),
        ]
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.SearchField("location_name"),
        index.SearchField("location_address"),
        index.SearchField("meeting_point"),
        index.RelatedFields("category", [index.SearchField("name")]),
        index.FilterField("latitude"),
        index.FilterField("longitude"),
        index.FilterField("start_date"),
    ]

    class Meta:
        verbose_name = _("Event detail page")
        verbose_name_plural = _("Event detail pages")
        ordering = ["-start_date"]

    def clean(self):
        super().clean()
        if self.registration_deadline and self.start_date:
            if self.registration_deadline >= self.start_date:
                raise ValidationError(
                    {"registration_deadline": _("Registration deadline must be before the event start date.")}
                )
        # Auto-populate latitude/longitude from location_coordinates
        self._sync_lat_lng()

    def save(self, *args, **kwargs):
        self._sync_lat_lng()
        super().save(*args, **kwargs)

    def _sync_lat_lng(self):
        """Parse location_coordinates and set latitude/longitude."""
        if self.location_coordinates and "," in self.location_coordinates:
            try:
                parts = self.location_coordinates.split(",")
                self.latitude = float(parts[0].strip())
                self.longitude = float(parts[1].strip())
            except (ValueError, IndexError):
                self.latitude = None
                self.longitude = None
        else:
            self.latitude = None
            self.longitude = None

    # --- Computed properties ---

    @property
    def is_past(self) -> bool:
        """Return True if the event has already ended (or started, when no end_date)."""
        reference = self.end_date or self.start_date
        return reference < timezone.now()

    @property
    def computed_deadline(self):
        """Deadline from PricingTier with is_deadline=True, or fallback to registration_deadline."""
        from datetime import timedelta

        deadline_tier = self.pricing_tiers.filter(is_deadline=True).first()
        if deadline_tier and self.start_date:
            offset = timedelta(
                days=deadline_tier.days_before,
                hours=deadline_tier.hours_before,
                minutes=deadline_tier.minutes_before,
            )
            return self.start_date - offset
        return self.registration_deadline

    @property
    def is_registration_open(self) -> bool:
        """Check if registration is currently accepted."""
        if not self.registration_open:
            return False
        if self.is_past:
            return False
        deadline = self.computed_deadline
        if deadline and timezone.now() > deadline:
            return False
        if self.max_attendees and self.confirmed_count >= self.max_attendees:
            return False
        return True

    @cached_property
    def confirmed_count(self) -> int:
        """Number of confirmed registrations.

        Returns 0 if the registration model has not been created yet.
        """
        try:
            return self.registrations.filter(
                status__in=["registered", "confirmed"]
            ).count()
        except Exception:
            return 0

    @property
    def spots_remaining(self) -> int | None:
        """Return remaining spots, or None if unlimited."""
        if not self.max_attendees:
            return None
        remaining = self.max_attendees - self.confirmed_count
        return max(0, remaining)

    @property
    def current_price(self) -> "models.Decimal":
        """Return current price considering early-bird discount."""
        from decimal import Decimal

        price = self.base_fee
        if (
            self.early_bird_discount
            and self.early_bird_deadline
            and timezone.now() < self.early_bird_deadline
        ):
            discount = Decimal(self.early_bird_discount) / Decimal(100)
            price = price * (1 - discount)
        return price

    def member_price(self) -> "models.Decimal":
        """Return price with member discount applied on top of current price."""
        from decimal import Decimal

        price = self.current_price
        if self.member_discount_percent:
            discount = Decimal(self.member_discount_percent) / Decimal(100)
            price = price * (1 - discount)
        return price

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if request.user.is_authenticated:
            from apps.events.models import EventRegistration

            context["user_registration"] = (
                EventRegistration.objects.filter(
                    event=self,
                    user=request.user,
                    status__in=["registered", "confirmed"],
                ).first()
            )
        return context

    # ------------------------------------------------------------------
    # Routable sub-pages
    # ------------------------------------------------------------------

    @route(r"^$")
    def detail_view(self, request):
        """Serve the normal event detail page."""
        return self.render(request)

    @route(r"^register/$", name="register")
    def register_view(self, request):
        """
        Handle event registration for both authenticated and guest users.

        GET:  display the registration form with pricing info.
        POST: validate and create the EventRegistration record.
        """
        from django.db import transaction
        from django.shortcuts import redirect
        from django.urls import reverse

        from apps.events.forms import EventRegistrationForm, GuestRegistrationForm
        from apps.events.models import EventRegistration
        from apps.events.utils import calculate_price

        user = request.user if request.user.is_authenticated else None
        form_class = EventRegistrationForm if user else GuestRegistrationForm

        if request.method == "POST":
            form = form_class(
                request.POST, event_page=self, user=user,
            )
            if form.is_valid():
                return self._process_registration(request, form, user)
        else:
            form = form_class(event_page=self, user=user)

        pricing = calculate_price(self, user=user)
        return self.render(
            request,
            template="events/register.html",
            context_overrides={
                "form": form,
                "event": self,
                "pricing": pricing,
                "page": self,
            },
        )

    def _process_registration(self, request, form, user):
        """Validate business rules and create the EventRegistration."""
        from django.db import transaction
        from django.shortcuts import redirect
        from django.utils import timezone as tz

        from apps.events.models import EventRegistration
        from apps.events.utils import calculate_price, events_area_url

        # Validate registration is open
        if not self.is_registration_open:
            form.add_error(None, _("Registration is not open for this event."))
            return self._render_register_form(request, form, user)

        # Check deadline
        deadline = self.computed_deadline or self.registration_deadline
        if deadline and tz.now() > deadline:
            form.add_error(None, _("The registration deadline has passed."))
            return self._render_register_form(request, form, user)

        # Check member permissions
        if user and hasattr(user, "can_register_events"):
            if not user.can_register_events:
                form.add_error(
                    None,
                    _(
                        "Your membership does not include event registration. "
                        "Please upgrade your membership."
                    ),
                )
                return self._render_register_form(request, form, user)

        # Check for duplicate registration
        if user:
            existing = EventRegistration.objects.filter(
                event=self,
                user=user,
                status__in=["registered", "confirmed", "waitlist"],
            ).exists()
            if existing:
                form.add_error(
                    None,
                    _("You are already registered for this event."),
                )
                return self._render_register_form(request, form, user)

        # Calculate payment amount
        pricing = calculate_price(self, user=user)
        guests = form.cleaned_data.get("guests", 0) or 0
        has_passenger = form.cleaned_data.get("has_passenger", False)
        per_person = pricing["final_price"]
        total_heads = 1 + guests
        payment_amount = per_person * total_heads
        if has_passenger:
            payment_amount += pricing["passenger_price"]

        # Build registration
        max_attendees = self.max_attendees or 0
        registration = form.save(commit=False)
        registration.event = self
        registration.payment_amount = payment_amount

        if user:
            registration.user = user

        if payment_amount <= 0:
            registration.payment_status = "paid"
            registration.payment_provider = "free"

        with transaction.atomic():
            if max_attendees > 0:
                confirmed_count = (
                    EventRegistration.objects.select_for_update()
                    .filter(
                        event=self,
                        status__in=["registered", "confirmed"],
                    )
                    .count()
                )
                if confirmed_count >= max_attendees:
                    registration.status = "waitlist"
                else:
                    registration.status = "registered"
            else:
                registration.status = "registered"

            registration.save()

        # Redirect to payment choice for paid events
        if payment_amount > 0 and user:
            return redirect(events_area_url("payment_choice", args=[registration.pk]))

        if user:
            return redirect(events_area_url("my_registrations"))
        return redirect(self.url)

    def _render_register_form(self, request, form, user):
        """Re-render the register form with errors."""
        from apps.events.utils import calculate_price

        pricing = calculate_price(self, user=user)
        return self.render(
            request,
            template="events/register.html",
            context_overrides={
                "form": form,
                "event": self,
                "pricing": pricing,
                "page": self,
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# 7b. EventsAreaPage
# ═══════════════════════════════════════════════════════════════════════════

class EventsAreaPage(RoutablePageMixin, Page):
    """
    Container page for authenticated event-management views.

    Routes:
        /                              — landing (redirect to my-registrations)
        /my-registrations/             — list user's registrations
        /my-events/                    — favorite events (upcoming)
        /my-events/archive/            — past favorites
        /cancel/<pk>/                  — cancel registration (POST)
        /payment/<pk>/                 — choose payment provider
        /payment/<pk>/bank-transfer/   — bank transfer instructions
        /payment/<pk>/success/         — payment success
        /payment/<pk>/cancel/          — payment cancelled
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Introductory text for the events area landing page."),
    )

    max_count = 1
    parent_page_types = ["wagtailcore.Page", "website.HomePage"]
    subpage_types = []
    template = "events/my_registrations.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    class Meta:
        verbose_name = _("Events Area Page")
        verbose_name_plural = _("Events Area Pages")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _login_required(self, request):
        """Return a redirect to login if user is not authenticated, else None."""
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            from django.shortcuts import redirect

            login_url = getattr(django_settings, "LOGIN_URL", "/account/login/")
            return redirect(f"{login_url}?next={request.path}")
        return None

    # ------------------------------------------------------------------
    # Landing → my-registrations
    # ------------------------------------------------------------------

    @route(r"^$")
    def landing_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir
        from django.shortcuts import redirect

        return redirect(self.url + self.reverse_subpage("my_registrations"))

    # ------------------------------------------------------------------
    # My Registrations
    # ------------------------------------------------------------------

    @route(r"^my-registrations/$", name="my_registrations")
    def my_registrations_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from apps.events.models import EventRegistration

        qs = (
            EventRegistration.objects.filter(user=request.user)
            .select_related("event")
            .order_by("-registered_at")
        )

        paginator = Paginator(qs, 20)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return self.render(
            request,
            template="events/my_registrations.html",
            context_overrides={
                "registrations": page_obj,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # My Events (upcoming favorites)
    # ------------------------------------------------------------------

    @route(r"^my-events/$", name="my_events")
    def my_events_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from apps.events.models import EventFavorite

        now = timezone.now()
        qs = (
            EventFavorite.objects.filter(
                user=request.user,
                event__start_date__gte=now,
            )
            .select_related("event")
            .order_by("event__start_date")
        )

        paginator = Paginator(qs, 20)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return self.render(
            request,
            template="events/my_events.html",
            context_overrides={
                "favorites": page_obj,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # My Events Archive (past favorites)
    # ------------------------------------------------------------------

    @route(r"^my-events/archive/$", name="my_events_archive")
    def my_events_archive_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from apps.events.models import EventFavorite

        now = timezone.now()
        qs = (
            EventFavorite.objects.filter(
                user=request.user,
                event__start_date__lt=now,
            )
            .select_related("event")
            .order_by("-event__start_date")
        )

        paginator = Paginator(qs, 30)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # Group by year
        grouped = {}
        for fav in page_obj:
            year = fav.event.start_date.year
            grouped.setdefault(year, []).append(fav)
        favorites_by_year = dict(sorted(grouped.items(), reverse=True))

        return self.render(
            request,
            template="events/my_events_archive.html",
            context_overrides={
                "favorites": page_obj,
                "favorites_by_year": favorites_by_year,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Cancel Registration
    # ------------------------------------------------------------------

    @route(r"^cancel/(\d+)/$", name="cancel")
    def cancel_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        if request.method != "POST":
            from django.http import HttpResponseNotAllowed

            return HttpResponseNotAllowed(["POST"])

        from django.shortcuts import get_object_or_404, redirect

        from apps.events.models import EventRegistration
        from apps.events.utils import promote_from_waitlist

        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        if registration.status == "cancelled":
            return redirect(self.url + self.reverse_subpage("my_registrations"))

        if (
            registration.event.start_date
            and registration.event.start_date < timezone.now()
        ):
            return redirect(self.url + self.reverse_subpage("my_registrations"))

        was_active = registration.status in ("registered", "confirmed")
        registration.status = "cancelled"
        registration.save(update_fields=["status"])

        if was_active:
            promote_from_waitlist(registration.event)

        return redirect(self.url + self.reverse_subpage("my_registrations"))

    # ------------------------------------------------------------------
    # Payment Choice
    # ------------------------------------------------------------------

    @route(r"^payment/(\d+)/$", name="payment_choice")
    def payment_choice_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.shortcuts import get_object_or_404, redirect

        from apps.events.models import EventRegistration
        from apps.website.models.settings import PaymentSettings

        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        if registration.payment_status == "paid":
            return redirect(self.url + self.reverse_subpage("my_registrations"))

        payment_settings = PaymentSettings.for_request(request)

        if request.method == "POST":
            provider = request.POST.get("provider", "")

            if provider == "bank_transfer" and payment_settings.bank_transfer_enabled:
                return self._setup_bank_transfer(request, registration, payment_settings)

            if provider == "stripe" and payment_settings.stripe_enabled:
                return self._setup_stripe(request, registration, payment_settings)

            if provider == "paypal" and payment_settings.paypal_enabled:
                return self._setup_paypal(request, registration, payment_settings)

        return self._render_payment_choice(request, registration, payment_settings)

    def _render_payment_choice(self, request, registration, payment_settings, error=None):
        ctx = {
            "registration": registration,
            "event": registration.event,
            "available_providers": payment_settings.available_providers,
            "payment_settings": payment_settings,
            "page": self,
        }
        if error:
            ctx["error"] = error
        return self.render(
            request,
            template="events/payment_choice.html",
            context_overrides=ctx,
        )

    def _setup_bank_transfer(self, request, registration, payment_settings):
        import logging
        from datetime import timedelta

        from django.shortcuts import redirect

        from apps.events.payment import generate_payment_reference

        now = timezone.now()
        expiry_days = payment_settings.bank_transfer_expiry_days or 5
        expires_at = now + timedelta(days=expiry_days)

        if registration.event.start_date:
            max_expires = registration.event.start_date - timedelta(days=1)
            if expires_at > max_expires:
                expires_at = max_expires

        registration.payment_provider = "bank_transfer"
        registration.payment_reference = generate_payment_reference(registration)
        registration.payment_expires_at = expires_at
        registration.save(
            update_fields=["payment_provider", "payment_reference", "payment_expires_at"]
        )

        if registration.user:
            try:
                from apps.notifications.services import create_notification

                create_notification(
                    notification_type="payment_instructions",
                    title=str(_("Payment instructions: {event}")).format(
                        event=registration.event.title,
                    ),
                    body=str(
                        _("Please complete the bank transfer of \u20ac{amount} "
                          "with reference {ref} by {expires}.")
                    ).format(
                        amount=registration.payment_amount,
                        ref=registration.payment_reference,
                        expires=registration.payment_expires_at.strftime("%d/%m/%Y"),
                    ),
                    url=self.url + self.reverse_subpage("bank_transfer_instructions", args=[str(registration.pk)]),
                    recipients=[registration.user],
                    channels=["email"],
                    content_object=registration,
                )
            except Exception:
                pass

        return redirect(
            self.url + self.reverse_subpage("bank_transfer_instructions", args=[str(registration.pk)])
        )

    def _setup_stripe(self, request, registration, payment_settings):
        import logging

        from django.shortcuts import redirect

        logger = logging.getLogger(__name__)
        try:
            from apps.events.payment import create_stripe_checkout_session

            session_url = create_stripe_checkout_session(
                registration, payment_settings, request
            )
            return redirect(session_url)
        except Exception:
            logger.exception(
                "Stripe session creation failed for registration %s",
                registration.pk,
            )
            return self._render_payment_choice(
                request, registration, payment_settings,
                error=_("Payment service temporarily unavailable. Please try again."),
            )

    def _setup_paypal(self, request, registration, payment_settings):
        import logging

        from django.shortcuts import redirect

        logger = logging.getLogger(__name__)
        try:
            from apps.events.payment import create_paypal_order

            order_id, approval_url = create_paypal_order(
                registration, payment_settings, request
            )
            return redirect(approval_url)
        except Exception:
            logger.exception(
                "PayPal order creation failed for registration %s",
                registration.pk,
            )
            return self._render_payment_choice(
                request, registration, payment_settings,
                error=_("Payment service temporarily unavailable. Please try again."),
            )

    # ------------------------------------------------------------------
    # Bank Transfer Instructions
    # ------------------------------------------------------------------

    @route(r"^payment/(\d+)/bank-transfer/$", name="bank_transfer_instructions")
    def bank_transfer_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.shortcuts import get_object_or_404, redirect

        from apps.events.models import EventRegistration
        from apps.website.models.settings import PaymentSettings

        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )
        if registration.payment_provider != "bank_transfer":
            return redirect(self.url + self.reverse_subpage("my_registrations"))

        payment_settings = PaymentSettings.for_request(request)

        return self.render(
            request,
            template="events/payment_bank_transfer.html",
            context_overrides={
                "registration": registration,
                "event": registration.event,
                "payment_settings": payment_settings,
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Payment Success
    # ------------------------------------------------------------------

    @route(r"^payment/(\d+)/success/$", name="payment_success")
    def payment_success_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        import logging

        from django.shortcuts import get_object_or_404

        from apps.events.models import EventRegistration

        logger = logging.getLogger(__name__)
        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        # Verify Stripe payment if webhook hasn't arrived yet
        if (
            registration.payment_provider == "stripe"
            and registration.payment_status != "paid"
            and registration.payment_session_id
        ):
            try:
                import stripe as stripe_lib

                from apps.website.models.settings import PaymentSettings
                from wagtail.models import Site

                site = Site.objects.get(is_default_site=True)
                payment_settings = PaymentSettings.for_site(site)
                stripe_lib.api_key = payment_settings.stripe_secret_key

                session = stripe_lib.checkout.Session.retrieve(
                    registration.payment_session_id
                )
                if session.payment_status == "paid":
                    registration.payment_status = "paid"
                    registration.payment_id = session.payment_intent or ""
                    registration.save(
                        update_fields=["payment_status", "payment_id"]
                    )
            except Exception:
                logger.exception(
                    "Stripe payment verification failed for registration %s",
                    registration.pk,
                )

        return self.render(
            request,
            template="events/payment_success.html",
            context_overrides={
                "registration": registration,
                "event": registration.event,
                "payment_verified": registration.payment_status == "paid",
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Payment Cancel
    # ------------------------------------------------------------------

    @route(r"^payment/(\d+)/cancel/$", name="payment_cancel")
    def payment_cancel_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.shortcuts import get_object_or_404

        from apps.events.models import EventRegistration

        registration = get_object_or_404(
            EventRegistration, pk=pk, user=request.user,
        )

        return self.render(
            request,
            template="events/payment_cancel.html",
            context_overrides={
                "registration": registration,
                "event": registration.event,
                "page": self,
            },
        )


# ═══════════════════════════════════════════════════════════════════════════
# 8. GalleryPage
# ═══════════════════════════════════════════════════════════════════════════

class GalleryPage(RoutablePageMixin, Page):
    """
    Main gallery hub.  Displays albums from Wagtail collections.

    Sub-routes handle photo upload, user uploads list, and staff moderation.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo mostrato sopra le gallerie."),
    )
    root_collection = models.ForeignKey(
        Collection,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Root collection"),
        help_text=_("Starting collection for gallery display.  Sub-collections become albums."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto aggiuntivo sotto la galleria."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/gallery_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("root_collection"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = _("Gallery page")
        verbose_name_plural = _("Gallery pages")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from wagtail.images import get_image_model

        ImageModel = get_image_model()

        # Determine root; fall back to the global root collection.
        root = self.root_collection or Collection.objects.filter(depth=1).first()

        albums = []
        if root:
            children = root.get_children()
            for child in children:
                images = ImageModel.objects.filter(collection=child)
                if images.exists():
                    albums.append(
                        {
                            "id": child.pk,
                            "name": child.name,
                            "collection": child,
                            "cover_image": images.first(),
                            "image_count": images.count(),
                        }
                    )

        # If a specific album was requested via GET param, show its images
        album_id = request.GET.get("album")
        album = None
        photos = None
        if album_id:
            try:
                album = Collection.objects.get(pk=album_id)
                all_images = ImageModel.objects.filter(collection=album)
                paginator = Paginator(all_images, 24)
                page_number = request.GET.get("page")
                try:
                    photos = paginator.page(page_number)
                except PageNotAnInteger:
                    photos = paginator.page(1)
                except EmptyPage:
                    photos = paginator.page(paginator.num_pages)
                context["paginator"] = paginator
            except Collection.DoesNotExist:
                pass

        context["albums"] = albums
        context["album"] = album
        context["photos"] = photos
        return context

    # ------------------------------------------------------------------
    # Route: photo upload (active member + can_upload)
    # ------------------------------------------------------------------

    @route(r"^upload/$", name="upload_photo")
    def upload_photo_view(self, request):
        import logging

        from django.contrib.auth.decorators import login_required
        from django.http import HttpResponseForbidden

        from apps.members.decorators import active_member_required
        from apps.website.forms import PhotoUploadForm
        from apps.website.models.uploads import PhotoUpload
        from wagtail.images import get_image_model

        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            from django.shortcuts import redirect

            login_url = getattr(django_settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        if not getattr(request.user, "is_active_member", False):
            return HttpResponseForbidden(
                _("Access denied. Active membership is required.")
            )

        if not request.user.can_upload:
            return HttpResponseForbidden(
                _("Access denied. Your membership does not include "
                  "gallery upload privileges.")
            )

        ImageModel = get_image_model()

        if request.method == "POST":
            form = PhotoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                files = form.cleaned_data["photos"]
                title_prefix = form.cleaned_data.get("title_prefix", "")
                event = form.cleaned_data.get("event")
                tags = form.cleaned_data.get("tags", [])

                uploads_created = 0
                for i, f in enumerate(files):
                    if title_prefix:
                        title = f"{title_prefix} - {i + 1}"
                    else:
                        name_part = f.name.rsplit(".", 1)[0] if "." in f.name else f.name
                        title = name_part

                    image = ImageModel(
                        title=title,
                        file=f,
                        uploaded_by_user=request.user,
                    )
                    image.save()

                    upload = PhotoUpload.objects.create(
                        image=image,
                        uploaded_by=request.user,
                        event=event,
                    )
                    if tags:
                        upload.tags.set(tags)
                    uploads_created += 1

                from django.shortcuts import render
                return render(
                    request,
                    "website/uploads/upload_photo.html",
                    {
                        "form": PhotoUploadForm(),
                        "success": True,
                        "uploads_count": uploads_created,
                        "page": self,
                    },
                )
        else:
            form = PhotoUploadForm()

        from django.shortcuts import render
        return render(
            request,
            "website/uploads/upload_photo.html",
            {"form": form, "page": self},
        )

    # ------------------------------------------------------------------
    # Route: my uploads (login required)
    # ------------------------------------------------------------------

    @route(r"^my-uploads/$", name="my_uploads")
    def my_uploads_view(self, request):
        from django.shortcuts import redirect, render

        from apps.website.models.uploads import PhotoUpload

        if not request.user.is_authenticated:
            from django.conf import settings as django_settings

            login_url = getattr(django_settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        uploads_qs = PhotoUpload.objects.filter(
            uploaded_by=request.user
        ).select_related("image", "event").order_by("-uploaded_at")

        paginator = Paginator(uploads_qs, 20)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(
            request,
            "website/uploads/my_uploads.html",
            {
                "uploads": page_obj,
                "page_obj": page_obj,
                "is_paginated": paginator.num_pages > 1,
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Route: moderation queue (staff only)
    # ------------------------------------------------------------------

    @route(r"^moderation/$", name="moderation_queue")
    def moderation_queue_view(self, request):
        from django.http import HttpResponseForbidden
        from django.shortcuts import redirect, render

        from apps.website.models.uploads import PhotoUpload

        if not request.user.is_authenticated:
            from django.conf import settings as django_settings

            login_url = getattr(django_settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        if not request.user.is_staff:
            return HttpResponseForbidden(
                _("Access denied. Staff only.")
            )

        uploads_qs = PhotoUpload.objects.filter(
            is_approved=False,
            rejection_reason="",
        ).select_related(
            "image", "uploaded_by", "event"
        ).order_by("-uploaded_at")

        paginator = Paginator(uploads_qs, 30)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        return render(
            request,
            "website/uploads/moderation_queue.html",
            {
                "uploads": page_obj,
                "page_obj": page_obj,
                "is_paginated": paginator.num_pages > 1,
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Route: approve photo (staff only, POST)
    # ------------------------------------------------------------------

    @route(r"^moderation/approve/(?P<pk>\d+)/$", name="approve_photo")
    def approve_photo_view(self, request, pk):
        from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
        from django.shortcuts import get_object_or_404, redirect

        from apps.website.models.uploads import PhotoUpload

        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden(_("Access denied."))

        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        upload = get_object_or_404(PhotoUpload, pk=pk)

        upload.is_approved = True
        upload.approved_by = request.user
        upload.approved_at = timezone.now()
        upload.rejection_reason = ""
        upload.save(update_fields=[
            "is_approved",
            "approved_by",
            "approved_at",
            "rejection_reason",
        ])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"status": "approved", "pk": pk})

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(
            self.url + self.reverse_subpage("moderation_queue")
        )

    # ------------------------------------------------------------------
    # Route: reject photo (staff only, POST)
    # ------------------------------------------------------------------

    @route(r"^moderation/reject/(?P<pk>\d+)/$", name="reject_photo")
    def reject_photo_view(self, request, pk):
        from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
        from django.shortcuts import get_object_or_404

        from apps.website.models.uploads import PhotoUpload

        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden(_("Access denied."))

        if request.method != "POST":
            return HttpResponseNotAllowed(["POST"])

        upload = get_object_or_404(PhotoUpload, pk=pk)
        reason = request.POST.get("reason", "").strip()

        if not reason:
            reason = _("Rejected by moderator.")

        upload.is_approved = False
        upload.rejection_reason = reason
        upload.save(update_fields=["is_approved", "rejection_reason"])

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "status": "rejected",
                "pk": pk,
                "reason": str(reason),
            })

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(
            self.url + self.reverse_subpage("moderation_queue")
        )


# ═══════════════════════════════════════════════════════════════════════════
# 9. ContactPage
# ═══════════════════════════════════════════════════════════════════════════

class ContactPage(Page):
    """
    Contact information and contact form.
    """

    # Hero section (optional)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Hero image"),
        help_text=_("Optional background image for the page header."),
    )
    hero_badge = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Hero badge"),
        help_text=_("Small text above the title (e.g. 'Let's Talk')."),
    )

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo mostrato sopra il form di contatto."),
    )
    form_title = models.CharField(
        max_length=255,
        blank=True,
        default=_("Contact us"),
        verbose_name=_("Form title"),
        help_text=_("Titolo mostrato sopra il form di contatto."),
    )
    success_message = RichTextField(
        blank=True,
        verbose_name=_("Success message"),
        help_text=_("Confirmation shown after form submission."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto aggiuntivo sotto il form."),
    )

    # Captcha / anti-spam settings (stored per page for flexibility)
    captcha_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Enable captcha"),
        help_text=_("Attiva la protezione anti-spam sul form."),
    )
    captcha_provider = models.CharField(
        max_length=30,
        blank=True,
        default="honeypot",
        choices=[
            ("honeypot", _("Honeypot + Time check")),
            ("turnstile", _("Cloudflare Turnstile")),
            ("hcaptcha", _("hCaptcha")),
        ],
        verbose_name=_("Captcha provider"),
        help_text=_("Servizio anti-spam da utilizzare."),
    )
    captcha_site_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Captcha site key"),
        help_text=_("Chiave pubblica del servizio CAPTCHA."),
    )
    captcha_secret_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Captcha secret key"),
        help_text=_("Chiave segreta del servizio CAPTCHA."),
    )

    # Membership CTA (translatable - shown in sidebar)
    membership_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Membership CTA title"),
        help_text=_("E.g. 'Become a Member'"),
    )
    membership_description = models.TextField(
        blank=True,
        verbose_name=_("Membership CTA description"),
        help_text=_("Brief description of membership benefits."),
    )
    membership_price = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Membership price"),
        help_text=_("E.g. 'Annual fee €80'"),
    )
    membership_cta_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Membership CTA button text"),
        help_text=_("E.g. 'Request Form'"),
    )
    membership_cta_url = models.URLField(
        blank=True,
        verbose_name=_("Membership CTA URL"),
        help_text=_("Link to membership form or page."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/contact_page.html"

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_badge"),
            ],
            heading=_("Hero section"),
        ),
        FieldPanel("intro"),
        FieldPanel("form_title"),
        FieldPanel("success_message"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("membership_title"),
                FieldPanel("membership_description"),
                FieldPanel("membership_price"),
                FieldPanel("membership_cta_text"),
                FieldPanel("membership_cta_url"),
            ],
            heading=_("Membership CTA"),
        ),
    ]

    captcha_panels = [
        MultiFieldPanel(
            [
                FieldPanel("captcha_enabled"),
                FieldPanel("captcha_provider"),
                FieldPanel("captcha_site_key"),
                FieldPanel("captcha_secret_key"),
            ],
            heading=_("Anti-spam settings"),
        ),
    ]

    promote_panels = Page.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(captcha_panels, heading=_("Anti-spam")),
            ObjectList(promote_panels, heading=_("Promote")),
            ObjectList(Page.settings_panels, heading=_("Settings")),
        ]
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Contact page")
        verbose_name_plural = _("Contact pages")


# ═══════════════════════════════════════════════════════════════════════════
# 10. PrivacyPage
# ═══════════════════════════════════════════════════════════════════════════

class PrivacyPage(Page):
    """
    Privacy policy and legal information.
    """

    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto della pagina privacy/informativa."),
    )
    last_updated = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Last updated"),
        help_text=_("Date the policy was last revised."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/privacy_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("last_updated"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Privacy page")
        verbose_name_plural = _("Privacy pages")


# ═══════════════════════════════════════════════════════════════════════════
# 11. TransparencyPage
# ═══════════════════════════════════════════════════════════════════════════

class TransparencyPage(Page):
    """
    Legal documents, statutes, annual reports for nonprofit transparency.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo per la sezione trasparenza."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Use document-list and accordion blocks for organising documents."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/transparency_page.html"

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
        verbose_name = _("Transparency page")
        verbose_name_plural = _("Transparency pages")


# ═══════════════════════════════════════════════════════════════════════════
# 12. PressPage
# ═══════════════════════════════════════════════════════════════════════════

class PressPage(Page):
    """
    Press office / media page with brand kit, press releases, and contact.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Testo introduttivo per l'ufficio stampa."),
    )
    press_email = models.EmailField(
        blank=True,
        verbose_name=_("Press email"),
        help_text=_("Email dedicata per i contatti stampa."),
    )
    press_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Press phone"),
        help_text=_("Telefono dedicato per i contatti stampa."),
    )
    press_contact = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Press contact person"),
        help_text=_("Nome del referente stampa."),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
        help_text=_("Contenuto aggiuntivo per la pagina stampa."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/press_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("press_email"),
                FieldPanel("press_phone"),
                FieldPanel("press_contact"),
            ],
            heading=_("Press contact"),
        ),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Press page")
        verbose_name_plural = _("Press pages")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from apps.website.models.snippets import BrandAsset, PressRelease

        context["press_releases"] = PressRelease.objects.filter(
            is_archived=False
        ).order_by("-date")
        context["brand_assets"] = BrandAsset.objects.all().order_by("order", "name")
        return context


# ---------------------------------------------------------------------------
# MembershipPlansPage — public membership products page
# ---------------------------------------------------------------------------


class MembershipPlansPage(Page):
    """
    Public page showing available membership products/plans.

    Replaces the former Django TemplateView. As a Wagtail Page it gets
    automatic breadcrumbs, SEO tags, i18n via wagtail-localize, and lives
    in the page tree.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Displayed below the page title."),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/membership_plans_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = Page.promote_panels

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = _("Membership plans page")
        verbose_name_plural = _("Membership plans pages")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from apps.website.models.snippets import Product

        context["products"] = Product.objects.filter(
            is_active=True, locale=self.locale
        ).order_by("order")
        if request.user.is_authenticated:
            context["user_products"] = {
                p.pk for p in request.user.products.all()
            }
        else:
            context["user_products"] = set()
        return context

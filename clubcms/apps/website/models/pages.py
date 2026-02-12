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
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Hero background image"),
    )
    primary_cta_text = models.CharField(
        max_length=120,
        blank=True,
        verbose_name=_("Primary CTA text"),
    )
    primary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Primary CTA link"),
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
    )
    secondary_cta_link = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Secondary CTA link"),
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
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
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
    )

    # Tags and categories
    tags = ClusterTaggableManager(
        through="website.NewsPageTag",
        blank=True,
        verbose_name=_("Tags"),
    )
    category = models.ForeignKey(
        "website.NewsCategory",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_pages",
        verbose_name=_("Category"),
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
        return context


# ═══════════════════════════════════════════════════════════════════════════
# 7. EventDetailPage
# ═══════════════════════════════════════════════════════════════════════════

class EventDetailPage(Page):
    """
    Individual event with details, location, registration, and pricing.
    """

    # --- Core Fields ---
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
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
    )

    # --- Date/Time ---
    start_date = models.DateTimeField(
        verbose_name=_("Start date & time"),
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("End date & time"),
    )

    # --- Location ---
    location_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Venue name"),
    )
    location_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Address"),
    )
    location_coordinates = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Coordinates"),
        help_text=_("Latitude,Longitude (e.g. '45.4642,9.1900')"),
    )

    # --- Registration ---
    registration_open = models.BooleanField(
        default=False,
        verbose_name=_("Registration open"),
    )
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration deadline"),
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
    )
    early_bird_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Early-bird deadline"),
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
        index.RelatedFields("category", [index.SearchField("name")]),
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


# ═══════════════════════════════════════════════════════════════════════════
# 8. GalleryPage
# ═══════════════════════════════════════════════════════════════════════════

class GalleryPage(Page):
    """
    Main gallery hub.  Displays albums from Wagtail collections.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
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
                            "collection": child,
                            "cover": images.first(),
                            "count": images.count(),
                        }
                    )

        # If a specific album was requested via GET param, show its images
        album_id = request.GET.get("album")
        album_images = None
        current_album = None
        if album_id:
            try:
                current_album = Collection.objects.get(pk=album_id)
                all_images = ImageModel.objects.filter(collection=current_album)
                paginator = Paginator(all_images, 24)
                page_number = request.GET.get("page")
                try:
                    album_images = paginator.page(page_number)
                except PageNotAnInteger:
                    album_images = paginator.page(1)
                except EmptyPage:
                    album_images = paginator.page(paginator.num_pages)
                context["album_paginator"] = paginator
            except Collection.DoesNotExist:
                pass

        context["albums"] = albums
        context["album_images"] = album_images
        context["current_album"] = current_album
        return context


# ═══════════════════════════════════════════════════════════════════════════
# 9. ContactPage
# ═══════════════════════════════════════════════════════════════════════════

class ContactPage(Page):
    """
    Contact information and contact form.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
    )
    form_title = models.CharField(
        max_length=255,
        blank=True,
        default=_("Contact us"),
        verbose_name=_("Form title"),
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
    )

    # Captcha / anti-spam settings (stored per page for flexibility)
    captcha_enabled = models.BooleanField(
        default=True,
        verbose_name=_("Enable captcha"),
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
    )
    captcha_site_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Captcha site key"),
    )
    captcha_secret_key = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Captcha secret key"),
    )

    # --- Wagtail config ---
    max_count = 1
    subpage_types = []
    template = "website/pages/contact_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("form_title"),
        FieldPanel("success_message"),
        FieldPanel("body"),
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
    )
    press_email = models.EmailField(
        blank=True,
        verbose_name=_("Press email"),
    )
    press_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Press phone"),
    )
    press_contact = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Press contact person"),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Body"),
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

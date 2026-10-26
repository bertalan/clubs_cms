import json

from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet


# ---------------------------------------------------------------------------
# Tassonomia
# ---------------------------------------------------------------------------

class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Clubhouse")
    MONUMENT = "monument", _("Monument")
    SQUARE = "square", _("Square")
    POI = "poi", _("Point of interest")
    EVENT_VENUE = "event_venue", _("Event venue")
    ACCOMMODATION = "accommodation", _("Accommodation")
    RESTAURANT = "restaurant", _("Restaurant")


SCHEMA_TYPE_MAP = {
    PlaceType.CLUBHOUSE: ["Organization", "LocalBusiness"],
    PlaceType.MONUMENT: ["LandmarksOrHistoricalBuildings"],
    PlaceType.SQUARE: ["CivicStructure"],
    PlaceType.POI: ["TouristAttraction"],
    PlaceType.EVENT_VENUE: ["EventVenue"],
    PlaceType.ACCOMMODATION: ["LodgingBusiness"],
    PlaceType.RESTAURANT: ["FoodEstablishment"],
}

MAP_ICON_MAP = {
    PlaceType.CLUBHOUSE: "motorcycle",
    PlaceType.MONUMENT: "landmark",
    PlaceType.SQUARE: "map-pin",
    PlaceType.POI: "star",
    PlaceType.EVENT_VENUE: "calendar-check",
    PlaceType.ACCOMMODATION: "bed",
    PlaceType.RESTAURANT: "utensils",
}


# ---------------------------------------------------------------------------
# Snippet: PlaceTag
# ---------------------------------------------------------------------------

@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_("Slug"),
        help_text=_(
            "Appears in the link that lists every place with this tag, "
            "e.g. ?tag=castles. Lowercase letters, numbers and hyphens only."
        ),
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = _("Place tag")
        verbose_name_plural = _("Place tags")
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# PlaceIndexPage
# ---------------------------------------------------------------------------

class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa globale."""

    intro = RichTextField(blank=True, verbose_name=_("Introduction"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1
    template = "places/place_index_page.html"

    class Meta:
        verbose_name = _("Places index")
        verbose_name_plural = _("Places indexes")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = (
            PlacePage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("title")
        )

        # Filtro per tipo (whitelist sui valori validi)
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        # Filtro per tag
        tag_slug = request.GET.get("tag")
        if tag_slug:
            places = places.filter(tags__slug=tag_slug)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        context["active_type"] = place_type
        context["active_tag"] = tag_slug or ""
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        """Serializza i luoghi in GeoJSON per Leaflet."""
        features = []
        for place in places:
            if place.latitude is not None and place.longitude is not None:
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [
                                float(place.longitude),
                                float(place.latitude),
                            ],
                        },
                        "properties": {
                            "name": place.title,
                            "type": place.place_type,
                            "url": place.url,
                            "icon": place.get_map_icon(),
                        },
                    }
                )
        return json.dumps({"type": "FeatureCollection", "features": features})


# ---------------------------------------------------------------------------
# PlacePage
# ---------------------------------------------------------------------------

class PlacePage(Page):
    """Singolo luogo geolocalizzato con profilo Schema.org."""

    # Tipo
    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Place type"),
        help_text=_(
            "Sets the map icon and the type reported to search engines. "
            "Visitors can also filter the places list by type."
        ),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
        help_text=_(
            "Decimal degrees, e.g. 45.916700. Without both coordinates the "
            "place gets no map and no pin on the places map."
        ),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
        help_text=_("Decimal degrees, e.g. 9.316700. Copy it from a map app together with the latitude."),
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Street address"),
        help_text=_(
            "Street and number, e.g. Via Roma 12. Postal code, city and "
            "province have their own fields."
        ),
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
        help_text=_("Shown on the place card and searchable from the site search."),
    )
    province = models.CharField(
        max_length=5,
        blank=True,
        verbose_name=_("Province"),
        help_text=_("Abbreviation, e.g. LC. Shown in brackets after the city on the place card."),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("Postal code")
    )
    country = models.CharField(
        max_length=2,
        default="IT",
        verbose_name=_("Country code"),
        help_text=_("Two-letter ISO code, e.g. IT for Italy or CH for Switzerland."),
    )

    # Contenuto
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Short description"),
        help_text=_(
            "Shown on the place card and under the title of the place page. "
            "Search engines also use it as the page description."
        ),
    )
    description = RichTextField(blank=True, verbose_name=_("Description"))
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
        help_text=_("Shown at the top of the place page and on the place card."),
    )

    # Contatti & orari (dati pubblici del luogo, non dati personali utente)
    opening_hours = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Opening hours"),
        help_text=_(
            "Use the format search engines read, e.g. Mo-Fr 09:00-18:00, "
            "Sa 10:00-14:00. Visitors see it as written."
        ),
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Phone"),
        help_text=_("Public number of the place, never a member's. Visitors can tap it to call."),
    )
    email = models.EmailField(
        blank=True,
        verbose_name=_("Email"),
        help_text=_("Public address of the place, never a member's. Shown on the place page."),
    )
    website_url = models.URLField(
        blank=True,
        verbose_name=_("Website"),
        help_text=_("Full address starting with https://, shown as a link on the place page."),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag",
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Visitors can click a tag on the place page to list every place with the same tag."),
    )

    # ------------------------------------------------------------------
    # Panels
    # ------------------------------------------------------------------
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel(
            [
                FieldPanel("latitude"),
                FieldPanel("longitude"),
                FieldPanel("address"),
                FieldPanel("city"),
                FieldPanel("province"),
                FieldPanel("postal_code"),
                FieldPanel("country"),
            ],
            heading=_("Location"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("opening_hours"),
                FieldPanel("phone"),
                FieldPanel("email"),
                FieldPanel("website_url"),
            ],
            heading=_("Contacts and opening hours"),
        ),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Gallery images")),
    ]

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
    ]

    # ------------------------------------------------------------------
    # Page tree
    # ------------------------------------------------------------------
    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []
    template = "places/place_page.html"

    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")

    def __str__(self):
        return self.title

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_map_icon(self):
        """Nome icona per il frontend (Font Awesome)."""
        return MAP_ICON_MAP.get(self.place_type, "map-pin")

    def get_schema_types(self):
        """Lista di tipi Schema.org per questo luogo."""
        return SCHEMA_TYPE_MAP.get(self.place_type, ["Place"])

    def get_full_address(self):
        """Indirizzo leggibile in una riga."""
        parts = filter(None, [
            self.address,
            self.postal_code,
            self.city,
            self.province,
            self.country,
        ])
        return ", ".join(parts)


# ---------------------------------------------------------------------------
# PlaceGalleryImage (Orderable)
# ---------------------------------------------------------------------------

class PlaceGalleryImage(Orderable):
    """Immagine nella galleria di un luogo."""

    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("Image"),
    )
    caption = models.CharField(
        max_length=250,
        blank=True,
        verbose_name=_("Caption"),
        help_text=_(
            "Shown under the photo and read aloud by screen readers. "
            "If empty, the image title is used."
        ),
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _("Gallery image")
        verbose_name_plural = _("Gallery images")


# ---------------------------------------------------------------------------
# RoutePage
# ---------------------------------------------------------------------------

class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Short description"),
        help_text=_(
            "Shown under the title of the route page. Search engines also "
            "use it as the page description."
        ),
    )
    description = RichTextField(blank=True, verbose_name=_("Description"))
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Cover image"),
    )
    distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("Distance (km)"),
    )
    estimated_duration = models.DurationField(
        null=True,
        blank=True,
        verbose_name=_("Estimated duration"),
        help_text=_("Hours, minutes and seconds, e.g. 2:30:00 for two and a half hours."),
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", _("Easy")),
            ("medium", _("Medium")),
            ("hard", _("Hard")),
        ],
        default="medium",
        verbose_name=_("Difficulty"),
    )
    gpx_file = models.FileField(
        upload_to="routes/gpx/",
        blank=True,
        verbose_name=_("GPX file"),
        help_text=_(
            "Track exported from a GPS device or route planner. Visitors can "
            "download it from the route page."
        ),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel(
            [
                FieldPanel("distance_km"),
                FieldPanel("estimated_duration"),
                FieldPanel("difficulty"),
                FieldPanel("gpx_file"),
            ],
            heading=_("Route details"),
        ),
        InlinePanel("route_stops", label=_("Stops"), min_num=2),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.FilterField("difficulty"),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []
    template = "places/route_page.html"

    class Meta:
        verbose_name = _("Route")
        verbose_name_plural = _("Routes")

    def get_ordered_stops(self):
        return self.route_stops.select_related("place").order_by("sort_order")

    def get_duration_display(self):
        """Durata leggibile (es. '2h 30min')."""
        if not self.estimated_duration:
            return ""
        total_seconds = int(self.estimated_duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes = remainder // 60
        if hours and minutes:
            return f"{hours}h {minutes}min"
        if hours:
            return f"{hours}h"
        return f"{minutes}min"


# ---------------------------------------------------------------------------
# RouteStop (Orderable)
# ---------------------------------------------------------------------------

class RouteStop(Orderable):
    """Tappa di un percorso."""

    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops"
    )
    place = models.ForeignKey(
        "places.PlacePage",
        on_delete=models.CASCADE,
        related_name="route_appearances",
        verbose_name=_("Place"),
    )
    note = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Note"),
        help_text=_("Shown next to the stop in the route's list of stops, e.g. Coffee break."),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("note"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _("Stop")
        verbose_name_plural = _("Stops")

    def __str__(self):
        return f"{self.sort_order}. {self.place.title}"

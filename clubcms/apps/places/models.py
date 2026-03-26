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
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


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
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")
        ordering = ["name"]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# PlaceIndexPage
# ---------------------------------------------------------------------------

class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa globale."""

    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["wagtailcore.Page"]
    max_count = 1
    template = "places/place_index_page.html"

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

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
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo")
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città")
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia")
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP")
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO 3166-1)")
    )

    # Contenuto
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine di copertina"),
    )

    # Contatti & orari (dati pubblici del luogo, non dati personali utente)
    opening_hours = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(
        max_length=30, blank=True, verbose_name=_("Telefono")
    )
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag")
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
            heading=_("Geolocalizzazione"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("opening_hours"),
                FieldPanel("phone"),
                FieldPanel("email"),
                FieldPanel("website_url"),
            ],
            heading=_("Contatti e Orari"),
        ),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
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
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

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
        verbose_name=_("Immagine"),
    )
    caption = models.CharField(
        max_length=250, blank=True, verbose_name=_("Didascalia")
    )

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _("Immagine galleria")
        verbose_name_plural = _("Immagini galleria")


# ---------------------------------------------------------------------------
# RoutePage
# ---------------------------------------------------------------------------

class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve")
    )
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata")
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ("easy", _("Facile")),
            ("medium", _("Media")),
            ("hard", _("Difficile")),
        ],
        default="medium",
        verbose_name=_("Difficoltà"),
    )
    gpx_file = models.FileField(
        upload_to="routes/gpx/",
        blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
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
            heading=_("Dettagli Percorso"),
        ),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
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
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")

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
        verbose_name=_("Luogo"),
    )
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa")
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("note"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = _("Tappa")
        verbose_name_plural = _("Tappe")

    def __str__(self):
        return f"{self.sort_order}. {self.place.title}"

# Code Citations

## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/benoitdavidfr/cartes/blob/d924fc3dad68b22d2acff4b5c134db8758406c63/carte-gpf.html

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


## License: unknown
https://github.com/noahspoling/static-map/blob/de02a800b47f93b5733f282f4d8dc075bc0756ac/js/service/initMap.js

```
# Piano di Integrazione: App `places` — Luoghi Geolocalizzati con Schema.org

## Analisi

Hai ragione, manca un'entità fondamentale per un CMS di club/federazioni: i **luoghi**. Un motoclub ha una sede, organizza raduni in piazze, percorsi turistici passano per monumenti, ecc. Servono pagine con:

1. **Geolocalizzazione** (lat/lng, mappa)
2. **Markup Schema.org** semantico e differenziato per tipo
3. **Integrazione con il resto del CMS** (eventi in un luogo, club associato a una sede, percorsi come sequenze di luoghi)

---

## Architettura Proposta

### Nuova app: `places`

```
apps/places/
├── __init__.py
├── models.py          # PlacePage, Route, PlaceCategory
├── schema.py          # Generazione JSON-LD per ogni tipo
├── templatetags/
│   └── places_tags.py # {% place_schema %}, {% place_map %}
├── templates/
│   └── places/
│       ├── place_page.html
│       ├── place_index_page.html
│       ├── route_page.html
│       └── includes/
│           ├── map_widget.html
│           ├── schema_jsonld.html
│           └── place_card.html
├── wagtail_hooks.py
├── serializers.py     # API REST per mappa
├── views.py
├── tests/
│   ├── test_models.py
│   ├── test_schema.py
│   ├── test_views.py
│   └── test_api.py
└── migrations/
```

---

## Modelli

### 1. Tassonomia dei Luoghi (`PlaceType`)

Ogni tipo mappa a uno schema Schema.org diverso:

| Tipo interno | Schema.org | Uso |
|---|---|---|
| `clubhouse` | `Organization` + `LocalBusiness` | Sede motoclub |
| `monument` | `LandmarksOrHistoricalBuildings` | Monumento |
| `square` | `CivicStructure` | Piazza |
| `route` | `TouristTrip` | Percorso turistico |
| `poi` | `TouristAttraction` | Punto di interesse |
| `event_venue` | `EventVenue` | Luogo per eventi |
| `accommodation` | `LodgingBusiness` | Alloggio convenzionato |
| `restaurant` | `FoodEstablishment` | Ristorante convenzionato |

### 2. Modello Dati

````python
# filepath: apps/places/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField
from wagtail.search import index
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet


class PlaceType(models.TextChoices):
    CLUBHOUSE = "clubhouse", _("Sede Club")
    MONUMENT = "monument", _("Monumento")
    SQUARE = "square", _("Piazza")
    ROUTE = "route", _("Percorso Turistico")
    POI = "poi", _("Punto di Interesse")
    EVENT_VENUE = "event_venue", _("Luogo Eventi")
    ACCOMMODATION = "accommodation", _("Alloggio")
    RESTAURANT = "restaurant", _("Ristorante")


class PlaceIndexPage(Page):
    """Pagina indice che elenca tutti i luoghi con mappa."""
    intro = RichTextField(blank=True, verbose_name=_("Introduzione"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["places.PlacePage", "places.RoutePage"]
    parent_page_types = ["website.HomePage"]

    class Meta:
        verbose_name = _("Indice Luoghi")
        verbose_name_plural = _("Indici Luoghi")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        places = PlacePage.objects.live().public().specific()

        # Filtro per tipo
        place_type = request.GET.get("type")
        if place_type and place_type in PlaceType.values:
            places = places.filter(place_type=place_type)

        context["places"] = places
        context["place_types"] = PlaceType.choices
        # GeoJSON per la mappa
        context["places_geojson"] = self._build_geojson(places)
        return context

    def _build_geojson(self, places):
        import json
        features = []
        for place in places:
            if place.latitude and place.longitude:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(place.longitude), float(place.latitude)],
                    },
                    "properties": {
                        "name": place.title,
                        "type": place.place_type,
                        "url": place.full_url,
                        "icon": place.get_map_icon(),
                    },
                })
        return json.dumps({"type": "FeatureCollection", "features": features})


class PlacePage(Page):
    """Singolo luogo geolocalizzato."""

    place_type = models.CharField(
        max_length=20,
        choices=PlaceType.choices,
        default=PlaceType.POI,
        verbose_name=_("Tipo di luogo"),
    )

    # Geolocalizzazione
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Latitudine"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name=_("Longitudine"),
    )
    address = models.CharField(
        max_length=255, blank=True, verbose_name=_("Indirizzo"),
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name=_("Città"),
    )
    province = models.CharField(
        max_length=5, blank=True, verbose_name=_("Provincia"),
    )
    postal_code = models.CharField(
        max_length=10, blank=True, verbose_name=_("CAP"),
    )
    country = models.CharField(
        max_length=2, default="IT", verbose_name=_("Paese (ISO)"),
    )

    # Contenuto
    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
        help_text=_("Usata nelle card e nei risultati di ricerca."),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name=_("Immagine di copertina"),
    )

    # Metadati Schema.org aggiuntivi
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Orari di apertura"),
        help_text=_("Formato: Mo-Fr 09:00-18:00, Sa 10:00-14:00"),
    )
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Telefono"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    website_url = models.URLField(blank=True, verbose_name=_("Sito web"))

    # Relazione con Club (per sedi)
    associated_club = models.ForeignKey(
        "core.Club",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="places",
        verbose_name=_("Club associato"),
    )

    # Tags
    tags = ParentalManyToManyField(
        "places.PlaceTag", blank=True, verbose_name=_("Tag"),
    )

    # Panels
    content_panels = Page.content_panels + [
        FieldPanel("place_type"),
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("latitude"),
            FieldPanel("longitude"),
            FieldPanel("address"),
            FieldPanel("city"),
            FieldPanel("province"),
            FieldPanel("postal_code"),
            FieldPanel("country"),
        ], heading=_("Geolocalizzazione")),
        MultiFieldPanel([
            FieldPanel("opening_hours"),
            FieldPanel("phone"),
            FieldPanel("email"),
            FieldPanel("website_url"),
        ], heading=_("Contatti e Orari")),
        FieldPanel("associated_club"),
        FieldPanel("tags"),
        InlinePanel("gallery_images", label=_("Galleria immagini")),
    ]

    # Search
    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("short_description"),
        index.SearchField("city"),
        index.SearchField("address"),
        index.FilterField("place_type"),
        index.FilterField("city"),
    ]

    # API
    api_fields = [
        APIField("place_type"),
        APIField("latitude"),
        APIField("longitude"),
        APIField("address"),
        APIField("city"),
        APIField("short_description"),
        APIField("cover_image", serializer=ImageRenditionField("fill-400x300")),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Luogo")
        verbose_name_plural = _("Luoghi")

    def get_map_icon(self):
        """Icona per la mappa in base al tipo."""
        icons = {
            PlaceType.CLUBHOUSE: "motorcycle",
            PlaceType.MONUMENT: "landmark",
            PlaceType.SQUARE: "map-pin",
            PlaceType.ROUTE: "route",
            PlaceType.POI: "star",
            PlaceType.EVENT_VENUE: "calendar-check",
            PlaceType.ACCOMMODATION: "bed",
            PlaceType.RESTAURANT: "utensils",
        }
        return icons.get(self.place_type, "map-pin")

    def get_schema_type(self):
        """Restituisce il tipo Schema.org corrispondente."""
        mapping = {
            PlaceType.CLUBHOUSE: "Organization",
            PlaceType.MONUMENT: "LandmarksOrHistoricalBuildings",
            PlaceType.SQUARE: "CivicStructure",
            PlaceType.ROUTE: "TouristTrip",
            PlaceType.POI: "TouristAttraction",
            PlaceType.EVENT_VENUE: "EventVenue",
            PlaceType.ACCOMMODATION: "LodgingBusiness",
            PlaceType.RESTAURANT: "FoodEstablishment",
        }
        return mapping.get(self.place_type, "Place")


class PlaceGalleryImage(models.Model):
    """Immagine della galleria di un luogo."""
    page = ParentalKey(
        PlacePage, on_delete=models.CASCADE, related_name="gallery_images",
    )
    image = models.ForeignKey(
        "wagtailimages.Image", on_delete=models.CASCADE, related_name="+",
    )
    caption = models.CharField(max_length=250, blank=True, verbose_name=_("Didascalia"))

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    class Meta:
        verbose_name = _("Immagine galleria")


@register_snippet
class PlaceTag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name=_("Nome"))
    slug = models.SlugField(max_length=50, unique=True)

    panels = [FieldPanel("name"), FieldPanel("slug")]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Luogo")
        verbose_name_plural = _("Tag Luoghi")


class RoutePage(Page):
    """Percorso turistico = sequenza ordinata di PlacePage."""

    description = RichTextField(blank=True, verbose_name=_("Descrizione"))
    short_description = models.CharField(
        max_length=300, blank=True, verbose_name=_("Descrizione breve"),
    )
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        verbose_name=_("Immagine di copertina"),
    )
    distance_km = models.DecimalField(
        max_digits=7, decimal_places=1, null=True, blank=True,
        verbose_name=_("Distanza (km)"),
    )
    estimated_duration = models.DurationField(
        null=True, blank=True, verbose_name=_("Durata stimata"),
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
        upload_to="routes/gpx/", blank=True,
        verbose_name=_("File GPX"),
        help_text=_("Traccia GPX del percorso"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("short_description"),
        FieldPanel("description"),
        FieldPanel("cover_image"),
        MultiFieldPanel([
            FieldPanel("distance_km"),
            FieldPanel("estimated_duration"),
            FieldPanel("difficulty"),
            FieldPanel("gpx_file"),
        ], heading=_("Dettagli Percorso")),
        InlinePanel("route_stops", label=_("Tappe"), min_num=2),
    ]

    parent_page_types = ["places.PlaceIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = _("Percorso")
        verbose_name_plural = _("Percorsi")


class RouteStop(models.Model):
    """Tappa di un percorso."""
    route = ParentalKey(
        RoutePage, on_delete=models.CASCADE, related_name="route_stops",
    )
    place = models.ForeignKey(
        PlacePage, on_delete=models.CASCADE, related_name="route_appearances",
        verbose_name=_("Luogo"),
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordine"))
    note = models.CharField(
        max_length=255, blank=True, verbose_name=_("Nota tappa"),
    )

    panels = [
        FieldPanel("place"),
        FieldPanel("order"),
        FieldPanel("note"),
    ]

    class Meta:
        ordering = ["order"]
        verbose_name = _("Tappa")
````

---

## Schema.org — Generazione JSON-LD

````python
# filepath: apps/places/schema.py
import json
from django.utils.translation import gettext as _


def build_place_schema(place):
    """Genera il JSON-LD Schema.org per un PlacePage."""
    schema_type = place.get_schema_type()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": place.title,
        "description": place.short_description or place.search_description,
        "url": place.full_url,
    }

    # Geo
    if place.latitude and place.longitude:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address
    if place.address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": place.address,
            "addressLocality": place.city,
            "postalCode": place.postal_code,
            "addressRegion": place.province,
            "addressCountry": place.country,
        }

    # Image
    if place.cover_image:
        rendition = place.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    # Tipo-specifici
    if place.place_type == "clubhouse" and place.associated_club:
        schema["@type"] = ["Organization", "LocalBusiness"]
        schema["memberOf"] = {
            "@type": "Organization",
            "name": str(place.associated_club),
        }

    if place.opening_hours:
        schema["openingHours"] = place.opening_hours

    if place.phone:
        schema["telephone"] = place.phone

    if place.website_url:
        schema["sameAs"] = place.website_url

    return json.dumps(schema, ensure_ascii=False, indent=2)


def build_route_schema(route):
    """Genera il JSON-LD per un RoutePage (TouristTrip)."""
    stops = route.route_stops.select_related("place").all()

    itinerary = []
    for stop in stops:
        item = {
            "@type": "Place",
            "name": stop.place.title,
        }
        if stop.place.latitude and stop.place.longitude:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary.append(item)

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "description": route.short_description or route.search_description,
        "url": route.full_url,
        "itinerary": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "item": item,
                }
                for i, item in enumerate(itinerary)
            ],
        },
    }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        rendition = route.cover_image.get_rendition("fill-1200x630")
        schema["image"] = rendition.full_url

    return json.dumps(schema, ensure_ascii=False, indent=2)
````

---

## Template Tags

````python
# filepath: apps/places/templatetags/places_tags.py
from django import template
from django.utils.safestring import mark_safe
from apps.places.schema import build_place_schema, build_route_schema

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """Inserisce il JSON-LD Schema.org nel <head>."""
    from apps.places.models import PlacePage, RoutePage
    if isinstance(page, RoutePage):
        json_ld = build_route_schema(page)
    elif isinstance(page, PlacePage):
        json_ld = build_place_schema(page)
    else:
        return ""
    return mark_safe(f'<script type="application/ld+json">{json_ld}</script>')


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """Renderizza una mappa Leaflet."""
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }
````

---

## Integrazione con Eventi

````python
# filepath: apps/events/models.py (modifica)
# ...existing code...

# Aggiungere al modello EventPage:
venue = models.ForeignKey(
    "places.PlacePage",
    null=True, blank=True,
    on_delete=models.SET_NULL,
    related_name="events",
    verbose_name=_("Luogo"),
)

# Aggiungere ai content_panels:
# FieldPanel("venue"),
# ...existing code...
````

Questo permette di linkare ogni evento a un luogo e di mostrare nella pagina del luogo tutti gli eventi futuri associati.

---

## Mappa Frontend (Leaflet, zero costi)

````html
<!-- filepath: apps/places/templates/places/includes/map_widget.html -->
{% load i18n %}

<div id="place-map" style="height: {{ height }}; width: 100%; border-radius: var(--radius-md, 8px);"></div>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9/dist/leaflet.js"></script>

<script>
(function() {
    const map = L.map('place-map');
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(map);

    {% if place and place.latitude and place.longitude %}
        const lat
```


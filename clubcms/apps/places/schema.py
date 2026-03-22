"""
Generazione JSON-LD Schema.org per luoghi e percorsi.

Segue le stesse escape utilizzate da Django ``json_script`` per prevenire
XSS quando il JSON viene inserito in un tag ``<script>``.
"""

import json

from django.utils.html import strip_tags

# Escape characters that could break out of a <script> tag.
# Same approach as Django's json_script filter.
_JSON_SCRIPT_ESCAPES = str.maketrans(
    {
        "<": "\\u003C",
        ">": "\\u003E",
        "&": "\\u0026",
    }
)


def _safe_json(data):
    """Serializza dict in JSON sicuro per embedding in <script>."""
    return json.dumps(data, ensure_ascii=False, indent=2).translate(
        _JSON_SCRIPT_ESCAPES
    )


def build_place_schema(place):
    """Genera il dict JSON-LD Schema.org per un PlacePage."""
    schema_types = place.get_schema_types()

    schema = {
        "@context": "https://schema.org",
        "@type": schema_types if len(schema_types) > 1 else schema_types[0],
        "name": place.title,
        "url": place.full_url,
    }

    # Descrizione
    if place.short_description:
        schema["description"] = place.short_description
    elif place.description:
        schema["description"] = strip_tags(place.description)[:300]

    # Geo
    if place.latitude is not None and place.longitude is not None:
        schema["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": str(place.latitude),
            "longitude": str(place.longitude),
        }

    # Address — include only when at least street or city is provided
    has_meaningful_address = place.address or place.city
    if has_meaningful_address:
        address_parts = {"@type": "PostalAddress"}
        if place.address:
            address_parts["streetAddress"] = place.address
        if place.city:
            address_parts["addressLocality"] = place.city
        if place.province:
            address_parts["addressRegion"] = place.province
        if place.postal_code:
            address_parts["postalCode"] = place.postal_code
        if place.country:
            address_parts["addressCountry"] = place.country
        schema["address"] = address_parts

    # Immagine
    if place.cover_image:
        try:
            rendition = place.cover_image.get_rendition("fill-1200x630")
            schema["image"] = rendition.full_url
        except Exception:
            pass

    # Contatti (dati pubblici del luogo, non dati personali)
    if place.opening_hours:
        schema["openingHours"] = place.opening_hours
    if place.phone:
        schema["telephone"] = place.phone
    if place.website_url:
        schema["sameAs"] = place.website_url

    return schema


def build_route_schema(route):
    """Genera il dict JSON-LD Schema.org per un RoutePage (TouristTrip)."""
    stops = route.get_ordered_stops()

    itinerary_items = []
    for i, stop in enumerate(stops, 1):
        item = {"@type": "Place", "name": stop.place.title}
        if stop.place.latitude is not None and stop.place.longitude is not None:
            item["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(stop.place.latitude),
                "longitude": str(stop.place.longitude),
            }
        itinerary_items.append(
            {"@type": "ListItem", "position": i, "item": item}
        )

    schema = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": route.title,
        "url": route.full_url,
    }

    if route.short_description:
        schema["description"] = route.short_description
    elif route.description:
        schema["description"] = strip_tags(route.description)[:300]

    if itinerary_items:
        schema["itinerary"] = {
            "@type": "ItemList",
            "itemListElement": itinerary_items,
        }

    if route.distance_km:
        schema["distance"] = f"{route.distance_km} km"

    if route.cover_image:
        try:
            rendition = route.cover_image.get_rendition("fill-1200x630")
            schema["image"] = rendition.full_url
        except Exception:
            pass

    return schema


def render_jsonld(schema_dict):
    """Serializza un dict schema in stringa JSON-LD sicura per <script>."""
    return _safe_json(schema_dict)

from django import template
from django.utils.safestring import mark_safe

from apps.places.schema import build_place_schema, build_route_schema, render_jsonld

register = template.Library()


@register.simple_tag
def place_schema_jsonld(page):
    """
    Inserisce il JSON-LD Schema.org nel <head>.

    Uso: {% load places_tags %}{% place_schema_jsonld self %}

    Il JSON è sanitizzato con le stesse escape di Django ``json_script``
    per prevenire XSS (< > & vengono convertiti in \\uXXXX).
    """
    from apps.places.models import PlacePage, RoutePage

    if isinstance(page, PlacePage):
        schema = build_place_schema(page)
    elif isinstance(page, RoutePage):
        schema = build_route_schema(page)
    else:
        return ""

    json_ld = render_jsonld(schema)
    return mark_safe(
        f'<script type="application/ld+json">\n{json_ld}\n</script>'
    )


@register.inclusion_tag("places/includes/map_widget.html")
def place_map(place=None, geojson=None, height="400px"):
    """
    Renderizza una mappa Leaflet per un singolo luogo o per un GeoJSON.

    Uso singolo:   {% place_map place=self %}
    Uso indice:    {% place_map geojson=places_geojson %}
    """
    return {
        "place": place,
        "geojson": geojson,
        "height": height,
    }

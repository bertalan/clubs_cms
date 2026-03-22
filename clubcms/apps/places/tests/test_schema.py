"""Tests per la generazione JSON-LD Schema.org."""

import json
from decimal import Decimal

import pytest
from wagtail.models import Page

from apps.places.models import (
    PlaceIndexPage,
    PlacePage,
    PlaceType,
    RoutePage,
    RouteStop,
)
from apps.places.schema import (
    _safe_json,
    build_place_schema,
    build_route_schema,
    render_jsonld,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def place_index(db):
    root = Page.objects.first()
    return root.add_child(
        instance=PlaceIndexPage(title="Luoghi", slug="luoghi-schema")
    )


@pytest.fixture()
def poi_place(place_index):
    return place_index.add_child(
        instance=PlacePage(
            title="Test Place",
            slug="test-place",
            place_type=PlaceType.POI,
            latitude=Decimal("42.000000"),
            longitude=Decimal("12.000000"),
            address="Via Roma 1",
            city="Roma",
            province="RM",
            postal_code="00100",
            country="IT",
            short_description="Un bel posto.",
            phone="+39 06 1234567",
            opening_hours="Mo-Fr 09:00-18:00",
            website_url="https://example.com",
        )
    )


# ---------------------------------------------------------------------------
# _safe_json — XSS prevention
# ---------------------------------------------------------------------------

class TestSafeJson:

    def test_escapes_script_closing_tag(self):
        data = {"name": "Test </script> XSS"}
        result = _safe_json(data)
        assert "</script>" not in result
        assert "\\u003C/script\\u003E" in result

    def test_escapes_angle_brackets(self):
        data = {"html": "<b>bold</b>"}
        result = _safe_json(data)
        assert "<b>" not in result
        assert "\\u003C" in result

    def test_escapes_ampersand(self):
        data = {"q": "a&b"}
        result = _safe_json(data)
        assert "&" not in result
        assert "\\u0026" in result

    def test_preserves_unicode(self):
        data = {"name": "Città della Pieve"}
        result = _safe_json(data)
        assert "Città" in result


# ---------------------------------------------------------------------------
# build_place_schema
# ---------------------------------------------------------------------------

class TestBuildPlaceSchema:

    def test_basic_structure(self, poi_place):
        schema = build_place_schema(poi_place)
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "TouristAttraction"
        assert schema["name"] == "Test Place"

    def test_geo_coordinates(self, poi_place):
        schema = build_place_schema(poi_place)
        assert "geo" in schema
        assert schema["geo"]["@type"] == "GeoCoordinates"
        assert schema["geo"]["latitude"] == "42.000000"

    def test_address(self, poi_place):
        schema = build_place_schema(poi_place)
        assert "address" in schema
        assert schema["address"]["@type"] == "PostalAddress"
        assert schema["address"]["streetAddress"] == "Via Roma 1"
        assert schema["address"]["addressLocality"] == "Roma"

    def test_clubhouse_multi_type(self, place_index):
        place = place_index.add_child(
            instance=PlacePage(
                title="Sede Club",
                slug="sede-club",
                place_type=PlaceType.CLUBHOUSE,
            )
        )
        schema = build_place_schema(place)
        assert schema["@type"] == ["Organization", "LocalBusiness"]

    def test_restaurant_type(self, place_index):
        place = place_index.add_child(
            instance=PlacePage(
                title="Ristorante",
                slug="ristorante",
                place_type=PlaceType.RESTAURANT,
            )
        )
        schema = build_place_schema(place)
        assert schema["@type"] == "FoodEstablishment"

    def test_description_from_short(self, poi_place):
        schema = build_place_schema(poi_place)
        assert schema["description"] == "Un bel posto."

    def test_contacts(self, poi_place):
        schema = build_place_schema(poi_place)
        assert schema["telephone"] == "+39 06 1234567"
        assert schema["openingHours"] == "Mo-Fr 09:00-18:00"
        assert schema["sameAs"] == "https://example.com"

    def test_no_geo_when_missing(self, place_index):
        place = place_index.add_child(
            instance=PlacePage(
                title="No Geo",
                slug="no-geo",
                latitude=None,
                longitude=None,
            )
        )
        schema = build_place_schema(place)
        assert "geo" not in schema

    def test_no_address_when_empty(self, place_index):
        place = place_index.add_child(
            instance=PlacePage(
                title="No Addr",
                slug="no-addr",
            )
        )
        schema = build_place_schema(place)
        assert "address" not in schema


# ---------------------------------------------------------------------------
# build_route_schema
# ---------------------------------------------------------------------------

class TestBuildRouteSchema:

    @pytest.fixture()
    def route_with_stops(self, place_index, poi_place):
        place_b = place_index.add_child(
            instance=PlacePage(
                title="Arrivo",
                slug="arrivo",
                latitude=Decimal("43.500000"),
                longitude=Decimal("11.500000"),
            )
        )
        route = place_index.add_child(
            instance=RoutePage(
                title="Giro della Toscana",
                slug="giro-toscana",
                short_description="Un bel giro.",
                distance_km=Decimal("120.0"),
            )
        )
        RouteStop.objects.create(route=route, place=poi_place, sort_order=1)
        RouteStop.objects.create(route=route, place=place_b, sort_order=2)
        return route

    def test_basic_structure(self, route_with_stops):
        schema = build_route_schema(route_with_stops)
        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "TouristTrip"
        assert schema["name"] == "Giro della Toscana"

    def test_itinerary(self, route_with_stops):
        schema = build_route_schema(route_with_stops)
        items = schema["itinerary"]["itemListElement"]
        assert len(items) == 2
        assert items[0]["position"] == 1
        assert items[0]["item"]["name"] == "Test Place"
        assert items[1]["position"] == 2

    def test_distance(self, route_with_stops):
        schema = build_route_schema(route_with_stops)
        assert schema["distance"] == "120.0 km"

    def test_description(self, route_with_stops):
        schema = build_route_schema(route_with_stops)
        assert schema["description"] == "Un bel giro."


# ---------------------------------------------------------------------------
# render_jsonld
# ---------------------------------------------------------------------------

class TestRenderJsonld:

    def test_valid_json(self):
        data = {"@context": "https://schema.org", "@type": "Place", "name": "Test"}
        result = render_jsonld(data)
        # Replace escaped characters back for JSON parsing
        raw = result.replace("\\u003C", "<").replace("\\u003E", ">").replace("\\u0026", "&")
        parsed = json.loads(raw)
        assert parsed["name"] == "Test"

    def test_unicode_preserved(self):
        data = {"name": "Città della Pieve"}
        result = render_jsonld(data)
        assert "Città" in result

    def test_no_raw_script_tag(self):
        data = {"name": "</script><script>alert(1)</script>"}
        result = render_jsonld(data)
        assert "</script>" not in result

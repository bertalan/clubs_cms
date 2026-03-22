"""Tests per i modelli dell'app places."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.test import RequestFactory
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from apps.places.models import (
    PlaceGalleryImage,
    PlaceIndexPage,
    PlacePage,
    PlaceTag,
    PlaceType,
    RoutePage,
    RouteStop,
)

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def place_index(db):
    """PlaceIndexPage sotto la root di Wagtail."""
    root = Page.objects.first()
    return root.add_child(
        instance=PlaceIndexPage(title="Luoghi", slug="luoghi")
    )


@pytest.fixture()
def place_square(place_index):
    """PlacePage di tipo piazza con coordinate."""
    return place_index.add_child(
        instance=PlacePage(
            title="Piazza del Campo",
            slug="piazza-del-campo",
            place_type=PlaceType.SQUARE,
            latitude=Decimal("43.318340"),
            longitude=Decimal("11.331650"),
            address="Piazza del Campo",
            city="Siena",
            province="SI",
            postal_code="53100",
            country="IT",
            short_description="La piazza principale di Siena.",
            phone="+39 0577 123456",
            opening_hours="Mo-Su 00:00-24:00",
            website_url="https://example.com",
        )
    )


@pytest.fixture()
def place_clubhouse(place_index):
    """PlacePage di tipo sede club."""
    return place_index.add_child(
        instance=PlacePage(
            title="Sede Bikers Roma",
            slug="sede-bikers-roma",
            place_type=PlaceType.CLUBHOUSE,
            latitude=Decimal("41.890210"),
            longitude=Decimal("12.492231"),
            city="Roma",
            province="RM",
        )
    )


@pytest.fixture()
def place_restaurant(place_index):
    """PlacePage di tipo ristorante senza coordinate."""
    return place_index.add_child(
        instance=PlacePage(
            title="Trattoria da Mario",
            slug="trattoria-da-mario",
            place_type=PlaceType.RESTAURANT,
        )
    )


# ---------------------------------------------------------------------------
# Page tree (Wagtail)
# ---------------------------------------------------------------------------

class TestPlacePageTree(WagtailPageTestCase):
    """Verifica la gerarchia delle pagine Wagtail."""

    def test_place_can_be_created_under_index(self):
        self.assertCanCreateAt(PlaceIndexPage, PlacePage)

    def test_route_can_be_created_under_index(self):
        self.assertCanCreateAt(PlaceIndexPage, RoutePage)

    def test_place_cannot_nest_under_place(self):
        self.assertCanNotCreateAt(PlacePage, PlacePage)

    def test_route_cannot_nest_under_place(self):
        self.assertCanNotCreateAt(PlacePage, RoutePage)


# ---------------------------------------------------------------------------
# PlacePage
# ---------------------------------------------------------------------------

class TestPlacePage:

    def test_str(self, place_square):
        assert str(place_square) == "Piazza del Campo"

    def test_place_type_display(self, place_square):
        assert place_square.get_place_type_display() == "Piazza"

    def test_get_map_icon_square(self, place_square):
        assert place_square.get_map_icon() == "map-pin"

    def test_get_map_icon_clubhouse(self, place_clubhouse):
        assert place_clubhouse.get_map_icon() == "motorcycle"

    def test_get_schema_types_square(self, place_square):
        assert place_square.get_schema_types() == ["CivicStructure"]

    def test_get_schema_types_clubhouse(self, place_clubhouse):
        assert place_clubhouse.get_schema_types() == [
            "Organization",
            "LocalBusiness",
        ]

    def test_get_schema_types_unknown_fallback(self, place_square):
        place_square.place_type = "nonexistent"
        assert place_square.get_schema_types() == ["Place"]

    def test_get_full_address(self, place_square):
        full = place_square.get_full_address()
        assert "Piazza del Campo" in full
        assert "53100" in full
        assert "Siena" in full
        assert "SI" in full

    def test_get_full_address_partial(self, place_square):
        place_square.postal_code = ""
        place_square.province = ""
        full = place_square.get_full_address()
        assert "Siena" in full
        assert "SI" not in full


# ---------------------------------------------------------------------------
# PlaceTag
# ---------------------------------------------------------------------------

class TestPlaceTag:

    def test_str(self, db):
        tag = PlaceTag.objects.create(name="Storico", slug="storico")
        assert str(tag) == "Storico"

    def test_unique_name(self, db):
        PlaceTag.objects.create(name="Cultura", slug="cultura")
        with pytest.raises(Exception):
            PlaceTag.objects.create(name="Cultura", slug="cultura-2")


# ---------------------------------------------------------------------------
# PlaceIndexPage context
# ---------------------------------------------------------------------------

class TestPlaceIndexContext:

    def test_context_has_all_places(self, place_index, place_square, place_clubhouse):
        request = RequestFactory().get("/luoghi/")
        context = place_index.get_context(request)
        assert context["places"].count() == 2

    def test_context_filter_by_type(self, place_index, place_square, place_clubhouse):
        request = RequestFactory().get("/luoghi/?type=square")
        context = place_index.get_context(request)
        assert context["places"].count() == 1
        assert context["places"].first().title == "Piazza del Campo"

    def test_context_invalid_type_shows_all(self, place_index, place_square, place_clubhouse):
        request = RequestFactory().get("/luoghi/?type=INVALID")
        context = place_index.get_context(request)
        assert context["places"].count() == 2

    def test_geojson_structure(self, place_index, place_square, place_clubhouse):
        import json

        request = RequestFactory().get("/luoghi/")
        context = place_index.get_context(request)
        geojson = json.loads(context["places_geojson"])
        assert geojson["type"] == "FeatureCollection"
        assert len(geojson["features"]) == 2

    def test_geojson_excludes_places_without_coords(
        self, place_index, place_square, place_restaurant
    ):
        import json

        request = RequestFactory().get("/luoghi/")
        context = place_index.get_context(request)
        geojson = json.loads(context["places_geojson"])
        # restaurant has no coordinates
        assert len(geojson["features"]) == 1
        assert geojson["features"][0]["properties"]["name"] == "Piazza del Campo"


# ---------------------------------------------------------------------------
# RoutePage
# ---------------------------------------------------------------------------

class TestRoutePage:

    def test_duration_display_hours_and_minutes(self, place_index):
        route = place_index.add_child(
            instance=RoutePage(
                title="Percorso Test",
                slug="percorso-test",
                estimated_duration=timedelta(hours=2, minutes=30),
                distance_km=Decimal("85.5"),
            )
        )
        assert route.get_duration_display() == "2h 30min"

    def test_duration_display_hours_only(self, place_index):
        route = place_index.add_child(
            instance=RoutePage(
                title="Percorso H",
                slug="percorso-h",
                estimated_duration=timedelta(hours=3),
            )
        )
        assert route.get_duration_display() == "3h"

    def test_duration_display_minutes_only(self, place_index):
        route = place_index.add_child(
            instance=RoutePage(
                title="Percorso M",
                slug="percorso-m",
                estimated_duration=timedelta(minutes=45),
            )
        )
        assert route.get_duration_display() == "45min"

    def test_duration_display_empty(self, place_index):
        route = place_index.add_child(
            instance=RoutePage(
                title="Percorso Vuoto",
                slug="percorso-vuoto",
            )
        )
        assert route.get_duration_display() == ""

    def test_get_ordered_stops(self, place_index, place_square, place_clubhouse):
        route = place_index.add_child(
            instance=RoutePage(
                title="Giro Centro",
                slug="giro-centro",
            )
        )
        RouteStop.objects.create(
            route=route, place=place_clubhouse, sort_order=2, note="Arrivo"
        )
        RouteStop.objects.create(
            route=route, place=place_square, sort_order=1, note="Partenza"
        )
        stops = list(route.get_ordered_stops())
        assert len(stops) == 2
        assert stops[0].place.title == "Piazza del Campo"
        assert stops[1].place.title == "Sede Bikers Roma"

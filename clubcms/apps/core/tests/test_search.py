"""
Tests for the site-wide search functionality.
"""

from django.test import RequestFactory, TestCase

from apps.core.views import SearchView, haversine_km


class HaversineTests(TestCase):
    """Tests for the haversine_km distance function."""

    def test_same_point_returns_zero(self):
        self.assertAlmostEqual(haversine_km(45.0, 9.0, 45.0, 9.0), 0.0, places=5)

    def test_known_distance_milano_roma(self):
        """Milano (45.4642,9.19) → Roma (41.9028,12.4964) ≈ 477 km."""
        d = haversine_km(45.4642, 9.1900, 41.9028, 12.4964)
        self.assertAlmostEqual(d, 477, delta=10)

    def test_known_distance_milano_torino(self):
        """Milano → Torino ≈ 126 km."""
        d = haversine_km(45.4642, 9.1900, 45.0703, 7.6869)
        self.assertAlmostEqual(d, 126, delta=10)

    def test_antipodal_points(self):
        """Antipodal points should be roughly half Earth circumference."""
        d = haversine_km(0.0, 0.0, 0.0, 180.0)
        self.assertAlmostEqual(d, 20015, delta=50)


class SearchViewContextTests(TestCase):
    """Tests for SearchView parameter parsing."""

    def setUp(self):
        self.factory = RequestFactory()
        self.view = SearchView()

    def test_empty_params(self):
        request = self.factory.get("/search/")
        q, lat, lng, radius, rtype, per_page = self.view._get_params(request)
        self.assertEqual(q, "")
        self.assertIsNone(lat)
        self.assertIsNone(lng)
        self.assertEqual(radius, 50)
        self.assertEqual(rtype, "all")
        self.assertEqual(per_page, 25)

    def test_query_param(self):
        request = self.factory.get("/search/?q=motogiro&type=events")
        q, lat, lng, radius, rtype, per_page = self.view._get_params(request)
        self.assertEqual(q, "motogiro")
        self.assertEqual(rtype, "events")

    def test_geo_params(self):
        request = self.factory.get("/search/?lat=45.46&lng=9.19&radius=25")
        q, lat, lng, radius, rtype, per_page = self.view._get_params(request)
        self.assertAlmostEqual(lat, 45.46)
        self.assertAlmostEqual(lng, 9.19)
        self.assertEqual(radius, 25)

    def test_invalid_type_defaults(self):
        request = self.factory.get("/search/?type=INVALID")
        _, _, _, _, rtype, _ = self.view._get_params(request)
        self.assertEqual(rtype, "all")


class GeoFilterTests(TestCase):
    """Tests for the geo filtering mechanism."""

    def _make_mock_event(self, lat, lng, name="Event"):
        """Create a simple mock with the required attributes."""

        class MockEvent:
            pass

        ev = MockEvent()
        ev.latitude = lat
        ev.longitude = lng
        ev.location_name = name
        return ev

    def test_filter_within_radius(self):
        # Milano center
        user_lat, user_lng = 45.4642, 9.1900
        ev_near = self._make_mock_event(45.47, 9.20, "Near")  # ~1 km
        ev_far = self._make_mock_event(41.90, 12.50, "Far")  # ~477 km

        result = SearchView._apply_geo_filter(
            [ev_near, ev_far], user_lat, user_lng, 50
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].location_name, "Near")
        self.assertLess(result[0].distance_km, 5)

    def test_filter_with_no_coords(self):
        """Events without coordinates are excluded from geo results."""
        user_lat, user_lng = 45.4642, 9.1900
        ev = self._make_mock_event(None, None, "No coords")

        result = SearchView._apply_geo_filter([ev], user_lat, user_lng, 100)
        self.assertEqual(len(result), 0)

    def test_no_geo_returns_all(self):
        """When lat/lng are None, all events are returned unfiltered."""
        ev = self._make_mock_event(45.0, 9.0)
        result = SearchView._apply_geo_filter([ev], None, None, 50)
        self.assertEqual(len(result), 1)

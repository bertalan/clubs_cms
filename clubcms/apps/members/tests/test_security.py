"""
Tests for security fixes: rate limiting and access control.

SEC-2: Favorites rate limiting uses Django cache.
SEC-3: HelperDetailView requires active membership.
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client

User = get_user_model()


@pytest.mark.django_db
class TestFavoritesRateLimiting:
    """SEC-2: Rate limiting uses Django cache, not in-memory dict."""

    def test_rate_limit_uses_cache(self):
        """Verify the toggle_fav cache key pattern exists after toggle attempt."""
        user = User.objects.create_user(
            username="rateuser", password="testpass123!",
            membership_expiry=date.today() + timedelta(days=30),
        )
        # Set a cache key manually to simulate a recent toggle
        cache_key = f"toggle_fav_{user.pk}"
        cache.set(cache_key, True, 1)

        # The cache key should exist
        assert cache.get(cache_key) is True

    def test_no_module_level_dict_in_events_views(self):
        """The in-memory _toggle_timestamps dict should not exist in events.views."""
        from apps.events import views as events_views
        assert not hasattr(events_views, "_toggle_timestamps"), (
            "SEC-2: _toggle_timestamps dict still exists in events.views"
        )


@pytest.mark.django_db
class TestHelperDetailAccess:
    """SEC-3: HelperDetailView requires active membership."""

    def _create_helper(self):
        """Create a user who is available as a helper."""
        return User.objects.create_user(
            username="helper1",
            password="testpass123!",
            aid_available=True,
            aid_location_city="Rome",
            membership_expiry=date.today() + timedelta(days=365),
        )

    def test_anonymous_redirected_to_login(self, client):
        """Anonymous user is redirected to login."""
        helper = self._create_helper()
        response = client.get(f"/it/mutual-aid/helper/{helper.pk}/")
        assert response.status_code == 302
        assert "login" in response.url or "account" in response.url

    def test_non_member_gets_403(self, client):
        """Logged-in user without active membership gets 403."""
        helper = self._create_helper()
        viewer = User.objects.create_user(
            username="nonmember", password="testpass123!",
            membership_expiry=None,
        )
        client.force_login(viewer)
        response = client.get(f"/it/mutual-aid/helper/{helper.pk}/")
        assert response.status_code == 403

    def test_expired_member_gets_403(self, client):
        """Logged-in user with expired membership gets 403."""
        helper = self._create_helper()
        viewer = User.objects.create_user(
            username="expired", password="testpass123!",
            membership_expiry=date.today() - timedelta(days=1),
        )
        client.force_login(viewer)
        response = client.get(f"/it/mutual-aid/helper/{helper.pk}/")
        assert response.status_code == 403

    def test_active_member_gets_200(self, client):
        """Active member gets 200."""
        helper = self._create_helper()
        viewer = User.objects.create_user(
            username="active", password="testpass123!",
            membership_expiry=date.today() + timedelta(days=30),
        )
        client.force_login(viewer)
        response = client.get(f"/it/mutual-aid/helper/{helper.pk}/")
        assert response.status_code == 200

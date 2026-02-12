"""
Tests for ClubUser model.

Tests membership status properties and display name logic.
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


# ---------------------------------------------------------------------------
# Membership Status Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMembershipStatus:
    """Tests for ClubUser membership status properties."""

    def test_is_active_member_valid_expiry(self):
        """User with expiry in the future should be an active member."""
        future_date = date.today() + timedelta(days=30)
        user = User.objects.create_user(
            username="active_user",
            password="testpass123!",
            membership_expiry=future_date,
        )

        assert user.is_active_member is True

    def test_is_active_member_today_expiry(self):
        """User with expiry date today should still be an active member."""
        today = date.today()
        user = User.objects.create_user(
            username="today_user",
            password="testpass123!",
            membership_expiry=today,
        )

        assert user.is_active_member is True

    def test_is_active_member_past_expiry(self):
        """User with expiry in the past should not be an active member."""
        past_date = date.today() - timedelta(days=1)
        user = User.objects.create_user(
            username="expired_user",
            password="testpass123!",
            membership_expiry=past_date,
        )

        assert user.is_active_member is False

    def test_is_active_member_no_expiry(self):
        """User with no expiry date set should not be an active member."""
        user = User.objects.create_user(
            username="no_expiry_user",
            password="testpass123!",
            membership_expiry=None,
        )

        assert user.is_active_member is False

    def test_is_expired_inverse(self):
        """is_expired should be the opposite of is_active_member."""
        future_date = date.today() + timedelta(days=30)
        past_date = date.today() - timedelta(days=1)

        active_user = User.objects.create_user(
            username="active_for_expired",
            password="testpass123!",
            membership_expiry=future_date,
        )
        expired_user = User.objects.create_user(
            username="expired_for_expired",
            password="testpass123!",
            membership_expiry=past_date,
        )
        no_expiry_user = User.objects.create_user(
            username="no_expiry_for_expired",
            password="testpass123!",
            membership_expiry=None,
        )

        assert active_user.is_expired is False
        assert active_user.is_expired == (not active_user.is_active_member)

        assert expired_user.is_expired is True
        assert expired_user.is_expired == (not expired_user.is_active_member)

        assert no_expiry_user.is_expired is True
        assert no_expiry_user.is_expired == (not no_expiry_user.is_active_member)

    def test_days_to_expiry_future(self):
        """days_to_expiry should return positive days for future expiry."""
        future_date = date.today() + timedelta(days=15)
        user = User.objects.create_user(
            username="future_days_user",
            password="testpass123!",
            membership_expiry=future_date,
        )

        assert user.days_to_expiry == 15

    def test_days_to_expiry_past(self):
        """days_to_expiry should return negative days for past expiry."""
        past_date = date.today() - timedelta(days=10)
        user = User.objects.create_user(
            username="past_days_user",
            password="testpass123!",
            membership_expiry=past_date,
        )

        assert user.days_to_expiry == -10

    def test_days_to_expiry_none(self):
        """days_to_expiry should return None when no expiry is set."""
        user = User.objects.create_user(
            username="none_days_user",
            password="testpass123!",
            membership_expiry=None,
        )

        assert user.days_to_expiry is None


# ---------------------------------------------------------------------------
# Display Name Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDisplayName:
    """Tests for ClubUser.get_visible_name() method."""

    def test_get_visible_name_with_display_name(self):
        """Should use display_name when it is set."""
        user = User.objects.create_user(
            username="display_user",
            password="testpass123!",
            first_name="John",
            last_name="Doe",
            display_name="JD_Rider",
        )

        # Without a viewer, should return display_name
        assert user.get_visible_name() == "JD_Rider"

    def test_get_visible_name_without_display_name(self):
        """Should fall back to first/last name or username when no display_name."""
        # User with first and last name
        user_with_name = User.objects.create_user(
            username="named_user",
            password="testpass123!",
            first_name="Jane",
            last_name="Smith",
            display_name="",
        )

        # Should return "Jane S." format (first name + last initial)
        visible_name = user_with_name.get_visible_name()
        assert "Jane" in visible_name
        assert "S." in visible_name

        # User with only first name
        user_first_only = User.objects.create_user(
            username="first_only_user",
            password="testpass123!",
            first_name="Bob",
            last_name="",
            display_name="",
        )

        assert user_first_only.get_visible_name() == "Bob"

        # User with no names set should return an empty string or just whitespace
        user_no_names = User.objects.create_user(
            username="no_names_user",
            password="testpass123!",
            first_name="",
            last_name="",
            display_name="",
        )

        # When no display_name, first_name, or last_name, result is empty/stripped
        assert user_no_names.get_visible_name() == ""

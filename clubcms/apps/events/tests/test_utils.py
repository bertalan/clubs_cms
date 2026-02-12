"""
Unit tests for apps/events/utils.py

Tests pricing calculations and ICS calendar generation using mock objects.
No database access required - uses SimpleNamespace for mock objects.
"""

from datetime import datetime, timedelta, timezone as tz
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from apps.events.utils import (
    _escape_ics,
    calculate_price,
    generate_ics,
    generate_single_ics,
)


# ---------------------------------------------------------------------------
# Mock object factories
# ---------------------------------------------------------------------------


def create_mock_pricing_tier(
    days_before=0, hours_before=0, minutes_before=0, discount_percent=0
):
    """Create a mock PricingTier object."""
    return SimpleNamespace(
        days_before=days_before,
        hours_before=hours_before,
        minutes_before=minutes_before,
        discount_percent=discount_percent,
    )


def create_mock_event_page(
    base_fee=Decimal("0.00"),
    start_date=None,
    end_date=None,
    member_discount_percent=0,
    max_attendees=0,
    title="Test Event",
    pk=1,
    location_name="",
    location_address="",
    search_description="",
    pricing_tiers=None,
):
    """
    Create a mock EventPage object.

    Args:
        pricing_tiers: List of mock PricingTier objects or None for empty.
    """
    if start_date is None:
        start_date = datetime.now(tz.utc) + timedelta(days=30)

    # Build a mock manager that supports .all().order_by() chain
    tier_manager = MagicMock()
    tier_list = pricing_tiers or []

    def order_by_mock(*args):
        # Sort tiers by offset (descending) for the calculate_current_tier logic
        sorted_tiers = sorted(
            tier_list,
            key=lambda t: (t.days_before, t.hours_before, t.minutes_before),
            reverse=True,
        )
        return sorted_tiers

    tier_manager.all.return_value.order_by = order_by_mock

    return SimpleNamespace(
        base_fee=base_fee,
        start_date=start_date,
        end_date=end_date,
        member_discount_percent=member_discount_percent,
        max_attendees=max_attendees,
        title=title,
        pk=pk,
        location_name=location_name,
        location_address=location_address,
        search_description=search_description,
        pricing_tiers=tier_manager,
    )


def create_mock_user(is_active_member=False, max_discount_percent=0):
    """Create a mock User object."""
    return SimpleNamespace(
        is_active_member=is_active_member,
        max_discount_percent=max_discount_percent,
    )


# ---------------------------------------------------------------------------
# Pricing Tests
# ---------------------------------------------------------------------------


class TestCalculatePrice:
    """Tests for calculate_price function."""

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_no_fee(self, mock_tier):
        """Test that base_fee=0 results in final_price=0."""
        mock_tier.return_value = None
        event = create_mock_event_page(base_fee=Decimal("0.00"))

        result = calculate_price(event)

        assert result["base_fee"] == Decimal("0.00")
        assert result["final_price"] == Decimal("0.00")
        assert result["tier"] is None
        assert result["tier_discount_percent"] == 0
        assert result["member_discount_percent"] == 0
        assert result["total_discount_percent"] == 0

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_base_fee_no_discounts(self, mock_tier):
        """Test base_fee=100 with no discounts results in final_price=100."""
        mock_tier.return_value = None
        event = create_mock_event_page(base_fee=Decimal("100.00"))

        result = calculate_price(event)

        assert result["base_fee"] == Decimal("100.00")
        assert result["final_price"] == Decimal("100.00")
        assert result["tier_discount_percent"] == 0
        assert result["member_discount_percent"] == 0
        assert result["total_discount_percent"] == 0

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_with_tier_discount(self, mock_tier):
        """Test tier discount of 20% on base_fee=100 results in final_price=80."""
        tier = create_mock_pricing_tier(discount_percent=20)
        mock_tier.return_value = tier
        event = create_mock_event_page(base_fee=Decimal("100.00"))

        result = calculate_price(event)

        assert result["base_fee"] == Decimal("100.00")
        assert result["tier"] == tier
        assert result["tier_discount_percent"] == 20
        assert result["member_discount_percent"] == 0
        assert result["total_discount_percent"] == 20
        assert result["final_price"] == Decimal("80.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_with_member_discount(self, mock_tier):
        """Test member discount of 10% on base_fee=100 results in final_price=90."""
        mock_tier.return_value = None
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=10,
        )
        user = create_mock_user(is_active_member=True, max_discount_percent=0)

        result = calculate_price(event, user=user)

        assert result["base_fee"] == Decimal("100.00")
        assert result["tier_discount_percent"] == 0
        assert result["member_discount_percent"] == 10
        assert result["total_discount_percent"] == 10
        assert result["final_price"] == Decimal("90.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_combined_discounts(self, mock_tier):
        """Test tier 20% + member 10% = 30% discount -> final=70."""
        tier = create_mock_pricing_tier(discount_percent=20)
        mock_tier.return_value = tier
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=10,
        )
        user = create_mock_user(is_active_member=True, max_discount_percent=0)

        result = calculate_price(event, user=user)

        assert result["base_fee"] == Decimal("100.00")
        assert result["tier_discount_percent"] == 20
        assert result["member_discount_percent"] == 10
        assert result["total_discount_percent"] == 30
        assert result["final_price"] == Decimal("70.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_discount_capped_at_100(self, mock_tier):
        """Test tier 80% + member 50% = capped at 100% -> final=0."""
        tier = create_mock_pricing_tier(discount_percent=80)
        mock_tier.return_value = tier
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=50,
        )
        user = create_mock_user(is_active_member=True, max_discount_percent=0)

        result = calculate_price(event, user=user)

        assert result["base_fee"] == Decimal("100.00")
        assert result["tier_discount_percent"] == 80
        assert result["member_discount_percent"] == 50
        assert result["total_discount_percent"] == 100  # Capped
        assert result["final_price"] == Decimal("0.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_no_member_discount_for_non_members(self, mock_tier):
        """Test that non-active members get no member discount."""
        mock_tier.return_value = None
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=10,
        )
        user = create_mock_user(is_active_member=False, max_discount_percent=20)

        result = calculate_price(event, user=user)

        assert result["member_discount_percent"] == 0
        assert result["final_price"] == Decimal("100.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_no_user(self, mock_tier):
        """Test that user=None results in no member discount."""
        mock_tier.return_value = None
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=10,
        )

        result = calculate_price(event, user=None)

        assert result["member_discount_percent"] == 0
        assert result["final_price"] == Decimal("100.00")

    @patch("apps.events.utils.calculate_current_tier")
    def test_calculate_price_user_max_discount_wins(self, mock_tier):
        """Test that user.max_discount_percent is used when higher than event discount."""
        mock_tier.return_value = None
        event = create_mock_event_page(
            base_fee=Decimal("100.00"),
            member_discount_percent=10,  # Event discount is 10%
        )
        user = create_mock_user(
            is_active_member=True, max_discount_percent=25  # User discount is 25%
        )

        result = calculate_price(event, user=user)

        # User's max_discount_percent (25) wins over event's member_discount_percent (10)
        assert result["member_discount_percent"] == 25
        assert result["final_price"] == Decimal("75.00")


# ---------------------------------------------------------------------------
# ICS Escape Tests
# ---------------------------------------------------------------------------


class TestEscapeIcs:
    """Tests for _escape_ics function."""

    def test_escape_ics_special_chars(self):
        """Test that backslash, semicolon, comma, and newline are escaped."""
        text = "Hello\\World;Test,Data\nNewline"
        result = _escape_ics(text)

        assert result == "Hello\\\\World\\;Test\\,Data\\nNewline"

    def test_escape_ics_empty(self):
        """Test that empty string and None return empty string."""
        assert _escape_ics("") == ""
        assert _escape_ics(None) == ""

    def test_escape_ics_no_special_chars(self):
        """Test that text without special chars is unchanged."""
        text = "Simple text without special characters"
        result = _escape_ics(text)

        assert result == text

    def test_escape_ics_multiple_same_chars(self):
        """Test escaping multiple occurrences of same special char."""
        text = "a;b;c;d"
        result = _escape_ics(text)

        assert result == "a\\;b\\;c\\;d"


# ---------------------------------------------------------------------------
# ICS Generation Tests
# ---------------------------------------------------------------------------


class TestGenerateSingleIcs:
    """Tests for generate_single_ics function."""

    def test_generate_single_ics_structure(self):
        """Test that output contains required VCALENDAR and VEVENT markers."""
        event = create_mock_event_page(
            title="Test Event",
            pk=123,
            start_date=datetime(2025, 6, 15, 14, 0, tzinfo=tz.utc),
        )

        result = generate_single_ics(event)

        assert "BEGIN:VCALENDAR" in result
        assert "BEGIN:VEVENT" in result
        assert "END:VEVENT" in result
        assert "END:VCALENDAR" in result
        assert "VERSION:2.0" in result
        assert "PRODID:-//ClubCMS//Event//EN" in result

    def test_generate_single_ics_event_data(self):
        """Test that SUMMARY and DTSTART are present in output."""
        event = create_mock_event_page(
            title="Summer Ride 2025",
            pk=42,
            start_date=datetime(2025, 7, 20, 9, 30, tzinfo=tz.utc),
        )

        result = generate_single_ics(event)

        assert "SUMMARY:Summer Ride 2025" in result
        assert "DTSTART:20250720T093000Z" in result
        assert "UID:event-42@clubcms" in result

    def test_generate_single_ics_optional_end_date(self):
        """Test that DTEND is present when end_date is set."""
        event = create_mock_event_page(
            title="Weekend Rally",
            pk=99,
            start_date=datetime(2025, 8, 1, 10, 0, tzinfo=tz.utc),
            end_date=datetime(2025, 8, 3, 18, 0, tzinfo=tz.utc),
        )

        result = generate_single_ics(event)

        assert "DTSTART:20250801T100000Z" in result
        assert "DTEND:20250803T180000Z" in result

    def test_generate_single_ics_no_end_date(self):
        """Test that DTEND is not present when end_date is None."""
        event = create_mock_event_page(
            title="Short Meetup",
            pk=50,
            start_date=datetime(2025, 5, 10, 18, 0, tzinfo=tz.utc),
            end_date=None,
        )

        result = generate_single_ics(event)

        assert "DTSTART:20250510T180000Z" in result
        assert "DTEND:" not in result

    def test_generate_single_ics_no_location(self):
        """Test that LOCATION is not present when location_name is empty."""
        event = create_mock_event_page(
            title="Virtual Event",
            pk=77,
            start_date=datetime(2025, 9, 5, 20, 0, tzinfo=tz.utc),
            location_name="",
            location_address="",
        )

        result = generate_single_ics(event)

        assert "LOCATION:" not in result

    def test_generate_single_ics_with_location(self):
        """Test that LOCATION is present when location_name is set."""
        event = create_mock_event_page(
            title="Club Meeting",
            pk=88,
            start_date=datetime(2025, 10, 15, 19, 0, tzinfo=tz.utc),
            location_name="Club House",
            location_address="123 Main Street",
        )

        result = generate_single_ics(event)

        assert "LOCATION:Club House\\, 123 Main Street" in result

    def test_generate_single_ics_with_description(self):
        """Test that DESCRIPTION is present when search_description is set."""
        event = create_mock_event_page(
            title="Charity Ride",
            pk=111,
            start_date=datetime(2025, 11, 1, 8, 0, tzinfo=tz.utc),
            search_description="Annual charity ride to support local causes.",
        )

        result = generate_single_ics(event)

        assert "DESCRIPTION:Annual charity ride to support local causes." in result


class TestGenerateIcs:
    """Tests for generate_ics function (multiple events)."""

    def test_generate_ics_multiple_events(self):
        """Test that output has multiple VEVENTs for multiple events."""
        events = [
            create_mock_event_page(
                title="Event One",
                pk=1,
                start_date=datetime(2025, 1, 15, 10, 0, tzinfo=tz.utc),
            ),
            create_mock_event_page(
                title="Event Two",
                pk=2,
                start_date=datetime(2025, 2, 20, 14, 0, tzinfo=tz.utc),
            ),
            create_mock_event_page(
                title="Event Three",
                pk=3,
                start_date=datetime(2025, 3, 25, 18, 0, tzinfo=tz.utc),
            ),
        ]

        result = generate_ics(events)

        # Should have exactly one VCALENDAR
        assert result.count("BEGIN:VCALENDAR") == 1
        assert result.count("END:VCALENDAR") == 1

        # Should have three VEVENTs
        assert result.count("BEGIN:VEVENT") == 3
        assert result.count("END:VEVENT") == 3

        # Check each event is included
        assert "SUMMARY:Event One" in result
        assert "SUMMARY:Event Two" in result
        assert "SUMMARY:Event Three" in result
        assert "UID:event-1@clubcms" in result
        assert "UID:event-2@clubcms" in result
        assert "UID:event-3@clubcms" in result

    def test_generate_ics_empty_events(self):
        """Test that empty list produces valid calendar with no VEVENTs."""
        result = generate_ics([])

        # Should have valid calendar structure
        assert "BEGIN:VCALENDAR" in result
        assert "END:VCALENDAR" in result
        assert "VERSION:2.0" in result
        assert "PRODID:-//ClubCMS//Events//EN" in result

        # Should have no VEVENTs
        assert "BEGIN:VEVENT" not in result
        assert "END:VEVENT" not in result

    def test_generate_ics_calendar_name(self):
        """Test that the calendar has the X-WR-CALNAME header."""
        events = [
            create_mock_event_page(
                title="Test Event",
                pk=1,
                start_date=datetime(2025, 4, 1, 12, 0, tzinfo=tz.utc),
            ),
        ]

        result = generate_ics(events)

        assert "X-WR-CALNAME:My Favorite Events" in result

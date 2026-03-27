"""
Utility functions for the events app.

Provides pricing calculations, ICS calendar generation,
waitlist promotion logic, and EventsAreaPage URL resolution.
"""

from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# EventsAreaPage URL resolver
# ---------------------------------------------------------------------------


def events_area_url(route_name, args=None):
    """
    Resolve a URL for an EventsAreaPage routable sub-page.

    Args:
        route_name: The route name (e.g. "my_registrations", "payment_choice").
        args: Optional list of positional args for the route.

    Returns:
        str: The resolved URL path, or "/" as fallback.
    """
    from apps.website.models.pages import EventsAreaPage

    page = EventsAreaPage.objects.live().first()
    if page and page.url:
        if args:
            return page.url + page.reverse_subpage(
                route_name, args=[str(a) for a in args]
            )
        return page.url + page.reverse_subpage(route_name)
    return "/"


# ---------------------------------------------------------------------------
# 1. calculate_current_tier — find the active PricingTier for an event
# ---------------------------------------------------------------------------


def calculate_current_tier(event_page):
    """
    Return the currently active PricingTier for the given event page.

    Tiers are evaluated from the longest time-before-event to the
    shortest.  The first tier whose deadline has not yet passed
    (i.e. we are still *before* the tier boundary) is the active one.

    Returns None if no tier is active or no tiers are defined.
    """
    now = timezone.now()
    start = event_page.start_date
    if not start:
        return None

    # Fetch tiers ordered from longest offset to shortest
    tiers = list(
        event_page.pricing_tiers.all().order_by(
            "-days_before", "-hours_before", "-minutes_before"
        )
    )
    if not tiers:
        return None

    for tier in tiers:
        offset = timedelta(
            days=tier.days_before,
            hours=tier.hours_before,
            minutes=tier.minutes_before,
        )
        tier_deadline = start - offset
        if now <= tier_deadline:
            return tier

    # All tier deadlines have passed — no active tier
    return None


# ---------------------------------------------------------------------------
# 2. calculate_price — compute final price with tier + member discounts
# ---------------------------------------------------------------------------


def calculate_price(event_page, user=None):
    """
    Calculate the final price for an event registration.

    Applies the active tier discount first, then the member discount
    on the remaining amount.  Discounts are capped at 100%.

    Returns a dict with:
        - base_fee: Decimal
        - tier: PricingTier or None
        - tier_discount_percent: int
        - member_discount_percent: int
        - total_discount_percent: int (capped at 100)
        - final_price: Decimal
    """
    base_fee = Decimal(str(event_page.base_fee or 0))

    tier = calculate_current_tier(event_page)
    tier_discount = tier.discount_percent if tier else 0

    member_discount = 0
    if user and hasattr(user, "is_active_member") and user.is_active_member:
        # Use the higher of event member_discount_percent and user max_discount_percent
        event_member_discount = getattr(event_page, "member_discount_percent", 0) or 0
        user_max_discount = getattr(user, "max_discount_percent", 0) or 0
        member_discount = max(event_member_discount, user_max_discount)

    total_discount = min(tier_discount + member_discount, 100)
    discount_amount = base_fee * Decimal(total_discount) / Decimal(100)
    final_price = max(base_fee - discount_amount, Decimal("0.00"))

    return {
        "base_fee": base_fee,
        "tier": tier,
        "tier_discount_percent": tier_discount,
        "member_discount_percent": member_discount,
        "total_discount_percent": total_discount,
        "final_price": final_price,
        "passenger_price": _calculate_passenger_price(event_page, user),
    }


def _calculate_passenger_price(event_page, user=None):
    """
    Calculate the price for a passenger/companion.

    If passenger_included is True, returns 0.
    If passenger_fee is 0, uses the base_fee.
    Applies passenger_member_discount_percent if user is an active member.
    """
    if getattr(event_page, "passenger_included", False):
        return Decimal("0.00")

    passenger_fee = Decimal(str(getattr(event_page, "passenger_fee", 0) or 0))
    if passenger_fee <= 0:
        passenger_fee = Decimal(str(event_page.base_fee or 0))

    discount = 0
    if user and hasattr(user, "is_active_member") and user.is_active_member:
        discount = getattr(event_page, "passenger_member_discount_percent", 0) or 0

    discount_amount = passenger_fee * Decimal(discount) / Decimal(100)
    return max(passenger_fee - discount_amount, Decimal("0.00"))


# ---------------------------------------------------------------------------
# 3. generate_single_ics — ICS for a single event
# ---------------------------------------------------------------------------


def _escape_ics(text):
    """Escape text for use in an ICS field value."""
    if not text:
        return ""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _format_dt(dt):
    """Format a datetime as ICS DTSTART/DTEND value (UTC)."""
    if dt.tzinfo is not None:
        from datetime import timezone as tz

        dt = dt.astimezone(tz.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _build_vevent(event, lines):
    """Append a VEVENT block to *lines* for a single event."""
    lines.append("BEGIN:VEVENT")
    lines.append(f"UID:event-{event.pk}@clubcms")
    lines.append(f"DTSTART:{_format_dt(event.start_date)}")

    if event.end_date:
        lines.append(f"DTEND:{_format_dt(event.end_date)}")
    else:
        # Fallback: 2-hour duration so calendar apps don't show 0-length events
        fallback_end = event.start_date + timedelta(hours=2)
        lines.append(f"DTEND:{_format_dt(fallback_end)}")

    lines.append(f"SUMMARY:{_escape_ics(event.title)}")

    # Location
    location_parts = []
    if getattr(event, "location_name", ""):
        location_parts.append(event.location_name)
    if getattr(event, "location_address", ""):
        location_parts.append(event.location_address)
    if location_parts:
        lines.append(f"LOCATION:{_escape_ics(', '.join(location_parts))}")

    # GEO (latitude;longitude per RFC 5545)
    lat = getattr(event, "latitude", None)
    lng = getattr(event, "longitude", None)
    if lat is not None and lng is not None:
        lines.append(f"GEO:{lat};{lng}")

    # Description (no PII)
    description = getattr(event, "search_description", "") or ""
    if description:
        lines.append(f"DESCRIPTION:{_escape_ics(description)}")

    # URL — link back to event page
    url = getattr(event, "full_url", "") or ""
    if url:
        lines.append(f"URL:{url}")

    # Categories from tags
    tags = getattr(event, "tags", None)
    if tags:
        try:
            tag_names = [t.name for t in tags.all()]
        except (AttributeError, TypeError):
            tag_names = []
        if tag_names:
            lines.append(f"CATEGORIES:{_escape_ics(','.join(tag_names))}")

    # SEQUENCE from last_published_at (revision counter)
    last_pub = getattr(event, "last_published_at", None)
    if last_pub:
        lines.append(f"LAST-MODIFIED:{_format_dt(last_pub)}")

    now_str = _format_dt(timezone.now())
    lines.append(f"DTSTAMP:{now_str}")
    lines.append("SEQUENCE:0")
    lines.append("END:VEVENT")


def generate_single_ics(event):
    """
    Generate an ICS calendar string for a single event page.

    Only exposes event data (title, dates, location) — no PII.

    Args:
        event: An EventDetailPage instance.

    Returns:
        str: A complete ICS calendar string.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ClubCMS//Event//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    _build_vevent(event, lines)
    lines.append("END:VCALENDAR")

    return "\r\n".join(lines)


# ---------------------------------------------------------------------------
# 4. generate_ics — ICS for multiple events
# ---------------------------------------------------------------------------


def generate_ics(events, cal_name=None):
    """
    Generate an ICS calendar string for a list of event pages.

    Only exposes event data (title, dates, location) — no PII.

    Args:
        events: An iterable of EventDetailPage instances.
        cal_name: Calendar display name (defaults to translated
                  "My Favorite Events").

    Returns:
        str: A complete ICS calendar string with multiple VEVENTs.
    """
    if cal_name is None:
        cal_name = str(_("My Favorite Events"))

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ClubCMS//Events//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_escape_ics(cal_name)}",
        "REFRESH-INTERVAL;VALUE=DURATION:PT1H",
        "X-PUBLISHED-TTL:PT1H",
    ]

    for event in events:
        _build_vevent(event, lines)

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


# ---------------------------------------------------------------------------
# 5. promote_from_waitlist — when a spot opens
# ---------------------------------------------------------------------------


def promote_from_waitlist(event_page):
    """
    Promote the oldest waitlisted registration to 'registered' status.

    Called after a cancellation frees up a spot.  Respects the
    max_attendees limit (0 = unlimited).

    Returns the promoted EventRegistration or None.
    """
    from apps.events.models import EventRegistration

    # If event has unlimited capacity, there should be no waitlist
    max_attendees = event_page.max_attendees or 0
    if max_attendees == 0:
        return None

    confirmed_count = EventRegistration.objects.filter(
        event=event_page,
        status__in=["registered", "confirmed"],
    ).count()

    if confirmed_count >= max_attendees:
        return None

    # Promote the earliest waitlisted registration
    waitlisted = (
        EventRegistration.objects.filter(
            event=event_page,
            status="waitlist",
        )
        .order_by("registered_at")
        .first()
    )

    if waitlisted:
        waitlisted.status = "registered"
        waitlisted.save(update_fields=["status"])

        # Send promotion notification
        if waitlisted.user:
            try:
                from apps.notifications.services import create_notification

                create_notification(
                    notification_type="waitlist_promoted",
                    title=str(_("Spot available: {event}")).format(
                        event=event_page.title,
                    ),
                    body=str(
                        _("A spot has opened up! You have been promoted "
                          "from the waitlist for {event}.")
                    ).format(event=event_page.title),
                    recipients=[waitlisted.user],
                    channels=["email", "push"],
                    content_object=waitlisted,
                )
            except Exception:
                pass

    return waitlisted

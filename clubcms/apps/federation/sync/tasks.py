"""
Federation sync tasks.

Handles fetching events from partner clubs, syncing interest counts,
and cleaning up old external events. Designed to be called by
django-q2 scheduled tasks or the management command.
"""

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone as dj_tz

from apps.federation.api.security import sign_request
from apps.federation.models import ExternalEvent, ExternalEventInterest, FederatedClub
from apps.federation.utils import sanitize_html

logger = logging.getLogger(__name__)

# Timeout for outbound HTTP requests (seconds)
HTTP_TIMEOUT = 30


def sync_all_clubs():
    """
    Django-Q2 task: sync events from all active, approved partner clubs.

    Iterates over every active partner and calls ``sync_club_events``
    individually, catching per-club errors so one failure does not
    block the rest.
    """
    clubs = FederatedClub.objects.filter(is_active=True, is_approved=True)
    results = {"success": 0, "failed": 0}

    for club in clubs:
        try:
            sync_club_events(str(club.pk))
            results["success"] += 1
        except Exception as exc:
            results["failed"] += 1
            logger.error("Failed to sync %s: %s", club.short_code, exc)

    logger.info(
        "Federation sync complete: %d succeeded, %d failed",
        results["success"],
        results["failed"],
    )
    return results


def sync_club_events(club_id):
    """
    Fetch events from a single partner club via their Federation API.

    Builds an HMAC-signed request, fetches the JSON response via
    ``urllib``, and upserts ``ExternalEvent`` records.

    Parameters
    ----------
    club_id : str
        UUID primary key of the ``FederatedClub`` record (as string).
    """
    club = FederatedClub.objects.get(pk=club_id)

    # Build the URL
    base = club.base_url.rstrip("/")
    from_date = (dj_tz.now() - timedelta(days=1)).date().isoformat()
    url = f"{base}/api/federation/events/?from_date={from_date}"

    # Sign the request
    # When we call their API, we send X-Federation-Key = our_key_for_them
    # (so they can look us up) and sign with api_key (shared secret).
    timestamp = datetime.now(timezone.utc).isoformat()
    signature = sign_request(
        secret_key=club.our_key_for_them,
        timestamp=timestamp,
        body="",
    )

    headers = {
        "X-Federation-Key": club.api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Accept": "application/json",
        "User-Agent": "ClubCMS-Federation/1.0",
    }

    req = urllib.request.Request(url, headers=headers, method="GET")

    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        error_msg = f"HTTP {exc.code} from {club.short_code}: {exc.reason}"
        logger.error(error_msg)
        club.last_error = error_msg
        club.save(update_fields=["last_error"])
        raise
    except urllib.error.URLError as exc:
        error_msg = f"Connection error for {club.short_code}: {exc.reason}"
        logger.error(error_msg)
        club.last_error = error_msg
        club.save(update_fields=["last_error"])
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        error_msg = f"Invalid JSON from {club.short_code}: {exc}"
        logger.error(error_msg)
        club.last_error = error_msg
        club.save(update_fields=["last_error"])
        raise

    # Parse and upsert events
    events = data.get("events", [])
    created_count = 0
    updated_count = 0

    for event_data in events:
        external_id = event_data.get("id", "")
        if not external_id:
            continue

        # Parse dates
        start_date = _parse_datetime(event_data.get("start_date"))
        if start_date is None:
            logger.warning("Skipping event %s: invalid start_date", external_id)
            continue

        end_date = _parse_datetime(event_data.get("end_date"))

        # Sanitize description HTML
        description = sanitize_html(event_data.get("description", ""))

        defaults = {
            "event_name": event_data.get("event_name", "")[:255],
            "start_date": start_date,
            "end_date": end_date,
            "location_name": event_data.get("location_name", "")[:255],
            "location_address": event_data.get("location_address", "")[:500],
            "location_lat": event_data.get("location_lat"),
            "location_lon": event_data.get("location_lon"),
            "description": description,
            "event_status": event_data.get("event_status", "EventScheduled"),
            "image_url": event_data.get("image_url", "")[:200],
            "detail_url": event_data.get("detail_url", "")[:200],
            "is_approved": club.auto_import,
        }

        _, created = ExternalEvent.objects.update_or_create(
            source_club=club,
            external_id=external_id,
            defaults=defaults,
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    # Update club sync status
    club.last_sync = dj_tz.now()
    club.last_error = ""
    club.save(update_fields=["last_sync", "last_error"])

    logger.info(
        "Synced %s: %d created, %d updated (of %d total)",
        club.short_code,
        created_count,
        updated_count,
        len(events),
    )


def sync_interest_counts():
    """
    Batch POST our members' interest counts to each partner club.

    Aggregates ``ExternalEventInterest`` records per external event,
    grouped by source club, and sends a POST to each partner's
    ``/api/federation/interest/`` endpoint.
    """
    # Get all interest counts grouped by event and source club
    interests = (
        ExternalEventInterest.objects.values(
            "external_event__source_club",
            "external_event__external_id",
            "interest_level",
        )
        .annotate(count=Count("id"))
        .order_by("external_event__source_club")
    )

    # Group by club
    club_events = {}
    for row in interests:
        club_id = row["external_event__source_club"]
        event_id = row["external_event__external_id"]
        level = row["interest_level"]
        count = row["count"]

        if club_id not in club_events:
            club_events[club_id] = {}
        if event_id not in club_events[club_id]:
            club_events[club_id][event_id] = {}
        club_events[club_id][event_id][level] = count

    our_code = getattr(settings, "FEDERATION_OUR_CLUB_CODE", "")

    for club_id, events in club_events.items():
        try:
            club = FederatedClub.objects.get(pk=club_id, is_active=True)
        except FederatedClub.DoesNotExist:
            continue

        for event_id, counts in events.items():
            _post_interest_to_partner(club, event_id, counts, our_code)


def _post_interest_to_partner(club, event_id, counts, our_code):
    """
    POST interest counts for a single event to a partner club.
    """
    url = f"{club.base_url.rstrip('/')}/api/federation/interest/"

    body_data = {
        "event_id": event_id,
        "club_code": our_code,
        "counts": counts,
    }
    body_bytes = json.dumps(body_data).encode("utf-8")
    body_str = body_bytes.decode("utf-8")

    timestamp = datetime.now(timezone.utc).isoformat()
    signature = sign_request(
        secret_key=club.our_key_for_them,
        timestamp=timestamp,
        body=body_str,
    )

    headers = {
        "X-Federation-Key": club.api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "ClubCMS-Federation/1.0",
    }

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as response:
            result = json.loads(response.read().decode("utf-8"))
            logger.debug(
                "Posted interest to %s for event %s: %s",
                club.short_code, event_id, result,
            )
    except Exception as exc:
        logger.warning(
            "Failed to post interest to %s for event %s: %s",
            club.short_code, event_id, exc,
        )


def cleanup_past_events(days=90):
    """
    Remove external events older than *days* days.

    Parameters
    ----------
    days : int
        Number of days after which past events are deleted.
        Defaults to 90.

    Returns
    -------
    int
        Number of deleted events.
    """
    cutoff = dj_tz.now() - timedelta(days=days)
    deleted, _ = ExternalEvent.objects.filter(start_date__lt=cutoff).delete()
    logger.info("Cleaned up %d past external events (older than %d days)", deleted, days)
    return deleted


def _parse_datetime(value):
    """
    Parse an ISO 8601 datetime string into a timezone-aware datetime.

    Returns ``None`` on failure.
    """
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError, AttributeError):
        return None

"""
Federation API views.

Endpoints for partner clubs to consume our events and send interest counts.
All endpoints are HMAC-authenticated and rate-limited.
"""

import json
import logging
from datetime import date, timedelta

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from apps.federation.api.security import verify_request
from apps.federation.models import FederatedClub

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate-limit constants
# ---------------------------------------------------------------------------
FEDERATION_RATE_LIMIT = 60  # max requests per hour per partner
FEDERATION_RATE_WINDOW = 3600  # seconds


def _rate_limit_check(club):
    """
    Return True if the partner club has exceeded its rate limit.
    Uses Django cache with a per-club key.
    """
    cache_key = f"federation_rate_{club.pk}"
    current = cache.get(cache_key, 0)
    if current >= FEDERATION_RATE_LIMIT:
        return True
    cache.set(cache_key, current + 1, FEDERATION_RATE_WINDOW)
    return False


def _authenticate_partner(request):
    """
    Authenticate a federation API request.

    Reads X-Federation-Key, X-Timestamp, X-Signature headers,
    looks up the partner club, checks rate limits, and verifies
    the HMAC signature.

    Returns
    -------
    tuple[FederatedClub | None, JsonResponse | None]
        ``(club, None)`` on success, ``(None, error_response)`` on failure.
    """
    federation_key = request.headers.get("X-Federation-Key", "")
    timestamp = request.headers.get("X-Timestamp", "")
    signature = request.headers.get("X-Signature", "")

    if not federation_key or not timestamp or not signature:
        return None, JsonResponse(
            {"error": "Missing authentication headers"}, status=401
        )

    # Look up the partner by their public key
    try:
        club = FederatedClub.objects.get(
            api_key=federation_key,
            is_active=True,
            is_approved=True,
        )
    except FederatedClub.DoesNotExist:
        logger.warning("Federation auth failed: unknown key %s...", federation_key[:8])
        return None, JsonResponse(
            {"error": "Authentication failed"}, status=401
        )

    # Rate limit check
    if _rate_limit_check(club):
        logger.warning("Federation rate limit exceeded for %s", club.short_code)
        return None, JsonResponse(
            {"error": "Rate limit exceeded"}, status=429
        )

    # Verify HMAC signature
    # The partner signed using our_key_for_them as the shared secret.
    body = request.body.decode("utf-8") if request.body else ""
    if not verify_request(
        api_key=club.our_key_for_them,
        timestamp=timestamp,
        signature=signature,
        body=body,
    ):
        logger.warning("Federation HMAC verification failed for %s", club.short_code)
        return None, JsonResponse(
            {"error": "Authentication failed"}, status=401
        )

    return club, None


# ---------------------------------------------------------------------------
# Events API
# ---------------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class FederationEventsAPIView(View):
    """
    GET /api/federation/events/

    Returns our published events for an authenticated partner club.
    Query params:
        from_date (YYYY-MM-DD): only events starting on or after this date.
    """

    http_method_names = ["get"]

    def get(self, request):
        club, error = _authenticate_partner(request)
        if error:
            return error

        # Check that we are sharing events with this partner
        if not club.share_our_events:
            return JsonResponse(
                {"error": "Event sharing is not enabled for this partner"},
                status=403,
            )

        # Parse from_date filter
        from_date_str = request.GET.get("from_date", "")
        if from_date_str:
            try:
                from_date = date.fromisoformat(from_date_str)
            except ValueError:
                from_date = date.today() - timedelta(days=1)
        else:
            from_date = date.today() - timedelta(days=1)

        # Query published events
        from apps.website.models.pages import EventDetailPage

        events_qs = (
            EventDetailPage.objects.live()
            .public()
            .filter(start_date__date__gte=from_date)
            .order_by("start_date")
        )

        events_data = []
        for event in events_qs:
            # Parse coordinates if available
            lat = None
            lon = None
            if event.location_coordinates:
                parts = event.location_coordinates.split(",")
                if len(parts) == 2:
                    try:
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                    except (ValueError, IndexError):
                        pass

            # Build image URL
            image_url = ""
            if event.cover_image:
                try:
                    rendition = event.cover_image.get_rendition("fill-800x400")
                    image_url = request.build_absolute_uri(rendition.url)
                except Exception:
                    pass

            events_data.append(
                {
                    "id": str(event.pk),
                    "event_name": event.title,
                    "start_date": event.start_date.isoformat(),
                    "end_date": event.end_date.isoformat() if event.end_date else None,
                    "location_name": event.location_name,
                    "location_address": event.location_address,
                    "location_lat": lat,
                    "location_lon": lon,
                    "description": event.intro or "",
                    "event_status": "EventScheduled",
                    "image_url": image_url,
                    "detail_url": request.build_absolute_uri(event.url),
                }
            )

        our_name = getattr(settings, "FEDERATION_OUR_CLUB_NAME", "")
        our_code = getattr(settings, "FEDERATION_OUR_CLUB_CODE", "")
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")

        return JsonResponse(
            {
                "club": {
                    "name": our_name,
                    "code": our_code,
                    "url": base_url,
                },
                "events": events_data,
                "total": len(events_data),
                "last_updated": timezone.now().isoformat(),
            }
        )


# ---------------------------------------------------------------------------
# Interest API
# ---------------------------------------------------------------------------


@method_decorator(csrf_exempt, name="dispatch")
class FederationInterestAPIView(View):
    """
    POST /api/federation/interest/

    Receives interest counts from a partner club for one of our events.
    Body JSON:
        {
            "event_id": "<page_id>",
            "club_code": "PARTNER",
            "counts": {"interested": 5, "going": 3, "maybe": 2}
        }
    """

    http_method_names = ["post"]

    def post(self, request):
        club, error = _authenticate_partner(request)
        if error:
            return error

        # Parse JSON body
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        event_id = body.get("event_id")
        counts = body.get("counts", {})
        # Always use the authenticated partner's code, never trust client input
        club_code = club.short_code

        if not event_id:
            return JsonResponse({"error": "event_id is required"}, status=400)

        # Validate event exists
        from apps.website.models.pages import EventDetailPage

        try:
            EventDetailPage.objects.live().get(pk=event_id)
        except EventDetailPage.DoesNotExist:
            return JsonResponse({"error": "Event not found"}, status=404)

        # Store interest counts in cache (30-day TTL)
        cache_key = f"federation_interest_{event_id}_{club_code}"
        cache.set(
            cache_key,
            {
                "counts": counts,
                "club_code": club_code,
                "club_name": club.name,
                "updated_at": timezone.now().isoformat(),
            },
            timeout=60 * 60 * 24 * 30,
        )

        logger.info(
            "Received federation interest from %s for event %s: %s",
            club_code, event_id, counts,
        )

        return JsonResponse({"status": "ok", "received": True})

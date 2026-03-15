"""
Mutual Aid views.

Provides map view with geolocated search, helper detail, contact form,
contact unlock, access request handling, and a JSON API for helpers data.
"""

import logging

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from apps.mutual_aid.forms import AidRequestForm, GeoSearchForm
from apps.mutual_aid.geo import haversine_km, parse_coordinates
from apps.mutual_aid.models import (
    AidPrivacySettings,
    AidRequest,
    ContactUnlock,
    FederatedAidAccess,
    FederatedAidAccessRequest,
    FederatedHelper,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _parse_float_locale(value):
    """
    Parse a float from a GET parameter that might use comma as decimal
    separator (Italian/European locale).  ``45,6395418`` → ``45.6395418``.
    """
    if not value:
        raise ValueError("empty")
    # Replace comma with dot (only if there is exactly one comma and no dot)
    v = value.strip()
    if "," in v and "." not in v:
        v = v.replace(",", ".")
    return float(v)


def _is_active_member(user):
    """Check if user is an active club member (staff/superusers always pass)."""
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    return getattr(user, "is_active_member", False)


def _get_privacy(user):
    """Get or create AidPrivacySettings for a user."""
    settings, _ = AidPrivacySettings.objects.get_or_create(user=user)
    return settings


def _parse_helper_coords(helper):
    """Parse aid_coordinates from a ClubUser into (lat, lng) or None."""
    return parse_coordinates(getattr(helper, "aid_coordinates", ""))


def _annotate_distances(helpers, user_lat, user_lng):
    """
    Add ``distance_km`` to each helper dict. Return sorted list.

    ``helpers`` is a list of dicts with optional ``lat`` and ``lng`` keys.
    """
    for h in helpers:
        lat = h.get("lat")
        lng = h.get("lng")
        if lat is not None and lng is not None:
            h["distance_km"] = round(haversine_km(user_lat, user_lng, lat, lng), 1)
        else:
            h["distance_km"] = None
    return sorted(helpers, key=lambda h: (h["distance_km"] is None, h["distance_km"] or 0))


class MutualAidMapView(LoginRequiredMixin, ListView):
    """
    Map view showing available helpers with optional geo-search.

    Displays local helpers and (if federation is enabled)
    federated helpers from partner clubs.
    """

    template_name = "mutual_aid/mutual_aid_page.html"
    context_object_name = "helpers"
    paginate_by = 20

    def get_paginate_by(self, queryset):
        # Disable pagination when geo-search is active (results are filtered)
        if self._is_geo_search():
            return None
        return self.paginate_by

    def _is_geo_search(self):
        """True if lat/lng are present AND parseable as floats."""
        try:
            _parse_float_locale(self.request.GET.get("lat", ""))
            _parse_float_locale(self.request.GET.get("lng", ""))
            return True
        except (ValueError, TypeError):
            return False

    def _get_search_params(self):
        """Parse and validate geo-search GET parameters."""
        try:
            lat = _parse_float_locale(self.request.GET.get("lat", ""))
            lng = _parse_float_locale(self.request.GET.get("lng", ""))
        except (ValueError, TypeError):
            return None, None, 50
        try:
            radius = int(self.request.GET.get("radius", "50"))
            radius = max(5, min(500, radius))
        except (ValueError, TypeError):
            radius = 50
        return lat, lng, radius

    def get_queryset(self):
        qs = (
            User.objects.filter(aid_available=True, is_active=True)
            .exclude(aid_location_city="")
            .order_by("aid_location_city")
        )

        if not self._is_geo_search():
            return qs

        user_lat, user_lng, radius = self._get_search_params()
        if user_lat is None:
            return qs

        # Filter and sort by distance in Python (no PostGIS)
        helpers_with_distance = []
        for helper in qs:
            coords = _parse_helper_coords(helper)
            if coords:
                dist = haversine_km(user_lat, user_lng, coords[0], coords[1])
                if dist <= radius:
                    helper.distance_km = round(dist, 1)
                    helpers_with_distance.append(helper)
            else:
                # Helpers without coordinates: include but at the end
                helper.distance_km = None
                helpers_with_distance.append(helper)

        helpers_with_distance.sort(
            key=lambda h: (h.distance_km is None, h.distance_km or 0)
        )
        return helpers_with_distance

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_active_member"] = _is_active_member(self.request.user)

        # Geo search form
        geo_form = GeoSearchForm(self.request.GET or None)
        context["geo_form"] = geo_form

        user_lat, user_lng, radius = self._get_search_params()
        context["search_active"] = self._is_geo_search()
        context["search_lat"] = user_lat
        context["search_lng"] = user_lng
        context["search_radius"] = radius
        context["search_location"] = self.request.GET.get("location", "")

        # Federated helpers
        from apps.mutual_aid.models import MutualAidPage
        aid_page = MutualAidPage.objects.live().first()
        context["aid_page"] = aid_page

        federated_helpers = []
        if aid_page and aid_page.enable_federation:
            fed_qs = FederatedHelper.objects.filter(
                is_approved=True,
                is_hidden=False,
                source_club__is_active=True,
                source_club__is_approved=True,
            ).select_related("source_club")

            for fh in fed_qs:
                entry = {
                    "display_name": fh.display_name,
                    "city": fh.city,
                    "radius_km": fh.radius_km,
                    "notes": fh.notes,
                    "photo_url": fh.photo_url,
                    "source_club_name": fh.source_club.name,
                    "source_club_code": fh.source_club.short_code,
                    "source_club_url": fh.source_club.base_url,
                    "lat": fh.latitude,
                    "lng": fh.longitude,
                    "is_federated": True,
                }

                if self._is_geo_search() and user_lat is not None:
                    if fh.latitude and fh.longitude:
                        dist = haversine_km(user_lat, user_lng, fh.latitude, fh.longitude)
                        if dist <= radius:
                            entry["distance_km"] = round(dist, 1)
                            federated_helpers.append(entry)
                    else:
                        entry["distance_km"] = None
                        federated_helpers.append(entry)
                else:
                    entry["distance_km"] = None
                    federated_helpers.append(entry)

            federated_helpers.sort(
                key=lambda h: (h["distance_km"] is None, h["distance_km"] or 0)
            )

        context["federated_helpers"] = federated_helpers

        # Build unified list for template, sorted by distance
        helpers = context.get("helpers") or context.get("object_list") or []
        all_helpers = []
        for h in helpers:
            all_helpers.append({
                "type": "local",
                "pk": h.pk,
                "display_name": h.get_visible_name(),
                "city": h.aid_location_city,
                "radius_km": h.aid_radius_km,
                "notes": h.aid_notes,
                "distance_km": getattr(h, "distance_km", None),
            })
        for fh in federated_helpers:
            all_helpers.append({
                "type": "federated",
                "display_name": fh["display_name"],
                "city": fh["city"],
                "radius_km": fh["radius_km"],
                "notes": fh.get("notes", ""),
                "distance_km": fh.get("distance_km"),
                "source_club_name": fh.get("source_club_name", ""),
                "source_club_url": fh.get("source_club_url", ""),
            })

        # Sort: helpers with distance first (ascending), then without
        all_helpers.sort(
            key=lambda h: (h["distance_km"] is None, h["distance_km"] or 0)
        )
        context["all_helpers"] = all_helpers

        context["local_count"] = len(helpers) if isinstance(helpers, list) else helpers.count() if hasattr(helpers, "count") else 0
        context["federated_count"] = len(federated_helpers)
        context["total_count"] = context["local_count"] + context["federated_count"]

        return context


class HelperDetailView(LoginRequiredMixin, View):
    """
    Detail view for a single helper.

    Shows helper info according to their privacy settings.
    """

    def get(self, request, pk):
        from apps.mutual_aid.models import MutualAidPage

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)
        privacy = _get_privacy(helper)
        is_member = _is_active_member(request.user)
        aid_page = MutualAidPage.objects.live().first()

        context = {
            "helper": helper,
            "privacy": privacy,
            "is_active_member": is_member,
            "aid_page": aid_page,
        }

        return render(request, "mutual_aid/helper_card.html", context)


class ContactFormView(LoginRequiredMixin, View):
    """
    Send an aid request to a helper.
    """

    def get(self, request, pk):
        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)
        form = AidRequestForm(initial={
            "requester_name": request.user.get_visible_name(),
            "requester_email": request.user.email,
            "requester_phone": request.user.mobile or request.user.phone,
        })

        return render(request, "mutual_aid/contact_form.html", {
            "form": form,
            "helper": helper,
        })

    def post(self, request, pk):
        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)
        form = AidRequestForm(request.POST)

        if form.is_valid():
            aid_request = form.save(commit=False)
            aid_request.helper = helper
            aid_request.requester_user = request.user
            aid_request.save()

            try:
                from apps.notifications.services import create_notification

                create_notification(
                    notification_type="mutual_aid_request",
                    title=f"New aid request from {aid_request.requester_name}",
                    body=(
                        f"{aid_request.requester_name} needs help: "
                        f"{aid_request.get_issue_type_display()}"
                    ),
                    url=reverse("mutual_aid:helper_detail", kwargs={"pk": helper.pk}),
                    recipients=User.objects.filter(pk=helper.pk),
                    content_object=aid_request,
                )
            except Exception:
                logger.exception("Failed to send aid request notification")

            messages.success(request, _("Your help request has been sent."))
            return HttpResponseRedirect(
                reverse("mutual_aid:helper_detail", kwargs={"pk": helper.pk})
            )

        return render(request, "mutual_aid/contact_form.html", {
            "form": form,
            "helper": helper,
        })


class ContactUnlockView(LoginRequiredMixin, View):
    """Unlock a helper's contact information for a federated user."""

    http_method_names = ["post"]

    def post(self, request, pk):
        if _is_active_member(request.user):
            return HttpResponseRedirect(
                reverse("mutual_aid:contact_form", kwargs={"pk": pk})
            )

        federated_access_id = request.session.get("federated_access_id")
        if not federated_access_id:
            return HttpResponseForbidden("Federation access required")

        try:
            access = FederatedAidAccess.objects.get(
                pk=federated_access_id,
                is_active=True,
                access_level="contact",
            )
        except FederatedAidAccess.DoesNotExist:
            return HttpResponseForbidden("Invalid federation access")

        if access.expires_at and access.expires_at < timezone.now():
            return HttpResponseForbidden("Federation access has expired")

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)

        if not ContactUnlock.can_unlock(access):
            return render(request, "mutual_aid/limit_reached.html", {
                "helper": helper,
                "unlock_limit": ContactUnlock.UNLOCK_LIMIT,
                "window_days": ContactUnlock.UNLOCK_WINDOW_DAYS,
            })

        ContactUnlock.objects.get_or_create(
            federated_access=access,
            helper=helper,
        )

        access.contacts_unlocked = ContactUnlock.objects.filter(
            federated_access=access
        ).count()
        access.save(update_fields=["contacts_unlocked"])

        return HttpResponseRedirect(
            reverse("mutual_aid:helper_detail", kwargs={"pk": pk})
        )


class RequestAccessView(LoginRequiredMixin, View):
    """Handle access requests from federated users."""

    def get(self, request):
        return render(request, "mutual_aid/access_request.html")

    def post(self, request):
        federated_access_id = request.session.get("federated_access_id")
        if not federated_access_id:
            return HttpResponseForbidden("Federation access required")

        try:
            access = FederatedAidAccess.objects.get(pk=federated_access_id)
        except FederatedAidAccess.DoesNotExist:
            return HttpResponseForbidden("Invalid federation access")

        if access.expires_at and access.expires_at < timezone.now():
            return HttpResponseForbidden("Federation access has expired")

        message = request.POST.get("message", "").strip()[:1000]

        existing = FederatedAidAccessRequest.objects.filter(
            federated_access=access,
            status="pending",
        ).exists()

        if not existing:
            FederatedAidAccessRequest.objects.create(
                federated_access=access,
                message=message,
            )

            try:
                from apps.notifications.services import create_notification

                admins = User.objects.filter(is_staff=True, is_active=True)
                create_notification(
                    notification_type="aid_request",
                    title="New federation access request",
                    body=(
                        f"{access.external_display_name} from "
                        f"{access.source_club.name} is requesting "
                        f"access to the mutual aid directory."
                    ),
                    url="/admin/",
                    recipients=admins,
                )
            except Exception:
                logger.exception("Failed to send access request notification")

        messages.success(request, _("Your access request has been submitted."))
        return HttpResponseRedirect(reverse("mutual_aid:map"))


class HelpersAPIView(LoginRequiredMixin, View):
    """
    JSON API for helpers data (used by the map JavaScript).

    Accepts optional geo-search params: ?lat=X&lng=Y&radius=Z
    Returns local helpers and federated helpers with distance info.
    """

    http_method_names = ["get"]

    def get(self, request):
        if not _is_active_member(request.user):
            return JsonResponse({"error": "Active membership required"}, status=403)

        # Parse geo params
        try:
            user_lat = _parse_float_locale(request.GET.get("lat", ""))
            user_lng = _parse_float_locale(request.GET.get("lng", ""))
        except (ValueError, TypeError):
            user_lat = user_lng = None
        try:
            radius = int(request.GET.get("radius", "50"))
            radius = max(5, min(500, radius))
        except (ValueError, TypeError):
            radius = 50

        has_geo = user_lat is not None and user_lng is not None

        # Local helpers
        helpers = User.objects.filter(
            aid_available=True,
            is_active=True,
        ).exclude(aid_location_city="")

        data = []
        for helper in helpers:
            privacy = _get_privacy(helper)

            helper_data = {
                "id": helper.pk,
                "type": "local",
                "display_name": helper.get_visible_name(viewer=request.user),
                "city": helper.aid_location_city,
                "radius_km": helper.aid_radius_km,
                "notes": helper.aid_notes if privacy.show_bio_on_aid else "",
            }

            if privacy.show_exact_location and helper.aid_coordinates:
                coords = parse_coordinates(helper.aid_coordinates)
                if coords:
                    helper_data["lat"] = coords[0]
                    helper_data["lon"] = coords[1]

                    if has_geo:
                        dist = haversine_km(user_lat, user_lng, coords[0], coords[1])
                        helper_data["distance_km"] = round(dist, 1)
                        if dist > radius:
                            continue  # outside search radius

            if privacy.show_photo_on_aid and helper.photo:
                try:
                    rendition = helper.photo.get_rendition("fill-80x80")
                    helper_data["photo_url"] = request.build_absolute_uri(rendition.url)
                except Exception:
                    pass

            data.append(helper_data)

        # Federated helpers
        federated_data = []
        from apps.mutual_aid.models import MutualAidPage
        aid_page = MutualAidPage.objects.live().first()

        if aid_page and aid_page.enable_federation:
            fed_qs = FederatedHelper.objects.filter(
                is_approved=True,
                is_hidden=False,
                source_club__is_active=True,
                source_club__is_approved=True,
            ).select_related("source_club")

            for fh in fed_qs:
                fh_data = {
                    "id": str(fh.pk),
                    "type": "federated",
                    "display_name": fh.display_name,
                    "city": fh.city,
                    "radius_km": fh.radius_km,
                    "notes": fh.notes,
                    "source_club": fh.source_club.name,
                    "source_club_code": fh.source_club.short_code,
                }

                if fh.latitude and fh.longitude:
                    fh_data["lat"] = fh.latitude
                    fh_data["lon"] = fh.longitude

                    if has_geo:
                        dist = haversine_km(user_lat, user_lng, fh.latitude, fh.longitude)
                        fh_data["distance_km"] = round(dist, 1)
                        if dist > radius:
                            continue

                if fh.photo_url:
                    fh_data["photo_url"] = fh.photo_url

                federated_data.append(fh_data)

        # Sort by distance if geo-search active
        if has_geo:
            data.sort(key=lambda h: h.get("distance_km", 99999))
            federated_data.sort(key=lambda h: h.get("distance_km", 99999))

        return JsonResponse({
            "helpers": data,
            "federated_helpers": federated_data,
            "total": len(data) + len(federated_data),
        })

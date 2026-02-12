"""
Mutual Aid views.

Provides map view, helper detail, contact form, contact unlock,
access request handling, and a JSON API for helpers data.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView

from apps.mutual_aid.forms import AidRequestForm
from apps.mutual_aid.models import (
    AidPrivacySettings,
    AidRequest,
    ContactUnlock,
    FederatedAidAccess,
    FederatedAidAccessRequest,
)

logger = logging.getLogger(__name__)
User = get_user_model()


def _is_active_member(user):
    """Check if user is an active club member."""
    return getattr(user, "is_active_member", False)


def _get_privacy(user):
    """Get or create AidPrivacySettings for a user."""
    settings, _ = AidPrivacySettings.objects.get_or_create(user=user)
    return settings


class MutualAidMapView(LoginRequiredMixin, ListView):
    """
    Map view showing available helpers.

    Displays a list of helpers who have ``aid_available=True``
    with optional radius filtering.

    Template: ``mutual_aid/mutual_aid_page.html``
    URL: ``/mutuo-soccorso/``
    """

    template_name = "mutual_aid/mutual_aid_page.html"
    context_object_name = "helpers"
    paginate_by = 20

    def get_queryset(self):
        return (
            User.objects.filter(
                aid_available=True,
                is_active=True,
            )
            .exclude(aid_location_city="")
            .order_by("aid_location_city")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_active_member"] = _is_active_member(self.request.user)
        return context


class HelperDetailView(LoginRequiredMixin, View):
    """
    Detail view for a single helper.

    Shows helper info according to their privacy settings.

    Template: ``mutual_aid/helper_card.html``
    URL: ``/mutuo-soccorso/helper/<int:pk>/``
    """

    def get(self, request, pk):
        if not _is_active_member(request.user):
            return HttpResponseForbidden(_("Active membership required."))

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)
        privacy = _get_privacy(helper)

        context = {
            "helper": helper,
            "privacy": privacy,
            "is_active_member": _is_active_member(request.user),
        }

        return render(request, "mutual_aid/helper_card.html", context)


class ContactFormView(LoginRequiredMixin, View):
    """
    Send an aid request to a helper.

    GET: Display the form.
    POST: Validate and create the AidRequest.

    Template: ``mutual_aid/contact_form.html``
    URL: ``/mutuo-soccorso/helper/<int:pk>/contact/``
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

            # Send notification to helper
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

            return HttpResponseRedirect(
                reverse("mutual_aid:helper_detail", kwargs={"pk": helper.pk})
            )

        return render(request, "mutual_aid/contact_form.html", {
            "form": form,
            "helper": helper,
        })


class ContactUnlockView(LoginRequiredMixin, View):
    """
    Unlock a helper's contact information for a federated user.

    Limited to 3 unlocks per 30-day period.

    POST-only.
    URL: ``/mutuo-soccorso/helper/<int:pk>/unlock/``
    """

    http_method_names = ["post"]

    def post(self, request, pk):
        # This view is for federated access only.
        # For now, redirect local members to the contact form.
        if _is_active_member(request.user):
            return HttpResponseRedirect(
                reverse("mutual_aid:contact_form", kwargs={"pk": pk})
            )

        # Look up federated access
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

        # Enforce expiry
        if access.expires_at and access.expires_at < timezone.now():
            return HttpResponseForbidden("Federation access has expired")

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)

        # Check unlock limit
        if not ContactUnlock.can_unlock(access):
            return render(request, "mutual_aid/limit_reached.html", {
                "helper": helper,
                "unlock_limit": ContactUnlock.UNLOCK_LIMIT,
                "window_days": ContactUnlock.UNLOCK_WINDOW_DAYS,
            })

        # Create or get unlock
        ContactUnlock.objects.get_or_create(
            federated_access=access,
            helper=helper,
        )

        # Increment counter
        access.contacts_unlocked = ContactUnlock.objects.filter(
            federated_access=access
        ).count()
        access.save(update_fields=["contacts_unlocked"])

        return HttpResponseRedirect(
            reverse("mutual_aid:helper_detail", kwargs={"pk": pk})
        )


class RequestAccessView(LoginRequiredMixin, View):
    """
    Handle access requests from federated users.

    GET: Show the request form.
    POST: Create the access request.

    Template: ``mutual_aid/access_request.html``
    URL: ``/mutuo-soccorso/request-access/``
    """

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

        # Enforce expiry
        if access.expires_at and access.expires_at < timezone.now():
            return HttpResponseForbidden("Federation access has expired")

        message = request.POST.get("message", "").strip()[:1000]

        # Prevent duplicate pending requests
        existing = FederatedAidAccessRequest.objects.filter(
            federated_access=access,
            status="pending",
        ).exists()

        if not existing:
            FederatedAidAccessRequest.objects.create(
                federated_access=access,
                message=message,
            )

            # Notify admins
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

        return HttpResponseRedirect(reverse("mutual_aid:map"))


class HelpersAPIView(LoginRequiredMixin, View):
    """
    JSON API for helpers data (used by the map JavaScript).

    Returns a list of helpers with their approximate locations
    (city-level only unless privacy settings allow exact coords).

    GET /mutuo-soccorso/api/helpers/
    """

    http_method_names = ["get"]

    def get(self, request):
        if not _is_active_member(request.user):
            return JsonResponse({"error": "Active membership required"}, status=403)

        helpers = User.objects.filter(
            aid_available=True,
            is_active=True,
        ).exclude(aid_location_city="")

        data = []
        for helper in helpers:
            privacy = _get_privacy(helper)

            helper_data = {
                "id": helper.pk,
                "display_name": helper.get_visible_name(viewer=request.user),
                "city": helper.aid_location_city,
                "radius_km": helper.aid_radius_km,
                "notes": helper.aid_notes if privacy.show_bio_on_aid else "",
            }

            # Include coordinates only if privacy allows
            if privacy.show_exact_location and helper.aid_coordinates:
                parts = helper.aid_coordinates.split(",")
                if len(parts) == 2:
                    try:
                        helper_data["lat"] = float(parts[0].strip())
                        helper_data["lon"] = float(parts[1].strip())
                    except (ValueError, IndexError):
                        pass

            if privacy.show_photo_on_aid and helper.photo:
                try:
                    rendition = helper.photo.get_rendition("fill-80x80")
                    helper_data["photo_url"] = request.build_absolute_uri(rendition.url)
                except Exception:
                    pass

            data.append(helper_data)

        return JsonResponse({"helpers": data, "total": len(data)})

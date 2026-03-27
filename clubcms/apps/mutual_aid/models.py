"""
Mutual Aid models.

Includes the Wagtail page model (MutualAidPage) with RoutablePageMixin,
privacy settings, aid requests, federated access management, and
contact unlock tracking.
"""

import logging
import uuid

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponseForbidden, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# StreamField blocks for emergency contacts
# ---------------------------------------------------------------------------
from wagtail.blocks import CharBlock, StructBlock


class EmergencyContactBlock(StructBlock):
    """A single emergency contact entry."""

    name = CharBlock(max_length=100, label=_("Name"))
    role = CharBlock(max_length=100, blank=True, label=_("Role"))
    phone = CharBlock(max_length=30, label=_("Phone"))

    class Meta:
        icon = "warning"
        label = _("Emergency Contact")


# ---------------------------------------------------------------------------
# MutualAidPage (Wagtail Page)
# ---------------------------------------------------------------------------


class MutualAidPage(RoutablePageMixin, Page):
    """
    Wagtail page for the mutual aid section.

    Displays a map of available helpers, a list of helpers,
    and emergency contacts. Sub-routes handle helper detail,
    contact form, unlock, access requests, and JSON API.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Introductory text displayed above the helpers map."),
    )
    body = StreamField(
        [
            ("emergency_contact", EmergencyContactBlock()),
        ],
        blank=True,
        use_json_field=True,
        verbose_name=_("Emergency contacts"),
        help_text=_("Contatti di emergenza configurabili dall'admin."),
    )
    default_radius_km = models.PositiveIntegerField(
        default=50,
        verbose_name=_("Default map radius (km)"),
        help_text=_("Default radius for the helpers map view."),
    )
    enable_federation = models.BooleanField(
        default=False,
        verbose_name=_("Enable federation"),
        help_text=_("Allow approved partner clubs to see our helpers."),
    )

    # Wagtail config
    parent_page_types = ["wagtailcore.Page", "website.HomePage"]
    subpage_types = []
    template = "mutual_aid/mutual_aid_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("default_radius_km"),
                FieldPanel("enable_federation"),
            ],
            heading=_("Settings"),
        ),
    ]

    class Meta:
        verbose_name = _("Mutual Aid Page")
        verbose_name_plural = _("Mutual Aid Pages")

    # ------------------------------------------------------------------
    # Helpers (private)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_float_locale(value):
        if not value:
            raise ValueError("empty")
        v = value.strip()
        if "," in v and "." not in v:
            v = v.replace(",", ".")
        return float(v)

    @staticmethod
    def _is_active_member(user):
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True
        return getattr(user, "is_active_member", False)

    @staticmethod
    def _get_privacy(user):
        privacy, _ = AidPrivacySettings.objects.get_or_create(user=user)
        return privacy

    def _parse_geo_params(self, request):
        try:
            lat = self._parse_float_locale(request.GET.get("lat", ""))
            lng = self._parse_float_locale(request.GET.get("lng", ""))
        except (ValueError, TypeError):
            return None, None, self.default_radius_km
        try:
            radius = int(request.GET.get("radius", str(self.default_radius_km)))
            radius = max(5, min(500, radius))
        except (ValueError, TypeError):
            radius = self.default_radius_km
        return lat, lng, radius

    def _has_geo_search(self, request):
        try:
            self._parse_float_locale(request.GET.get("lat", ""))
            self._parse_float_locale(request.GET.get("lng", ""))
            return True
        except (ValueError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Route: landing / map  (^$)
    # ------------------------------------------------------------------

    @route(r"^$")
    @method_decorator(login_required)
    def map_view(self, request):
        from apps.mutual_aid.forms import GeoSearchForm
        from apps.mutual_aid.geo import haversine_km, parse_coordinates

        User = get_user_model()
        is_geo = self._has_geo_search(request)
        user_lat, user_lng, radius = self._parse_geo_params(request)

        # Base queryset
        qs = (
            User.objects.filter(aid_available=True, is_active=True)
            .exclude(aid_location_city="")
            .order_by("aid_location_city")
        )

        helpers_list = list(qs)
        if is_geo and user_lat is not None:
            filtered = []
            for helper in helpers_list:
                coords = parse_coordinates(getattr(helper, "aid_coordinates", ""))
                if coords:
                    dist = haversine_km(user_lat, user_lng, coords[0], coords[1])
                    if dist <= radius:
                        helper.distance_km = round(dist, 1)
                        filtered.append(helper)
                else:
                    helper.distance_km = None
                    filtered.append(helper)
            filtered.sort(key=lambda h: (h.distance_km is None, h.distance_km or 0))
            helpers_list = filtered

        # Federated helpers
        federated_helpers = []
        if self.enable_federation:
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
                if is_geo and user_lat is not None:
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

        # Build unified list
        all_helpers = []
        for h in helpers_list:
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
        all_helpers.sort(
            key=lambda h: (h["distance_km"] is None, h["distance_km"] or 0)
        )

        context = {
            "helpers": helpers_list,
            "all_helpers": all_helpers,
            "federated_helpers": federated_helpers,
            "is_active_member": self._is_active_member(request.user),
            "geo_form": GeoSearchForm(request.GET or None),
            "search_active": is_geo,
            "search_lat": user_lat,
            "search_lng": user_lng,
            "search_radius": radius,
            "search_location": request.GET.get("location", ""),
            "aid_page": self,
            "local_count": len(helpers_list),
            "federated_count": len(federated_helpers),
            "total_count": len(helpers_list) + len(federated_helpers),
        }

        return self.render(
            request,
            template="mutual_aid/mutual_aid_page.html",
            context_overrides=context,
        )

    # ------------------------------------------------------------------
    # Route: helper detail
    # ------------------------------------------------------------------

    @route(r"^helper/(?P<pk>\d+)/$", name="helper_detail")
    @method_decorator(login_required)
    def helper_detail_view(self, request, pk):
        User = get_user_model()
        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)
        privacy = self._get_privacy(helper)

        context = {
            "helper": helper,
            "privacy": privacy,
            "is_active_member": self._is_active_member(request.user),
            "aid_page": self,
            "page": self,
        }
        return render(request, "mutual_aid/helper_card.html", context)

    # ------------------------------------------------------------------
    # Route: contact form
    # ------------------------------------------------------------------

    @route(r"^helper/(?P<pk>\d+)/contact/$", name="contact_form")
    @method_decorator(login_required)
    def contact_form_view(self, request, pk):
        from apps.mutual_aid.forms import AidRequestForm

        User = get_user_model()

        if not self._is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        helper = get_object_or_404(User, pk=pk, aid_available=True, is_active=True)

        if request.method == "POST":
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
                        url=self.url + self.reverse_subpage(
                            "helper_detail", kwargs={"pk": helper.pk}
                        ),
                        recipients=User.objects.filter(pk=helper.pk),
                        content_object=aid_request,
                    )
                except Exception:
                    logger.exception("Failed to send aid request notification")

                messages.success(request, _("Your help request has been sent."))
                return HttpResponseRedirect(
                    self.url + self.reverse_subpage(
                        "helper_detail", kwargs={"pk": helper.pk}
                    )
                )
        else:
            form = AidRequestForm(initial={
                "requester_name": request.user.get_visible_name(),
                "requester_email": request.user.email,
                "requester_phone": request.user.mobile or request.user.phone,
            })

        return render(request, "mutual_aid/contact_form.html", {
            "form": form,
            "helper": helper,
            "page": self,
        })

    # ------------------------------------------------------------------
    # Route: contact unlock (federated users)
    # ------------------------------------------------------------------

    @route(r"^helper/(?P<pk>\d+)/unlock/$", name="unlock_contact")
    @method_decorator(login_required)
    def unlock_contact_view(self, request, pk):
        User = get_user_model()

        if request.method != "POST":
            return HttpResponseRedirect(
                self.url + self.reverse_subpage("helper_detail", kwargs={"pk": pk})
            )

        if self._is_active_member(request.user):
            return HttpResponseRedirect(
                self.url + self.reverse_subpage("contact_form", kwargs={"pk": pk})
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
                "page": self,
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
            self.url + self.reverse_subpage("helper_detail", kwargs={"pk": pk})
        )

    # ------------------------------------------------------------------
    # Route: access request (federated users)
    # ------------------------------------------------------------------

    @route(r"^request-access/$", name="request_access")
    @method_decorator(login_required)
    def access_request_view(self, request):
        User = get_user_model()

        if request.method == "POST":
            federated_access_id = request.session.get("federated_access_id")
            if not federated_access_id:
                return HttpResponseForbidden("Federation access required")

            try:
                access = FederatedAidAccess.objects.get(pk=federated_access_id)
            except FederatedAidAccess.DoesNotExist:
                return HttpResponseForbidden("Invalid federation access")

            if access.expires_at and access.expires_at < timezone.now():
                return HttpResponseForbidden("Federation access has expired")

            message_text = request.POST.get("message", "").strip()[:1000]

            existing = FederatedAidAccessRequest.objects.filter(
                federated_access=access,
                status="pending",
            ).exists()

            if not existing:
                FederatedAidAccessRequest.objects.create(
                    federated_access=access,
                    message=message_text,
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
            return HttpResponseRedirect(self.url)

        return render(request, "mutual_aid/access_request.html", {
            "page": self,
        })

    # ------------------------------------------------------------------
    # Route: JSON API for map JS
    # ------------------------------------------------------------------

    @route(r"^api/helpers/$", name="helpers_api")
    @method_decorator(login_required)
    def helpers_api_view(self, request):
        from apps.mutual_aid.geo import haversine_km, parse_coordinates

        User = get_user_model()

        if not self._is_active_member(request.user):
            return JsonResponse({"error": "Active membership required"}, status=403)

        try:
            user_lat = self._parse_float_locale(request.GET.get("lat", ""))
            user_lng = self._parse_float_locale(request.GET.get("lng", ""))
        except (ValueError, TypeError):
            user_lat = user_lng = None
        try:
            radius = int(request.GET.get("radius", str(self.default_radius_km)))
            radius = max(5, min(500, radius))
        except (ValueError, TypeError):
            radius = self.default_radius_km

        has_geo = user_lat is not None and user_lng is not None

        helpers = User.objects.filter(
            aid_available=True,
            is_active=True,
        ).exclude(aid_location_city="")

        data = []
        for helper in helpers:
            privacy = self._get_privacy(helper)

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
                            continue

            if privacy.show_photo_on_aid and helper.photo:
                try:
                    rendition = helper.photo.get_rendition("fill-80x80")
                    helper_data["photo_url"] = request.build_absolute_uri(rendition.url)
                except Exception:
                    pass

            data.append(helper_data)

        federated_data = []
        if self.enable_federation:
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

        if has_geo:
            data.sort(key=lambda h: h.get("distance_km", 99999))
            federated_data.sort(key=lambda h: h.get("distance_km", 99999))

        return JsonResponse({
            "helpers": data,
            "federated_helpers": federated_data,
            "total": len(data) + len(federated_data),
        })


# ---------------------------------------------------------------------------
# AidPrivacySettings (per-user privacy for mutual aid)
# ---------------------------------------------------------------------------


class AidPrivacySettings(models.Model):
    """
    Per-user privacy settings for the mutual aid system.

    Controls what personal information is visible to other members
    and to federated partner clubs.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aid_privacy",
        help_text=_("Utente a cui si applicano le impostazioni privacy."),
    )
    show_phone_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show phone number"),
        help_text=_("Mostra il telefono fisso nella scheda aiuto."),
    )
    show_mobile_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show mobile number"),
        help_text=_("Mostra il cellulare nella scheda aiuto."),
    )
    show_whatsapp_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show WhatsApp availability"),
        help_text=_("Mostra la disponibilità WhatsApp."),
    )
    show_email_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show email address"),
        help_text=_("Mostra l'email nella scheda aiuto."),
    )
    show_exact_location = models.BooleanField(
        default=False,
        verbose_name=_("Show exact location"),
        help_text=_("If disabled, only the city name is shown."),
    )
    show_photo_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show profile photo"),
        help_text=_("Mostra la foto profilo nella scheda aiuto."),
    )
    show_bio_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show bio"),
        help_text=_("Mostra la bio nella scheda aiuto."),
    )
    show_hours_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show availability hours"),
        help_text=_("Mostra gli orari di disponibilità."),
    )

    class Meta:
        verbose_name = _("Aid Privacy Settings")
        verbose_name_plural = _("Aid Privacy Settings")

    def __str__(self):
        return f"Aid privacy for {self.user}"


# ---------------------------------------------------------------------------
# AidRequest
# ---------------------------------------------------------------------------


class AidRequest(models.Model):
    """
    A request for help from a member or federated user.
    """

    URGENCY_CHOICES = [
        ("low", _("Low - can wait")),
        ("medium", _("Medium - within a day")),
        ("high", _("High - urgent")),
        ("emergency", _("Emergency - immediate")),
    ]

    STATUS_CHOICES = [
        ("open", _("Open")),
        ("accepted", _("Accepted")),
        ("in_progress", _("In progress")),
        ("resolved", _("Resolved")),
        ("cancelled", _("Cancelled")),
    ]

    ISSUE_TYPE_CHOICES = [
        ("breakdown", _("Breakdown")),
        ("flat_tire", _("Flat tire")),
        ("fuel", _("Out of fuel")),
        ("accident", _("Accident")),
        ("tow", _("Need towing")),
        ("tools", _("Need tools")),
        ("transport", _("Need transport")),
        ("accommodation", _("Need accommodation")),
        ("other", _("Other")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="aid_requests_received",
        verbose_name=_("Helper"),
        help_text=_("Soccorritore a cui è indirizzata la richiesta."),
    )
    requester_name = models.CharField(
        max_length=100,
        verbose_name=_("Requester name"),
        help_text=_("Nome di chi richiede aiuto."),
    )
    requester_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Requester phone"),
        help_text=_("Telefono di chi richiede aiuto."),
    )
    requester_email = models.EmailField(
        blank=True,
        verbose_name=_("Requester email"),
        help_text=_("Email di chi richiede aiuto."),
    )
    requester_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aid_requests_sent",
        verbose_name=_("Requester (if member)"),
        help_text=_("Socio richiedente (se autenticato)."),
    )

    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES,
        default="other",
        verbose_name=_("Issue type"),
        help_text=_("Tipo di problema riscontrato."),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Describe what you need help with."),
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Location"),
        help_text=_("Where are you? Address or coordinates."),
    )
    urgency = models.CharField(
        max_length=20,
        choices=URGENCY_CHOICES,
        default="medium",
        verbose_name=_("Urgency"),
        help_text=_("Livello di urgenza della richiesta."),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name=_("Status"),
        help_text=_("Stato corrente della richiesta di aiuto."),
    )

    # Federation fields
    is_from_federation = models.BooleanField(
        default=False,
        verbose_name=_("From federation"),
        help_text=_("La richiesta proviene da un club federato."),
    )
    federation_access = models.ForeignKey(
        "mutual_aid.FederatedAidAccess",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aid_requests",
        verbose_name=_("Federation access"),
        help_text=_("Accesso federato che ha generato la richiesta."),
    )

    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data e ora di invio della richiesta."),
    )
    updated_at = models.DateTimeField(auto_now=True,
        help_text=_("Data e ora dell'ultimo aggiornamento."),
    )

    class Meta:
        verbose_name = _("Aid Request")
        verbose_name_plural = _("Aid Requests")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["helper"]),
        ]

    def __str__(self):
        return f"{self.issue_type} - {self.requester_name} ({self.status})"


# ---------------------------------------------------------------------------
# FederatedAidAccess
# ---------------------------------------------------------------------------


class FederatedAidAccess(models.Model):
    """
    Tracks a federated user's access to the mutual aid helpers list.

    Created when a partner club grants one of their members access
    to our helpers directory.
    """

    ACCESS_LEVEL_CHOICES = [
        ("view_list", _("View helpers list only")),
        ("contact", _("Can contact helpers")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_club = models.ForeignKey(
        "federation.FederatedClub",
        on_delete=models.CASCADE,
        related_name="aid_access_grants",
        verbose_name=_("Source club"),
        help_text=_("Club federato che ha concesso l'accesso."),
    )
    external_user_id = models.CharField(
        max_length=100,
        verbose_name=_("External user ID"),
        help_text=_("ID dell'utente nel sistema del club partner."),
    )
    external_display_name = models.CharField(
        max_length=100,
        verbose_name=_("External display name"),
        help_text=_("Nome visualizzato dell'utente federato."),
    )
    contacts_unlocked = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Contacts unlocked"),
        help_text=_("Number of helper contacts this user has unlocked."),
    )
    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_LEVEL_CHOICES,
        default="view_list",
        verbose_name=_("Access level"),
        help_text=_("Livello di accesso alla directory soccorritori."),
    )
    is_active = models.BooleanField(default=True,
        help_text=_("L'accesso è attualmente attivo."),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Approved by"),
        help_text=_("Amministratore che ha approvato l'accesso."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data di concessione dell'accesso."),
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expires at"),
        help_text=_("Scadenza dell'accesso. Vuoto = nessuna scadenza."),
    )

    class Meta:
        verbose_name = _("Federated Aid Access")
        verbose_name_plural = _("Federated Aid Access Grants")
        unique_together = [("source_club", "external_user_id")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.external_display_name} ({self.source_club.short_code})"


# ---------------------------------------------------------------------------
# FederatedAidAccessRequest
# ---------------------------------------------------------------------------


class FederatedAidAccessRequest(models.Model):
    """
    A request from a federated user to gain or upgrade access
    to the mutual aid helpers directory.
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("denied", _("Denied")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    federated_access = models.ForeignKey(
        FederatedAidAccess,
        on_delete=models.CASCADE,
        related_name="access_requests",
        verbose_name=_("Federated access"),
        help_text=_("Accesso federato di riferimento."),
    )
    message = models.TextField(
        blank=True,
        verbose_name=_("Message"),
        help_text=_("Why are you requesting access?"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        help_text=_("Stato della richiesta di accesso."),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Reviewed by"),
        help_text=_("Amministratore che ha valutato la richiesta."),
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Reviewed at"),
        help_text=_("Data e ora della valutazione."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data e ora di invio della richiesta."),
    )

    class Meta:
        verbose_name = _("Federated Aid Access Request")
        verbose_name_plural = _("Federated Aid Access Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Access request from {self.federated_access} ({self.status})"


# ---------------------------------------------------------------------------
# ContactUnlock
# ---------------------------------------------------------------------------


class ContactUnlock(models.Model):
    """
    Tracks when a federated user unlocks a helper's contact info.

    Limited to 3 unlocks per 30-day period per federated user.
    """

    UNLOCK_LIMIT = 3
    UNLOCK_WINDOW_DAYS = 30

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    federated_access = models.ForeignKey(
        FederatedAidAccess,
        on_delete=models.CASCADE,
        related_name="contact_unlocks",
        verbose_name=_("Federated access"),
        help_text=_("Accesso federato che ha sbloccato il contatto."),
    )
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contact_unlocks_received",
        verbose_name=_("Helper"),
        help_text=_("Soccorritore il cui contatto è stato sbloccato."),
    )
    unlocked_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data e ora dello sblocco."),
    )

    class Meta:
        verbose_name = _("Contact Unlock")
        verbose_name_plural = _("Contact Unlocks")
        unique_together = [("federated_access", "helper")]
        ordering = ["-unlocked_at"]

    def __str__(self):
        return f"{self.federated_access} unlocked {self.helper}"

    @classmethod
    def can_unlock(cls, federated_access):
        """
        Check if the federated user can unlock another contact.

        Returns True if they have fewer than UNLOCK_LIMIT unlocks
        in the last UNLOCK_WINDOW_DAYS days.
        """
        from datetime import timedelta

        from django.utils import timezone

        window_start = timezone.now() - timedelta(days=cls.UNLOCK_WINDOW_DAYS)
        recent_count = cls.objects.filter(
            federated_access=federated_access,
            unlocked_at__gte=window_start,
        ).count()
        return recent_count < cls.UNLOCK_LIMIT


# ---------------------------------------------------------------------------
# FederatedHelper — cached helper data from partner clubs
# ---------------------------------------------------------------------------


class FederatedHelper(models.Model):
    """
    Cached helper data from a federated partner club.

    Follows the same pattern as ExternalEvent: data is synced
    periodically from partner club APIs and displayed alongside
    local helpers. No personal data (email, phone) is ever stored.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_club = models.ForeignKey(
        "federation.FederatedClub",
        on_delete=models.CASCADE,
        related_name="federated_helpers",
        verbose_name=_("Source club"),
    )
    external_id = models.CharField(
        max_length=100,
        verbose_name=_("External ID"),
        help_text=_("Helper ID on the partner system."),
    )
    display_name = models.CharField(max_length=100, verbose_name=_("Display name"))
    city = models.CharField(max_length=100, blank=True, verbose_name=_("City"))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_("Latitude"))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_("Longitude"))
    radius_km = models.PositiveIntegerField(default=25, verbose_name=_("Radius (km)"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))
    photo_url = models.URLField(blank=True, verbose_name=_("Photo URL"))
    is_approved = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    fetched_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Federated Helper")
        verbose_name_plural = _("Federated Helpers")
        unique_together = [("source_club", "external_id")]
        ordering = ["city", "display_name"]

    def __str__(self):
        return f"{self.display_name} ({self.source_club.short_code})"

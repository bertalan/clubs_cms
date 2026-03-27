"""
Federation models: FederatedClub, ExternalEvent, ExternalEventInterest,
ExternalEventComment, FederationInfoPage.
"""

import json
import logging
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import models
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.website.blocks import BODY_BLOCKS, FAQBlock, TimelineBlock

logger = logging.getLogger(__name__)


class FederatedClub(models.Model):
    """
    A partner club in the federation network.
    Only admins can create/edit these records.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text=_("Display name of the partner club"))
    short_code = models.CharField(
        max_length=20, unique=True, help_text=_("URL-safe identifier")
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("City"),
        help_text=_("City where the partner club is based."),
    )
    base_url = models.URLField(help_text=_("Partner site base URL"))
    description = models.TextField(
        blank=True,
        help_text=_("Short description of the partner club (visible on federation page)."),
    )
    logo_url = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Logo URL (external) or static path (e.g. /static/img/federation/logo.svg)."),
    )
    api_key = models.CharField(
        max_length=64, help_text=_("Their public API key (given to us)")
    )
    our_key_for_them = models.CharField(
        max_length=64, blank=True, help_text=_("Our key we gave them (auto-generated)")
    )
    is_active = models.BooleanField(default=False,
        help_text=_("Attiva la connessione con questo club partner."),
    )
    is_approved = models.BooleanField(default=False,
        help_text=_("Il club partner è stato verificato e approvato."),
    )
    share_our_events = models.BooleanField(
        default=False, help_text=_("Share our events with this partner")
    )
    auto_import = models.BooleanField(
        default=True, help_text=_("Auto-approve imported events")
    )
    last_sync = models.DateTimeField(null=True, blank=True,
        help_text=_("Data e ora dell'ultima sincronizzazione eventi."),
    )
    last_error = models.TextField(blank=True,
        help_text=_("Ultimo messaggio di errore durante la sincronizzazione."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data di creazione del record."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Amministratore che ha aggiunto il club partner."),
    )

    class Meta:
        verbose_name = _("Federated Club")
        verbose_name_plural = _("Federated Clubs")
        ordering = ["name"]

    def clean(self):
        super().clean()
        if self.logo_url and not (
            self.logo_url.startswith("/static/")
            or self.logo_url.startswith("http://")
            or self.logo_url.startswith("https://")
        ):
            raise ValidationError(
                {"logo_url": _("Logo must be a URL (http/https) or a /static/ path.")}
            )

    def __str__(self):
        return self.name


class ExternalEvent(models.Model):
    """
    An event fetched from a partner club.
    Read-only: never editable by admin, only updated via sync.
    """

    EVENT_STATUS_CHOICES = [
        ("EventScheduled", "Scheduled"),
        ("EventCancelled", "Cancelled"),
        ("EventPostponed", "Postponed"),
        ("EventMovedOnline", "Moved Online"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_club = models.ForeignKey(
        FederatedClub, on_delete=models.CASCADE, related_name="external_events",
        help_text=_("Club partner che ha pubblicato l'evento."),
    )
    external_id = models.CharField(max_length=100,
        help_text=_("ID univoco dell'evento nel sistema del partner."),
    )
    event_name = models.CharField(max_length=255,
        help_text=_("Nome dell'evento come fornito dal partner."),
    )
    start_date = models.DateTimeField(
        help_text=_("Data e ora di inizio dell'evento."),
    )
    end_date = models.DateTimeField(null=True, blank=True,
        help_text=_("Data e ora di fine dell'evento."),
    )
    location_name = models.CharField(max_length=255, blank=True,
        help_text=_("Nome del luogo dell'evento."),
    )
    location_address = models.CharField(max_length=500, blank=True,
        help_text=_("Indirizzo completo del luogo."),
    )
    location_lat = models.FloatField(null=True, blank=True,
        help_text=_("Latitudine della posizione."),
    )
    location_lon = models.FloatField(null=True, blank=True,
        help_text=_("Longitudine della posizione."),
    )
    description = models.TextField(blank=True, help_text=_("Sanitized HTML"))
    event_status = models.CharField(
        max_length=20, choices=EVENT_STATUS_CHOICES, default="EventScheduled",
        help_text=_("Stato corrente dell'evento."),
    )
    image_url = models.URLField(blank=True,
        help_text=_("URL dell'immagine di copertina."),
    )
    detail_url = models.URLField(blank=True,
        help_text=_("URL della pagina dell'evento sul sito partner."),
    )
    is_approved = models.BooleanField(default=True,
        help_text=_("L'evento è visibile ai soci."),
    )
    is_hidden = models.BooleanField(default=False,
        help_text=_("Nascondi l'evento dall'elenco pubblico."),
    )
    fetched_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data del primo import dell'evento."),
    )
    updated_at = models.DateTimeField(auto_now=True,
        help_text=_("Data dell'ultimo aggiornamento."),
    )

    class Meta:
        verbose_name = _("External Event")
        verbose_name_plural = _("External Events")
        unique_together = [("source_club", "external_id")]
        ordering = ["start_date"]
        indexes = [
            models.Index(fields=["start_date"]),
            models.Index(fields=["is_approved", "is_hidden"]),
        ]

    def __str__(self):
        return f"{self.event_name} ({self.source_club.short_code})"


class ExternalEventInterest(models.Model):
    """
    A member's interest in an external event.
    """

    INTEREST_CHOICES = [
        ("interested", "Interested"),
        ("maybe", "Maybe"),
        ("going", "Going"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_interests",
        help_text=_("Socio che ha espresso interesse."),
    )
    external_event = models.ForeignKey(
        ExternalEvent, on_delete=models.CASCADE, related_name="interests",
        help_text=_("Evento esterno di interesse."),
    )
    interest_level = models.CharField(max_length=20, choices=INTEREST_CHOICES,
        help_text=_("Livello di interesse per l'evento."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data di espressione dell'interesse."),
    )
    updated_at = models.DateTimeField(auto_now=True,
        help_text=_("Data dell'ultima modifica."),
    )

    class Meta:
        verbose_name = _("External Event Interest")
        verbose_name_plural = _("External Event Interests")
        unique_together = [("user", "external_event")]
        indexes = [
            models.Index(fields=["external_event"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.interest_level} - {self.external_event}"


class ExternalEventComment(models.Model):
    """
    A comment on an external event for local member organization.
    Comments are never shared with the partner club.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_comments",
        help_text=_("Socio autore del commento."),
    )
    external_event = models.ForeignKey(
        ExternalEvent, on_delete=models.CASCADE, related_name="comments",
        help_text=_("Evento esterno commentato."),
    )
    content = models.TextField(
        help_text=_("Testo del commento (non condiviso col partner)."),
    )
    created_at = models.DateTimeField(auto_now_add=True,
        help_text=_("Data di creazione del commento."),
    )
    updated_at = models.DateTimeField(auto_now=True,
        help_text=_("Data dell'ultima modifica."),
    )
    is_deleted = models.BooleanField(default=False,
        help_text=_("Il commento è stato cancellato (soft delete)."),
    )

    class Meta:
        verbose_name = _("External Event Comment")
        verbose_name_plural = _("External Event Comments")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["external_event", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.external_event}"


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# FederationInfoPage (Wagtail RoutablePageMixin)
# ---------------------------------------------------------------------------


def _is_active_member(user):
    """Check if user is an active club member."""
    return getattr(user, "is_active_member", False)


def _build_event_json_ld(event):
    """Build a schema.org/Event dict for JSON-LD structured data."""
    from django.template.defaultfilters import truncatewords
    from django.utils.html import strip_tags

    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event.event_name,
        "startDate": event.start_date.isoformat(),
        "eventStatus": f"https://schema.org/{event.event_status}",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "organizer": {
            "@type": "Organization",
            "name": event.source_club.name,
        },
    }

    if event.end_date:
        data["endDate"] = event.end_date.isoformat()
    if event.source_club.base_url:
        data["organizer"]["url"] = event.source_club.base_url
    if event.detail_url:
        data["url"] = event.detail_url

    if event.location_name or event.location_address:
        location = {"@type": "Place"}
        if event.location_name:
            location["name"] = event.location_name
        if event.location_address:
            location["address"] = event.location_address
        if event.location_lat and event.location_lon:
            location["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": event.location_lat,
                "longitude": event.location_lon,
            }
        data["location"] = location

    if event.description:
        data["description"] = truncatewords(strip_tags(event.description), 50)
    if event.image_url:
        data["image"] = event.image_url

    return data


class FederationInfoPage(RoutablePageMixin, Page):
    """
    Federation landing page with routable sub-views for
    partner events listing, detail, interest, and comments.

    Routes:
        /                                       — info landing
        /events/                                — partner events list
        /events/<club_code>/<event_id>/         — event detail
        /events/<club_code>/<event_id>/interest/  — set interest (POST)
        /events/<club_code>/<event_id>/comment/   — add comment (POST)
        /events/<club_code>/<event_id>/comment/delete/ — delete comment (POST)
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Introductory text displayed below the page title."),
    )
    how_it_works = StreamField(
        [("step", TimelineBlock())],
        blank=True,
        use_json_field=True,
        verbose_name=_("How it works"),
        help_text=_("Steps explaining the federation process."),
    )
    faq = StreamField(
        [("faq", FAQBlock())],
        blank=True,
        use_json_field=True,
        verbose_name=_("FAQ"),
    )
    body = StreamField(
        BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        verbose_name=_("Additional content"),
    )
    cta_text = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("CTA button text"),
        help_text=_("Label for the call-to-action button."),
    )
    events_intro = RichTextField(
        blank=True,
        verbose_name=_("Events page introduction"),
        help_text=_("Introductory text for the partner events listing page."),
    )
    events_per_page = models.PositiveIntegerField(
        default=12,
        verbose_name=_("Events per page"),
        help_text=_("Number of events to display per page."),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("how_it_works"),
        MultiFieldPanel(
            [
                FieldPanel("cta_text"),
                FieldPanel("events_intro"),
                FieldPanel("events_per_page"),
            ],
            heading=_("Events Section"),
        ),
        FieldPanel("faq"),
        FieldPanel("body"),
    ]

    max_count = 1
    subpage_types = []
    parent_page_types = ["wagtailcore.Page", "website.HomePage"]
    template = "federation/federation_info_page.html"

    class Meta:
        verbose_name = _("Federation Info Page")
        verbose_name_plural = _("Federation Info Pages")

    # ------------------------------------------------------------------
    # Route: landing page (info, stats, partners, FAQ)
    # ------------------------------------------------------------------

    @route(r"^$")
    def info_view(self, request):
        return self.render(
            request,
            template="federation/federation_info_page.html",
            context_overrides=self._info_context(request),
        )

    def _info_context(self, request):
        from django.db.models import Count, Q

        partner_clubs = (
            FederatedClub.objects.filter(is_active=True, is_approved=True)
            .annotate(
                event_count=Count(
                    "external_events",
                    filter=Q(
                        external_events__is_approved=True,
                        external_events__is_hidden=False,
                    ),
                )
            )
            .order_by("name")
        )
        return {
            "partner_clubs": partner_clubs,
            "partner_count": partner_clubs.count(),
            "event_count": ExternalEvent.objects.filter(
                is_approved=True, is_hidden=False
            ).count(),
        }

    # ------------------------------------------------------------------
    # Route: events list
    # ------------------------------------------------------------------

    @route(r"^events/$", name="events_list")
    @method_decorator(login_required)
    def events_list_view(self, request):
        qs = (
            ExternalEvent.objects.filter(
                is_approved=True,
                is_hidden=False,
                start_date__gte=timezone.now(),
            )
            .select_related("source_club")
            .order_by("start_date")
        )

        # Optional filtering by club
        club_code = request.GET.get("club")
        if club_code:
            qs = qs.filter(source_club__short_code=club_code)

        # Optional search
        search = request.GET.get("q")
        if search:
            qs = qs.filter(event_name__icontains=search)

        paginator = Paginator(qs, self.events_per_page)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        partner_clubs = FederatedClub.objects.filter(
            is_active=True, is_approved=True
        ).order_by("name")

        return self.render(
            request,
            template="federation/external_events_list.html",
            context_overrides={
                "events": page_obj,
                "page_obj": page_obj,
                "paginator": paginator,
                "is_paginated": page_obj.has_other_pages(),
                "partner_clubs": partner_clubs,
                "selected_club": club_code or "",
                "search_query": search or "",
            },
        )

    # ------------------------------------------------------------------
    # Route: event detail
    # ------------------------------------------------------------------

    @route(r"^events/(?P<club_code>[\w-]+)/(?P<event_id>[0-9a-f-]+)/$", name="event_detail")
    @method_decorator(login_required)
    def event_detail_view(self, request, club_code, event_id):
        event = get_object_or_404(
            ExternalEvent.objects.select_related("source_club"),
            source_club__short_code=club_code,
            pk=event_id,
            is_approved=True,
            is_hidden=False,
        )

        user = request.user
        user_interest = None
        if user.is_authenticated:
            try:
                user_interest = ExternalEventInterest.objects.get(
                    user=user, external_event=event
                )
            except ExternalEventInterest.DoesNotExist:
                pass

        comments = (
            event.comments.filter(is_deleted=False)
            .select_related("user")
            .order_by("created_at")
        )

        interest_counts = {
            "interested": event.interests.filter(interest_level="interested").count(),
            "maybe": event.interests.filter(interest_level="maybe").count(),
            "going": event.interests.filter(interest_level="going").count(),
        }

        json_ld = mark_safe(
            json.dumps(_build_event_json_ld(event), ensure_ascii=False)
        )

        return self.render(
            request,
            template="federation/external_event_detail.html",
            context_overrides={
                "event": event,
                "user_interest": user_interest,
                "comments": comments,
                "interest_counts": interest_counts,
                "is_active_member": _is_active_member(user),
                "json_ld": json_ld,
            },
        )

    # ------------------------------------------------------------------
    # Route: set interest (POST)
    # ------------------------------------------------------------------

    @route(r"^events/(?P<club_code>[\w-]+)/(?P<event_id>[0-9a-f-]+)/interest/$", name="set_interest")
    @method_decorator(login_required)
    def set_interest_view(self, request, club_code, event_id):
        if request.method != "POST":
            return HttpResponseRedirect(self.reverse_subpage(
                "event_detail", args=[club_code, event_id]
            ))

        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        event = get_object_or_404(
            ExternalEvent,
            source_club__short_code=club_code,
            pk=event_id,
            is_approved=True,
        )

        interest_level = request.POST.get("interest_level", "")

        if interest_level == "remove":
            ExternalEventInterest.objects.filter(
                user=request.user, external_event=event
            ).delete()
        elif interest_level in ("interested", "maybe", "going"):
            ExternalEventInterest.objects.update_or_create(
                user=request.user,
                external_event=event,
                defaults={"interest_level": interest_level},
            )
        else:
            return HttpResponseForbidden("Invalid interest level")

        return HttpResponseRedirect(
            self.url + self.reverse_subpage("event_detail", args=[club_code, event_id])
        )

    # ------------------------------------------------------------------
    # Route: add comment (POST)
    # ------------------------------------------------------------------

    @route(r"^events/(?P<club_code>[\w-]+)/(?P<event_id>[0-9a-f-]+)/comment/$", name="add_comment")
    @method_decorator(login_required)
    def add_comment_view(self, request, club_code, event_id):
        detail_url = self.url + self.reverse_subpage(
            "event_detail", args=[club_code, event_id]
        )

        if request.method != "POST":
            return HttpResponseRedirect(detail_url)

        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        event = get_object_or_404(
            ExternalEvent,
            source_club__short_code=club_code,
            pk=event_id,
            is_approved=True,
        )

        content = request.POST.get("content", "").strip()
        if not content:
            return HttpResponseRedirect(detail_url)

        # Limit comment length
        content = content[:2000]

        ExternalEventComment.objects.create(
            user=request.user,
            external_event=event,
            content=content,
        )

        # Send notification to other commenters
        try:
            from apps.notifications.services import create_notification

            other_commenters = (
                ExternalEventComment.objects.filter(
                    external_event=event, is_deleted=False
                )
                .exclude(user=request.user)
                .values_list("user", flat=True)
                .distinct()
            )

            from django.contrib.auth import get_user_model

            User = get_user_model()
            recipients = User.objects.filter(pk__in=other_commenters)

            if recipients.exists():
                display_name = request.user.get_visible_name()
                create_notification(
                    notification_type="partner_event_comment",
                    title=f"New comment on {event.event_name}",
                    body=f"{display_name} commented on the partner event '{event.event_name}'",
                    url=detail_url,
                    recipients=recipients,
                    content_object=event,
                )
        except Exception:
            logger.exception("Failed to send comment notification")

        return HttpResponseRedirect(detail_url)

    # ------------------------------------------------------------------
    # Route: delete comment (POST)
    # ------------------------------------------------------------------

    @route(r"^events/(?P<club_code>[\w-]+)/(?P<event_id>[0-9a-f-]+)/comment/delete/$", name="delete_comment")
    @method_decorator(login_required)
    def delete_comment_view(self, request, club_code, event_id):
        detail_url = self.url + self.reverse_subpage(
            "event_detail", args=[club_code, event_id]
        )

        if request.method != "POST":
            return HttpResponseRedirect(detail_url)

        comment_id = request.POST.get("comment_id", "")

        comment = get_object_or_404(
            ExternalEventComment,
            pk=comment_id,
            user=request.user,
            external_event__source_club__short_code=club_code,
            external_event__pk=event_id,
        )

        comment.is_deleted = True
        comment.save(update_fields=["is_deleted"])

        return HttpResponseRedirect(detail_url)

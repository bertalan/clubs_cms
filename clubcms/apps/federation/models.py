"""
Federation models: FederatedClub, ExternalEvent, ExternalEventInterest,
ExternalEventComment, FederationInfoPage.
"""

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.website.blocks import BODY_BLOCKS, FAQBlock, TimelineBlock


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
# FederationInfoPage (Wagtail Page)
# ---------------------------------------------------------------------------


class FederationInfoPage(Page):
    """
    Public landing page explaining the federation network.

    Shows how federation works, lists approved partner clubs,
    and provides a CTA to the external events listing.
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
    cta_url = models.CharField(
        max_length=200,
        blank=True,
        default="/eventi/partner/",
        verbose_name=_("CTA link"),
        help_text=_("URL the CTA button links to."),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("how_it_works"),
        MultiFieldPanel(
            [FieldPanel("cta_text"), FieldPanel("cta_url")],
            heading=_("Call to Action"),
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

    def get_context(self, request, *args, **kwargs):
        from django.db.models import Count, Q

        context = super().get_context(request, *args, **kwargs)
        context["partner_clubs"] = (
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
        context["partner_count"] = context["partner_clubs"].count()
        context["event_count"] = ExternalEvent.objects.filter(
            is_approved=True, is_hidden=False
        ).count()
        return context

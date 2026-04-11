"""
Transactional models: Activity log, Reactions, Comments.
Wagtail page models: SearchPage, ContributionsPage.

These models use GenericForeignKey to work with any content type
(pages, events, photos, etc.).
"""

import math

from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.shortcuts import redirect, render
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from apps.website.blocks import BODY_BLOCKS


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------


class Activity(models.Model):
    """
    Log of user actions: uploads, registrations, comments, etc.

    Used for per-user activity feeds and admin audit trails.
    """

    ACTION_CHOICES = [
        ("upload", _("Upload")),
        ("register", _("Registration")),
        ("comment", _("Comment")),
        ("reaction", _("Reaction")),
        ("profile_update", _("Profile update")),
        ("login", _("Login")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name=_("User"),
        help_text=_("Utente che ha eseguito l'azione."),
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        verbose_name=_("Action"),
        help_text=_("Tipo di azione registrata nel log attività."),
    )

    # Generic target (page, event, photo, etc.)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Target content type"),
        help_text=_("Tipo di contenuto dell'oggetto collegato."),
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Target ID"),
        help_text=_("ID dell'oggetto collegato a questa attività."),
    )
    target = GenericForeignKey("target_content_type", "target_id")
    target_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Target title"),
        help_text=_("Titolo dell'oggetto collegato, salvato per riferimento rapido."),
    )
    target_url = models.URLField(
        blank=True,
        verbose_name=_("Target URL"),
        help_text=_("URL dell'oggetto collegato, se disponibile."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Data e ora di registrazione dell'attività."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user} — {self.get_action_display()} — {self.target_title}"


# ---------------------------------------------------------------------------
# Reaction
# ---------------------------------------------------------------------------


class Reaction(models.Model):
    """
    Like/Love reaction on any content.

    Unique constraint per user + content object prevents duplicate reactions.
    """

    REACTION_CHOICES = [
        ("like", _("Like")),
        ("love", _("Love")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name=_("User"),
        help_text=_("Utente che ha lasciato la reazione."),
    )
    reaction_type = models.CharField(
        max_length=10,
        choices=REACTION_CHOICES,
        default="like",
        verbose_name=_("Reaction"),
        help_text=_("Tipo di reazione: Like o Love."),
    )

    # Generic target
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
        help_text=_("Tipo di contenuto dell'oggetto a cui è associata la reazione."),
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("Object ID"),
        help_text=_("ID dell'oggetto a cui è associata la reazione."),
    )
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Data e ora in cui è stata lasciata la reazione."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("reaction")
        verbose_name_plural = _("reactions")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "content_type", "object_id"],
                name="unique_reaction_per_user",
            ),
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user} {self.get_reaction_type_display()} on {self.content_object}"


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------


class Comment(models.Model):
    """
    Moderated comment on any content. Supports reply threading.
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_comments",
        verbose_name=_("User"),
        help_text=_("Utente autore del commento."),
    )
    content = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Testo del commento."),
    )

    # Generic target
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Content type"),
        help_text=_("Tipo di contenuto dell'oggetto commentato."),
    )
    object_id = models.PositiveIntegerField(
        verbose_name=_("Object ID"),
        help_text=_("ID dell'oggetto commentato."),
    )
    content_object = GenericForeignKey("content_type", "object_id")

    # Threading
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name=_("Reply to"),
        help_text=_("Commento genitore, se questo è una risposta."),
    )

    # Moderation
    moderation_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        help_text=_("Stato di moderazione: in attesa, approvato o rifiutato."),
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_comments",
        verbose_name=_("Moderated by"),
        help_text=_("Moderatore che ha revisionato il commento."),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Data e ora di creazione del commento."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("Data e ora dell'ultima modifica."),
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("comment")
        verbose_name_plural = _("comments")
        indexes = [
            models.Index(fields=["content_type", "object_id", "moderation_status"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.user} ({self.get_moderation_status_display()})"

    @property
    def is_reply(self):
        return self.parent_id is not None


# ---------------------------------------------------------------------------
# Contribution
# ---------------------------------------------------------------------------


class Contribution(models.Model):
    """
    Member-submitted content: stories, event proposals, announcements.

    All contributions start as 'pending' and must be approved by a moderator.
    """

    TYPE_CHOICES = [
        ("story", _("Story")),
        ("proposal", _("Event proposal")),
        ("announcement", _("Announcement")),
    ]
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contributions",
        verbose_name=_("Author"),
        help_text=_("Utente autore del contributo."),
    )
    contribution_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("Type"),
        help_text=_("Tipo di contributo: storia, proposta evento o annuncio."),
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("Titolo del contributo (max 255 caratteri)."),
    )
    body = models.TextField(
        verbose_name=_("Content"),
        help_text=_("Corpo del contributo. Supporta testo semplice."),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name=_("Status"),
        help_text=_("Stato di moderazione del contributo."),
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_contributions",
        verbose_name=_("Moderated by"),
        help_text=_("Moderatore che ha revisionato il contributo."),
    )
    moderation_note = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Moderation note"),
        help_text=_("Nota del moderatore visibile all'autore."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Data e ora di invio del contributo."),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
        help_text=_("Data e ora dell'ultima modifica."),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("contribution")
        verbose_name_plural = _("contributions")
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"


# ---------------------------------------------------------------------------
# Haversine distance utility
# ---------------------------------------------------------------------------

_EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Return approximate distance in km between two lat/lon points.

    Uses the Haversine formula — accurate enough for event proximity
    searches up to a few hundred km.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    return _EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


# ---------------------------------------------------------------------------
# SearchPage
# ---------------------------------------------------------------------------

RADIUS_CHOICES = [10, 25, 50, 100, 200]
DEFAULT_RADIUS_KM = 50
PER_PAGE_CHOICES = [25, 50, 100]
DEFAULT_PER_PAGE = 25


class SearchPage(RoutablePageMixin, Page):
    """
    Site-wide search page with full-text and geo-proximity filtering.

    Query params: q, lat, lng, radius, type, per_page, page.
    """

    intro = RichTextField(blank=True, verbose_name=_("Introduction"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    template = "search/search_results.html"

    class Meta:
        verbose_name = _("Search page")
        verbose_name_plural = _("Search pages")

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _get_params(self, request):
        """Extract and validate query parameters."""
        query = request.GET.get("q", "").strip()
        lat = self._safe_float(request.GET.get("lat"))
        lng = self._safe_float(request.GET.get("lng"))
        radius = self._safe_float(request.GET.get("radius")) or DEFAULT_RADIUS_KM
        result_type = request.GET.get("type", "all")
        if result_type not in ("all", "events", "news", "pages"):
            result_type = "all"
        per_page = self._safe_int(request.GET.get("per_page")) or DEFAULT_PER_PAGE
        if per_page not in PER_PAGE_CHOICES:
            per_page = DEFAULT_PER_PAGE
        return query, lat, lng, radius, result_type, per_page

    # ── full-text search ──────────────────────────────────────────────

    MIN_FULLTEXT_LENGTH = 4

    @staticmethod
    def _search_pages(query, result_type):
        from django.db.models import Q
        from apps.website.models.pages import EventDetailPage

        events = []
        pages = []
        use_fulltext = len(query) >= SearchPage.MIN_FULLTEXT_LENGTH if query else False

        if result_type in ("all", "events"):
            qs = EventDetailPage.objects.live()
            if query:
                if use_fulltext:
                    qs = qs.search(query)
                else:
                    qs = qs.filter(
                        Q(title__icontains=query)
                        | Q(intro__icontains=query)
                        | Q(location_name__icontains=query)
                    )
            events = list(qs)

        if result_type in ("all", "pages", "news"):
            qs = Page.objects.live().not_type(EventDetailPage)
            if query:
                if use_fulltext:
                    qs = qs.search(query)
                else:
                    qs = qs.filter(title__icontains=query)
            pages = list(qs)

        return events, pages

    @staticmethod
    def _search_external_events(query):
        if not getattr(settings, "FEDERATION_ENABLED", False):
            return []
        try:
            from apps.federation.models import ExternalEvent

            qs = ExternalEvent.objects.filter(is_approved=True, is_hidden=False)
            if query:
                from django.db.models import Q

                qs = qs.filter(
                    Q(event_name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(location_name__icontains=query)
                    | Q(location_address__icontains=query)
                )
            return list(qs)
        except Exception:
            return []

    # ── geo filtering ─────────────────────────────────────────────────

    @staticmethod
    def _apply_geo_filter(events, lat, lng, radius_km):
        if lat is None or lng is None:
            return events

        filtered = []
        for ev in events:
            ev_lat = getattr(ev, "latitude", None) or getattr(ev, "location_lat", None)
            ev_lng = getattr(ev, "longitude", None) or getattr(ev, "location_lon", None)
            if ev_lat is None or ev_lng is None:
                continue
            try:
                dist = haversine_km(lat, lng, float(ev_lat), float(ev_lng))
            except (TypeError, ValueError):
                continue
            if dist <= radius_km:
                ev.distance_km = round(dist, 1)
                filtered.append(ev)

        filtered.sort(key=lambda e: e.distance_km)
        return filtered

    # ── main context ──────────────────────────────────────────────────

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        query, lat, lng, radius, result_type, per_page = self._get_params(request)

        events, pages = self._search_pages(query, result_type)
        external_events = (
            self._search_external_events(query)
            if result_type in ("all", "events")
            else []
        )

        geo_active = lat is not None and lng is not None
        if geo_active:
            events = self._apply_geo_filter(events, lat, lng, radius)
            external_events = self._apply_geo_filter(external_events, lat, lng, radius)

        all_events = list(events) + list(external_events)
        if geo_active:
            all_events.sort(key=lambda e: getattr(e, "distance_km", 9999))

        paginator = Paginator(all_events + list(pages), per_page)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        context.update(
            {
                "search_query": query,
                "results": page_obj,
                "page_obj": page_obj,
                "paginator": paginator,
                "result_count": paginator.count,
                "events_count": len(all_events),
                "pages_count": len(pages),
                "geo_active": geo_active,
                "user_lat": lat,
                "user_lng": lng,
                "radius": radius,
                "radius_choices": RADIUS_CHOICES,
                "result_type": result_type,
                "per_page": per_page,
                "per_page_choices": PER_PAGE_CHOICES,
            }
        )
        return context


# ---------------------------------------------------------------------------
# ContributionsPage
# ---------------------------------------------------------------------------


class ContributionsPage(RoutablePageMixin, Page):
    """
    Member contributions hub: list own contributions & submit new ones.

    Routes:
    - index: my contributions list (login required)
    - submit/: submit new contribution form (login required)
    """

    intro = RichTextField(blank=True, verbose_name=_("Introduction"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["core.ContributionPage"]
    max_count = 1
    template = "account/my_contributions.html"

    class Meta:
        verbose_name = _("Contributions page")
        verbose_name_plural = _("Contributions pages")

    # ── index: my contributions ───────────────────────────────────────

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        if request.user.is_authenticated:
            qs = (
                ContributionPage.objects
                .child_of(self)
                .filter(author=request.user)
                .order_by("-first_published_at", "-latest_revision_created_at")
            )
            paginator = Paginator(qs, 20)
            page_number = request.GET.get("page")
            try:
                page_obj = paginator.page(page_number)
            except PageNotAnInteger:
                page_obj = paginator.page(1)
            except EmptyPage:
                page_obj = paginator.page(paginator.num_pages)
            context["contributions"] = page_obj
            context["page_obj"] = page_obj
            context["paginator"] = paginator
            context["is_paginated"] = paginator.num_pages > 1
        return context

    def serve(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        return super().serve(request, *args, **kwargs)

    # ── submit contribution ───────────────────────────────────────────

    @route(r"^submit/$", name="submit_contribution")
    def submit_contribution_view(self, request):
        from apps.core.forms import ContributionForm

        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())

        if request.method == "POST":
            form = ContributionForm(request.POST, user=request.user)
            if form.is_valid():
                body_text = form.cleaned_data["body"]
                paragraphs = body_text.strip().split("\n\n")
                body_html = "".join(
                    f"<p>{p.strip()}</p>"
                    for p in paragraphs if p.strip()
                )
                slug_base = slugify(form.cleaned_data["title"])[:50] or "contribution"
                slug = slug_base
                counter = 1
                while Page.objects.filter(
                    slug=slug, path__startswith=self.path
                ).exists():
                    slug = f"{slug_base}-{counter}"
                    counter += 1

                child = self.add_child(
                    instance=ContributionPage(
                        title=form.cleaned_data["title"],
                        slug=slug,
                        contribution_type=form.cleaned_data["contribution_type"],
                        body=[{"type": "rich_text", "value": body_html}],
                        author=request.user,
                        owner=request.user,
                        live=False,
                        has_unpublished_changes=True,
                    )
                )
                child.save_revision()
                messages.success(
                    request,
                    _("Your contribution has been submitted and is awaiting moderation."),
                )
                return redirect(self.url)
        else:
            form = ContributionForm(user=request.user)

        return render(
            request,
            "account/submit_contribution.html",
            {"page": self, "form": form},
        )


# ---------------------------------------------------------------------------
# ContributionPage
# ---------------------------------------------------------------------------


class ContributionPage(Page):
    """
    Individual member contribution: story, event proposal, or announcement.

    Created from the frontend form and moderated via Wagtail admin.
    Approved contributions are published as real pages with their own URL.
    """

    TYPE_CHOICES = [
        ("story", _("Story")),
        ("proposal", _("Event proposal")),
        ("announcement", _("Announcement")),
    ]
    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
    ]

    contribution_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name=_("Type"),
    )
    body = StreamField(
        BODY_BLOCKS, blank=True, use_json_field=True,
        verbose_name=_("Content"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="contribution_pages",
        verbose_name=_("Author"),
    )
    moderation_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name=_("Moderation status"),
    )
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_contribution_pages",
        verbose_name=_("Moderated by"),
    )
    moderation_note = models.TextField(
        blank=True,
        verbose_name=_("Moderation note"),
    )

    parent_page_types = ["core.ContributionsPage"]
    subpage_types = []
    template = "website/pages/contribution_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("contribution_type"),
        FieldPanel("body"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("moderation_status"),
                FieldPanel("moderated_by"),
                FieldPanel("moderation_note"),
            ],
            heading=_("Moderation"),
        ),
    ]

    class Meta:
        verbose_name = _("Contribution")
        verbose_name_plural = _("Contributions")

    def __str__(self):
        return f"[{self.get_moderation_status_display()}] {self.title}"

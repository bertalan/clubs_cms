"""
Notification system models.

Provides a notification queue for email, push, and in-app delivery,
push subscription management, token-based unsubscribe, and a
NotificationsPage (RoutablePageMixin) for history and mark-read.
"""

import json

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from wagtail.models import Page


# ---------------------------------------------------------------------------
# Notification type choices
# ---------------------------------------------------------------------------

NOTIFICATION_TYPE_CHOICES = [
    # Content notifications
    ("news_published", _("News published")),
    ("event_published", _("Event published")),
    ("event_reminder", _("Event reminder")),
    ("weekend_favorites", _("Weekend favorites")),
    ("registration_opens", _("Registration opens")),
    ("photo_approved", _("Photo approved")),
    ("membership_expiring", _("Membership expiring")),
    # Partner / federation
    ("partner_news", _("Partner news")),
    ("partner_events", _("Partner events")),
    ("partner_event_interest", _("Partner event interest")),
    ("partner_event_comment", _("Partner event comment")),
    ("partner_event_cancelled", _("Partner event cancelled")),
    # Mutual-aid
    ("aid_request", _("Aid request")),
    ("mutual_aid_request", _("Mutual aid request")),
    ("mutual_aid_access_request", _("Mutual aid access request")),
    # Event registration
    ("event_registered", _("Event registration confirmed")),
    ("payment_instructions", _("Payment instructions")),
    ("payment_confirmed", _("Payment confirmed")),
    ("payment_expired", _("Payment expired")),
    ("registration_cancelled", _("Registration cancelled")),
    ("waitlist_promoted", _("Promoted from waitlist")),
]

CHANNEL_CHOICES = [
    ("email", _("Email")),
    ("push", _("Push notification")),
    ("in_app", _("In-app notification")),
]

STATUS_CHOICES = [
    ("pending", _("Pending")),
    ("sent", _("Sent")),
    ("failed", _("Failed")),
    ("skipped", _("Skipped")),
]


# ---------------------------------------------------------------------------
# Mapping: notification_type -> user preference field
# ---------------------------------------------------------------------------

NOTIFICATION_PREFERENCE_MAP = {
    "news_published": "news_updates",
    "event_published": "event_updates",
    "event_reminder": "event_reminders",
    "weekend_favorites": "event_updates",
    "registration_opens": "event_updates",
    "photo_approved": "news_updates",
    "membership_expiring": "membership_alerts",
    "partner_news": "partner_updates",
    "partner_events": "partner_events",
    "partner_event_interest": "partner_events",
    "partner_event_comment": "partner_event_comments",
    "partner_event_cancelled": "partner_events",
    "aid_request": "aid_requests",
    "mutual_aid_request": "aid_requests",
    "mutual_aid_access_request": "aid_requests",
    "event_registered": "event_updates",
    "payment_instructions": "event_updates",
    "payment_confirmed": "event_updates",
    "payment_expired": "event_updates",
    "registration_cancelled": "event_updates",
    "waitlist_promoted": "event_updates",
}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class NotificationQueue(models.Model):
    """
    Single notification entry destined for one recipient via one channel.
    """

    notification_type = models.CharField(
        _("notification type"),
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        db_index=True,
        help_text=_("Tipo di notifica da inviare."),
    )

    # Generic relation to the triggering content object (optional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("content type"),
        help_text=_("Tipo di contenuto che ha generato la notifica."),
    )
    object_id = models.PositiveIntegerField(
        _("object ID"),
        null=True,
        blank=True,
        help_text=_("ID dell'oggetto che ha generato la notifica."),
    )
    content_object = GenericForeignKey("content_type", "object_id")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("recipient"),
        help_text=_("Destinatario della notifica."),
    )

    channel = models.CharField(
        _("channel"),
        max_length=10,
        choices=CHANNEL_CHOICES,
        help_text=_("Canale di invio: email, push o in-app."),
    )

    status = models.CharField(
        _("status"),
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        help_text=_("Stato di invio della notifica."),
    )

    title = models.CharField(_("title"), max_length=255,
        help_text=_("Titolo della notifica."),
    )
    body = models.TextField(_("body"),
        help_text=_("Corpo del messaggio della notifica."),
    )
    url = models.CharField(_("URL"), max_length=500, blank=True, default="",
        help_text=_("URL di destinazione quando si clicca la notifica."),
    )

    scheduled_for = models.DateTimeField(
        _("scheduled for"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("If set, notification will not be sent before this time."),
    )
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True,
        help_text=_("Data e ora di invio effettivo."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True,
        help_text=_("Data e ora di creazione nella coda."),
    )

    error_message = models.TextField(_("error message"), blank=True, default="",
        help_text=_("Messaggio di errore in caso di invio fallito."),
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_for"]),
            models.Index(fields=["recipient", "created_at"]),
            models.Index(fields=["notification_type", "status"]),
        ]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} -> {self.recipient}"


class PushSubscription(models.Model):
    """
    Web Push subscription registered by a user's browser.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
        verbose_name=_("user"),
        help_text=_("Utente proprietario della sottoscrizione push."),
    )
    endpoint = models.TextField(
        _("endpoint"),
        help_text=_("Push service URL"),
    )
    p256dh_key = models.TextField(
        _("p256dh key"),
        help_text=_("Client public encryption key"),
    )
    auth_key = models.TextField(
        _("auth key"),
        help_text=_("Client auth secret"),
    )
    is_active = models.BooleanField(_("active"), default=True,
        help_text=_("La sottoscrizione è attiva e valida."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True,
        help_text=_("Data di registrazione della sottoscrizione."),
    )
    last_used = models.DateTimeField(_("last used"), null=True, blank=True,
        help_text=_("Ultima volta che la sottoscrizione è stata usata."),
    )
    user_agent = models.TextField(_("user agent"), blank=True, default="",
        help_text=_("Browser e dispositivo dell'utente."),
    )

    class Meta:
        unique_together = [("user", "endpoint")]
        verbose_name = _("push subscription")
        verbose_name_plural = _("push subscriptions")

    def __str__(self):
        return f"Push sub {self.pk} for {self.user}"


class UnsubscribeToken(models.Model):
    """
    HMAC-based token allowing one-click unsubscribe without login.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="unsubscribe_tokens",
        verbose_name=_("user"),
        help_text=_("Utente che può disiscriversi con questo token."),
    )
    notification_type = models.CharField(
        _("notification type"),
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text=_("Tipo di notifica da cui disiscriversi."),
    )
    token = models.CharField(
        _("token"),
        max_length=64,
        unique=True,
        help_text=_("Token univoco HMAC per la disiscrizione."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True,
        help_text=_("Data di generazione del token."),
    )

    class Meta:
        unique_together = [("user", "notification_type")]
        verbose_name = _("unsubscribe token")
        verbose_name_plural = _("unsubscribe tokens")

    def __str__(self):
        return f"Unsub {self.notification_type} for {self.user}"


# ---------------------------------------------------------------------------
# Wagtail page – Notification history + mark-read
# ---------------------------------------------------------------------------


class NotificationsPage(RoutablePageMixin, Page):
    """
    Lists the authenticated user's sent notifications with pagination,
    and provides a mark-read AJAX sub-route.
    """

    intro = RichTextField(blank=True, verbose_name=_("Intro text"))

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    parent_page_types = ["website.HomePage"]
    template = "notifications/history.html"

    class Meta:
        verbose_name = _("Notifications page")
        verbose_name_plural = _("Notifications pages")

    # -- main view (history list) ------------------------------------------

    def serve(self, request, *args, **kwargs):
        from django.contrib.auth.decorators import login_required

        @login_required
        def _inner(request):
            return super(NotificationsPage, self).serve(request, *args, **kwargs)
        return _inner(request)

    def get_context(self, request, *args, **kwargs):
        from django.core.paginator import Paginator

        ctx = super().get_context(request, *args, **kwargs)

        qs = (
            NotificationQueue.objects.filter(
                recipient=request.user,
                status="sent",
            )
            .order_by("-sent_at")
        )

        paginator = Paginator(qs, 25)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        ctx["notifications"] = page_obj
        ctx["paginator"] = paginator
        ctx["page_obj"] = page_obj
        ctx["is_paginated"] = page_obj.has_other_pages()
        return ctx

    # -- mark-read sub-route -----------------------------------------------

    @route(r"^mark-read/(?P<pk>\d+)/$", name="mark_read")
    def mark_read(self, request, pk):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "login required"}, status=403)
        if request.method != "POST":
            return JsonResponse({"error": "POST required"}, status=405)

        notification = get_object_or_404(
            NotificationQueue,
            pk=pk,
            recipient=request.user,
        )

        if not notification.sent_at:
            notification.sent_at = timezone.now()
            notification.save(update_fields=["sent_at"])

        return JsonResponse({"ok": True, "pk": notification.pk})

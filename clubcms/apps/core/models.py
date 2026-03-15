"""
Transactional models: Activity log, Reactions, Comments.

These models use GenericForeignKey to work with any content type
(pages, events, photos, etc.).
"""

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


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

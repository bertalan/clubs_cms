"""
Gallery upload models for member photo contributions.

PhotoUpload: tracks member-uploaded photos through a moderation workflow.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class PhotoUpload(models.Model):
    """
    Member-uploaded gallery photo that goes through a moderation workflow.

    Members with can_upload privilege may submit photos, optionally
    linked to an event.  Staff approve or reject uploads before they
    appear publicly.
    """

    image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.CASCADE,
        related_name="photo_uploads",
        verbose_name=_("Image"),
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photo_uploads",
        verbose_name=_("Uploaded by"),
    )
    event = models.ForeignKey(
        "website.EventDetailPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="photo_uploads",
        verbose_name=_("Event"),
        help_text=_("Optionally link this photo to an event."),
    )
    tags = models.ManyToManyField(
        "website.PhotoTag",
        blank=True,
        related_name="photo_uploads",
        verbose_name=_("Tags"),
    )

    # --- Moderation fields ---
    is_approved = models.BooleanField(
        default=False,
        verbose_name=_("Approved"),
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_photos",
        verbose_name=_("Approved by"),
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved at"),
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name=_("Rejection reason"),
    )

    # --- Timestamps ---
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded at"),
    )

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = _("photo upload")
        verbose_name_plural = _("photo uploads")
        indexes = [
            models.Index(fields=["uploaded_by", "-uploaded_at"]),
            models.Index(fields=["is_approved", "-uploaded_at"]),
        ]

    def __str__(self) -> str:
        status = _("approved") if self.is_approved else _("pending")
        return f"Photo #{self.pk} by {self.uploaded_by} ({status})"

    @property
    def is_rejected(self) -> bool:
        """Return True if the photo has been rejected."""
        return not self.is_approved and bool(self.rejection_reason)

    @property
    def is_pending(self) -> bool:
        """Return True if the photo is awaiting moderation."""
        return not self.is_approved and not self.rejection_reason

"""
Federation models: FederatedClub, ExternalEvent, ExternalEventInterest, ExternalEventComment.
"""

import uuid

from django.conf import settings
from django.db import models


class FederatedClub(models.Model):
    """
    A partner club in the federation network.
    Only admins can create/edit these records.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Display name of the partner club")
    short_code = models.CharField(
        max_length=20, unique=True, help_text="URL-safe identifier"
    )
    base_url = models.URLField(help_text="Partner site base URL")
    logo_url = models.URLField(blank=True, help_text="Optional logo URL")
    api_key = models.CharField(
        max_length=64, help_text="Their public API key (given to us)"
    )
    our_key_for_them = models.CharField(
        max_length=64, blank=True, help_text="Our key we gave them (auto-generated)"
    )
    is_active = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    share_our_events = models.BooleanField(
        default=False, help_text="Share our events with this partner"
    )
    auto_import = models.BooleanField(
        default=True, help_text="Auto-approve imported events"
    )
    last_sync = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    class Meta:
        verbose_name = "Federated Club"
        verbose_name_plural = "Federated Clubs"
        ordering = ["name"]

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
        FederatedClub, on_delete=models.CASCADE, related_name="external_events"
    )
    external_id = models.CharField(max_length=100)
    event_name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    location_address = models.CharField(max_length=500, blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lon = models.FloatField(null=True, blank=True)
    description = models.TextField(blank=True, help_text="Sanitized HTML")
    event_status = models.CharField(
        max_length=20, choices=EVENT_STATUS_CHOICES, default="EventScheduled"
    )
    image_url = models.URLField(blank=True)
    detail_url = models.URLField(blank=True)
    is_approved = models.BooleanField(default=True)
    is_hidden = models.BooleanField(default=False)
    fetched_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "External Event"
        verbose_name_plural = "External Events"
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
    )
    external_event = models.ForeignKey(
        ExternalEvent, on_delete=models.CASCADE, related_name="interests"
    )
    interest_level = models.CharField(max_length=20, choices=INTEREST_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "External Event Interest"
        verbose_name_plural = "External Event Interests"
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
    )
    external_event = models.ForeignKey(
        ExternalEvent, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "External Event Comment"
        verbose_name_plural = "External Event Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["external_event", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.external_event}"

"""
Mutual Aid models.

Includes the Wagtail page model (MutualAidPage), privacy settings,
aid requests, federated access management, and contact unlock tracking.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


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


class MutualAidPage(Page):
    """
    Wagtail page for the mutual aid section.

    Displays a map of available helpers, a list of helpers,
    and emergency contacts.
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
    )
    show_phone_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show phone number"),
    )
    show_mobile_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show mobile number"),
    )
    show_whatsapp_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show WhatsApp availability"),
    )
    show_email_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show email address"),
    )
    show_exact_location = models.BooleanField(
        default=False,
        verbose_name=_("Show exact location"),
        help_text=_("If disabled, only the city name is shown."),
    )
    show_photo_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show profile photo"),
    )
    show_bio_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show bio"),
    )
    show_hours_on_aid = models.BooleanField(
        default=False,
        verbose_name=_("Show availability hours"),
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
    )
    requester_name = models.CharField(
        max_length=100,
        verbose_name=_("Requester name"),
    )
    requester_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Requester phone"),
    )
    requester_email = models.EmailField(
        blank=True,
        verbose_name=_("Requester email"),
    )
    requester_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aid_requests_sent",
        verbose_name=_("Requester (if member)"),
    )

    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES,
        default="other",
        verbose_name=_("Issue type"),
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
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        verbose_name=_("Status"),
    )

    # Federation fields
    is_from_federation = models.BooleanField(
        default=False,
        verbose_name=_("From federation"),
    )
    federation_access = models.ForeignKey(
        "mutual_aid.FederatedAidAccess",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="aid_requests",
        verbose_name=_("Federation access"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    )
    external_user_id = models.CharField(
        max_length=100,
        verbose_name=_("External user ID"),
    )
    external_display_name = models.CharField(
        max_length=100,
        verbose_name=_("External display name"),
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
    )
    is_active = models.BooleanField(default=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Approved by"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expires at"),
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
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Reviewed by"),
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Reviewed at"),
    )
    created_at = models.DateTimeField(auto_now_add=True)

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
    )
    helper = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="contact_unlocks_received",
        verbose_name=_("Helper"),
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)

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

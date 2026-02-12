"""
Custom user model for ClubCMS.

This module defines ClubUser which extends Django's AbstractUser.
AUTH_USER_MODEL = "members.ClubUser" is set in settings/base.py,
so this model MUST exist before any migrations can run.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalManyToManyField


class ClubUser(AbstractUser):
    """
    Extended user model for motorcycle club members.

    Adds personal data, membership card fields, address, privacy
    preferences, and mutual aid availability on top of Django's
    built-in AbstractUser.
    """

    # ---- Display name system ----
    display_name = models.CharField(
        max_length=100, blank=True, help_text="Public display name (nickname)"
    )
    show_real_name_to_members = models.BooleanField(
        default=False,
        help_text="Allow active members to see your real name",
    )

    # ---- Personal data ----
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    birth_place = models.CharField(max_length=100, blank=True)
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # ---- Identity document ----
    fiscal_code = models.CharField(max_length=16, blank=True)
    DOCUMENT_TYPES = [
        ("id_card", "ID Card"),
        ("license", "Driver's License"),
        ("passport", "Passport"),
    ]
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, blank=True
    )
    document_number = models.CharField(max_length=50, blank=True)
    document_expiry = models.DateField(null=True, blank=True)

    # ---- Address ----
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=2, blank=True)
    postal_code = models.CharField(max_length=5, blank=True)
    country = models.CharField(max_length=2, default="IT")

    # ---- Membership card ----
    card_number = models.CharField(max_length=50, blank=True, unique=True, null=True)
    membership_date = models.DateField(null=True, blank=True)
    membership_expiry = models.DateField(null=True, blank=True)

    # ---- Preferences ----
    newsletter = models.BooleanField(default=False)
    show_in_directory = models.BooleanField(default=False)
    public_profile = models.BooleanField(default=False)
    bio = models.TextField(blank=True)

    # ---- Mutual aid ----
    aid_available = models.BooleanField(default=False)
    aid_radius_km = models.PositiveIntegerField(default=25)
    aid_location_city = models.CharField(max_length=100, blank=True)
    aid_coordinates = models.CharField(
        max_length=50, blank=True, help_text="lat,lon format"
    )
    aid_notes = models.TextField(blank=True)

    # ---- Notification preferences ----
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=False)
    news_updates = models.BooleanField(default=True)
    event_updates = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    membership_alerts = models.BooleanField(default=True)
    partner_updates = models.BooleanField(default=False)
    aid_requests = models.BooleanField(default=True)
    partner_events = models.BooleanField(default=True)
    partner_event_comments = models.BooleanField(default=True)

    DIGEST_FREQUENCY_CHOICES = [
        ("immediate", "Immediate"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
    ]
    digest_frequency = models.CharField(
        max_length=10, choices=DIGEST_FREQUENCY_CHOICES, default="daily"
    )

    # ---- Products (composable membership) ----
    products = ParentalManyToManyField(
        "website.Product",
        blank=True,
        related_name="members",
        verbose_name=_("Products"),
    )

    class Meta:
        verbose_name = "Club User"
        verbose_name_plural = "Club Users"

    def __str__(self):
        return self.get_visible_name()

    def get_display_name(self):
        """Return display_name if set, otherwise first_name or username."""
        if self.display_name:
            return self.display_name
        if self.first_name:
            return self.first_name
        return self.username

    def get_visible_name(self, viewer=None):
        """
        Return the appropriate display name based on who is viewing.
        """
        if viewer and getattr(viewer, "is_staff", False):
            dn = self.display_name or ""
            return f"{self.first_name} {self.last_name} ({dn})" if dn else self.get_full_name()

        if (
            viewer
            and getattr(viewer, "is_active_member", False)
            and self.show_real_name_to_members
        ):
            return self.get_full_name()

        if self.display_name:
            return self.display_name

        last_initial = f"{self.last_name[0]}." if self.last_name else ""
        return f"{self.first_name} {last_initial}".strip()

    @property
    def is_active_member(self):
        from django.utils import timezone

        if not self.membership_expiry:
            return False
        return self.membership_expiry >= timezone.now().date()

    @property
    def is_expired(self):
        return not self.is_active_member

    @property
    def days_to_expiry(self):
        from django.utils import timezone

        if not self.membership_expiry:
            return None
        return (self.membership_expiry - timezone.now().date()).days

    @property
    def can_vote(self):
        return self.products.filter(grants_vote=True).exists()

    @property
    def can_upload(self):
        return self.products.filter(grants_upload=True).exists()

    @property
    def can_register_events(self):
        return self.products.filter(grants_events=True).exists()

    @property
    def max_discount_percent(self):
        result = self.products.filter(grants_discount=True).aggregate(
            max_discount=models.Max("discount_percent")
        )
        return result["max_discount"] or 0

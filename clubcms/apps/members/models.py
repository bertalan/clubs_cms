"""
Custom user model for ClubCMS.

This module defines ClubUser which extends Django's AbstractUser.
AUTH_USER_MODEL = "members.ClubUser" is set in settings/base.py,
so this model MUST exist before any migrations can run.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class ClubUser(AbstractUser):
    """
    Extended user model for motorcycle club members.

    Adds personal data, membership card fields, address, privacy
    preferences, and mutual aid availability on top of Django's
    built-in AbstractUser.
    """

    # ---- Display name system ----
    display_name = models.CharField(
        max_length=100, blank=True,
        help_text=_("Choose a nickname that will be shown publicly instead of your real name."),
    )
    show_real_name_to_members = models.BooleanField(
        default=False,
        help_text=_("When enabled, active members can see your real first and last name."),
    )

    # ---- Personal data ----
    phone = models.CharField(
        max_length=30, blank=True,
        help_text=_("Landline number with country prefix. Example: +39 02 1234567"),
    )
    mobile = models.CharField(
        max_length=30, blank=True,
        help_text=_("Mobile number with country prefix. Example: +39 333 1234567"),
    )
    birth_date = models.DateField(
        null=True, blank=True,
        help_text=_("Your date of birth. Used for birthday greetings and age-restricted events."),
    )
    birth_place = models.CharField(
        max_length=100, blank=True,
        help_text=_("City or town where you were born."),
    )
    photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Foto profilo del socio."),
    )

    # ---- Identity document ----
    fiscal_code = models.CharField(max_length=16, blank=True,
        help_text=_("Codice fiscale italiano (16 caratteri)."),
    )
    DOCUMENT_TYPES = [
        ("id_card", "ID Card"),
        ("license", "Driver's License"),
        ("passport", "Passport"),
    ]
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPES, blank=True,
        help_text=_("Tipo di documento di identità."),
    )
    document_number = models.CharField(max_length=50, blank=True,
        help_text=_("Numero del documento di identità."),
    )
    document_expiry = models.DateField(null=True, blank=True,
        help_text=_("Data di scadenza del documento."),
    )

    # ---- Address ----
    address = models.CharField(
        max_length=255, blank=True,
        help_text=_("Street address. Example: Via Roma 42"),
    )
    city = models.CharField(
        max_length=100, blank=True,
        help_text=_("City or town of residence."),
    )
    province = models.CharField(
        max_length=2, blank=True,
        help_text=_("Two-letter province code. Example: MI"),
    )
    postal_code = models.CharField(
        max_length=5, blank=True,
        help_text=_("5-digit postal code. Example: 20100"),
    )
    country = models.CharField(
        max_length=2, default="IT",
        help_text=_("Two-letter country code (ISO 3166-1). Example: IT"),
    )

    # ---- Membership card ----
    card_number = models.CharField(max_length=50, blank=True, unique=True, null=True,
        help_text=_("Numero tessera socio (generato automaticamente)."),
    )
    membership_date = models.DateField(null=True, blank=True,
        help_text=_("Data di prima iscrizione al club."),
    )
    membership_expiry = models.DateField(null=True, blank=True,
        help_text=_("Data di scadenza della tessera."),
    )
    
    CARD_STATUS_CHOICES = [
        ("active", _("Active")),
        ("suspended", _("Suspended")),
        ("terminated", _("Terminated")),
    ]
    card_status = models.CharField(
        max_length=20,
        choices=CARD_STATUS_CHOICES,
        default="active",
        help_text=_("Status of the membership card. Suspended cards can be reactivated."),
    )
    card_status_reason = models.TextField(
        blank=True,
        help_text=_("Reason for suspension or termination."),
    )
    card_status_changed = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When the card status was last changed."),
    )

    # ---- Preferences ----
    newsletter = models.BooleanField(
        default=False,
        help_text=_("Receive our periodic newsletter with club news and upcoming events."),
    )
    show_in_directory = models.BooleanField(
        default=False,
        help_text=_("When enabled, your display name appears in the member directory visible to other members."),
    )
    public_profile = models.BooleanField(
        default=False,
        help_text=_("When enabled, your profile page is visible to anyone, including non-members."),
    )
    bio = models.TextField(
        blank=True,
        help_text=_("A short description about yourself. Visible on your profile page."),
    )

    # ---- Mutual aid ----
    aid_available = models.BooleanField(
        default=False,
        help_text=_("Enable this to appear in the mutual aid helper directory."),
    )
    aid_radius_km = models.PositiveIntegerField(
        default=25,
        help_text=_("Maximum distance in km you are willing to travel to help. Example: 25"),
    )
    aid_location_city = models.CharField(
        max_length=100, blank=True,
        help_text=_("The city where you are usually based for mutual aid."),
    )
    aid_coordinates = models.CharField(
        max_length=50, blank=True,
        help_text=_("Latitude and longitude, comma-separated. Example: 45.4642,9.1900"),
    )
    aid_notes = models.TextField(
        blank=True,
        help_text=_("Additional information: tools, skills, vehicle type, availability hours."),
    )

    # ---- Notification preferences ----
    email_notifications = models.BooleanField(
        default=True,
        help_text=_("Receive notifications via email."),
    )
    push_notifications = models.BooleanField(
        default=False,
        help_text=_("Receive push notifications in your browser (requires PWA support)."),
    )
    news_updates = models.BooleanField(
        default=True,
        help_text=_("Get notified when new articles or announcements are published."),
    )
    event_updates = models.BooleanField(
        default=True,
        help_text=_("Get notified about new events and changes to events you registered for."),
    )
    event_reminders = models.BooleanField(
        default=True,
        help_text=_("Receive a reminder before events you are registered for."),
    )
    membership_alerts = models.BooleanField(
        default=True,
        help_text=_("Alerts about membership expiry, renewal, and card updates."),
    )
    partner_updates = models.BooleanField(
        default=False,
        help_text=_("News and promotions from partner clubs."),
    )
    aid_requests = models.BooleanField(
        default=True,
        help_text=_("Notifications when someone nearby requests mutual aid."),
    )
    partner_events = models.BooleanField(
        default=True,
        help_text=_("Events published by federated partner clubs."),
    )
    partner_event_comments = models.BooleanField(
        default=True,
        help_text=_("Comments on partner events you showed interest in."),
    )

    DIGEST_FREQUENCY_CHOICES = [
        ("immediate", _("Immediate")),
        ("daily", _("Daily")),
        ("weekly", _("Weekly")),
    ]
    digest_frequency = models.CharField(
        max_length=10, choices=DIGEST_FREQUENCY_CHOICES, default="daily",
        help_text=_("How often to receive a digest email summarising your notifications."),
    )

    # ---- Products (composable membership) ----
    products = models.ManyToManyField(
        "website.Product",
        blank=True,
        related_name="members",
        verbose_name=_("Products"),
        help_text=_("Prodotti/abbonamenti acquistati dal socio."),
    )

    class Meta:
        verbose_name = _("Club User")
        verbose_name_plural = _("Club Users")

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
        if self.card_status != "active":
            return False
        return self.membership_expiry >= timezone.localdate()

    @property
    def is_expired(self):
        return not self.is_active_member

    @property
    def days_to_expiry(self):
        from django.utils import timezone

        if not self.membership_expiry:
            return None
        return (self.membership_expiry - timezone.localdate()).days

    @property
    def can_vote(self):
        if not self.products.exists():
            return True
        return self.products.filter(grants_vote=True).exists()

    @property
    def can_upload(self):
        if not self.products.exists():
            return True
        return self.products.filter(grants_upload=True).exists()

    @property
    def can_register_events(self):
        # If the user has no products assigned, no restriction applies.
        if not self.products.exists():
            return True
        return self.products.filter(grants_events=True).exists()

    @property
    def max_discount_percent(self):
        result = self.products.filter(grants_discount=True).aggregate(
            max_discount=models.Max("discount_percent")
        )
        return result["max_discount"] or 0

    def issue_card(self, validity_days=365, force_new=False):
        """
        Issue a new membership card to the user.
        
        Generates card_number if not present, sets membership_date to today,
        and sets expiry to validity_days from today.
        
        Args:
            validity_days: Number of days the card is valid (default 365).
            force_new: If True, issues a new card number even if one exists
                       (used when re-issuing after termination).
        
        Returns True if card was issued, False if user already has an active card.
        """
        from django.utils import timezone
        import random

        # Don't re-issue if already has active card (unless forcing)
        if self.card_number and self.card_status == "active" and self.is_active_member and not force_new:
            return False

        # Generate new card number if needed or forcing new card
        if not self.card_number or force_new:
            year = timezone.now().year
            # Generate unique sequence
            existing = ClubUser.objects.filter(
                card_number__startswith=f"AQR-{year}-"
            ).count()
            seq = existing + 1001
            self.card_number = f"AQR-{year}-{seq:04d}"

        # Set membership dates
        today = timezone.localdate()
        if not self.membership_date or force_new:
            self.membership_date = today
        
        self.membership_expiry = today + timezone.timedelta(days=validity_days)
        
        # Reset card status to active
        self.card_status = "active"
        self.card_status_reason = ""
        self.card_status_changed = timezone.now()
        
        self.save()
        return True

    def renew_card(self, validity_days=365):
        """
        Renew an existing membership card.
        
        Extends expiry from current expiry date (if in future) or from today.
        Returns True if renewed, False if no card exists.
        """
        from django.utils import timezone

        if not self.card_number:
            return False

        today = timezone.localdate()
        
        # Extend from current expiry if still valid, otherwise from today
        if self.membership_expiry and self.membership_expiry > today:
            base_date = self.membership_expiry
        else:
            base_date = today
        
        self.membership_expiry = base_date + timezone.timedelta(days=validity_days)
        self.save()
        return True

    def get_qr_data(self):
        """
        Return vCard data for QR code generation.
        """
        from django.utils import timezone
        
        expiry_str = self.membership_expiry.strftime("%d/%m/%Y") if self.membership_expiry else ""
        
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{self.get_full_name()}
ORG:Moto Club Aquile Rosse
TEL:{self.phone or self.mobile or ''}
EMAIL:{self.email}
NOTE:Card: {self.card_number} - Expires: {expiry_str}
END:VCARD"""
        return vcard


# ---------------------------------------------------------------------------
# MembershipRequest — Request to purchase a membership product
# ---------------------------------------------------------------------------


class MembershipRequest(models.Model):
    """
    Tracks membership purchase requests from users.

    Flow:
    1. User selects a product and submits a request
    2. Admin reviews and approves/rejects
    3. If approved, the product is assigned and card generated
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("cancelled", _("Cancelled")),
    ]

    user = models.ForeignKey(
        ClubUser,
        on_delete=models.CASCADE,
        related_name="membership_requests",
        verbose_name=_("User"),
        help_text=_("Socio che ha inviato la richiesta."),
    )
    product = models.ForeignKey(
        "website.Product",
        on_delete=models.CASCADE,
        related_name="membership_requests",
        verbose_name=_("Product"),
        help_text=_("Prodotto/abbonamento richiesto."),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        help_text=_("Stato della richiesta di adesione."),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Any additional information or requests."),
    )
    admin_notes = models.TextField(
        blank=True,
        verbose_name=_("Admin Notes"),
        help_text=_("Internal notes for administrators."),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created"),
        help_text=_("Data e ora di invio della richiesta."),
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated"),
        help_text=_("Data e ora dell'ultimo aggiornamento."),
    )
    processed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Processed at"),
        help_text=_("Data e ora di elaborazione da parte dell'admin."),
    )
    processed_by = models.ForeignKey(
        ClubUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="processed_requests",
        verbose_name=_("Processed by"),
        help_text=_("Amministratore che ha gestito la richiesta."),
    )

    class Meta:
        verbose_name = _("Membership Request")
        verbose_name_plural = _("Membership Requests")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.get_status_display()})"

    def approve(self, admin_user=None):
        """
        Approve the request and assign the product to the user.
        Also generates a card number if the user doesn't have one.
        """
        from django.utils import timezone
        from datetime import timedelta

        if self.status != "pending":
            return False

        # Assign product to user
        self.user.products.add(self.product)

        # Generate card number if needed
        if not self.user.card_number:
            import random
            year = timezone.now().year
            seq = random.randint(1000, 9999)
            self.user.card_number = f"AQR-{year}-{seq}"

        # Set membership dates if not set
        if not self.user.membership_date:
            self.user.membership_date = timezone.localdate()

        # Extend expiry using product's validity_days
        validity_days = getattr(self.product, 'validity_days', 365)
        if self.user.membership_expiry and self.user.membership_expiry > timezone.localdate():
            new_expiry = self.user.membership_expiry + timedelta(days=validity_days)
        else:
            new_expiry = timezone.localdate() + timedelta(days=validity_days)
        self.user.membership_expiry = new_expiry

        self.user.save()

        # Update request status
        self.status = "approved"
        self.processed_at = timezone.now()
        self.processed_by = admin_user
        self.save()

        return True

    def reject(self, admin_user=None, reason=""):
        """Reject the membership request."""
        from django.utils import timezone

        if self.status != "pending":
            return False

        self.status = "rejected"
        self.processed_at = timezone.now()
        self.processed_by = admin_user
        if reason:
            self.admin_notes = reason
        self.save()

        return True

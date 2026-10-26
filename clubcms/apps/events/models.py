"""
Models for the events app.

Provides EventRegistration for event sign-ups, PricingTier for
time-based pricing (as an Orderable linked to EventDetailPage),
and EventFavorite for user bookmarks.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel


# ---------------------------------------------------------------------------
# Status choices
# ---------------------------------------------------------------------------

REGISTRATION_STATUS_CHOICES = [
    ("registered", _("Registered")),
    ("confirmed", _("Confirmed")),
    ("cancelled", _("Cancelled")),
    ("waitlist", _("Waitlist")),
]

PAYMENT_STATUS_CHOICES = [
    ("pending", _("Pending")),
    ("paid", _("Paid")),
    ("refunded", _("Refunded")),
    ("expired", _("Expired")),
]

PAYMENT_PROVIDER_CHOICES = [
    ("stripe", _("Stripe")),
    ("paypal", _("PayPal")),
    ("bank_transfer", _("Bank Transfer")),
    ("free", _("Free")),
]


# ---------------------------------------------------------------------------
# 1. EventRegistration
# ---------------------------------------------------------------------------


class EventRegistration(models.Model):
    """
    Tracks a user's registration for an event.

    Supports both authenticated users and guest registrations (user=null).
    Includes optional passenger/companion information for motorcycle events.
    """

    event = models.ForeignKey(
        "website.EventDetailPage",
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name=_("Event"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_registrations",
        verbose_name=_("User"),
        help_text=_(
            "Empty for a guest registration. The guest's name and email are "
            "then in the Guest info tab."
        ),
    )
    status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS_CHOICES,
        default="registered",
        verbose_name=_("Status"),
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Registered at"),
    )
    guests = models.IntegerField(
        default=0,
        verbose_name=_("Number of guests"),
        help_text=_(
            "Extra people coming with the registrant, not counting a passenger. "
            "Each one is charged the per-person price at registration."
        ),
    )
    guest_names = models.TextField(
        blank=True,
        verbose_name=_("Guest names"),
        help_text=_("Names of the extra people, one per line."),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_(
            "Written by the registrant: allergies, dietary needs or other "
            "requests for the organizers."
        ),
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
        verbose_name=_("Payment status"),
    )
    payment_provider = models.CharField(
        max_length=20,
        choices=PAYMENT_PROVIDER_CHOICES,
        blank=True,
        default="",
        verbose_name=_("Payment provider"),
    )
    payment_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Payment ID"),
    )
    payment_session_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Payment session ID"),
    )
    payment_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name=_("Payment amount"),
    )
    payment_reference = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Payment reference"),
    )
    payment_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Payment expires at"),
    )

    # ---- Guest registration fields (when user is null) ----
    email = models.CharField(
        max_length=254,
        blank=True,
        verbose_name=_("Email"),
        help_text=_(
            "Guest registrations only. The registration confirmation is sent "
            "to this address."
        ),
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("First name"),
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Last name"),
    )

    # ---- Passenger / companion fields ----
    has_passenger = models.BooleanField(
        default=False,
        verbose_name=_("Has passenger"),
    )
    passenger_is_member = models.BooleanField(
        default=False,
        verbose_name=_("Passenger is a member"),
        help_text=_(
            "If on, the passenger is picked in Passenger (member). If off, the "
            "passenger's details are typed in the fields below."
        ),
    )
    passenger_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="passenger_registrations",
        verbose_name=_("Passenger (member)"),
    )
    passenger_first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Passenger first name"),
    )
    passenger_last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name=_("Passenger last name"),
    )
    passenger_email = models.CharField(
        max_length=254,
        blank=True,
        verbose_name=_("Passenger email"),
    )
    passenger_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("Passenger phone"),
    )
    passenger_fiscal_code = models.CharField(
        max_length=16,
        blank=True,
        verbose_name=_("Passenger fiscal code"),
        help_text=_("Italian tax code, 16 characters. Example: VRDMRC85M01H501Z"),
    )
    passenger_birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Passenger birth date"),
    )
    passenger_emergency_contact = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Passenger emergency contact"),
        help_text=_(
            "Name and phone number to call in an emergency. "
            "Example: Anna Verdi +39 340 7654321"
        ),
    )

    class Meta:
        verbose_name = _("Event Registration")
        verbose_name_plural = _("Event Registrations")
        ordering = ["-registered_at"]

    def __str__(self):
        user_display = self.user or self.email or _("Guest")
        return f"{user_display} - {self.event} ({self.status})"


# ---------------------------------------------------------------------------
# 2. PricingTier (Orderable, linked to EventDetailPage)
# ---------------------------------------------------------------------------


class PricingTier(ClusterableModel):
    """
    Time-based pricing tier for an event.

    Each tier defines a time offset before the event start and an
    associated discount.  Tiers are evaluated from the longest offset
    to the shortest: the first tier whose deadline has not yet passed
    is the active one.
    """

    event_page = ParentalKey(
        "website.EventDetailPage",
        on_delete=models.CASCADE,
        related_name="pricing_tiers",
        verbose_name=_("Event page"),
    )
    days_before = models.IntegerField(
        default=0,
        verbose_name=_("Days before event"),
        help_text=_(
            "Days, hours and minutes together set when this tier ends, counted "
            "back from the event start. The total must be greater than zero."
        ),
    )
    hours_before = models.IntegerField(
        default=0,
        verbose_name=_("Hours before event"),
    )
    minutes_before = models.IntegerField(
        default=0,
        verbose_name=_("Minutes before event"),
    )
    discount_percent = models.IntegerField(
        default=0,
        verbose_name=_("Discount percent"),
        help_text=_(
            "Discount on the base fee while this tier is active, added to any "
            "member discount. Example: 20"
        ),
    )
    label = models.CharField(
        max_length=100,
        verbose_name=_("Label"),
        help_text=_(
            "Shown with the price on the registration form while this tier is "
            "active. Example: Early bird"
        ),
    )
    is_deadline = models.BooleanField(
        default=False,
        verbose_name=_("Is registration deadline"),
        help_text=_("If checked, registration closes when this tier expires."),
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("days_before"),
        FieldPanel("hours_before"),
        FieldPanel("minutes_before"),
        FieldPanel("discount_percent"),
        FieldPanel("is_deadline"),
    ]

    class Meta:
        verbose_name = _("Pricing Tier")
        verbose_name_plural = _("Pricing Tiers")
        ordering = ["-days_before", "-hours_before", "-minutes_before"]

    def __str__(self):
        return f"{self.label} ({self.discount_percent}%)"

    @property
    def total_minutes(self):
        """Return the total offset in minutes for comparison."""
        return (self.days_before * 1440) + (self.hours_before * 60) + self.minutes_before

    def clean(self):
        super().clean()
        if self.total_minutes <= 0:
            raise ValidationError(
                _("The time offset must be greater than zero.")
            )


# ---------------------------------------------------------------------------
# 3. EventFavorite
# ---------------------------------------------------------------------------


class EventFavorite(models.Model):
    """
    Allows a user to bookmark / favorite an event.

    Unique together on (user, event) prevents duplicate bookmarks.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_events",
        verbose_name=_("User"),
    )
    event = models.ForeignKey(
        "website.EventDetailPage",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name=_("Event"),
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Added at"),
    )

    class Meta:
        verbose_name = _("Event Favorite")
        verbose_name_plural = _("Event Favorites")
        unique_together = [("user", "event")]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user} - {self.event}"

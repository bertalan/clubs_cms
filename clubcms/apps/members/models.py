"""
Custom user model for ClubCMS.

This module defines ClubUser which extends Django's AbstractUser.
AUTH_USER_MODEL = "members.ClubUser" is set in settings/base.py,
so this model MUST exist before any migrations can run.

Also defines MembersAreaPage — a RoutablePageMixin page that serves
all member-account views (profile, card, directory, etc.) as sub-routes.
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from wagtail.models import Page


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


# ═══════════════════════════════════════════════════════════════════════════
# MembersAreaPage — RoutablePageMixin page for all account views
# ═══════════════════════════════════════════════════════════════════════════


class MembersAreaPage(RoutablePageMixin, Page):
    """
    Container page for all member-account views.

    Routes:
        /                       — landing (card overview if logged in)
        /profile/               — edit profile (login required)
        /card/                  — digital membership card (login required)
        /privacy/               — privacy settings (login required)
        /notifications/         — notification preferences (login required)
        /aid/                   — mutual-aid availability (login required)
        /directory/             — member directory (login required)
        /membership-request/<id>/ — request a product (login required)
        /membership-requests/   — user's request history (login required)
        /<username>/            — public profile (public)
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Introductory text displayed on the members area landing page."),
    )
    directory_intro = RichTextField(
        blank=True,
        verbose_name=_("Directory introduction"),
        help_text=_("Text shown at the top of the member directory."),
    )
    card_help_text = RichTextField(
        blank=True,
        verbose_name=_("Card help text"),
        help_text=_("Help text displayed on the membership card page."),
    )

    max_count = 1
    parent_page_types = ["wagtailcore.Page", "website.HomePage"]
    subpage_types = []
    template = "members/pages/members_area_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("directory_intro"),
        FieldPanel("card_help_text"),
    ]

    class Meta:
        verbose_name = _("Members Area Page")
        verbose_name_plural = _("Members Area Pages")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _login_required(self, request):
        """Return a redirect to login if user is not authenticated, else None."""
        if not request.user.is_authenticated:
            from django.conf import settings as django_settings
            from django.shortcuts import redirect

            login_url = getattr(django_settings, "LOGIN_URL", "/account/login/")
            return redirect(f"{login_url}?next={request.path}")
        return None

    # ------------------------------------------------------------------
    # Landing
    # ------------------------------------------------------------------

    @route(r"^$")
    def landing_view(self, request):
        if request.user.is_authenticated:
            from django.shortcuts import redirect

            return redirect(self.url + self.reverse_subpage("card"))
        return self.render(request)

    # ------------------------------------------------------------------
    # Profile
    # ------------------------------------------------------------------

    @route(r"^profile/$", name="profile")
    def profile_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.contrib import messages

        from apps.members.forms import ProfileForm

        user = request.user
        if request.method == "POST":
            form = ProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _("Profile updated successfully."))
                from django.shortcuts import redirect

                return redirect(self.url + self.reverse_subpage("profile"))
        else:
            form = ProfileForm(instance=user)

        return self.render(
            request,
            template="account/profile.html",
            context_overrides={"form": form, "page": self},
        )

    # ------------------------------------------------------------------
    # Card
    # ------------------------------------------------------------------

    @route(r"^card/$", name="card")
    def card_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        import os

        from django.conf import settings

        user = request.user
        ctx = {
            "user": user,
            "club_name": getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS"),
            "page": self,
        }

        # User's products
        if hasattr(user, "products"):
            ctx["user_products"] = user.products.all()
        else:
            ctx["user_products"] = []

        # Available products for purchase
        from apps.website.models.snippets import Product
        from wagtail.models import Locale

        locale = Locale.get_active()
        ctx["available_products"] = Product.objects.filter(
            is_active=True, locale=locale
        ).order_by("order")

        # QR code and barcode images
        if user.card_number:
            safe_name = user.card_number.replace("/", "-").replace("\\", "-")
            qr_path = os.path.join("members", "qr", f"{safe_name}.png")
            barcode_path = os.path.join("members", "barcode", f"{safe_name}.png")
            qr_full = os.path.join(settings.MEDIA_ROOT, qr_path)
            barcode_full = os.path.join(settings.MEDIA_ROOT, barcode_path)
            if os.path.exists(qr_full):
                ctx["qr_url"] = settings.MEDIA_URL + qr_path
            if os.path.exists(barcode_full):
                ctx["barcode_url"] = settings.MEDIA_URL + barcode_path

        # Membership request status for banner
        from datetime import timedelta

        from django.utils import timezone

        ctx["pending_requests"] = MembershipRequest.objects.filter(
            user=user, status="pending"
        ).select_related("product")
        thirty_days_ago = timezone.now() - timedelta(days=30)
        ctx["recent_resolved"] = (
            MembershipRequest.objects.filter(
                user=user,
                status__in=["approved", "rejected"],
                processed_at__gte=thirty_days_ago,
            )
            .select_related("product")
            .order_by("-processed_at")[:3]
        )

        return self.render(
            request,
            template="account/card.html",
            context_overrides=ctx,
        )

    # ------------------------------------------------------------------
    # Privacy
    # ------------------------------------------------------------------

    @route(r"^privacy/$", name="privacy")
    def privacy_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.contrib import messages

        from apps.members.forms import PrivacySettingsForm

        user = request.user
        if request.method == "POST":
            form = PrivacySettingsForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _("Privacy settings saved."))
                from django.shortcuts import redirect

                return redirect(self.url + self.reverse_subpage("privacy"))
        else:
            form = PrivacySettingsForm(instance=user)

        return self.render(
            request,
            template="account/privacy.html",
            context_overrides={"form": form, "page": self},
        )

    # ------------------------------------------------------------------
    # Notification preferences
    # ------------------------------------------------------------------

    @route(r"^notifications/preferences/$", name="notification_prefs")
    def notification_prefs_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.conf import settings as django_settings
        from django.contrib import messages

        from apps.members.forms import NotificationPreferencesForm

        user = request.user
        if request.method == "POST":
            form = NotificationPreferencesForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _("Notification preferences saved."))
                from django.shortcuts import redirect

                return redirect(
                    self.url + self.reverse_subpage("notification_prefs")
                )
        else:
            form = NotificationPreferencesForm(instance=user)

        vapid = getattr(django_settings, "WEBPUSH_SETTINGS", {})
        return self.render(
            request,
            template="account/notifications.html",
            context_overrides={
                "form": form,
                "page": self,
                "vapid_public_key": vapid.get("VAPID_PUBLIC_KEY", ""),
            },
        )

    # ------------------------------------------------------------------
    # Mutual-aid availability
    # ------------------------------------------------------------------

    @route(r"^aid/$", name="aid")
    def aid_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.contrib import messages

        from apps.members.forms import AidAvailabilityForm

        user = request.user
        if request.method == "POST":
            form = AidAvailabilityForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, _("Mutual aid availability saved."))
                from django.shortcuts import redirect

                return redirect(self.url + self.reverse_subpage("aid"))
        else:
            form = AidAvailabilityForm(instance=user)

        ctx = {"form": form, "page": self}
        coords = user.aid_coordinates
        if coords and "," in coords:
            parts = coords.split(",", 1)
            try:
                ctx["initial_lat"] = float(parts[0].strip())
                ctx["initial_lng"] = float(parts[1].strip())
            except (ValueError, IndexError):
                pass

        return self.render(
            request,
            template="account/aid.html",
            context_overrides=ctx,
        )

    # ------------------------------------------------------------------
    # Member directory
    # ------------------------------------------------------------------

    @route(r"^directory/$", name="directory")
    def directory_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.core.paginator import Paginator

        qs = ClubUser.objects.filter(
            show_in_directory=True, is_active=True
        ).order_by("last_name", "first_name")

        paginator = Paginator(qs, 30)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        viewer = request.user
        for member in page_obj:
            member.visible_name = member.get_visible_name(viewer=viewer)

        return self.render(
            request,
            template="account/directory.html",
            context_overrides={
                "members": page_obj,
                "page_obj": page_obj,
                "is_paginated": page_obj.has_other_pages(),
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Membership request (create)
    # ------------------------------------------------------------------

    @route(r"^membership-request/(?P<product_id>\d+)/$", name="membership_request")
    def membership_request_view(self, request, product_id):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.contrib import messages
        from django.http import Http404
        from django.shortcuts import redirect

        from apps.website.models.snippets import Product

        product_id = int(product_id)
        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            raise Http404(_("Product not found."))

        user = request.user
        card_url = self.url + self.reverse_subpage("card")

        # Already has this product
        if product in user.products.all():
            messages.info(request, _("You already have this membership."))
            return redirect(card_url)

        # Pending request exists
        pending = MembershipRequest.objects.filter(
            user=user, product=product, status="pending"
        ).exists()
        if pending:
            messages.info(
                request,
                _("You already have a pending request for this product."),
            )
            return redirect(card_url)

        if request.method == "POST":
            notes = request.POST.get("notes", "").strip()
            MembershipRequest.objects.create(
                user=user, product=product, notes=notes
            )
            messages.success(
                request,
                _(
                    "Your membership request has been submitted! "
                    "The club will contact you shortly."
                ),
            )
            return redirect(card_url)

        return self.render(
            request,
            template="account/membership_request.html",
            context_overrides={
                "product": product,
                "user_products": user.products.all(),
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Membership requests (list)
    # ------------------------------------------------------------------

    @route(r"^membership-requests/$", name="membership_requests")
    def membership_requests_view(self, request):
        redir = self._login_required(request)
        if redir:
            return redir

        requests_qs = MembershipRequest.objects.filter(
            user=request.user
        ).order_by("-created_at")

        active = [r for r in requests_qs if r.status == "pending"]
        archived = [r for r in requests_qs if r.status != "pending"]

        return self.render(
            request,
            template="account/membership_requests.html",
            context_overrides={
                "requests": requests_qs,
                "active_requests": active,
                "archived_requests": archived,
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Membership request detail (single)
    # ------------------------------------------------------------------

    @route(r"^request/(?P<pk>\d+)/$", name="request_detail")
    def request_detail_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.http import Http404

        try:
            membership_req = MembershipRequest.objects.select_related(
                "product"
            ).get(pk=pk, user=request.user)
        except MembershipRequest.DoesNotExist:
            raise Http404

        # Build stepper steps
        steps = [
            {
                "label": _("Submitted"),
                "date": membership_req.created_at,
                "done": True,
            },
            {
                "label": _("Under Review"),
                "date": None,
                "done": membership_req.status != "pending",
            },
        ]
        if membership_req.status == "approved":
            steps.append(
                {
                    "label": _("Approved"),
                    "date": membership_req.processed_at,
                    "done": True,
                }
            )
        elif membership_req.status == "rejected":
            steps.append(
                {
                    "label": _("Rejected"),
                    "date": membership_req.processed_at,
                    "done": True,
                }
            )
        elif membership_req.status == "cancelled":
            steps.append(
                {
                    "label": _("Cancelled"),
                    "date": membership_req.updated_at,
                    "done": True,
                }
            )
        else:
            steps.append(
                {
                    "label": _("Decision"),
                    "date": None,
                    "done": False,
                }
            )

        return self.render(
            request,
            template="account/request_detail.html",
            context_overrides={
                "membership_req": membership_req,
                "steps": steps,
                "page": self,
            },
        )

    # ------------------------------------------------------------------
    # Cancel membership request
    # ------------------------------------------------------------------

    @route(r"^request/(?P<pk>\d+)/cancel/$", name="cancel_request")
    def cancel_request_view(self, request, pk):
        redir = self._login_required(request)
        if redir:
            return redir

        from django.http import Http404
        from django.shortcuts import redirect
        from django.views.decorators.http import require_POST

        if request.method != "POST":
            raise Http404

        try:
            membership_req = MembershipRequest.objects.get(
                pk=pk, user=request.user, status="pending"
            )
        except MembershipRequest.DoesNotExist:
            raise Http404

        from django.contrib import messages

        membership_req.status = "cancelled"
        membership_req.save(update_fields=["status", "updated_at"])
        messages.success(request, _("Your membership request has been cancelled."))
        return redirect(
            self.url + self.reverse_subpage("membership_requests")
        )

    # ------------------------------------------------------------------
    # Public profile (no login required)
    # ------------------------------------------------------------------

    @route(r"^(?P<username>[\w.@+-]+)/$", name="public_profile")
    def public_profile_view(self, request, username):
        from django.http import Http404

        try:
            member = ClubUser.objects.get(
                username=username, public_profile=True, is_active=True
            )
        except ClubUser.DoesNotExist:
            raise Http404

        viewer = request.user if request.user.is_authenticated else None
        visible_name = member.get_visible_name(viewer=viewer)

        return self.render(
            request,
            template="account/public_profile.html",
            context_overrides={
                "member": member,
                "visible_name": visible_name,
                "page": self,
            },
        )

"""
Wagtail Site Settings for the Club CMS.

Uses ``BaseSiteSetting`` so each Wagtail Site can have its own configuration.
Access in templates via ``{{ settings.website.SiteSettings }}``.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField


THEME_CHOICES = [
    ("velocity", _("Velocity")),
    ("heritage", _("Heritage")),
    ("terra", _("Terra / Eco")),
    ("zen", _("Zen")),
    ("clubs", _("Clubs")),
    ("tricolore", _("Tricolore")),
]

CAPTCHA_PROVIDER_CHOICES = [
    ("honeypot", _("Honeypot (no external service)")),
    ("turnstile", _("Cloudflare Turnstile")),
    ("hcaptcha", _("hCaptcha")),
]

MAP_ROUTING_CHOICES = [
    ("openstreetmap", _("OpenStreetMap")),
    ("google", _("Google Maps")),
    ("mapbox", _("Mapbox")),
]


@register_setting
class SiteSettings(BaseSiteSetting):
    """
    Per-site configuration panel available under Settings -> Site Settings
    in the Wagtail admin.

    Organised into tabs: General, Theme, Branding, Contact, Social,
    Navigation, PWA, Forms, Map.
    """

    # -- General tab --------------------------------------------------------
    site_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("Site name"),
        help_text=_("Human-readable name shown in the header / meta tags."),
    )
    tagline = models.CharField(
        max_length=255, blank=True, verbose_name=_("Tagline"),
    )
    description = models.TextField(
        blank=True, verbose_name=_("Site description"),
        help_text=_("Default meta description for SEO."),
    )

    # -- Theme tab ----------------------------------------------------------
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default="velocity",
        verbose_name=_("Theme"),
    )
    color_scheme = models.ForeignKey(
        "website.ColorScheme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Colour scheme"),
    )

    # -- Branding tab -------------------------------------------------------
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
    )
    logo_dark = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo (dark variant)"),
        help_text=_("Optional dark-background version of the logo."),
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Favicon"),
    )

    # -- Contact tab --------------------------------------------------------
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Opening hours"),
    )

    # -- Social tab ---------------------------------------------------------
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter / X URL"))
    youtube_url = models.URLField(blank=True, verbose_name=_("YouTube URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))
    tiktok_url = models.URLField(blank=True, verbose_name=_("TikTok URL"))

    # -- Navigation tab -----------------------------------------------------
    navbar = models.ForeignKey(
        "website.Navbar",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Navbar"),
    )
    footer = models.ForeignKey(
        "website.Footer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Footer"),
    )

    # -- PWA tab ------------------------------------------------------------
    pwa_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("PWA name"),
    )
    pwa_short_name = models.CharField(
        max_length=50, blank=True, verbose_name=_("PWA short name"),
    )
    pwa_description = models.TextField(
        blank=True, verbose_name=_("PWA description"),
    )
    pwa_icon_192 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("PWA icon 192x192"),
    )
    pwa_icon_512 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("PWA icon 512x512"),
    )
    pwa_theme_color = models.CharField(
        max_length=7, default="#0F172A", verbose_name=_("PWA theme colour"),
    )
    pwa_background_color = models.CharField(
        max_length=7, default="#FFFFFF", verbose_name=_("PWA background colour"),
    )

    # -- Forms tab ----------------------------------------------------------
    captcha_provider = models.CharField(
        max_length=20,
        choices=CAPTCHA_PROVIDER_CHOICES,
        default="honeypot",
        verbose_name=_("CAPTCHA provider"),
    )
    captcha_site_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("CAPTCHA site key"),
    )
    captcha_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("CAPTCHA secret key"),
    )

    # -- Map tab ------------------------------------------------------------
    map_routing_service = models.CharField(
        max_length=20,
        choices=MAP_ROUTING_CHOICES,
        default="openstreetmap",
        verbose_name=_("Map routing service"),
    )
    map_api_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Map API key"),
        help_text=_("Required for Google Maps / Mapbox."),
    )
    map_default_center = models.CharField(
        max_length=100, blank=True, verbose_name=_("Default map centre"),
        help_text=_("Latitude,Longitude (e.g. '45.4642,9.1900')."),
    )
    map_default_zoom = models.IntegerField(
        default=10, verbose_name=_("Default map zoom"),
    )

    # -- Computed helpers ---------------------------------------------------

    @property
    def map_latitude(self):
        """Return latitude from map_default_center, or empty string."""
        if self.map_default_center and "," in self.map_default_center:
            return self.map_default_center.split(",")[0].strip()
        return ""

    @property
    def map_longitude(self):
        """Return longitude from map_default_center, or empty string."""
        if self.map_default_center and "," in self.map_default_center:
            return self.map_default_center.split(",")[1].strip()
        return ""

    @property
    def map_embed_url(self):
        """Return an OpenStreetMap embed URL centred on map_default_center."""
        lat = self.map_latitude
        lng = self.map_longitude
        if not lat or not lng:
            return ""
        try:
            flat, flng = float(lat), float(lng)
        except (ValueError, TypeError):
            return ""
        offset = 0.007  # ~500 m
        bbox = f"{flng - offset:.4f},{flat - offset:.4f},{flng + offset:.4f},{flat + offset:.4f}"
        return (
            f"https://www.openstreetmap.org/export/embed.html"
            f"?bbox={bbox}&layer=mapnik&marker={flat},{flng}"
        )

    @property
    def map_link_url(self):
        """Return an OpenStreetMap link URL for the 'view larger' anchor."""
        lat = self.map_latitude
        lng = self.map_longitude
        if not lat or not lng:
            return ""
        return f"https://www.openstreetmap.org/?mlat={lat}&mlon={lng}#map=16/{lat}/{lng}"

    # -- Tabbed admin interface ---------------------------------------------

    general_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("site_name"),
                    FieldPanel("tagline"),
                    FieldPanel("description"),
                ],
                heading=_("General"),
            ),
        ],
        heading=_("General"),
    )

    theme_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("theme"),
                    FieldPanel("color_scheme"),
                ],
                heading=_("Theme"),
            ),
        ],
        heading=_("Theme"),
    )

    branding_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("logo"),
                    FieldPanel("logo_dark"),
                    FieldPanel("favicon"),
                ],
                heading=_("Branding"),
            ),
        ],
        heading=_("Branding"),
    )

    contact_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("phone"),
                    FieldPanel("email"),
                    FieldPanel("address"),
                    FieldPanel("hours"),
                ],
                heading=_("Contact"),
            ),
        ],
        heading=_("Contact"),
    )

    social_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("facebook_url"),
                    FieldPanel("instagram_url"),
                    FieldPanel("twitter_url"),
                    FieldPanel("youtube_url"),
                    FieldPanel("linkedin_url"),
                    FieldPanel("tiktok_url"),
                ],
                heading=_("Social media"),
            ),
        ],
        heading=_("Social"),
    )

    navigation_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("navbar"),
                    FieldPanel("footer"),
                ],
                heading=_("Navigation"),
            ),
        ],
        heading=_("Navigation"),
    )

    pwa_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("pwa_name"),
                    FieldPanel("pwa_short_name"),
                    FieldPanel("pwa_description"),
                    FieldPanel("pwa_icon_192"),
                    FieldPanel("pwa_icon_512"),
                    FieldPanel("pwa_theme_color"),
                    FieldPanel("pwa_background_color"),
                ],
                heading=_("Progressive Web App"),
            ),
        ],
        heading=_("PWA"),
    )

    forms_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("captcha_provider"),
                    FieldPanel("captcha_site_key"),
                    FieldPanel("captcha_secret_key"),
                ],
                heading=_("Anti-spam / CAPTCHA"),
            ),
        ],
        heading=_("Forms"),
    )

    map_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("map_routing_service"),
                    FieldPanel("map_api_key"),
                    FieldPanel("map_default_center"),
                    FieldPanel("map_default_zoom"),
                ],
                heading=_("Map & routing"),
            ),
        ],
        heading=_("Map"),
    )

    edit_handler = TabbedInterface(
        [
            general_panels,
            theme_panels,
            branding_panels,
            contact_panels,
            social_panels,
            navigation_panels,
            pwa_panels,
            forms_panels,
            map_panels,
        ]
    )

    class Meta:
        verbose_name = _("site settings")
        verbose_name_plural = _("site settings")

    def __str__(self) -> str:
        return f"Settings for {self.site}"

    # -- Helpers ------------------------------------------------------------

    def get_colors(self) -> dict[str, str]:
        """
        Return CSS custom-property dict from the related ColourScheme,
        or an empty dict when no scheme is assigned.
        """
        if self.color_scheme_id:
            return self.color_scheme.get_css_variables()
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# PaymentSettings — separate settings model for payment configuration
# ═══════════════════════════════════════════════════════════════════════════

PAYMENT_MODE_CHOICES = [
    ("test", _("Test")),
    ("live", _("Live")),
]


@register_setting
class PaymentSettings(BaseSiteSetting):
    """
    Per-site payment configuration.

    Registered as a separate settings panel so payment credentials
    are isolated from general site settings with granular admin permissions.
    """

    # -- Mode tab -----------------------------------------------------------
    payment_mode = models.CharField(
        max_length=10,
        choices=PAYMENT_MODE_CHOICES,
        default="test",
        verbose_name=_("Payment mode"),
        help_text=_("Only credentials for the selected mode are used at runtime."),
    )

    # -- Stripe test --------------------------------------------------------
    stripe_test_enabled = models.BooleanField(
        default=False, verbose_name=_("Stripe enabled (test)"),
    )
    stripe_test_public_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe public key (test)"),
    )
    stripe_test_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe secret key (test)"),
    )
    stripe_test_webhook_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe webhook secret (test)"),
    )

    # -- PayPal test --------------------------------------------------------
    paypal_test_enabled = models.BooleanField(
        default=False, verbose_name=_("PayPal enabled (test)"),
    )
    paypal_test_client_id = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal client ID (test)"),
    )
    paypal_test_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal secret (test)"),
    )

    # -- Stripe live --------------------------------------------------------
    stripe_live_enabled = models.BooleanField(
        default=False, verbose_name=_("Stripe enabled (live)"),
    )
    stripe_live_public_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe public key (live)"),
    )
    stripe_live_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe secret key (live)"),
    )
    stripe_live_webhook_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe webhook secret (live)"),
    )

    # -- PayPal live --------------------------------------------------------
    paypal_live_enabled = models.BooleanField(
        default=False, verbose_name=_("PayPal enabled (live)"),
    )
    paypal_live_client_id = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal client ID (live)"),
    )
    paypal_live_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal secret (live)"),
    )

    # -- Bank transfer ------------------------------------------------------
    bank_transfer_enabled = models.BooleanField(
        default=False, verbose_name=_("Bank transfer enabled"),
    )
    bank_account_holder = models.CharField(
        max_length=255, blank=True, verbose_name=_("Account holder"),
    )
    bank_iban = models.CharField(
        max_length=34, blank=True, verbose_name=_("IBAN"),
    )
    bank_bic = models.CharField(
        max_length=11, blank=True, verbose_name=_("BIC / SWIFT"),
    )
    bank_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Bank name"),
    )
    bank_transfer_instructions = RichTextField(
        blank=True,
        verbose_name=_("Bank transfer instructions"),
        help_text=_("Additional instructions shown to the user (e.g. 'Include the reference in the description')."),
    )
    bank_transfer_expiry_days = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Bank transfer expiry (days)"),
        help_text=_("Days allowed for the user to complete the bank transfer."),
    )

    # -- Computed helpers ---------------------------------------------------

    @property
    def is_test_mode(self):
        return self.payment_mode == "test"

    @property
    def stripe_enabled(self):
        if self.is_test_mode:
            return self.stripe_test_enabled
        return self.stripe_live_enabled

    @property
    def paypal_enabled(self):
        if self.is_test_mode:
            return self.paypal_test_enabled
        return self.paypal_live_enabled

    @property
    def stripe_public_key(self):
        if self.is_test_mode:
            return self.stripe_test_public_key
        return self.stripe_live_public_key

    @property
    def stripe_secret_key(self):
        if self.is_test_mode:
            return self.stripe_test_secret_key
        return self.stripe_live_secret_key

    @property
    def stripe_webhook_secret(self):
        if self.is_test_mode:
            return self.stripe_test_webhook_secret
        return self.stripe_live_webhook_secret

    @property
    def paypal_client_id(self):
        if self.is_test_mode:
            return self.paypal_test_client_id
        return self.paypal_live_client_id

    @property
    def paypal_secret(self):
        if self.is_test_mode:
            return self.paypal_test_secret
        return self.paypal_live_secret

    @property
    def paypal_base_url(self):
        if self.is_test_mode:
            return "https://api-m.sandbox.paypal.com"
        return "https://api-m.paypal.com"

    @property
    def available_providers(self):
        """Return list of enabled payment provider keys."""
        providers = []
        if self.stripe_enabled:
            providers.append("stripe")
        if self.paypal_enabled:
            providers.append("paypal")
        if self.bank_transfer_enabled:
            providers.append("bank_transfer")
        return providers

    # -- Admin panels -------------------------------------------------------

    mode_panels = ObjectList(
        [
            MultiFieldPanel(
                [FieldPanel("payment_mode")],
                heading=_("Active mode"),
            ),
        ],
        heading=_("Mode"),
    )

    test_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("stripe_test_enabled"),
                    FieldPanel("stripe_test_public_key"),
                    FieldPanel("stripe_test_secret_key"),
                    FieldPanel("stripe_test_webhook_secret"),
                ],
                heading=_("Stripe (test)"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("paypal_test_enabled"),
                    FieldPanel("paypal_test_client_id"),
                    FieldPanel("paypal_test_secret"),
                ],
                heading=_("PayPal (test)"),
            ),
        ],
        heading=_("Test configuration"),
    )

    live_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("stripe_live_enabled"),
                    FieldPanel("stripe_live_public_key"),
                    FieldPanel("stripe_live_secret_key"),
                    FieldPanel("stripe_live_webhook_secret"),
                ],
                heading=_("Stripe (live)"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("paypal_live_enabled"),
                    FieldPanel("paypal_live_client_id"),
                    FieldPanel("paypal_live_secret"),
                ],
                heading=_("PayPal (live)"),
            ),
        ],
        heading=_("Live configuration"),
    )

    bank_transfer_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("bank_transfer_enabled"),
                    FieldPanel("bank_account_holder"),
                    FieldPanel("bank_iban"),
                    FieldPanel("bank_bic"),
                    FieldPanel("bank_name"),
                    FieldPanel("bank_transfer_instructions"),
                    FieldPanel("bank_transfer_expiry_days"),
                ],
                heading=_("Bank transfer"),
            ),
        ],
        heading=_("Bank transfer"),
    )

    edit_handler = TabbedInterface(
        [
            mode_panels,
            test_panels,
            live_panels,
            bank_transfer_panels,
        ]
    )

    class Meta:
        verbose_name = _("payment settings")
        verbose_name_plural = _("payment settings")

    def __str__(self) -> str:
        return f"Payment settings for {self.site}"

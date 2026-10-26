"""
Wagtail Site Settings for the Club CMS.

Uses ``BaseSiteSetting`` so each Wagtail Site can have its own configuration.
Access in templates via ``{{ settings.website.SiteSettings }}``.
"""

from django.conf import settings as django_settings
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
        help_text=_(
            "Shown in the browser tab after each page title, in the footer "
            "and in search engine results."
        ),
    )
    tagline = models.CharField(
        max_length=255, blank=True, verbose_name=_("Tagline"),
        help_text=_(
            "Shown in the footer when the footer has no description of its own."
        ),
    )
    description = models.TextField(
        blank=True, verbose_name=_("Site description"),
        help_text=_(
            "Used by search engines for pages that have no search "
            "description of their own."
        ),
    )

    # -- Theme tab ----------------------------------------------------------
    theme = models.CharField(
        max_length=20,
        choices=THEME_CHOICES,
        default="velocity",
        verbose_name=_("Theme"),
        help_text=_("Visual style of the public site. The admin keeps its own look."),
    )
    color_scheme = models.ForeignKey(
        "website.ColorScheme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Colour scheme"),
        help_text=_(
            "Replaces the theme colours with your own palette. "
            "Leave empty to keep the theme's default colours."
        ),
    )

    # -- Branding tab -------------------------------------------------------
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo"),
        help_text=_(
            "Shown in the navigation bar, on the home page and in search "
            "engine data. A logo set on the navbar takes priority in the "
            "navigation bar."
        ),
    )
    logo_dark = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Logo (dark variant)"),
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Favicon"),
        help_text=_(
            "Small icon shown in the browser tab. Ignored when a PWA name "
            "is set, because the app icons are used instead."
        ),
    )
    logo_text = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Logo text"),
        help_text=_(
            "Shown next to the logo in the navigation bar. Line breaks are kept."
        ),
    )

    # -- Contact tab --------------------------------------------------------
    phone = models.CharField(max_length=30, blank=True, verbose_name=_("Phone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    address = models.TextField(blank=True, verbose_name=_("Address"))
    hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Opening hours"),
        help_text=_("Shown on the contact page only, for example Mon-Fri 9:00-18:00."),
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
        help_text=_(
            "Menu shown at the top of every page. Menus are edited under Snippets."
        ),
    )
    footer = models.ForeignKey(
        "website.Footer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Footer"),
        help_text=_(
            "Shown at the bottom of every page. Footers are edited under Snippets."
        ),
    )

    # -- PWA tab ------------------------------------------------------------
    pwa_name = models.CharField(
        max_length=200, blank=True, verbose_name=_("PWA name"),
        help_text=_(
            "If filled, visitors can install the site as an app on their "
            "phone. Example: Moto Club Aquile Rosse."
        ),
    )
    pwa_short_name = models.CharField(
        max_length=50, blank=True, verbose_name=_("PWA short name"),
        help_text=_(
            "Shown under the app icon on the home screen; keep it within "
            "12 characters. If empty, the PWA name is used."
        ),
    )
    pwa_description = models.TextField(
        blank=True, verbose_name=_("PWA description"),
        help_text=_(
            "Included in the app manifest; some phones show it while installing."
        ),
    )
    pwa_icon_192 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("PWA icon 192x192"),
        help_text=_("Square PNG of 192 x 192 pixels with a transparent background."),
    )
    pwa_icon_512 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("PWA icon 512x512"),
        help_text=_("Square PNG of 512 x 512 pixels with a transparent background."),
    )
    pwa_icon_180 = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Apple touch icon 180x180"),
        help_text=_("Square PNG of 180 x 180 pixels, the size Apple devices expect."),
    )
    pwa_theme_color = models.CharField(
        max_length=7, default="#0F172A", verbose_name=_("PWA theme colour"),
        help_text=_("Colour of the browser bar on phones, as a hex code like #0F172A."),
    )
    pwa_background_color = models.CharField(
        max_length=7, default="#FFFFFF", verbose_name=_("PWA background colour"),
        help_text=_(
            "Colour of the splash screen while the installed app opens, "
            "as a hex code like #FFFFFF."
        ),
    )

    # -- Forms tab ----------------------------------------------------------
    captcha_provider = models.CharField(
        max_length=20,
        choices=CAPTCHA_PROVIDER_CHOICES,
        default="honeypot",
        verbose_name=_("CAPTCHA provider"),
        help_text=_(
            "Used on the newsletter subscribe and unsubscribe forms. "
            "Honeypot needs no keys."
        ),
    )
    captcha_site_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("CAPTCHA site key"),
        help_text=_(
            "Copy it from the Cloudflare Turnstile or hCaptcha dashboard "
            "after adding this site there."
        ),
    )
    captcha_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("CAPTCHA secret key"),
        help_text=_(
            "Found in the same Turnstile or hCaptcha dashboard as the site "
            "key. Never share it."
        ),
    )

    # -- SEO tab ------------------------------------------------------------
    seo_indexing = models.BooleanField(
        default=True, verbose_name=_("Allow search engine indexing"),
        help_text=_(
            "If off, every page gets a noindex tag and robots.txt blocks all "
            "crawlers. Useful for test or preview sites."
        ),
    )
    allow_ai_bots = models.BooleanField(
        default=False, verbose_name=_("Allow AI bot crawling"),
        help_text=_(
            "If off, robots.txt asks AI crawlers (GPTBot, ChatGPT-User, "
            "Google-Extended, CCBot, Anthropic, Meta, Bytespider, "
            "PerplexityBot) to stay away."
        ),
    )
    robots_txt_extra = models.TextField(
        blank=True, verbose_name=_("Additional robots.txt rules"),
        help_text=_(
            "Added after the standard rules. For example, Disallow: /private/ "
            "asks search engines to skip that folder."
        ),
    )
    canonical_domain = models.URLField(
        blank=True, verbose_name=_("Canonical domain"),
        help_text=_(
            "Main address of the site, like https://www.example.com, used in "
            "the canonical link of every page. If empty, the address the "
            "visitor typed is used."
        ),
    )

    # -- Analytics tab ------------------------------------------------------
    tracking_code = models.TextField(
        blank=True, verbose_name=_("Tracking code"),
        help_text=_(
            "Paste the full snippet from Matomo, Google Analytics or similar. "
            "It is added to every page just before the closing body tag."
        ),
    )

    # -- GitHub tab ---------------------------------------------------------
    github_url = models.URLField(
        blank=True, verbose_name=_("GitHub repository URL"),
        help_text=_(
            "If filled, a 'Fork me on GitHub' ribbon appears in the top right "
            "corner and a GitHub link appears in the footer."
        ),
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
    )
    map_default_center = models.CharField(
        max_length=100, blank=True, verbose_name=_("Default map centre"),
        help_text=_(
            "Club location for the map on the contact page, as "
            "latitude,longitude. Example: 45.4642,9.1900."
        ),
    )
    map_default_zoom = models.IntegerField(
        default=10, verbose_name=_("Default map zoom"),
    )

    # -- Computed helpers ---------------------------------------------------

    @property
    def resolved_site_name(self):
        return self.site_name or getattr(django_settings, "WAGTAIL_SITE_NAME", "Club CMS")

    @property
    def resolved_pwa_name(self):
        return self.pwa_name or self.resolved_site_name

    @property
    def resolved_pwa_short_name(self):
        return self.pwa_short_name or self.resolved_pwa_name

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
                    FieldPanel("logo_text"),
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
                help_text=_(
                    "Phone, email and address appear on the contact page and "
                    "the membership card, and in the footer unless the footer "
                    "has its own contact details."
                ),
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
                help_text=_(
                    "Full profile addresses starting with https://. Search "
                    "engines use them to link the profiles to the club; the "
                    "footer icons are set in the footer snippet."
                ),
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
                    FieldPanel("pwa_icon_180"),
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

    seo_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("seo_indexing"),
                    FieldPanel("allow_ai_bots"),
                    FieldPanel("canonical_domain"),
                ],
                heading=_("Indexing & canonical"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("robots_txt_extra"),
                ],
                heading=_("robots.txt"),
            ),
        ],
        heading=_("SEO"),
    )

    analytics_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("tracking_code"),
                ],
                heading=_("Statistics & monitoring"),
            ),
        ],
        heading=_("Analytics"),
    )

    github_panels = ObjectList(
        [
            MultiFieldPanel(
                [
                    FieldPanel("github_url"),
                ],
                heading=_("GitHub"),
            ),
        ],
        heading=_("GitHub"),
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
            seo_panels,
            analytics_panels,
            github_panels,
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
        help_text=_(
            "Test uses the test keys and the PayPal sandbox, so no real money "
            "moves. Switch to Live only after filling in the live keys."
        ),
    )

    # -- Stripe test --------------------------------------------------------
    stripe_test_enabled = models.BooleanField(
        default=False, verbose_name=_("Stripe enabled (test)"),
        help_text=_("If on, members can pay event fees by card through Stripe."),
    )
    stripe_test_public_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe public key (test)"),
        help_text=_(
            "In the Stripe Dashboard, turn on test mode and open Developers > "
            "API keys. Copy the publishable key (pk_test_...)."
        ),
    )
    stripe_test_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe secret key (test)"),
        help_text=_(
            "In the Stripe Dashboard, turn on test mode and open Developers > "
            "API keys. Copy the secret key (sk_test_...) and never share it."
        ),
    )
    stripe_test_webhook_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe webhook secret (test)"),
        help_text=_(
            "In test mode, open Developers > Webhooks and add the endpoint "
            "https://your-domain/en/events/payment/webhook/stripe/ with the "
            "event checkout.session.completed, then copy its signing secret "
            "(whsec_...). It confirms payments even when the member does not "
            "come back to the site after paying."
        ),
    )

    # -- PayPal test --------------------------------------------------------
    paypal_test_enabled = models.BooleanField(
        default=False, verbose_name=_("PayPal enabled (test)"),
        help_text=_("If on, members can pay event fees with PayPal."),
    )
    paypal_test_client_id = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal client ID (test)"),
        help_text=_(
            "In the PayPal Developer dashboard open Apps & Credentials, choose "
            "Sandbox and copy the Client ID of your app."
        ),
    )
    paypal_test_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal secret (test)"),
        help_text=_(
            "Shown next to the Client ID of the same Sandbox app in PayPal "
            "Developer > Apps & Credentials. Never share it."
        ),
    )

    # -- Stripe live --------------------------------------------------------
    stripe_live_enabled = models.BooleanField(
        default=False, verbose_name=_("Stripe enabled (live)"),
        help_text=_("If on, members can pay event fees by card through Stripe."),
    )
    stripe_live_public_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe public key (live)"),
        help_text=_(
            "In the Stripe Dashboard, turn off test mode and open Developers > "
            "API keys. Copy the publishable key (pk_live_...)."
        ),
    )
    stripe_live_secret_key = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe secret key (live)"),
        help_text=_(
            "In the Stripe Dashboard, turn off test mode and open Developers > "
            "API keys. Copy the secret key (sk_live_...) and never share it."
        ),
    )
    stripe_live_webhook_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("Stripe webhook secret (live)"),
        help_text=_(
            "With test mode off, open Developers > Webhooks and add the endpoint "
            "https://your-domain/en/events/payment/webhook/stripe/ with the "
            "event checkout.session.completed, then copy its signing secret "
            "(whsec_...). It confirms payments even when the member does not "
            "come back to the site after paying."
        ),
    )

    # -- PayPal live --------------------------------------------------------
    paypal_live_enabled = models.BooleanField(
        default=False, verbose_name=_("PayPal enabled (live)"),
        help_text=_("If on, members can pay event fees with PayPal."),
    )
    paypal_live_client_id = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal client ID (live)"),
        help_text=_(
            "In the PayPal Developer dashboard open Apps & Credentials, choose "
            "Live and copy the Client ID of your app."
        ),
    )
    paypal_live_secret = models.CharField(
        max_length=255, blank=True, verbose_name=_("PayPal secret (live)"),
        help_text=_(
            "Shown next to the Client ID of the same Live app in PayPal "
            "Developer > Apps & Credentials. Never share it."
        ),
    )

    # -- Bank transfer ------------------------------------------------------
    bank_transfer_enabled = models.BooleanField(
        default=False, verbose_name=_("Bank transfer enabled"),
        help_text=_(
            "If on, members can pay event fees by bank transfer. They get the "
            "account details on screen and by email."
        ),
    )
    bank_account_holder = models.CharField(
        max_length=255, blank=True, verbose_name=_("Account holder"),
    )
    bank_iban = models.CharField(
        max_length=34, blank=True, verbose_name=_("IBAN"),
        help_text=_(
            "Up to 34 characters without spaces, for example "
            "IT60X0542811101000000123456."
        ),
    )
    bank_bic = models.CharField(
        max_length=11, blank=True, verbose_name=_("BIC / SWIFT"),
        help_text=_(
            "Bank identifier code of 8 or 11 characters, for example BCITITMM."
        ),
    )
    bank_name = models.CharField(
        max_length=255, blank=True, verbose_name=_("Bank name"),
    )
    bank_transfer_instructions = RichTextField(
        blank=True,
        verbose_name=_("Bank transfer instructions"),
        help_text=_(
            "Extra text below the account details, for example a reminder to "
            "put the payment reference in the transfer description."
        ),
    )
    bank_transfer_expiry_days = models.PositiveIntegerField(
        default=5,
        verbose_name=_("Bank transfer expiry (days)"),
        help_text=_(
            "Days the member has to pay, but never later than the day before "
            "the event. Unpaid registrations then expire and the place goes "
            "to the waiting list."
        ),
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
        help_text=_("Used only while the payment mode is Test."),
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
        help_text=_("Used only while the payment mode is Live. Real money is charged."),
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
                help_text=_(
                    "Members see these details on the payment instructions "
                    "page after choosing bank transfer."
                ),
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

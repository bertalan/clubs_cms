"""
Newsletter models.

- NewsletterCategory: topic categories for newsletters (e.g. Club News, Events).
- NewsletterSubscription: email-based subscriptions with category preferences.
- SentNewsletter: campaigns composed with StreamField, with scheduling and
  visibility options.
- NewsletterPage: Wagtail page (RoutablePageMixin) for subscribe, unsubscribe,
  archive, and detail views.
"""

import hashlib
import hmac

from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page

from apps.website.blocks.email import NEWSLETTER_BLOCKS


class NewsletterCategory(models.Model):
    """Topic category for newsletters (snippet)."""

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug"),
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Shown to subscribers when choosing categories."),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default"),
        help_text=_("Auto-selected for new subscribers."),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Sort order"),
    )

    class Meta:
        verbose_name = _("Newsletter category")
        verbose_name_plural = _("Newsletter categories")
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class NewsletterSubscription(models.Model):
    """Stores a newsletter email subscription."""

    email = models.EmailField(
        unique=True,
        verbose_name=_("Email address"),
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    categories = models.ManyToManyField(
        NewsletterCategory,
        blank=True,
        related_name="subscriptions",
        verbose_name=_("Categories"),
        help_text=_("Newsletter categories this subscriber opted into."),
    )
    subscribed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Subscribed at"),
    )
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Unsubscribed at"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP address"),
    )

    class Meta:
        verbose_name = _("Newsletter subscription")
        verbose_name_plural = _("Newsletter subscriptions")
        ordering = ["-subscribed_at"]

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.email} ({status})"

    def make_unsubscribe_token(self):
        """Generate an HMAC token for email-based unsubscribe links."""
        key = settings.SECRET_KEY.encode()
        return hmac.new(key, self.email.encode(), hashlib.sha256).hexdigest()[:32]

    @classmethod
    def verify_unsubscribe_token(cls, email, token):
        """Verify that a token matches the given email."""
        key = settings.SECRET_KEY.encode()
        expected = hmac.new(key, email.encode(), hashlib.sha256).hexdigest()[:32]
        return hmac.compare_digest(expected, token)


class SentNewsletter(models.Model):
    """A newsletter campaign composed and sent from the admin."""

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("scheduled", _("Scheduled")),
        ("sent", _("Sent")),
    ]

    subject = models.CharField(
        max_length=255,
        verbose_name=_("Subject"),
    )
    body = StreamField(
        NEWSLETTER_BLOCKS,
        verbose_name=_("Body"),
        help_text=_("Compose the newsletter using the available blocks."),
        blank=True,
        use_json_field=True,
    )
    category = models.ForeignKey(
        NewsletterCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="newsletters",
        verbose_name=_("Category"),
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("Public"),
        help_text=_("If checked, this newsletter is visible in the public archive."),
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
    )
    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Scheduled for"),
        help_text=_("If set, the newsletter will be sent automatically at this date and time."),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent at"),
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Sent by"),
    )
    recipient_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Recipients"),
    )

    class Meta:
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"


# ═══════════════════════════════════════════════════════════════════════════
# Wagtail page – Newsletter area (subscribe, unsubscribe, archive, detail)
# ═══════════════════════════════════════════════════════════════════════════


class NewsletterPage(RoutablePageMixin, Page):
    """
    Newsletter area served as a Wagtail page.

    Index (serve) → archive listing.
    Sub-routes: subscribe, unsubscribe, detail/<pk>.
    """

    intro = RichTextField(
        blank=True,
        verbose_name=_("Intro text"),
        help_text=_("Introductory text shown on the subscribe page."),
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    max_count = 1
    parent_page_types = ["website.HomePage"]
    subpage_types = []
    template = "website/newsletter_archive.html"

    class Meta:
        verbose_name = _("Newsletter page")
        verbose_name_plural = _("Newsletter pages")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_captcha_context():
        """Return captcha provider/key from SiteSettings for templates."""
        from apps.website.models.settings import SiteSettings
        from wagtail.models import Site

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            return {}
        try:
            ss = SiteSettings.for_site(site)
        except Exception:
            return {}
        return {
            "captcha_provider": ss.captcha_provider,
            "captcha_site_key": ss.captcha_site_key,
        }

    @staticmethod
    def _get_client_ip(request):
        """Extract the client IP address from the request."""
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")

    # ------------------------------------------------------------------
    # Route: archive (index)  — default serve
    # ------------------------------------------------------------------

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)

        category_slug = request.GET.get("category")
        categories = NewsletterCategory.objects.all()
        active_category = None
        if category_slug:
            active_category = NewsletterCategory.objects.filter(
                slug=category_slug
            ).first()

        newsletters = SentNewsletter.objects.filter(status="sent")

        is_subscriber = False
        if request.user.is_authenticated:
            is_subscriber = NewsletterSubscription.objects.filter(
                email=request.user.email, is_active=True
            ).exists()

        if not is_subscriber:
            newsletters = newsletters.filter(is_public=True)

        if active_category:
            newsletters = newsletters.filter(category=active_category)

        newsletters = newsletters.select_related("category").order_by("-sent_at")[:50]

        ctx.update({
            "categories": categories,
            "active_category": active_category,
            "newsletters": newsletters,
            "is_subscriber": is_subscriber,
        })
        return ctx

    # ------------------------------------------------------------------
    # Route: subscribe
    # ------------------------------------------------------------------

    @route(r"^subscribe/$", name="subscribe")
    def subscribe_view(self, request):
        from django.contrib import messages as msg_framework
        from apps.website.forms import NewsletterSubscribeForm

        if request.method == "POST":
            form = NewsletterSubscribeForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                categories = form.cleaned_data.get("categories", [])
                sub, created = NewsletterSubscription.objects.get_or_create(
                    email=email,
                    defaults={"ip_address": self._get_client_ip(request)},
                )
                if not created and not sub.is_active:
                    sub.is_active = True
                    sub.unsubscribed_at = None
                    sub.ip_address = self._get_client_ip(request)
                    sub.save(
                        update_fields=["is_active", "unsubscribed_at", "ip_address"]
                    )

                if categories:
                    sub.categories.set(categories)
                elif created:
                    defaults = NewsletterCategory.objects.filter(is_default=True)
                    if defaults.exists():
                        sub.categories.set(defaults)

                msg_framework.success(request, _("Thanks for subscribing!"))
                return redirect(self.url + self.reverse_subpage("subscribe"))

            ctx = {"form": form, "page": self}
            ctx.update(self._get_captcha_context())
            return render(request, "website/newsletter_subscribe.html", ctx)

        form = NewsletterSubscribeForm()
        ctx = {"form": form, "page": self}
        ctx.update(self._get_captcha_context())
        return render(request, "website/newsletter_subscribe.html", ctx)

    # ------------------------------------------------------------------
    # Route: unsubscribe
    # ------------------------------------------------------------------

    @route(r"^unsubscribe/$", name="unsubscribe")
    def unsubscribe_view(self, request):
        from django.contrib import messages as msg_framework
        from apps.website.forms import NewsletterUnsubscribeForm

        if request.method == "POST":
            form = NewsletterUnsubscribeForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data["email"]
                try:
                    sub = NewsletterSubscription.objects.get(
                        email=email, is_active=True
                    )
                    sub.is_active = False
                    sub.unsubscribed_at = timezone.now()
                    sub.save(update_fields=["is_active", "unsubscribed_at"])
                    msg_framework.success(
                        request, _("You have been unsubscribed.")
                    )
                except NewsletterSubscription.DoesNotExist:
                    msg_framework.info(
                        request,
                        _("This email is not subscribed to our newsletter."),
                    )
                return redirect(self.url + self.reverse_subpage("unsubscribe"))

            ctx = {"form": form, "page": self}
            ctx.update(self._get_captcha_context())
            return render(request, "website/newsletter_unsubscribe.html", ctx)

        form = NewsletterUnsubscribeForm()
        ctx = {"form": form, "page": self}
        ctx.update(self._get_captcha_context())
        return render(request, "website/newsletter_unsubscribe.html", ctx)

    # ------------------------------------------------------------------
    # Route: detail
    # ------------------------------------------------------------------

    @route(r"^(?P<pk>\d+)/$", name="detail")
    def detail_view(self, request, pk):
        from django.http import Http404
        from apps.website.render_email import render_newsletter_body_html

        newsletter = get_object_or_404(SentNewsletter, pk=pk, status="sent")

        if not newsletter.is_public:
            is_subscriber = False
            if request.user.is_authenticated:
                is_subscriber = NewsletterSubscription.objects.filter(
                    email=request.user.email, is_active=True
                ).exists()
            if not is_subscriber:
                raise Http404

        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
        body_html = render_newsletter_body_html(newsletter, base_url=base_url)

        ctx = {
            "newsletter": newsletter,
            "body_html": body_html,
            "page": self,
        }
        return render(request, "website/newsletter_detail.html", ctx)

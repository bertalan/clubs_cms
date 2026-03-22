"""
Newsletter models.

- NewsletterCategory: topic categories for newsletters (e.g. Club News, Events).
- NewsletterSubscription: email-based subscriptions with category preferences.
- SentNewsletter: campaigns composed with StreamField, with scheduling and
  visibility options.
"""

import hashlib
import hmac

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from wagtail.fields import StreamField

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

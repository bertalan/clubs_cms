"""
Wagtail admin ViewSets for newsletter management.

- NewsletterCategoryViewSet: manage newsletter categories.
- NewsletterSubscriptionViewSet: list/inspect/edit/export subscribers.
- SentNewsletterViewSet: compose, preview, schedule, and send campaigns.
"""

from django import forms as django_forms
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.ui.tables import Column
from wagtail.admin.viewsets.model import ModelViewSet

from apps.website.models.newsletter import (
    NewsletterCategory,
    NewsletterSubscription,
    SentNewsletter,
)


class NewsletterCategoryViewSet(ModelViewSet):
    """Manage newsletter categories."""

    model = NewsletterCategory
    icon = "tag"
    menu_label = _("Categories")
    menu_order = 50
    add_to_admin_menu = False
    list_display = ["name", "slug", "is_default", "sort_order"]
    search_fields = ["name"]
    ordering = ["sort_order", "name"]
    form_fields = ["name", "slug", "description", "is_default", "sort_order"]


class NewsletterSubscriptionViewSet(ModelViewSet):
    """Admin viewset for managing newsletter subscribers."""

    model = NewsletterSubscription
    icon = "user"
    menu_label = _("Subscribers")
    menu_order = 100
    add_to_admin_menu = False
    list_display = [
        "email",
        "is_active",
        "subscribed_at",
        "unsubscribed_at",
        "ip_address",
    ]
    list_filter = ["is_active"]
    search_fields = ["email"]
    ordering = ["-subscribed_at"]
    inspect_view_enabled = True
    panels = [
        FieldPanel("email"),
        FieldPanel("is_active"),
        FieldPanel(
            "categories",
            widget=django_forms.CheckboxSelectMultiple,
        ),
    ]
    list_export = ["email", "is_active", "subscribed_at", "unsubscribed_at", "ip_address"]
    export_headings = {
        "email": _("Email"),
        "is_active": _("Active"),
        "subscribed_at": _("Subscribed at"),
        "unsubscribed_at": _("Unsubscribed at"),
        "ip_address": _("IP address"),
    }


class PreviewColumn(Column):
    """Custom column that renders a Preview button for each newsletter."""

    def get_value(self, instance):
        url = reverse("newsletter_preview", args=[instance.pk])
        return format_html(
            '<a class="button button-small button-secondary" href="{}">'
            "{}</a>",
            url,
            _("Preview"),
        )


class SendActionColumn(Column):
    """Custom column that renders Send/Schedule/Sent badges."""

    def get_value(self, instance):
        if instance.status == "sent":
            return format_html(
                '<span style="color:var(--w-color-positive,green);">'
                "\u2714 {}</span>",
                _("Sent"),
            )
        if instance.status == "scheduled":
            return format_html(
                '<span style="color:var(--w-color-info, #2563eb);">'
                "\u23F0 {}</span>",
                _("Scheduled"),
            )
        url = reverse("newsletter_send", args=[instance.pk])
        return format_html(
            '<a class="button button-small button-secondary" href="{}">'
            "{}</a>",
            url,
            _("Send"),
        )


class SentNewsletterViewSet(ModelViewSet):
    """Admin viewset for composing and tracking newsletters."""

    model = SentNewsletter
    icon = "doc-full"
    menu_label = _("Campaigns")
    menu_order = 200
    add_to_admin_menu = False
    list_display = [
        "subject",
        "category",
        "status",
        "is_public",
        "recipient_count",
        "sent_at",
        "created_at",
        PreviewColumn("preview", label=_("Preview")),
        SendActionColumn("send", label=_("Action")),
    ]
    list_filter = ["status", "category", "is_public"]
    search_fields = ["subject"]
    ordering = ["-created_at"]
    inspect_view_enabled = True
    panels = [
        FieldPanel("subject"),
        FieldPanel("category"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("is_public"),
                FieldPanel("status"),
                FieldPanel("scheduled_at"),
            ],
            heading=_("Publishing"),
        ),
    ]

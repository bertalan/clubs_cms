"""
Wagtail hooks for the website app.

Registers the Maintenance admin page under Settings and
the Newsletter admin group in the sidebar.
"""

from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.viewsets.base import ViewSetGroup

from apps.website.admin_newsletter import (
    NewsletterCategoryViewSet,
    NewsletterSubscriptionViewSet,
    SentNewsletterViewSet,
)


@hooks.register("register_admin_urls")
def register_maintenance_url():
    from apps.website.views_admin import MaintenanceView

    return [
        path("maintenance/", MaintenanceView.as_view(), name="maintenance_admin"),
    ]


@hooks.register("register_admin_urls")
def register_newsletter_admin_urls():
    from apps.website.views_admin import PreviewNewsletterView, SendNewsletterView

    return [
        path(
            "newsletter/send/<int:pk>/",
            SendNewsletterView.as_view(),
            name="newsletter_send",
        ),
        path(
            "newsletter/preview/<int:pk>/",
            PreviewNewsletterView.as_view(),
            name="newsletter_preview",
        ),
    ]


@hooks.register("register_settings_menu_item")
def register_maintenance_menu_item():
    return MenuItem(
        _("Maintenance"),
        reverse("maintenance_admin"),
        icon_name="cog",
        order=9000,
    )


# ── Newsletter admin group ─────────────────────────────────────────────────


class NewsletterViewSetGroup(ViewSetGroup):
    """Groups newsletter viewsets under a single sidebar item."""

    menu_label = _("Newsletter")
    menu_icon = "mail"
    menu_order = 650
    items = (
        NewsletterCategoryViewSet,
        NewsletterSubscriptionViewSet,
        SentNewsletterViewSet,
    )


@hooks.register("register_admin_viewset")
def register_newsletter_viewset_group():
    return NewsletterViewSetGroup()


# ── Admin geocoder (Leaflet + Nominatim for EventDetailPage) ───────────────


LEAFLET_CSS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
LEAFLET_JS = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"


@hooks.register("insert_global_admin_css")
def admin_geocoder_css():
    return format_html(
        '<link rel="stylesheet" href="{leaflet}">'
        '<link rel="stylesheet" href="{geocoder}">',
        leaflet=LEAFLET_CSS,
        geocoder=static("css/admin_geocoder.css"),
    )


@hooks.register("insert_global_admin_js")
def admin_geocoder_js():
    return format_html(
        '<script src="{leaflet}"></script>'
        '<script src="{widget}"></script>'
        '<script src="{bridge}"></script>',
        leaflet=LEAFLET_JS,
        widget=static("js/geocoder-widget.js"),
        bridge=static("js/admin_geocoder.js"),
    )

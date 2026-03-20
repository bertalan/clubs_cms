"""
Wagtail hooks for the website app.

Registers the Maintenance admin page under Settings.
"""

from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register("register_admin_urls")
def register_maintenance_url():
    from apps.website.views_admin import MaintenanceView

    return [
        path("maintenance/", MaintenanceView.as_view(), name="maintenance_admin"),
    ]


@hooks.register("register_settings_menu_item")
def register_maintenance_menu_item():
    return MenuItem(
        _("Maintenance"),
        reverse("maintenance_admin"),
        icon_name="cog",
        order=9000,
    )

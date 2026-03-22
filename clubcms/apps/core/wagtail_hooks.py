"""
Wagtail hooks for core functionality.

Register admin ViewSets for transactional models (Activity, Comment, Reaction).
Inject global admin CSS/JS for field help tooltips.
"""

import os

from django.templatetags.static import static
from django.utils.html import format_html

from wagtail import hooks

from apps.core.admin import activity_viewset, comment_viewset, reaction_viewset


@hooks.register("register_icons")
def register_custom_icons(icons):
    icons.append("wagtailadmin/icons/bolt.svg")
    return icons


@hooks.register("register_admin_viewset")
def register_comment_viewset():
    return comment_viewset


@hooks.register("register_admin_viewset")
def register_activity_viewset():
    return activity_viewset


@hooks.register("register_admin_viewset")
def register_reaction_viewset():
    return reaction_viewset


@hooks.register("insert_global_admin_css")
def admin_field_help_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/admin_field_help.css"),
    )


@hooks.register("insert_global_admin_css")
def admin_colorpicker_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/admin_colorpicker.css"),
    )


@hooks.register("insert_global_admin_js")
def admin_field_help_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/admin_field_help.js"),
    )


@hooks.register("insert_global_admin_js")
def admin_colorpicker_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/admin_colorpicker.js"),
    )


# ── Icon picker (Font Awesome 6) ──────────────────────────────────────────

FA_CSS = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css"


@hooks.register("insert_global_admin_css")
def admin_iconpicker_css():
    return format_html(
        '<link rel="stylesheet" href="{fa}" crossorigin="anonymous">'
        '<link rel="stylesheet" href="{picker}">',
        fa=FA_CSS,
        picker=static("css/admin_iconpicker.css"),
    )


@hooks.register("insert_global_admin_js")
def admin_iconpicker_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/admin_iconpicker.js"),
    )

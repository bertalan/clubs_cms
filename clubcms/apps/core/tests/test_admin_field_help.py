"""
T25 — Test copertura help_text per admin Wagtail.

Verifica:
- Hook CSS/JS registrati correttamente
- File statici esistono
- Tutti i Page model hanno help_text sui field editabili
- Tutti gli snippet registrati hanno help_text sui field editabili
- help_text sono stringhe traducibili (LazyString)
"""

import os

from django.db import models
from django.test import TestCase
from django.utils.functional import Promise

from wagtail.models import Page
from wagtail.snippets.models import get_snippet_models

from apps.core.wagtail_hooks import admin_field_help_css, admin_field_help_js


# Fields to exclude from help_text checks
EXCLUDED_FIELD_NAMES = {
    # Inherited from Page base
    "title", "slug", "seo_title", "search_description", "show_in_menus",
    "content_type", "page_ptr", "live", "has_unpublished_changes",
    "first_published_at", "last_published_at", "go_live_at", "expire_at",
    "owner", "locked", "locked_at", "locked_by", "latest_revision",
    "live_revision", "translation_key", "locale",
    # Auto fields
    "id", "pk",
    # Technical relation fields
    "page_ptr_id", "path", "depth", "numchild", "url_path",
    "draft_title", "latest_revision_created_at",
}

# Field types to exclude
EXCLUDED_FIELD_TYPES = (
    models.AutoField,
    models.BigAutoField,
)


def _get_editable_fields(model):
    """Return model fields that are user-editable and should have help_text."""
    fields = []
    for field in model._meta.get_fields():
        # Skip non-concrete fields (reverse relations, GenericForeignKey, etc.)
        if not hasattr(field, "column") and not isinstance(field, models.ManyToManyField):
            continue
        # Skip auto fields
        if isinstance(field, EXCLUDED_FIELD_TYPES):
            continue
        # Skip excluded names
        if field.name in EXCLUDED_FIELD_NAMES:
            continue
        # Skip non-editable fields
        if hasattr(field, "editable") and not field.editable:
            continue
        # Skip ParentalKey (technical relation, not user-facing)
        try:
            from modelcluster.fields import ParentalKey
            if isinstance(field, ParentalKey):
                continue
        except ImportError:
            pass
        fields.append(field)
    return fields


def _get_page_models():
    """Return all concrete Page subclasses from apps.website.models.pages."""
    from apps.website.models import pages as pages_module

    page_models = []
    for name in dir(pages_module):
        obj = getattr(pages_module, name)
        if (
            isinstance(obj, type)
            and issubclass(obj, Page)
            and obj is not Page
            and not obj._meta.abstract
        ):
            page_models.append(obj)
    return page_models


class TestAdminFieldHelpHooks(TestCase):
    """Hook tests: CSS and JS are registered correctly."""

    def test_admin_css_hook_registered(self):
        result = admin_field_help_css()
        self.assertIn("admin_field_help.css", str(result))
        self.assertIn("<link", str(result))

    def test_admin_js_hook_registered(self):
        result = admin_field_help_js()
        self.assertIn("admin_field_help.js", str(result))
        self.assertIn("<script", str(result))

    def test_css_hook_in_wagtail_hooks(self):
        from wagtail import hooks as wagtail_hooks

        css_hooks = wagtail_hooks.get_hooks("insert_global_admin_css")
        css_results = [fn() for fn in css_hooks]
        css_html = " ".join(str(r) for r in css_results)
        self.assertIn("admin_field_help.css", css_html)

    def test_js_hook_in_wagtail_hooks(self):
        from wagtail import hooks as wagtail_hooks

        js_hooks = wagtail_hooks.get_hooks("insert_global_admin_js")
        js_results = [fn() for fn in js_hooks]
        js_html = " ".join(str(r) for r in js_results)
        self.assertIn("admin_field_help.js", js_html)


class TestStaticFilesExist(TestCase):
    """Static file existence checks."""

    def test_admin_css_file_exists(self):
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "css", "admin_field_help.css",
        )
        self.assertTrue(os.path.isfile(css_path), f"Missing: {css_path}")

    def test_admin_js_file_exists(self):
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "js", "admin_field_help.js",
        )
        self.assertTrue(os.path.isfile(js_path), f"Missing: {js_path}")


class TestPageFieldsHaveHelpText(TestCase):
    """All Page model fields should have help_text."""

    def test_all_page_fields_have_help_text(self):
        missing = []
        for model in _get_page_models():
            for field in _get_editable_fields(model):
                if not getattr(field, "help_text", ""):
                    missing.append(f"{model.__name__}.{field.name}")
        if missing:
            self.fail(
                f"{len(missing)} page field(s) missing help_text:\n"
                + "\n".join(f"  - {m}" for m in sorted(missing))
            )


class TestSnippetFieldsHaveHelpText(TestCase):
    """All snippet model fields should have help_text."""

    def test_all_snippet_fields_have_help_text(self):
        missing = []
        for model in get_snippet_models():
            # Only check snippets from our apps
            if not model._meta.app_label.startswith(("website", "core")):
                continue
            for field in _get_editable_fields(model):
                if not getattr(field, "help_text", ""):
                    missing.append(f"{model.__name__}.{field.name}")
        if missing:
            self.fail(
                f"{len(missing)} snippet field(s) missing help_text:\n"
                + "\n".join(f"  - {m}" for m in sorted(missing))
            )


class TestHelpTextTranslatable(TestCase):
    """All help_text should be wrapped in _() (LazyString)."""

    def test_help_text_is_translatable(self):
        not_lazy = []
        all_models = list(_get_page_models()) + [
            m for m in get_snippet_models()
            if m._meta.app_label.startswith(("website", "core"))
        ]
        for model in all_models:
            for field in _get_editable_fields(model):
                help_text = getattr(field, "help_text", "")
                if help_text and not isinstance(help_text, Promise):
                    not_lazy.append(f"{model.__name__}.{field.name}")
        if not_lazy:
            self.fail(
                f"{len(not_lazy)} field(s) with non-translatable help_text:\n"
                + "\n".join(f"  - {m}" for m in sorted(not_lazy))
            )

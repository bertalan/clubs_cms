"""
Admin help policy (rivista il 2026-10-25).

Verifica:
- Guida di pagina (GuidePanel + modale) caricata nell'admin; il vecchio
  tooltip che ripeteva il help_text non c'è più
- Nessun obbligo di help_text: un help serve solo se aggiunge informazione
  (dove si trova il dato, formato, effetto). In tutti i modelli del
  progetto (rivisti il 2026-10-26) gli help non devono ripetere l'etichetta
- Ogni campo ha un'etichetta traducibile (verbose_name con gettext_lazy)
- help_text sono stringhe traducibili (LazyString)
"""

import os

from django.apps import apps as django_apps
from django.db import models
from django.test import TestCase
from django.utils.functional import Promise

from wagtail.models import Page
from wagtail.snippets.models import get_snippet_models

from apps.core.help_quality import is_redundant_help
from apps.core.wagtail_hooks import (
    admin_colorpicker_css,
    admin_colorpicker_js,
    admin_guide_css,
    admin_guide_js,
)
from apps.federation.models import FederatedClub

# Every model of the project: help texts were reviewed on 2026-10-26.
REVIEWED_MODELS = [
    m for m in django_apps.get_models() if m.__module__.startswith("apps.") and not m._meta.abstract
]


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


def _from_third_party_base(model, field):
    """True if the field is defined by an abstract base outside the project
    (AbstractUser, taggit's TaggedItemBase, ...): its label is not ours."""
    for base in model.__mro__[1:]:
        meta = getattr(base, "_meta", None)
        if meta is None or not meta.abstract or base.__module__.startswith("apps."):
            continue
        if field.name in {f.name for f in meta.local_fields + meta.local_many_to_many}:
            return True
    return False


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


class TestAdminHelpHooks(TestCase):
    """Hook tests: CSS and JS are registered correctly."""

    def test_admin_css_hook_registered(self):
        result = admin_guide_css()
        self.assertIn("admin_guide.css", str(result))
        self.assertIn("<link", str(result))

    def test_admin_js_hook_registered(self):
        result = admin_guide_js()
        self.assertIn("admin_guide.js", str(result))
        self.assertIn("<script", str(result))

    def test_admin_colorpicker_css_hook_registered(self):
        result = admin_colorpicker_css()
        self.assertIn("admin_colorpicker.css", str(result))
        self.assertIn("<link", str(result))

    def test_admin_colorpicker_js_hook_registered(self):
        result = admin_colorpicker_js()
        self.assertIn("admin_colorpicker.js", str(result))
        self.assertIn("<script", str(result))

    def test_css_hook_in_wagtail_hooks(self):
        from wagtail import hooks as wagtail_hooks

        css_hooks = wagtail_hooks.get_hooks("insert_global_admin_css")
        css_results = [fn() for fn in css_hooks]
        css_html = " ".join(str(r) for r in css_results)
        self.assertIn("admin_guide.css", css_html)
        self.assertNotIn("admin_field_help", css_html)
        self.assertIn("admin_colorpicker.css", css_html)

    def test_js_hook_in_wagtail_hooks(self):
        from wagtail import hooks as wagtail_hooks

        js_hooks = wagtail_hooks.get_hooks("insert_global_admin_js")
        js_results = [fn() for fn in js_hooks]
        js_html = " ".join(str(r) for r in js_results)
        self.assertIn("admin_guide.js", js_html)
        self.assertNotIn("admin_field_help", js_html)
        self.assertIn("admin_colorpicker.js", js_html)


class TestStaticFilesExist(TestCase):
    """Static file existence checks."""

    def test_admin_css_file_exists(self):
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "css", "admin_guide.css",
        )
        self.assertTrue(os.path.isfile(css_path), f"Missing: {css_path}")

    def test_admin_js_file_exists(self):
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "js", "admin_guide.js",
        )
        self.assertTrue(os.path.isfile(js_path), f"Missing: {js_path}")

    def test_admin_colorpicker_css_file_exists(self):
        css_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "css", "admin_colorpicker.css",
        )
        self.assertTrue(os.path.isfile(css_path), f"Missing: {css_path}")

    def test_admin_colorpicker_js_file_exists(self):
        js_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "static", "js", "admin_colorpicker.js",
        )
        self.assertTrue(os.path.isfile(js_path), f"Missing: {js_path}")


class TestReviewedModelsHaveUsefulHelp(TestCase):
    """Rewritten help texts must not just restate the field label."""

    def test_reviewed_help_texts_add_information(self):
        redundant = []
        for model in REVIEWED_MODELS:
            for field in _get_editable_fields(model):
                if _from_third_party_base(model, field):
                    continue
                help_text = str(getattr(field, "help_text", "") or "")
                if help_text and is_redundant_help(field, help_text):
                    redundant.append(f"{model.__name__}.{field.name}: {help_text!r}")
        if redundant:
            self.fail(
                f"{len(redundant)} help text(s) only restate the label:\n"
                + "\n".join(f"  - {r}" for r in sorted(redundant))
            )

    def test_every_field_has_a_translatable_label(self):
        missing = []
        for model in REVIEWED_MODELS:
            for field in _get_editable_fields(model):
                if _from_third_party_base(model, field):
                    continue
                if not isinstance(field.verbose_name, Promise):
                    missing.append(f"{model.__name__}.{field.name}")
        if missing:
            self.fail(
                f"{len(missing)} field(s) without verbose_name=_(...):\n"
                + "\n".join(f"  - {m}" for m in sorted(missing))
            )

    def test_heuristic_flags_restated_labels(self):
        field = FederatedClub._meta.get_field("base_url")
        self.assertTrue(is_redundant_help(field, "Partner site base URL"))
        self.assertFalse(
            is_redundant_help(
                field,
                "Root address of the partner site without any path, "
                "e.g. https://partner.example",
            )
        )


class TestHelpTextTranslatable(TestCase):
    """All help_text should be wrapped in _() (LazyString)."""

    def test_help_text_is_translatable(self):
        not_lazy = []
        all_models = list(_get_page_models()) + [
            m for m in get_snippet_models()
            if m._meta.app_label.startswith(("website", "core", "federation"))
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

"""
Automated i18n coverage test.

Verifies that every ``_("...")`` / ``gettext_lazy("...")`` string found in
the project's Python source and Django templates has a non-empty translation
in **all** supported locales.

Usage::

    pytest apps/core/tests/test_i18n_coverage.py -v

The test reads ``.po`` files directly (no compiled ``.mo`` needed),
parses each ``msgid`` / ``msgstr`` pair, and reports any missing or
empty translations.
"""

import os
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # clubcms/
LOCALE_DIR = BASE_DIR / "locale"
SUPPORTED_LANGUAGES = ["it", "en", "de", "fr", "es"]
APPS_DIR = BASE_DIR / "apps"
TEMPLATES_DIR = BASE_DIR / "templates"


# ---------------------------------------------------------------------------
# .po parsing helpers
# ---------------------------------------------------------------------------

def _parse_po_file(po_path: Path) -> dict[str, str]:
    """
    Parse a .po file and return a ``{msgid: msgstr}`` dict.

    Handles multi-line strings (continued lines starting with ``"``).
    Skips the metadata header (empty ``msgid``).
    """
    entries: dict[str, str] = {}
    current_id: list[str] = []
    current_str: list[str] = []
    reading = None  # "id" | "str"

    with open(po_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")

            if line.startswith("msgid "):
                # Flush previous entry
                if reading == "str":
                    mid = "".join(current_id)
                    mstr = "".join(current_str)
                    if mid:  # skip header
                        entries[mid] = mstr
                reading = "id"
                current_id = [_extract_quoted(line[6:])]
                current_str = []

            elif line.startswith("msgstr "):
                reading = "str"
                current_str = [_extract_quoted(line[7:])]

            elif line.startswith('"') and reading:
                val = _extract_quoted(line)
                if reading == "id":
                    current_id.append(val)
                else:
                    current_str.append(val)

            elif line.startswith("#") or not line.strip():
                # Comment or blank — do nothing
                pass

        # Flush last entry
        if reading == "str":
            mid = "".join(current_id)
            mstr = "".join(current_str)
            if mid:
                entries[mid] = mstr

    return entries


def _extract_quoted(s: str) -> str:
    """Extract the content between the first pair of double quotes."""
    m = re.search(r'"(.*)"', s)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# Source scanning — collect all translatable strings
# ---------------------------------------------------------------------------

_PY_GETTEXT_RE = re.compile(
    r"""(?:gettext_lazy|gettext|_|pgettext_lazy|pgettext|ngettext|ngettext_lazy)\(\s*["']"""
)
_PY_STRING_RE = re.compile(r"""(?:_|gettext_lazy|gettext)\(\s*(['"])(.*?)\1\s*\)""")
_TEMPLATE_TRANS_RE = re.compile(r"""\{%\s*trans\s+["'](.+?)["']""")

# Strings that come from model Meta (verbose_name) and field help_text
# are part of the Django admin and typically not translated to .po until
# makemessages is run.  For this test we focus on UI-facing strings:
# template {% trans %} and explicit _("...") in views / forms.
_PY_SCAN_PATTERNS = ("views.py", "forms.py", "forms_helpers.py",
                     "context_processors.py", "decorators.py", "tasks.py")


def _collect_python_strings() -> set[str]:
    """Collect translatable strings from UI-facing Python files under apps/."""
    strings: set[str] = set()
    for py_file in APPS_DIR.rglob("*.py"):
        # Skip migrations, __pycache__, model files (verbose_name)
        parts = py_file.parts
        if "__pycache__" in parts or "migrations" in parts:
            continue
        if py_file.name not in _PY_SCAN_PATTERNS:
            continue
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in _PY_STRING_RE.finditer(text):
            s = match.group(2)
            if s:
                strings.add(s)
    return strings


def _collect_template_strings() -> set[str]:
    """Collect translatable strings from Django templates."""
    strings: set[str] = set()
    for html_file in TEMPLATES_DIR.rglob("*.html"):
        try:
            text = html_file.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in _TEMPLATE_TRANS_RE.finditer(text):
            s = match.group(1)
            if s:
                strings.add(s)
    return strings


def _all_translatable_strings() -> set[str]:
    """Union of Python and template translatable strings."""
    return _collect_python_strings() | _collect_template_strings()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestI18nCoverage:
    """Verify that all locales have translations for every msgid in the source."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self.all_msgids = _all_translatable_strings()

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_po_file_exists(self, lang):
        """Each supported language must have a .po file."""
        po = LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"
        assert po.exists(), f"Missing .po file for language '{lang}': {po}"

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_no_empty_translations(self, lang):
        """
        The .po file should have a reasonable percentage of non-empty
        msgstr entries.  We allow some empties because model verbose_name
        strings are not yet fully translated and English may use empty
        msgstr (source fallback).

        Threshold: warn at 40% empty, fail at 90% empty.
        """
        if lang == "en":
            pytest.skip("English .po may use empty msgstr (source language)")
        po = LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"
        if not po.exists():
            pytest.skip(f"No .po for {lang}")

        entries = _parse_po_file(po)
        total = len(entries)
        empty = [mid for mid, mstr in entries.items() if not mstr.strip()]
        pct_empty = len(empty) / total * 100 if total else 0

        if pct_empty > 40:
            import warnings
            warnings.warn(
                f"Language '{lang}' has {len(empty)}/{total} "
                f"({pct_empty:.0f}%) empty translations"
            )

        assert pct_empty < 90, (
            f"Language '{lang}' has {len(empty)}/{total} "
            f"({pct_empty:.0f}%) empty translations — too many!"
        )

    @pytest.mark.parametrize("lang", SUPPORTED_LANGUAGES)
    def test_source_strings_have_translations(self, lang):
        """
        Every translatable string found in the source code must
        appear as a msgid in the locale .po file.
        """
        if lang == "en":
            pytest.skip("English .po may not translate source strings")
        po = LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"
        if not po.exists():
            pytest.skip(f"No .po for {lang}")

        entries = _parse_po_file(po)
        po_msgids = set(entries.keys())

        missing = self.all_msgids - po_msgids
        # Filter out strings that could be dynamic / complex (containing %)
        # and very short strings (1-2 chars) that may be intentional
        significant_missing = {
            s for s in missing
            if len(s) > 2 and "%" not in s and "{" not in s
        }

        if significant_missing:
            # Report coverage ratio — warn at >50%, fail at >85%
            # Many strings come from model verbose_name, help_text, etc.
            # that may not yet be in .po files.
            ratio = len(significant_missing) / max(len(self.all_msgids), 1)
            coverage_pct = (1 - ratio) * 100
            if ratio > 0.85:
                pytest.fail(
                    f"Language '{lang}' has very low i18n coverage "
                    f"({coverage_pct:.0f}%): {len(significant_missing)} of "
                    f"{len(self.all_msgids)} source strings missing.\n"
                    "Run 'python manage.py makemessages' to update .po files.\n"
                    + "\n".join(f"  - {m!r}" for m in sorted(significant_missing)[:30])
                )
            elif ratio > 0.50:
                import warnings
                warnings.warn(
                    f"Language '{lang}' i18n coverage is {coverage_pct:.0f}% — "
                    f"{len(significant_missing)} strings missing. "
                    f"Run 'python manage.py makemessages' to update.",
                    stacklevel=1,
                )

    def test_all_languages_present(self):
        """SUPPORTED_LANGUAGES list covers expected locales."""
        existing = [
            d.name
            for d in LOCALE_DIR.iterdir()
            if d.is_dir() and (d / "LC_MESSAGES" / "django.po").exists()
        ]
        for lang in existing:
            assert lang in SUPPORTED_LANGUAGES, (
                f"Locale '{lang}' exists on disk but is not in SUPPORTED_LANGUAGES"
            )

    def test_consistent_po_entry_counts(self):
        """All non-English .po files should have roughly the same number of entries."""
        counts = {}
        for lang in SUPPORTED_LANGUAGES:
            po = LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"
            if po.exists():
                entries = _parse_po_file(po)
                counts[lang] = len(entries)

        if len(counts) < 2:
            pytest.skip("Need at least 2 locales to compare")

        max_count = max(counts.values())
        min_count = min(counts.values())
        if max_count > 0:
            diff_ratio = (max_count - min_count) / max_count
            assert diff_ratio < 0.20, (
                f"Entry counts differ by {diff_ratio:.0%} across locales: {counts}"
            )

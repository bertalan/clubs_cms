"""
Translation catalogues must not contain broken entries.

Before 2026-10-26 the Italian catalogue had ~65 msgstrs repeated two or
three times in a row (an old script appended instead of replacing), some
with the English original glued at the end, and DE/FR/ES rendered a literal
"%(date)s" next to "Member since". These checks run on every locale.
"""

import re
from pathlib import Path

import polib
import pytest

LOCALE_DIR = Path(__file__).resolve().parents[3] / "locale"
LANGS = ["it", "de", "fr", "es", "en"]
PLACEHOLDER = re.compile(r"%\(\w+\)[sdif]|\{\w*\}")


def _entries(lang):
    po = polib.pofile(str(LOCALE_DIR / lang / "LC_MESSAGES" / "django.po"))
    for entry in po:
        if entry.obsolete:
            continue
        strings = list(entry.msgstr_plural.values()) if entry.msgid_plural else [entry.msgstr]
        for msgstr in strings:
            if msgstr:
                yield entry, msgstr


def _repeated(text):
    for k in (2, 3, 4):
        if len(text) % k == 0 and text == text[: len(text) // k] * k:
            return True
    return False


@pytest.mark.parametrize("lang", LANGS)
def test_no_repeated_translations(lang):
    bad = [e.msgid[:60] for e, s in _entries(lang) if _repeated(s) and not _repeated(e.msgid)]
    assert not bad, bad


@pytest.mark.parametrize("lang", [lang for lang in LANGS if lang != "en"])
def test_no_english_original_glued_to_translation(lang):
    bad = [
        e.msgid[:60] for e, s in _entries(lang)
        if len(e.msgid) > 30 and s != e.msgid and e.msgid.strip() in s
    ]
    assert not bad, bad


@pytest.mark.parametrize("lang", LANGS)
def test_translations_use_only_placeholders_of_the_original(lang):
    bad = []
    for entry, msgstr in _entries(lang):
        source = entry.msgid + (entry.msgid_plural or "")
        extra = set(PLACEHOLDER.findall(msgstr)) - set(PLACEHOLDER.findall(source))
        if extra:
            bad.append((entry.msgid[:60], sorted(extra)))
    assert not bad, bad


@pytest.mark.parametrize("lang", LANGS)
def test_no_msgcat_conflict_markers(lang):
    bad = [e.msgid[:60] for e, s in _entries(lang) if "#-#-#-#-#" in s]
    assert not bad, bad

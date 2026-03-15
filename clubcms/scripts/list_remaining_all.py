#!/usr/bin/env python3
"""
List remaining untranslated strings for a given language (or all languages).
Usage:
    python list_remaining_all.py              # all languages
    python list_remaining_all.py de           # only German
    python list_remaining_all.py de es fr     # multiple languages
"""
import os
import sys

LOCALE_DIR = "locale"
ALL_LANGUAGES = ["de", "en", "es", "fr", "it"]
LANG_NAMES = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
}


def parse_untranslated(filepath):
    """Return a list of untranslated (or fuzzy) msgid strings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    untranslated = []

    for block in blocks:
        lines = block.split("\n")
        msgid_lines = []
        msgstr_lines = []
        in_msgid = False
        in_msgstr = False
        is_fuzzy = "#, fuzzy" in block

        for line in lines:
            if line.startswith("msgid "):
                in_msgid = True
                in_msgstr = False
                msgid_lines.append(line[6:].strip('"'))
            elif line.startswith("msgstr "):
                in_msgid = False
                in_msgstr = True
                msgstr_lines.append(line[7:].strip('"'))
            elif line.startswith('"') and in_msgid:
                msgid_lines.append(line.strip('"'))
            elif line.startswith('"') and in_msgstr:
                msgstr_lines.append(line.strip('"'))
            else:
                in_msgid = False
                in_msgstr = False

        msgid = "".join(msgid_lines)
        msgstr = "".join(msgstr_lines)

        if msgid and (not msgstr or is_fuzzy):
            untranslated.append(msgid)

    return untranslated


def main():
    # Change to project root if running from scripts/
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")

    # Determine which languages to process
    if len(sys.argv) > 1:
        languages = [l for l in sys.argv[1:] if l in ALL_LANGUAGES]
        if not languages:
            print(f"Usage: {sys.argv[0]} [lang ...] (available: {', '.join(ALL_LANGUAGES)})")
            sys.exit(1)
    else:
        languages = ALL_LANGUAGES

    for lang in languages:
        po_path = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", "django.po")
        if not os.path.exists(po_path):
            print(f"⚠  {lang}: {po_path} not found, skipping.\n")
            continue

        untranslated = parse_untranslated(po_path)

        print("=" * 72)
        print(f"  {LANG_NAMES.get(lang, lang)} ({lang}) — {len(untranslated)} remaining untranslated")
        print("=" * 72)

        if not untranslated:
            print("  ✓ All strings are translated!\n")
            continue

        for i, s in enumerate(untranslated):
            short = s[:120].replace("\n", "\\n")
            print(f"  {i+1:4d}. {short}")
        print()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Analyze and report on .po file translation status for ALL languages.
Produces a summary table plus per-language detail.
"""
import os
import sys

LOCALE_DIR = "locale"
LANGUAGES = ["de", "en", "es", "fr", "it"]
LANG_NAMES = {
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano",
}


def parse_po(filepath):
    """Parse a .po file and return (translated, fuzzy, untranslated) lists."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    translated = []
    fuzzy_list = []
    untranslated = []

    for block in blocks:
        lines = block.strip().split("\n")
        if not lines:
            continue

        msgid_parts = []
        msgstr_parts = []
        in_msgid = False
        in_msgstr = False
        is_fuzzy = "#, fuzzy" in block

        for line in lines:
            if line.startswith("msgid "):
                in_msgid = True
                in_msgstr = False
                msgid_parts.append(line[6:].strip().strip('"'))
            elif line.startswith("msgstr "):
                in_msgid = False
                in_msgstr = True
                msgstr_parts.append(line[7:].strip().strip('"'))
            elif line.startswith('"') and in_msgid:
                msgid_parts.append(line.strip().strip('"'))
            elif line.startswith('"') and in_msgstr:
                msgstr_parts.append(line.strip().strip('"'))
            else:
                in_msgid = False
                in_msgstr = False

        msgid = "".join(msgid_parts)
        msgstr = "".join(msgstr_parts)

        if not msgid:
            continue

        if is_fuzzy:
            fuzzy_list.append(msgid)
        elif not msgstr:
            untranslated.append(msgid)
        else:
            translated.append(msgid)

    return translated, fuzzy_list, untranslated


def main():
    # Change to project root if running from scripts/
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")

    print("=" * 72)
    print("  TRANSLATION STATUS REPORT — ALL LANGUAGES")
    print("=" * 72)
    print()

    results = {}
    for lang in LANGUAGES:
        po_path = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", "django.po")
        if not os.path.exists(po_path):
            print(f"⚠  {lang}: file {po_path} not found, skipping.")
            continue
        translated, fuzzy, untranslated = parse_po(po_path)
        total = len(translated) + len(fuzzy) + len(untranslated)
        results[lang] = {
            "translated": translated,
            "fuzzy": fuzzy,
            "untranslated": untranslated,
            "total": total,
        }

    # ── Summary table ──
    print(f"{'Lang':<6} {'Name':<12} {'Total':>6} {'Translated':>11} {'Fuzzy':>6} {'Untranslated':>13} {'Coverage':>9}")
    print("-" * 72)
    for lang in LANGUAGES:
        if lang not in results:
            continue
        r = results[lang]
        total = r["total"]
        pct = (len(r["translated"]) / total * 100) if total else 0
        print(
            f"{lang:<6} {LANG_NAMES[lang]:<12} {total:>6} "
            f"{len(r['translated']):>11} {len(r['fuzzy']):>6} "
            f"{len(r['untranslated']):>13} {pct:>8.1f}%"
        )
    print()

    # ── Per-language detail ──
    show_samples = "--detail" in sys.argv or "-d" in sys.argv
    if show_samples:
        for lang in LANGUAGES:
            if lang not in results:
                continue
            r = results[lang]
            print(f"\n{'─' * 72}")
            print(f"  {LANG_NAMES[lang]} ({lang})")
            print(f"{'─' * 72}")

            if r["untranslated"]:
                print(f"\n  Untranslated ({len(r['untranslated'])}) — first 30:")
                for i, s in enumerate(r["untranslated"][:30]):
                    short = s[:90].replace("\n", "\\n")
                    print(f"    {i+1:4d}. {short}")

            if r["fuzzy"]:
                print(f"\n  Fuzzy ({len(r['fuzzy'])}) — first 20:")
                for i, s in enumerate(r["fuzzy"][:20]):
                    short = s[:90].replace("\n", "\\n")
                    print(f"    {i+1:4d}. {short}")
    else:
        print("Tip: run with --detail (-d) to show sample untranslated/fuzzy strings.")


if __name__ == "__main__":
    main()

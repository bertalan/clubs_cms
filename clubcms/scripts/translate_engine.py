#!/usr/bin/env python3
"""
Common translation engine for .po files.
Used by all language-specific translation scripts.
"""
import os
import sys


def translate_po(input_path, translations, identity=False):
    """
    Read .po file, fill in translations, write output.
    
    Args:
        input_path: path to the .po file
        translations: dict of {msgid: msgstr}
        identity: if True, set msgstr = msgid for ALL untranslated entries
                  (used for the English locale where source == target)
    Returns:
        dict with translation stats
    """
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.split("\n\n")
    result_blocks = []
    stats = {"translated": 0, "fuzzy_fixed": 0, "skipped": 0, "already": 0}

    for block in blocks:
        lines = block.split("\n")

        msgid_lines = []
        msgstr_lines = []
        comment_lines = []
        is_fuzzy = False
        in_msgid = False
        in_msgstr = False
        has_msgid_plural = False

        for line in lines:
            if line == "#, fuzzy":
                is_fuzzy = True
                comment_lines.append(line)
            elif line.startswith("#"):
                comment_lines.append(line)
                in_msgid = False
                in_msgstr = False
            elif line.startswith("msgid_plural"):
                has_msgid_plural = True
                in_msgid = False
                in_msgstr = False
            elif line.startswith("msgid "):
                in_msgid = True
                in_msgstr = False
                msgid_lines.append(line[6:].strip('"'))
            elif line.startswith("msgstr"):
                in_msgid = False
                in_msgstr = True
                if line.startswith("msgstr "):
                    msgstr_lines.append(line[7:].strip('"'))
            elif line.startswith('"') and in_msgid:
                msgid_lines.append(line.strip('"'))
            elif line.startswith('"') and in_msgstr:
                msgstr_lines.append(line.strip('"'))

        msgid = "".join(msgid_lines)
        msgstr = "".join(msgstr_lines)

        # Skip plural forms, header, and empty msgids
        if has_msgid_plural or not msgid:
            result_blocks.append(block)
            continue

        needs_translation = (not msgstr) or is_fuzzy

        # Determine the new translation
        new_msgstr = None
        if needs_translation:
            if msgid in translations:
                new_msgstr = translations[msgid]
            elif identity:
                new_msgstr = msgid  # English: source == target

        if new_msgstr is not None:
            # Rebuild block
            new_lines = [l for l in comment_lines if l != "#, fuzzy"]
            new_lines.append(f'msgid "{msgid}"')
            new_lines.append(f'msgstr "{new_msgstr}"')

            result_blocks.append("\n".join(new_lines))
            if is_fuzzy:
                stats["fuzzy_fixed"] += 1
            else:
                stats["translated"] += 1
        elif not needs_translation:
            stats["already"] += 1
            result_blocks.append(block)
        else:
            stats["skipped"] += 1
            result_blocks.append(block)

    with open(input_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(result_blocks))

    return stats


def run_translation(lang_code, lang_name, translations, identity=False):
    """Run translation for a given language and print results."""
    # Change to project root if running from scripts/
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir("..")

    po_file = f"locale/{lang_code}/LC_MESSAGES/django.po"
    if not os.path.exists(po_file):
        print(f"ERROR: {po_file} not found!")
        sys.exit(1)

    print(f"=== Translating: {lang_name} ({lang_code}) ===")
    print(f"Dictionary size: {len(translations)} entries")
    if identity:
        print("Mode: identity (msgstr = msgid for untranslated)")
    print()

    stats = translate_po(po_file, translations, identity=identity)

    print(f"Already translated:  {stats['already']}")
    print(f"Newly translated:    {stats['translated']}")
    print(f"Fuzzy fixed:         {stats['fuzzy_fixed']}")
    print(f"Still untranslated:  {stats['skipped']}")
    print(f"Total processed:     {sum(stats.values())}")

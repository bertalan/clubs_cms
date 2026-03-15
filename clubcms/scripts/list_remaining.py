#!/usr/bin/env python3
"""List remaining untranslated strings to build more translations."""

PO_FILE = "locale/it/LC_MESSAGES/django.po"

with open(PO_FILE, "r", encoding="utf-8") as f:
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

print(f"Total remaining untranslated: {len(untranslated)}")
print()
# Print all remaining, grouped by first 50 chars
for i, s in enumerate(untranslated):
    short = s[:100].replace("\n", "\\n")
    print(f"{i+1:4d}. {short}")

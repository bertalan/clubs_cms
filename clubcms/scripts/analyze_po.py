#!/usr/bin/env python3
"""Analyze and report on .po file translation status."""
import re
import sys

PO_FILE = "locale/it/LC_MESSAGES/django.po"

with open(PO_FILE, "r") as f:
    content = f.read()

# Split into blocks
blocks = content.split("\n\n")
untranslated = []
fuzzy_list = []
translated = []

for block in blocks:
    lines = block.strip().split("\n")
    if not lines:
        continue
    
    # Find msgid
    msgid_parts = []
    msgstr_parts = []
    in_msgid = False
    in_msgstr = False
    is_fuzzy = "#, fuzzy" in block
    
    for line in lines:
        if line.startswith("msgid "):
            in_msgid = True
            in_msgstr = False
            val = line[6:].strip().strip('"')
            msgid_parts.append(val)
        elif line.startswith("msgstr "):
            in_msgid = False
            in_msgstr = True
            val = line[7:].strip().strip('"')
            msgstr_parts.append(val)
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

print(f"Translated: {len(translated)}")
print(f"Fuzzy: {len(fuzzy_list)}")
print(f"Untranslated: {len(untranslated)}")
print()
print("=== SAMPLE UNTRANSLATED (first 60) ===")
for s in untranslated[:60]:
    print(repr(s))
print()
print("=== SAMPLE FUZZY (first 20) ===")
for s in fuzzy_list[:20]:
    print(repr(s))

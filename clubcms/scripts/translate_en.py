#!/usr/bin/env python3
"""
Batch-translate the English .po file for ClubCMS.
Since English IS the source language, we set msgstr = msgid (identity).
"""
from translate_engine import run_translation

# English doesn't need a dictionary — identity mode fills everything.
# But we include a few where the displayed English should differ from
# the internal msgid (e.g. locale-specific examples).
TRANSLATIONS = {
    # Override Italian-centric examples for English locale
    "Italian tax identification code, 16 characters. Example: VRDMRC85M01H501Z":
        "Italian tax identification code, 16 characters. Example: VRDMRC85M01H501Z",
    "Name and phone number to call in case of emergency. Example: Anna Verdi +39 340 7654321":
        "Name and phone number to call in case of emergency. Example: Jane Smith +1 555 0123",
    "Include country prefix. Example: +39 333 1234567":
        "Include country prefix. Example: +1 555 0123456",
}

if __name__ == "__main__":
    run_translation("en", "English", TRANSLATIONS, identity=True)

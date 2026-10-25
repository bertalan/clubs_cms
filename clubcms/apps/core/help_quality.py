"""
Heuristic for admin help texts that only restate the field label.

A useful help text says where the value comes from, its format or its
effect. One that is very short, or adds fewer than three words to the
label, is considered redundant.
"""

import re

_STOP_WORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "is", "it",
    "its", "of", "on", "or", "our", "the", "their", "this", "that", "to",
    "with", "your",
}
MIN_WORDS = 7
MIN_NEW_WORDS = 3


def _tokens(text):
    return [
        w for w in re.findall(r"[^\W\d_]+", str(text).lower()) if w not in _STOP_WORDS
    ]


def is_redundant_help(field, help_text):
    words = re.findall(r"[^\W\d_]+", str(help_text))
    label_tokens = set(_tokens(f"{field.verbose_name} {field.name.replace('_', ' ')}"))
    new_words = {w for w in _tokens(help_text) if w not in label_tokens}
    return len(words) < MIN_WORDS or len(new_words) < MIN_NEW_WORDS

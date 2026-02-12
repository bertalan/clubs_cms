"""
Federation utility functions.

Key generation for federation API key pairs and HTML sanitization
for external content received from partner clubs.
"""

import secrets

import bleach


def generate_public_key():
    """
    Generate a public API key for federation.

    Format: ``pk_`` + 24-byte URL-safe token (~32 chars).
    """
    return f"pk_{secrets.token_urlsafe(24)}"


def generate_secret_key():
    """
    Generate a secret API key for federation.

    Format: ``sk_`` + 48-byte URL-safe token (~64 chars).
    """
    return f"sk_{secrets.token_urlsafe(48)}"


def generate_api_key_pair():
    """
    Generate a (public_key, secret_key) tuple for federation.

    Returns
    -------
    tuple[str, str]
        ``(public_key, secret_key)``
    """
    return generate_public_key(), generate_secret_key()


# Allowlisted HTML tags and attributes for external content sanitisation.
_ALLOWED_TAGS = [
    "a", "abbr", "b", "blockquote", "br", "code", "dd", "div", "dl", "dt",
    "em", "h1", "h2", "h3", "h4", "h5", "h6", "hr", "i", "li", "ol", "p",
    "pre", "small", "span", "strong", "sub", "sup", "table", "tbody", "td",
    "th", "thead", "tr", "u", "ul",
]

_ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "rel", "target"],
    "abbr": ["title"],
    "td": ["colspan", "rowspan"],
    "th": ["colspan", "rowspan"],
}

_ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(html_string):
    """
    Sanitise external HTML using ``bleach`` with an explicit allowlist.

    Only safe structural and text-formatting tags are preserved.
    All event-handler attributes, ``javascript:`` URIs, ``<script>``,
    ``<style>``, ``<iframe>``, ``<svg>``, ``<math>``, ``<img>``,
    ``<object>``, ``<embed>``, ``<form>`` and similar are stripped.

    Parameters
    ----------
    html_string : str
        Raw HTML from an external source (partner club).

    Returns
    -------
    str
        Sanitised HTML safe to render in templates with ``|safe``.
    """
    if not html_string:
        return ""

    return bleach.clean(
        html_string,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    ).strip()

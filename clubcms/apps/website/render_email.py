"""
Render newsletter StreamField blocks to email-safe inline-styled HTML.

Email clients (especially Outlook, Gmail) strip ``<style>`` tags and most
CSS.  Every element therefore uses inline ``style`` attributes and
table-based layout to ensure consistent rendering.
"""

from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe


# ── Shared inline styles ──────────────────────────────────────────────────

_TEXT_STYLE = (
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.6; "
    "color: #333333; margin: 0 0 16px 0;"
)

_HEADING_STYLE = (
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif; font-size: 22px; font-weight: 600; "
    "color: #1a1a1a; margin: 24px 0 12px 0; line-height: 1.3;"
)

_BUTTON_PRIMARY = (
    "display: inline-block; padding: 12px 28px; "
    "background-color: #2563eb; color: #ffffff; "
    "text-decoration: none; border-radius: 6px; "
    "font-weight: 500; font-size: 16px; "
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif;"
)

_BUTTON_SECONDARY = (
    "display: inline-block; padding: 12px 28px; "
    "background-color: #6b7280; color: #ffffff; "
    "text-decoration: none; border-radius: 6px; "
    "font-weight: 500; font-size: 16px; "
    "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, "
    "Helvetica, Arial, sans-serif;"
)

_DIVIDER_STYLE = (
    "border: 0; border-top: 1px solid #e5e7eb; margin: 24px 0;"
)

_QUOTE_STYLE = (
    "border-left: 4px solid #2563eb; padding: 12px 16px; "
    "margin: 16px 0; background-color: #f8fafc;"
)

_QUOTE_TEXT_STYLE = (
    "font-style: italic; font-size: 16px; line-height: 1.6; "
    "color: #374151; margin: 0;"
)

_QUOTE_ATTR_STYLE = (
    "font-size: 14px; color: #6b7280; margin: 8px 0 0 0;"
)


# ── Renderer ──────────────────────────────────────────────────────────────


def render_newsletter_body_html(newsletter, base_url=""):
    """
    Render a SentNewsletter's StreamField ``body`` to email-safe HTML.

    Parameters
    ----------
    newsletter : SentNewsletter
        The newsletter instance whose ``body`` StreamField to render.
    base_url : str
        Site base URL for building absolute image URLs.

    Returns
    -------
    str (marked safe)
        Inline-styled HTML ready for embedding in an email template.
    """
    parts = []
    for block in newsletter.body:
        renderer = _BLOCK_RENDERERS.get(block.block_type)
        if renderer:
            parts.append(renderer(block.value, base_url))
    return mark_safe("\n".join(parts))


def render_newsletter_body_text(newsletter):
    """
    Render a SentNewsletter's StreamField ``body`` to plain text.

    Used as the text/plain alternative in multipart emails.
    """
    parts = []
    for block in newsletter.body:
        renderer = _TEXT_RENDERERS.get(block.block_type)
        if renderer:
            parts.append(renderer(block.value))
    return "\n\n".join(parts)


# ── HTML block renderers ──────────────────────────────────────────────────


def _render_heading(value, base_url):
    return format_html('<h2 style="{}">{}</h2>', _HEADING_STYLE, value)


def _render_text(value, base_url):
    # RichTextBlock value is already safe HTML from Wagtail
    html = str(value)
    return f'<div style="{_TEXT_STYLE}">{html}</div>'


def _render_image(value, base_url):
    image = value.get("image")
    if not image:
        return ""
    caption = value.get("caption", "")
    alt = value.get("alt_text", "") or caption or image.title
    # Use a rendition suitable for email (max 560px wide)
    try:
        rendition = image.get_rendition("width-560")
        src = rendition.url
        if base_url and src.startswith("/"):
            src = base_url + src
    except Exception:
        return ""

    html = format_html(
        '<div style="text-align: center; margin: 16px 0;">'
        '<img src="{}" alt="{}" width="{}" '
        'style="max-width: 100%; height: auto; border-radius: 6px; display: block; margin: 0 auto;" />'
        "</div>",
        src,
        alt,
        rendition.width,
    )
    if caption:
        html += format_html(
            '<p style="text-align: center; font-size: 13px; color: #6b7280; '
            'margin: 4px 0 16px 0;">{}</p>',
            caption,
        )
    return html


def _render_button(value, base_url):
    text = value.get("text", "")
    url = value.get("url", "")
    style_choice = value.get("style", "primary")
    btn_style = _BUTTON_PRIMARY if style_choice == "primary" else _BUTTON_SECONDARY
    return format_html(
        '<div style="text-align: center; margin: 20px 0;">'
        '<a href="{}" style="{}">{}</a>'
        "</div>",
        url,
        btn_style,
        text,
    )


def _render_divider(value, base_url):
    return format_html('<hr style="{}" />', _DIVIDER_STYLE)


def _render_quote(value, base_url):
    text = value.get("text", "")
    attribution = value.get("attribution", "")
    html = format_html(
        '<blockquote style="{}">'
        '<p style="{}">{}</p>',
        _QUOTE_STYLE,
        _QUOTE_TEXT_STYLE,
        text,
    )
    if attribution:
        html += format_html(
            '<p style="{}">— {}</p>',
            _QUOTE_ATTR_STYLE,
            attribution,
        )
    html += "</blockquote>"
    return html


# ── Plain text block renderers ────────────────────────────────────────────


def _text_heading(value):
    return str(value).upper()


def _text_text(value):
    from django.utils.html import strip_tags
    return strip_tags(str(value))


def _text_image(value):
    caption = value.get("caption", "")
    alt = value.get("alt_text", "")
    return f"[{alt or caption or 'Image'}]"


def _text_button(value):
    text = value.get("text", "")
    url = value.get("url", "")
    return f"{text}: {url}"


def _text_divider(value):
    return "---"


def _text_quote(value):
    text = value.get("text", "")
    attribution = value.get("attribution", "")
    result = f'"{text}"'
    if attribution:
        result += f"\n— {attribution}"
    return result


# ── Registries ────────────────────────────────────────────────────────────

_BLOCK_RENDERERS = {
    "heading": _render_heading,
    "text": _render_text,
    "image": _render_image,
    "button": _render_button,
    "divider": _render_divider,
    "quote": _render_quote,
}

_TEXT_RENDERERS = {
    "heading": _text_heading,
    "text": _text_text,
    "image": _text_image,
    "button": _text_button,
    "divider": _text_divider,
    "quote": _text_quote,
}

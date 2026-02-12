"""
Template tags for SEO: JSON-LD, Open Graph, Twitter Cards, hreflang,
canonical URL, breadcrumb schema, and feed discovery.

Load in templates with::

    {% load seo_tags %}
"""

from django import template
from django.utils.safestring import mark_safe

from apps.core.seo import (
    _get_site_settings,
    _json_ld_script,
    get_article_schema,
    get_breadcrumb_schema,
    get_contact_page_schema,
    get_event_schema,
    get_item_list_schema,
    get_og_tags,
    get_organization_schema,
    get_twitter_tags,
)

register = template.Library()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _page_class_name(page):
    """Return the lowercased class name of a page instance."""
    return page.__class__.__name__.lower() if page else ""


# ─────────────────────────────────────────────────────────────────────────────
# 1. json_ld_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def json_ld_tag(context):
    """
    Output the appropriate JSON-LD ``<script>`` block for the current page.

    Dispatches to the correct schema generator based on page type:
    - HomePage       -> Organization
    - NewsPage       -> Article
    - EventDetailPage -> Event
    - ContactPage    -> ContactPage
    - NewsIndexPage / EventsPage -> ItemList
    - Other pages    -> generic WebPage
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    site_settings = _get_site_settings(request)
    cls = _page_class_name(page)

    if cls == "homepage":
        data = get_organization_schema(site_settings, request)
    elif cls == "newspage":
        data = get_article_schema(page, request, site_settings)
    elif cls == "eventdetailpage":
        data = get_event_schema(page, request, site_settings)
    elif cls == "contactpage":
        data = get_contact_page_schema(page, request, site_settings)
    elif cls in ("newsindexpage", "eventspage"):
        # Try to get child items for the list schema
        items = []
        if cls == "newsindexpage":
            items = context.get("news_items", [])
        elif cls == "eventspage":
            items = context.get("events", [])
        data = get_item_list_schema(page, items, request)
    else:
        # Generic WebPage fallback
        data = {
            "@type": "WebPage",
            "name": page.title,
            "url": request.build_absolute_uri(page.url),
        }
        desc = getattr(page, "search_description", "") or getattr(page, "intro", "")
        if desc:
            data["description"] = desc

    return _json_ld_script(data)


# ─────────────────────────────────────────────────────────────────────────────
# 2. og_tags_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def og_tags_tag(context):
    """
    Output Open Graph ``<meta>`` tags for the current page.
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    tags = get_og_tags(page, request)
    lines = []
    for prop, content in tags.items():
        escaped = str(content).replace('"', "&quot;")
        lines.append(f'<meta property="{prop}" content="{escaped}">')
    return mark_safe("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 3. twitter_tags_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def twitter_tags_tag(context):
    """
    Output Twitter Card ``<meta>`` tags for the current page.
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    tags = get_twitter_tags(page, request)
    lines = []
    for name, content in tags.items():
        escaped = str(content).replace('"', "&quot;")
        lines.append(f'<meta name="{name}" content="{escaped}">')
    return mark_safe("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 4. hreflang_tags_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def hreflang_tags_tag(context):
    """
    Output ``<link rel="alternate" hreflang="...">`` tags for all
    translations of the current page (using Wagtail's i18n API).
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    lines = []
    try:
        translations = page.get_translations(inclusive=True)
        for translation in translations:
            if not translation.live:
                continue
            lang_code = str(translation.locale.language_code)
            url = request.build_absolute_uri(translation.url)
            lines.append(
                f'<link rel="alternate" hreflang="{lang_code}" href="{url}">'
            )
        # Add x-default pointing to the page in its own locale
        if lines:
            own_url = request.build_absolute_uri(page.url)
            lines.append(
                f'<link rel="alternate" hreflang="x-default" href="{own_url}">'
            )
    except Exception:
        # Translations not available (wagtail_localize not configured, etc.)
        pass

    return mark_safe("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 5. breadcrumb_json_ld_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def breadcrumb_json_ld_tag(context):
    """
    Output a JSON-LD BreadcrumbList ``<script>`` block by walking the
    page ancestors.
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    data = get_breadcrumb_schema(page, request)
    return _json_ld_script(data)


# ─────────────────────────────────────────────────────────────────────────────
# 6. canonical_url_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def canonical_url_tag(context):
    """
    Output a ``<link rel="canonical">`` tag for the current page.
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    url = request.build_absolute_uri(page.url)
    return mark_safe(f'<link rel="canonical" href="{url}">')


# ─────────────────────────────────────────────────────────────────────────────
# 7. feed_discovery_tag
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag(takes_context=True)
def feed_discovery_tag(context):
    """
    Output ``<link rel="alternate">`` tags for RSS and Atom feed discovery.
    """
    request = context.get("request")
    if not request:
        return ""

    site_settings = _get_site_settings(request)
    site_name = ""
    if site_settings:
        site_name = getattr(site_settings, "site_name", "") or "Club CMS"
    else:
        site_name = "Club CMS"

    lines = [
        f'<link rel="alternate" type="application/rss+xml" title="{site_name} - News (RSS)" href="/feed/rss/">',
        f'<link rel="alternate" type="application/atom+xml" title="{site_name} - News (Atom)" href="/feed/atom/">',
        f'<link rel="alternate" type="application/rss+xml" title="{site_name} - Events (RSS)" href="/feed/events/rss/">',
    ]
    return mark_safe("\n".join(lines))

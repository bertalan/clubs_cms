"""
Template tags for SEO: JSON-LD, Open Graph, Twitter Cards, hreflang,
canonical URL, breadcrumb schema, and feed discovery.

Load in templates with::

    {% load seo_tags %}
"""

import re

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

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
            items = context.get("news_pages", context.get("news_items", []))
        elif cls == "eventspage":
            items = context.get("event_pages", context.get("events", []))
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

    If ``SiteSettings.canonical_domain`` is set, uses that domain
    instead of the request host.
    """
    request = context.get("request")
    page = context.get("self")
    if not page or not request:
        return ""

    site_settings = _get_site_settings(request)
    canonical_domain = (
        getattr(site_settings, "canonical_domain", "") or ""
    ).rstrip("/")

    if canonical_domain:
        url = f"{canonical_domain}{page.url}"
    else:
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

    news_rss = _("News (RSS)")
    news_atom = _("News (Atom)")
    events_rss = _("Events (RSS)")
    lines = [
        f'<link rel="alternate" type="application/rss+xml" title="{site_name} - {news_rss}" href="/feed/rss/">',
        f'<link rel="alternate" type="application/atom+xml" title="{site_name} - {news_atom}" href="/feed/atom/">',
        f'<link rel="alternate" type="application/rss+xml" title="{site_name} - {events_rss}" href="/feed/events/rss/">',
    ]
    return mark_safe("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# 8. strip_language_prefix filter (for language switcher)
# ─────────────────────────────────────────────────────────────────────────────


@register.filter
def strip_language_prefix(path):
    """
    Remove the language prefix from a URL path.

    Example:
        {{ "/it/chi-siamo/"|strip_language_prefix }}  -> "/chi-siamo/"
        {{ "/en/about/"|strip_language_prefix }}      -> "/about/"

    This is useful for the language switcher where we need the path
    without the current language prefix so Django can add the new one.
    """
    if not path:
        return path

    # Build pattern from available languages
    lang_codes = [code for code, _ in settings.LANGUAGES]
    pattern = r"^/(" + "|".join(re.escape(code) for code in lang_codes) + r")/"

    # Strip the language prefix
    stripped = re.sub(pattern, "/", path)
    return stripped


# ─────────────────────────────────────────────────────────────────────────────
# 8b. translate_url tag — resolve URL in target language
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag
def translate_url(path, lang_code):
    """
    Return the equivalent URL path in the given language.

    Activates the source language (detected from the URL prefix) before
    resolving, then reverses under the target language so translated URL
    segments are handled (e.g. /it/eventi/miei-eventi/ → /en/events/my-events/).

    For Wagtail catch-all pages it falls back to swapping the language prefix.

    Usage:
        {% translate_url request.get_full_path "en" %}
    """
    from django.urls import resolve, reverse
    from django.utils.translation import override

    # Detect the source language from the URL prefix
    lang_codes = [code for code, _ in settings.LANGUAGES]
    source_lang = None
    for code in lang_codes:
        if path.startswith(f"/{code}/"):
            source_lang = code
            break

    # Try to resolve and reverse in the target language
    try:
        with override(source_lang or settings.LANGUAGE_CODE):
            match = resolve(path)
        to_be_reversed = (
            f"{match.namespace}:{match.url_name}" if match.namespace
            else match.url_name
        )
        with override(lang_code):
            return reverse(to_be_reversed, args=match.args, kwargs=match.kwargs)
    except Exception:
        pass

    # Fallback: swap language prefix (covers Wagtail catch-all pages)
    prefix_pattern = r"^/(" + "|".join(re.escape(c) for c in lang_codes) + r")/"
    return re.sub(prefix_pattern, f"/{lang_code}/", path)


# ─────────────────────────────────────────────────────────────────────────────
# 9. get_active_locales - return Wagtail Locales for language switcher
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag
def get_active_locales():
    """
    Return list of active Wagtail Locales as (language_code, language_name) tuples.

    This uses the Locale model from Wagtail to get only the languages
    that are actually configured in the CMS, rather than all languages
    defined in settings.LANGUAGES.

    Usage in templates:
        {% get_active_locales as locales %}
        {% for lang_code, lang_name in locales %}
            ...
        {% endfor %}
    """
    from wagtail.models import Locale

    # Build a lookup dict from settings.LANGUAGES
    lang_names = dict(settings.LANGUAGES)

    # Get active locales from Wagtail; fall back to settings.LANGUAGES
    # if no Locale records exist (e.g. fresh install).
    locales = Locale.objects.all().order_by("language_code")
    if locales.exists():
        return [
            (locale.language_code, lang_names.get(locale.language_code, locale.language_code))
            for locale in locales
        ]
    return list(settings.LANGUAGES)


# ─────────────────────────────────────────────────────────────────────────────
# 10. localized_slugurl — locale-aware version of Wagtail's slugurl
# ─────────────────────────────────────────────────────────────────────────────


@register.simple_tag
def localized_slugurl(slug):
    """
    Find a page by slug and return its localized URL.

    Unlike Wagtail's built-in ``{% slugurl %}``, this applies ``.localized``
    so the resulting URL matches the active language.

    Usage:
        {% localized_slugurl 'federazione' as fed_url %}
    """
    from wagtail.models import Page

    page = Page.objects.filter(slug=slug).live().first()
    if page:
        return page.localized.url
    return ""

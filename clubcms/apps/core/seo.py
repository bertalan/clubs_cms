"""
SEO utilities: JSON-LD structured data, Open Graph, and Twitter Card helpers.

Provides:
- JsonLdMixin           -- Wagtail page mixin for JSON-LD injection
- get_organization_schema  -- schema.org/Organization from SiteSettings
- get_article_schema       -- schema.org/Article for NewsPage
- get_event_schema         -- schema.org/Event for EventDetailPage
- get_contact_page_schema  -- schema.org/ContactPage
- get_item_list_schema     -- schema.org/ItemList for index pages
- get_breadcrumb_schema    -- schema.org/BreadcrumbList from page ancestors
- get_og_tags              -- Open Graph meta tag dict
- get_twitter_tags         -- Twitter Card meta tag dict
"""

import json
from datetime import date, datetime

from django.utils.safestring import mark_safe


# ─────────────────────────────────────────────────────────────────────────────
# JSON-LD mixin (kept for backward compatibility)
# ─────────────────────────────────────────────────────────────────────────────


class JsonLdMixin:
    """
    Mixin that adds JSON-LD structured data to Wagtail pages.

    Subclasses should implement ``get_json_ld()`` returning a dictionary
    of schema.org properties.  The ``@context`` key is added automatically.
    """

    def get_json_ld(self):
        """Override in subclasses to return schema.org data as a dict."""
        return {
            "@type": "WebPage",
            "name": getattr(self, "title", ""),
        }

    def get_json_ld_script(self):
        """Return the complete JSON-LD ``<script>`` tag as safe HTML."""
        data = self.get_json_ld()
        if not data:
            return ""
        if "@context" not in data:
            data["@context"] = "https://schema.org"
        serialised = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
        return mark_safe(
            '<script type="application/ld+json">'
            f"{serialised}"
            "</script>"
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["json_ld"] = self.get_json_ld_script()
        return context


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────


def _get_site_settings(request):
    """Return SiteSettings for the current request, or None on failure."""
    try:
        from apps.website.models import SiteSettings

        return SiteSettings.for_request(request)
    except Exception:
        return None


def _get_absolute_image_url(image, request, spec="fill-1200x630"):
    """Return absolute URL for an image rendition, or empty string."""
    if not image:
        return ""
    try:
        rendition = image.get_rendition(spec)
        return request.build_absolute_uri(rendition.url)
    except Exception:
        return ""


def _to_iso(value):
    """Convert date/datetime to ISO-8601 string, or return empty string."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return ""


def _json_ld_script(data):
    """Wrap a schema dict in a ``<script type="application/ld+json">`` tag."""
    if not data:
        return ""
    if "@context" not in data:
        data["@context"] = "https://schema.org"
    serialised = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return mark_safe(
        '<script type="application/ld+json">'
        f"{serialised}"
        "</script>"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Schema generators
# ─────────────────────────────────────────────────────────────────────────────


def get_organization_schema(site_settings, request):
    """
    Build a schema.org/Organization dict from SiteSettings.

    Returns an empty dict when *site_settings* is ``None``.
    """
    if not site_settings:
        return {}

    schema = {
        "@type": "Organization",
        "name": getattr(site_settings, "site_name", "") or "Club CMS",
        "url": request.build_absolute_uri("/"),
    }

    # Logo
    logo_url = _get_absolute_image_url(
        getattr(site_settings, "logo", None), request, "original"
    )
    if logo_url:
        schema["logo"] = logo_url

    # Description
    description = getattr(site_settings, "description", "")
    if description:
        schema["description"] = description

    # Contact info
    phone = getattr(site_settings, "phone", "")
    if phone:
        schema["telephone"] = phone

    email = getattr(site_settings, "email", "")
    if email:
        schema["email"] = email

    address = getattr(site_settings, "address", "")
    if address:
        schema["address"] = {
            "@type": "PostalAddress",
            "streetAddress": address,
        }

    # Social profiles
    same_as = []
    for field in (
        "facebook_url",
        "instagram_url",
        "twitter_url",
        "youtube_url",
        "linkedin_url",
        "tiktok_url",
    ):
        val = getattr(site_settings, field, "")
        if val:
            same_as.append(val)
    if same_as:
        schema["sameAs"] = same_as

    return schema


def get_article_schema(page, request, site_settings=None):
    """
    Build a schema.org/Article dict from a NewsPage instance.
    """
    site_settings = site_settings or _get_site_settings(request)

    schema = {
        "@type": "Article",
        "headline": page.title,
        "url": request.build_absolute_uri(page.url),
    }

    # Image
    cover_url = _get_absolute_image_url(
        getattr(page, "cover_image", None), request
    )
    if cover_url:
        schema["image"] = cover_url

    # Description
    intro = getattr(page, "intro", "") or getattr(page, "search_description", "")
    if intro:
        schema["description"] = intro

    # Dates
    display_date = getattr(page, "display_date", None)
    if display_date:
        schema["datePublished"] = _to_iso(display_date)

    last_pub = getattr(page, "last_published_at", None)
    if last_pub:
        schema["dateModified"] = _to_iso(last_pub)

    # Author
    author = getattr(page, "author", None)
    if author:
        full_name = author.get_full_name() if hasattr(author, "get_full_name") else str(author)
        if full_name:
            schema["author"] = {
                "@type": "Person",
                "name": full_name,
            }

    # Publisher (organization)
    if site_settings:
        publisher = {
            "@type": "Organization",
            "name": getattr(site_settings, "site_name", "") or "Club CMS",
        }
        logo_url = _get_absolute_image_url(
            getattr(site_settings, "logo", None), request, "original"
        )
        if logo_url:
            publisher["logo"] = {
                "@type": "ImageObject",
                "url": logo_url,
            }
        schema["publisher"] = publisher

    return schema


def get_event_schema(page, request, site_settings=None):
    """
    Build a schema.org/Event dict from an EventDetailPage instance.
    """
    site_settings = site_settings or _get_site_settings(request)

    schema = {
        "@type": "Event",
        "name": page.title,
        "url": request.build_absolute_uri(page.url),
    }

    # Image
    cover_url = _get_absolute_image_url(
        getattr(page, "cover_image", None), request
    )
    if cover_url:
        schema["image"] = cover_url

    # Description
    intro = getattr(page, "intro", "") or getattr(page, "search_description", "")
    if intro:
        schema["description"] = intro

    # Dates
    start_date = getattr(page, "start_date", None)
    if start_date:
        schema["startDate"] = _to_iso(start_date)

    end_date = getattr(page, "end_date", None)
    if end_date:
        schema["endDate"] = _to_iso(end_date)

    # Location
    location_name = getattr(page, "location_name", "")
    location_address = getattr(page, "location_address", "")
    if location_name or location_address:
        location = {"@type": "Place"}
        if location_name:
            location["name"] = location_name
        if location_address:
            location["address"] = {
                "@type": "PostalAddress",
                "streetAddress": location_address,
            }
        schema["location"] = location

    # Event status
    if getattr(page, "is_past", False):
        schema["eventStatus"] = "https://schema.org/EventScheduled"
        schema["eventAttendanceMode"] = "https://schema.org/OfflineEventAttendanceMode"

    # Offers (pricing)
    base_fee = getattr(page, "base_fee", 0)
    if base_fee and float(base_fee) > 0:
        schema["offers"] = {
            "@type": "Offer",
            "price": str(base_fee),
            "priceCurrency": "EUR",
            "availability": (
                "https://schema.org/InStock"
                if getattr(page, "is_registration_open", False)
                else "https://schema.org/SoldOut"
            ),
            "url": request.build_absolute_uri(page.url),
        }
    else:
        schema["isAccessibleForFree"] = True

    # Organizer
    if site_settings:
        schema["organizer"] = {
            "@type": "Organization",
            "name": getattr(site_settings, "site_name", "") or "Club CMS",
            "url": request.build_absolute_uri("/"),
        }

    return schema


def get_contact_page_schema(page, request, site_settings=None):
    """
    Build a schema.org/ContactPage dict from a ContactPage instance.
    """
    site_settings = site_settings or _get_site_settings(request)

    schema = {
        "@type": "ContactPage",
        "name": page.title,
        "url": request.build_absolute_uri(page.url),
    }

    intro = getattr(page, "intro", "") or getattr(page, "search_description", "")
    if intro:
        schema["description"] = intro

    if site_settings:
        phone = getattr(site_settings, "phone", "")
        if phone:
            schema["telephone"] = phone
        email = getattr(site_settings, "email", "")
        if email:
            schema["email"] = email

    return schema


def get_item_list_schema(page, items, request):
    """
    Build a schema.org/ItemList for index pages (news, events).

    *items* should be a queryset or iterable of Wagtail pages.
    """
    schema = {
        "@type": "ItemList",
        "name": page.title,
        "url": request.build_absolute_uri(page.url),
        "numberOfItems": len(items) if hasattr(items, "__len__") else 0,
    }

    elements = []
    for position, item in enumerate(items, start=1):
        element = {
            "@type": "ListItem",
            "position": position,
            "url": request.build_absolute_uri(item.url),
            "name": item.title,
        }
        elements.append(element)
        if position >= 20:  # cap at 20 items in schema
            break

    if elements:
        schema["itemListElement"] = elements

    return schema


def get_breadcrumb_schema(page, request):
    """
    Build a schema.org/BreadcrumbList by walking page ancestors.
    """
    ancestors = page.get_ancestors(inclusive=True).live()
    items = []

    for position, ancestor in enumerate(ancestors, start=1):
        # Skip the Wagtail root page (depth=1)
        if ancestor.depth <= 1:
            continue
        items.append(
            {
                "@type": "ListItem",
                "position": position - 1,  # adjust for skipped root
                "name": ancestor.title,
                "item": request.build_absolute_uri(ancestor.url),
            }
        )

    if not items:
        return {}

    # Re-number positions starting from 1
    for i, item in enumerate(items, start=1):
        item["position"] = i

    return {
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Open Graph / Twitter Card helpers
# ─────────────────────────────────────────────────────────────────────────────


def get_og_tags(page, request, site_settings=None):
    """
    Return a dict of Open Graph meta tags for the given page.

    Keys are the ``property`` attribute values (e.g. ``og:title``).
    """
    site_settings = site_settings or _get_site_settings(request)

    tags = {
        "og:title": page.seo_title or page.title,
        "og:url": request.build_absolute_uri(page.url),
        "og:type": "website",
    }

    # Description
    desc = (
        getattr(page, "search_description", "")
        or getattr(page, "intro", "")
    )
    if not desc and site_settings:
        desc = getattr(site_settings, "description", "")
    if desc:
        tags["og:description"] = desc

    # Image
    cover_url = _get_absolute_image_url(
        getattr(page, "cover_image", None)
        or getattr(page, "hero_image", None),
        request,
    )
    if cover_url:
        tags["og:image"] = cover_url

    # Site name
    if site_settings:
        tags["og:site_name"] = getattr(site_settings, "site_name", "") or "Club CMS"

    # Locale
    lang = getattr(page, "locale", None)
    if lang:
        tags["og:locale"] = str(lang).replace("-", "_")

    return tags


def get_twitter_tags(page, request, site_settings=None):
    """
    Return a dict of Twitter Card meta tags for the given page.

    Keys are the ``name`` attribute values (e.g. ``twitter:card``).
    """
    site_settings = site_settings or _get_site_settings(request)

    tags = {
        "twitter:card": "summary_large_image",
        "twitter:title": page.seo_title or page.title,
    }

    # Description
    desc = (
        getattr(page, "search_description", "")
        or getattr(page, "intro", "")
    )
    if not desc and site_settings:
        desc = getattr(site_settings, "description", "")
    if desc:
        tags["twitter:description"] = desc

    # Image
    cover_url = _get_absolute_image_url(
        getattr(page, "cover_image", None)
        or getattr(page, "hero_image", None),
        request,
    )
    if cover_url:
        tags["twitter:image"] = cover_url

    # Twitter handle from URL
    if site_settings:
        twitter_url = getattr(site_settings, "twitter_url", "")
        if twitter_url:
            # Extract handle from URL like https://twitter.com/handle
            handle = twitter_url.rstrip("/").split("/")[-1]
            if handle and not handle.startswith("@"):
                handle = f"@{handle}"
            if handle:
                tags["twitter:site"] = handle

    return tags

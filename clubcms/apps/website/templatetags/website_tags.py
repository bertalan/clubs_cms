"""
Custom template tags for the website app.
"""

from django import template
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def block_attrs(settings, base_class=""):
    """
    Render HTML attributes from a BlockSettings value.

    Usage::

        {% block_attrs self.settings "block-cta" %}

    Output example::

        id="my-section" class="block-cta bg-primary pad-lg extra-class"
    """
    if not settings:
        if base_class:
            return mark_safe(f'class="{base_class}"')
        return mark_safe("")

    parts = []

    # id
    custom_id = settings.get("custom_id", "")
    if custom_id:
        # Sanitize: only allow alphanumeric, hyphens, underscores
        safe_id = "".join(c for c in custom_id if c.isalnum() or c in "-_")
        if safe_id:
            parts.append(f'id="{safe_id}"')

    # class
    classes = []
    if base_class:
        classes.append(base_class)
    bg = settings.get("background", "default")
    if bg and bg != "default":
        classes.append(f"bg-{bg}")
    pad = settings.get("padding", "md")
    if pad and pad != "md":
        classes.append(f"pad-{pad}")
    custom_class = settings.get("custom_class", "")
    if custom_class:
        # Sanitize: strip dangerous chars
        safe_class = " ".join(
            c for c in custom_class.split() if all(ch.isalnum() or ch in "-_" for ch in c)
        )
        if safe_class:
            classes.append(safe_class)
    if classes:
        parts.append(f'class="{" ".join(classes)}"')

    return mark_safe(" ".join(parts))


@register.simple_tag
def upcoming_events(count=3):
    """Return up to `count` upcoming (future) events, ordered by start_date."""
    from apps.website.models import EventDetailPage

    return list(
        EventDetailPage.objects.live()
        .filter(start_date__gte=timezone.now())
        .order_by("start_date")[:count]
    )


@register.simple_tag
def homepage_partners(count=6):
    """Return up to `count` active partners marked for homepage display."""
    from apps.website.models import PartnerPage

    qs = (
        PartnerPage.objects.live()
        .filter(show_on_homepage=True)
        .order_by("display_order", "title")[:count]
    )
    results = list(qs)
    # Fallback: if none are flagged for homepage, show featured partners
    if not results:
        results = list(
            PartnerPage.objects.live()
            .filter(is_featured=True)
            .order_by("display_order", "title")[:count]
        )
    # Final fallback: show any active partners
    if not results:
        results = list(
            PartnerPage.objects.live()
            .order_by("display_order", "title")[:count]
        )
    return results


@register.simple_tag
def partner_index_url():
    """Return the URL of the PartnerIndexPage, or '#' if not found."""
    from apps.website.models import PartnerIndexPage

    page = PartnerIndexPage.objects.live().first()
    if page:
        return page.url
    return "#"


@register.simple_tag
def events_index_url():
    """Return the URL of the EventsPage, or '#' if not found."""
    from apps.website.models import EventsPage

    page = EventsPage.objects.live().first()
    if page:
        return page.url
    return "#"

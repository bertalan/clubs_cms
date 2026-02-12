"""
Custom template tags for the website app.
"""

from django import template
from django.utils import timezone

register = template.Library()


@register.simple_tag
def upcoming_events(count=3):
    """Return up to `count` upcoming (future) events, ordered by start_date."""
    from apps.website.models import EventDetailPage

    return list(
        EventDetailPage.objects.live()
        .filter(start_date__gte=timezone.now())
        .order_by("start_date")[:count]
    )

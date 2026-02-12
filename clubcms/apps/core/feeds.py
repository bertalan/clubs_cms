"""
RSS and Atom feeds for news articles and upcoming events.

Feeds:
- LatestNewsFeed       -- RSS 2.0 feed of the 20 most recent news articles
- LatestNewsAtomFeed   -- Atom 1.0 version of the news feed
- UpcomingEventsFeed   -- RSS 2.0 feed of the next 20 upcoming events
"""

from datetime import datetime, time

from django.contrib.syndication.views import Feed
from django.utils import timezone
from django.utils.feedgenerator import Atom1Feed


# ─────────────────────────────────────────────────────────────────────────────
# News feeds
# ─────────────────────────────────────────────────────────────────────────────


class LatestNewsFeed(Feed):
    """RSS 2.0 feed of the latest 20 news articles."""

    title = "Club CMS - News"
    description = "Latest news and articles"

    def link(self):
        try:
            from apps.website.models.pages import NewsIndexPage

            index = NewsIndexPage.objects.live().first()
            if index:
                return index.full_url
        except Exception:
            pass
        return "/"

    def items(self):
        try:
            from apps.website.models.pages import NewsPage

            return (
                NewsPage.objects.live()
                .public()
                .order_by("-display_date", "-first_published_at")[:20]
            )
        except Exception:
            return []

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return getattr(item, "intro", "") or getattr(item, "search_description", "") or ""

    def item_pubdate(self, item):
        display_date = getattr(item, "display_date", None)
        if display_date:
            # display_date is a DateField; convert to datetime for the feed
            if isinstance(display_date, datetime):
                return display_date
            return datetime.combine(display_date, time.min, tzinfo=timezone.utc)
        return getattr(item, "first_published_at", None)

    def item_link(self, item):
        return item.full_url

    def item_author_name(self, item):
        author = getattr(item, "author", None)
        if author and hasattr(author, "get_full_name"):
            return author.get_full_name() or str(author)
        return ""

    def item_categories(self, item):
        categories = []
        category = getattr(item, "category", None)
        if category:
            categories.append(str(category))
        try:
            for tag in item.tags.all():
                categories.append(tag.name)
        except Exception:
            pass
        return categories


class LatestNewsAtomFeed(LatestNewsFeed):
    """Atom 1.0 version of the news feed."""

    feed_type = Atom1Feed
    subtitle = LatestNewsFeed.description


# ─────────────────────────────────────────────────────────────────────────────
# Events feed
# ─────────────────────────────────────────────────────────────────────────────


class UpcomingEventsFeed(Feed):
    """RSS 2.0 feed of the next 20 upcoming events."""

    title = "Club CMS - Upcoming Events"
    description = "Upcoming events and activities"

    def link(self):
        try:
            from apps.website.models.pages import EventsPage

            index = EventsPage.objects.live().first()
            if index:
                return index.full_url
        except Exception:
            pass
        return "/"

    def items(self):
        try:
            from apps.website.models.pages import EventDetailPage

            now = timezone.now()
            return (
                EventDetailPage.objects.live()
                .public()
                .filter(start_date__gte=now)
                .order_by("start_date")[:20]
            )
        except Exception:
            return []

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        parts = []
        intro = getattr(item, "intro", "")
        if intro:
            parts.append(intro)
        location = getattr(item, "location_name", "")
        if location:
            parts.append(f"Location: {location}")
        start = getattr(item, "start_date", None)
        if start:
            parts.append(f"Date: {start.strftime('%d/%m/%Y %H:%M')}")
        return " | ".join(parts) if parts else ""

    def item_pubdate(self, item):
        return getattr(item, "first_published_at", None)

    def item_link(self, item):
        return item.full_url

    def item_categories(self, item):
        categories = []
        category = getattr(item, "category", None)
        if category:
            categories.append(str(category))
        try:
            for tag in item.tags.all():
                categories.append(tag.name)
        except Exception:
            pass
        return categories

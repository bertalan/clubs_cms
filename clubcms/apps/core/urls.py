"""
URL patterns for the core app: feeds for RSS/Atom syndication.

Search is handled by SearchPage (RoutablePageMixin) in the Wagtail
page tree. Contributions are handled by ContributionsPage.

Include these in the project ``urls.py`` **before** the Wagtail catch-all::

    urlpatterns = [
        ...
        path("", include("apps.core.urls")),
        path("", include(wagtail_urls)),   # catch-all last
    ]
"""

from django.urls import path

from apps.core.feeds import LatestNewsAtomFeed, LatestNewsFeed, UpcomingEventsFeed

urlpatterns = [
    # News feeds (technical paths — not translated)
    path("feed/rss/", LatestNewsFeed(), name="feed-news-rss"),
    path("feed/atom/", LatestNewsAtomFeed(), name="feed-news-atom"),
    path("feed/events/rss/", UpcomingEventsFeed(), name="feed-events-rss"),
]

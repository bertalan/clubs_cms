"""
URL patterns for the core app: feeds and robots.txt.

Include these in the project ``urls.py`` **before** the Wagtail catch-all::

    urlpatterns = [
        ...
        path("", include("apps.core.urls")),
        path("", include(wagtail_urls)),   # catch-all last
    ]
"""

from django.urls import path

from apps.core.feeds import LatestNewsAtomFeed, LatestNewsFeed, UpcomingEventsFeed
from apps.core.views import RobotsTxtView

urlpatterns = [
    # News feeds
    path("feed/rss/", LatestNewsFeed(), name="feed-news-rss"),
    path("feed/atom/", LatestNewsAtomFeed(), name="feed-news-atom"),
    # Events feed
    path("feed/events/rss/", UpcomingEventsFeed(), name="feed-events-rss"),
    # robots.txt
    path("robots.txt", RobotsTxtView.as_view(), name="robots-txt"),
]

"""
URL patterns for the core app: feeds, robots.txt, and site search.

Include these in the project ``urls.py`` **before** the Wagtail catch-all::

    urlpatterns = [
        ...
        path("", include("apps.core.urls")),
        path("", include(wagtail_urls)),   # catch-all last
    ]
"""

from django.urls import path
from django.utils.translation import gettext_lazy as _

from apps.core.feeds import LatestNewsAtomFeed, LatestNewsFeed, UpcomingEventsFeed
from apps.core.views import RobotsTxtView, SearchView

urlpatterns = [
    # Site-wide search
    path(_("search/"), SearchView.as_view(), name="site-search"),
    # News feeds (technical paths — not translated)
    path("feed/rss/", LatestNewsFeed(), name="feed-news-rss"),
    path("feed/atom/", LatestNewsAtomFeed(), name="feed-news-atom"),
    path("feed/events/rss/", UpcomingEventsFeed(), name="feed-events-rss"),
    # robots.txt
    path("robots.txt", RobotsTxtView.as_view(), name="robots-txt"),
]

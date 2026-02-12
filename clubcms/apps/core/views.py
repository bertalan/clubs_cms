"""
Core views: robots.txt generation.
"""

from django.http import HttpResponse
from django.views import View


class RobotsTxtView(View):
    """
    Serve a ``robots.txt`` with references to the sitemap and feeds.

    In production the web server can serve a static file instead;
    this view is a convenient fallback.
    """

    def get(self, request, *args, **kwargs):
        lines = [
            "User-agent: *",
            "Allow: /",
            "",
            "# Disallow admin areas",
            "Disallow: /admin/",
            "Disallow: /django-admin/",
            "Disallow: /account/",
            "",
            "# Sitemap",
            f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
            "",
            "# Feeds",
            f"# RSS:  {request.build_absolute_uri('/feed/rss/')}",
            f"# Atom: {request.build_absolute_uri('/feed/atom/')}",
            "",
        ]
        return HttpResponse(
            "\n".join(lines),
            content_type="text/plain; charset=utf-8",
        )

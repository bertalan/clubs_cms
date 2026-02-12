"""
ClubCMS URL Configuration.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.members.views import PublicProfileView

# Non-i18n URLs (admin, API, documents - no language prefix)
urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Language switcher helper
    path("i18n/", include("django.conf.urls.i18n")),
]

# Federation API urls (if federation app is installed)
if settings.FEDERATION_ENABLED:
    urlpatterns += [
        path("api/federation/", include("apps.federation.urls_api")),
    ]

# Build i18n URL list (order matters — Wagtail catch-all must be last)
_i18n_urls = [
    # Member account pages
    path("account/", include("apps.members.urls")),
    # Public member profile
    path(
        "members/<str:username>/",
        PublicProfileView.as_view(),
        name="public_profile",
    ),
    # Events (registration, favorites, ICS)
    path("events/", include("apps.events.urls")),
    # Mutual Aid network
    path("mutual-aid/", include("apps.mutual_aid.urls")),
    # Website views (verification, uploads, moderation)
    path("", include("apps.website.urls")),
    # Notifications (unsubscribe, push, history)
    path("notifications/", include("apps.notifications.urls")),
    # Core feeds, robots.txt
    path("", include("apps.core.urls")),
    # Sitemap
    path("sitemap.xml", sitemap),
]

# django-allauth routes (login, signup, logout, password reset)
# Must be before Wagtail catch-all so allauth URLs resolve correctly
try:
    import allauth  # noqa: F401

    _i18n_urls.append(path("account/", include("allauth.urls")))
except ImportError:
    pass

# Wagtail pages (must be last — catch-all)
_i18n_urls.append(path("", include(wagtail_urls)))

# i18n URLs (all public-facing - prefixed with /it/, /en/, etc.)
urlpatterns += i18n_patterns(*_i18n_urls, prefix_default_language=True)

# Federation frontend (inside i18n)
if settings.FEDERATION_ENABLED:
    urlpatterns += i18n_patterns(
        path("eventi/partner/", include("apps.federation.urls_frontend")),
        prefix_default_language=True,
    )

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Debug toolbar
    try:
        import debug_toolbar  # noqa: F401

        urlpatterns = [
            path("__debug__/", include("debug_toolbar.urls")),
        ] + urlpatterns
    except ImportError:
        pass

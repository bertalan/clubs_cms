"""
ClubCMS URL Configuration.

URL path segments are translatable via gettext_lazy so that each language
gets its own natural paths, e.g. /it/eventi/partner/ vs /en/events/partner/.
"""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.translation import gettext_lazy as _

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.core.views import HealthCheckView, PWAManifestView, PWAOfflineView, PWAServiceWorkerView, RobotsTxtView
from apps.members.views import PublicProfileView

# Non-i18n URLs (admin, API, documents - no language prefix)
urlpatterns = [
    path("health/", HealthCheckView.as_view(), name="health-check"),
    # PWA
    path("manifest.json", PWAManifestView.as_view(), name="pwa-manifest"),
    path("sw.js", PWAServiceWorkerView.as_view(), name="pwa-sw"),
    path("offline/", PWAOfflineView.as_view(), name="pwa-offline"),
    # SEO: robots.txt and sitemap.xml must be at the root
    path("robots.txt", RobotsTxtView.as_view(), name="robots-txt"),
    path("sitemap.xml", sitemap, name="sitemap-xml"),
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
# Path segments wrapped in _() are translated per-language via .po files.
_i18n_urls = [
    # Member account pages (profile/, card/, privacy/, aid/, membership-request/, …)
    # NOTE: allauth also mounts at /account/ (line below) for login/, signup/,
    # logout/, password/.  The two sets do NOT overlap — members app is matched
    # first, then allauth picks up auth-related paths.
    path(_("account/"), include("apps.members.urls")),
    # Public member profile
    path(
        _("members/<str:username>/"),
        PublicProfileView.as_view(),
        name="public_profile",
    ),
    # Events (registration, favorites, ICS)
    path(_("events/"), include("apps.events.urls")),
    # Website views (verification, uploads, moderation)
    path("", include("apps.website.urls")),
    # Notifications (unsubscribe, push, history)
    path(_("notifications/"), include("apps.notifications.urls")),
    # Core feeds, robots.txt
    path("", include("apps.core.urls")),
    # Sitemap (also available at root /sitemap.xml above)
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

"""
Core views: robots.txt generation, PWA support, health check.

Search is handled by SearchPage, contributions by ContributionsPage.
"""

import json

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import TemplateView


# ───────────────────────────────────────────────────────────────────────────
# Health Check
# ───────────────────────────────────────────────────────────────────────────


class HealthCheckView(View):
    """Lightweight health endpoint for load balancers and monitoring."""

    def get(self, request, *args, **kwargs):
        db_ok = "ok"
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = "error"
        return JsonResponse({"status": "ok", "database": db_ok})


# ───────────────────────────────────────────────────────────────────────────
# PWA Manifest & Service Worker
# ───────────────────────────────────────────────────────────────────────────


class PWAManifestView(View):
    """Generate Web App Manifest JSON from SiteSettings."""

    def get(self, request, *args, **kwargs):
        from wagtail.models import Site

        site = Site.find_for_request(request)
        site_settings = None
        try:
            from apps.website.models.settings import SiteSettings
            site_settings = SiteSettings.for_site(site)
        except Exception:
            pass

        resolved_pwa_name = getattr(site_settings, "resolved_pwa_name", "") or getattr(
            site_settings, "site_name", ""
        ) or getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
        resolved_pwa_short_name = getattr(site_settings, "resolved_pwa_short_name", "") or resolved_pwa_name

        manifest = {
            "name": resolved_pwa_name,
            "short_name": resolved_pwa_short_name,
            "description": getattr(site_settings, "pwa_description", "") or "",
            "id": "/",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "orientation": "portrait-primary",
            "lang": request.LANGUAGE_CODE if hasattr(request, "LANGUAGE_CODE") else "en",
            "categories": ["social"],
            "background_color": getattr(site_settings, "pwa_background_color", "#ffffff"),
            "theme_color": getattr(site_settings, "pwa_theme_color", "#0F172A"),
            "prefer_related_applications": False,
            "icons": [
                {
                    "src": static("pwa/icon-192.png"),
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any",
                },
                {
                    "src": static("pwa/icon-512.png"),
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
        }

        return JsonResponse(manifest)


class PWAServiceWorkerView(View):
    """Serve the PWA service worker JavaScript."""

    def get(self, request, *args, **kwargs):
        from wagtail.models import Site

        notification_title = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
        try:
            from apps.website.models.settings import SiteSettings

            site = Site.find_for_request(request)
            site_settings = SiteSettings.for_site(site)
            notification_title = getattr(site_settings, "resolved_pwa_name", "") or notification_title
        except Exception:
            pass

        sw_js = """
// ClubCMS Service Worker
const CACHE_NAME = 'clubcms-v1';
const OFFLINE_URL = '/offline/';
const STATIC_ASSETS = [];

// Install: cache offline page
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll([OFFLINE_URL]);
        })
    );
    self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            )
        )
    );
    self.clients.claim();
});

// Fetch: network-first for HTML, cache-first for static assets
self.addEventListener('fetch', event => {
    const request = event.request;

    // Skip non-GET requests
    if (request.method !== 'GET') return;

    // Static assets: cache-first
    if (request.url.match(/\\.(css|js|woff2?|ttf|eot|png|jpg|jpeg|gif|svg|webp|ico)$/)) {
        event.respondWith(
            caches.match(request).then(cached => {
                if (cached) return cached;
                return fetch(request).then(response => {
                    if (response.ok) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
                    }
                    return response;
                }).catch(() => caches.match(request));
            })
        );
        return;
    }

    // HTML pages: network-first
    if (request.headers.get('Accept') && request.headers.get('Accept').includes('text/html')) {
        event.respondWith(
            fetch(request).catch(() => caches.match(OFFLINE_URL))
        );
        return;
    }
});

// Push: show notification from server payload
self.addEventListener('push', event => {
    let data = { title: __PWA_NOTIFICATION_TITLE__, body: '', url: '/', type: '' };
    if (event.data) {
        try { data = Object.assign(data, event.data.json()); } catch (e) {}
    }
    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/static/pwa/icon-192.png',
            badge: '/static/pwa/badge-72.png',
            data: { url: data.url || '/' },
            vibrate: [100, 50, 100],
            tag: data.type || 'general',
            renotify: true
        })
    );
});

// Notification click: open target URL
self.addEventListener('notificationclick', event => {
    event.notification.close();
    const url = (event.notification.data && event.notification.data.url) || '/';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then(windowClients => {
            for (const client of windowClients) {
                if (client.url === url && 'focus' in client) return client.focus();
            }
            return clients.openWindow(url);
        })
    );
});
""".replace("__PWA_NOTIFICATION_TITLE__", json.dumps(notification_title))
        return HttpResponse(
            sw_js.strip(),
            content_type="application/javascript",
        )


class PWAOfflineView(TemplateView):
    """Offline fallback page."""

    template_name = "pwa/offline.html"


# ───────────────────────────────────────────────────────────────────────────
# RobotsTxtView
# ───────────────────────────────────────────────────────────────────────────


# AI bot user-agents to block when allow_ai_bots is False
_AI_BOT_AGENTS = [
    "GPTBot",
    "ChatGPT-User",
    "Google-Extended",
    "CCBot",
    "anthropic-ai",
    "Claude-Web",
    "Meta-ExternalAgent",
    "FacebookBot",
    "Bytespider",
    "PerplexityBot",
    "Amazonbot",
    "YouBot",
]


class RobotsTxtView(View):
    """
    Serve a ``robots.txt`` built from base rules + SiteSettings overrides.

    Reads ``seo_indexing``, ``allow_ai_bots``, and ``robots_txt_extra``
    from SiteSettings to produce a dynamic output.
    """

    def get(self, request, *args, **kwargs):
        from wagtail.models import Site

        site_settings = None
        try:
            from apps.website.models.settings import SiteSettings
            site_settings = SiteSettings.for_site(Site.find_for_request(request))
        except Exception:
            pass

        seo_indexing = getattr(site_settings, "seo_indexing", True)
        allow_ai = getattr(site_settings, "allow_ai_bots", False)
        extra = (getattr(site_settings, "robots_txt_extra", "") or "").strip()

        lines = []

        if not seo_indexing:
            # Block everything when indexing is disabled
            lines += [
                "# Indexing disabled via Site Settings",
                "User-agent: *",
                "Disallow: /",
                "",
            ]
        else:
            lines += [
                "User-agent: *",
                "Allow: /",
                "",
                "# Disallow admin areas",
                "Disallow: /admin/",
                "Disallow: /django-admin/",
                "Disallow: /account/",
                "",
            ]

        # AI bot blocking
        if not allow_ai:
            lines.append("# AI bot crawlers — blocked")
            for agent in _AI_BOT_AGENTS:
                lines += [
                    f"User-agent: {agent}",
                    "Disallow: /",
                    "",
                ]

        # Custom rules from admin
        if extra:
            lines += [
                "# Custom rules",
                extra,
                "",
            ]

        # Sitemap & feeds
        lines += [
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


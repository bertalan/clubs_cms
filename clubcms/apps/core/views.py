"""
Core views: robots.txt generation, site-wide search, contributions.
"""

import json
import math

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView

from wagtail.models import Page


# ───────────────────────────────────────────────────────────────────────────
# Haversine distance utility
# ───────────────────────────────────────────────────────────────────────────

_EARTH_RADIUS_KM = 6371.0


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Return approximate distance in km between two lat/lon points.

    Uses the Haversine formula — accurate enough for event proximity
    searches up to a few hundred km.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return _EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a))


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

        manifest = {
            "name": getattr(site_settings, "pwa_name", "") or "Club CMS",
            "short_name": getattr(site_settings, "pwa_short_name", "") or "Club",
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
    let data = { title: 'Club CMS', body: '', url: '/', type: '' };
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
"""
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


# ───────────────────────────────────────────────────────────────────────────
# Site-wide Search View
# ───────────────────────────────────────────────────────────────────────────

# Radius options shown in the UI (km)
RADIUS_CHOICES = [10, 25, 50, 100, 200]
DEFAULT_RADIUS_KM = 50
PER_PAGE_CHOICES = [25, 50, 100]
DEFAULT_PER_PAGE = 25


class SearchView(TemplateView):
    """
    Full-text search across all Wagtail pages, with optional geo-radius
    filtering for events.

    Query params
    ------------
    q        : free-text query (optional, may be empty for geo-only search)
    lat, lng : user coordinates for proximity filter
    radius   : max distance in km (default 50)
    type     : 'all' | 'events' | 'news' | 'pages' (default 'all')
    per_page : results per page (25, 50, 100)
    page     : pagination
    """

    template_name = "search/search_results.html"

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _get_params(self, request):
        """Extract and validate query parameters."""
        query = request.GET.get("q", "").strip()
        lat = self._safe_float(request.GET.get("lat"))
        lng = self._safe_float(request.GET.get("lng"))
        radius = self._safe_float(request.GET.get("radius")) or DEFAULT_RADIUS_KM
        result_type = request.GET.get("type", "all")
        if result_type not in ("all", "events", "news", "pages"):
            result_type = "all"
        # Per page
        per_page = self._safe_int(request.GET.get("per_page")) or DEFAULT_PER_PAGE
        if per_page not in PER_PAGE_CHOICES:
            per_page = DEFAULT_PER_PAGE
        return query, lat, lng, radius, result_type, per_page

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # ── full-text search ──────────────────────────────────────────────

    # Minimum query length for Wagtail full-text search; shorter queries
    # use icontains fallback for better results
    MIN_FULLTEXT_LENGTH = 4

    @staticmethod
    def _search_pages(query, result_type):
        """
        Search published Wagtail pages using the configured search backend.

        For short queries (< 4 characters), uses title/intro icontains
        filter for better results with the default database backend.

        Returns (events_qs, pages_qs) where pages_qs excludes events
        when they are returned separately.
        """
        from django.db.models import Q

        from apps.website.models.pages import EventDetailPage

        events = []
        pages = []
        use_fulltext = len(query) >= SearchView.MIN_FULLTEXT_LENGTH if query else False

        if result_type in ("all", "events"):
            qs = EventDetailPage.objects.live()
            if query:
                if use_fulltext:
                    qs = qs.search(query)
                else:
                    # Short query: use icontains on searchable fields
                    qs = qs.filter(
                        Q(title__icontains=query)
                        | Q(intro__icontains=query)
                        | Q(location_name__icontains=query)
                    )
            events = list(qs)

        if result_type in ("all", "pages", "news"):
            qs = Page.objects.live().not_type(EventDetailPage)
            if query:
                if use_fulltext:
                    qs = qs.search(query)
                else:
                    # Short query: use icontains on title
                    qs = qs.filter(title__icontains=query)
            pages = list(qs)

        return events, pages

    @staticmethod
    def _search_external_events(query):
        """Search federated external events (if federation is enabled)."""
        if not getattr(settings, "FEDERATION_ENABLED", False):
            return []
        try:
            from apps.federation.models import ExternalEvent

            qs = ExternalEvent.objects.filter(is_approved=True, is_hidden=False)
            if query:
                from django.db.models import Q

                qs = qs.filter(
                    Q(event_name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(location_name__icontains=query)
                    | Q(location_address__icontains=query)
                )
            return list(qs)
        except Exception:
            return []

    # ── geo filtering ─────────────────────────────────────────────────

    @staticmethod
    def _apply_geo_filter(events, lat, lng, radius_km):
        """
        Filter a list of events/external events by distance.

        Annotates each event with a ``distance_km`` attribute.
        """
        if lat is None or lng is None:
            return events

        filtered = []
        for ev in events:
            ev_lat = getattr(ev, "latitude", None) or getattr(ev, "location_lat", None)
            ev_lng = getattr(ev, "longitude", None) or getattr(ev, "location_lon", None)
            if ev_lat is None or ev_lng is None:
                continue
            try:
                dist = haversine_km(lat, lng, float(ev_lat), float(ev_lng))
            except (TypeError, ValueError):
                continue
            if dist <= radius_km:
                ev.distance_km = round(dist, 1)
                filtered.append(ev)

        filtered.sort(key=lambda e: e.distance_km)
        return filtered

    # ── main context ──────────────────────────────────────────────────

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        query, lat, lng, radius, result_type, per_page = self._get_params(request)

        # Full-text search
        events, pages = self._search_pages(query, result_type)
        external_events = (
            self._search_external_events(query)
            if result_type in ("all", "events")
            else []
        )

        # Geo filtering (events only)
        geo_active = lat is not None and lng is not None
        if geo_active:
            events = self._apply_geo_filter(events, lat, lng, radius)
            external_events = self._apply_geo_filter(external_events, lat, lng, radius)

        # Combined event results
        all_events = list(events) + list(external_events)
        if geo_active:
            all_events.sort(key=lambda e: getattr(e, "distance_km", 9999))

        # Pagination
        paginator = Paginator(all_events + list(pages), per_page)
        page_number = request.GET.get("page")
        try:
            page_obj = paginator.page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        # Template context
        context.update(
            {
                "search_query": query,
                "results": page_obj,
                "page_obj": page_obj,
                "paginator": paginator,
                "result_count": paginator.count,
                "events_count": len(all_events),
                "pages_count": len(pages),
                # Geo
                "geo_active": geo_active,
                "user_lat": lat,
                "user_lng": lng,
                "radius": radius,
                "radius_choices": RADIUS_CHOICES,
                # Filters
                "result_type": result_type,
                # Per page
                "per_page": per_page,
                "per_page_choices": PER_PAGE_CHOICES,
            }
        )
        return context


# ───────────────────────────────────────────────────────────────────────────
# Member Contributions
# ───────────────────────────────────────────────────────────────────────────


class SubmitContributionView(LoginRequiredMixin, CreateView):
    """Submit a new story, proposal, or announcement."""

    template_name = "account/submit_contribution.html"
    success_url = reverse_lazy("account:my_contributions")

    def get_form_class(self):
        from apps.core.forms import ContributionForm
        return ContributionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(
            self.request,
            _("Your contribution has been submitted and is awaiting moderation."),
        )
        return super().form_valid(form)


class MyContributionsView(LoginRequiredMixin, ListView):
    """List the logged-in user's contributions."""

    template_name = "account/my_contributions.html"
    context_object_name = "contributions"
    paginate_by = 20

    def get_queryset(self):
        from apps.core.models import Contribution
        return Contribution.objects.filter(user=self.request.user)

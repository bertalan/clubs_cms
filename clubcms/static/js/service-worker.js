/**
 * Service Worker for ClubCMS PWA.
 *
 * Strategies:
 *  - Cache-first for static assets (CSS, JS, fonts, images)
 *  - Network-first for HTML pages
 *  - Offline fallback page
 *  - Push notification event handler
 *  - Notification click handler (opens URL)
 */

const CACHE_NAME = "clubcms-v1";
const OFFLINE_URL = "/offline/";

// Static assets to pre-cache on install
const PRECACHE_ASSETS = [
  OFFLINE_URL,
];

// ---------------------------------------------------------------------------
// Install: pre-cache essential assets
// ---------------------------------------------------------------------------
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  self.skipWaiting();
});

// ---------------------------------------------------------------------------
// Activate: clean up old caches
// ---------------------------------------------------------------------------
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// ---------------------------------------------------------------------------
// Fetch: routing strategies
// ---------------------------------------------------------------------------

/**
 * Determine if a request is for a static asset.
 */
function isStaticAsset(url) {
  const path = new URL(url).pathname;
  return (
    path.startsWith("/static/") ||
    path.match(/\.(css|js|woff2?|ttf|eot|svg|png|jpg|jpeg|gif|ico|webp)$/)
  );
}

/**
 * Determine if a request is for an HTML page (navigation).
 */
function isNavigationRequest(request) {
  return (
    request.mode === "navigate" ||
    (request.method === "GET" &&
      request.headers.get("accept") &&
      request.headers.get("accept").includes("text/html"))
  );
}

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Only handle GET requests
  if (request.method !== "GET") return;

  if (isStaticAsset(request.url)) {
    // Cache-first for static assets
    event.respondWith(
      caches.match(request).then((cached) => {
        if (cached) return cached;
        return fetch(request)
          .then((response) => {
            if (response && response.status === 200) {
              const clone = response.clone();
              caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
            }
            return response;
          })
          .catch(() => caches.match(OFFLINE_URL));
      })
    );
  } else if (isNavigationRequest(request)) {
    // Network-first for HTML pages
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, clone));
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then((cached) => {
            return cached || caches.match(OFFLINE_URL);
          });
        })
    );
  }
});

// ---------------------------------------------------------------------------
// Push notification handler
// ---------------------------------------------------------------------------
self.addEventListener("push", (event) => {
  let data = { title: "New notification", body: "", url: "/" };

  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body || "",
    icon: "/static/img/icon-192.png",
    badge: "/static/img/badge-72.png",
    data: {
      url: data.url || "/",
      type: data.type || "",
    },
    vibrate: [100, 50, 100],
    requireInteraction: false,
    tag: data.type || "default",
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

// ---------------------------------------------------------------------------
// Notification click handler — open the URL
// ---------------------------------------------------------------------------
self.addEventListener("notificationclick", (event) => {
  event.notification.close();

  const url = event.notification.data && event.notification.data.url
    ? event.notification.data.url
    : "/";

  event.waitUntil(
    clients
      .matchAll({ type: "window", includeUncontrolled: true })
      .then((clientList) => {
        // Focus existing tab if the URL is already open
        for (const client of clientList) {
          if (client.url === url && "focus" in client) {
            return client.focus();
          }
        }
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

// Service Worker for Toronto Kids Events PWA
const CACHE_NAME = 'kidsevents-2026-11-09'; // v21: de-mill static About + Data Sources modals + keywords meta 2026-06-18. v20: de-mill homepage editorial (stat cards/FAQ/About/meta now venue-circuit, not EarlyON/TPL/Parks) 2026-06-18. v19: removed earlyon/parks guide pages (links/cards/sitemap/llms/redirects) 2026-06-18. v18: calendar day-expand collapses EarlyON/ParksRec mill into one summary line (distinctive-first) 2026-06-18. v17: trim inline ItemList schema 200->50 (~133KB off HTML, mobile perf) 2026-06-18. v14: top-5 distinctive picks/day (freq-demote routine), no Join (whole chip tap->editorial match), warmer header (2026-06-14)
const urlsToCache = [
  '/kidsevents/',
  '/kidsevents/index.html',
  '/kidsevents/load_events.js'
  // NOTE: JSON files are NOT cached - they use network-first strategy for fresh data
];

// Install event - cache core files
self.addEventListener('install', event => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Caching files');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - network-first for JSON, cache-first for static assets
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  const url = new URL(event.request.url);
  const isJSONFile = url.pathname.endsWith('.json');

  // NETWORK-FIRST strategy for JSON files (always fetch fresh data)
  if (isJSONFile) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          console.log('Service Worker: Fetched fresh JSON from network:', url.pathname);
          // Don't cache JSON files - they change frequently
          return response;
        })
        .catch(error => {
          console.log('Service Worker: Network failed for JSON, checking cache:', error);
          // Fall back to cache only if network fails (offline mode)
          return caches.match(event.request)
            .then(cachedResponse => {
              if (cachedResponse) {
                console.log('Service Worker: Serving stale JSON from cache (offline)');
                return cachedResponse;
              }
              return new Response('{"error": "Offline and no cached data available"}', {
                headers: { 'Content-Type': 'application/json' }
              });
            });
        })
    );
    return;
  }

  // NETWORK-FIRST for pages, so a normal load always gets the current HTML (cache is the offline fallback)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200 && response.type === 'basic') {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
          }
          return response;
        })
        .catch(() => caches.match(event.request).then(r => r || caches.match('/kidsevents/')))
    );
    return;
  }

  // CACHE-FIRST strategy for static assets (HTML, JS, CSS)
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          console.log('Service Worker: Serving from cache:', event.request.url);
          return response;
        }

        // Clone the request
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Cache the fetched response for future use
          const responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              // Only cache GET requests for static assets
              if (event.request.method === 'GET') {
                cache.put(event.request, responseToCache);
              }
            });

          return response;
        }).catch(error => {
          console.log('Service Worker: Fetch failed:', error);
          return new Response('You are offline. Please check your internet connection.', {
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});

// Background sync removed - JSON files are always fetched fresh from network

// Push notification support (optional)
self.addEventListener('push', event => {
  console.log('Service Worker: Push notification received');
  const options = {
    body: event.data ? event.data.text() : 'New events available!',
    icon: '/kidsevents/icons/icon-192x192.png',
    badge: '/kidsevents/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('Toronto Kids Events', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification clicked');
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/kidsevents/')
  );
});

// Service Worker for Toronto Kids Events PWA
const CACHE_NAME = 'kidsevents-v1';
const urlsToCache = [
  '/kidsevents/',
  '/kidsevents/index.html',
  '/kidsevents/load_events.js',
  '/kidsevents/scrapers/events.json'
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

// Fetch event - serve from cache, fall back to network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
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
              // Only cache GET requests
              if (event.request.method === 'GET') {
                cache.put(event.request, responseToCache);
              }
            });

          return response;
        }).catch(error => {
          console.log('Service Worker: Fetch failed, serving offline page', error);
          // You could return a custom offline page here
          return new Response('You are offline. Please check your internet connection.', {
            headers: { 'Content-Type': 'text/plain' }
          });
        });
      })
  );
});

// Background sync for updating events
self.addEventListener('sync', event => {
  console.log('Service Worker: Background sync');
  if (event.tag === 'sync-events') {
    event.waitUntil(
      fetch('/kidsevents/scrapers/events.json')
        .then(response => response.json())
        .then(data => {
          return caches.open(CACHE_NAME).then(cache => {
            return cache.put('/kidsevents/scrapers/events.json',
              new Response(JSON.stringify(data))
            );
          });
        })
        .catch(error => console.log('Sync failed:', error))
    );
  }
});

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

// public/js/service-worker.js

const CACHE_NAME = 'luminasync-cache-v1';
const urlsToCache = [
    './',
    './public/css/main.css',
    './public/js/main.js',
    './public/logo192.png',
    './public/logo512.png',
    './public/favicon.ico',
    './manifest.webmanifest',
    './service-worker.js',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);

    // Handle HTML files with a Network-First strategy
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then(async response => {
                    const cache = await caches.open(CACHE_NAME);
                    cache.put(event.request, response.clone());
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Handle other assets with a Cache-First strategy
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                return response || fetch(event.request);
            })
    );
});


self.addEventListener('activate', event => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (!cacheWhitelist.includes(cacheName)) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// service-worker.js

// The cache name is versioned to ensure that updates to the PWA
// trigger a new service worker installation and cache refresh.
const CACHE_NAME = 'noodle-nudge-cache-v1.2.9';

// App Shell: Core files needed for the app to run offline immediately.
// This list is now corrected to match the final manifest.json.
const APP_SHELL_URLS = [
    './',
    './index.html',
    './manifest.json',
    './favicon.ico',
    './icons/icon-192x192.png',
    './icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.2/dist/chart.umd.js',
    'https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Source+Sans+Pro:wght@400;600;700&display=swap'
];

// Dynamic Content: JSON files to be pre-cached for offline access.
const CONTENT_URLS = [
    './JSON/Q1_Core%20Personality.json',
    './JSON/Q2_Core%20Values.json',
    './JSON/Q3_Core%20Agency.json',
    './JSON/Q4_Work%20Motivation.json',
    './JSON/Q5_Perceived%20Stress%20Scale%20(PSS).json',
    './JSON/Q6_Conflict%20%26%20Negotiation%20Style.json',
    './JSON/Q7_Authentic%20%26%20Ethical%20Leadership.json',
    './JSON/Q8_Assertiveness%20Profile.json',
    './JSON/Q9_Power%20%26%20Influence%20Profile.json',
    './JSON/Q10_Proactive%20Personality%20Scale.json',
    './JSON/Content_CognitiveBiases.json',
    './JSON/Content_Meditations.json',
    './JSON/Content_Quotes.json',
    './JSON/Content_Reflections.json'
];

const ALL_URLS_TO_CACHE = [...APP_SHELL_URLS, ...CONTENT_URLS];

// Install Event: Caches all essential app shell and content files.
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log(`[Service Worker] Caching all files for ${CACHE_NAME}`);
                return cache.addAll(ALL_URLS_TO_CACHE);
            })
            .catch(error => {
                console.error('[Service Worker] Failed to cache files during install:', error);
            })
    );
});

// Activate Event: Cleans up old caches to remove outdated files.
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.filter(name => name !== CACHE_NAME)
                         .map(name => {
                            console.log(`[Service Worker] Deleting old cache: ${name}`);
                            return caches.delete(name);
                         })
            );
        })
    );
});

// Fetch Event: Implements a Cache-First strategy.
// This is ideal for an offline-first PWA. It serves assets from the cache
// immediately if available, falling back to the network only if necessary.
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // If the request is in the cache, return the cached version.
                if (response) {
                    return response;
                }
                // If not in cache, fetch from the network.
                return fetch(event.request);
            })
    );
});
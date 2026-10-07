/* Jura Game Service Worker — offline-first untuk aset & halaman same-origin.
   Konten pihak ketiga (embed game GamePix/GameMonetize, iklan, analytics)
   TIDAK di-cache agar selalu segar dan tidak melanggar kebijakan mereka. */
const CACHE_VERSION = 'jura-v4';
const CORE_ASSETS = [
  '/',
  '/css/tailwind.css',
  '/games-home.json',
  '/games.json',
  '/articles-index.json',
  '/manifest.webmanifest',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/icons/icon-512-maskable.png',
  '/apple-touch-icon.png',
  '/favicon.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
      .catch(() => {})
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

function isCacheable(request) {
  if (request.method !== 'GET') return false;
  const url = new URL(request.url);
  // Hanya same-origin. CDN/script/iklan/embed game pihak ketiga dilewati.
  if (url.origin !== self.location.origin) return false;
  return true;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (!isCacheable(request)) return; // biarkan browser handle normal

  const url = new URL(request.url);
  const isPage = request.mode === 'navigate' ||
    (request.headers.get('accept') || '').includes('text/html');
  // Katalog artikel & game berubah tiap ada postingan/jadwal: network-first seperti halaman
  const isArticleFeed = url.pathname.endsWith('/articles.json') ||
    url.pathname.endsWith('/articles-index.json') ||
    url.pathname.endsWith('/games.json');

  if (isPage || isArticleFeed) {
    // Halaman & feed artikel: network-first agar konten selalu terbaru, fallback ke cache saat offline
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(request).then((hit) => hit || (isPage ? caches.match('/') : undefined)))
    );
    return;
  }

  // Aset statis (ikon, manifest, gambar lokal): cache-first, fallback network
  event.respondWith(
    caches.match(request).then((hit) => {
      if (hit) return hit;
      return fetch(request).then((res) => {
        if (res && res.ok) {
          const copy = res.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy)).catch(() => {});
        }
        return res;
      });
    })
  );
});

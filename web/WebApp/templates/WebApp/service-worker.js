const STATIC_CACHE = "artesano-static-{{ static_version }}";
const RUNTIME_CACHE = "artesano-runtime-{{ static_version }}";
const OFFLINE_URL = "{{ offline_url }}";

const APP_SHELL = [
  "{{ home_url }}",
  "{{ catalogo_url }}",
  "{{ contacto_url }}",
  "{{ carro_url }}",
  OFFLINE_URL,
  "/static/WebApp/css/gestion.css",
  "/static/WebApp/js/store.js",
  "/static/WebApp/img/pwa/icon-192.svg",
  "/static/WebApp/img/pwa/icon-512.svg",
  "/static/WebApp/vendor/bootstrap/css/bootstrap.min.css",
  "/static/WebApp/vendor/bootstrap/js/bootstrap.bundle.min.js",
  "/static/WebApp/vendor/jquery/jquery.min.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => ![STATIC_CACHE, RUNTIME_CACHE].includes(key))
          .map((key) => caches.delete(key)),
      ),
    ).then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);

  if (request.mode === "navigate") {
    event.respondWith(networkFirst(request, OFFLINE_URL));
    return;
  }

  if (url.pathname.startsWith("/static/")) {
    event.respondWith(cacheFirst(request));
    return;
  }

  if (url.pathname.startsWith("/media/")) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  if (url.pathname.startsWith("/catalogo/") || url.pathname.startsWith("/carro/")) {
    event.respondWith(networkFirst(request, OFFLINE_URL));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});

async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  const response = await fetch(request);
  const cache = await caches.open(RUNTIME_CACHE);
  cache.put(request, response.clone());
  return response;
}

async function networkFirst(request, fallbackUrl) {
  try {
    const response = await fetch(request);
    const cache = await caches.open(RUNTIME_CACHE);
    cache.put(request, response.clone());
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    return caches.match(fallbackUrl);
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(request);

  const networkPromise = fetch(request)
    .then((response) => {
      cache.put(request, response.clone());
      return response;
    })
    .catch(() => cached);

  return cached || networkPromise;
}

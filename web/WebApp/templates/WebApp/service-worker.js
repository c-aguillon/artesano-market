const CACHE_NAME = "artesano-market-v1";
const APP_SHELL = [
  "{{ home_url }}",
  "{{ catalogo_url }}",
  "{{ carro_url }}",
  "{{ css_url }}",
  "{{ bootstrap_css_url }}",
  "{{ bootstrap_js_url }}",
  "{{ jquery_url }}",
  "{{ cart_js_url }}",
  "{{ pwa_js_url }}"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const requestUrl = new URL(event.request.url);
  if (event.request.method !== "GET") return;

  if (
    requestUrl.origin !== self.location.origin ||
    requestUrl.pathname.startsWith("/pagar/") ||
    requestUrl.pathname.startsWith("/api/paypal/") ||
    requestUrl.pathname.startsWith("/cuentas/") ||
    requestUrl.pathname.startsWith("/carro/agregar/") ||
    requestUrl.pathname.startsWith("/carro/restar/") ||
    requestUrl.pathname.startsWith("/carro/eliminar/") ||
    requestUrl.pathname.startsWith("/carro/limpiar/") ||
    requestUrl.pathname.startsWith("/carro/sincronizar/")
  ) {
    return;
  }

  const isStaticAsset = requestUrl.pathname.startsWith("/static/") || requestUrl.pathname.startsWith("/media/");

  if (isStaticAsset) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        if (cachedResponse) return cachedResponse;
        return fetch(event.request).then((networkResponse) => {
          const copy = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return networkResponse;
        });
      })
    );
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        const copy = networkResponse.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
        return networkResponse;
      })
      .catch(() => caches.match(event.request).then((cachedResponse) => cachedResponse || caches.match("{{ home_url }}")))
  );
});

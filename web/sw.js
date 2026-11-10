// Cache the interface only. API calls and external sources always go to the network.
const SHELL = "halio-shell-v13";
const FILES = [
  "./", "index.html", "cek.html", "radar.html", "coverage.html", "landing.css", "landing.js", "style.css", "app.css", "app.js", "static-demo.js", "dashboard-demo.js", "radar.css", "radar.js", "coverage.js", "uji.html", "uji.js", "laporan.html", "laporan.js", "laporan.css",
  "icons/icon.svg", "manifest.webmanifest", "brand.css", "fonts/fonts.css",
  "fonts/Inter-normal-latin.woff2", "fonts/Archivo-normal-latin.woff2",
  "fonts/InstrumentSerif-normal-latin.woff2", "fonts/InstrumentSerif-italic-latin.woff2",
];

self.addEventListener("install", (event) => event.waitUntil(caches.open(SHELL).then((cache) => cache.addAll(FILES))));
self.addEventListener("activate", (event) =>
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== SHELL).map((key) => caches.delete(key))))));
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.includes("/api/")) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request, { ignoreSearch: true })));
});

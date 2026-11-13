// simpen tampilan antarmuka aja di cache; panggilan /api/ sm sumber luar wajib lewat jaringan langsung
const SHELL = "halio-shell-v15";
const FILES = [
  "./", "index.html", "cek.html", "radar.html", "coverage.html", "landing.css", "landing.js", "style.css", "app.css", "app.js", "static-demo.js", "engine/data.js", "engine/halio-local.js", "dashboard-demo.js", "radar.css", "radar.js", "coverage.js", "uji.html", "uji.js", "laporan.html", "laporan.js", "laporan.css",
  "icons/icon.svg", "manifest.webmanifest", "brand.css", "fonts/fonts.css",
  "fonts/Inter-normal-latin.woff2", "fonts/Archivo-normal-latin.woff2",
  "fonts/InstrumentSerif-normal-latin.woff2", "fonts/InstrumentSerif-italic-latin.woff2",
];

self.addEventListener("install", (event) => event.waitUntil(caches.open(SHELL).then((cache) => cache.addAll(FILES))));
// sapu bersih cache versi lama pas service worker baru aktif
self.addEventListener("activate", (event) =>
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== SHELL).map((key) => caches.delete(key))))));
// utamain ambil dr jaringan dulu, kl lg offline baru jatuh ke file simpanan cache
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.includes("/api/")) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request, { ignoreSearch: true })));
});

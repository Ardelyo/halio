// Cache the interface only. API calls and external sources always go to the network.
const SHELL = "halio-shell-v2";
const FILES = [
  "./", "index.html", "cek.html", "radar.html", "coverage.html", "landing.css", "landing.js", "style.css", "app.js", "static-demo.js", "radar.js", "coverage.js",
  "icons/icon.svg", "manifest.webmanifest", "fonts/dm-sans-regular.ttf", "fonts/dm-sans-semibold.ttf",
  "fonts/dm-sans-bold.ttf", "fonts/instrument-serif.ttf", "fonts/instrument-serif-italic.ttf",
];

self.addEventListener("install", (event) => event.waitUntil(caches.open(SHELL).then((cache) => cache.addAll(FILES))));
self.addEventListener("activate", (event) =>
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== SHELL).map((key) => caches.delete(key))))));
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.origin !== location.origin || url.pathname.includes("/api/")) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request, { ignoreSearch: true })));
});

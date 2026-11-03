const DEFAULTS = { badges: true, blurMode: "judol", apiUrl: "http://localhost:8000" };
const $ = (id) => document.getElementById(id);

chrome.storage.sync.get(DEFAULTS, (s) => {
  $("badges").checked = s.badges;
  $("blurMode").value = s.blurMode;
  $("apiUrl").value = s.apiUrl;
});
chrome.storage.local.get("stats", ({ stats = {} }) => {
  $("imagesChecked").textContent = stats.imagesChecked || 0;
  $("textChecks").textContent = stats.textChecks || 0;
  $("bytesSent").textContent = (stats.bytesSent || 0).toLocaleString("id-ID");
});
chrome.runtime.sendMessage({ type: "model-status" }, (r) => {
  $("model").textContent = r && r.ok
    ? "Model NudeNet terpasang dan berjalan di perangkat."
    : "Model konten dewasa belum terpasang; mode 'pintar' akan menyembunyikan gambar sampai bisa diperiksa.";
});

$("badges").onchange = (e) => chrome.storage.sync.set({ badges: e.target.checked });
$("blurMode").onchange = (e) => chrome.storage.sync.set({ blurMode: e.target.value });
$("apiUrl").onchange = (e) => chrome.storage.sync.set({ apiUrl: e.target.value.trim() || DEFAULTS.apiUrl });

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
// Only the platforms, their image CDNs, localhost and the demo server are granted at install. Another Halio server is asked
// for here, when the user types its address (a user gesture), so the extension never holds access to every site.
$("apiUrl").onchange = (e) => {
  const apiUrl = e.target.value.trim() || DEFAULTS.apiUrl;
  let origin;
  try { origin = new URL(apiUrl).origin + "/*"; } catch { e.target.value = DEFAULTS.apiUrl; return; }
  chrome.permissions.contains({ origins: [origin] }, (has) => {
    const save = () => chrome.storage.sync.set({ apiUrl });
    if (has || !origin.startsWith("https://")) return save();
    chrome.permissions.request({ origins: [origin] }, (granted) => { if (granted) save(); });
  });
};

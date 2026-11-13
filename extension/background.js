// service worker ekstensi: ngatur lalu lintas pesan, nembak API Halio kl user minta cek teks,
// sm nyiapin dokumen offscreen buat klasifikasi gambar lokal di perangkat
const DEFAULTS = { badges: true, blurMode: "judol", apiUrl: "http://localhost:8000" };

// pas buka feed banyak pesan "classify" masuk barengan; kl ga disimpen di satu promise bareng,
// semuanya liat hasDocument() === false terus rebutan manggil createDocument sampe error
let creating = null;

async function ensureOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  creating ??= chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["WORKERS"],
    justification: "Klasifikasi gambar di perangkat (NudeNet ONNX) agar tidak ada gambar yang dikirim keluar.",
  }).finally(() => { creating = null; });
  await creating;
}

// simpen hitungan statistik lokal buat ditampilin jujur di popup transparansi
async function bump(key, by = 1) {
  const { stats = {} } = await chrome.storage.local.get("stats");
  stats[key] = (stats[key] || 0) + by;
  await chrome.storage.local.set({ stats });
}

async function checkText(text) {
  const { apiUrl } = await chrome.storage.sync.get(DEFAULTS);
  const body = JSON.stringify({ text: text.slice(0, 300), channel: "extension" });
  await bump("textChecks");
  // cuma request ini satu-satunya yg bawa teks dr halaman keluar; catet persis jumlah byte-nya
  await bump("bytesSent", new TextEncoder().encode(body).length);
  const r = await fetch(apiUrl.replace(/\/$/, "") + "/api/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
  });
  if (!r.ok) throw new Error("HTTP " + r.status);
  return r.json();
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg.target === "offscreen") return false; // udah diurus langsung sm offscreen.js
  if (msg.type === "check") {
    checkText(msg.text).then(reply, (e) => reply({ error: String(e) }));
    return true;
  }
  if (msg.type === "classify" || msg.type === "model-status") {
    ensureOffscreen()
      .then(() => chrome.runtime.sendMessage({ ...msg, target: "offscreen" }))
      .then(reply, (e) => reply({ ok: false, error: String(e) }));
    return true;
  }
  if (msg.type === "stat") {
    bump(msg.key).then(() => reply({ ok: true }));
    return true;
  }
  return false;
});

// Service worker: routes messages, calls the Halio API for user-requested text
// checks, and hosts image classification in an offscreen document.
const DEFAULTS = { badges: true, blurMode: "judol", apiUrl: "http://localhost:8000" };

// A feed fires many "classify" messages at once; without a shared promise each one sees
// hasDocument() === false and calls createDocument, and all but the first throw.
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

async function bump(key, by = 1) {
  const { stats = {} } = await chrome.storage.local.get("stats");
  stats[key] = (stats[key] || 0) + by;
  await chrome.storage.local.set({ stats });
}

async function checkText(text) {
  const { apiUrl } = await chrome.storage.sync.get(DEFAULTS);
  const body = JSON.stringify({ text: text.slice(0, 300), channel: "extension" });
  await bump("textChecks");
  // This is the extension's only request that carries page content; count exactly what it sends.
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
  if (msg.target === "offscreen") return false; // handled by offscreen.js
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

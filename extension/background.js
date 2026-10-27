// Service worker: routes messages, calls the Halio API for user-requested text
// checks, and hosts image classification in an offscreen document.
const DEFAULTS = { badges: true, blurMode: "judol", apiUrl: "http://localhost:8000" };

async function ensureOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  await chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["WORKERS"],
    justification: "Klasifikasi gambar di perangkat (NudeNet ONNX) agar tidak ada gambar yang dikirim keluar.",
  });
}

async function bump(key) {
  const { stats = {} } = await chrome.storage.local.get("stats");
  stats[key] = (stats[key] || 0) + 1;
  await chrome.storage.local.set({ stats });
}

async function checkText(text) {
  const { apiUrl } = await chrome.storage.sync.get(DEFAULTS);
  await bump("textChecks");
  const r = await fetch(apiUrl.replace(/\/$/, "") + "/api/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: text.slice(0, 300), channel: "extension" }),
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

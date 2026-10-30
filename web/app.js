// Halio web app: paste or share a message, get an honest, sourced answer.
const API = window.HALIO_API || "";

const EXAMPLES = [
  ["Bansos dari Presiden", "Bapak ibu, ada video Pak Presiden bagi-bagi bantuan tunai! Langsung chat nomor WA 0812-3456-7890 untuk daftar, bayar biaya admin 150rb dulu. SEBARKAN!!"],
  ["Masuk TNI dijamin lulus", "Ada kenalan di kodam bisa bantu anak masuk TNI AD jalur khusus, dijamin lulus asal siapkan uang 80 juta. Hubungi saya segera, kuota terbatas."],
  ["Prediksi gempa", "WASPADA!!! Menurut BMKG akan terjadi gempa besar dan tsunami tanggal 12 bulan depan. Segera siapkan tas siaga dan teruskan ke semua grup!"],
  ["Obat dari air kelapa", "Info dari dokter: air kelapa muda dicampur garam dan jeruk nipis bisa menyembuhkan covid. Sudah terbukti, bagikan ke keluarga."],
  ["Kabar belum dikenal", "Jembatan Suramadu akan ditutup total selama seminggu mulai besok karena perbaikan. Tolong sebarkan."],
  ["Salam pagi", "Selamat pagi keluarga, semoga hari ini sehat dan penuh berkah. Amin"],
];
const ICON = { terbukti_salah: "🔴", tidak_yakin: "🟠", belum_ada_pemeriksaan: "⚪" };

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const store = {
  get(k, d) { try { return localStorage.getItem(k) ?? d; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};

function deviceId() {
  let id = store.get("halio.device");
  if (!id) { id = crypto.randomUUID(); store.set("halio.device", id); }
  return "web:" + id;
}

function toast(text) {
  const t = document.createElement("div");
  t.className = "toast"; t.textContent = text; t.setAttribute("role", "status");
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

async function check(text) {
  const btn = $("#go");
  btn.disabled = true; btn.textContent = "⏳ Sedang mengecek…";
  try {
    const r = await fetch(API + "/api/check", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, channel: "web", sapaan: $("#sapaan").value, reporter: deviceId() }),
    });
    if (r.status === 429) return toast("Terlalu banyak cek dalam semenit. Tunggu sebentar, lalu coba lagi.");
    if (r.status === 422) return toast("Pesannya belum bisa dibaca. Pastikan isinya teks, minimal 3 huruf.");
    if (!r.ok) throw new Error("HTTP " + r.status);
    render(await r.json(), text);
  } catch (e) {
    // Only a network failure or a server error reaches here.
    toast("Maaf, Halio sedang tidak bisa dihubungi. Coba lagi sebentar lagi.");
    console.error(e);
  } finally {
    btn.disabled = false; btn.textContent = "🔍 Cek pesan ini";
  }
}

function render(r, original) {
  const m = r.match;
  const sources = m ? m.sumber.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.nama)}</a></li>`).join("") : "";
  const tricks = r.manipulation.techniques.map((t) =>
    `<div class="trick"><b>${esc(t.label)}</b>${esc(t.lesson)}<div class="note">Contoh di pesan: “${t.evidence.map(esc).join("”, “")}”</div></div>`).join("");
  const warnings = r.links.warnings.map((w) => `<p class="warn">🔗 ${esc(w)}</p>`).join("");

  $("#result").innerHTML = `
    <div class="verdict ${r.status}">
      <h2><span aria-hidden="true">${ICON[r.status]}</span>${esc(r.status_label)}</h2>
      <p class="say">${esc(m ? m.sederhana : r.voice_script)}</p>
      ${m ? `<p><b>Faktanya:</b> ${esc(m.fakta)}</p><p><b>Sumber:</b></p><ul class="sources">${sources}</ul>` : ""}
      ${r.llm ? `<p class="note">Kutipan sumber: “${esc(r.llm.kutipan)}”</p>` : ""}
      <p class="claim">Yang dicek: “${esc(r.claim)}”</p>
      ${warnings}
      <div class="actions">
        <button id="listen">🔊 Dengarkan</button>
        <button id="share">📤 Bagikan kartu ke keluarga</button>
        ${r.offer_human_review ? `<button id="human">🙋 Tanya pemeriksa manusia</button>` : `<button id="appeal">⚖️ Ajukan banding</button>`}
        <button id="forward">⏸️ Saya tetap mau meneruskan</button>
      </div>
    </div>
    ${tricks ? `<details open><summary>🧠 Kenali trik dalam pesan ini (${r.manipulation.techniques.length})</summary>${tricks}</details>` : ""}
    <details><summary>🖼️ Kartu Halio</summary><img class="cardimg" src="${API + r.card_url}" alt="Kartu Halio: ${esc(r.status_label)}"></details>
    <p class="note">${esc(r.disclaimer)} Metode: ${esc(r.method)}.</p>`;
  $("#result").classList.remove("hidden");
  $("#result").scrollIntoView({ behavior: "smooth" });

  $("#listen").onclick = () => speak(r);
  $("#share").onclick = () => shareCard(r);
  $("#forward").onclick = (e) => pauseBeforeShare(e.currentTarget, original);
  const human = $("#human");
  if (human) human.onclick = () => post("/api/escalate", { check_id: r.id }).then((d) => toast(d.message));
  const appeal = $("#appeal");
  if (appeal) appeal.onclick = () => {
    const reason = prompt("Apa yang menurut Anda keliru? (boleh dikosongkan)") ?? "";
    post("/api/appeal", { check_id: r.id, reason }).then(() => toast("Banding dicatat. Terima kasih sudah kritis!"));
  };
}

async function post(path, body) {
  const r = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json();
}

function speak(r) {
  const audio = new Audio(API + r.voice_url);
  audio.play().catch(() => {
    // Server TTS unavailable: use the device's own Indonesian voice.
    if (!("speechSynthesis" in window)) return toast("Perangkat ini belum mendukung suara.");
    const u = new SpeechSynthesisUtterance(r.voice_script);
    u.lang = "id-ID"; u.rate = 0.92;
    const v = speechSynthesis.getVoices().find((v) => v.lang.startsWith("id"));
    if (v) u.voice = v;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  });
}

async function shareCard(r) {
  const blob = await (await fetch(API + r.card_url)).blob();
  const file = new File([blob], "kartu-halio.png", { type: "image/png" });
  const text = r.match ? `${r.status_label}: ${r.match.sederhana} Sumber: ${r.match.sumber[0].url}` : r.voice_script;
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], text }); } catch { /* user cancelled */ }
  } else {
    const a = Object.assign(document.createElement("a"), { href: URL.createObjectURL(blob), download: "kartu-halio.png" });
    a.click();
    toast("Kartu diunduh. Kirim gambarnya ke grup keluarga.");
  }
}

// "Jeda sebelum berbagi": a 10-second pause, then the original is copied.
function pauseBeforeShare(btn, original) {
  let n = 10;
  btn.disabled = true;
  const tick = () => {
    btn.textContent = `⏸️ Tarik napas… ${n} detik. Sudah yakin sumbernya jelas?`;
    if (n-- > 0) return setTimeout(tick, 1000);
    btn.disabled = false;
    btn.textContent = "📋 Salin pesan asli";
    btn.onclick = async () => {
      try { await navigator.clipboard.writeText(original); toast("Pesan disalin. Sertakan sumbernya, ya."); }
      catch { toast("Tidak bisa menyalin otomatis di perangkat ini."); }
    };
  };
  tick();
}

function init() {
  const sapaan = $("#sapaan");
  sapaan.value = store.get("halio.sapaan", "Bapak, Ibu");
  sapaan.onchange = () => store.set("halio.sapaan", sapaan.value);

  for (const [label, text] of EXAMPLES) {
    const b = Object.assign(document.createElement("button"), { className: "chip", textContent: label });
    b.onclick = () => { $("#msg").value = text; check(text); };
    $("#examples").appendChild(b);
  }
  $("#go").onclick = () => {
    const text = $("#msg").value.trim();
    if (text.length < 3) return toast("Tempel dulu pesannya, ya.");
    check(text);
  };

  // Android share sheet -> PWA share target (manifest.webmanifest).
  const p = new URLSearchParams(location.search);
  const shared = [p.get("title"), p.get("text"), p.get("url")].filter(Boolean).join("\n");
  if (shared) { $("#msg").value = shared; check(shared); history.replaceState(null, "", location.pathname); }

  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
}

init();

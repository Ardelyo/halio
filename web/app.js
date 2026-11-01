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
const ICON = { terbukti_salah: "!", tidak_yakin: "?", belum_ada_pemeriksaan: "—" };

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
  btn.disabled = true; btn.textContent = "Sedang mengecek…";
  try {
    let result;
    if (window.HALIO_STATIC_DEMO) {
      await new Promise((resolve) => setTimeout(resolve, 500));
      result = window.HalioStaticDemo.check(text);
    } else {
      const r = await fetch(API + "/api/check", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, channel: "web", sapaan: $("#sapaan").value, reporter: deviceId() }),
      });
      if (!r.ok) throw new Error((await r.json()).detail?.[0]?.msg || r.statusText);
      result = await r.json();
    }
    render(result, text);
  } catch (e) {
    toast("Maaf, Halio sedang tidak bisa dihubungi. Coba lagi sebentar lagi.");
    console.error(e);
  } finally {
    btn.disabled = false; btn.innerHTML = 'Cek pesan ini <span aria-hidden="true">→</span>';
  }
}

function render(r, original) {
  const m = r.match;
  const sources = m ? m.sumber.map((s) => `<li><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.nama)}</a></li>`).join("") : "";
  const tricks = r.manipulation.techniques.map((t) =>
    `<div class="trick"><b>${esc(t.label)}</b>${esc(t.lesson)}<div class="note">Contoh di pesan: “${t.evidence.map(esc).join("”, “")}”</div></div>`).join("");
  const warnings = r.links.warnings.map((w) => `<p class="warn">${esc(w)}</p>`).join("");

  $("#result").innerHTML = `
    <div class="verdict ${r.status}">
      <h2><span class="verdict-mark" aria-hidden="true">${ICON[r.status]}</span>${esc(r.status_label)}</h2>
      <p class="say">${esc(m ? m.sederhana : r.voice_script)}</p>
      ${m ? `<p><b>Faktanya:</b> ${esc(m.fakta)}</p><p><b>Sumber:</b></p><ul class="sources">${sources}</ul>` : ""}
      ${r.llm ? `<p class="note">Kutipan sumber: “${esc(r.llm.kutipan)}”</p>` : ""}
      <p class="claim">Yang dicek: “${esc(r.claim)}”</p>
      ${warnings}
      <div class="actions">
        <button id="listen">Dengarkan jawaban</button>
        <button id="share">Bagikan kartu</button>
        ${r.offer_human_review ? `<button id="human">Tanya pemeriksa manusia</button>` : `<button id="appeal">Ajukan banding</button>`}
        <button id="forward">Saya tetap mau meneruskan</button>
      </div>
    </div>
    ${tricks ? `<details open><summary>Kenali trik dalam pesan ini (${r.manipulation.techniques.length})</summary>${tricks}</details>` : ""}
    ${r.card_url ? `<details><summary>Lihat Kartu Halio</summary><img class="cardimg" src="${API + r.card_url}" alt="Kartu Halio: ${esc(r.status_label)}"></details>` : ""}
    <p class="note">${esc(r.disclaimer)} Metode: ${esc(r.method)}.</p>`;
  $("#result").classList.remove("hidden");
  $("#result").scrollIntoView({ behavior: window.HALIO_STATIC_DEMO ? "auto" : "smooth", block: "start" });

  $("#listen").onclick = () => speak(r);
  $("#share").onclick = () => shareCard(r).catch(() => toast("Kartu belum bisa dibuat. Coba lagi."));
  $("#forward").onclick = (e) => pauseBeforeShare(e.currentTarget, original);
  const human = $("#human");
  if (human) human.onclick = () => post("/api/escalate", { check_id: r.id }).then((d) => toast(d.message));
  const appeal = $("#appeal");
  if (appeal) appeal.onclick = () => {
    const reason = prompt("Apa yang menurut Anda keliru? (boleh dikosongkan)") ?? "";
    post("/api/appeal", { check_id: r.id, reason }).then((d) => toast(d.message || "Banding dicatat. Terima kasih sudah kritis!"));
  };
}

async function post(path, body) {
  if (window.HALIO_STATIC_DEMO) {
    return { message: "Mode demo: tidak ada tiket atau banding yang dikirim ke server." };
  }
  const r = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  return r.json();
}

function speak(r) {
  const fallback = () => {
    if (!("speechSynthesis" in window)) return toast("Perangkat ini belum mendukung suara.");
    const u = new SpeechSynthesisUtterance(r.voice_script);
    u.lang = "id-ID"; u.rate = 0.92;
    const v = speechSynthesis.getVoices().find((v) => v.lang.startsWith("id"));
    if (v) u.voice = v;
    speechSynthesis.cancel(); speechSynthesis.speak(u);
  };
  if (!r.voice_url) return fallback();
  const audio = new Audio(API + r.voice_url);
  audio.play().catch(fallback);
}

function makeStaticCard(r) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080; canvas.height = 1350;
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#f5f4ed"; ctx.fillRect(0, 0, 1080, 1350);
  ctx.fillStyle = "#173f35"; ctx.fillRect(0, 0, 1080, 170);
  ctx.fillStyle = "#dff584"; ctx.font = "bold 64px Arial"; ctx.fillText("halio.", 80, 108);
  ctx.fillStyle = "#b84c35"; ctx.font = "bold 70px Arial";
  const status = ctx.measureText(r.status_label).width > 900 ? "Belum ada pemeriksaan" : r.status_label;
  ctx.fillText(status, 80, 300);
  ctx.fillStyle = "#173f35"; ctx.font = "46px Arial";
  const words = r.voice_script.split(" ");
  let line = "", y = 410;
  for (const word of words) {
    const test = line + word + " ";
    if (ctx.measureText(test).width > 900) { ctx.fillText(line, 80, y); y += 68; line = ""; }
    line += word + " ";
  }
  ctx.fillText(line, 80, y);
  if (r.match) {
    ctx.fillStyle = "#62716a"; ctx.font = "28px Arial";
    ctx.fillText("Sumber:", 80, 1060);
    ctx.fillStyle = "#173f35"; ctx.font = "bold 30px Arial";
    ctx.fillText(r.match.sumber[0].nama.slice(0, 58), 80, 1110);
  }
  ctx.fillStyle = "#62716a"; ctx.font = "25px Arial";
  ctx.fillText(window.HALIO_STATIC_DEMO ? "Kartu dari simulasi lokal · periksa kembali sumbernya" : "Kartu Halio · periksa kembali sumbernya", 80, 1250);
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

async function shareCard(r) {
  const blob = r.card_url ? await (await fetch(API + r.card_url)).blob() : await makeStaticCard(r);
  if (!blob) throw new Error("Kartu tidak dapat dibuat");
  const file = new File([blob], "kartu-halio.png", { type: "image/png" });
  const text = r.match ? `${r.status_label}: ${r.match.sederhana} Sumber: ${r.match.sumber[0].url}` : r.voice_script;
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], text }); } catch { /* user cancelled */ }
  } else {
    const url = URL.createObjectURL(blob);
    const a = Object.assign(document.createElement("a"), { href: url, download: "kartu-halio.png" });
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
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
  if (window.HALIO_STATIC_DEMO) $("#static-notice").classList.remove("hidden");
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

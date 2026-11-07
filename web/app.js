const API = window.HALIO_API || "";

const EXAMPLES = [
  ["Bansos dari Presiden", "Bapak ibu, ada video Pak Presiden bagi-bagi bantuan tunai! Langsung chat nomor WA 0812-3456-7890 untuk daftar, bayar biaya admin 150rb dulu. SEBARKAN!!"],
  ["Masuk TNI dijamin lulus", "Ada kenalan di kodam bisa bantu anak masuk TNI AD jalur khusus, dijamin lulus asal siapkan uang 80 juta. Hubungi saya segera, kuota terbatas."],
  ["Prediksi gempa", "WASPADA!!! Menurut BMKG akan terjadi gempa besar dan tsunami tanggal 12 bulan depan. Segera siapkan tas siaga dan teruskan ke semua grup!"],
  ["Obat dari air kelapa", "Info dari dokter: air kelapa muda dicampur garam dan jeruk nipis bisa menyembuhkan covid. Sudah terbukti, bagikan ke keluarga."],
  ["Kabar belum dikenal", "Jembatan Suramadu akan ditutup total selama seminggu mulai besok karena perbaikan. Tolong sebarkan."],
  ["Salam pagi", "Selamat pagi keluarga, semoga hari ini sehat dan penuh berkah. Amin"],
];
const ICON = { terbukti_salah: "!", sejalan_dengan_sumber: "✓", dilaporkan_media: "i", tidak_yakin: "?", belum_ada_pemeriksaan: "—" };
const LABEL_BY_REASON = { berita_media_dikenal: "Berita dari media dikenal", kumpulan_judul: "Beberapa judul sekaligus", beberapa_klaim: "Pesan berisi beberapa klaim" };
const STATUS_WORD = { terbukti_salah: "Terbukti salah", sejalan_dengan_sumber: "Sejalan dengan sumber", dilaporkan_media: "Dilaporkan media", tidak_yakin: "Halio tidak yakin", belum_ada_pemeriksaan: "Belum ada pemeriksaan" };
const PLAIN_REASONS = ["berita_media_dikenal", "kumpulan_judul"];
const REJECT_WHY = {
  mesin_pencari_atau_pengalih: "tautannya hanya mesin pencari atau pengalih", bukan_sumber_dikenal: "situsnya bukan sumber yang dikenal",
  http_404: "halaman tidak ditemukan", http_403: "situs menolak dibuka otomatis", http_410: "halaman sudah dihapus",
  sumber_tidak_dapat_diakses: "halaman tidak bisa dibuka",
};
const TIER_ORDER = { A: 0, B: 1, C: 2 };
const longDate = (iso) => {
  const m = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
  const d = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  return d ? `${Number(d[3])} ${m[Number(d[2]) - 1]} ${d[1]}` : "";
};
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character]));
const store = {
  get(key, fallback) { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* Storage may be unavailable. */ } },
};
let appealCheckId = "";
let cardPreviewUrl = "";
let currentAudio = null;

function safeUrl(value) {
  try {
    const url = new URL(value, location.href);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
  } catch { return "#"; }
}

function deviceId() {
  let id = store.get("halio.device", "");
  if (!id) {
    id = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    store.set("halio.device", id);
  }
  return `web:${id}`;
}

function toast(text, error = false) {
  const item = document.createElement("div");
  item.className = `toast${error ? " error" : ""}`;
  item.textContent = text;
  item.setAttribute("role", error ? "alert" : "status");
  $("#toast-region").replaceChildren(item);
  setTimeout(() => item.remove(), 4500);
}

function reducedMotion() {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function updateInput() {
  const length = $("#msg").value.length;
  $("#char-count").textContent = `${length.toLocaleString("id-ID")} / 4.000`;
  $("#clear-input").classList.toggle("hidden", !length);
}

async function check(text) {
  const button = $("#go");
  button.disabled = true;
  startStages(button);
  $("#result").setAttribute("aria-busy", "true");
  try {
    let result;
    if (window.HALIO_STATIC_DEMO) {
      await new Promise((resolve) => setTimeout(resolve, 350));
      result = window.HalioStaticDemo.check(text);
    } else {
      const response = await fetch(`${API}/api/check`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, channel: "web", sapaan: $("#sapaan").value, reporter: deviceId(), mode: $("#noai")?.checked ? "tanpa_ai" : "penuh" }),
      });
      const data = await response.json();
      if (!response.ok) throw Object.assign(new Error(response.statusText), { http: response.status });
      result = data;
    }
    render(result, text);
  } catch (error) {
    console.error(error);
    toast(
      error.http === 429 ? "Terlalu banyak cek dalam semenit. Tunggu sebentar, lalu coba lagi."
        : error.http === 422 ? "Pesannya belum bisa dibaca. Pastikan isinya teks, minimal 3 huruf."
        : "Halio belum bisa memeriksa pesan. Periksa koneksi, lalu coba lagi.",
      true,
    );
  } finally {
    stopStages();
    button.disabled = false;
    button.innerHTML = 'Cek pesan ini <span aria-hidden="true">→</span>';
    $("#result").removeAttribute("aria-busy");
  }
}

async function checkMedia(file) {
  const button = $("#go");
  button.disabled = true;
  button.textContent = "Membaca berkas…";
  try {
    if (file.size > 6_000_000) throw Object.assign(new Error("big"), { http: 413 });
    const bytes = new Uint8Array(await file.arrayBuffer());
    let binary = "";
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    const response = await fetch(`${API}/api/check-media`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data_b64: btoa(binary), mime: file.type || "image/jpeg", channel: "web", sapaan: $("#sapaan").value, reporter: deviceId() }),
    });
    const data = await response.json();
    if (!response.ok) throw Object.assign(new Error(data.detail || response.statusText), { http: response.status, detail: data.detail });
    if (data.readable === false) { toast(data.message, true); return; }
    $("#msg").value = data.claim;
    updateInput();
    render(data, data.claim);
    toast("Halio membaca isi berkas Anda. Halio tidak menilai apakah fotonya asli, hanya isinya.");
  } catch (error) {
    console.error(error);
    toast(error.http === 413 ? "Berkasnya terlalu besar (maksimal 6 MB)."
      : error.http === 503 || error.http === 415 ? (error.detail || "Halio belum bisa membaca berkas ini. Ketik teksnya saja.")
      : "Halio belum bisa membaca berkas. Coba lagi atau ketik teksnya.", true);
  } finally {
    button.disabled = false;
    button.innerHTML = 'Cek pesan ini <span aria-hidden="true">→</span>';
    $("#media-file").value = "";
  }
}

function sourceList(match) {
  if (!match?.sumber?.length) return "";
  return `<ul class="source-list" aria-label="Sumber pemeriksaan">${match.sumber.map((source) => `
    <li><a class="source-link" href="${esc(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">
      <span aria-hidden="true">↗</span><span><small>Sumber pemeriksaan</small><b>${esc(source.nama)}</b></span><span aria-hidden="true">›</span>
    </a></li>`).join("")}</ul>`;
}

function processPanel(result) {
  const rows = [];
  const m = result.match;
  const used = (result.method || "").split("+");
  if (result.media) rows.push(["ok", `Membaca ${result.media.kind === "ucapan" ? "suara" : "foto"} dengan Gemini`, "Hanya isi tulisan/ucapan yang dibaca. Keaslian foto tidak dinilai."]);
  rows.push(["ok", "Mengenali klaim yang bisa dicek", `“${result.claim}”`]);
  rows.push([m ? "ok" : "none", "Mencocokkan dengan bantahan dan sumber yang sudah terverifikasi", m ? `Cocok dengan: ${m.klaim_dibantah} (kemiripan ${Math.round((m.score || 0) * 100)}%)` : "Tidak ada yang cukup mirip. Halio tidak menebak."]);
  const ev = result.evidence;
  if (used.includes("bukti_v2") && ev) {
    const why = [...new Set((ev.ditolak || []).map((r) => REJECT_WHY[r.alasan] || "halaman tidak bisa dipakai"))].slice(0, 2);
    rows.push(["ok", "AI mencari di web, kode memilih kutipan",
      `${ev.dicari?.length ? `Kata kunci: ${ev.dicari.slice(0, 2).join(", ")}. ` : ""}Halio membuka ${ev.dibuka} halaman; ${ev.relevan} berisi kalimat yang cocok dengan klaim, disalin oleh kode. AI hanya menilai hubungan tiap kutipan, tidak menulis kutipan dan tidak memberi vonis.${why.length ? ` Tidak dipakai: ${why.join("; ")}.` : ""}`]);
  } else if (used.includes("gemini_search")) {
    const n = result.llm || {};
    rows.push(["ok", "AI (Gemini) mencari di web", `${n.sumber_ditemukan ?? 0} sumber ditemukan. Kode Halio membuka setiap halaman dan mencocokkan kutipan: ${n.sumber_terverifikasi ?? 0} terverifikasi. AI tidak memberi vonis sendiri.`]);
  } else {
    rows.push(["none", "Pencarian web oleh AI", "Tidak dipakai pada pemeriksaan ini."]);
  }
  const links = result.links?.checked || [];
  for (const c of links) {
    rows.push([c.state === "terbuka" ? "ok" : "warn", `Membuka tautan ${c.host}`, c.state === "terbuka" ? `Terbuka${c.title ? `: “${c.title}”` : ""}${c.note ? ` · ${c.note}` : ""}` : c.note || c.state]);
  }
  const icon = { ok: "✓", warn: "!", none: "–" };
  return `<details class="process-details" open><summary>Bagaimana Halio memeriksa ini</summary><ol class="process-list">${rows.map(([k, t, d]) => `<li class="${k}"><span aria-hidden="true">${icon[k]}</span><div><b>${esc(t)}</b><small>${esc(d)}</small></div></li>`).join("")}</ol></details>`;
}

function readingPanel(result) {
  const link = (u, text) => `<a href="${esc(safeUrl(u))}" target="_blank" rel="noopener noreferrer">${esc(text)}</a>`;
  const items = (result.reading?.items || []).filter((i) => safeUrl(i.url) !== "#");
  const manual = (result.reading?.buka_sendiri || []).filter((i) => safeUrl(i.url) !== "#");
  const find = (result.cari_sendiri || []).filter((i) => safeUrl(i.url) !== "#");
  let html = "";
  if (items.length) {
    html += `<div class="reading-block"><h3>Halaman yang Halio buka dan bisa Anda baca</h3><p class="reading-note">Sudah dicek: bukan halaman error. Ini bahan bacaan, bukan dasar vonis; Halio tidak menyatakan isinya benar.</p><ul>${items.map((i) => `<li>${link(i.url, i.title)} <span class="reading-kind ${esc(i.kind)}">${esc(i.kind_label)}</span><small>${esc(i.host)}${i.tanggal ? " · " + esc(i.tanggal) : ""}</small></li>`).join("")}</ul>${result.reading.disaring ? `<small>${result.reading.disaring} halaman lain tidak ditampilkan karena rusak, tidak bisa dibuka, atau tidak membahas klaim ini.</small>` : ""}</div>`;
  } else if (result.evidence && ["belum_ada_pemeriksaan", "tidak_yakin"].includes(result.status)) {
    html += `<div class="reading-block"><h3>Bahan bacaan</h3><p class="reading-note">Tidak ada halaman relevan yang bisa dibuka untuk klaim ini.</p></div>`;
  }
  if (manual.length) html += `<div class="reading-block"><p class="reading-note">Situs ini menolak dibuka otomatis, mungkin tetap berguna:</p><ul>${manual.map((i) => `<li>${link(i.url, i.title)}<small>${esc(i.host)}</small></li>`).join("")}</ul></div>`;
  if (find.length) html += `<div class="reading-block"><h3>Cari sendiri</h3><ul>${find.map((i) => `<li>${link(i.url, i.nama)}</li>`).join("")}</ul></div>`;
  return html;
}

let stageTimer = 0;
function startStages(button) {
  const stages = ["Membaca dan mengenali klaim…", "Mencocokkan dengan bantahan terverifikasi…", "AI mencari sumber di web…", "Membuka dan mencocokkan kutipan sumber…"];
  let i = 0;
  button.textContent = stages[0];
  stageTimer = setInterval(() => { i = Math.min(i + 1, stages.length - 1); button.textContent = stages[i]; }, 1800);
}
function stopStages() { clearInterval(stageTimer); }

function render(result, original) {
  if (cardPreviewUrl) {
    URL.revokeObjectURL(cardPreviewUrl);
    cardPreviewUrl = "";
  }
  if (currentAudio) currentAudio.pause();
  window.speechSynthesis?.cancel();
  const match = result.match;
  const techniques = result.manipulation?.techniques || [];
  const warnings = result.links?.warnings || [];
  const tricks = techniques.map((technique) => `<div class="trick">
    <h3>${esc(technique.label)}</h3><p>${esc(technique.lesson)}</p>
    <small>Kalimat yang memicu perhatian: “${technique.evidence.map(esc).join("”, “")}”</small>
  </div>`).join("");
  const plain = PLAIN_REASONS.includes(result.reason);
  const many = Array.isArray(result.claims) && result.claims.length > 1;
  const steps = many
    ? ["Baca jawaban untuk tiap klaim di bawah.", "Jangan teruskan klaim yang sudah dibantah.", "Bagikan hanya bagian yang bersumber, dan sebut sumbernya."]
    : result.reason === "berita_media_dikenal"
    ? ["Halio belum menilai isi berita ini.", "Untuk hal penting, bandingkan dengan satu atau dua media lain.", "Buka artikelnya dan baca sampai habis sebelum membagikan."]
    : result.reason === "kumpulan_judul"
    ? ["Kirim satu judul atau satu berita per pesan.", "Halio akan memeriksanya satu per satu."]
    : result.status === "dilaporkan_media"
    ? ["Ini laporan media, bukan pemeriksaan fakta.", "Cek tanggal laporan dan bandingkan dengan sumber lain.", "Bila dibagikan, sebut sumbernya."]
    : match
    ? ["Baca bantahan dan buka sumbernya.", "Jangan teruskan pesan yang menyesatkan.", "Beritahu pengirim dengan bahasa yang sopan."]
    : ["Tahan dulu sebelum meneruskan.", "Cari kabar dari kanal resmi.", "Minta bantuan pemeriksa bila tersedia."];

  $("#result").innerHTML = `
    <article class="verdict-card ${esc(result.status)}">
      ${result.mode === "tanpa_ai" ? '<p class="mode-banner">🔌 <b>Mode tanpa AI.</b> Jawaban ini hanya dari korpus dan arsip bantahan; tidak ada model yang dipanggil.</p>' : ""}
      <div class="result-kicker"><span>Hasil pemeriksaan</span><span>${window.HALIO_STATIC_DEMO ? "Simulasi lokal" : "Halio"}</span></div>
      <div class="verdict-heading"><span class="verdict-mark" aria-hidden="true">${ICON[result.status] || "?"}</span><div><h2>${esc(LABEL_BY_REASON[result.reason] || result.status_label)}</h2><p>Klaim diperiksa, bukan pengirimnya.</p></div></div>
      ${infoPanel(result)}
      ${plain ? "" : `<p class="answer-lead">${esc(match && !many ? match.sederhana : result.voice_script)}</p>`}
      ${result.attribution ? `<p class="warning attribution"><b>Sumber yang disebut berbeda.</b> ${esc(result.attribution.catatan)}</p>` : ""}
      ${claimsPanel(result)}
      ${many ? "" : evidencePanel(result)}
      ${match && !many ? `<div class="fact-block"><h3>Fakta di baliknya</h3><p>${esc(match.fakta)}</p></div>${sourceList(match)}` : ""}
      ${result.llm?.kutipan ? `<div class="fact-block"><h3>Kutipan pendukung</h3><p>“${esc(result.llm.kutipan)}”</p></div>` : ""}
      ${processPanel(result)}
      ${window.HALIO_STATIC_DEMO ? "" : `<div class="telusur-cta"><a class="action-button" href="laporan.html?mulai=1&tampilan=keluarga&q=${encodeURIComponent(result.claim || original || "")}">🔬 Telusuri mendalam</a><small>Laporan analis: puluhan sumber, linimasa, asal-usul yang ditemukan. 1–3 menit.</small></div>`}
      ${readingPanel(result)}
      <div class="next-steps"><h3>Yang bisa Anda lakukan</h3><ol>${steps.map((step) => `<li>${esc(step)}</li>`).join("")}</ol></div>
      ${warnings.map((warning) => `<p class="warning">${esc(warning)}</p>`).join("")}
      <details class="claim-details"><summary>Lihat klaim yang diperiksa</summary><p>“${esc(result.claim)}”</p></details>
      <div class="main-actions">
        <button id="share" class="action-button primary" type="button"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 16V3m0 0L7 8m5-5 5 5M5 13v7h14v-7" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>Bagikan kartu</button>
        <button id="listen" class="action-button" type="button"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 9v6h4l5 4V5L9 9H5Zm12 0c1.3 1.7 1.3 4.3 0 6m2-9c3.3 3.3 3.3 8.7 0 12" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>Dengarkan</button>
      </div>
      <div class="secondary-actions">${result.offer_human_review
        ? '<button id="human" class="text-button" type="button">Minta pemeriksa manusia</button>'
        : '<button id="appeal" class="text-button" type="button">Ajukan banding atas hasil</button>'}</div>
      <details class="forward-details"><summary>Saya tetap ingin meneruskan pesan asli</summary><div class="forward-box"><p>Ambil jeda sepuluh detik. Pesan hanya akan disalin setelah hitungan selesai; sertakan konteks dan sumber saat membagikannya.</p><button id="forward" class="action-button" type="button">Mulai jeda 10 detik</button></div></details>
      <p class="result-footnote">${esc(result.disclaimer)} Metode: ${esc(result.method)}.</p>
    </article>
    ${tricks ? `<details class="manipulation-details"><summary>Kenali trik dalam pesan ini (${techniques.length})</summary>${tricks}</details>` : ""}
    <details class="card-details" id="card-details"><summary>Pratinjau kartu untuk dibagikan</summary><div id="card-preview"></div></details>
    <button id="check-again" class="action-button check-again" type="button">Periksa pesan lain</button>`;

  const resultElement = $("#result");
  resultElement.classList.remove("hidden", "result-enter");
  void resultElement.offsetWidth;
  resultElement.classList.add("result-enter");
  resultElement.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
  $("#share").onclick = async () => {
    const button = $("#share");
    button.disabled = true;
    try { await shareCard(result); }
    catch (error) { if (error.name !== "AbortError") toast("Kartu belum bisa dibagikan. Coba unduh kembali.", true); }
    finally { button.disabled = false; }
  };
  $("#listen").onclick = () => speak(result);
  $("#forward").onclick = (event) => pauseBeforeShare(event.currentTarget, original);
  $("#check-again").onclick = () => {
    $("#msg").focus();
    $("#checker").scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth" });
  };
  const human = $("#human");
  if (human) human.onclick = () => submitReview("/api/escalate", { check_id: result.id }, human);
  const appeal = $("#appeal");
  if (appeal) appeal.onclick = () => openAppeal(result.id);
  $("#card-details").addEventListener("toggle", (event) => {
    if (event.currentTarget.open) showCardPreview(result);
  });
}

async function post(path, body) {
  if (window.HALIO_STATIC_DEMO) {
    return { message: "Ini demo lokal. Tidak ada tiket atau banding yang dikirim ke server." };
  }
  const response = await fetch(API + path, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Permintaan belum berhasil.");
  return data;
}

async function submitReview(path, body, button) {
  button.disabled = true;
  try {
    const data = await post(path, body);
    toast(data.message || "Banding dicatat. Terima kasih sudah memeriksa kembali.");
    if (data.ticket) toast(`Tiket #${data.ticket}. Simpan nomor ini untuk tindak lanjut.`);
  } catch (error) {
    toast(error.message || "Belum bisa dikirim. Coba lagi.", true);
  } finally { button.disabled = false; }
}

function openAppeal(checkId) {
  appealCheckId = checkId;
  $("#appeal-reason").value = "";
  $("#appeal-dialog").showModal();
  $("#appeal-reason").focus();
}

function speak(result) {
  const button = $("#listen");
  const fallback = () => {
    if (!("speechSynthesis" in window)) return toast("Perangkat ini belum mendukung suara.", true);
    const utterance = new SpeechSynthesisUtterance(result.voice_script);
    utterance.lang = "id-ID";
    utterance.rate = 0.92;
    const voice = speechSynthesis.getVoices().find((item) => item.lang.startsWith("id"));
    if (voice) utterance.voice = voice;
    utterance.onend = utterance.onerror = () => { button.textContent = "Dengarkan"; };
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
  };
  button.textContent = "Memutar suara…";
  if (!result.voice_url) return fallback();
  if (currentAudio) currentAudio.pause();
  currentAudio = new Audio(API + result.voice_url);
  currentAudio.onended = () => { button.textContent = "Dengarkan"; };
  currentAudio.play().catch(fallback);
}

function infoPanel(result) {
  const info = result.info;
  if (!info) return "";
  if (result.kind === "kumpulan_judul") {
    return `<div class="fact-block"><h3>Judul yang terbaca</h3><ol>${(info.judul_list || []).map((t) => `<li>${esc(t)}</li>`).join("")}</ol></div>`;
  }
  const when = longDate(info.terbit);
  return `<div class="fact-block"><h3>${esc(info.judul || "Artikel")}</h3><p>${esc(info.penerbit)}${when ? ` · ${esc(when)}` : ""}</p>
    ${info.ringkasan ? `<p>“${esc(info.ringkasan)}”</p><small>Ringkasan dari halaman itu sendiri, bukan penilaian Halio.</small>` : ""}
    ${info.url ? `<p><a href="${esc(safeUrl(info.url))}" target="_blank" rel="noopener">Buka artikel</a></p>` : ""}</div>`;
}

function claimsPanel(result) {
  if (!Array.isArray(result.claims) || result.claims.length < 2) return "";
  const rows = result.claims.map((c, i) => {
    const src = (c.match?.sumber || [])[0];
    const why = c.match?.sederhana || c.evidence?.alasan || "";
    return `<li class="claim-row ${esc(c.status)}"><span class="claim-no" aria-hidden="true">${i + 1}</span><div>
      <b>${esc(STATUS_WORD[c.status] || c.status_label)}</b><p class="claim-text">“${esc(c.claim)}”</p>
      ${why ? `<p>${esc(why)}</p>` : ""}${src ? `<p><a href="${esc(safeUrl(src.url))}" target="_blank" rel="noopener">${esc(src.nama)}</a></p>` : ""}</div></li>`;
  }).join("");
  return `<div class="fact-block claims-block"><h3>Jawaban untuk tiap klaim</h3><ol class="claim-list">${rows}</ol></div>`;
}

function evidencePanel(result) {
  const ev = result.evidence;
  if (!ev || !ev.items?.length) return "";
  const bar = "■".repeat(ev.kekuatan) + "□".repeat(4 - ev.kekuatan);
  const rows = [...ev.items].sort((a, b) => (TIER_ORDER[a.tingkat] ?? 9) - (TIER_ORDER[b.tingkat] ?? 9)).slice(0, 4).map((it) => {
    const when = longDate(it.tanggal);
    return `<li><a href="${esc(safeUrl(it.url_sorot || it.url))}" target="_blank" rel="noopener" title="Membuka halaman asli dengan kalimat ini disorot">${esc(it.penerbit)}</a> <span class="tier">${esc(it.tingkat_label)}${when ? ` · ${esc(when)}` : ""}</span>
      <blockquote>“${esc(it.kutipan.length > 240 ? it.kutipan.slice(0, 237) + "…" : it.kutipan)}”</blockquote><small class="hl-note">Klik nama sumber: halaman asli terbuka dengan kalimat ini disorot.</small></li>`;
  }).join("");
  return `<div class="fact-block evidence-block"><h3>Yang Halio temukan <span class="meter" title="Kekuatan bukti 0 sampai 4">${bar} ${ev.kekuatan}/4</span></h3>
    <ul class="evidence-list">${rows}</ul><p>${esc(ev.alasan)}</p>
    <small>Kutipan disalin langsung dari halaman oleh kode; AI hanya menilai hubungannya dengan klaim.</small></div>`;
}

async function makeStaticCard(result) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1350;
  const context = canvas.getContext("2d");
  context.fillStyle = "#F8F3F0";
  context.fillRect(0, 0, 1080, 1350);
  // Same layout and palette as the server's Kartu Halio (backend/halio/card.py, video/BRAND.md).
  const THEME = { terbukti_salah: "#B42318", sejalan_dengan_sumber: "#067647", dilaporkan_media: "#014BAA", tidak_yakin: "#B54708", belum_ada_pemeriksaan: "#475467" };
  const SERIF = '"Instrument Serif", Georgia, serif', SANS = 'Inter, system-ui, Arial, sans-serif';
  try { await Promise.all([document.fonts.load(`80px ${SERIF}`), document.fonts.load(`600 30px ${SANS}`)]); } catch { /* fall back to system fonts */ }
  context.fillStyle = "#014BAA";
  context.fillRect(0, 0, 1080, 170);
  context.fillStyle = "#F8F3F0";
  context.font = `84px ${SERIF}`;
  context.fillText("halio", 80, 112);
  context.fillStyle = "#FFC83D";
  context.fillText(".", 80 + context.measureText("halio").width, 112);
  context.fillStyle = THEME[result.status] || "#0E1726";
  context.font = `700 66px ${SANS}`;
  const status = context.measureText(result.status_label).width > 900 ? "Belum ada pemeriksaan" : result.status_label;
  context.fillText(status, 80, 300);
  context.fillStyle = "#0E1726";
  context.font = `500 46px ${SANS}`;
  let line = "";
  let y = 410;
  for (const word of result.voice_script.split(" ")) {
    const test = `${line}${word} `;
    if (context.measureText(test).width > 900) {
      context.fillText(line, 80, y);
      y += 68;
      line = "";
    }
    line += `${word} `;
  }
  context.fillText(line, 80, y);
  if (result.match?.sumber?.length) {
    context.fillStyle = "#5B6475";
    context.font = `500 28px ${SANS}`;
    context.fillText("Sumber:", 80, 1060);
    context.fillStyle = "#0E1726";
    context.font = `700 30px ${SANS}`;
    context.fillText(result.match.sumber[0].nama.slice(0, 58), 80, 1110);
  }
  context.fillStyle = "#5B6475";
  context.font = `500 25px ${SANS}`;
  context.fillText(window.HALIO_STATIC_DEMO ? "Kartu simulasi lokal · periksa kembali sumbernya" : "Kartu Halio · periksa kembali sumbernya", 80, 1250);
  return new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
}

async function cardBlob(result) {
  if (result.card_url) {
    const response = await fetch(API + result.card_url);
    if (!response.ok) throw new Error("Kartu belum tersedia");
    return response.blob();
  }
  const blob = await makeStaticCard(result);
  if (!blob) throw new Error("Kartu belum dapat dibuat");
  return blob;
}

async function showCardPreview(result) {
  const container = $("#card-preview");
  if (!container || container.childElementCount) return;
  container.innerHTML = '<p class="result-footnote">Menyiapkan kartu…</p>';
  try {
    const blob = await cardBlob(result);
    cardPreviewUrl = URL.createObjectURL(blob);
    container.innerHTML = "";
    const image = new Image();
    image.className = "card-preview";
    image.src = cardPreviewUrl;
    image.alt = `Kartu Halio: ${result.status_label}. ${result.voice_script}`;
    container.appendChild(image);
  } catch { container.innerHTML = '<p class="result-footnote">Kartu belum bisa ditampilkan.</p>'; }
}

async function shareCard(result) {
  const blob = await cardBlob(result);
  const file = new File([blob], "kartu-halio.png", { type: "image/png" });
  const text = result.match ? `${result.status_label}: ${result.match.sederhana} Sumber: ${result.match.sumber[0].url}` : result.voice_script;
  if (navigator.canShare?.({ files: [file] })) {
    await navigator.share({ files: [file], text });
  } else {
    const url = URL.createObjectURL(blob);
    const anchor = Object.assign(document.createElement("a"), { href: url, download: "kartu-halio.png" });
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    toast("Kartu diunduh. Sertakan sumber saat membagikannya.");
  }
}

function pauseBeforeShare(button, original) {
  let seconds = 10;
  button.disabled = true;
  const tick = () => {
    button.textContent = `Tunggu ${seconds} detik · periksa sumbernya dulu`;
    if (seconds-- > 0) return setTimeout(tick, 1000);
    button.disabled = false;
    button.textContent = "Salin pesan asli";
    button.onclick = async () => {
      try {
        await navigator.clipboard.writeText(original);
        toast("Pesan disalin. Sertakan konteks dan sumbernya saat meneruskan.");
      } catch { toast("Perangkat ini tidak mengizinkan penyalinan otomatis.", true); }
    };
  };
  tick();
}

async function showVersion() {
  const el = $("#version");
  if (!el) return;
  if (window.HALIO_STATIC_DEMO) { el.textContent = "Demo statis di browser (tanpa server)"; return; }
  try {
    const h = await (await fetch(`${API}/health`)).json();
    el.textContent = `Halio v${h.version} · build ${h.build || "lokal"} · AI web: ${h.llm ? "aktif" : "mati"}`;
  } catch { el.textContent = "Versi server tidak terbaca"; }
}

function init() {
  showVersion();
  // The no-AI switch is a demo control, shown with ?demo=1 so ordinary visitors are not confused by it.
  if (new URLSearchParams(location.search).has("demo") && !window.HALIO_STATIC_DEMO) $("#noai-row")?.classList.remove("hidden");
  if (window.HALIO_STATIC_DEMO) $("#static-notice").classList.remove("hidden");
  const sapaan = $("#sapaan");
  sapaan.value = store.get("halio.sapaan", "Bapak, Ibu");
  sapaan.onchange = () => store.set("halio.sapaan", sapaan.value);
  if (window.HALIO_STATIC_DEMO) $("#media-row")?.classList.add("hidden");
  else $("#media-file")?.addEventListener("change", (event) => event.target.files[0] && checkMedia(event.target.files[0]));
  $("#msg").addEventListener("input", updateInput);
  $("#msg").addEventListener("keydown", (event) => {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      $("#go").click();
    }
  });
  $("#clear-input").onclick = () => { $("#msg").value = ""; updateInput(); $("#msg").focus(); };
  for (const [label, text] of EXAMPLES) {
    const button = Object.assign(document.createElement("button"), { className: "example-button", type: "button", textContent: label });
    button.onclick = () => {
      $("#msg").value = text;
      updateInput();
      $("#msg").focus();
      $("#checker").scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "center" });
    };
    $("#examples").appendChild(button);
  }
  $("#go").onclick = () => {
    const text = $("#msg").value.trim();
    if (text.length < 3) return toast("Tempel dulu pesan yang ingin diperiksa.");
    if (!$("#go").disabled) check(text);
  };
  $("#appeal-close").onclick = () => $("#appeal-dialog").close();
  $("#appeal-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  $("#appeal-form").onsubmit = async (event) => {
    event.preventDefault();
    const button = event.currentTarget.querySelector('[type="submit"]');
    button.disabled = true;
    try {
      const data = await post("/api/appeal", { check_id: appealCheckId, reason: $("#appeal-reason").value.trim() });
      $("#appeal-dialog").close();
      toast(data.message || "Banding dicatat. Terima kasih sudah memeriksa kembali.");
    } catch (error) { toast(error.message || "Banding belum bisa dikirim.", true); }
    finally { button.disabled = false; }
  };

  const params = new URLSearchParams(location.search);
  const shared = [params.get("title"), params.get("text"), params.get("url")].filter(Boolean).join("\n");
  if (shared) {
    $("#msg").value = shared.slice(0, 4000);
    updateInput();
    check($("#msg").value);
    history.replaceState(null, "", location.pathname);
  }
  if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js").catch(() => {});
  window.addEventListener("pagehide", () => {
    if (cardPreviewUrl) URL.revokeObjectURL(cardPreviewUrl);
    if (currentAudio) currentAudio.pause();
  });
}

init();

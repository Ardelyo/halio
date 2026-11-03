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
  button.textContent = "Sedang memeriksa…";
  $("#result").setAttribute("aria-busy", "true");
  try {
    let result;
    if (window.HALIO_STATIC_DEMO) {
      await new Promise((resolve) => setTimeout(resolve, 350));
      result = window.HalioStaticDemo.check(text);
    } else {
      const response = await fetch(`${API}/api/check`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, channel: "web", sapaan: $("#sapaan").value, reporter: deviceId() }),
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
    button.disabled = false;
    button.innerHTML = 'Cek pesan ini <span aria-hidden="true">→</span>';
    $("#result").removeAttribute("aria-busy");
  }
}

function sourceList(match) {
  if (!match?.sumber?.length) return "";
  return `<ul class="source-list" aria-label="Sumber pemeriksaan">${match.sumber.map((source) => `
    <li><a class="source-link" href="${esc(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">
      <span aria-hidden="true">↗</span><span><small>Sumber pemeriksaan</small><b>${esc(source.nama)}</b></span><span aria-hidden="true">›</span>
    </a></li>`).join("")}</ul>`;
}

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
  const steps = match
    ? ["Baca bantahan dan buka sumbernya.", "Jangan teruskan pesan yang menyesatkan.", "Beritahu pengirim dengan bahasa yang sopan."]
    : ["Tahan dulu sebelum meneruskan.", "Cari kabar dari kanal resmi.", "Minta bantuan pemeriksa bila tersedia."];

  $("#result").innerHTML = `
    <article class="verdict-card ${esc(result.status)}">
      <div class="result-kicker"><span>Hasil pemeriksaan</span><span>${window.HALIO_STATIC_DEMO ? "Simulasi lokal" : "Halio"}</span></div>
      <div class="verdict-heading"><span class="verdict-mark" aria-hidden="true">${ICON[result.status] || "?"}</span><div><h2>${esc(result.status_label)}</h2><p>Klaim diperiksa, bukan pengirimnya.</p></div></div>
      <p class="answer-lead">${esc(match ? match.sederhana : result.voice_script)}</p>
      ${match ? `<div class="fact-block"><h3>Fakta di baliknya</h3><p>${esc(match.fakta)}</p></div>${sourceList(match)}` : ""}
      ${result.llm ? `<div class="fact-block"><h3>Kutipan pendukung</h3><p>“${esc(result.llm.kutipan)}”</p></div>` : ""}
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

async function makeStaticCard(result) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1350;
  const context = canvas.getContext("2d");
  context.fillStyle = "#F8F3F0";
  context.fillRect(0, 0, 1080, 1350);
  // Same layout and palette as the server's Kartu Halio (backend/halio/card.py, video/BRAND.md).
  const THEME = { terbukti_salah: "#B42318", sejalan_dengan_sumber: "#067647", tidak_yakin: "#B54708", belum_ada_pemeriksaan: "#475467" };
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

function init() {
  if (window.HALIO_STATIC_DEMO) $("#static-notice").classList.remove("hidden");
  const sapaan = $("#sapaan");
  sapaan.value = store.get("halio.sapaan", "Bapak, Ibu");
  sapaan.onchange = () => store.set("halio.sapaan", sapaan.value);
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

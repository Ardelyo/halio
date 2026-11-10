const API = window.HALIO_API || "";
const STATIC = window.HALIO_STATIC_DEMO;
const KATEGORI = {
  penipuan_bansos: "Penipuan bansos", penipuan_catut_tni: "Penipuan mencatut TNI", bencana: "Bencana",
  kesehatan: "Kesehatan", phishing: "Phishing / pencurian data", keamanan_publik: "Keamanan publik", claimreview: "Pemeriksa fakta lain",
};
const TECH = {
  ajakan_sebar: "Desakan menyebarkan", urgensi: "Dibuat terburu-buru", otoritas_palsu: "Mengaku orang penting",
  rasa_takut: "Menakut-nakuti", iming_iming: "Iming-iming hadiah", minta_data_uang: "Minta data atau uang",
};
const STATUS = [
  ["terbukti_salah", "Terbukti salah", "#B42318"],
  ["sejalan_dengan_sumber", "Sejalan dengan sumber", "#067647"],
  ["dilaporkan_media", "Dilaporkan media", "#014BAA"],
  ["tidak_yakin", "Tidak yakin", "#B54708"],
  ["belum_ada_pemeriksaan", "Belum diperiksa", "#98A2B3"],
];
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[character]));
const storage = {
  get(key) { try { return localStorage.getItem(key) || ""; } catch { return ""; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* Storage may be unavailable. */ } },
};
const state = {
  days: 7, view: "overview", type: "escalations", openOnly: true,
  radar: null, reviews: { escalations: { items: [], events: [] }, appeals: { items: [], events: [] } },
  coverage: null, recent: null, currentTicket: null, loading: false, token: storage.get("halio.radar"),
};

function formatDate(value, withTime = false) {
  const date = new Date(value?.length === 10 ? `${value}T00:00:00+07:00` : value);
  if (Number.isNaN(date.getTime())) return value || "—";
  return new Intl.DateTimeFormat("id-ID", withTime
    ? { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }
    : { day: "numeric", month: "short", year: "numeric" }).format(date);
}

function shortDate(value) {
  return new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "short" }).format(new Date(`${value}T00:00:00+07:00`));
}

function toast(text, error = false) {
  const item = document.createElement("div");
  item.className = `toast${error ? " error" : ""}`;
  item.textContent = text;
  item.setAttribute("role", error ? "alert" : "status");
  $("#toast-region").replaceChildren(item);
  setTimeout(() => item.remove(), 5000);
}

async function request(path, options = {}) {
  const response = await fetch(API + path, {
    ...options,
    headers: { "Content-Type": "application/json", ...(state.token ? { Authorization: `Bearer ${state.token}` } : {}), ...options.headers },
  });
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(typeof data.detail === "string" ? data.detail : "Permintaan belum berhasil.");
    error.status = response.status;
    throw error;
  }
  return data;
}

async function loadDashboard() {
  if (state.loading) return;
  state.loading = true;
  $("#refresh").disabled = true;
  $("#load-error").classList.add("hidden");
  $("#connection-label").textContent = "Memperbarui data";
  $("#connection-dot").className = "connection-dot";
  try {
    if (STATIC) {
      state.radar = window.HalioDashboardDemo.radar(state.days);
      state.reviews.escalations = window.HalioDashboardDemo.reviews("escalations", false);
      state.reviews.appeals = window.HalioDashboardDemo.reviews("appeals", false);
      state.coverage = window.HalioDashboardDemo.coverage.coverage;
      state.recent = window.HalioDashboardDemo.coverage.recent;
    } else {
      const [radar, escalations, appeals, coverage, recent] = await Promise.all([
        request(`/api/radar?days=${state.days}`),
        request("/api/review/escalations?open_only=false"),
        request("/api/review/appeals?open_only=false"),
        request("/api/sensor/coverage"),
        request("/api/sensor/items?limit=8"),
      ]);
      Object.assign(state, { radar, coverage, recent });
      // Seeded demo rows (channel "demo") sit beside real ones on a server; say so whenever any are in the window.
      const demoEvents = Number(radar.demo_events || 0);
      $("#seed-notice").classList.toggle("hidden", demoEvents <= 0);
      $("#seed-count").textContent = `${demoEvents} dari ${radar.total_checks} cek`;
      state.reviews = { escalations, appeals };
    }
    renderAll();
    $("#connection-label").textContent = STATIC ? "Simulasi di perangkat" : "API terhubung";
    $("#connection-dot").className = "connection-dot online";
    $("#last-updated").textContent = STATIC ? "Data sintetis · sesi ini" : `Diperbarui ${new Intl.DateTimeFormat("id-ID", { hour: "2-digit", minute: "2-digit" }).format(new Date())}`;
  } catch (error) {
    console.error(error);
    $("#connection-label").textContent = error.status === 401 ? "Akses diperlukan" : "Koneksi terputus";
    $("#connection-dot").className = "connection-dot offline";
    const message = error.status === 401 ? "Radar memerlukan token akses dari server." : "Data belum dapat dimuat. Periksa API dan token akses, lalu coba lagi.";
    $("#load-error").textContent = message;
    $("#load-error").classList.remove("hidden");
    if (error.status === 401) openAccess();
  } finally {
    state.loading = false;
    $("#refresh").disabled = false;
  }
}

function renderAll() {
  renderOverview();
  renderQueue();
  renderEmerging();
  renderCoverage();
}

function renderOverview() {
  const data = state.radar;
  const openTotal = data.open_appeals + data.open_escalations;
  const metrics = [
    ["Pesan diperiksa", data.total_checks, `${data.window_days} hari terakhir`, "↗", ""],
    ["Terbukti salah", data.by_status.terbukti_salah || 0, `${percentage(data.by_status.terbukti_salah || 0, data.total_checks)} dari seluruh cek`, "!", ""],
    ["Belum ada pemeriksaan", data.by_status.belum_ada_pemeriksaan || 0, "Bukan berarti kabar benar", "?", ""],
    ["Perlu tindakan", openTotal, `${data.open_escalations} eskalasi · ${data.open_appeals} banding`, "□", "attention"],
  ];
  $("#metrics").innerHTML = metrics.map(([label, value, note, symbol, className]) => `<article class="metric-card ${className}"><div class="metric-label"><span>${esc(label)}</span><span class="metric-symbol" aria-hidden="true">${symbol}</span></div><div class="metric-value">${esc(value)}</div><p class="metric-note">${esc(note)}</p></article>`).join("");
  $("#nav-queue-count").textContent = openTotal;
  $("#queue-callout-title").textContent = openTotal ? `${openTotal} tiket menunggu tindakan.` : "Tidak ada tiket terbuka.";
  $("#trend-total").textContent = `${data.total_checks} cek`;
  renderTrend(data);
  renderStatus(data);
  renderBars("#categories", data.by_kategori.map((item) => ({ label: KATEGORI[item.kategori] || item.kategori, n: item.n })));
  renderBars("#techniques", Object.entries(data.techniques).map(([key, n]) => ({ label: TECH[key] || key, n })));
  renderEvidenceHealth(data.evidence_telemetry);
}

function percentage(value, total) {
  return total ? `${Math.round(value / total * 100)}%` : "0%";
}

const REJECT = {
  domain_bukan_sumber_primer: "Situs bukan sumber resmi atau pemeriksa fakta", bukan_sumber_dikenal: "Situs bukan media atau sumber yang dikenal",
  mesin_pencari_atau_pengalih: "Hanya mesin pencari atau pengalih", sumber_tidak_dapat_diakses: "Halaman tidak bisa dibuka",
  http_404: "Halaman tidak ditemukan (404)", http_403: "Situs menolak dibuka otomatis (403)", http_410: "Halaman sudah dihapus (410)",
  jenis_konten_tidak_didukung: "Bukan halaman web (PDF, gambar)", halaman_terlalu_besar: "Halaman terlalu besar", url_tidak_aman: "Alamat tidak aman",
  alamat_jaringan_tidak_publik: "Alamat jaringan tidak publik", terlalu_banyak_redirect: "Terlalu banyak pengalihan",
};
const OUTCOME = {
  dibantah_resmi: "Dibantah sumber resmi", dibantah_pemeriksa_fakta: "Dibantah pemeriksa fakta", cocok_dengan_sumber_resmi: "Sejalan dengan sumber resmi",
  dilaporkan_beberapa_media: "Dilaporkan beberapa media", satu_media_melaporkan: "Baru satu media melaporkan", bukti_bertentangan: "Bukti saling bertentangan",
  media_melaporkan_bantahan: "Media melaporkan bantahan", laporan_media_tanpa_tanggal_baru: "Laporan media tanpa tanggal baru",
  sumber_resmi_tanpa_tanggal_atau_lama: "Sumber resmi tanpa tanggal atau lama", tidak_ada_sumber_relevan: "Tidak ada sumber yang relevan",
};

function renderEvidenceHealth(t) {
  const panel = document.querySelector(".evidence-health");
  if (!panel) return;
  if (!t || !t.pemeriksaan) {
    $("#evidence-summary").textContent = "Belum ada pemeriksaan yang memakai pencarian web pada periode ini.";
    $("#evidence-rejections").innerHTML = ""; $("#evidence-results").innerHTML = "";
    return;
  }
  const usable = t.halaman_dibuka ? Math.round(t.halaman_relevan / t.halaman_dibuka * 100) : 0;
  $("#evidence-summary").textContent = `${t.pemeriksaan} pemeriksaan memakai pencarian web. Halio membuka ${t.halaman_dibuka} halaman; ${t.halaman_relevan} (${usable}%) berisi kalimat yang cocok dengan klaim.`
    + (t.mesin_cadangan ? ` Mesin cadangan dipakai ${t.mesin_cadangan} kali karena pencarian atau penilaian gagal.` : "");
  renderBars("#evidence-rejections", t.ditolak.map((r) => ({ label: REJECT[r.alasan] || r.alasan, n: r.n })));
  renderBars("#evidence-results", t.hasil.map((r) => ({ label: OUTCOME[r.alasan] || r.alasan, n: r.n })));
}

function renderBars(selector, rows) {
  const max = Math.max(1, ...rows.map((row) => typeof row.n === "number" ? row.n : 1));
  $(selector).innerHTML = rows.length ? rows.map((row) => {
    const value = typeof row.n === "number" ? row.n : 1;
    return `<div class="bar-row"><span>${esc(row.label)}</span><span class="bar-track"><span class="bar-fill" style="display:block;width:${Math.max(4, value / max * 100)}%"></span></span><b>${esc(row.n)}</b></div>`;
  }).join("") : '<p class="empty-state">Belum ada data pada periode ini.</p>';
}

function trendRows(data) {
  const totals = Object.fromEntries(data.daily.map((row) => [row.day, 0]));
  for (const row of data.daily) totals[row.day] = (totals[row.day] || 0) + row.n;
  const rows = [];
  for (let date = new Date(`${data.since}T00:00:00Z`); rows.length < data.window_days; date.setUTCDate(date.getUTCDate() + 1)) {
    const day = date.toISOString().slice(0, 10);
    rows.push({ day, n: totals[day] || 0 });
  }
  return rows;
}

function renderTrend(data) {
  const rows = trendRows(data);
  const width = 660;
  const height = 205;
  const left = 28;
  const right = 12;
  const top = 18;
  const bottom = 35;
  const max = Math.max(1, ...rows.map((row) => row.n));
  const roundedMax = Math.max(4, Math.ceil(max / 4) * 4);
  const x = (index) => left + index * ((width - left - right) / Math.max(1, rows.length - 1));
  const y = (value) => top + (height - top - bottom) * (1 - value / roundedMax);
  const points = rows.map((row, index) => [x(index), y(row.n)]);
  const line = points.map(([px, py], index) => `${index ? "L" : "M"}${px.toFixed(1)},${py.toFixed(1)}`).join(" ");
  const area = `${line} L${points.at(-1)[0]},${height - bottom} L${points[0][0]},${height - bottom} Z`;
  const grids = [0, .5, 1].map((ratio) => {
    const gy = top + (height - top - bottom) * ratio;
    const value = Math.round(roundedMax * (1 - ratio));
    return `<line class="chart-grid" x1="${left}" x2="${width - right}" y1="${gy}" y2="${gy}"/><text class="chart-label" x="0" y="${gy + 3}">${value}</text>`;
  }).join("");
  const labelEvery = Math.max(1, Math.ceil(rows.length / 6));
  const labels = rows.map((row, index) => (index % labelEvery === 0 || index === rows.length - 1)
    ? `<text class="chart-label" text-anchor="middle" x="${x(index)}" y="${height - 10}">${esc(shortDate(row.day))}</text>` : "").join("");
  const circles = rows.map((row, index) => `<circle class="chart-point" cx="${x(index)}" cy="${y(row.n)}" r="3"><title>${esc(formatDate(row.day))}: ${row.n} cek</title></circle>`).join("");
  $("#trend-chart").innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Grafik ${data.total_checks} pemeriksaan selama ${data.window_days} hari"><defs><linearGradient id="chart-fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6F7D93" stop-opacity=".25"/><stop offset="1" stop-color="#6F7D93" stop-opacity="0"/></linearGradient></defs>${grids}<path class="chart-area" d="${area}"/><path class="chart-line" d="${line}"/>${circles}${labels}</svg>`;
  $("#trend-table").innerHTML = `<thead><tr><th>Tanggal</th><th class="numeric">Jumlah cek</th></tr></thead><tbody>${rows.map((row) => `<tr><td>${esc(formatDate(row.day))}</td><td class="numeric">${row.n}</td></tr>`).join("")}</tbody>`;
}

function renderStatus(data) {
  const total = data.total_checks;
  let cursor = 0;
  const segments = STATUS.map(([key, , color]) => {
    const start = cursor;
    cursor += total ? (data.by_status[key] || 0) / total * 100 : 0;
    return `${color} ${start}% ${cursor}%`;
  });
  if (!total) segments.push("#E7E1DC 0 100%");
  $("#status-breakdown").innerHTML = `<div class="donut-layout"><div class="donut" style="background:conic-gradient(${segments.join(",")})"><div class="donut-center"><b>${total}</b><span>total cek</span></div></div><div class="status-legend">${STATUS.map(([key, label, color]) => `<div class="status-row"><i style="background:${color}"></i><span>${label}</span><b>${data.by_status[key] || 0}</b></div>`).join("")}</div></div>`;
}

function pending(item, type = state.type) {
  return item.status === (type === "appeals" ? "baru" : "menunggu");
}

function renderQueue() {
  for (const type of ["escalations", "appeals"]) {
    const count = state.reviews[type].items.filter((item) => pending(item, type)).length;
    $(type === "escalations" ? "#escalation-count" : "#appeal-count").textContent = count;
  }
  const items = state.reviews[state.type].items.filter((item) => !state.openOnly || pending(item));
  $("#ticket-list").innerHTML = items.length ? items.map((item) => `<button class="ticket" type="button" data-ticket-id="${item.id}" aria-label="Buka tiket ${item.id}">
    <span class="ticket-id">#${item.id}</span><span class="ticket-main"><span class="ticket-meta"><span class="status-chip ${item.status === "selesai" ? "closed" : ""}">${item.status === "selesai" ? "Selesai" : "Terbuka"}</span><span>${esc(formatDate(item.created, true))}</span></span><p class="ticket-claim">${esc(state.type === "appeals" ? item.reason || "Banding tanpa catatan tambahan" : item.claim)}</p></span><span class="ticket-arrow" aria-hidden="true">›</span>
  </button>`).join("") : `<div class="panel empty-state">${state.openOnly ? "Tidak ada tiket yang perlu ditangani. Pilih “Semua tiket” untuk melihat riwayat." : "Belum ada tiket pada antrean ini."}</div>`;
}

function renderEmerging() {
  const data = state.radar;
  $("#k-anonymity").textContent = data.k_anonymity;
  $("#below-k").textContent = `${data.rumours_below_k} di bawah ambang`;
  $("#emerging-table").innerHTML = `<thead><tr><th>Kabar</th><th>Pelapor berbeda</th><th>Pertama terlihat</th><th>Terakhir terlihat</th></tr></thead><tbody>${data.emerging_rumours.length ? data.emerging_rumours.map((item) => `<tr><td>${esc(item.text)}</td><td class="numeric">${item.count}</td><td class="date-cell">${esc(formatDate(item.first_seen))}</td><td class="date-cell">${esc(formatDate(item.last_seen))}</td></tr>`).join("") : '<tr><td colspan="4" class="empty-state">Belum ada kabar yang melewati ambang.</td></tr>'}</tbody>`;
  $("#top-table").innerHTML = `<thead><tr><th>ID bantahan</th><th>Kategori</th><th class="numeric">Cek</th></tr></thead><tbody>${data.top_debunks.length ? data.top_debunks.map((item) => `<tr><td>${esc(item.debunk_id)}</td><td>${esc(KATEGORI[item.kategori] || item.kategori)}</td><td class="numeric">${esc(item.n)}</td></tr>`).join("") : '<tr><td colspan="3" class="empty-state">Belum ada data.</td></tr>'}</tbody>`;
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "#";
  } catch { return "#"; }
}

function renderCoverage() {
  const data = state.coverage;
  if (!data) return;
  const live = Math.round((data.live_share || 0) * 100);
  const delay = data.seen_delay_s_median == null ? "—" : `${Math.round(data.seen_delay_s_median / 60)} mnt`;
  $("#coverage-summary").innerHTML = [
    [`${data.sources_total || 0}`, "Sumber dalam pemantauan"],
    [`${live}%`, "Feed berstatus hidup"],
    [delay, "Median jeda penemuan item"],
  ].map(([value, label]) => `<div class="coverage-stat"><b>${esc(value)}</b><span>${esc(label)}</span></div>`).join("");
  $("#coverage-table").innerHTML = `<thead><tr><th>Sumber</th><th>Jenis</th><th>Status</th><th>Item / jam</th><th>Kendala</th></tr></thead><tbody>${(data.sources || []).map((source) => `<tr><td>${esc(source.name)}</td><td>${esc(source.kind_label)}</td><td><span class="feed-status ${esc(source.status)}">${esc(source.status)}</span></td><td class="numeric">${esc(source.items_per_hour ?? "—")}</td><td>${esc(source.last_error || "—")}</td></tr>`).join("")}</tbody>`;
  $("#blind-spots").innerHTML = (data.blind_spots || []).map((spot) => `<div class="blind-spot"><b>${esc(spot.name)}</b><span>Tingkat ${esc(spot.tier)}</span><p>${esc(spot.reason)}</p></div>`).join("") || '<p class="empty-state">Belum ada catatan titik buta.</p>';
  $("#recent-items").innerHTML = (state.recent?.items || []).map((item) => `<div class="recent-item"><a href="${esc(safeUrl(item.url))}" target="_blank" rel="noopener noreferrer">${esc(item.title)}</a><small>${esc(item.source_id)} · ${esc(formatDate(item.first_seen, true))}</small></div>`).join("") || '<p class="empty-state">Belum ada item feed.</p>';
}

function switchView(view) {
  state.view = view;
  if (view === "brief") loadBrief();
  document.querySelectorAll(".dashboard-view").forEach((element) => element.classList.toggle("hidden", element.id !== `view-${view}`));
  document.querySelectorAll(".nav-item").forEach((button) => {
    const active = button.dataset.view === view;
    button.classList.toggle("active", active);
    if (active) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  const element = $(`#view-${view}`);
  element.classList.remove("view-enter");
  void element.offsetWidth;
  element.classList.add("view-enter");
  window.scrollTo({ top: 0, behavior: "auto" });
}

function openTicket(id) {
  const item = state.reviews[state.type].items.find((entry) => entry.id === id);
  if (!item) return;
  state.currentTicket = item;
  const closed = item.status === "selesai";
  const isAppeal = state.type === "appeals";
  const supported = !isAppeal && ["telegram", "whatsapp"].includes(item.channel);
  const subject = isAppeal ? item.reason || "Tidak ada catatan tambahan." : item.claim;
  $("#ticket-detail").innerHTML = `<p class="section-kicker">${isAppeal ? "Banding hasil" : "Eskalasi pemeriksaan"}</p><h2>Tiket #${item.id}</h2><div class="ticket-detail-meta"><span>${closed ? "Selesai" : "Perlu ditangani"}</span><span>${esc(formatDate(item.created, true))}</span><span>Kanal: ${esc(item.channel || "web / banding")}</span></div>
    <div class="detail-block"><h3>${isAppeal ? "Catatan pengaju" : "Klaim yang perlu diperiksa"}</h3><p>${esc(subject)}</p></div>
    ${item.debunk_id ? `<div class="detail-block"><h3>Rujukan bantahan</h3><p>${esc(item.debunk_id)}</p><a href="https://github.com/Ardelyo/halio/blob/main/data/debunks.json" target="_blank" rel="noopener noreferrer">Buka korpus bersumber ↗</a></div>` : ""}
    <div class="detail-block"><h3>ID pemeriksaan</h3><p>${esc(item.check_id)}</p></div>`;
  const response = $("#analyst-response");
  response.value = "";
  response.disabled = closed;
  response.placeholder = closed ? "Tiket ini sudah diselesaikan." : "Tulis jawaban, dasar pemeriksaan, dan langkah yang dapat dilakukan penerima…";
  $("#response-count").textContent = "0 / 2.000";
  $("#send-option").classList.toggle("hidden", !supported || STATIC || closed);
  $("#send-response").checked = supported;
  $("#resolve-submit").disabled = closed;
  $("#resolve-submit").innerHTML = closed ? "Tiket sudah selesai" : 'Simpan dan selesaikan <span aria-hidden="true">→</span>';
  $("#resolve-error").classList.add("hidden");
  $("#delivery-note").textContent = closed ? "Respons dan waktu penyelesaian tersimpan pada riwayat di bawah." : STATIC
    ? "Demo lokal: respons hanya dicatat selama sesi ini. Tidak ada pesan yang dikirim."
    : isAppeal ? "Banding tidak memiliki kanal balasan otomatis. Respons akan dicatat pada riwayat."
      : supported ? "Jika pengiriman gagal, tiket tetap terbuka dan respons belum dicatat sebagai penyelesaian."
        : "Kanal web tidak mendukung balasan otomatis. Respons dicatat; tindak lanjut manual tetap diperlukan.";
  renderHistory();
  $("#ticket-dialog").showModal();
}

function renderHistory() {
  const item = state.currentTicket;
  if (!item) return;
  const events = state.reviews[state.type].events.filter((event) => event.item_id === item.id);
  $("#review-history").innerHTML = events.length ? events.map((event) => `<article class="history-item"><p>${esc(event.response)}</p><small>Respons dicatat · ${esc(formatDate(event.created, true))}</small></article>`).join("") : '<p class="history-empty">Belum ada tindakan yang dicatat untuk tiket ini.</p>';
}

async function resolveTicket(event) {
  event.preventDefault();
  const item = state.currentTicket;
  if (!item || item.status === "selesai") return;
  const response = $("#analyst-response").value.trim();
  if (!response) {
    $("#resolve-error").textContent = "Tulis respons sebelum menyelesaikan tiket.";
    $("#resolve-error").classList.remove("hidden");
    return;
  }
  const button = $("#resolve-submit");
  button.disabled = true;
  button.textContent = "Menyimpan…";
  $("#resolve-error").classList.add("hidden");
  try {
    const send = !$("#send-option").classList.contains("hidden") && $("#send-response").checked;
    const result = STATIC
      ? window.HalioDashboardDemo.resolve(state.type, item.id, response)
      : await request(`/api/review/${state.type}/${item.id}/resolve`, { method: "POST", body: JSON.stringify({ response, send }) });
    $("#ticket-dialog").close();
    state.currentTicket = null;
    toast(result.message);
    await loadDashboard();
  } catch (error) {
    $("#resolve-error").textContent = `${error.message} Tiket tetap terbuka.`;
    $("#resolve-error").classList.remove("hidden");
    button.disabled = false;
    button.innerHTML = 'Coba lagi <span aria-hidden="true">→</span>';
  }
}

function openAccess() {
  if (STATIC) return toast("Demo lokal tidak memerlukan token akses.");
  $("#radar-token").value = state.token;
  $("#access-error").classList.add("hidden");
  if (!$("#access-dialog").open) $("#access-dialog").showModal();
}

const BRIEF_ICON = { terbukti_salah: "🔴", sejalan_dengan_sumber: "🟢", dilaporkan_media: "🔵", tidak_yakin: "🟠", belum_ada_pemeriksaan: "⚪" };
state.briefTopic = "tni";

async function loadBrief() {
  if (STATIC) { $("#brief-list").innerHTML = '<p class="brief-meta">Brief harian membutuhkan server Halio dengan sensor dan AI aktif.</p>'; return; }
  $("#brief-meta").textContent = "Memuat brief…";
  try {
    const data = await request(`/api/brief?topic=${encodeURIComponent(state.briefTopic)}`);
    renderBrief(data);
    const running = (data.brief?.narasi || []).some((n) => n.hasil && ["antre", "berjalan"].includes(n.hasil.status));
    clearTimeout(state.briefTimer);
    if (running && state.view === "brief") state.briefTimer = setTimeout(loadBrief, 6000);
  } catch (error) {
    $("#brief-meta").textContent = error.status === 401 ? "Brief memerlukan akses analis (token Radar)." : error.message;
    $("#brief-list").innerHTML = "";
  }
}

function renderBrief(data) {
  const b = data.brief;
  if (!b) {
    $("#brief-meta").textContent = `Belum ada brief untuk ${data.label}. ${data.otomatis ? "Brief otomatis disusun setiap pagi setelah 06.00 WIB." : "Tekan “Susun brief sekarang”."}`;
    $("#brief-list").innerHTML = ""; return;
  }
  $("#brief-meta").textContent = `${b.label} · disusun ${formatDate(b.dibuat, true)} · ${b.berita_dibaca.toLocaleString("id-ID")} berita dibaca dalam ${b.jendela_jam} jam, ${b.berita_cocok_topik.toLocaleString("id-ID")} cocok topik, ${b.narasi.length} narasi.`;
  $("#brief-note").textContent = b.catatan;
  if (!b.narasi.length) { $("#brief-list").innerHTML = '<p class="brief-meta">Tidak ada narasi yang cocok dengan topik ini dalam jendela waktu.</p>'; return; }
  $("#brief-list").innerHTML = b.narasi.map((n, i) => {
    const h = n.hasil;
    let result = "";
    if (n.investigasi) {
      const link = `<a href="laporan.html?id=${encodeURIComponent(n.investigasi)}" target="_blank" rel="noopener">Buka laporan lengkap ↗</a>`;
      if (!h || ["antre", "berjalan"].includes(h.status)) result = `<div class="brief-result"><b>Sedang ditelusuri swarm… (${esc(h?.tahap || "antre")})</b>${link}</div>`;
      else if (h.status === "gagal") result = `<div class="brief-result"><b>Penelusuran gagal.</b>${link}</div>`;
      else result = `<div class="brief-result"><b>${BRIEF_ICON[h.kode_status] || ""} ${esc(h.status_label)}</b>${(h.ringkasan || []).map((s) => `<p>${esc(s)}</p>`).join("")}
        <p class="brief-meta">${h.asal ? `Kemunculan paling awal yang ditemukan: ${esc(h.asal.tanggal)} · ${esc(h.asal.penerbit)} · ` : ""}${esc(h.bukti)} bukti · ${esc(h.dibuka ?? 0)} halaman dibuka</p>${link}</div>`;
    } else if (n.catatan) result = `<div class="brief-result">${esc(n.catatan)}</div>`;
    return `<article class="brief-card"><span class="brief-rank">NARASI ${i + 1} · SKOR ${esc(n.skor)}</span><h3>${esc(n.judul)}</h3>
      <div class="brief-tags"><span>${esc(n.jumlah_berita)} berita</span><span>${esc(n.jumlah_sumber)} sumber</span>${n.jenis_sumber.includes("cek_fakta") ? '<span class="hot">pemeriksa fakta terlibat</span>' : ""}${n.berbau_hoaks ? '<span class="hot">kata hoaks/penipuan</span>' : ""}<span>pertama ${esc(formatDate(n.pertama, true))}</span></div>
      <ul class="brief-heads">${n.berita.map((x) => `<li><a href="${esc(safeUrl(x.url))}" target="_blank" rel="noopener noreferrer">${esc(x.judul)}</a> <small>· ${esc(x.sumber)}</small></li>`).join("")}</ul>${result}</article>`;
  }).join("");
}

async function runBrief() {
  const button = $("#brief-run");
  button.disabled = true;
  try { await request(`/api/brief/run?topic=${encodeURIComponent(state.briefTopic)}`, { method: "POST" }); toast("Brief disusun; tiga narasi teratas sedang ditelusuri."); await loadBrief(); }
  catch (error) { toast(error.status === 401 ? "Perlu akses analis (token Radar)." : error.message, true); }
  finally { button.disabled = false; }
}

function init() {
  document.querySelectorAll("[data-topic]").forEach((button) => {
    button.onclick = () => {
      state.briefTopic = button.dataset.topic;
      document.querySelectorAll("[data-topic]").forEach((item) => { item.classList.toggle("active", item === button); item.setAttribute("aria-pressed", String(item === button)); });
      loadBrief();
    };
  });
  $("#brief-run").onclick = runBrief;
  if (STATIC) $("#demo-notice").classList.remove("hidden");
  document.querySelectorAll(".nav-item").forEach((button) => { button.onclick = () => switchView(button.dataset.view); });
  document.querySelectorAll("[data-go-queue]").forEach((button) => { button.onclick = () => switchView("queue"); });
  document.querySelectorAll("[data-days]").forEach((button) => {
    button.onclick = () => {
      state.days = Number(button.dataset.days);
      document.querySelectorAll("[data-days]").forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-pressed", String(active));
      });
      loadDashboard();
    };
  });
  document.querySelectorAll("[data-type]").forEach((button) => {
    button.onclick = () => {
      state.type = button.dataset.type;
      document.querySelectorAll("[data-type]").forEach((item) => {
        const active = item === button;
        item.classList.toggle("active", active);
        item.setAttribute("aria-selected", String(active));
      });
      renderQueue();
    };
  });
  $("#queue-filter").onchange = (event) => { state.openOnly = event.target.value === "open"; renderQueue(); };
  $("#ticket-list").onclick = (event) => {
    const button = event.target.closest("[data-ticket-id]");
    if (button) openTicket(Number(button.dataset.ticketId));
  };
  $("#ticket-close").onclick = () => $("#ticket-dialog").close();
  $("#ticket-dialog").addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); });
  $("#analyst-response").oninput = (event) => { $("#response-count").textContent = `${event.target.value.length.toLocaleString("id-ID")} / 2.000`; };
  $("#resolve-form").onsubmit = resolveTicket;
  $("#refresh").onclick = loadDashboard;
  $("#access").onclick = openAccess;
  $("#access-close").onclick = () => $("#access-dialog").close();
  $("#access-dialog").addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); });
  $("#access-form").onsubmit = (event) => {
    event.preventDefault();
    state.token = $("#radar-token").value.trim();
    storage.set("halio.radar", state.token);
    $("#access-dialog").close();
    loadDashboard();
  };
  loadDashboard();
}

init();

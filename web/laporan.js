// Halio Telusur report page: start an investigation, follow its progress, render the report for analysts.
const API = window.HALIO_API || "";
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const safeUrl = (u) => { try { const x = new URL(u, location.href); return ["http:", "https:"].includes(x.protocol) ? x.href : "#"; } catch { return "#"; } };
const link = (u, t) => `<a href="${esc(safeUrl(u))}" target="_blank" rel="noopener noreferrer">${esc(t)}</a>`;

const STAGES = [
  ["merencanakan", "Merencanakan kueri pencarian"],
  ["mencari", "Mencari di Google, arsip sensor, ClaimReview, GDELT"],
  ["membuka", "Membuka halaman dan menyalin kutipan (oleh kode)"],
  ["menilai", "AI menilai hubungan tiap kutipan bernomor"],
  ["menelusuri_asal", "Putaran kedua: menelusuri asal-usul"],
  ["menyusun", "Menyusun linimasa dan laporan; kode memeriksa tiap kalimat"],
];
const STATUS_ICON = { terbukti_salah: "🔴", sejalan_dengan_sumber: "🟢", dilaporkan_media: "🔵", tidak_yakin: "🟠", belum_ada_pemeriksaan: "⚪" };
const REL = { refutes: "membantah", supports: "mendukung", context: "konteks", claimreview: "ClaimReview" };
const VIA = { halaman: "halaman", sensor: "sensor Halio", gdelt: "GDELT", claimreview: "ClaimReview", wayback: "Internet Archive" };

function show(id) { for (const s of ["#start", "#progress", "#error", "#report"]) $(s).classList.toggle("hidden", s !== id); }

function fail(text, retry = false) {
  $("#error").innerHTML = `<h1>Belum berhasil</h1><p>${esc(text)}</p>${retry ? '<button class="lp-primary" type="button" id="again">Coba lagi</button>' : ""}`;
  show("#error");
  const again = $("#again");
  if (again) again.onclick = () => { history.replaceState(null, "", location.pathname); init(); };
}

async function start(text) {
  $("#go").disabled = true;
  try {
    const body = { text, channel: "web" };
    const file = $("#photo")?.files?.[0];
    if (file) {
      if (file.size > 6_000_000) throw new Error("Foto terlalu besar (maksimal 6 MB).");
      const bytes = new Uint8Array(await file.arrayBuffer());
      let bin = "";
      for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
      body.image_b64 = btoa(bin); body.mime = file.type || "image/jpeg";
      if (text.length < 10) body.text = "Foto tanpa tulisan yang diteruskan pengguna";
    }
    const r = await fetch(`${API}/api/investigate`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || r.statusText);
    history.replaceState(null, "", `?id=${data.id}`);
    poll(data.id);
  } catch (e) { fail(e.message, true); }
  finally { $("#go").disabled = false; }
}

function renderProgress(job) {
  const idx = Math.max(0, STAGES.findIndex(([k]) => k === job.tahap));
  $("#stages").innerHTML = STAGES.map(([k, label], i) => `<li class="${i < idx ? "done" : i === idx ? "now" : ""}">${esc(label)}</li>`).join("");
  const p = job.progres || {};
  const c = [["kueri", "kueri"], ["kandidat", "kandidat URL"], ["dibuka", "halaman dibuka"], ["kutipan", "kutipan disalin"], ["dinilai", "kutipan dinilai"], ["detik", "detik"]];
  $("#counters").innerHTML = c.map(([k, l]) => `<div><b>${esc(p[k] ?? 0)}</b><small>${esc(l)}</small></div>`).join("");
}

async function poll(id) {
  show("#progress");
  renderProgress({ tahap: "merencanakan" });
  for (let i = 0; i < 200; i++) {
    let job;
    try {
      const r = await fetch(`${API}/api/investigate/${encodeURIComponent(id)}`);
      if (r.status === 404) return fail("Laporan tidak ditemukan. Mungkin tautannya salah.");
      job = await r.json();
    } catch { await new Promise((ok) => setTimeout(ok, 3000)); continue; }
    if (job.status === "selesai") return renderReport(job.laporan, job);
    if (job.status === "gagal") return fail(`Penelusuran berhenti (${job.galat || "galat"}). Biaya model tidak terpakai sia-sia: coba lagi.`, true);
    renderProgress(job);
    await new Promise((ok) => setTimeout(ok, 2000));
  }
  fail("Penelusuran terlalu lama. Muat ulang halaman ini nanti.");
}

function sentences(list) {
  return (list || []).map((s) => `<p class="s">${esc(s.teks)}${s.sumber.map((n) => `<a class="cite" href="#b${n}">[${n}]</a>`).join("")}</p>`).join("");
}

let VIEW = new URLSearchParams(location.search).get("tampilan") === "keluarga" ? "keluarga" : "analis";
let LAST = null;

function toggleBar() {
  return `<div class="lp-toggle" role="group" aria-label="Pilih tampilan"><button type="button" data-view="keluarga" aria-pressed="${VIEW === "keluarga"}">Tampilan keluarga</button><button type="button" data-view="analis" aria-pressed="${VIEW === "analis"}">Tampilan analis</button></div>`;
}

function wireToggle() {
  document.querySelectorAll("[data-view]").forEach((b) => {
    b.onclick = () => {
      VIEW = b.dataset.view;
      const q = new URLSearchParams(location.search); q.set("tampilan", VIEW); history.replaceState(null, "", `?${q}`);
      renderReport(...LAST);
    };
  });
  const listen = $("#listen");
  if (listen) listen.onclick = () => {
    if (!("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(LAST[0].keluarga?.suara || "");
    u.lang = "id-ID"; u.rate = 0.9;
    speechSynthesis.speak(u);
  };
}

function renderFamily(r) {
  const f = r.keluarga || {};
  const g = r.gambar;
  return `${toggleBar()}<article class="fam">
    <p class="fam-kicker">Hasil penelusuran Halio</p>
    <h1 class="fam-head ${esc(r.status)}">${STATUS_ICON[r.status] || ""} ${esc(f.judul || r.status_label)}</h1>
    <p class="fam-claim">Kabar yang diperiksa: “${esc(r.klaim)}”</p>
    <button id="listen" class="lp-primary fam-listen" type="button">🔊 Dengarkan</button>
    ${(f.poin || []).length ? `<h2>Yang perlu diketahui</h2><ul class="fam-list">${f.poin.map((p) => `<li>${esc(p)}</li>`).join("")}</ul>` : ""}
    ${f.sejak ? `<p class="fam-line">🕰 ${esc(f.sejak)}</p>` : ""}
    ${(f.pembantah || []).length ? `<p class="fam-line">🛡 Yang sudah membantah: <b>${f.pembantah.map(esc).join(", ")}</b></p>` : ""}
    ${g ? `<p class="fam-line">🖼 Foto yang sama ditemukan di ${esc(g.halaman_sama + g.halaman_mirip)} halaman${g.paling_awal ? `, paling awal ${esc(g.paling_awal.tanggal)}` : ""}.</p>` : ""}
    <div class="fam-advice"><b>Sebaiknya</b><p>${esc(f.saran || "")}</p></div>
    <p class="lp-muted">Halio membuka ${esc(r.metode?.dibuka ?? 0)} halaman untuk menyusun ini. Halio membantu memeriksa, bukan menggantikan penilaian Anda.</p>
  </article>`;
}

function renderReport(r, job) {
  LAST = [r, job];
  if (VIEW === "keluarga") {
    $("#report").innerHTML = renderFamily(r);
    show("#report");
    wireToggle();
    return;
  }
  const m = r.metode || {};
  const a = r.asal;
  const bar = "■".repeat(r.kekuatan || 0) + "□".repeat(4 - (r.kekuatan || 0));
  const html = [];
  html.push(toggleBar());
  html.push(`<header class="lp-head"><div class="lp-kicker">Laporan Halio Telusur · ${esc(job.dibuat || r.dibuat)}</div>
    <p class="lp-claim">“${esc(r.klaim)}”</p>
    ${r.inti ? `<p class="lp-muted">Inti klaim yang dicari: ${esc(r.inti)}</p>` : ""}
    <span class="lp-chip ${esc(r.status)}">${STATUS_ICON[r.status] || ""} ${esc(r.status_label)}</span><span class="lp-strength">kekuatan bukti ${bar} ${esc(r.kekuatan)}/4</span>
    <p>${esc(r.alasan)}</p>
    <div class="lp-stats"><span>${esc(m.kueri)} kueri</span><span>${esc(m.kandidat)} kandidat URL</span><span>${esc(m.dibuka)} halaman dibuka</span><span>${esc(m.gagal)} gagal dibuka</span><span>${esc(m.kutipan)} kutipan</span><span>${esc(m.detik)} detik</span></div>
    ${(r.klaim_lain || []).length ? `<p class="lp-muted">Klaim lain dalam pesan (tidak ditelusuri di laporan ini): ${r.klaim_lain.map(esc).join(" · ")}</p>` : ""}
  </header>`);
  const L = r.laporan || {};
  if ((L.ringkasan || []).length) html.push(`<section class="lp-sec"><h2>Ringkasan</h2>${sentences(L.ringkasan)}</section>`);
  if ((L.temuan || []).length || (L.konteks || []).length) html.push(`<section class="lp-sec"><h2>Temuan dan konteks</h2>${sentences(L.temuan)}${sentences(L.konteks)}</section>`);
  if (a) {
    const f = a.pertama, t = a.tanggapan_pertama;
    html.push(`<section class="lp-sec"><h2>Asal-usul yang ditemukan</h2>
      <p><b>Kemunculan paling awal:</b> ${esc(f.tanggal)} · ${esc(f.penerbit)} (${esc(VIA[f.asal] || f.asal)}) · ${link(f.url, f.judul || f.url)}</p>
      ${t ? `<p><b>Tanggapan pertama sumber resmi / pemeriksa fakta:</b> ${esc(t.tanggal)} · ${esc(t.penerbit)} · ${link(t.url, t.judul || t.url)}</p>` : "<p>Belum ditemukan tanggapan sumber resmi atau pemeriksa fakta yang bertanggal.</p>"}
      <p class="lp-muted">${esc(a.catatan)}</p></section>`);
  }
  if (r.gambar) {
    const g = r.gambar, f = g.paling_awal;
    html.push(`<section class="lp-sec"><h2>Pencarian gambar terbalik</h2>
      <p>${esc(g.halaman_sama)} halaman memuat gambar yang sama persis, ${esc(g.halaman_mirip)} memuat gambar mirip; ${esc(g.dibuka)} dibuka.</p>
      ${f ? `<p><b>Kemunculan gambar paling awal yang ditemukan:</b> ${esc(f.tanggal)} · ${link(f.url, f.judul || f.host)}</p>` : ""}
      ${(g.label || []).length ? `<p>Tebakan Vision: ${g.label.map(esc).join(", ")}${(g.entitas || []).length ? ` · entitas: ${g.entitas.map(esc).join(", ")}` : ""}</p>` : ""}
      <p class="lp-muted">${esc(g.catatan)}</p></section>`);
  }
  if ((r.agen || []).length) {
    html.push(`<section class="lp-sec"><h2>Swarm agen (${r.agen.length} bekerja paralel)</h2><div class="lp-agents">${r.agen.map((a) =>
      `<div><b>${esc(a.nama)}</b><small>${esc(a.tugas)}</small><span>${esc(a.kueri)} kueri · ${esc(a.temuan)} temuan · ${esc(a.halaman_relevan)} halaman relevan</span></div>`).join("")}</div>
      <p class="lp-muted">Semua agen mengisi satu kumpulan bukti bersama yang dideduplikasi. Vonis tetap diputuskan aturan kode.</p></section>`);
  }
  if ((r.linimasa || []).length) {
    html.push(`<section class="lp-sec"><h2>Linimasa (${r.linimasa.length})</h2><ol class="lp-line">${r.linimasa.map((e) =>
      `<li class="${esc(e.tingkat)}"><time>${esc(e.tanggal)}</time>${link(e.url, e.judul || e.url)}<small>${esc(e.penerbit)} · ${esc(VIA[e.asal] || e.asal)}${e.catatan ? " · " + esc(e.catatan) : ""}</small></li>`).join("")}</ol></section>`);
  }
  if ((r.bukti || []).length) {
    html.push(`<section class="lp-sec"><h2>Bukti bernomor (${r.bukti.length})</h2><p class="lp-muted">Kutipan disalin langsung dari halaman oleh kode. Hubungan dinilai AI; status diputuskan aturan kode.</p><ol class="lp-ev">${r.bukti.map((b) =>
      `<li id="b${b.no}" class="${esc(b.hubungan)}"><span class="who">[${b.no}] ${esc(b.penerbit)}</span><span class="rel">${esc(REL[b.hubungan] || b.hubungan)}</span>
       <div class="meta">${esc(b.tingkat_label)}${b.tanggal ? " · " + esc(b.tanggal) : ""} · ${link(b.url, b.host || b.url)}</div><blockquote>“${esc(b.kutipan)}”</blockquote></li>`).join("")}</ol></section>`);
  }
  if ((r.varian || []).length) {
    html.push(`<section class="lp-sec"><h2>Versi kalimat yang beredar</h2><ul class="lp-list">${r.varian.map((v) =>
      `<li>“${esc(v.contoh)}” <span class="lp-muted">· ${esc(v.jumlah_situs)} situs${v.paling_awal ? " · paling awal " + esc(v.paling_awal) : ""} · ${v.situs.map(esc).join(", ")}</span></li>`).join("")}</ul></section>`);
  }
  if (r.cakupan) {
    html.push(`<section class="lp-sec"><h2>Cakupan sumber (suara berbeda)</h2><div class="lp-grid">${Object.values(r.cakupan).map((c) => `<div><b>${esc(c.suara)}</b>${esc(c.label)}</div>`).join("")}</div>
      <p class="lp-muted">Media satu grup atau salinan kantor berita yang sama dihitung satu suara.</p></section>`);
  }
  if ((r.bacaan || []).length) {
    html.push(`<section class="lp-sec"><h2>Halaman relevan untuk dibaca (${r.bacaan.length})</h2><ul class="lp-list">${r.bacaan.map((p) =>
      `<li>${link(p.url, p.judul)} <span class="lp-muted">· ${esc(p.tingkat_label)} · ${esc(p.host)}${p.tanggal ? " · " + esc(p.tanggal) : ""}</span></li>`).join("")}</ul></section>`);
  }
  html.push(`<section class="lp-sec"><h2>Titik buta</h2><ul class="lp-list">${(r.titik_buta || []).map((s) => `<li>${esc(s)}</li>`).join("")}</ul></section>`);
  const k = m.kalimat || {};
  html.push(`<section class="lp-sec"><details class="lp-method"><summary>Metodologi dan anggaran</summary>
    <p>${esc(r.catatan)}</p>
    <p>Kalimat laporan: ${esc(k.ditulis ?? 0)} ditulis AI, ${esc(k.dibuang ?? 0)} dibuang oleh pemeriksa kode${k.model === false ? " (AI penulis tidak tersedia; ringkasan berisi kutipan apa adanya)" : ""}.</p>
    <p>Anggaran: ${esc(m.anggaran?.kueri)} kueri, ${esc(m.anggaran?.halaman)} halaman, ${esc(m.anggaran?.detik)} detik. Sumber kandidat: ${(m.sumber_kandidat || []).map(esc).join(", ")}.</p>
    <p>Gagal dibuka: ${Object.entries(m.gagal_rinci || {}).map(([x, n]) => `${esc(x)} ${esc(n)}`).join(", ") || "tidak ada"}.</p>
    <p>Kueri yang dijalankan:</p><ol class="lp-list">${(m.daftar_kueri || []).map((q) => `<li>${esc(q)}</li>`).join("")}</ol></details></section>`);
  $("#report").innerHTML = html.join("");
  show("#report");
  wireToggle();
  document.title = `Telusur: ${r.klaim.slice(0, 60)} — Halio`;
}

async function version() {
  try { const h = await (await fetch(`${API}/health`)).json(); $("#version").textContent = `Halio v${h.version} · build ${h.build || "lokal"}`; } catch { /* footer stays empty */ }
}

function init() {
  $("#print").onclick = () => window.print();
  if (window.HALIO_STATIC_DEMO) return fail("Halio Telusur membutuhkan server Halio (pencarian web sungguhan). Halaman ini sedang dibuka sebagai demo statis.");
  version();
  const q = new URLSearchParams(location.search);
  if (q.get("id")) return poll(q.get("id"));
  show("#start");
  if (q.get("q")) $("#claim").value = q.get("q");
  if (q.get("q") && q.get("mulai") === "1") return start(q.get("q"));
  $("#go").onclick = () => {
    const t = $("#claim").value.trim();
    if (t.length >= 10 || $("#photo")?.files?.length) start(t);
    else fail("Tulis klaimnya (minimal 10 huruf) atau pilih foto.", true);
  };
}
init();

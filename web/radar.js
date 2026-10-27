// Radar dashboard: aggregate, k-anonymous trends from /api/radar.
const API = window.HALIO_API || "";

const KATEGORI = {
  penipuan_bansos: "Penipuan bansos", penipuan_catut_tni: "Penipuan mencatut TNI", bencana: "Bencana",
  kesehatan: "Kesehatan", phishing: "Phishing / pencurian data", keamanan_publik: "Keamanan publik",
  claimreview: "Pemeriksa fakta lain",
};
const TECH = {
  ajakan_sebar: "Desakan menyebarkan", urgensi: "Dibuat terburu-buru", otoritas_palsu: "Mengaku orang penting",
  rasa_takut: "Menakut-nakuti", iming_iming: "Iming-iming hadiah", minta_data_uang: "Minta data atau uang",
};
const STATUS = [
  ["terbukti_salah", "🔴 Terbukti salah"], ["tidak_yakin", "🟠 Tidak yakin"], ["belum_ada_pemeriksaan", "⚪ Belum ada pemeriksaan"],
];

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const num = (n) => (typeof n === "number" ? n : 0);

const tip = Object.assign(document.createElement("div"), { className: "tip hidden" });
document.body.appendChild(tip);
function hover(el, text) {
  el.addEventListener("pointermove", (e) => {
    tip.textContent = text; tip.classList.remove("hidden");
    tip.style.left = Math.min(e.clientX + 12, innerWidth - tip.offsetWidth - 8) + "px";
    tip.style.top = e.clientY - 36 + "px";
  });
  el.addEventListener("pointerleave", () => tip.classList.add("hidden"));
}

function bars(el, rows) {
  const max = Math.max(1, ...rows.map((r) => num(r.n)));
  el.innerHTML = rows.length ? "" : `<p class="note">Belum ada data.</p>`;
  for (const r of rows) {
    const row = document.createElement("div");
    row.className = "barrow";
    row.innerHTML = `<span>${esc(r.label)}${r.tag ? `<span class="tag">${esc(r.tag)}</span>` : ""}</span>
      <span class="bartrack"><span class="bar" style="display:block;width:${(num(r.n) / max) * 100}%"></span></span>
      <span class="n">${esc(r.n)}</span>`;
    hover(row, `${r.label}: ${r.n} cek`);
    el.appendChild(row);
  }
}

async function load() {
  let token = null;
  try { token = localStorage.getItem("halio.radar"); } catch { /* storage blocked */ }
  let r = await fetch(API + "/api/radar", { headers: token ? { Authorization: "Bearer " + token } : {} });
  if (r.status === 401) {
    token = prompt("Radar memerlukan token akses:");
    try { localStorage.setItem("halio.radar", token); } catch { /* storage blocked */ }
    r = await fetch(API + "/api/radar", { headers: { Authorization: "Bearer " + token } });
  }
  const d = await r.json();

  $("#window").textContent = `${d.window_days} hari terakhir (sejak ${d.since})`;
  if (d.demo_events) {
    const demo = $("#demo");
    demo.textContent = `⚠️ Termasuk ${d.demo_events} dari ${d.total_checks} cek berupa data simulasi untuk demonstrasi prototipe.`;
    demo.classList.remove("hidden");
  }

  $("#tiles").innerHTML = [["Total cek", d.total_checks], ...STATUS.map(([k, label]) => [label, d.by_status[k] || 0]),
    ["Banding terbuka", d.open_appeals], ["Antre pemeriksa manusia", d.open_escalations]]
    .map(([k, v]) => `<div class="tile"><div class="k">${esc(k)}</div><div class="v">${esc(v)}</div></div>`).join("");

  bars($("#kategori"), d.by_kategori.map((x) => ({
    label: KATEGORI[x.kategori] || x.kategori, n: x.n, tag: x.kategori === "penipuan_catut_tni" ? "TNI AD" : "",
  })));
  bars($("#techniques"), Object.entries(d.techniques).map(([k, n]) => ({ label: TECH[k] || k, n })));

  const perDay = {};
  for (const row of d.daily) perDay[row.day] = (perDay[row.day] || 0) + row.n;
  const days = [];
  for (let t = new Date(d.since + "T00:00:00Z"); days.length < d.window_days; t.setUTCDate(t.getUTCDate() + 1)) {
    days.push(t.toISOString().slice(0, 10));
  }
  const max = Math.max(1, ...Object.values(perDay));
  $("#daily").innerHTML = "";
  for (const day of days) {
    const col = Object.assign(document.createElement("div"), { className: "col" });
    col.style.height = ((perDay[day] || 0) / max) * 100 + "%";
    hover(col, `${day}: ${perDay[day] || 0} cek`);
    $("#daily").appendChild(col);
  }
  $("#d0").textContent = days[0];
  $("#d1").textContent = days[days.length - 1];
  $("#dailytable").innerHTML = "<tr><th>Tanggal</th><th>Cek</th></tr>" +
    days.map((day) => `<tr><td>${day}</td><td class="num">${perDay[day] || 0}</td></tr>`).join("");

  $("#k").textContent = d.k_anonymity;
  $("#belowk").textContent = d.rumours_below_k ? `${d.rumours_below_k} kabar lain masih di bawah ambang dan isinya tidak disimpan.` : "";
  $("#emerging").innerHTML = d.emerging_rumours.length
    ? "<tr><th>Kabar</th><th>Pelapor</th><th>Pertama terlihat</th></tr>" + d.emerging_rumours.map((x) =>
      `<tr><td>${esc(x.text)}</td><td class="num">${x.count}</td><td>${esc(x.first_seen)}</td></tr>`).join("")
    : `<tr><td class="note">Belum ada kabar baru yang melewati ambang.</td></tr>`;
  $("#top").innerHTML = d.top_debunks.length
    ? "<tr><th>Bantahan</th><th>Kategori</th><th>Cek</th></tr>" + d.top_debunks.map((x) =>
      `<tr><td>${esc(x.debunk_id)}</td><td>${esc(KATEGORI[x.kategori] || x.kategori)}</td><td class="num">${esc(x.n)}</td></tr>`).join("")
    : `<tr><td class="note">Belum ada data.</td></tr>`;
}

load().catch((e) => { console.error(e); $("#tiles").innerHTML = `<p class="note">Radar tidak bisa dimuat.</p>`; });

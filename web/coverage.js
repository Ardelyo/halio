// Sensor coverage panel: which sources are watched, how fresh, and the declared blind spots.
const API = window.HALIO_API || "";
const REFRESH_MS = 30000;

const STATUS_LABEL = { hidup: "● Hidup", basi: "◐ Basi", tertunda: "◌ Tertunda", mati: "✕ Mati", belum: "○ Belum" };

const $ = (s) => document.querySelector(s);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function age(sec) {
  if (sec == null) return "—";
  if (sec < 90) return `${Math.round(sec)} dtk`;
  if (sec < 5400) return `${Math.round(sec / 60)} mnt`;
  if (sec < 172800) return `${Math.round(sec / 3600)} jam`;
  return `${Math.round(sec / 86400)} hari`;
}

async function get(path) {
  let token = null;
  try { token = localStorage.getItem("halio.radar"); } catch { /* storage blocked */ }
  let r = await fetch(API + path, { headers: token ? { Authorization: "Bearer " + token } : {} });
  if (r.status === 401) {
    token = prompt("Halaman ini memerlukan token akses:");
    try { localStorage.setItem("halio.radar", token); } catch { /* storage blocked */ }
    r = await fetch(API + path, { headers: { Authorization: "Bearer " + token } });
  }
  if (!r.ok) throw new Error(path + " " + r.status);
  return r.json();
}

function render(c, recent) {
  $("#gen").textContent = "diperbarui " + new Date(c.generated).toLocaleTimeString("id-ID");
  $("#off").classList.toggle("hidden", c.polling);
  $("#disclaimer").textContent = c.disclaimer;

  const tile = (k, v) => `<div class="tile"><div class="k">${esc(k)}</div><div class="v">${esc(v)}</div></div>`;
  $("#tiles").innerHTML = [
    tile("Sumber terdaftar", c.sources_total),
    tile("Hidup sekarang", `${c.counts.hidup} (${Math.round(c.live_share * 100)}%)`),
    tile("Basi / mati / tertunda", `${c.counts.basi} / ${c.counts.mati} / ${c.counts.tertunda}`),
    tile("Median keterlambatan lihat", c.seen_delay_s_median == null ? "—" : age(c.seen_delay_s_median)),
  ].join("");

  const rows = c.sources.map((s) => `<tr>
    <td>${esc(s.name)}<div class="note">${esc(s.kind_label)}${s.notes ? " · " + esc(s.notes) : ""}</div></td>
    <td><span class="st ${esc(s.status)}">${STATUS_LABEL[s.status] || esc(s.status)}</span>${s.last_error ? `<div class="note">${esc(s.last_error)}</div>` : ""}</td>
    <td class="num">${age(s.newest_item_age_s)}</td>
    <td class="num">${s.items_per_hour == null ? "—" : s.items_per_hour}</td>
    <td class="num">${s.latency_ms_median == null ? "—" : Math.round(s.latency_ms_median) + " ms"}</td>
    <td class="num">${s.seen_delay_s_median == null ? "—" : age(s.seen_delay_s_median)}</td></tr>`).join("");
  $("#sources").innerHTML = `<tr><th>Sumber</th><th>Status</th><th>Isi terbaru</th><th>Item/jam</th><th>Respons</th><th>Keterlambatan lihat</th></tr>` + rows;

  $("#blind").innerHTML = c.blind_spots.map((b) =>
    `<li><b>${esc(b.name)}</b> <span class="st belum">${b.tier === "C" ? "tidak mungkin" : "butuh izin/anggaran"}</span><div class="note">${esc(b.reason)}</div></li>`).join("");

  $("#recent").innerHTML = recent.items.length
    ? recent.items.slice(0, 15).map((i) => `<li><a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(i.title)}</a><div class="note">${esc(i.source_id)} · terlihat ${esc(i.first_seen.slice(11, 19))} UTC</div></li>`).join("")
    : `<li class="note">Belum ada judul baru yang tercatat.</li>`;
}

async function load() {
  const [c, recent] = await Promise.all([get("/api/sensor/coverage"), get("/api/sensor/items?limit=15")]);
  render(c, recent);
}

load().catch((e) => { console.error(e); $("#tiles").innerHTML = `<p class="note">Cakupan tidak bisa dimuat.</p>`; });
setInterval(() => load().catch(() => {}), REFRESH_MS);

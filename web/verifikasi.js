// verifikasi keaslian: kirim byte mentah berkas ke POST /api/verify, tampilin SAH / TIDAK SAH
const API = window.HALIO_API || "";
const $ = (s) => document.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let current = null; // { name, bytes: Uint8Array }

async function verify(bytes, label) {
  $("#out").innerHTML = '<p class="lp-muted">Memeriksa…</p>';
  try {
    const resp = await fetch(`${API}/api/verify`, { method: "POST", body: bytes, headers: { "Content-Type": "application/octet-stream" } });
    const r = await resp.json();
    if (!resp.ok) throw new Error(r.detail || resp.statusText);
    const sum = r.ringkasan ? `<pre class="sum">${esc(JSON.stringify(r.ringkasan, null, 1))}</pre>` : "";
    $("#out").innerHTML = `<div class="verdict ${r.sah ? "ok" : "bad"}"><h2>${r.sah ? "✓ SAH" : "✕ TIDAK SAH / DIMODIFIKASI"}</h2>${label ? `<small>${esc(label)}</small><br>` : ""}${esc(r.alasan)}${sum}</div>`;
  } catch (e) {
    $("#out").innerHTML = `<div class="verdict bad"><h2>Belum berhasil</h2>${esc(e.message)}</div>`;
  }
}

async function load(file) {
  if (!file) return;
  current = { name: file.name, bytes: new Uint8Array(await file.arrayBuffer()) };
  $("#actions").hidden = false;
  verify(current.bytes, file.name);
}

// simulasi pemalsuan: balik satu bit di tengah berkas, lalu minta server menilai ulang
function tamper() {
  if (!current) return;
  const b = current.bytes.slice();
  b[Math.floor(b.length / 2)] ^= 1;
  verify(b, `${current.name} (1 byte diubah)`);
}

async function init() {
  if (window.HALIO_STATIC_DEMO) {
    $("#drop").outerHTML = '<p>Verifikasi memanggil server Halio. Halaman ini dibuka sebagai demo statis, jadi tidak bisa dijalankan. Gunakan <code>python -m halio.verify</code>.</p>';
    return;
  }
  const drop = $("#drop"), input = $("#file");
  drop.onclick = () => input.click();
  drop.onkeydown = (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); } };
  input.onchange = () => load(input.files[0]);
  drop.ondragover = (e) => { e.preventDefault(); drop.classList.add("over"); };
  drop.ondragleave = () => drop.classList.remove("over");
  drop.ondrop = (e) => { e.preventDefault(); drop.classList.remove("over"); load(e.dataTransfer.files[0]); };
  $("#tamper").onclick = tamper;
  try {
    const k = await (await fetch(`${API}/api/pubkey`)).json();
    $("#key").textContent = `Kunci satuan: ${k.alg} · ${k.key_id}`;
    const h = await (await fetch(`${API}/health`)).json(); $("#version").textContent = `Halio v${h.version}`;
  } catch { /* kosongkan saja kl gagal */ }
}
init();

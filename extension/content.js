// lapisan pelindung di feed medsos: lencana "Perlu dicek?" + blur gambar sesuai aturan keluarga
// teks postingan cuma keluar dr perangkat kl user beneran mencet tombol "Cek dengan Halio"
// gambar ga pernah keluar dr perangkatt sama sekali, dicek lokal di offscreen canvas
(() => {
  const { analyze, isJudol, scrub } = globalThis.HalioLexicon;
  const POSTS = '[role="article"], article, [data-halio-post]';
  const DEFAULTS = { badges: true, blurMode: "judol", apiUrl: "http://localhost:8000" };
  let settings = { ...DEFAULTS };

  const send = (msg) => new Promise((resolve) => chrome.runtime.sendMessage(msg, resolve));
  const el = (tag, cls, text) => Object.assign(document.createElement(tag), { className: cls, textContent: text || "" });

  // ---- lencana peringatan teks postingan ----
  function badgePost(post) {
    if (post.dataset.halio) return;
    post.dataset.halio = "1";
    const text = (post.innerText || "").slice(0, 2000);
    if (text.length < 40) return;
    const res = analyze(text);
    if (!res.needsCheck) return;

    const box = el("div", "halio-badge");
    box.append(el("strong", "", "⚠️ Perlu dicek?"),
      el("span", "halio-why", " Pesan ini memakai trik: " + res.techniques.map((t) => t.label.toLowerCase()).join(", ")));
    const btn = el("button", "halio-btn", "Cek dengan Halio");
    btn.addEventListener("click", async (e) => {
      e.preventDefault(); e.stopPropagation();
      btn.disabled = true; btn.textContent = "Mengecek…";
      // bersihin dulu nomor hp, NIK, email, sm link sebelum dikirim ke API
      const r = await send({ type: "check", text: scrub(text) });
      btn.remove();
      box.append(renderResult(r));
    });
    box.append(btn);
    post.prepend(box);
  }

  function renderResult(r) {
    const out = el("div", "halio-result");
    if (!r || r.error) {
      out.textContent = "Halio tidak bisa dihubungi. Pastikan server Halio menyala.";
      return out;
    }
    const icon = { terbukti_salah: "🔴", tidak_yakin: "🟠", belum_ada_pemeriksaan: "⚪" }[r.status];
    out.append(el("b", "", `${icon} ${r.status_label}. `),
      el("span", "", r.match ? r.match.sederhana : r.voice_script));
    if (r.match) {
      const a = el("a", "", " Sumber: " + r.match.sumber[0].nama);
      a.href = r.match.sumber[0].url; a.target = "_blank"; a.rel = "noopener";
      out.append(a);
    }
    return out;
  }

  // ---- saringan & blur gambar di feed ----
  function contextText(img) {
    const link = img.closest("a");
    return [img.alt, img.title, link && link.href, img.parentElement && img.parentElement.innerText.slice(0, 200)].join(" ");
  }

  function hide(img, note) {
    img.classList.add("halio-blur");
    img.dataset.halioNote = note;
    if (!img.previousElementSibling || !img.previousElementSibling.classList.contains("halio-imgnote")) {
      img.before(el("div", "halio-imgnote", note + " · ketuk gambar untuk melihat"));
    }
    img.addEventListener("click", reveal, { capture: true, once: true });
  }

  function reveal(e) {
    e.preventDefault(); e.stopPropagation();
    const img = e.currentTarget;
    img.classList.remove("halio-blur");
    const note = img.previousElementSibling;
    if (note && note.classList.contains("halio-imgnote")) note.remove();
  }

  async function screenImage(img) {
    if (img.dataset.halioImg || settings.blurMode === "off") return;
    // lewatin ikon kecil, avatar profil, atau stiker biar tampilan ga berantakan
    if ((img.naturalWidth || img.width) < 120 && (img.naturalHeight || img.height) < 120) return;
    img.dataset.halioImg = "1";
    send({ type: "stat", key: "imagesChecked" });

    if (isJudol(contextText(img))) return hide(img, "🎰 Konten judi online disembunyikan (aturan keluarga)");
    if (settings.blurMode === "semua") return hide(img, "Gambar disembunyikan (mode semua)");
    if (settings.blurMode !== "pintar") return;

    // jaga-jaga: blur dulu di awal, baru buka lagi kl model lokal udah bilang aman
    img.classList.add("halio-blur");
    const r = await send({ type: "classify", src: img.currentSrc || img.src });
    if (r && r.ok && !r.unsafe) img.classList.remove("halio-blur");
    else if (r && r.ok && r.unsafe) hide(img, "Konten dewasa disembunyikan (aturan keluarga)");
    else hide(img, "Gambar belum bisa diperiksa");
  }

  // ---- pemindaian DOM pas halaman berubah / di-scroll ----
  function scan() {
    if (settings.badges) document.querySelectorAll(POSTS).forEach(badgePost);
    document.querySelectorAll("img").forEach((img) => {
      if (img.complete) screenImage(img);
      else img.addEventListener("load", () => screenImage(img), { once: true });
    });
  }

  // kasih jeda 400ms biar ga berat pas user scroll cepet di linimasa
  let pending = null;
  new MutationObserver(() => {
    clearTimeout(pending);
    pending = setTimeout(scan, 400);
  }).observe(document.documentElement, { childList: true, subtree: true });

  chrome.storage.sync.get(DEFAULTS, (s) => { settings = s; scan(); });
  chrome.storage.onChanged.addListener((changes) => {
    for (const [k, v] of Object.entries(changes)) settings[k] = v.newValue;
  });
})();

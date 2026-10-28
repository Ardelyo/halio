// The 18 scenes of the Halio demo video. Timing comes from timeline.js (narration cues);
// every animation below is keyed to those cue times, so editing the narration re-times the video.
(() => {
  const { el, P, ease, reveal, words, stagger, lerp, clamp, rand, shape, SHAPES, PALETTE, registry: R, cueStart: cs, cueEnd: ce } = Engine;
  const D = window.DATA || {};
  const A = "../assets/";

  // Edit before rendering if the prototype status changes (keep it honest).
  const STATUS = D.status || {
    done: [
      "Cek pesan dengan tiga keadaan dan sumber bernama",
      "Kartu Halio dan pesan suara",
      "Radar agregat dengan k-anonimitas",
      "Sensor 23 feed dan panel cakupan",
      "29 uji otomatis lulus",
    ],
    todo: [
      "Korpus bantahan baru 7 entri",
      "Uji independen: 6 dari 20 kalimat benar masih salah ditandai",
      "Bot Telegram dan WhatsApp belum diuji langsung",
      "Deteksi narasi (klaster) belum dibangun",
    ],
  };

  // ---------- shared builders ----------
  const at = (n, x, y, extra = {}) => Object.assign(n.style, { position: "absolute", left: x + "px", top: y + "px", ...extra });
  function photo(root, file) { return el("div", "photo", null, root, { backgroundImage: `url(${A}${file})` }); }
  function kenBurns(n, lt, dur, from = 1.03, to = 1.09) { n.style.transform = `scale(${lerp(from, to, clamp(lt / dur))})`; }
  function text(root, cls, x, y, html, style = {}) { const n = el("div", cls, null, root); at(n, x, y, style); const sp = words(n, html); return { n, sp }; }
  function block(root, cls, html, x, y, style = {}) { const n = el("div", cls, html, root); at(n, x, y, style); return n; }

  function phoneShot(root, x, y, scale, srcs) {
    const w = 390 * scale, h = 844 * scale;
    const f = el("div", "phone", null, root); at(f, x, y, { width: w + 24 + "px", height: h + 24 + "px" });
    const scr = el("div", "screen", null, f);
    const imgs = srcs.map((s) => { const i = el("img", null, null, scr); i.src = A + "shots/" + s; return i; });
    return { f, imgs, scale, scroll(img, cssY) { img.style.transform = `translateY(${-cssY * scale}px)`; } };
  }
  function browserShot(root, x, y, w, h, src, url, natW) {
    const f = el("div", "browser", null, root); at(f, x, y, { width: w + "px", height: h + "px" });
    const bar = el("div", "bar", null, f); el("b", null, null, bar); el("b", null, null, bar); el("b", null, null, bar);
    el("span", "url", url, bar);
    const view = el("div", "view", null, f, { height: h - 54 + "px" });
    const img = el("img", null, null, view); img.src = A + "shots/" + src;
    const k = w / natW;
    return { f, img, scroll(px) { img.style.transform = `translateY(${-px}px)`; }, k };
  }
  function confetti(root, n, seed, area) {
    const r = rand(seed), items = [];
    for (let i = 0; i < n; i++) {
      const size = 34 + r() * 62;
      const node = el("div", null, shape(SHAPES[i % SHAPES.length], PALETTE[i % PALETTE.length], size), root);
      let x, y;
      do { x = area.x + r() * area.w; y = area.y + r() * area.h; } while (area.avoid && x > area.avoid.x && x < area.avoid.x + area.avoid.w && y > area.avoid.y && y < area.avoid.y + area.avoid.h);
      at(node, x, y);
      items.push({ node, x, y, size, rot: r() * 360, spin: (r() - 0.5) * 30, ph: r() * 6.28, amp: 8 + r() * 16, delay: r() * 0.8 });
    }
    return items;
  }

  // ---------- 0 · Prolog ----------
  R.pembuka = {
    bg: "bg-ink", dark: true,
    build(root, sc) {
      const s = { bg: photo(root, "field-meadow.jpg") };
      el("div", null, null, root, { position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(14,23,38,.18), rgba(14,23,38,.05) 45%, rgba(14,23,38,.25))" });
      // a lone phone in the field (reference: lone desk in a meadow)
      const sh = el("div", null, null, root); at(sh, 830, 712, { width: "260px", height: "46px", borderRadius: "50%", background: "radial-gradient(closest-side, rgba(0,0,0,.42), rgba(0,0,0,0))" });
      const ph = el("div", null, null, root); at(ph, 888, 430, { width: "144px", height: "290px", borderRadius: "28px", background: "#0B1220", padding: "8px", boxShadow: "0 18px 40px rgba(0,0,0,.35)" });
      const scr = el("div", null, null, ph, { width: "100%", height: "100%", borderRadius: "21px", background: "#F8F3F0", position: "relative", overflow: "hidden" });
      el("div", null, null, scr, { position: "absolute", left: "10px", top: "40px", width: "86px", height: "34px", borderRadius: "12px", background: "#fff", boxShadow: "0 2px 6px rgba(0,0,0,.08)" });
      el("div", null, null, scr, { position: "absolute", left: "10px", top: "84px", width: "104px", height: "60px", borderRadius: "12px", background: "#fff", boxShadow: "0 2px 6px rgba(0,0,0,.08)" });
      el("div", null, null, scr, { position: "absolute", right: "10px", top: "156px", width: "70px", height: "30px", borderRadius: "12px", background: "#DCE8F8" });
      s.ph = ph; s.sh = sh;
      const grid = [["SETIAP", "PAGI,", "JUTAAN", "PESAN"], ["DITERUSKAN", "KE", "GRUP", "KELUARGA."]];
      const xs = [190, 610, 1150, 1560];
      s.grid = [];
      grid.forEach((row, ri) => row.forEach((w, ci) => {
        const n = block(root, null, w, xs[ci], 470 + ri * 120, { font: "700 34px/1 Inter", letterSpacing: ".06em", color: "#F8F3F0", textShadow: "0 2px 14px rgba(0,0,0,.3)" });
        s.grid.push(n);
      }));
      s.line = text(root, "serif", 0, 800, "dikirim karena *sayang*.", { width: "1920px", textAlign: "center", fontSize: "104px", color: "#F8F3F0", textShadow: "0 4px 30px rgba(0,0,0,.25)" });
      return s;
    },
    update(t, s, sc) {
      kenBurns(s.bg, t, sc.dur, 1.02, 1.08);
      reveal(s.ph, P(t, 0.2, 1.2), { y: 30, blur: 10 }); reveal(s.sh, P(t, 0.2, 1.2), { y: 0, blur: 0 });
      const a = cs(sc, 0), d = ce(sc, 0) - a;
      s.grid.forEach((n, i) => reveal(n, P(t, a + (i * d) / 8.5, 0.7), { y: 14, blur: 12, max: t > cs(sc, 1) ? lerp(1, 0.45, P(t, cs(sc, 1), 0.8)) : 1 }));
      stagger(s.line.sp, t, cs(sc, 1), 0.14, 0.8);
    },
  };

  // ---------- 1 · Ibu Sri ----------
  R.cerita = {
    bg: "bg-cream",
    build(root) {
      const s = { bg: photo(root, "field-day.jpg") };
      s.pill = block(root, "micro", "Persona ilustratif", 120, 176, { padding: "10px 16px", borderRadius: "999px", background: "rgba(248,243,240,.75)", color: "#0E1726" });
      s.h1 = text(root, "serif", 120, 232, "Bayangkan *Ibu Sri*,", { fontSize: "128px", color: "#0E1726" });
      s.h2 = text(root, "serif", 120, 362, "68 tahun.", { fontSize: "128px", color: "#0E1726" });
      const f = el("div", "phone", null, root); at(f, 1180, 120, { width: "384px", height: "780px" }); s.phone = f;
      const scr = el("div", "screen", null, f, { background: "#EFE8E2" });
      const hd = el("div", null, null, scr, { position: "absolute", left: 0, right: 0, top: 0, height: "112px", background: "#014BAA", padding: "48px 24px 0" });
      el("div", null, "Grup Keluarga Besar", hd, { font: "600 25px/1.1 Inter", color: "#F8F3F0" });
      el("div", null, "Ibu Sri, Tante Yuli, +40 lainnya", hd, { font: "500 16px/1.4 Inter", color: "rgba(248,243,240,.8)", marginTop: "4px" });
      const bub = (top, html, style = {}) => { const b = el("div", null, html, scr); at(b, 14, top, { width: "300px", padding: "14px 16px", borderRadius: "20px", background: "#fff", font: "500 19px/1.35 Inter", color: "#0E1726", boxShadow: "0 2px 6px rgba(0,0,0,.06)", ...style }); return b; };
      s.b1 = bub(132, `<div style="font:600 16px Inter;color:#014BAA">Tante Yuli</div><div style="font:italic 500 14px Inter;color:#6B7486;margin:2px 0 8px">↪ Diteruskan berkali-kali</div>
        <div style="height:150px;border-radius:12px;background:linear-gradient(135deg,#1c2a44,#3a2f2a);position:relative;overflow:hidden">
          <div style="position:absolute;left:50%;top:50%;width:54px;height:54px;margin:-27px;border-radius:50%;background:rgba(248,243,240,.9)"></div>
          <div style="position:absolute;left:50%;top:50%;margin:-12px -6px;border-left:20px solid #0E1726;border-top:12px solid transparent;border-bottom:12px solid transparent"></div>
          <div style="position:absolute;left:10px;bottom:8px;font:700 13px Inter;letter-spacing:.05em;color:#fff">VIDEO · PRESIDEN BAGI-BAGI BANSOS TUNAI</div></div>`);
      s.b2 = bub(392, "Langsung chat WA <b>0812-3456-7890</b> untuk daftar, bayar admin 150rb dulu. SEBARKAN!!");
      s.b3 = bub(552, "Wah, saya teruskan ke grup arisan, ya.", { left: "auto", right: "14px", width: "250px", background: "#DCE8F8" });
      return s;
    },
    update(t, s, sc) {
      kenBurns(s.bg, t, sc.dur);
      reveal(s.pill, P(t, 0.4, 0.6), { y: 10 });
      stagger(s.h1.sp, t, cs(sc, 0) - 0.1, 0.12, 0.8);
      stagger(s.h2.sp, t, cs(sc, 0) + 0.9, 0.12, 0.8);
      reveal(s.phone, P(t, 0.3, 1.1), { x: 80, y: 0, blur: 8 });
      reveal(s.b1, P(t, cs(sc, 1), 0.6, ease.back), { y: 20, blur: 0, scale: 0.94 });
      reveal(s.b2, P(t, cs(sc, 1) + 1.8, 0.6, ease.back), { y: 20, blur: 0, scale: 0.94 });
      reveal(s.b3, P(t, cs(sc, 2) + 1.0, 0.6, ease.back), { y: 20, blur: 0, scale: 0.94 });
    },
  };

  // ---------- 1 · facts ----------
  R.fakta = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      s.h = text(root, "serif", 140, 150, "Itu *bukan* karangan.", { fontSize: "120px" });
      const cols = [["100", "korban"], ["20", "provinsi"], ["65", "juta rupiah kerugian"]];
      s.nums = cols.map(([v, label], i) => {
        const x = [140, 780, 1340][i];
        const num = block(root, "grot", "0", x, 360, { fontSize: "230px", color: "#014BAA" });
        const lab = block(root, "micro", label, x + 6, 610, { color: "#3A4456" });
        return { num, lab, v: +v };
      });
      s.rp = block(root, "micro", "Rp", 1346, 340, { color: "#014BAA", fontSize: "26px" });
      s.desc = block(root, "body", "Video deepfake pejabat negara mengarahkan korban ke WhatsApp, lalu meminta “biaya administrasi” berulang kali.", 140, 700, { width: "1420px", color: "#3A4456" });
      s.src = block(root, "micro", "Sumber · Katadata, mengutip Bareskrim Polri · Februari 2025", 140, 846, { color: "#6B7486" });
      return s;
    },
    update(t, s, sc) {
      stagger(s.h.sp, t, cs(sc, 0) - 0.2, 0.12, 0.8);
      const a = cs(sc, 1) - 0.4;
      s.nums.forEach((c, i) => {
        const p = P(t, a + i * 0.35, 0.9);
        reveal(c.num, p, { y: 40, blur: 16 });
        reveal(c.lab, P(t, a + i * 0.35 + 0.3, 0.6), { y: 10 });
        c.num.textContent = Math.round(c.v * P(t, a + i * 0.35, 1.3, ease.expo));
      });
      reveal(s.rp, P(t, a + 0.9, 0.6), { y: 10 });
      reveal(s.desc, P(t, a + 1.4, 0.8), { y: 16 });
      reveal(s.src, P(t, a + 1.8, 0.6), { y: 8 });
    },
  };

  // ---------- 1 · harm ----------
  R.dampak = {
    bg: "bg-ink", dark: true,
    build(root) {
      const s = {};
      s.l1 = text(root, "serif", 140, 250, "Hoaks tidak hanya *menipu*.", { fontSize: "124px", color: "#F8F3F0" });
      s.kicker = block(root, "micro", "Kendal · 1 November 2018", 146, 430, { color: "#FFC83D" });
      s.l2 = text(root, "serif", 140, 476, "Ia *melukai* orang yang tak bersalah.", { fontSize: "104px", color: "#F8F3F0" });
      s.body = block(root, "body", "Pesan berantai tentang penculik anak berakhir dengan amuk massa terhadap seorang pria yang kemudian diketahui mengalami gangguan jiwa.", 146, 640, { width: "1250px", color: "rgba(248,243,240,.72)", fontSize: "30px" });
      s.src = block(root, "micro", "Sumber · detikNews", 146, 800, { color: "rgba(248,243,240,.5)" });
      return s;
    },
    update(t, s, sc) {
      stagger(s.l1.sp, t, cs(sc, 0) - 0.1, 0.12, 0.8);
      reveal(s.kicker, P(t, cs(sc, 1) - 0.2, 0.6), { y: 8 });
      stagger(s.l2.sp, t, cs(sc, 1) + 0.6, 0.1, 0.8);
      reveal(s.body, P(t, cs(sc, 2), 0.8), { y: 14 });
      reveal(s.src, P(t, cs(sc, 2) + 0.6, 0.6), { y: 6 });
    },
  };

  // ---------- 1 · literacy ----------
  R.literasi = {
    bg: "bg-blue", dark: true,
    build(root) {
      const s = {};
      s.big = block(root, "grot", "4 dari 10", 0, 160, { width: "1920px", textAlign: "center", fontSize: "230px", color: "#F8F3F0" });
      s.figs = [];
      for (let i = 0; i < 10; i++) {
        const on = i < 4;
        const f = el("div", null, null, root); at(f, 290 + i * 140, 470, { width: "90px", height: "170px" });
        el("div", null, null, f, { position: "absolute", left: "17px", top: 0, width: "56px", height: "56px", borderRadius: "50%", background: on ? "#FFC83D" : "transparent", border: on ? "none" : "4px solid rgba(248,243,240,.55)" });
        el("div", null, null, f, { position: "absolute", left: 0, top: "68px", width: "90px", height: "100px", borderRadius: "45px 45px 18px 18px", background: on ? "#FFC83D" : "transparent", border: on ? "none" : "4px solid rgba(248,243,240,.55)" });
        s.figs.push(f);
      }
      s.cap = block(root, null, "orang Indonesia ragu mampu mengenali hoaks", 0, 690, { width: "1920px", textAlign: "center", font: "600 42px/1.2 Inter", color: "#F8F3F0" });
      s.src = block(root, "micro", "Sumber · Status Literasi Digital Indonesia 2023 (40,2%)", 0, 760, { width: "1920px", textAlign: "center", color: "rgba(248,243,240,.6)" });
      s.l1 = text(root, "serif", 0, 170, "Ibu Sri tidak bodoh.", { width: "1920px", textAlign: "center", fontSize: "120px", color: "#F8F3F0" });
      s.l2 = text(root, "serif", 0, 300, "Ia *sendirian*.", { width: "1920px", textAlign: "center", fontSize: "150px", color: "#F8F3F0" });
      return s;
    },
    update(t, s, sc) {
      const b = cs(sc, 1) - 0.2, out = P(t, b, 0.6);
      reveal(s.big, P(t, cs(sc, 0) - 0.4, 0.9) * (1 - out), { y: 30, blur: 16 });
      s.figs.forEach((f, i) => {
        const p = P(t, cs(sc, 0) + i * 0.12, 0.6, ease.back);
        reveal(f, p, { y: 30, blur: 0, scale: 0.6, max: i === 0 ? 1 : lerp(1, 0.22, out) });
        f.style.transform += ` translateY(${out * 140}px)`;
      });
      reveal(s.cap, P(t, cs(sc, 0) + 1.2, 0.7) * (1 - out), { y: 12 });
      reveal(s.src, P(t, cs(sc, 0) + 1.6, 0.6) * (1 - out), { y: 8 });
      stagger(s.l1.sp, t, b + 0.3, 0.12, 0.8);
      stagger(s.l2.sp, t, b + 1.6, 0.18, 0.9);
    },
  };

  // ---------- 2 · cognitive domain ----------
  R.medan = {
    bg: "bg-ink", dark: true,
    build(root) {
      const s = { bg: photo(root, "field-dusk.jpg") };
      const sh = { textShadow: "0 4px 40px rgba(60,20,60,.25)", color: "#F8F3F0" };
      s.k = block(root, "micro", "Kedaulatan kognitif", 0, 280, { width: "1920px", textAlign: "center", letterSpacing: ".4em", color: "#F8F3F0" });
      s.l1 = text(root, "serif", 0, 330, "Ruang pikiran", { width: "1920px", textAlign: "center", fontSize: "150px", ...sh });
      s.l2 = text(root, "serif", 0, 470, "kini menjadi *medan*.", { width: "1920px", textAlign: "center", fontSize: "150px", ...sh });
      s.l3 = text(root, "serif", 0, 690, "Pertahanannya dimulai dari *keluarga*.", { width: "1920px", textAlign: "center", fontSize: "84px", ...sh });
      return s;
    },
    update(t, s, sc) {
      kenBurns(s.bg, t, sc.dur, 1.04, 1.1);
      reveal(s.k, P(t, 0.3, 0.7), { y: 8 });
      const up = P(t, cs(sc, 1) - 0.3, 0.8, ease.inOut);
      stagger(s.l1.sp, t, cs(sc, 0) - 0.2, 0.15, 0.9, { max: lerp(1, 0.72, up) });
      stagger(s.l2.sp, t, cs(sc, 0) + 0.5, 0.15, 0.9, { max: lerp(1, 0.72, up) });
      [s.l1.n, s.l2.n, s.k].forEach((n) => { n.style.marginTop = -60 * up + "px"; });
      stagger(s.l3.sp, t, cs(sc, 1), 0.1, 0.8);
    },
  };

  // ---------- 3 · Halio ----------
  R.halio = {
    bg: "bg-blue", dark: true, noBrand: true,
    build(root) {
      const s = {};
      s.conf = confetti(root, 26, 11, { x: 40, y: 60, w: 1840, h: 900, avoid: { x: 460, y: 60, w: 1000, h: 860 } });
      s.mark = el("img", null, null, root); s.mark.src = A + "halio-mark.svg"; at(s.mark, 845, 150, { width: "230px", height: "230px" });
      s.word = block(root, "serif", 'halio<span style="color:#FFC83D">.</span>', 0, 380, { width: "1920px", textAlign: "center", fontSize: "280px", color: "#F8F3F0" });
      s.tag = block(root, null, "Cek dulu, baru teruskan.", 0, 690, { width: "1920px", textAlign: "center", font: "500 40px/1 Inter", color: "rgba(248,243,240,.9)" });
      const pill = (x, a, b) => { const p = el("div", "pill", `<b style="font-weight:700">${a}</b><span style="opacity:.7;font-weight:500">${b}</span>`, root); at(p, x, 780, { background: "#F8F3F0", color: "#0E1726" }); return p; };
      s.p1 = pill(470, "Halio Keluarga", "cek pesan"); s.p2 = pill(1010, "Halio Sensor", "pantau narasi");
      return s;
    },
    update(t, s, sc) {
      s.conf.forEach((c) => {
        const p = P(t, 0.1 + c.delay, 0.8, ease.back);
        c.node.style.opacity = p;
        c.node.style.transform = `translate(${Math.sin(t * 0.7 + c.ph) * c.amp}px, ${Math.cos(t * 0.6 + c.ph) * c.amp}px) rotate(${c.rot + t * c.spin}deg) scale(${p})`;
      });
      reveal(s.mark, P(t, 0.3, 0.9, ease.back), { y: 0, blur: 0, scale: 0.4 });
      reveal(s.word, P(t, cs(sc, 0) - 0.2, 0.9), { y: 30, blur: 20 });
      reveal(s.tag, P(t, cs(sc, 0) + 0.7, 0.7), { y: 12 });
      reveal(s.p1, P(t, cs(sc, 1) + 0.2, 0.7, ease.back), { y: 24, blur: 0, scale: 0.9 });
      reveal(s.p2, P(t, cs(sc, 1) + 2.6, 0.7, ease.back), { y: 24, blur: 0, scale: 0.9 });
    },
  };

  // ---------- 4 · check a message ----------
  R.cek = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      s.k = block(root, "micro", "Cara pakai · web dan PWA", 146, 190, { color: "#014BAA" });
      s.h = text(root, "serif", 140, 236, "Tempel. Cek. *Paham.*", { fontSize: "124px" });
      const steps = ["Tempel pesan yang meragukan", "Baca jawaban sederhana dan sumbernya", "Kenali trik manipulasinya"];
      s.steps = steps.map((txt, i) => {
        const row = el("div", null, null, root); at(row, 146, 470 + i * 120, { display: "flex", alignItems: "center", gap: "30px" });
        el("div", "grot", "0" + (i + 1), row, { fontSize: "60px", color: "#014BAA", width: "120px" });
        el("div", null, txt, row, { font: "600 36px/1.2 Inter", color: "#0E1726" });
        return row;
      });
      s.ph = phoneShot(root, 1250, 96, 0.9, ["phone-input.png", "phone-result-full.png"]);
      return s;
    },
    update(t, s, sc) {
      reveal(s.k, P(t, 0.3, 0.6), { y: 8 });
      stagger(s.h.sp, t, 0.4, 0.16, 0.8);
      s.steps.forEach((r, i) => {
        const on = P(t, cs(sc, i) - 0.1, 0.6);
        reveal(r, P(t, 0.9 + i * 0.25, 0.7), { y: 16, max: lerp(0.32, 1, on) });
      });
      reveal(s.ph.f, P(t, 0.2, 1.0), { x: 60, y: 0, blur: 8 });
      const sw = P(t, cs(sc, 1) - 0.5, 0.5);
      s.ph.imgs[0].style.opacity = 1 - sw; s.ph.imgs[1].style.opacity = sw;
      const y = lerp(lerp(0, 740, P(t, cs(sc, 1), 1.6, ease.inOut)), 1834, P(t, cs(sc, 2) + 0.4, 2.4, ease.inOut));
      s.ph.scroll(s.ph.imgs[1], y);
    },
  };

  // ---------- 4 · voice note + card ----------
  R.suara = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      const card = el("div", "card", null, root); at(card, 140, 200, { width: "840px", height: "600px" }); s.card = card;
      const play = el("div", null, null, card); at(play, 44, 44, { width: "96px", height: "96px", borderRadius: "50%", background: "#014BAA" });
      el("div", null, null, play, { position: "absolute", left: "38px", top: "30px", borderLeft: "30px solid #F8F3F0", borderTop: "18px solid transparent", borderBottom: "18px solid transparent" });
      el("div", null, "Pesan suara dari Halio", card, { position: "absolute", left: "170px", top: "52px", font: "600 32px Inter" });
      s.time = el("div", null, "0:00", card, { position: "absolute", left: "170px", top: "98px", font: "500 24px Inter", color: "#6B7486" });
      const r = rand(5); s.bars = [];
      for (let i = 0; i < 58; i++) {
        const h = 16 + Math.pow(r(), 1.3) * 96;
        const b = el("div", null, null, card); at(b, 44 + i * 13, 160 + (110 - h) / 2 + 20, { width: "7px", height: h + "px", borderRadius: "4px", background: "#D9D1CB" });
        s.bars.push(b);
      }
      const script = (D.bansos && D.bansos.voice_script) || "Bu, pesan ini sudah dicek dan ternyata tidak benar.";
      const tw = el("div", null, null, card); at(tw, 44, 330, { width: "750px", font: "500 29px/1.45 Inter", color: "#0E1726" });
      s.tw = words(tw, script.split(" ").slice(0, 34).join(" ") + (script.split(" ").length > 34 ? "…" : ""));
      s.kartu = el("img", null, null, root); s.kartu.src = A + "shots/kartu-bansos.png"; at(s.kartu, 1120, 130, { width: "640px", height: "640px", borderRadius: "18px", boxShadow: "0 40px 90px rgba(14,23,38,.25)" });
      s.share = block(root, "pill", "↗&nbsp; Dibagikan ke Grup Keluarga Besar", 1170, 810, { background: "#014BAA", color: "#F8F3F0" });
      return s;
    },
    update(t, s, sc) {
      reveal(s.card, P(t, 0.2, 0.9), { y: 30, blur: 8 });
      const p = P(t, cs(sc, 0), ce(sc, 0) - cs(sc, 0) + 1.2, (x) => x);
      const active = Math.floor(p * s.bars.length);
      s.bars.forEach((b, i) => { b.style.background = i < active ? "#014BAA" : "#D9D1CB"; b.style.transform = i === active ? "scaleY(1.25)" : "none"; });
      s.time.textContent = "0:" + String(Math.round(p * 16)).padStart(2, "0") + " / 0:16";
      s.tw.forEach((w, i) => { w.style.color = i / s.tw.length < p ? "#0E1726" : "#B9B2AD"; });
      reveal(s.kartu, P(t, cs(sc, 1) - 0.3, 0.9, ease.back), { x: 80, y: 0, blur: 0, scale: 0.92, rot: lerp(-8, -3, P(t, cs(sc, 1) - 0.3, 0.9)) });
      reveal(s.share, P(t, cs(sc, 1) + 1.8, 0.6, ease.back), { y: 16, blur: 0, scale: 0.9 });
    },
  };

  // ---------- 5 · honest abstain ----------
  R.jujur = {
    bg: "bg-cream",
    build(root) {
      const s = { bg: photo(root, "field-day-blur.jpg") };
      el("div", null, null, root, { position: "absolute", inset: 0, background: "linear-gradient(90deg, rgba(248,243,240,.55), rgba(248,243,240,.1) 60%)" });
      s.q = text(root, "serif", 140, 230, "Bagaimana jika *belum ada* yang memeriksa?", { width: "1000px", fontSize: "104px" });
      s.h = text(root, "serif", 140, 220, "Halio tidak *menebak*.", { width: "1000px", fontSize: "150px" });
      const items = ["Bilang terus terang: belum ada pemeriksaan", "Sarankan pesan ditahan dulu", "Tawarkan pemeriksa manusia"];
      s.items = items.map((txt, i) => {
        const r = el("div", null, null, root); at(r, 140, 520 + i * 104, { display: "flex", alignItems: "center", gap: "20px", padding: "18px 28px 18px 18px", borderRadius: "999px", background: "rgba(255,255,255,.82)", font: "600 30px Inter" });
        el("div", null, '<svg width="44" height="44" viewBox="0 0 44 44"><circle cx="22" cy="22" r="22" fill="#014BAA"/><path d="M13 23l6 6 12-13" fill="none" stroke="#F8F3F0" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>', r);
        el("span", null, txt, r);
        return r;
      });
      s.ph = phoneShot(root, 1250, 96, 0.9, ["phone-abstain-full.png"]);
      return s;
    },
    update(t, s, sc) {
      kenBurns(s.bg, t, sc.dur, 1.04, 1.07);
      const sw = P(t, cs(sc, 1) - 0.3, 0.6);
      stagger(s.q.sp, t, cs(sc, 0) - 0.2, 0.08, 0.7, { max: 1 - sw });
      stagger(s.h.sp, t, cs(sc, 1) - 0.1, 0.14, 0.8);
      reveal(s.items[0], P(t, cs(sc, 1) + 1.0, 0.6), { x: -30, y: 0 });
      reveal(s.items[1], P(t, cs(sc, 1) + 3.0, 0.6), { x: -30, y: 0 });
      reveal(s.items[2], P(t, cs(sc, 2) - 0.1, 0.6), { x: -30, y: 0 });
      reveal(s.ph.f, P(t, 0.2, 1.0), { x: 60, y: 0, blur: 8 });
      s.ph.scroll(s.ph.imgs[0], lerp(lerp(0, 740, P(t, cs(sc, 1) - 0.4, 1.4, ease.inOut)), 1060, P(t, cs(sc, 2) - 0.2, 1.4, ease.inOut)));
    },
  };

  // ---------- 5 · three states ----------
  R.tiga = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      s.h = text(root, "serif", 0, 150, "Tiga keadaan. *Tanpa tebakan.*", { width: "1920px", textAlign: "center", fontSize: "104px" });
      const C = [
        ["#B42318", "Terbukti salah", "Sudah dibantah pemeriksa fakta atau sumber resmi yang disebutkan.", "Disertai nama sumber dan tautan"],
        ["#B54708", "Tidak yakin", "Mirip kabar bohong, tetapi tidak sama persis, atau bukan klaim faktual.", "Disarankan ditahan dulu"],
        ["#475467", "Belum ada pemeriksaan", "Belum ada bantahan. Halio tidak menebak.", "Ditawarkan pemeriksa manusia"],
      ];
      s.cards = C.map(([c, label, desc, foot], i) => {
        const k = el("div", "card", null, root); at(k, 140 + i * 560, 330, { width: "520px", height: "500px", overflow: "hidden" });
        el("div", "grot", label, k, { background: c, color: "#F8F3F0", fontSize: "46px", padding: "40px 36px", height: "190px", display: "flex", alignItems: "flex-end" });
        el("div", null, desc, k, { font: "600 30px/1.35 Inter", padding: "32px 36px 0", color: "#0E1726" });
        el("div", "micro", foot, k, { position: "absolute", left: "36px", bottom: "34px", color: c, fontSize: "17px" });
        return k;
      });
      return s;
    },
    update(t, s, sc) {
      stagger(s.h.sp, t, cs(sc, 0) - 0.3, 0.12, 0.8);
      const per = (ce(sc, 1) - cs(sc, 1)) / 3;
      s.cards.forEach((k, i) => reveal(k, P(t, cs(sc, 1) - 0.2 + i * per, 0.8, ease.back), { y: 60, blur: 0, scale: 0.94 }));
    },
  };

  // ---------- 6 · how it works ----------
  R.mesin = {
    bg: "bg-blue", dark: true,
    build(root) {
      const s = {};
      s.k = block(root, "micro", "Cara kerja", 146, 140, { color: "#FFC83D" });
      s.h = text(root, "serif", 140, 180, "Dari pesan berantai ke jawaban yang *jujur*.", { fontSize: "86px", color: "#F8F3F0" });
      const L = ["Pilih kalimat yang layak dicek", "Hapus nomor, NIK, dan tautan", "Cocokkan dengan bantahan bersumber", "Jaga inti klaim", "LLM opsional, wajib kutipan persis"];
      s.chips = L.map((txt, i) => {
        const c = el("div", null, null, root); at(c, 140 + i * 332, 330, { width: "312px", height: "150px", borderRadius: "24px", background: "#F8F3F0", padding: "22px 24px" });
        el("div", "grot", "0" + (i + 1), c, { fontSize: "36px", color: "#014BAA" });
        el("div", null, txt, c, { font: "600 24px/1.25 Inter", color: "#0E1726", marginTop: "12px" });
        return c;
      });
      const panel = el("div", null, null, root); at(panel, 140, 520, { width: "1640px", height: "330px", borderRadius: "28px", background: "#F8F3F0", padding: "40px 44px" }); s.panel = panel;
      el("div", "micro", "Pesan yang diterima", panel, { color: "#6B7486", fontSize: "17px", marginBottom: "16px" });
      const msg = el("div", null, null, panel, { width: "960px", font: "500 30px/1.5 Inter", color: "#0E1726" });
      s.claim = el("span", null, "Bapak ibu, ada video Pak Presiden bagi-bagi bantuan tunai! Langsung chat nomor WA ", msg);
      s.phoneTok = el("span", null, "0812-3456-7890", msg, { display: "inline-block", position: "relative" });
      s.nomor = el("span", null, "[NOMOR]", s.phoneTok, { position: "absolute", left: 0, top: "2px", padding: "0 8px", borderRadius: "8px", background: "#014BAA", color: "#F8F3F0", font: "700 26px/1.4 Inter", whiteSpace: "nowrap" });
      s.claim2 = el("span", null, " untuk daftar, bayar biaya admin 150rb dulu.", msg);
      s.drop = el("span", null, " SEBARKAN!!", msg);
      const score = D.bansos && D.bansos.match ? D.bansos.match.score : 0.56;
      const src = D.bansos && D.bansos.match ? D.bansos.match.sumber[0].nama : "Katadata (mengutip Bareskrim Polri)";
      s.match = el("div", null, `<div class="micro" style="color:#6B7486;font-size:16px">Cocok dengan bantahan</div>
        <div style="font:600 25px/1.3 Inter;margin:10px 0 16px">${src}</div>
        <div style="height:12px;border-radius:6px;background:#E7E1DC;overflow:hidden"><div class="fill" style="height:100%;width:0;background:#014BAA"></div></div>
        <div style="font:500 20px Inter;color:#6B7486;margin-top:10px">kemiripan ${score.toFixed(2).replace(".", ",")} · ambang 0,40</div>`, panel);
      at(s.match, 1150, 40, { width: "450px" });
      s.fill = s.match.querySelector(".fill"); s.score = score;
      s.core = el("div", null, '<span style="color:#2FBF71">✔</span>&nbsp; Inti klaim hadir: daftar · bayar · biaya', panel); at(s.core, 1150, 196, { font: "600 22px Inter", color: "#0E1726" });
      s.verdict = el("div", "grot", "Terbukti salah", panel); at(s.verdict, 1150, 240, { fontSize: "30px", padding: "14px 20px", borderRadius: "14px", background: "#B42318", color: "#F8F3F0" });
      s.conf = confetti(root, 30, 21, { x: 120, y: 40, w: 1700, h: 480, avoid: { x: 120, y: 120, w: 1300, h: 200 } });
      s.conf.forEach((c, i) => { c.target = i % 5; });
      return s;
    },
    update(t, s, sc) {
      reveal(s.k, P(t, 0.2, 0.6), { y: 8 });
      stagger(s.h.sp, t, 0.3, 0.08, 0.7);
      reveal(s.panel, P(t, 0.6, 0.8), { y: 30, blur: 0 });
      s.chips.forEach((c, i) => { const on = P(t, cs(sc, i) - 0.15, 0.5); reveal(c, P(t, 0.5 + i * 0.12, 0.6), { y: 20, blur: 0, max: lerp(0.28, 1, on) }); c.style.boxShadow = on > 0.5 && t < cs(sc, Math.min(i + 1, 4)) + (i === 4 ? 9 : 0) ? "0 0 0 6px rgba(255,200,61,.9)" : "none"; });
      s.conf.forEach((c) => {
        const a = P(t, 0.1 + c.delay, 0.7, ease.back);
        const go = P(t, cs(sc, c.target) - 0.2 + c.delay * 0.4, 0.9, ease.inOut);
        const tx = 140 + c.target * 332 + 156 - c.size / 2, ty = 330 + 75 - c.size / 2;
        const x = lerp(c.x + Math.sin(t * 0.8 + c.ph) * c.amp, tx, go), y = lerp(c.y + Math.cos(t * 0.7 + c.ph) * c.amp, ty, go);
        c.node.style.left = x + "px"; c.node.style.top = y + "px";
        c.node.style.opacity = a * (1 - P(t, cs(sc, c.target) + 0.5 + c.delay * 0.4, 0.4));
        c.node.style.transform = `rotate(${c.rot + t * c.spin}deg) scale(${a * (1 - 0.6 * go)})`;
      });
      const hl = P(t, cs(sc, 0) + 0.3, 0.8);
      [s.claim, s.phoneTok, s.claim2].forEach((n) => { n.style.background = `rgba(255,200,61,${0.45 * hl})`; n.style.borderRadius = "6px"; });
      s.drop.style.opacity = lerp(1, 0.25, hl); s.drop.style.textDecoration = hl > 0.5 ? "line-through" : "none";
      const nm = P(t, cs(sc, 1) + 0.6, 0.5);
      s.nomor.style.opacity = nm; s.phoneTok.style.color = `rgba(14,23,38,${1 - nm})`;
      if (s.wFrom == null) { s.wFrom = s.phoneTok.offsetWidth; s.wTo = s.nomor.offsetWidth; }
      s.phoneTok.style.width = lerp(s.wFrom, s.wTo, nm) + "px"; s.phoneTok.style.overflow = "hidden"; s.phoneTok.style.verticalAlign = "bottom"; s.phoneTok.style.whiteSpace = "nowrap";
      reveal(s.match, P(t, cs(sc, 2), 0.7), { x: 30, y: 0 });
      s.fill.style.width = (s.score * 100 * P(t, cs(sc, 2) + 0.4, 1.2)) + "%";
      reveal(s.core, P(t, cs(sc, 3) + 0.2, 0.6), { x: 20, y: 0 });
      reveal(s.verdict, P(t, cs(sc, 4) + 0.6, 0.7, ease.back), { y: 10, blur: 0, scale: 0.8 });
    },
  };

  // ---------- 7 · sensor ----------
  R.sensor = {
    bg: "bg-ink", dark: true,
    build(root) {
      const s = {};
      const cov = D.coverage || { sources_total: 23, hidup: 22 };
      s.k = block(root, "micro", "Sensor · panel cakupan", 146, 190, { color: "#FFC83D" });
      s.n = block(root, "grot", String(cov.sources_total), 136, 236, { fontSize: "300px", color: "#F8F3F0" });
      s.l = block(root, null, "feed terbuka dipantau", 146, 520, { font: "600 38px Inter", color: "#F8F3F0" });
      s.d = block(root, "body", `Berita, cek fakta, dan sumber resmi. ${cov.hidup} hidup saat direkam, diperbarui tiap 2 sampai 10 menit.`, 146, 578, { width: "580px", fontSize: "27px", color: "rgba(248,243,240,.7)" });
      s.bk = block(root, "micro", "Titik buta yang diakui", 146, 718, { color: "rgba(248,243,240,.6)" });
      s.chips = ["WhatsApp privat", "Facebook & Instagram", "TikTok", "X", "YouTube", "Telegram"].map((c, i) => {
        const n = el("span", "chip", c, root); at(n, 146 + [0, 230, 0, 150, 220, 410][i], 760 + [0, 0, 64, 64, 64, 64][i], { border: "2px solid rgba(248,243,240,.35)", color: "#F8F3F0", fontSize: "22px" });
        return n;
      });
      s.b = browserShot(root, 800, 140, 980, 740, "desk-coverage.png", "halio · /coverage", 2160);
      return s;
    },
    update(t, s, sc) {
      reveal(s.k, P(t, 0.3, 0.6), { y: 8 });
      reveal(s.n, P(t, cs(sc, 1) - 0.4, 0.9), { y: 40, blur: 18 });
      reveal(s.l, P(t, cs(sc, 1), 0.7), { y: 12 });
      reveal(s.d, P(t, cs(sc, 1) + 0.8, 0.7), { y: 12 });
      reveal(s.bk, P(t, cs(sc, 2) - 0.2, 0.6), { y: 8 });
      s.chips.forEach((c, i) => reveal(c, P(t, cs(sc, 2) + i * 0.25, 0.5, ease.back), { y: 12, blur: 0, scale: 0.85 }));
      reveal(s.b.f, P(t, 0.2, 1.0), { x: 60, y: 0, blur: 8 });
      const full = (s.b.img.naturalHeight || 5800) * s.b.k;
      s.b.scroll(lerp(lerp(0, 330, P(t, cs(sc, 1), 2.5, ease.inOut)), full * 0.66, P(t, cs(sc, 2) - 0.4, 2.0, ease.inOut)));
    },
  };

  // ---------- 7 · radar ----------
  R.radar = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      s.b = browserShot(root, 140, 140, 1040, 740, "desk-radar.png", "halio · /radar", 2160);
      s.badge = block(root, "micro", "Data simulasi untuk demo", 860, 112, { padding: "12px 18px", borderRadius: "999px", background: "#FFC83D", color: "#0E1726", fontSize: "17px", boxShadow: "0 8px 20px rgba(14,23,38,.15)" });
      s.k = block(root, "micro", "Radar ketahanan kognitif", 1266, 190, { color: "#014BAA" });
      s.h = text(root, "serif", 1260, 232, "Tren, *bukan* orang.", { width: "560px", fontSize: "110px" });
      const rows = [["#014BAA", "Kategori hoaks"], ["#8B5CF6", "Trik manipulasi yang sering dipakai"], ["#B42318", "Penipuan yang mencatut TNI AD"], ["#2FBF71", "Kabar baru tampil setelah ≥ 5 pelapor berbeda"]];
      s.rows = rows.map(([c, txt], i) => { const r = block(root, null, `<span class="dot" style="background:${c}"></span>${txt}`, 1266, 500 + i * 84, { width: "560px", font: "600 28px/1.25 Inter", display: "flex", alignItems: "flex-start" }); return r; });
      return s;
    },
    update(t, s, sc) {
      reveal(s.b.f, P(t, 0.2, 1.0), { x: -60, y: 0, blur: 8 });
      reveal(s.badge, P(t, 1.0, 0.6, ease.back), { y: 10, blur: 0, scale: 0.8 });
      reveal(s.k, P(t, 0.4, 0.6), { y: 8 });
      stagger(s.h.sp, t, cs(sc, 0) - 0.2, 0.14, 0.8);
      const a = cs(sc, 1), d = ce(sc, 1) - a;
      [a, a + d * 0.3, a + d * 0.6, cs(sc, 2)].forEach((st, i) => reveal(s.rows[i], P(t, st, 0.6), { x: 24, y: 0 }));
      s.b.scroll(lerp(0, (s.b.img.naturalHeight || 3443) * s.b.k - 686, P(t, 1.2, sc.dur - 2.4, ease.inOut)));
    },
  };

  // ---------- 8 · governance ----------
  R.batas = {
    bg: "bg-ink", dark: true,
    build(root) {
      const s = {};
      s.l1 = text(root, "serif", 0, 200, "Pertahanan siber,", { width: "1920px", textAlign: "center", fontSize: "136px", color: "#F8F3F0" });
      s.l2 = text(root, "serif", 0, 340, "*bukan* pengawasan warga.", { width: "1920px", textAlign: "center", fontSize: "136px", color: "#F8F3F0" });
      const C = ["Tanpa profil individu", "Pesan pribadi tidak disimpan tanpa permintaan", "Hanya agregat dan k-anonim"];
      s.cards = C.map((txt, i) => {
        const k = el("div", null, null, root); at(k, 140 + i * 560, 590, { width: "520px", height: "190px", borderRadius: "26px", background: "rgba(248,243,240,.07)", border: "1px solid rgba(248,243,240,.16)", padding: "30px 32px", display: "flex", gap: "22px", alignItems: "flex-start" });
        el("div", null, '<svg width="52" height="52" viewBox="0 0 44 44"><circle cx="22" cy="22" r="22" fill="#FFC83D"/><path d="M13 23l6 6 12-13" fill="none" stroke="#0E1726" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/></svg>', k, { flex: "0 0 52px" });
        el("div", null, txt, k, { font: "600 31px/1.3 Inter", color: "#F8F3F0" });
        return k;
      });
      return s;
    },
    update(t, s, sc) {
      stagger(s.l1.sp, t, cs(sc, 0) - 0.3, 0.14, 0.8);
      stagger(s.l2.sp, t, cs(sc, 0) + 0.8, 0.14, 0.8);
      const a = cs(sc, 1), d = ce(sc, 1) - a;
      s.cards.forEach((k, i) => reveal(k, P(t, a - 0.2 + (i * d) / 3, 0.7), { y: 30, blur: 0 }));
    },
  };

  // ---------- 9 · deployment ----------
  R.pasang = {
    bg: "bg-blue", dark: true,
    build(root) {
      const s = {};
      const term = el("div", null, null, root); at(term, 140, 220, { width: "940px", height: "500px", borderRadius: "24px", background: "#0B1220", boxShadow: "0 40px 90px rgba(0,0,0,.35)", overflow: "hidden" }); s.term = term;
      const bar = el("div", null, null, term, { height: "52px", display: "flex", gap: "10px", alignItems: "center", padding: "0 22px", background: "#141C2C" });
      ["#FF6159", "#FFBD2E", "#28C840"].forEach((c) => el("b", null, null, bar, { width: "14px", height: "14px", borderRadius: "50%", background: c, display: "block" }));
      el("span", null, "server-satuan — halio", bar, { marginLeft: "16px", font: "500 18px Inter", color: "rgba(248,243,240,.5)" });
      const mono = { font: '500 30px/1.7 "DejaVu Sans Mono", monospace', color: "#F8F3F0" };
      s.cmd = el("div", null, "", term, { ...mono, padding: "36px 40px 10px" });
      s.cmdText = "$ docker compose up -d";
      s.out = ["halio-api     siap di :8000", "sensor        23 feed terbuka", "radar         /radar", "cakupan       /coverage"].map((l) =>
        el("div", null, `<span style="color:#2FBF71">✔</span> ${l}`, term, { ...mono, fontSize: "27px", padding: "0 40px", color: "rgba(248,243,240,.85)", whiteSpace: "pre" }));
      s.chips = ["1 kontainer", "Tanpa GPU", "Tanpa API berbayar", "On-premise"].map((c, i) =>
        block(root, "grot", c, 1170, 230 + i * 118, { fontSize: "46px", padding: "20px 30px", borderRadius: "999px", border: "2px solid rgba(248,243,240,.4)", color: "#F8F3F0", whiteSpace: "nowrap" }));
      s.note = block(root, "micro", "LLM dan ClaimReview bersifat opsional", 1176, 718, { color: "rgba(248,243,240,.65)" });
      return s;
    },
    update(t, s, sc) {
      reveal(s.term, P(t, 0.2, 0.9), { y: 30, blur: 0 });
      const n = Math.floor(s.cmdText.length * P(t, 0.8, 1.4, (x) => x));
      s.cmd.textContent = s.cmdText.slice(0, n) + (Math.floor(t * 2) % 2 && n < s.cmdText.length + 1 ? "▍" : "");
      s.out.forEach((o, i) => reveal(o, P(t, 2.5 + i * 0.4, 0.4), { y: 8, blur: 0 }));
      s.chips.forEach((c, i) => reveal(c, P(t, cs(sc, 0) + 0.4 + i * 0.9, 0.6, ease.back), { x: 30, y: 0, blur: 0, scale: 0.9 }));
      reveal(s.note, P(t, cs(sc, 1) + 0.6, 0.6), { y: 8 });
    },
  };

  // ---------- 10 · honest status ----------
  R.status = {
    bg: "bg-cream",
    build(root) {
      const s = {};
      s.h = text(root, "serif", 140, 150, "Status *jujur* prototipe.", { fontSize: "110px" });
      const col = (x, title, color, items) => {
        const k = el("div", "card", null, root); at(k, x, 320, { width: "800px", height: "450px", padding: "40px 44px" });
        el("div", "micro", title, k, { color, marginBottom: "26px" });
        const rows = items.map((txt) => el("div", null, `<span class="dot" style="background:${color};margin-top:12px;flex:0 0 14px"></span><span>${txt}</span>`, k, { display: "flex", alignItems: "flex-start", font: "500 29px/1.35 Inter", color: "#0E1726", marginBottom: "22px" }));
        return { k, rows };
      };
      s.a = col(140, "Sudah berjalan", "#2F8F4E", STATUS.done);
      s.b = col(980, "Sedang diperbaiki", "#B54708", STATUS.todo);
      return s;
    },
    update(t, s, sc) {
      stagger(s.h.sp, t, 0.3, 0.14, 0.8);
      reveal(s.a.k, P(t, 0.4, 0.8), { y: 30, blur: 0 });
      reveal(s.b.k, P(t, cs(sc, 0) + 1.2, 0.8), { y: 30, blur: 0 });
      s.a.rows.forEach((r, i) => reveal(r, P(t, 0.9 + i * 0.35, 0.5), { x: 16, y: 0 }));
      const a = cs(sc, 1) - 0.6, d = ce(sc, 2) - a;
      s.b.rows.forEach((r, i) => reveal(r, P(t, a + (i * d) / s.b.rows.length, 0.5), { x: 16, y: 0 }));
    },
  };

  // ---------- Epilog ----------
  R.penutup = {
    bg: "bg-cream", noChrome: true,
    build(root) {
      const s = { bg: photo(root, "field-day.jpg") };
      el("div", null, null, root, { position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(248,243,240,.55), rgba(248,243,240,.35) 55%, rgba(248,243,240,0) 80%)" });
      s.l1 = text(root, "serif", 0, 150, "Ketahanan kognitif", { width: "1920px", textAlign: "center", fontSize: "120px" });
      s.l2 = text(root, "serif", 0, 270, "dimulai dari *keluarga*.", { width: "1920px", textAlign: "center", fontSize: "120px" });
      const row = el("div", null, null, root); at(row, 0, 470, { width: "1920px", display: "flex", justifyContent: "center", alignItems: "center", gap: "28px" }); s.row = row;
      el("img", null, null, row, { width: "128px", height: "128px" }).src = A + "halio-mark.svg";
      el("div", "serif", 'halio<span style="color:#014BAA">.</span>', row, { fontSize: "170px", lineHeight: "1", color: "#0E1726" });
      s.tag = block(root, null, "Cek dulu, baru teruskan.", 0, 650, { width: "1920px", textAlign: "center", font: "600 40px Inter", color: "#0E1726" });
      s.meta = block(root, "micro", "Kartika Cyber Hackathon 2026 · Kategori Siber Sosial · github.com/Ardelyo/halio", 0, 730, { width: "1920px", textAlign: "center", color: "#0E1726" });
      return s;
    },
    update(t, s, sc) {
      kenBurns(s.bg, t, sc.dur, 1.03, 1.07);
      stagger(s.l1.sp, t, cs(sc, 0) - 0.3, 0.14, 0.9);
      stagger(s.l2.sp, t, cs(sc, 0) + 0.6, 0.14, 0.9);
      reveal(s.row, P(t, cs(sc, 1) - 0.2, 1.0, ease.back), { y: 30, blur: 0, scale: 0.85 });
      reveal(s.tag, P(t, cs(sc, 1) + 0.9, 0.7), { y: 12 });
      reveal(s.meta, P(t, cs(sc, 1) + 1.6, 0.7), { y: 8 });
    },
  };
})();

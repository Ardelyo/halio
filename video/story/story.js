// Halio "segera hadir" story teaser, 1080x1920, 25 s. Deterministic: Story.seek(t) draws time t.
// Cuts sit on the backing track's grid: one beat = 0.4 s, bar hits at 0.41 + 1.6k s (see video/tools/story_sfx.py).
(() => {
  const W = 1080, H = 1920, DUR = 25.0;
  const D = (k) => 0.41 + 1.6 * k;   // bar hits
  const A = "../assets/";

  // ---------- helpers ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const E = {
    out: (t) => 1 - Math.pow(1 - t, 3), inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    expo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)), inQuad: (t) => t * t, inCubic: (t) => t * t * t,
    back: (t) => { const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    lin: (t) => t,
  };
  const P = (t, a, d, e = E.out) => e(clamp((t - a) / Math.max(1e-6, d)));
  const lerp = (a, b, p) => a + (b - a) * p;
  function el(tag, cls, html, parent, style) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    if (style) Object.assign(n.style, style);
    if (parent) parent.appendChild(n);
    return n;
  }
  const at = (n, x, y, extra = {}) => Object.assign(n.style, { position: "absolute", left: x + "px", top: y + "px", ...extra });
  function rand(seed) { let a = seed >>> 0; return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function reveal(n, p, o = {}) {
    const y = o.y ?? 30, x = o.x ?? 0, blur = o.blur ?? 16;
    n.style.opacity = (o.max ?? 1) * p;
    let tr = o.pre || "";
    tr += ` translate(${(1 - p) * x}px, ${(1 - p) * y}px)`;
    if (o.scale != null) tr += ` scale(${lerp(o.scale, 1, p)})`;
    n.style.transform = tr;
    n.style.filter = p >= 0.999 || !blur ? "none" : `blur(${(1 - p) * blur}px)`;
  }
  function words(parent, text) {
    const out = [];
    text.split(/(\s+)/).forEach((tok) => {
      if (!tok) return;
      if (/^\s+$/.test(tok)) { parent.appendChild(document.createTextNode(" ")); return; }
      const m = tok.match(/^\*(.+)\*([.,:;!?]*)$/);
      const s = el("span", "w", null, parent);
      if (m) { el("em", null, m[1], s); if (m[2]) s.appendChild(document.createTextNode(m[2])); } else s.textContent = tok;
      out.push(s);
    });
    return out;
  }
  const stagger = (sp, t, start, per = 0.08, dur = 0.45, o = {}) => sp.forEach((s, i) => reveal(s, P(t, start + i * per, dur), { y: 26, blur: 14, ...o }));
  const PALETTE = ["#FFC83D", "#8B5CF6", "#FF8A3D", "#2FBF71", "#F8F3F0"];
  function shapeSVG(kind, color, s) {
    const h = s / 2;
    const p = {
      half: `<path d="M0 ${h}A${h} ${h} 0 0 1 ${s} ${h}Z" fill="${color}"/>`,
      quarter: `<path d="M0 ${s}A${s} ${s} 0 0 1 ${s} 0L${s} ${s}Z" fill="${color}"/>`,
      ring: `<path d="M${s * 0.12} ${s}A${s * 0.88} ${s * 0.88} 0 0 1 ${s} ${s * 0.12}" fill="none" stroke="${color}" stroke-width="${s * 0.22}" stroke-linecap="round"/>`,
      dot: `<circle cx="${h}" cy="${h}" r="${h}" fill="${color}"/>`,
      bar: `<rect x="0" y="${s * 0.36}" width="${s}" height="${s * 0.28}" rx="${s * 0.14}" fill="${color}"/>`,
    }[kind];
    return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" overflow="visible">${p}</svg>`;
  }
  const KINDS = ["half", "quarter", "ring", "dot", "bar"];

  // Extruded slab: stacked layers give real thickness when rotated in 3D.
  function slab(parent, w, h, depth, radius, side, faceHTML, faceStyle = {}) {
    const o = el("div", "obj", null, parent, { width: w + "px", height: h + "px" });
    const n = Math.max(8, Math.round(depth / 4));
    for (let i = n; i >= 1; i--) {
      const k = i / n;
      el("div", null, null, o, { position: "absolute", inset: 0, borderRadius: radius + "px", background: side(k), transform: `translateZ(${-k * depth}px)` });
    }
    const face = el("div", null, faceHTML, o, { position: "absolute", inset: 0, borderRadius: radius + "px", overflow: "hidden", ...faceStyle });
    return { o, face };
  }
  const blueSide = (k) => `rgb(${Math.round(1 + 10 * (1 - k))}, ${Math.round(48 - 18 * k)}, ${Math.round(118 - 40 * k)})`;
  const inkSide = (k) => `rgb(${Math.round(20 - 8 * k)}, ${Math.round(26 - 10 * k)}, ${Math.round(40 - 14 * k)})`;
  function mark3D(parent, size, depth) {
    return slab(parent, size, size, depth, size * 0.28, blueSide, `<img src="${A}halio-mark.svg" style="width:100%;height:100%;display:block">`);
  }

  // ---------- shots ----------
  const world = document.getElementById("world");
  const SHOTS = [];
  function shot(t0, t1, bg, build, update) {
    const root = el("div", "shot", null, world, { background: bg || "transparent" });
    SHOTS.push({ t0, t1, root, s: build(root) || {}, update });
  }
  const fits = new Map();
  function fit(n, maxW) { // shrink big type to the frame once fonts are ready (measures the inner span)
    if (fits.has(n)) return;
    const w = n.firstElementChild.offsetWidth;
    if (w > maxW) n.style.fontSize = parseFloat(n.style.fontSize) * (maxW / w) + "px";
    fits.set(n, 1);
  }

  // A · 08.00, notifications pile up
  shot(0, D(1), "radial-gradient(120% 70% at 50% 35%, #12305f 0%, #0b1529 55%, #05080f 100%)", (r) => {
    const s = {};
    s.g = el("div", "obj", null, r, { left: 0, top: 0, width: W + "px", height: H + "px" });
    s.time = el("div", "grot", "08.00", s.g); at(s.time, 0, 360, { width: W + "px", textAlign: "center", fontSize: "250px", color: "#F8F3F0" });
    s.day = el("div", "micro", "Selasa pagi", s.g); at(s.day, 0, 640, { width: W + "px", textAlign: "center", color: "rgba(248,243,240,.7)" });
    const N = [["Grup Keluarga Besar", "Tante Yuli: Bapak ibu, ada video Presiden bagi-bagi bantuan tunai…"], ["Grup Arisan RT 05", "Bu Ani: SEBARKAN!! Jangan berhenti di Anda"], ["Keluarga Pakde", "Pakde: WASPADA penculik anak naik mobil putih…"]];
    s.n = N.map(([a, b], i) => {
      const c = el("div", null, `<div style="display:flex;align-items:center;gap:16px"><div style="width:54px;height:54px;border-radius:16px;background:#F8F3F0;display:grid;place-items:center"><div style="width:26px;height:22px;border-radius:11px 11px 11px 3px;background:#014BAA"></div></div>
        <b style="font:700 30px Inter;color:#F8F3F0">${a}</b><span style="margin-left:auto;font:500 24px Inter;color:rgba(248,243,240,.6)">baru saja</span></div>
        <div style="font:500 30px/1.35 Inter;color:rgba(248,243,240,.9);margin-top:14px">${b}</div>`, s.g);
      at(c, 80, 840 + i * 250, { width: "920px", padding: "28px 32px", borderRadius: "34px", background: "rgba(248,243,240,.12)", border: "1px solid rgba(248,243,240,.18)", boxShadow: "0 30px 60px rgba(0,0,0,.35)" });
      return c;
    });
    s.more = el("div", "micro", "+ 128 pesan lainnya", s.g); at(s.more, 0, 1620, { width: W + "px", textAlign: "center", color: "#FFC83D" });
    return s;
  }, (t, s) => {
    s.g.style.transform = `translateZ(${lerp(-80, 140, P(t, 0, 2.0, E.inOut))}px) rotateX(${lerp(10, 2, P(t, 0, 2.0))}deg)`;
    reveal(s.time, P(t, 0.0, 0.5), { y: 0, blur: 30, scale: 1.15 });
    reveal(s.day, P(t, 0.25, 0.4), { y: 10 });
    s.n.forEach((c, i) => reveal(c, P(t, 0.41 + i * 0.4, 0.3, E.back), { y: 120, blur: 10, scale: 0.9 }));
    reveal(s.more, P(t, 1.61, 0.25), { y: 20, blur: 8 });
  });

  // B · a phone flies in: "SEBARKAN!!"
  shot(D(1), D(2), "radial-gradient(90% 60% at 50% 45%, #0A5BC9 0%, #014BAA 55%, #01326f 100%)", (r) => {
    const s = {};
    const screen = `<div style="position:absolute;inset:0;background:#EFE8E2">
      <div style="height:150px;background:#014BAA;padding:70px 34px 0;font:600 34px Inter;color:#F8F3F0">Grup Keluarga Besar</div>
      <div style="margin:30px 26px;padding:20px 22px;border-radius:26px;background:#fff;font:500 26px/1.35 Inter;color:#0E1726">
        <div style="font:600 22px Inter;color:#014BAA">Tante Yuli</div><div style="font:italic 500 20px Inter;color:#6B7486;margin:4px 0 12px">↪ Diteruskan berkali-kali</div>
        <div style="height:250px;border-radius:16px;background:linear-gradient(135deg,#1c2a44,#3a2f2a);position:relative"><div style="position:absolute;left:50%;top:50%;width:84px;height:84px;margin:-42px;border-radius:50%;background:rgba(248,243,240,.9)"></div></div>
        <div style="margin-top:14px">Video Presiden bagi-bagi bantuan tunai! Daftar lewat WA, biaya admin 150rb.</div></div></div>`;
    s.ph = slab(r, 580, 1180, 46, 80, inkSide, `<div style="position:absolute;inset:14px;border-radius:66px;overflow:hidden">${screen}</div>`, { background: "#0B1220" });
    at(s.ph.o, 250, 370);
    s.bub = el("div", "grot", "Sebarkan!!", r); at(s.bub, 150, 1200, { fontSize: "120px", padding: "30px 44px", borderRadius: "46px", background: "#F8F3F0", color: "#B42318", boxShadow: "0 30px 70px rgba(0,0,0,.35)", whiteSpace: "nowrap" });
    s.lab = el("div", "micro", "Diteruskan ke semua grup", r); at(s.lab, 0, 250, { width: W + "px", textAlign: "center", color: "#FFC83D" });
    return s;
  }, (t, s) => {
    const fly = P(t, 0, 0.4, E.expo);
    s.ph.o.style.transform = `translateZ(${lerp(-2600, 0, fly)}px) rotateY(${lerp(70, -14, fly) + t * 9}deg) rotateX(${lerp(24, 6, fly)}deg) rotateZ(${lerp(-18, -3, fly)}deg)`;
    s.ph.o.style.opacity = P(t, 0, 0.08);
    const pop = P(t, 0.8, 0.22, E.back);
    s.bub.style.opacity = P(t, 0.8, 0.05);
    s.bub.style.transform = `translateZ(220px) rotate(${lerp(-14, -4, pop)}deg) scale(${lerp(0.2, 1, pop)})`;
    reveal(s.lab, P(t, 1.2, 0.25), { y: 20 });
  });

  // C, K · one word per beat
  function wordBeats(t0, list) {
    list.forEach(([text, bg, color, size, glitch], i) => {
      shot(t0 + i * 0.4, t0 + (i + 1) * 0.4, bg, (r) => {
        const s = { echo: [] };
        for (let k = 3; k >= 1; k--) {
          const e = el("div", "grot", `<span>${text}</span>`, r); e.dataset.fit = "1"; at(e, 0, 0, { width: W + "px", height: H + "px", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontSize: size + "px", color, opacity: 0.12 * (4 - k) / 3, whiteSpace: "pre-line" });
          s.echo.push({ e, k });
        }
        s.w = el("div", "grot" + (glitch ? " glitch" : ""), `<span>${text}</span>`, r); s.w.dataset.fit = "1"; at(s.w, 0, 0, { width: W + "px", height: H + "px", display: "flex", alignItems: "center", justifyContent: "center", textAlign: "center", fontSize: size + "px", color, whiteSpace: "pre-line" });
        return s;
      }, (t, s) => {
        const p = P(t, 0, 0.14, E.out);
        s.w.style.transform = `scale(${lerp(1.45, 1, p) + t * 0.12}) rotate(${lerp(-5, 0, p)}deg)`;
        s.w.style.filter = p < 1 ? `blur(${(1 - p) * 10}px)` : "none";
        s.echo.forEach(({ e, k }) => { e.style.transform = `translateZ(${-k * 160 - t * 300}px) scale(${1 + t * 0.1})`; });
      });
    });
  }
  wordBeats(D(2), [
    ["Teruskan.", "#014BAA", "#F8F3F0", 210],
    ["Bagikan.", "#F8F3F0", "#014BAA", 230],
    ["Sebarkan.", "#0E1726", "#FFC83D", 200],
    ["Viralkan!!", "#FFC83D", "#0E1726", 190, true],
  ]);

  // D · tunnel of hoax fragments
  shot(D(3), D(4), "radial-gradient(80% 60% at 50% 50%, #142446 0%, #0E1726 60%, #05080f 100%)", (r) => {
    const R = rand(41), F = ["SEBARKAN!!", "INFO A1", "DIJAMIN LULUS", "BANSOS TUNAI", "KLIK LINK INI", "WASPADA!!!", "biaya admin 150rb", "jangan berhenti di Anda", "KUOTA GRATIS 50GB", "info dari orang dalam", "VIRALKAN", "TRANSFER DULU", "penculik anak", "kirim ke 10 grup", "PREDIKSI GEMPA", "SEGERA!!"];
    const s = { items: [] };
    for (let i = 0; i < 38; i++) {
      let node;
      if (i % 3 === 2) node = el("div", null, shapeSVG(KINDS[i % 5], PALETTE[i % 5], 90 + R() * 80), r);
      else {
        const txt = F[i % F.length], big = i % 2 === 0;
        node = el("div", big ? "grot" : null, txt, r, big ? { fontSize: 90 + R() * 70 + "px", color: R() > 0.5 ? "#F8F3F0" : "#FFC83D", whiteSpace: "nowrap" }
          : { font: "600 44px Inter", padding: "18px 28px", borderRadius: "999px", background: "rgba(248,243,240,.92)", color: "#0E1726", whiteSpace: "nowrap" });
      }
      at(node, W / 2, H / 2);
      s.items.push({ node, x: (R() - 0.5) * 1500, y: (R() - 0.5) * 2300, z: -400 - R() * 4600, rot: (R() - 0.5) * 50 });
    }
    return s;
  }, (t, s) => {
    const cam = lerp(0, 4300, P(t, 0, 1.6, (x) => x * x * (2.2 - 1.2 * x)));
    s.items.forEach((it) => {
      const z = it.z + cam;
      const vis = z < 1100;
      it.node.style.visibility = vis ? "visible" : "hidden";
      if (!vis) return;
      it.node.style.transform = `translate(-50%,-50%) translate3d(${it.x}px, ${it.y}px, ${z}px) rotate(${it.rot + t * 20}deg)`;
      it.node.style.opacity = clamp((z + 5200) / 1400) * clamp((1100 - z) / 300);
      const dof = clamp((z - 350) / 120, 0, 9);
      it.node.style.filter = dof > 0.3 ? `blur(${dof}px)` : "none";
    });
  });

  // E · cinematic field
  shot(D(4), D(5), "#9CC3EB", (r) => {
    const s = { bg: el("div", "photo", null, r, { backgroundImage: `url(${A}field-day.jpg)` }) };
    el("div", null, null, r, { position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(248,243,240,.35), rgba(248,243,240,0) 45%)" });
    s.l1 = el("div", "serif", null, r); at(s.l1, 0, 430, { width: W + "px", textAlign: "center", fontSize: "190px", color: "#0E1726" }); s.a = words(s.l1, "Satu kabar");
    s.l2 = el("div", "serif", null, r); at(s.l2, 0, 620, { width: W + "px", textAlign: "center", fontSize: "230px", color: "#0E1726" }); s.b = words(s.l2, "*bohong*,");
    s.l2.querySelectorAll("em").forEach((e) => (e.style.color = "#014BAA"));
    return s;
  }, (t, s) => {
    s.bg.style.transform = `scale(${lerp(1.38, 1.12, P(t, 0, 1.6, E.out))}) translateY(${lerp(-90, 30, P(t, 0, 1.6, E.inOut))}px) rotate(${lerp(-2, 0, P(t, 0, 1.6))}deg)`;
    stagger(s.a, t, 0.25, 0.12, 0.4);
    stagger(s.b, t, 0.75, 0.1, 0.4);
  });

  // F · it spreads: network on a tilted 3D floor
  shot(D(5), D(6), "radial-gradient(90% 60% at 50% 60%, #17284a 0%, #0E1726 60%, #05080f 100%)", (r) => {
    const s = {};
    s.l1 = el("div", "serif", null, r); at(s.l1, 0, 330, { width: W + "px", textAlign: "center", fontSize: "120px", color: "#F8F3F0" }); s.a = words(s.l1, "bisa sampai ke");
    s.l2 = el("div", "serif", null, r); at(s.l2, 0, 470, { width: W + "px", textAlign: "center", fontSize: "150px", color: "#F8F3F0" }); s.b = words(s.l2, "seluruh *keluarga*.");
    s.floor = el("div", "obj", null, r, { left: W / 2 - 700 + "px", top: 1180 - 700 + "px", width: "1400px", height: "1400px" });
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg"); svg.setAttribute("width", 1400); svg.setAttribute("height", 1400); svg.style.position = "absolute"; s.floor.appendChild(svg);
    s.rings = [];
    const C = 700, rings = [[6, 220], [14, 420], [26, 640]];
    rings.forEach(([n, rad], ri) => {
      const g = []; const prev = ri === 0 ? [[C, C]] : rings[ri - 1];
      for (let i = 0; i < n; i++) {
        const a = (i / n) * Math.PI * 2 + ri * 0.4, x = C + Math.cos(a) * rad, y = C + Math.sin(a) * rad;
        const line = document.createElementNS(svgNS, "line");
        const pa = ri === 0 ? 0 : (Math.round((i / n) * prev[0]) / prev[0]) * Math.PI * 2 + (ri - 1) * 0.4, pr = ri === 0 ? 0 : prev[1];
        line.setAttribute("x1", C + Math.cos(pa) * pr); line.setAttribute("y1", C + Math.sin(pa) * pr); line.setAttribute("x2", x); line.setAttribute("y2", y);
        line.setAttribute("stroke", "rgba(255,200,61,.55)"); line.setAttribute("stroke-width", 4); svg.appendChild(line);
        const dot = el("div", null, null, s.floor, { position: "absolute", left: x - 26 + "px", top: y - 26 + "px", width: "52px", height: "52px", borderRadius: "50%", background: "#FFC83D", boxShadow: "0 0 30px rgba(255,200,61,.8)" });
        g.push({ line, dot });
      }
      s.rings.push(g);
    });
    s.core = el("div", null, null, s.floor, { position: "absolute", left: C - 46 + "px", top: C - 46 + "px", width: "92px", height: "92px", borderRadius: "50%", background: "#F8F3F0", boxShadow: "0 0 50px rgba(248,243,240,.9)" });
    return s;
  }, (t, s) => {
    s.floor.style.transform = `rotateX(62deg) rotateZ(${t * 14}deg) scale(${lerp(0.8, 1.05, P(t, 0, 1.6))})`;
    stagger(s.a, t, 0.0, 0.1, 0.35);
    stagger(s.b, t, 0.8, 0.12, 0.35);
    s.rings.forEach((g, ri) => g.forEach(({ line, dot }, i) => {
      const p = P(t, 0.4 + ri * 0.4 + (i / g.length) * 0.2, 0.25, E.back);
      dot.style.transform = `scale(${p})`; line.style.opacity = P(t, 0.35 + ri * 0.4 + (i / g.length) * 0.2, 0.2);
    }));
  });

  // G · three honest answers on a 3D ring
  shot(D(6), D(7), "radial-gradient(90% 60% at 50% 50%, #ffffff 0%, #F8F3F0 60%, #e9e0d9 100%)", (r) => {
    const s = {};
    s.k = el("div", "micro", "Tiga jawaban jujur", r); at(s.k, 0, 330, { width: W + "px", textAlign: "center", color: "#014BAA" });
    s.ring = el("div", "obj", null, r, { left: W / 2 - 260 + "px", top: 700 + "px", width: "520px", height: "680px" });
    const C = [["#B42318", "Terbukti\nsalah", "Sudah dibantah sumber bernama"], ["#B54708", "Tidak\nyakin", "Mirip, tetapi tidak sama persis"], ["#475467", "Belum ada\npemeriksaan", "Halio tidak menebak"]];
    s.cards = C.map(([c, label, desc], i) => {
      const k = el("div", null, `<div class="grot" style="background:${c};color:#F8F3F0;font-size:64px;padding:40px 36px;height:280px;display:flex;align-items:flex-end;white-space:pre-line">${label}</div>
        <div style="font:600 38px/1.3 Inter;padding:36px;color:#0E1726">${desc}</div>`, s.ring, { position: "absolute", inset: 0, borderRadius: "36px", background: "#fff", overflow: "hidden", boxShadow: "0 40px 80px rgba(14,23,38,.22)", backfaceVisibility: "hidden" });
      return k;
    });
    return s;
  }, (t, s) => {
    reveal(s.k, P(t, 0.1, 0.3), { y: 16 });
    const spin = lerp(-70, -70 - 250, P(t, 0, 1.6, E.inOut));
    s.cards.forEach((k, i) => { k.style.transform = `rotateY(${spin + i * 120}deg) translateZ(430px)`; });
    s.ring.style.transform = `translateZ(${lerp(-900, -250, P(t, 0, 0.5, E.expo))}px) rotateX(-6deg)`;
  });

  // H · real UI, flash cuts
  const UI = [
    ["Kartu Halio", `url(${A}shots/kartu-bansos.png)`, "900px 900px", "0 0", 900, 900, "#014BAA"],
    ["Jawaban bersumber", `url(${A}shots/phone-result-full.png)`, "760px auto", "0 -1520px", 760, 1000, "#0E1726"],
    ["Radar tren anonim", `url(${A}shots/desk-radar.png)`, "1500px auto", "-60px -260px", 960, 900, "#F8F3F0"],
    ["Sensor 23 feed", `url(${A}shots/desk-coverage.png)`, "1500px auto", "-60px -130px", 960, 900, "#014BAA"],
  ];
  UI.forEach(([label, img, size, pos, w, h, bg], i) => {
    shot(D(7) + i * 0.4, D(7) + (i + 1) * 0.4, bg, (r) => {
      const s = {};
      s.c = el("div", null, null, r, { position: "absolute", left: (W - w) / 2 + "px", top: (H - h) / 2 - 40 + "px", width: w + "px", height: h + "px", borderRadius: "40px", backgroundImage: img, backgroundSize: size, backgroundPosition: pos, backgroundRepeat: "no-repeat", backgroundColor: "#fff", boxShadow: "0 50px 100px rgba(0,0,0,.35)" });
      s.l = el("div", "micro", label, r); at(s.l, 0, (H + h) / 2 + 20, { width: W + "px", textAlign: "center", color: bg === "#F8F3F0" ? "#014BAA" : "#FFC83D" });
      return s;
    }, (t, s) => {
      const p = P(t, 0, 0.18, E.expo);
      s.c.style.transform = `translateZ(${lerp(500, 0, p) + t * 120}px) rotateY(${lerp(i % 2 ? -32 : 32, i % 2 ? -6 : 6, p)}deg) rotateX(${lerp(12, 4, p)}deg)`;
      reveal(s.l, P(t, 0.06, 0.15), { y: 14, blur: 6 });
    });
  });

  // I · the question
  shot(D(8), D(9), "#c58db8", (r) => {
    const s = { bg: el("div", "photo", null, r, { backgroundImage: `url(${A}field-dusk.jpg)` }) };
    const sh = { textShadow: "0 6px 50px rgba(60,20,60,.3)", color: "#F8F3F0", width: W + "px", textAlign: "center" };
    s.l1 = el("div", "serif", null, r); at(s.l1, 0, 560, { ...sh, fontSize: "150px" }); s.a = words(s.l1, "Bagaimana kalau");
    s.l2 = el("div", "serif", null, r); at(s.l2, 0, 720, { ...sh, fontSize: "150px" }); s.b = words(s.l2, "ada yang");
    s.l3 = el("div", "serif", null, r); at(s.l3, 0, 880, { ...sh, fontSize: "200px" }); s.c = words(s.l3, "*cek* *dulu*?");
    return s;
  }, (t, s) => {
    s.bg.style.transform = `scale(${lerp(1.12, 1.24, P(t, 0, 1.6, E.lin))}) translateX(${lerp(30, -30, P(t, 0, 1.6, E.inOut))}px)`;
    stagger(s.a, t, 0.0, 0.1, 0.35);
    stagger(s.b, t, 0.4, 0.1, 0.35);
    stagger(s.c, t, 0.8, 0.14, 0.45);
  });

  // J · macro tease of the mark, rim light only
  shot(D(9), D(10), "#04070d", (r) => {
    const s = {};
    s.m = mark3D(r, 980, 160); at(s.m.o, 120, 520);
    s.m.o.style.filter = "brightness(.62) saturate(1.15) contrast(1.1)";
    s.sweep = el("div", null, null, s.m.face, { position: "absolute", inset: "-20%", background: "linear-gradient(105deg, rgba(255,255,255,0) 40%, rgba(255,255,255,.95) 50%, rgba(255,255,255,0) 60%)", mixBlendMode: "screen" });
    s.k = el("div", "micro", "Segera.", r); at(s.k, 0, 1540, { width: W + "px", textAlign: "center", color: "rgba(248,243,240,.75)", letterSpacing: ".6em" });
    return s;
  }, (t, s) => {
    const p = P(t, 0, 1.6, E.inOut);
    s.m.o.style.transform = `translateZ(${lerp(380, 260, p)}px) rotateY(${lerp(58, 24, p)}deg) rotateX(${lerp(18, 10, p)}deg) rotateZ(-6deg)`;
    s.sweep.style.transform = `translateX(${lerp(-90, 90, P(t, 0.2, 1.2, E.inOut))}%)`;
    reveal(s.k, P(t, 0.8, 0.5), { y: 10, max: 1 });
  });

  // K · what it stands for
  wordBeats(D(10), [
    ["Jujur.", "#014BAA", "#F8F3F0", 300],
    ["Bersumber.", "#F8F3F0", "#014BAA", 200],
    ["Tanpa\nmenebak.", "#0E1726", "#FFC83D", 210],
    ["Untuk\nkeluarga.", "#FFC83D", "#0E1726", 210, true],
  ]);

  // L · confetti forms a circle over the meadow (orbiting camera)
  shot(D(11), D(12), "#2f5a1f", (r) => {
    const s = { bg: el("div", "photo", null, r, { backgroundImage: `url(${A}field-meadow.jpg)` }) };
    el("div", null, null, r, { position: "absolute", inset: 0, background: "radial-gradient(60% 40% at 50% 50%, rgba(14,23,38,.0), rgba(14,23,38,.35))" });
    const R = rand(77); s.c = [];
    for (let i = 0; i < 34; i++) {
      const size = 50 + R() * 50, n = el("div", null, shapeSVG(KINDS[i % 5], PALETTE[i % 4], size), r);
      at(n, W / 2 - size / 2, 980 - size / 2);
      s.c.push({ n, x0: (R() - 0.5) * 1400, y0: (R() - 0.5) * 2000, a: (i / 34) * Math.PI * 2, rot: R() * 360 });
    }
    const sh = { color: "#F8F3F0", width: W + "px", textAlign: "center", textShadow: "0 6px 40px rgba(0,0,0,.35)" };
    s.l1 = el("div", "serif", null, r); at(s.l1, 0, 860, { ...sh, fontSize: "110px" }); s.a = words(s.l1, "Lini pertama");
    s.l2 = el("div", "serif", null, r); at(s.l2, 0, 975, { ...sh, fontSize: "110px" }); s.b = words(s.l2, "pertahanan *kognitif*.");
    return s;
  }, (t, s) => {
    s.bg.style.transform = `scale(1.35) rotate(${lerp(-6, 10, P(t, 0, 1.6, E.lin))}deg)`;
    const g = P(t, 0, 0.9, E.expo);
    s.c.forEach((c) => {
      const a = c.a + t * 0.9, rad = 440;
      const x = lerp(c.x0, Math.cos(a) * rad, g), y = lerp(c.y0, Math.sin(a) * rad, g);
      c.n.style.transform = `translate(${x}px, ${y}px) rotate(${c.rot + t * 90}deg)`;
    });
    stagger(s.a, t, 0.4, 0.1, 0.35);
    stagger(s.b, t, 0.75, 0.1, 0.35);
  });

  // M · hyperspace rings, speeding up
  shot(D(12), D(13), "radial-gradient(70% 50% at 50% 50%, #0A5BC9 0%, #013a85 45%, #05080f 100%)", (r) => {
    const s = { rings: [] };
    const col = ["#F8F3F0", "#FFC83D", "#0A5BC9", "#F8F3F0", "#8B5CF6"];
    for (let i = 0; i < 18; i++) {
      const n = el("div", null, null, r, { position: "absolute", left: W / 2 - 520 + "px", top: H / 2 - 520 + "px", width: "1040px", height: "1040px", borderRadius: i % 3 === 2 ? "120px" : "50%", border: `${i % 2 ? 6 : 14}px solid ${col[i % 5]}` });
      s.rings.push({ n, z: -i * 420, rot: i * 17 });
    }
    s.k = el("div", "micro", "Kartika Cyber Hackathon 2026", r); at(s.k, 0, H / 2 - 13, { width: W + "px", textAlign: "center", color: "#F8F3F0" });
    return s;
  }, (t, s) => {
    const cam = lerp(0, 7600, P(t, 0, 1.6, E.inQuad));
    s.rings.forEach((g) => {
      const z = g.z + cam;
      const vis = z < 1200 && z > -7600;
      g.n.style.visibility = vis ? "visible" : "hidden";
      if (!vis) return;
      g.n.style.transform = `translateZ(${z}px) rotate(${g.rot + t * 60}deg)`;
      g.n.style.opacity = clamp((z + 7600) / 2500) * clamp((1200 - z) / 400);
    });
    s.k.textContent = Math.floor(t / 0.2) % 2 ? "Kategori Siber Sosial" : "Kartika Cyber Hackathon 2026";
    s.k.style.opacity = 0.5 + 0.5 * (Math.floor(t * 10) % 2);
  });

  // N · breakdown: heartbeat in the dark
  shot(D(13), D(14), "#000", (r) => {
    const s = {};
    s.glow = el("div", null, null, r, { position: "absolute", left: W / 2 - 380 + "px", top: H / 2 - 380 + "px", width: "760px", height: "760px", borderRadius: "50%", background: "radial-gradient(closest-side, rgba(1,75,170,.75), rgba(1,75,170,0))" });
    s.txt = el("div", "serif", "", r); at(s.txt, 0, H / 2 - 50, { width: W + "px", textAlign: "center", fontSize: "92px", color: "#F8F3F0" });
    s.full = "untuk keluarga Indonesia.";
    return s;
  }, (t, s) => {
    const beat = [0.0, 0.4, 0.8, 1.0].reduce((acc, b) => acc + Math.exp(-Math.max(0, t - b) * 9) * (t >= b ? 1 : 0), 0);
    s.glow.style.opacity = 0.25 + 0.5 * clamp(beat);
    s.glow.style.transform = `scale(${0.8 + 0.2 * clamp(beat)})`;
    const n = Math.floor(s.full.length * P(t, 0.3, 0.9, E.lin));
    s.txt.textContent = s.full.slice(0, n) + (n < s.full.length && Math.floor(t * 8) % 2 ? "|" : "");
    s.txt.style.opacity = 1 - P(t, 1.4, 0.2);
  });

  // O · reveal
  shot(D(14), DUR + 1, "radial-gradient(80% 55% at 50% 42%, #1366d6 0%, #014BAA 45%, #012a63 100%)", (r) => {
    const s = {};
    s.rays = el("div", null, null, r, { position: "absolute", left: W / 2 - 1400 + "px", top: 820 - 1400 + "px", width: "2800px", height: "2800px", background: "repeating-conic-gradient(from 0deg, rgba(255,255,255,.10) 0deg 6deg, rgba(255,255,255,0) 6deg 18deg)", borderRadius: "50%", maskImage: "radial-gradient(closest-side, #000 20%, transparent 70%)", WebkitMaskImage: "radial-gradient(closest-side, #000 20%, transparent 70%)" });
    const R = rand(9); s.burst = [];
    for (let i = 0; i < 40; i++) {
      const size = 40 + R() * 60, n = el("div", null, shapeSVG(KINDS[i % 5], PALETTE[i % 4], size), r);
      at(n, W / 2 - size / 2, 820 - size / 2);
      const a = R() * Math.PI * 2, sp = 900 + R() * 1300;
      s.burst.push({ n, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 300, vz: (R() - 0.3) * 1600, rot: R() * 360, spin: (R() - 0.5) * 720 });
    }
    s.m = mark3D(r, 380, 80); at(s.m.o, W / 2 - 190, 630);
    s.word = el("div", "serif", 'halio<span style="color:#FFC83D">.</span>', r); at(s.word, 0, 1060, { width: W + "px", textAlign: "center", fontSize: "250px", color: "#F8F3F0" });
    s.tag = el("div", null, "Cek dulu, baru teruskan.", r); at(s.tag, 0, 1330, { width: W + "px", textAlign: "center", font: "600 46px Inter", color: "rgba(248,243,240,.92)" });
    s.stamp = el("div", "grot", "Segera hadir", r); at(s.stamp, 0, 1420, { width: W + "px", display: "flex", justifyContent: "center" });
    s.stamp.innerHTML = `<span style="background:#FFC83D;color:#0E1726;font-size:78px;padding:26px 46px;border-radius:999px;box-shadow:0 20px 50px rgba(0,0,0,.3)">Segera hadir</span>`;
    s.meta = el("div", "micro", "Kartika Cyber Hackathon 2026 · Siber Sosial", r); at(s.meta, 0, 1585, { width: W + "px", textAlign: "center", color: "rgba(248,243,240,.8)", fontSize: "22px" });
    return s;
  }, (t, s) => {
    s.rays.style.transform = `rotate(${t * 12}deg) scale(${lerp(0.6, 1, P(t, 0, 0.8, E.expo))})`;
    s.rays.style.opacity = P(t, 0, 0.3);
    s.burst.forEach((b) => {
      const k = Math.min(t, 1.6);
      const x = b.vx * (1 - Math.exp(-k * 2.2)) / 2.2, y = b.vy * (1 - Math.exp(-k * 2.2)) / 2.2 + 260 * k * k, z = b.vz * (1 - Math.exp(-k * 2)) / 2;
      b.n.style.transform = `translate3d(${x}px, ${y}px, ${z}px) rotate(${b.rot + b.spin * k}deg)`;
      b.n.style.opacity = clamp(1 - (t - 0.9) / 0.7);
    });
    const p = P(t, 0, 0.65, E.expo), land = P(t, 0.55, 0.5, E.back);
    const float = Math.sin(t * 2.2) * 10;
    s.m.o.style.transform = `translateY(${float}px) translateZ(${lerp(-3200, 0, p)}px) rotateY(${lerp(720, 0, p) + Math.sin(t * 1.4) * 10 * land}deg) rotateX(${lerp(40, 0, p) + 6}deg) scale(${lerp(0.9, 1, land)})`;
    s.m.o.style.opacity = P(t, 0, 0.1);
    reveal(s.word, P(t, 0.4, 0.5), { y: 40, blur: 24 });
    reveal(s.tag, P(t, 0.8, 0.45), { y: 20 });
    const st = P(t, D(15) - D(14), 0.22, E.back);
    s.stamp.style.opacity = P(t, D(15) - D(14), 0.05);
    s.stamp.style.transform = `scale(${lerp(1.8, 1, st)}) rotate(${lerp(-8, -2, st)}deg)`;
    reveal(s.meta, P(t, D(15) - D(14) + 0.2, 0.3), { y: 10 });
  });

  // ---------- global camera, flashes, light leaks ----------
  const HITS = [[0.41, .4], [2.41, 1.1], [2.81, .8], [3.61, 1], [4.01, 1], [4.41, 1], [4.81, 1.3], [5.21, .6], [6.81, .6], [8.41, .5], [9.21, .6], [10.01, .8],
    [11.61, .8], [12.01, .8], [12.41, .8], [12.81, .8], [13.21, .4], [16.41, 1], [16.81, 1], [17.21, 1], [17.61, 1.3], [18.01, .5], [19.61, .6], [21.21, 1], [22.81, 1.8], [24.41, 1.1]];
  const FLASH = [[6.81, .75, 7], [11.61, .4, 12], [12.01, .3, 12], [12.41, .3, 12], [12.81, .3, 12], [21.21, .6, 6], [22.81, 1.0, 3.2], [24.41, .35, 8]];
  const LEAK = [[6.81, 8.41, "#ffcf7a"], [13.21, 14.81, "#ff8fb1"], [18.01, 19.61, "#ffe08a"], [22.81, 26, "#9cc3ff"]];
  const cam = document.getElementById("cam"), flash = document.getElementById("flash"), leak = document.getElementById("leak"), grain = document.getElementById("grain");

  function seek(T, frame = Math.round(T * 60)) {
    for (const sh of SHOTS) {
      const vis = T >= sh.t0 && T < sh.t1;
      sh.root.style.visibility = vis ? "visible" : "hidden";
      if (vis) {
        sh.root.querySelectorAll("[data-fit]").forEach((n) => fit(n, W - 120));
        sh.update(T - sh.t0, sh.s, T);
      }
    }
    let sh = 0;
    for (const [h, a] of HITS) if (T >= h) sh += a * Math.exp(-(T - h) * 9);
    const n1 = Math.sin(T * 91.7) + Math.sin(T * 53.3 + 1.7), n2 = Math.cos(T * 77.1) + Math.sin(T * 41.9 + 0.3);
    cam.style.transform = `translate(${n1 * sh * 9}px, ${n2 * sh * 9}px) rotate(${n1 * sh * 0.35}deg) scale(${1 + sh * 0.012})`;
    let f = 0;
    for (const [t0, a, d] of FLASH) if (T >= t0) f = Math.max(f, a * Math.exp(-(T - t0) * d));
    flash.style.opacity = f;
    let lk = 0, lc = "#fff";
    for (const [a, b, c] of LEAK) if (T >= a && T < b) { lk = Math.sin(((T - a) / (b - a)) * Math.PI) * 0.45; lc = c; }
    leak.style.opacity = lk;
    leak.style.background = `radial-gradient(60% 40% at ${30 + 40 * Math.sin(T * 0.9)}% ${20 + 10 * Math.cos(T * 0.7)}%, ${lc}, rgba(0,0,0,0) 70%)`;
    const g = rand(Math.floor(frame / 6) + 3);
    grain.style.backgroundPosition = `${Math.floor(g() * 512)}px ${Math.floor(g() * 512)}px`;
  }

  async function ready() {
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => (i.complete ? i.decode().catch(() => {}) : new Promise((r) => { i.onload = i.onerror = r; }))));
    const urls = new Set();
    document.querySelectorAll("[style*='url(']").forEach((n) => { const m = n.style.backgroundImage.match(/url\("?(.*?)"?\)/); if (m) urls.add(m[1]); });
    await Promise.all([...urls].map((u) => new Promise((r) => { const i = new Image(); i.onload = i.onerror = r; i.src = u; })));
    return true;
  }
  window.Story = { seek, ready, DUR, W, H };
})();

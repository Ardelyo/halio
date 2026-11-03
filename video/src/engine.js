// Deterministic animation engine: Engine.seek(t) puts every element where it belongs at time t.
// No CSS transitions or timers, so each rendered frame is exact and repeatable.
(() => {
  const TL = window.TIMELINE;
  const FADE = 0.6; // scene cross-dissolve

  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ease = {
    out: (t) => 1 - Math.pow(1 - t, 3),
    inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
    back: (t) => { const c1 = 1.5, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); },
    expo: (t) => (t >= 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  };
  const P = (t, a, d, e = ease.out) => e(clamp((t - a) / Math.max(1e-6, d)));
  const lerp = (a, b, p) => a + (b - a) * p;

  function el(tag, cls, html, parent, style) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    if (style) Object.assign(n.style, style);
    if (parent) parent.appendChild(n);
    return n;
  }

  // Blur-to-sharp reveal used everywhere (reference: kinetic type reveals).
  function reveal(n, p, o = {}) {
    const y = o.y ?? 26, x = o.x ?? 0, blur = o.blur ?? 14, s = o.scale;
    n.style.opacity = o.max != null ? p * o.max : p;
    let tr = `translate(${(1 - p) * x}px, ${(1 - p) * y}px)`;
    if (s != null) tr += ` scale(${lerp(s, 1, p)})`;
    if (o.rot != null) tr += ` rotate(${o.rot}deg)`;
    n.style.transform = tr;
    n.style.filter = p >= 0.999 || !blur ? "none" : `blur(${(1 - p) * blur}px)`;
  }

  // "*kata*" -> italic accent. Returns the word spans for staggered reveals.
  function words(parent, text) {
    const spans = [];
    text.split(/(\s+)/).forEach((tok) => {
      if (!tok) return;
      if (/^\s+$/.test(tok)) { parent.appendChild(document.createTextNode(" ")); return; }
      const m = tok.match(/^\*(.+)\*([.,:;!?]*)$/);
      const s = el("span", "w", null, parent);
      if (m) { el("em", null, m[1], s); if (m[2]) s.appendChild(document.createTextNode(m[2])); }
      else s.textContent = tok.replace(/\*/g, "");
      spans.push(s);
    });
    return spans;
  }
  function stagger(spans, t, start, per = 0.07, dur = 0.7, o = {}) {
    spans.forEach((s, i) => reveal(s, P(t, start + i * per, dur), { y: 20, blur: 12, ...o }));
  }

  // Deterministic pseudo-random for confetti and waveforms.
  function rand(seed) {
    let a = seed >>> 0;
    return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }

  const PALETTE = ["#FFC83D", "#8B5CF6", "#FF8A3D", "#2FBF71"];
  function shape(kind, color, size) {
    const s = size, h = s / 2;
    const paths = {
      half: `<path d="M0 ${h}A${h} ${h} 0 0 1 ${s} ${h}Z" fill="${color}"/>`,
      quarter: `<path d="M0 ${s}A${s} ${s} 0 0 1 ${s} 0L${s} ${s}Z" fill="${color}"/>`,
      ring: `<path d="M${s * 0.12} ${s}A${s * 0.88} ${s * 0.88} 0 0 1 ${s} ${s * 0.12}" fill="none" stroke="${color}" stroke-width="${s * 0.22}" stroke-linecap="round"/>`,
      dot: `<circle cx="${h}" cy="${h}" r="${h}" fill="${color}"/>`,
      bar: `<rect x="0" y="${s * 0.36}" width="${s}" height="${s * 0.28}" rx="${s * 0.14}" fill="${color}"/>`,
    };
    return `<svg width="${s}" height="${s}" viewBox="0 0 ${s} ${s}" overflow="visible">${paths[kind]}</svg>`;
  }
  const SHAPES = ["half", "quarter", "ring", "dot", "bar"];

  const registry = {};
  const built = [];

  function cueStart(sc, i) { return sc.cues[Math.min(i, sc.cues.length - 1)].t0; }
  function cueEnd(sc, i) { return sc.cues[Math.min(i, sc.cues.length - 1)].t1; }

  function init() {
    const host = document.getElementById("scenes");
    TL.scenes.forEach((sc, idx) => {
      const def = registry[sc.id];
      if (!def) throw new Error("scene not defined: " + sc.id);
      const root = el("section", `scene ${def.bg || ""} ${def.dark ? "dark" : ""}`, null, host);
      root.style.zIndex = idx + 1;
      const state = def.build(root, sc) || {};
      built.push({ sc, def, root, state });
    });
  }

  let lastTag = null;
  function seek(T, frame = Math.round(T * TL.fps)) {
    let current = built[0];
    for (const b of built) {
      const lt = T - b.sc.start;
      const visible = lt >= 0 && lt < b.sc.dur + FADE;
      b.root.style.visibility = visible ? "visible" : "hidden";
      if (!visible) continue;
      if (lt < b.sc.dur) current = b;
      b.root.style.opacity = b === built[0] ? P(lt, 0, 0.8, ease.inOut) : P(lt, 0, FADE, ease.inOut);
      b.def.update(lt, b.state, b.sc);
    }
    const tag = document.getElementById("tag"), brand = document.getElementById("brand");
    const lt = T - current.sc.start;
    if (lastTag !== current.sc.tag) { tag.textContent = current.sc.tag; lastTag = current.sc.tag; }
    tag.className = "tag" + (current.def.dark ? " dark" : "");
    tag.style.opacity = P(lt, 0.25, 0.5) * (current.def.noChrome ? 0 : 1);
    brand.className = "brand" + (current.def.dark ? " dark" : "");
    brand.style.opacity = current.def.noChrome || current.def.noBrand ? 0 : P(lt, 0.25, 0.5);
    const g = rand(Math.floor(frame / 3) + 1); // film grain at 10 fps: cinematic, and compresses far better
    document.getElementById("grain").style.backgroundPosition = `${Math.floor(g() * 256)}px ${Math.floor(g() * 256)}px`;
  }

  async function ready() {
    await document.fonts.ready;
    const imgs = [...document.images];
    await Promise.all(imgs.map((i) => (i.complete ? i.decode().catch(() => {}) : new Promise((r) => { i.onload = i.onerror = r; }))));
    // CSS background images
    const urls = new Set();
    document.querySelectorAll(".photo").forEach((n) => { const m = n.style.backgroundImage.match(/url\("?(.*?)"?\)/); if (m) urls.add(m[1]); });
    await Promise.all([...urls].map((u) => new Promise((r) => { const i = new Image(); i.onload = i.onerror = r; i.src = u; })));
    return true;
  }

  window.Engine = { TL, P, ease, lerp, clamp, el, reveal, words, stagger, rand, shape, SHAPES, PALETTE, registry, init, seek, ready, cueStart, cueEnd };
})();

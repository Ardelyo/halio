// Halio Luring: mesin cek di perangkat (jalur T1, tanpa AI & tanpa jaringan).
// Port dr backend/halio/{textnorm,retrieval,claims,pii,manipulation,attribution,pipeline}.py. Daftar kata, pola regex, dan korpus
// diambil dr data.js (digenerate dr python), logika vonisnya ditulis ulang di sini dan dijaga SAMA lewat uji paritas:
//   node web/engine/parity.test.mjs   (bandingin sm backend/tests/parity_vectors.json, hasil python)
// Yg sengaja ga ada di sini: cek tautan, bukti web, AI, media. Kabar di luar korpus tetap "belum ada pemeriksaan", ga ditebak.
(function (root) {
  "use strict";
  const D = root.HalioEngineData;
  const api = { available: false, version: D ? D.version : null };
  root.HalioLocal = api;
  if (!D) return;

  // lookbehind dipake di beberapa pola; browser lawas (mis. Safari < 16.4) bakal error, jadi mesin dimatiin & UI pake jalur lama
  try { new RegExp("(?<=a)b"); } catch (e) { return; }

  // ---------- util mirip python ----------
  const pyRound = (x, n) => Number(x.toFixed(n)); // python round(): sama utk skor non-dyadic
  const slang = new Map(Object.entries(D.slang));
  const stop = new Set(D.stopwords);
  const cues = new Set(D.claimCues);
  const re = (p, f) => new RegExp(p, f || "");
  const R = {
    negation: re(D.regex.negation), defused: re(D.regex.defused), correction: re(D.regex.correction),
    notCorrection: re(D.regex.notCorrection), pipelineUrl: re(D.regex.pipelineUrl, "i"),
    url: D.regex.url, bare: D.regex.bare, bareWithPath: D.regex.bareWithPath,
  };
  const SCRUB = [[re(D.regex.url, "gi"), "[TAUTAN]"], [re(D.regex.bareWithPath, "gi"), "[TAUTAN]"]]
    .concat(D.scrub.map(([p, repl]) => [re(p, "g"), repl]));
  const TECH = D.techniques.map(([id, label, explain, lesson, pats]) => ({ id, label, explain, lesson, pats: pats.map((p) => re(p)) }));
  const ORGS = Object.entries(D.orgs).map(([name, pat]) => [name, re("\\b(?:" + pat + ")\\b")]);
  const SENT_SPLIT = /(?<=[.!?…])\s+|\n+/;
  const sortedStr = (arr) => arr.slice().sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));

  // ---------- textnorm ----------
  function fold(text) {
    return text.normalize("NFKD").replace(/\p{M}/gu, "").toLowerCase();
  }
  function tokens(text, dropStop = true) {
    const out = [];
    for (let tok of fold(text).match(/[a-z0-9]+/g) || []) {
      if (slang.has(tok)) tok = slang.get(tok);
      tok = tok.replace(/(.)\1{2,}/g, "$1");
      if (dropStop && (stop.has(tok) || tok.length < 2)) continue;
      out.push(tok);
    }
    return out;
  }
  const normalized = (t) => tokens(t).join(" ");

  // ---------- pii ----------
  function scrub(text, maxChars = 300) {
    let out = text;
    for (const [rx, repl] of SCRUB) out = out.replace(rx, repl);
    out = out.replace(/\s+/g, " ").trim();
    const cps = Array.from(out); // python ngitung per karakter, bukan per unit utf-16 (beda utk emoji)
    if (cps.length > maxChars) {
      const cut = cps.slice(0, maxChars - 1).join("");
      const i = cut.lastIndexOf(" ");
      out = (i < 0 ? cut : cut.slice(0, i)) + "…";
    }
    return out;
  }
  function hostOf(url) {
    if (!/^https?:\/\//i.test(url)) url = "http://" + url;
    let rest = url.replace(/^https?:\/\//i, "").split(/[/?#]/)[0];
    rest = rest.slice(rest.lastIndexOf("@") + 1).replace(/:\d*$/, "");
    return rest.toLowerCase().replace(/\.+$/, "").replace(/^www\./, "");
  }
  function extractDomains(text) {
    const domains = [];
    for (const url of text.match(re(R.url, "gi")) || []) {
      const host = hostOf(url.replace(/[.,)!?]+$/, ""));
      if (host && !domains.includes(host)) domains.push(host);
    }
    const stripped = text.replace(re(R.url, "gi"), " ");
    for (const m of stripped.matchAll(re(R.bare, "gi"))) {
      const host = m[1].toLowerCase().replace(/^www\./, "");
      if (!domains.includes(host)) domains.push(host);
    }
    return domains;
  }

  // ---------- retrieval ----------
  const wordFeats = (text) => {
    const toks = tokens(text), c = new Map();
    const add = (f) => c.set(f, (c.get(f) || 0) + 1);
    toks.forEach(add);
    for (let i = 0; i + 1 < toks.length; i++) add(toks[i] + "_" + toks[i + 1]);
    return c;
  };
  const charFeats = (text) => {
    const s = " " + normalized(text) + " ", c = new Map();
    for (let i = 0; i + 3 <= s.length; i++) { const g = s.slice(i, i + 3); c.set(g, (c.get(g) || 0) + 1); }
    return c;
  };
  class TfIdf {
    constructor(docs) {
      const n = docs.length, df = new Map();
      for (const d of docs) for (const f of d.keys()) df.set(f, (df.get(f) || 0) + 1);
      this.idf = new Map();
      for (const [f, c] of df) this.idf.set(f, Math.log((1 + n) / (1 + c)) + 1);
      this.vecs = docs.map((d) => this.vec(d));
    }
    vec(feats) {
      const v = new Map();
      let sq = 0;
      for (const [f, c] of feats) { const x = (1 + Math.log(c)) * (this.idf.has(f) ? this.idf.get(f) : 0); v.set(f, x); sq += x * x; }
      const norm = Math.sqrt(sq) || 1.0;
      for (const [f, x] of v) v.set(f, x / norm);
      return v;
    }
    scores(feats) {
      const q = this.vec(feats);
      return this.vecs.map((d) => { let s = 0; for (const [f, w] of q) s += w * (d.has(f) ? d.get(f) : 0); return s; });
    }
  }
  const debunks = D.corpus.map((d) => Object.assign({
    varian: [], syarat: [], jenis: "bantahan", kutipan_sumber: "", valid_from: null, valid_until: null, wilayah: "",
  }, d));
  const isPositive = (d) => d.jenis === "verifikasi_positif";
  const rows = [];
  for (const d of debunks) for (const t of [d.klaim].concat(d.varian)) rows.push([d, t]);
  const wordIdx = new TfIdf(rows.map(([, t]) => wordFeats(t)));
  const charIdx = new TfIdf(rows.map(([, t]) => charFeats(t)));
  const byScoreDesc = (a, b) => b.score - a.score; // sort JS stabil, sama kaya python sorted(reverse=True)

  function search(query, k = 3) {
    const ws = wordIdx.scores(wordFeats(query)), cs = charIdx.scores(charFeats(query));
    const best = new Map();
    rows.forEach(([deb, text], i) => {
      const score = 0.5 * ws[i] + 0.5 * cs[i];
      if (!best.has(deb.id) || score > best.get(deb.id).score) best.set(deb.id, { debunk: deb, score: pyRound(score, 3), matched_text: text });
    });
    return [...best.values()].sort(byScoreDesc).slice(0, k);
  }
  function isCorrection(text) {
    const low = fold(text);
    return R.correction.test(low) && !R.notCorrection.test(low);
  }
  function corePresent(d, text) {
    const low = fold(text);
    for (const group of d.syarat) {
      let any = false;
      for (const m of low.matchAll(re(group, "g"))) {
        const start = m.index, end = start + m[0].length;
        if (!R.negation.test(low.slice(Math.max(0, start - 16), start)) && !R.defused.test(low.slice(end, end + 24))) { any = true; break; }
      }
      if (!any) return false;
    }
    return true;
  }

  // ---------- claims ----------
  function sentences(text) {
    return text.split(SENT_SPLIT).map((s) => s.trim()).filter((s) => s.length > 3);
  }
  function checkworthiness(sentence) {
    const low = fold(sentence);
    if (sentence.trim().endsWith("?") && !/\d/.test(sentence)) return 0.05;
    const toks = tokens(sentence);
    if (!toks.length) return 0.0;
    let score = 0.0;
    score += Math.min(0.45, 0.15 * toks.filter((t) => cues.has(t)).length);
    if (/\d/.test(sentence)) score += 0.2;
    if (/(?<=\s)[A-Z][a-z]{2,}/.test(sentence)) score += 0.15;
    if (toks.length >= 5) score += 0.15;
    if (D.opinionCues.some((c) => low.includes(c))) score -= 0.4;
    return Math.max(0.0, Math.min(1.0, score));
  }
  function extract(text, maxSentences = 2) {
    let sents = sentences(text);
    if (!sents.length) sents = [text];
    const scored = sents.map((s, i) => [checkworthiness(s), i, s]);
    scored.sort((a, b) => (b[0] - a[0]) || (b[1] - a[1])); // python: sorted(tuple, reverse=True)
    const top = scored.slice(0, maxSentences).sort((a, b) => a[1] - b[1]);
    const best = scored[0][0];
    const chosen = top.filter(([sc]) => sc >= Math.max(0.2, best * 0.5)).map((x) => x[2]).join(" ") || scored[0][2];
    return { text: scrub(chosen), score: best, is_factual: best >= 0.3 };
  }
  function same(a, b) {
    const ta = new Set(tokens(a)), tb = new Set(tokens(b));
    if (!ta.size || !tb.size) return false;
    let inter = 0;
    for (const t of ta) if (tb.has(t)) inter++;
    return inter / (ta.size + tb.size - inter) >= 0.6;
  }
  function splitUnits(text, maxUnits = 3, minScore = 0.5, minTokens = 5) {
    const sents = sentences(text), marks = [];
    sents.forEach((s, i) => {
      if (checkworthiness(s) >= minScore && tokens(s).length >= minTokens && !marks.some((j) => same(s, sents[j]))) marks.push(i);
    });
    if (marks.length < 2) return [];
    const use = marks.slice(0, maxUnits);
    return use.map((start, k) => sents.slice(start, k + 1 < use.length ? use[k + 1] : sents.length).join(" "));
  }

  // ---------- manipulation ----------
  const isUpper = (c) => c !== c.toLowerCase() && c === c.toUpperCase();
  function analyze(text) {
    const low = fold(text), found = [];
    for (const t of TECH) {
      const hits = new Set();
      for (const p of t.pats) for (const m of low.matchAll(new RegExp(p.source, "g"))) hits.add(m[0]);
      if (hits.size) found.push({ id: t.id, label: t.label, explain: t.explain, lesson: t.lesson, evidence: sortedStr([...hits]).slice(0, 3) });
    }
    const letters = [...text].filter((c) => /\p{L}/u.test(c));
    const caps = letters.filter(isUpper).length / Math.max(1, letters.length);
    const shouting = (letters.length > 30 && caps > 0.6) || text.includes("!!!");
    const score = Math.min(1.0, 0.25 * found.length + (shouting ? 0.15 : 0.0));
    return { techniques: found, shouting, score: pyRound(score, 2), needs_check: score >= 0.5 };
  }

  // ---------- attribution ----------
  function orgsIn(text) {
    const low = fold(text), found = new Set(ORGS.filter(([, rx]) => rx.test(low)).map(([n]) => n));
    const spec = new Set([...found].filter((n) => n !== "Pemerintah"));
    return spec.size ? spec : found;
  }
  function mismatch(message, debunkText) {
    const said = orgsIn(message), covered = orgsIn(debunkText);
    if (!said.size || !covered.size || [...said].some((n) => covered.has(n))) return null;
    const sa = sortedStr([...said]), sb = sortedStr([...covered]), a = sa.join(", "), b = sb.join(", ");
    return {
      pesan: sa, bantahan: sb,
      catatan: `Pesan ini menyebut ${a} sebagai sumber, sedangkan bantahan yang cocok membahas klaim serupa yang dikaitkan dengan ${b}. ` +
        `Mencatut nama lembaga adalah trik yang umum. Periksa langsung ke kanal resmi ${a}.`,
    };
  }

  // ---------- pipeline (T1) ----------
  const uuid = () => (root.crypto && root.crypto.randomUUID ? root.crypto.randomUUID().replace(/-/g, "")
    : Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join(""));
  const hasKumpulanJudul = (text) => {
    if (R.pipelineUrl.test(text)) return null;
    const lines = text.split(new RegExp("\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]")).map((l) => l.trim()).filter(Boolean);
    const short = lines.filter((l) => l.split(/\s+/).length <= 12 && !/[.?!]$/.test(l));
    return lines.length >= 3 && short.length >= 0.8 * lines.length ? { judul_list: lines.slice(0, 8) } : null;
  };
  function searchSentences(claimText, k = 3, minTokens = 5) {
    const best = new Map(search(claimText, debunks.length).map((m) => [m.debunk.id, m]));
    const parts = sentences(claimText).filter((p) => tokens(p).length >= minTokens);
    if (parts.length >= 2) {
      for (const part of parts) for (const m of search(part, debunks.length)) {
        if (!best.has(m.debunk.id) || m.score > best.get(m.debunk.id).score) best.set(m.debunk.id, m);
      }
    }
    return [...best.values()].sort(byScoreDesc).slice(0, k);
  }
  const quotePlus = (s) => encodeURIComponent(s).replace(/[!'()*]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase()).replace(/%20/g, "+");
  function searchLinks(claim) {
    const q = quotePlus(Array.from(claim.split(/\s+/).filter(Boolean).join(" ")).slice(0, 140).join(""));
    return [
      { nama: "Cari beritanya di Google", url: `https://www.google.com/search?q=${q}` },
      { nama: 'Cari di Google dengan kata "hoaks" / "cek fakta"', url: `https://www.google.com/search?q=${q}+hoaks+OR+%22cek+fakta%22` },
      { nama: "Cari di TurnBackHoax", url: `https://turnbackhoax.id/?s=${q}` },
    ];
  }
  function linkWarnings(domains) {
    const out = [];
    for (const d of domains) {
      if (D.officialSuffixes.some((s) => d.endsWith(s))) continue;
      out.push(D.shorteners.includes(d)
        ? `Tautan ${d} menyembunyikan alamat aslinya. Jangan diklik sebelum tahu tujuannya.`
        : `Tautan ${d} bukan situs pemerintah (.go.id). Hati-hati bila diminta mengisi data.`);
    }
    return out;
  }
  const matchPayload = (m) => {
    const d = m.debunk;
    return {
      debunk_id: d.id, kategori: d.kategori, score: m.score, klaim_dibantah: d.klaim, fakta: d.fakta, sederhana: d.sederhana,
      sumber: d.sumber, jenis: d.jenis, kutipan_sumber: d.kutipan_sumber, valid_from: d.valid_from, valid_until: d.valid_until, wilayah: d.wilayah,
    };
  };
  function voice(status, reason, sapaan, match, manip) {
    if (reason === "kumpulan_judul") {
      return `${sapaan}, gambar ini berisi beberapa judul berita sekaligus. Kirim satu judul atau satu berita per pesan, supaya Halio bisa memeriksanya satu per satu.`;
    }
    if (status === "terbukti_salah" && match) {
      const src = match.debunk.sumber[0].nama.split(":")[0];
      return `${sapaan}, pesan ini sudah dicek dan ternyata tidak benar. ${match.debunk.sederhana} Sumbernya dari ${src}. Sebaiknya jangan diteruskan, ya.`;
    }
    if (status === "tidak_yakin" && match && reason === "tampak_meluruskan") {
      return `${sapaan}, pesan ini tampaknya justru memperingatkan soal kabar bohong, bukan menyebarkannya. Yang sudah dicek: ${match.debunk.sederhana}`;
    }
    if (status === "tidak_yakin" && match && reason === "inti_klaim_tidak_ada" && !isPositive(match.debunk)) {
      return `${sapaan}, topik pesan ini sama dengan kabar bohong yang pernah beredar, tetapi pesan ini tidak memuat bagian yang bohong itu. ` +
        `Halio belum memeriksa isinya lebih jauh. Yang sudah dicek: ${match.debunk.sederhana}`;
    }
    if (status === "tidak_yakin" && match) {
      const topic = isPositive(match.debunk) ? "informasi dari sumber resmi" : "kabar bohong yang pernah beredar";
      return `${sapaan}, Halio belum yakin. Pesan ini mirip dengan ${topic}, tapi buktinya belum cukup. Lebih aman ditahan dulu. Kalau mau, Halio bisa tanyakan ke pemeriksa manusia.`;
    }
    if (status === "tidak_yakin") {
      return `${sapaan}, pesan ini lebih mirip pendapat atau salam, bukan kabar yang bisa dicek benar atau salahnya. Halio tidak menilai pendapat orang.`;
    }
    const trick = manip.techniques.length ? ` Tapi hati-hati: ${manip.techniques[0].explain}` : "";
    return `${sapaan}, belum ada pemeriksa fakta yang memeriksa pesan ini, jadi Halio tidak mau menebak.${trick} Sebaiknya jangan diteruskan dulu. Halio bisa tanyakan ke pemeriksa manusia.`;
  }
  const capitalize = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : s);
  const wibNow = () => new Date(Date.now() + 7 * 3600e3).toISOString().replace(/\.\d+Z$/, "+07:00");
  const T = D.thresholds;

  function check(text, sapaan = "Bapak, Ibu", depth = 0) {
    const claim = extract(text), manip = analyze(text), domains = extractDomains(text);
    let kind = "pesan", info = hasKumpulanJudul(text);
    if (info) kind = "kumpulan_judul";
    const candidates = searchSentences(claim.text);
    const best = candidates[0] || null;
    if (kind === "kumpulan_judul" && ((best && best.score >= T.unsure) || manip.techniques.length)) { kind = "pesan"; info = null; }
    if (kind === "pesan" && depth === 0 && !R.pipelineUrl.test(text)) {
      let units = splitUnits(text);
      if (units.length >= 2 && best && best.score >= T.match && !isPositive(best.debunk) && corePresent(best.debunk, text) && !isCorrection(text)) {
        const alone = units.map((u) => { const m = searchSentences(u).find((x) => x.debunk.id === best.debunk.id); return m ? m.score : 0.0; });
        if (Math.max(...alone) < T.match) units = [];
      }
      if (units.length >= 2) return checkMany(text, units, sapaan, manip, domains);
    }
    const correction = isCorrection(text);
    let status, reason;
    if (best && best.score >= T.unsure && correction && !isPositive(best.debunk)) [status, reason] = ["tidak_yakin", "tampak_meluruskan"];
    else if (!claim.is_factual && (!best || best.score < T.match)) [status, reason] = ["tidak_yakin", "bukan_klaim_faktual"];
    else if (best && best.score >= T.match && isPositive(best.debunk)) [status, reason] = ["tidak_yakin", "memerlukan_verifikasi_ai"];
    else if (best && best.score >= T.match && !corePresent(best.debunk, text)) [status, reason] = ["tidak_yakin", "inti_klaim_tidak_ada"];
    else if (best && best.score >= T.match) [status, reason] = ["terbukti_salah", "cocok_dengan_bantahan"];
    else if (best && best.score >= T.unsure) [status, reason] = ["tidak_yakin", "mirip_tapi_tidak_sama"];
    else [status, reason] = ["belum_ada_pemeriksaan", "tidak_ada_bantahan"];

    if (correction && status === "terbukti_salah" && !(best && isPositive(best.debunk))) [status, reason] = ["tidak_yakin", "tampak_meluruskan"];
    if (kind === "kumpulan_judul" && status !== "terbukti_salah") [status, reason] = ["belum_ada_pemeriksaan", "kumpulan_judul"];

    const shown = !["belum_ada_pemeriksaan", "dilaporkan_media"].includes(status) && reason !== "bukan_klaim_faktual" ? best : null;
    const attrib = shown ? mismatch(text, `${shown.debunk.klaim} ${shown.debunk.fakta} ${shown.debunk.sederhana}`) : null;
    return {
      id: uuid(), created: wibNow(), status, status_label: D.statusLabel[status], reason, claim: claim.text,
      checkworthiness: pyRound(claim.score, 2), match: shown ? matchPayload(shown) : null, llm: null, evidence: null,
      engine_fallback: false, reading: { items: [], disaring: 0 },
      cari_sendiri: status === "belum_ada_pemeriksaan" || status === "tidak_yakin" ? searchLinks(claim.text) : [],
      attribution: attrib, manipulation: manip, links: { domains, warnings: linkWarnings(domains), checked: [] }, kind, info,
      voice_script: voice(status, reason, sapaan, shown, manip),
      offer_human_review: !["terbukti_salah", "sejalan_dengan_sumber"].includes(status) && !D.plainKinds.includes(reason),
      method: "lokal", disclaimer: D.disclaimer, on_device: true, card_url: "", voice_url: "",
    };
  }
  function checkMany(text, units, sapaan, manip, domains) {
    const subs = units.map((u) => check(u, sapaan, 1));
    const sev = (r) => D.severity.indexOf(r.status);
    const lead = subs.reduce((a, b) => (sev(b) < sev(a) ? b : a));
    const parts = subs.map((r, i) => `klaim ${i + 1}: ${D.short[r.status]}`).join("; ");
    const top = Object.assign({}, lead, {
      id: uuid(), reason: "beberapa_klaim", manipulation: manip, links: { domains, warnings: [], checked: [] },
      claims: subs.map((r) => ["claim", "status", "status_label", "reason", "match", "evidence", "kind", "info"].reduce((o, k) => (o[k] = r[k] === undefined ? null : r[k], o), {})),
      voice_script: `${sapaan}, pesan ini berisi ${subs.length} klaim yang berbeda. ${capitalize(parts)}. Halio menjawab satu per satu di bawah.`,
      offer_human_review: subs.some((r) => r.offer_human_review),
      method: [...new Set(subs.flatMap((r) => r.method.split("+")))].join("+"),
    });
    return top;
  }

  api.available = true;
  api.check = check;
  api.corpusSha256 = D.corpusSha256;
  api.corpusSize = debunks.length;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);

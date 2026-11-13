// deteksi trik pesan & saringan PII langsung di browser; daftar polanya diambil dr lexicon_data.js
// (hasil generate otomatis lewat scripts/sync_lexicon.py biar selalu kembar sm backend python)
// semua fungsi di file ini jalan murni lokal di halaman, ga ngirim apa2 keluar
(() => {
  const D = globalThis.HalioLexiconData;
  const TECHNIQUES = D.techniques.map(([id, label, ps]) => [id, label, ps.map((p) => new RegExp(p))]);
  const JUDOL_STRONG = D.judolStrong.map((p) => new RegExp(p));
  const JUDOL_WEAK = D.judolWeak.map((p) => new RegExp(p));
  const SCRUB = D.scrub.map(([p, flags, repl]) => [new RegExp(p, flags), repl]);

  // ratain huruf kecil & buang aksen unicode aneh biar kata yg diakalin tetep kebaca
  function fold(s) {
    return s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function analyze(text) {
    const low = fold(text);
    const techniques = [];
    for (const [id, label, patterns] of TECHNIQUES) {
      if (patterns.some((p) => p.test(low))) techniques.push({ id, label });
    }
    const letters = [...text].filter((c) => c.toLowerCase() !== c.toUpperCase());
    // cek gaya nulis ngegas pake HURUF BESAR SEMUA atau tanda seru berderet
    const caps = letters.length > 30 && letters.filter((c) => c === c.toUpperCase()).length / letters.length > 0.6;
    const shouting = caps || text.includes("!!!");
    const score = Math.min(1, 0.25 * techniques.length + (shouting ? 0.15 : 0));
    return { techniques, shouting, score, needsCheck: score >= 0.5 };
  }

  // cocokin 1 kata kunci judol yg kuat, atau minimal 2 kata umum kl muncul bareng ("slot" + "jackpot")
  function isJudol(text) {
    const low = fold(text || "");
    return JUDOL_STRONG.some((p) => p.test(low)) || JUDOL_WEAK.filter((p) => p.test(low)).length >= 2;
  }

  // aturan sensor data pribadi yg sama persis kaya backend/halio/pii.py sebelum teks boleh dikirim
  function scrub(text) {
    let out = text;
    for (const [re, repl] of SCRUB) out = out.replace(re, repl);
    out = out.replace(/\s+/g, " ").trim();
    return out.length > D.maxClaimChars ? out.slice(0, D.maxClaimChars - 1) + "…" : out;
  }

  globalThis.HalioLexicon = { analyze, isJudol, scrub };
})();

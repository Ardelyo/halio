// On-device text heuristics. The rules come from lexicon_data.js, which is generated from
// backend/halio/manipulation.py and pii.py (scripts/sync_lexicon.py), so both sides match.
// Runs entirely in the page; nothing is sent anywhere by this file.
(() => {
  const D = globalThis.HalioLexiconData;
  const TECHNIQUES = D.techniques.map(([id, label, ps]) => [id, label, ps.map((p) => new RegExp(p))]);
  const JUDOL_STRONG = D.judolStrong.map((p) => new RegExp(p));
  const JUDOL_WEAK = D.judolWeak.map((p) => new RegExp(p));
  const SCRUB = D.scrub.map(([p, flags, repl]) => [new RegExp(p, flags), repl]);

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
    const caps = letters.length > 30 && letters.filter((c) => c === c.toUpperCase()).length / letters.length > 0.6;
    const shouting = caps || text.includes("!!!");
    const score = Math.min(1, 0.25 * techniques.length + (shouting ? 0.15 : 0));
    return { techniques, shouting, score, needsCheck: score >= 0.5 };
  }

  // Strong words alone, or two everyday words together ("slot" + "jackpot"); see manipulation.py.
  function isJudol(text) {
    const low = fold(text || "");
    return JUDOL_STRONG.some((p) => p.test(low)) || JUDOL_WEAK.filter((p) => p.test(low)).length >= 2;
  }

  // Same rules as backend/halio/pii.py: only scrubbed text may leave the device.
  function scrub(text) {
    let out = text;
    for (const [re, repl] of SCRUB) out = out.replace(re, repl);
    out = out.replace(/\s+/g, " ").trim();
    return out.length > D.maxClaimChars ? out.slice(0, D.maxClaimChars - 1) + "…" : out;
  }

  globalThis.HalioLexicon = { analyze, isJudol, scrub };
})();

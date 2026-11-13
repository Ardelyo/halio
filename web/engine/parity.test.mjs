// Uji paritas: mesin JS (halio-local.js) harus ngasih jawaban SAMA dgn pipeline.check python utk semua vektor.
//   node web/engine/parity.test.mjs
// Vektor digenerate scripts/gen_parity_vectors.py. Exit code 1 kalo ada beda sekecil apa pun (skor boleh beda <= 0.001).
import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(import.meta.url);
require(path.join(here, "data.js")); // set globalThis.HalioEngineData
const Local = require(path.join(here, "halio-local.js"));
if (!Local.available) { console.error("mesin JS tidak tersedia"); process.exit(1); }

const { vectors } = JSON.parse(readFileSync(path.join(here, "..", "..", "backend", "tests", "parity_vectors.json"), "utf8"));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let bad = 0;
const shown = {};
const fail = (v, field, js, py) => {
  bad++;
  shown[field] = (shown[field] || 0) + 1;
  if (shown[field] <= 3) console.error(`BEDA [${field}] teks=${JSON.stringify(v.text.slice(0, 90))}\n   py=${JSON.stringify(py)}\n   js=${JSON.stringify(js)}`);
};

for (const v of vectors) {
  const r = Local.check(v.text);
  const got = {
    status: r.status, reason: r.reason, claim: r.claim, checkworthiness: r.checkworthiness,
    debunk_id: r.match ? r.match.debunk_id : null, kind: r.kind, info: r.info, manipulation: r.manipulation, attribution: r.attribution,
    domains: r.links.domains, warnings: r.links.warnings, cari_sendiri: r.cari_sendiri, voice_script: r.voice_script,
    offer_human_review: r.offer_human_review, method: r.method,
  };
  for (const k of Object.keys(got)) if (!same(got[k], v[k])) fail(v, k, got[k], v[k]);
  const jsScore = r.match ? r.match.score : null;
  if ((jsScore === null) !== (v.score === null) || (jsScore !== null && Math.abs(jsScore - v.score) > 0.001)) fail(v, "score", jsScore, v.score);
  if (v.claims) {
    const jc = (r.claims || []).map((c) => ({ claim: c.claim, status: c.status, reason: c.reason, debunk_id: c.match ? c.match.debunk_id : null }));
    if (!same(jc, v.claims)) fail(v, "claims", jc, v.claims);
  } else if (r.claims) fail(v, "claims", r.claims.length, "tidak ada");
}
console.log(`${vectors.length} vektor, ${bad} perbedaan${bad ? " " + JSON.stringify(shown) : ""}`);
process.exit(bad ? 1 : 0);

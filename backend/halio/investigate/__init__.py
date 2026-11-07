"""Halio Telusur: a budgeted investigation agent for analysts.

    plan queries -> fan out (Google via Gemini, sensor archive, ClaimReview, GDELT) -> open pages (code, safe fetch)
    -> passages copied by code -> model judges relations by number -> code decides the status (evidence.decide)
    -> one follow-up round aimed at origins -> timeline / earliest / variants (code) -> report sentences (model, checked by code)

The agent never issues the verdict and never writes a quote. Budgets (queries, pages, seconds) are hard limits.
"""

from __future__ import annotations

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout, as_completed
from dataclasses import dataclass
from datetime import date, datetime
from typing import Callable
from urllib.parse import urlparse

from .. import claims, evidence, outlets
from ..config import Settings
from ..pii import scrub
from ..source_verifier import SourceError, fetch_page
from ..store import WIB
from ..textnorm import tokens
from . import dossier, origin, planner
from .tools import Toolbox

log = logging.getLogger(__name__)

BLIND_SPOTS = [
    "Grup WhatsApp dan Telegram privat: tidak bisa diakses, jadi asal pesan berantai tidak bisa dilacak.",
    "TikTok, Instagram, Facebook, X: tanpa API resmi untuk pencarian; tidak ditelusuri.",
    "Halaman yang hanya tampil dengan JavaScript, berbayar, atau menolak program (HTTP 403): tidak terbaca.",
    "Keaslian foto/video (rekayasa AI, deepfake) tidak dinilai.",
]


@dataclass
class Budget:
    queries: int = 10          # first-round search queries (the claim itself is always one of them)
    followups: int = 4         # second-round, origin-oriented queries
    pages: int = 60            # pages opened in total
    seconds: float = 150.0     # wall clock for the whole investigation
    workers: int = 8
    judge_batch: int = 14
    passages: int = 42         # passages sent to the judge in total


_CHATTY = {"bapak", "ibu", "langsung", "chat", "daftar", "sebarkan", "segera", "tolong", "teruskan", "grup", "dulu", "waspada"}


def passages_for(core: str, text: str, limit: int = 2) -> list[str]:
    """Sentences of the page sharing enough of the core claim's words, copied verbatim. Same idea as
    evidence.extract_passages, with a slightly lower bar because the core is a short restatement, not a chatty forward."""
    want = {t for t in tokens(core) if t not in _CHATTY}
    if len(want) < 3:
        return []
    need = max(3, min(len(want), int(len(want) * 0.4 + 0.999)))
    scored, seen = [], set()
    for sentence in evidence._SENT.split(text):
        sentence = " ".join(sentence.split())
        if not 40 <= len(sentence) <= 500 or sentence in seen:
            continue
        shared = len(want & set(tokens(sentence)))
        if shared >= need:
            seen.add(sentence)
            scored.append((shared, sentence))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:limit]]


_VERDICT = re.compile(r"hoa[xk]s?|tidak benar|keliru|disinformasi|misinformasi|faktanya|klarifikasi|membantah|bantahan|"
                      r"dipastikan|penipuan|rekayasa|manipulasi|palsu|menyesatkan", re.I)


def verdict_sentences(core: str, text: str, title: str = "", limit: int = 2) -> list[str]:
    """Fact-check pages state the verdict in the title and in sentences like 'Faktanya, ...' that repeat few claim words.
    Keep such a sentence (verbatim) when it names at least two of the core claim's words."""
    want = {t for t in tokens(core) if t not in _CHATTY and len(t) >= 4}
    if len(want) < 2:
        return []
    out = []
    for sentence in [title, *evidence._SENT.split(text)]:
        sentence = " ".join((sentence or "").split())
        if 25 <= len(sentence) <= 400 and _VERDICT.search(sentence) and len(want & set(tokens(sentence))) >= 2 and sentence not in out:
            out.append(sentence)
        if len(out) >= limit:
            break
    return out


def _tier(url: str) -> str:
    return evidence.classify(url)[0]


class _Run:
    def __init__(self, claim, cfg, budget, toolbox, fetch, judge, progress, clock):
        self.claim, self.cfg, self.b, self.tools, self.fetch, self.judge = claim, cfg, budget, toolbox, fetch, judge
        self.say, self.clock = progress or (lambda **_: None), clock
        self.t0 = clock()
        self.cands: dict[str, dict] = {}
        self.opened: set[str] = set()
        self.pages: list[dict] = []          # every page opened and readable
        self.failed: dict[str, int] = {}
        self.passages: list[evidence.Passage] = []
        self.items: list[evidence.Item] = []
        self.side: list[dict] = []           # sensor / gdelt / claimreview hits, for the timeline
        self.reviews: list[dict] = []
        self.queries: list[str] = []
        self.core = claim

    def left(self) -> float:
        return self.b.seconds - (self.clock() - self.t0)

    def stats(self) -> dict:
        return {"kueri": len(self.queries), "kandidat": len(self.cands), "dibuka": len(self.pages),
                "gagal": sum(self.failed.values()), "kutipan": len(self.passages), "dinilai": len(self.items),
                "detik": round(self.clock() - self.t0, 1)}

    # -- candidates --------------------------------------------------------------------------------------------
    def add(self, hits: list[dict]) -> None:
        for h in hits:
            uri = h.get("uri", "")
            if not uri.startswith("https://") or outlets.is_not_a_source(uri) and "vertexaisearch" not in uri:
                continue
            key = evidence._canonical(uri)
            c = self.cands.setdefault(key, {"uri": uri, "title": h.get("title", ""), "via": set(), "hits": 0})
            c["via"].add(h.get("via", "?"))
            c["hits"] += 1
            c["title"] = c["title"] or h.get("title", "")

    def gather(self, queries: list[str], first: bool) -> None:
        self.queries += queries
        self.say(stage="mencari", **self.stats())
        with ThreadPoolExecutor(max_workers=6) as pool:
            jobs = [pool.submit(self.tools.search, q) for q in queries]
            if first:
                jobs += [pool.submit(self.tools.sensor, self.claim), pool.submit(self.tools.claimreview, self.claim),
                         pool.submit(self.tools.gdelt, self.claim)]
            try:
                for f in as_completed(jobs, timeout=max(5.0, self.left() - 30)):
                    hits = f.result() or []
                    self.add(hits)
                    self.side += [h for h in hits if h.get("via") in ("sensor", "gdelt", "claimreview")]
                    self.reviews += [h for h in hits if h.get("via") == "claimreview"]
                    self.say(stage="mencari", **self.stats())
            except FutureTimeout:
                log.info("search round cut by the time budget")

    # -- reading -----------------------------------------------------------------------------------------------
    def rank(self) -> list[dict]:
        def key(c):
            via = c["via"]
            return (0 if "claimreview" in via else 1, "ABCD?".index(_tier(c["uri"]) if "vertexaisearch" not in c["uri"] else "?"), -c["hits"])
        return sorted((c for k, c in self.cands.items() if k not in self.opened), key=key)

    def read(self) -> None:
        todo = self.rank()[: max(0, self.b.pages - len(self.opened))]
        if not todo or self.left() < 15:
            return
        self.say(stage="membuka", **self.stats())

        def one(c):
            try:
                return c, self.fetch(c["uri"]), None
            except SourceError as exc:
                return c, None, str(exc)
            except Exception:
                return c, None, "sumber_tidak_dapat_diakses"

        pool = ThreadPoolExecutor(max_workers=self.b.workers)
        try:
            futures = [pool.submit(one, c) for c in todo]
            for c in todo:
                self.opened.add(evidence._canonical(c["uri"]))
            for f in as_completed(futures, timeout=max(5.0, self.left() - 25)):
                c, page, err = f.result()
                if page is None:
                    self.failed[err] = self.failed.get(err, 0) + 1
                elif not outlets.is_not_a_source(page.final_url):
                    self.keep(c, page)
                self.say(stage="membuka", **self.stats())
        except FutureTimeout:
            self.failed["waktu_habis"] = self.failed.get("waktu_habis", 0) + sum(1 for f in futures if not f.done())
        finally:
            pool.shutdown(wait=False, cancel_futures=True)

    def keep(self, c: dict, page) -> None:
        tier, publisher, group = evidence.classify(page.final_url)
        wire = evidence.wire_group(page.text)
        if wire and tier == "C":
            group = wire
        found = passages_for(self.core, page.text)
        if tier in ("A", "B", "C"):
            found += [s for s in verdict_sentences(self.core, page.text, page.title) if s not in found]
        found = found[:3]
        host = urlparse(page.final_url).hostname or ""
        self.pages.append({"url": page.final_url, "host": host, "judul": page.title or c.get("title") or host, "penerbit": publisher,
                           "tingkat": tier, "tingkat_label": origin.KIND_LABEL[tier], "tanggal": (page.published or "")[:10],
                           "relevan": bool(found), "via": sorted(c["via"]), "grup": group})
        for text in found:
            self.passages.append(evidence.Passage(id=0, text=text, url=page.final_url, host=host, tier=tier, publisher=publisher,
                                                  group=group, published=evidence.parse_date(page.published), title=page.title))

    # -- judging -----------------------------------------------------------------------------------------------
    def judge_new(self) -> None:
        judged = {id(i.passage) for i in self.items}
        pending = [p for p in self.passages if p.tier != "D" and id(p) not in judged]
        pending.sort(key=lambda p: "ABCD".index(p.tier))
        room = self.b.passages - len(self.items)
        pending = pending[: max(0, room)]
        if not pending or self.left() < 10:
            return
        self.say(stage="menilai", **self.stats())
        start = max([i.passage.id for i in self.items], default=0)
        for n, p in enumerate(pending, start + 1):
            p.id = n
        batches = [pending[i:i + self.b.judge_batch] for i in range(0, len(pending), self.b.judge_batch)]
        with ThreadPoolExecutor(max_workers=3) as pool:
            for batch, out in zip(batches, pool.map(lambda bt: self._judge(bt), batches)):
                self.items += evidence.validate(out, batch)
        self.say(stage="menilai", **self.stats())

    def _judge(self, batch):
        try:
            return self.judge(self.claim, batch, self.cfg)
        except Exception as exc:
            log.warning("judge unavailable for a batch: %s", type(exc).__name__)
            return []


def run(text: str, cfg: Settings, *, progress: Callable | None = None, budget: Budget | None = None, toolbox=None,
        fetch=fetch_page, judge=evidence.gemini_judge, plan_ask=planner._ask, dossier_ask=dossier._ask,
        today: date | None = None, clock=time.monotonic) -> dict:
    from ..pipeline import STATUS_LABEL

    budget = budget or Budget()
    today = today or datetime.now(WIB).date()
    claim = claims.extract(text).text
    r = _Run(claim, cfg, budget, toolbox or Toolbox(cfg), fetch, judge, progress, clock)

    r.say(stage="merencanakan", **r.stats())
    queries, core = planner.plan(claim, cfg, limit=budget.queries, ask=plan_ask)
    r.core = core or claim
    r.gather(queries, first=True)
    r.read()
    r.judge_new()

    if r.left() > 45:
        r.say(stage="menelusuri_asal", **r.stats())
        found = sorted((p for p in r.pages if p["relevan"]), key=lambda p: p["tanggal"] or "9999")
        more = planner.follow_up(claim, found, r.queries, cfg, limit=budget.followups, ask=plan_ask)
        if more:
            r.gather(more, first=False)
            r.read()
            r.judge_new()

    d = evidence.decide(r.items, today)
    r.say(stage="menyusun", **r.stats())

    # evidence list, numbered for the report: judged passages (strongest first), then ClaimReview entries
    order = {"refutes": 0, "supports": 1, "context": 2, "unrelated": 3}
    shown = sorted((i for i in r.items if i.relation != "unrelated"), key=lambda i: ("ABCD".index(i.passage.tier), order[i.relation]))
    numbered = []
    for i in shown[:20]:
        p = i.passage
        numbered.append({"penerbit": p.publisher, "tingkat": p.tier, "tingkat_label": origin.KIND_LABEL[p.tier],
                         "tanggal": p.published.isoformat() if p.published else "", "kutipan": p.text, "url": p.url,
                         "host": p.host, "hubungan": i.relation, "grup": p.group})
    for rv in r.reviews[:5]:
        numbered.append({"penerbit": rv["penerbit"] or urlparse(rv["uri"]).hostname, "tingkat": "B", "tingkat_label": "Pemeriksa fakta",
                         "tanggal": rv.get("tanggal", ""), "kutipan": f"Penilaian: {rv['penilaian']}. Klaim yang diperiksa: {rv['klaim']}",
                         "url": rv["uri"], "host": urlparse(rv["uri"]).hostname or "", "hubungan": "claimreview", "grup": rv["penerbit"]})
    for n, b in enumerate(numbered, 1):
        b["no"] = n

    # timeline: pages with a date, side hits with a date, and the first archive capture of the earliest relevant pages
    events = [{"tanggal": p["tanggal"], "judul": p["judul"], "url": p["url"], "penerbit": p["penerbit"], "tingkat": p["tingkat"],
               "asal": "halaman", "catatan": "membahas klaim" if p["relevan"] else ""} for p in r.pages if p["relevan"]]
    events += [{"tanggal": h.get("seen") or h.get("tanggal", ""), "judul": h.get("title", ""), "url": h["uri"],
                "penerbit": h.get("penerbit") or h.get("domain") or urlparse(h["uri"]).hostname, "tingkat": _tier(h["uri"]),
                "asal": h["via"], "catatan": h.get("penilaian", "")} for h in r.side]
    dated = sorted((p for p in r.pages if p["relevan"]), key=lambda p: p["tanggal"] or "9999")[:3]
    if r.left() > 8:
        with ThreadPoolExecutor(max_workers=3) as pool:
            for p, first in zip(dated, pool.map(r.tools.wayback_first, [p["url"] for p in dated])):
                if first:
                    events.append({"tanggal": first, "judul": p["judul"], "url": p["url"], "penerbit": p["penerbit"],
                                   "tingkat": p["tingkat"], "asal": "wayback", "catatan": "pertama kali diarsipkan Internet Archive"})
    line = origin.timeline(events)
    quotes = [{"kutipan": p.text, "host": p.host, "tanggal": p.published.isoformat() if p.published else ""} for p in r.passages]

    status_label = STATUS_LABEL.get(d.status, d.status)
    text_out, written = dossier.write(claim, status_label, numbered, cfg, ask=dossier_ask)

    spots = list(BLIND_SPOTS)
    if not cfg.google_factcheck_key:
        spots.append("Basis data ClaimReview (Google Fact Check Tools) tidak dipakai: kunci API belum diisi.")
    if not any(h["via"] == "gdelt" for h in r.side):
        spots.append("GDELT tidak memberi hasil atau tidak tersedia; cakupan berita internasional terbatas.")
    if r.failed.get("http_403"):
        spots.append(f"{r.failed['http_403']} situs menolak dibuka otomatis (HTTP 403).")

    reading = sorted((p for p in r.pages if p["relevan"]), key=lambda p: ("ABCD".index(p["tingkat"]), p["tanggal"] or "9999"))
    return {
        "klaim": claim,
        "inti": r.core if r.core != claim else "",
        "klaim_lain": [c for c in (scrub(u) for u in claims.split_units(text)) if c.strip() and c.strip() != claim][:3],
        "status": d.status, "status_label": status_label, "reason": d.reason, "kekuatan": d.kekuatan, "alasan": d.alasan,
        "laporan": text_out,
        "bukti": numbered,
        "linimasa": line,
        "asal": origin.earliest(line),
        "varian": origin.variants(quotes),
        "cakupan": origin.coverage([{"tingkat": p["tingkat"], "grup": p["grup"]} for p in r.pages if p["relevan"]]),
        "bacaan": reading[:12],
        "titik_buta": spots,
        "metode": {**r.stats(), "daftar_kueri": r.queries, "gagal_rinci": r.failed, "kalimat": written,
                   "anggaran": {"kueri": budget.queries + budget.followups, "halaman": budget.pages, "detik": budget.seconds},
                   "sumber_kandidat": sorted({v for c in r.cands.values() for v in c["via"]})},
        "dibuat": datetime.now(WIB).isoformat(timespec="seconds"),
        "catatan": "Vonis berasal dari aturan kode atas kutipan yang disalin kode. AI hanya mencari, menilai hubungan kutipan bernomor, "
                   "dan menulis kalimat yang kemudian diperiksa ulang oleh kode.",
    }

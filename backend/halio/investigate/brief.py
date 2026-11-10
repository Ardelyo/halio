"""Daily brief for analysts: which narratives are rising in public news and fact-check feeds, each investigated by the swarm.

    sensor archive (last 48 h) -> topic filter (TNI AD / defence, or fact-check feeds for "umum")
    -> cluster near-identical headlines (code) -> score (distinct sources, fact-check involvement, hoax words, recency)
    -> top narratives get a Halio Telusur investigation -> brief stored, shown in Radar.

Narratives and claims only. No person, account or soldier is profiled; only public feeds are read (docs/PLAN_UNGGUL.md 5).
"""

from __future__ import annotations

import json
import logging
import re
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from ..config import Settings
from ..store import WIB
from ..textnorm import tokens

log = logging.getLogger(__name__)

TOPICS = {
    "tni": ("TNI AD dan pertahanan", re.compile(
        r"\b(tni|tentara nasional|kodam|korem|kodim|koramil|babinsa|kostrad|kopassus|kasad|ksad|dispenad|akmil|bintara|"
        r"tamtama|yonif|pangdam|danrem|dandim|angkatan darat|kemhan|menhan|wamenhan|kementerian pertahanan)\b", re.I)),
    "umum": ("Hoaks dan klaim yang sedang diperiksa", None),
}
# A foreign defence minister or army is not this topic, unless the headline also names an Indonesian service or place.
_FOREIGN = re.compile(r"\b(as|amerika|trump|hegseth|pentagon|rusia|israel|china|tiongkok|inggris|ukraina|iran|korea|jepang|nato)\b", re.I)
_INDONESIAN = re.compile(r"\b(tni|kodam|korem|kodim|koramil|babinsa|kasad|ksad|dispenad|indonesia|ri)\b", re.I)
# Official feeds that belong to a topic whatever their headline says ("Prajurit Yonif ... bantu warga").
TOPIC_SOURCES = {"tni": {"tniad", "kemhan"}}
# Fact-checkers label headlines "[SALAH]", "[HOAKS]", "[PENIPUAN]", "[MISLEADING]"...: the strongest signal of all.
_HOAX = re.compile(r"\bhoa[xk]s?\b|cek fakta|tidak benar|keliru|disinformasi|penipuan|\bpalsu\b|catut|mencatut|menyesatkan|"
                   r"\[\s*(salah|hoaks?|penipuan|misleading|menyesatkan|disinformasi|fitnah|satire|konten palsu)\s*\]", re.I)
_PREFIX = re.compile(r"^\s*(\[[^\]]{2,20}\]|hoaks?!?:?|cek fakta:?|klarifikasi:?)\s*", re.I)

SCHEMA = """
CREATE TABLE IF NOT EXISTS briefs (id TEXT PRIMARY KEY, created TEXT NOT NULL, day TEXT NOT NULL, topic TEXT NOT NULL, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_briefs_topic ON briefs (topic, created);
"""


def _jac(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def clusters(rows: list[dict], kinds: dict[str, str], names: dict[str, str], topic: str, now: datetime | None = None,
             threshold: float = 0.34) -> list[dict]:
    now = now or datetime.now(timezone.utc)
    rx = TOPICS[topic][1]
    own = TOPIC_SOURCES.get(topic, set())
    def on_topic(title: str) -> bool:
        return bool(rx.search(title)) and not (topic == "tni" and _FOREIGN.search(title) and not _INDONESIAN.search(title))

    picked = [r for r in rows if r["source_id"] in own or (on_topic(r["title"]) if rx else kinds.get(r["source_id"]) == "cek_fakta")]
    groups: list[dict] = []
    for r in picked:
        toks = set(tokens(_PREFIX.sub("", r["title"])))
        if len(toks) < 3:
            continue
        home = max(groups, key=lambda g: _jac(toks, g["_tok"]), default=None)
        if home is None or _jac(toks, home["_tok"]) < threshold:
            home = {"_tok": set(toks), "items": []}
            groups.append(home)
        home["items"].append(r)
    out = []
    for g in groups:
        items = sorted(g["items"], key=lambda r: r["first_seen"])
        sources = sorted({r["source_id"] for r in items})
        kinds_in = sorted({kinds.get(s, "berita") for s in sources})
        hoaxy = any(_HOAX.search(r["title"]) for r in items)
        recent = sum(1 for r in items if r["first_seen"] >= (now - timedelta(hours=12)).isoformat(timespec="seconds"))
        score = 2 * len(sources) + len(items) + (3 if "cek_fakta" in kinds_in else 0) + (2 if hoaxy else 0) + recent
        # Worth a swarm investigation only with a disinformation signal: hoax words, a fact-checker, or several outlets.
        # A single official release ("Majalah Palagan edisi ...") is context, not a narrative to investigate.
        worth = hoaxy or "cek_fakta" in kinds_in or len(sources) >= 2
        rep = min(items, key=lambda r: len(r["title"]))
        out.append({
            "judul": _PREFIX.sub("", rep["title"]).strip(), "skor": score, "jumlah_berita": len(items), "jumlah_sumber": len(sources),
            "sumber": [names.get(s, s) for s in sources], "jenis_sumber": kinds_in, "berbau_hoaks": hoaxy, "perlu_ditelusuri": worth,
            "pertama": items[0]["first_seen"], "terakhir": items[-1]["first_seen"],
            "berita": [{"judul": r["title"], "url": r["url"], "sumber": names.get(r["source_id"], r["source_id"]), "waktu": r["first_seen"]}
                       for r in items[-6:]],
        })
    return sorted(out, key=lambda c: (not c["perlu_ditelusuri"], -c["skor"]))


class Briefs:
    def __init__(self, cfg: Settings):
        self.cfg, self.path = cfg, str(cfg.db_path)
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self):
        conn = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def build(self, topic: str, jobs=None, top: int = 3, hours: int = 48, now: datetime | None = None) -> dict:
        from ..ingest.sources import SOURCES
        from ..ingest.store import SensorStore

        now = now or datetime.now(timezone.utc)
        rows = SensorStore(self.cfg.db_path).items_since((now - timedelta(hours=hours)).isoformat(timespec="seconds"))
        kinds = {s.id: s.kind for s in SOURCES}
        names = {s.id: s.name for s in SOURCES}
        found = clusters(rows, kinds, names, topic, now)
        narratives = [c for c in found if c["perlu_ditelusuri"]][:8]
        # Official releases on the topic, shown beside the narratives as the army's own public account (not investigated).
        context = [{"judul": c["judul"], "sumber": c["sumber"], "pertama": c["pertama"], "url": c["berita"][-1]["url"]}
                   for c in found if not c["perlu_ditelusuri"] and "resmi" in c["jenis_sumber"]][:6]
        for n in narratives[:top]:
            n["investigasi"] = None
            if jobs is not None:
                try:
                    n["investigasi"] = jobs.submit(n["judul"], "brief", "demo")
                except Exception as exc:  # daily cap reached, model off: the brief still lists the narratives
                    n["catatan"] = f"Belum ditelusuri: {exc}"
        brief = {
            "id": uuid.uuid4().hex, "dibuat": datetime.now(WIB).isoformat(timespec="seconds"), "topik": topic,
            "label": TOPICS[topic][0], "jendela_jam": hours, "berita_dibaca": len(rows),
            "berita_cocok_topik": sum(c["jumlah_berita"] for c in found), "narasi": narratives,
            "konteks_resmi": context,
            "catatan": "Disusun dari feed berita, pemeriksa fakta, dan situs resmi yang publik. Narasi dan klaim, bukan orang: "
                       "tidak ada akun, warga, atau prajurit yang diprofilkan. Skor = jumlah sumber berbeda, keterlibatan pemeriksa fakta, "
                       "kata hoaks, dan kebaruan; skor bukan vonis.",
        }
        with self._conn() as c:
            c.execute("INSERT INTO briefs (id, created, day, topic, data) VALUES (?,?,?,?,?)",
                      (brief["id"], brief["dibuat"], brief["dibuat"][:10], topic, json.dumps(brief, ensure_ascii=False)))
        return brief

    def latest(self, topic: str, jobs=None) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT data FROM briefs WHERE topic=? ORDER BY created DESC LIMIT 1", (topic,)).fetchone()
        if not row:
            return None
        brief = json.loads(row["data"])
        for n in brief["narasi"]:
            job_id = n.get("investigasi")
            if job_id and jobs is not None:
                job = jobs.get(job_id) or {}
                rep = job.get("laporan") or {}
                n["hasil"] = {"status": job.get("status"), "tahap": job.get("tahap"), "status_label": rep.get("status_label"),
                              "kode_status": rep.get("status"), "ringkasan": [s["teks"] for s in (rep.get("laporan") or {}).get("ringkasan", [])[:2]],
                              "asal": (rep.get("asal") or {}).get("pertama"), "bukti": len(rep.get("bukti", [])),
                              "dibuka": (rep.get("metode") or {}).get("dibuka")}
        return brief

    def has_today(self, topic: str) -> bool:
        day = datetime.now(WIB).date().isoformat()
        with self._conn() as c:
            return c.execute("SELECT 1 FROM briefs WHERE topic=? AND day=?", (topic, day)).fetchone() is not None

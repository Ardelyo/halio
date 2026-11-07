"""The swarm: specialised agents that search at the same time and feed one shared, deduplicated evidence pool.

Each agent is a search strategy with its own queries, not a free-running model: the verdict stays with code.
"""

from __future__ import annotations

from ..textnorm import tokens

AGENTS = {
    "umum": ("Perencana", "Kueri umum dari perencana AI: variasi kata kunci, nama, terjemahan."),
    "cek_fakta": ("Penelusur pemeriksa fakta", "TurnBackHoax/Mafindo, Kompas, Liputan6, Tempo Cek Fakta, AFP, ClaimReview."),
    "resmi": ("Penelusur sumber resmi", "Situs .go.id dan .mil.id: klarifikasi, rilis, pengumuman."),
    "media": ("Penelusur media", "Pemberitaan media nasional dan salinan kantor berita."),
    "arsip": ("Penelusur arsip", "Arsip pemeriksa fakta yang sudah pernah membahas klaim serupa, arsip sensor realtime, dan GDELT."),
    "asal": ("Penelusur asal-usul", "Putaran kedua: kemunculan paling awal, versi lama, nama asli foto/video."),
    "gambar": ("Penelusur gambar", "Pencarian gambar terbalik (Cloud Vision): halaman yang memuat gambar sama."),
}


def keywords(core: str, n: int = 6) -> str:
    seen: list[str] = []
    for t in tokens(core):
        if len(t) >= 4 and t not in seen:
            seen.append(t)
    return " ".join(seen[:n])


def tasks(core: str) -> list[tuple[str, str]]:
    k = keywords(core)
    if len(k.split()) < 2:
        return []
    return [
        ("cek_fakta", f"{k} site:turnbackhoax.id"),
        ("cek_fakta", f"{k} cek fakta site:kompas.com OR site:liputan6.com OR site:tempo.co"),
        ("resmi", f"{k} site:go.id"),
        ("resmi", f"{k} site:mil.id"),
        ("media", f"{k} berita terbaru"),
    ]


def summary(queries: dict[str, int], hits: dict[str, int], pages: list[dict]) -> list[dict]:
    out = []
    for key, (label, what) in AGENTS.items():
        relevant = sum(1 for p in pages if p["relevan"] and key in p.get("agen", []))
        if queries.get(key) or hits.get(key) or relevant:
            out.append({"id": key, "nama": label, "tugas": what, "kueri": queries.get(key, 0), "temuan": hits.get(key, 0),
                        "halaman_relevan": relevant})
    return out

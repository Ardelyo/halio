"""The swarm: specialised agents that search at the same time and feed one shared, deduplicated evidence pool.

Each agent is a search strategy with its own queries, not a free-running model: the verdict stays with code.
"""

from __future__ import annotations

import re

from ..textnorm import tokens

# daftar peran agen pencari yg jalan barengan ngisi satu kolam kandidat bukti
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
    # saring kata kunci yg cukup spesifik (>=4 huruf) tanpa dobel
    seen: list[str] = []
    for t in tokens(core):
        if len(t) >= 4 and t not in seen:
            seen.append(t)
    return " ".join(seen[:n])


TNI_TOPIC = re.compile(r"\b(tni|tentara|kodam|korem|kodim|koramil|kostrad|kopassus|kasad|dispenad|akmil|bintara|tamtama|taruna|prajurit|"
                       r"rekrutmen tni|penerimaan tni|angkatan darat|kemhan|menhan|panglima)\b", re.I)


def tasks(core: str) -> list[tuple[str, str]]:
    # bagi tugas pencarian terarah ke situs pemeriksa fakta, domain resmi .go.id/.mil.id, sm media berita
    k = keywords(core)
    if len(k.split()) < 2:
        return []
    out = [
        ("cek_fakta", f"{k} site:turnbackhoax.id"),
        ("cek_fakta", f"{k} cek fakta site:kompas.com OR site:liputan6.com OR site:tempo.co"),
        ("resmi", f"{k} site:go.id"),
        ("resmi", f"{k} site:mil.id"),
        ("media", f"{k} berita terbaru"),
    ]
    if TNI_TOPIC.search(core):
        # kl nyangkut isu TNI, wajib cek langsung ke kanal resmi TNI & Kemhan krn mereka rujukan utma soal aturan
        # rekrutmen, pengumuman resmi, sm peringatan modus penipuan catut nama
        out += [
            ("resmi", f"{k} site:tniad.mil.id"),
            ("resmi", f"{k} site:rekrutmen-tni.mil.id OR site:penerimaan.tniad.mil.id"),
            ("resmi", f"{k} site:kemhan.go.id OR site:tni.mil.id"),
        ]
    return out


def summary(queries: dict[str, int], hits: dict[str, int], pages: list[dict]) -> list[dict]:
    # rekap hasil kerja tiap agen buat ditampilin transparan di metode laporan
    out = []
    for key, (label, what) in AGENTS.items():
        relevant = sum(1 for p in pages if p["relevan"] and key in p.get("agen", []))
        if queries.get(key) or hits.get(key) or relevant:
            out.append({"id": key, "nama": label, "tugas": what, "kueri": queries.get(key, 0), "temuan": hits.get(key, 0),
                        "halaman_relevan": relevant})
    return out

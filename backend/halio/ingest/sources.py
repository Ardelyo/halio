"""Registry of feeds the sensor polls, and the blind spots it declares.

Every URL below answered with a parsable feed when polled on 2026-10-28 with our own
honest User-Agent (see docs/ARCHITECTURE_SENSOR.md §3 for the probe table, including the
candidates that failed or refused us; we do not disguise the sensor as a browser). Feeds change without notice: the coverage panel, not this list, is the
source of truth for whether a source is alive today.
"""

from __future__ import annotations

from dataclasses import dataclass

MIN, HOUR, DAY = 60, 3600, 86400

BERITA, CEK_FAKTA, RESMI = "berita", "cek_fakta", "resmi"
KIND_LABEL = {BERITA: "Berita", CEK_FAKTA: "Cek fakta", RESMI: "Sumber resmi"}


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    url: str
    kind: str
    cadence_s: int = 2 * MIN       # how often we poll
    max_quiet_s: int = 6 * HOUR    # newest item older than this => "basi" (stale)
    notes: str = ""


SOURCES: tuple[Source, ...] = (
    # --- berita nasional (volume tinggi) ---
    Source("antara-terkini", "ANTARA Terkini", "https://www.antaranews.com/rss/terkini.xml", BERITA),
    Source("cnn-nasional", "CNN Indonesia Nasional", "https://www.cnnindonesia.com/nasional/rss", BERITA),
    Source("cnn-internasional", "CNN Indonesia Internasional", "https://www.cnnindonesia.com/internasional/rss", BERITA),
    Source("cnn-teknologi", "CNN Indonesia Teknologi", "https://www.cnnindonesia.com/teknologi/rss", BERITA, max_quiet_s=12 * HOUR),
    Source("cnn-ekonomi", "CNN Indonesia Ekonomi", "https://www.cnnindonesia.com/ekonomi/rss", BERITA),
    Source("cnbc-id", "CNBC Indonesia", "https://www.cnbcindonesia.com/news/rss", BERITA),
    Source("detik-news", "detikNews", "https://news.detik.com/rss", BERITA),
    Source("liputan6-news", "Liputan6 News", "https://feed.liputan6.com/rss/news", BERITA),
    Source("liputan6-tekno", "Liputan6 Tekno", "https://feed.liputan6.com/rss/tekno", BERITA, max_quiet_s=12 * HOUR),
    Source("republika", "Republika", "https://www.republika.co.id/rss", BERITA),
    Source("okezone", "Okezone", "https://sindikasi.okezone.com/index.php/rss/0/RSS2.0", BERITA),
    Source("viva", "VIVA", "https://www.viva.co.id/get/all", BERITA),
    Source("kumparan", "kumparan", "https://lapi.kumparan.com/v2.0/rss/", BERITA),
    Source("mediaindonesia", "Media Indonesia", "https://mediaindonesia.com/feed", BERITA),
    Source("sindonews", "SINDOnews", "https://www.sindonews.com/feed", BERITA),
    Source("tempo-terkini", "Tempo Terkini", "https://rss.tempo.co/", BERITA),
    Source("alinea", "Alinea.id", "https://www.alinea.id/rss", BERITA, max_quiet_s=12 * HOUR,
           notes="Feed tanpa tanggal terbit: waktu dihitung dari saat pertama terlihat."),
    # --- cek fakta ---
    Source("turnbackhoax", "TurnBackHoax (Mafindo)", "https://turnbackhoax.id/feed", CEK_FAKTA, cadence_s=5 * MIN,
           max_quiet_s=3 * DAY, notes="Judul berlabel [SALAH]/[PENIPUAN]; feed tanpa tanggal terbit."),
    Source("cekfakta", "CekFakta.com", "https://www.cekfakta.com/feed", CEK_FAKTA, cadence_s=5 * MIN,
           max_quiet_s=3 * DAY, notes="Memuat ulang artikel yang sama dengan TurnBackHoax; jangan dihitung ganda."),
    Source("liputan6-cekfakta", "Liputan6 Cek Fakta", "https://feed.liputan6.com/rss/cek-fakta", CEK_FAKTA,
           cadence_s=5 * MIN, max_quiet_s=2 * DAY),
    Source("mafindo", "Mafindo", "https://www.mafindo.or.id/feed", CEK_FAKTA, cadence_s=30 * MIN, max_quiet_s=7 * DAY,
           notes="Pada uji 28 Okt 2026 entri terbarunya berumur sekitar 195 hari: sengaja dipertahankan "
                 "agar panel menunjukkan deteksi feed basi."),
    # --- sumber resmi ---
    Source("kemhan", "Kemhan", "https://www.kemhan.go.id/feed", RESMI, cadence_s=10 * MIN, max_quiet_s=3 * DAY),
    Source("tniad", "TNI AD", "https://tniad.mil.id/feed/", RESMI, cadence_s=10 * MIN, max_quiet_s=3 * DAY),
)

SOURCE_BY_ID = {s.id: s for s in SOURCES}


@dataclass(frozen=True)
class BlindSpot:
    id: str
    name: str
    tier: str     # "B" = butuh anggaran/izin, "C" = tidak mungkin
    reason: str


BLIND_SPOTS: tuple[BlindSpot, ...] = (
    BlindSpot("wa-privat", "WhatsApp dan obrolan privat", "C",
              "Terenkripsi dan privat. Halio hanya melihat pesan yang pengguna teruskan sendiri."),
    BlindSpot("meta", "Facebook dan Instagram", "B",
              "Meta Content Library hanya untuk lembaga riset nirlaba yang disetujui."),
    BlindSpot("tiktok", "TikTok", "B",
              "TikTok Research API tidak tersedia untuk Indonesia (daftar negara yang kami temukan)."),
    BlindSpot("x", "X (Twitter)", "B",
              "Berbayar per pembacaan; belum dipasang. Kandidat sampling kata kunci jika ada anggaran."),
    BlindSpot("youtube", "YouTube", "B",
              "Kuota bawaan 10.000 unit per hari (satu pencarian 100 unit); belum dipasang."),
    BlindSpot("telegram", "Kanal Telegram publik", "B",
              "Ketentuan layanan perlu ditinjau sebelum dipantau; belum dipasang."),
    BlindSpot("media-lokal", "Media lokal dan daerah", "B",
              "Belum ada daftar feed terverifikasi; cakupan nasional besar saja."),
)

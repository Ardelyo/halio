"""Narration -> timeline. One source of truth for scene timing, subtitles and the reading script.

    python video/tools/build_timeline.py

Writes:
  video/src/timeline.js      scene/cue timings used by the animation (window.TIMELINE)
  video/out/halio-demo.srt   subtitles for YouTube upload
  video/out/halio-demo.ass   styled subtitles burned into the MP4
  video/NASKAH.md            the narration with timecodes, for recording the voice-over

Cue length follows a calm reading pace (about 14 characters per second) so the person
recording can read along with the burned subtitles without rushing.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CPS = 14.0          # characters per second while reading aloud
MIN_CUE = 1.9
GAP = 0.25          # breath between cues
LEAD = 1.0          # visuals settle before the first line of each scene
TAIL = 0.8
EXTRA_TAIL = {"pembuka": 0.6, "halio": 1.0, "tiga": 0.6, "mesin": 0.8, "penutup": 4.0}  # let key visuals breathe

# (scene id, tag shown top-left, [narration cues])
SCENES: list[tuple[str, str, list[str]]] = [
    ("pembuka", "Prolog", [
        "Setiap pagi, jutaan pesan diteruskan ke grup keluarga.",
        "Hampir semuanya dikirim karena sayang.",
    ]),
    ("cerita", "01 · Masalah", [
        "Bayangkan Ibu Sri, enam puluh delapan tahun.",
        "Pagi ini ia menerima video Presiden yang membagikan bantuan tunai,",
        "lengkap dengan nomor WhatsApp untuk mendaftar.",
    ]),
    ("fakta", "01 · Masalah", [
        "Itu bukan karangan. Awal 2025, penipuan deepfake serupa",
        "menjerat seratus korban di dua puluh provinsi.",
    ]),
    ("dampak", "01 · Masalah", [
        "Hoaks tidak hanya menipu.",
        "Di Kendal, pada 2018, pesan berantai soal penculik anak",
        "berakhir dengan seorang pria tak bersalah dikeroyok massa.",
    ]),
    ("literasi", "01 · Masalah", [
        "Empat dari sepuluh orang Indonesia ragu mampu mengenali hoaks.",
        "Ibu Sri tidak bodoh. Ia sendirian.",
    ]),
    ("medan", "02 · Siber Sosial", [
        "Ruang pikiran kini menjadi medan.",
        "Pertahanannya dimulai dari unit sosial terkecil: keluarga.",
    ]),
    ("halio", "03 · Solusi", [
        "Inilah Halio.",
        "Teman cek pesan untuk keluarga, sekaligus sensor dini untuk satuan siber.",
    ]),
    ("cek", "04 · Cara pakai", [
        "Ibu Sri cukup menempelkan pesan itu ke Halio.",
        "Dalam hitungan detik, ia mendapat jawaban berbahasa sederhana,",
        "nama sumber pemeriksa fakta, dan trik manipulasi yang dipakai pesan itu.",
    ]),
    ("suara", "04 · Cara pakai", [
        "Halio juga membacakan jawabannya sebagai pesan suara,",
        "dan membuat Kartu Halio untuk meluruskan kabar di grup keluarga.",
    ]),
    ("jujur", "05 · Kejujuran", [
        "Bagaimana jika belum ada yang memeriksa?",
        "Halio tidak menebak. Ia bilang terus terang, menyarankan pesan ditahan dulu,",
        "dan menawarkan bantuan pemeriksa manusia.",
    ]),
    ("tiga", "05 · Kejujuran", [
        "Karena itu, setiap jawaban hanya punya tiga keadaan:",
        "terbukti salah, tidak yakin, atau belum ada pemeriksaan.",
    ]),
    ("mesin", "06 · Cara kerja", [
        "Di balik layar, Halio memilih kalimat yang layak dicek,",
        "lalu menghapus nomor telepon, NIK, dan tautan.",
        "Klaim dicocokkan dengan bantahan yang bersumber,",
        "dan dijaga agar topik yang sekadar mirip tidak langsung dicap hoaks.",
        "Model bahasa bersifat opsional, dan hanya boleh mengonfirmasi dengan kutipan persis.",
    ]),
    ("sensor", "07 · Untuk satuan siber", [
        "Untuk satuan siber, Halio menyediakan sensor.",
        "Dua puluh tiga feed berita, cek fakta, dan sumber resmi dipantau hampir realtime.",
        "Halio juga menunjukkan apa yang tidak bisa ia lihat.",
    ]),
    ("radar", "07 · Untuk satuan siber", [
        "Radar Ketahanan Kognitif merangkum tren secara anonim:",
        "kategori hoaks, trik yang sering dipakai, dan penipuan yang mencatut TNI AD.",
        "Kabar baru baru tampil setelah dikirim banyak orang berbeda.",
    ]),
    ("batas", "08 · Tata kelola", [
        "Ini alat pertahanan siber, bukan alat untuk mengawasi warga.",
        "Tidak ada profil individu, dan pesan pribadi tidak disimpan tanpa permintaan pengguna.",
    ]),
    ("pasang", "09 · Penerapan", [
        "Halio berjalan dalam satu kontainer, tanpa GPU dan tanpa API berbayar,",
        "sehingga dapat dipasang di server satuan.",
    ]),
    ("status", "10 · Status jujur", [
        "Ini masih prototipe. Korpus bantahan masih kecil,",
        "dan uji kami masih menemukan kalimat benar yang salah ditandai.",
        "Kami menampilkan angkanya, dan terus memperbaikinya.",
    ]),
    ("penutup", "Epilog", [
        "Ketahanan kognitif dimulai dari keluarga.",
        "Halio. Cek dulu, baru teruskan.",
    ]),
]


def cue_len(text: str) -> float:
    return max(MIN_CUE, len(text) / CPS)


def build() -> dict:
    t = 0.0
    scenes = []
    for sid, tag, lines in SCENES:
        start = t
        local = LEAD
        cues = []
        for line in lines:
            d = cue_len(line)
            cues.append({"text": line, "t0": round(local, 3), "t1": round(local + d, 3)})
            local += d + GAP
        dur = round(local - GAP + TAIL + EXTRA_TAIL.get(sid, 0.0), 3)
        scenes.append({"id": sid, "tag": tag, "start": round(start, 3), "dur": dur, "cues": cues})
        t += dur
    return {"fps": 30, "width": 1920, "height": 1080, "duration": round(t, 3), "scenes": scenes}


def ts(sec: float, sep: str = ",") -> str:
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if sep == ",":
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}"
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def write(tl: dict) -> None:
    (ROOT / "src").mkdir(exist_ok=True)
    (ROOT / "out").mkdir(exist_ok=True)
    (ROOT / "src" / "timeline.js").write_text(
        "// Generated by video/tools/build_timeline.py. Edit the narration there, not here.\n"
        f"window.TIMELINE = {json.dumps(tl, ensure_ascii=False, indent=1)};\n", encoding="utf-8")

    srt, ass_events, n = [], [], 1
    for sc in tl["scenes"]:
        for c in sc["cues"]:
            a, b = sc["start"] + c["t0"], sc["start"] + c["t1"]
            srt.append(f"{n}\n{ts(a)} --> {ts(b)}\n{c['text']}\n")
            ass_events.append(f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},Sub,,0,0,0,,{c['text']}")
            n += 1
    (ROOT / "out" / "halio-demo.srt").write_text("\n".join(srt), encoding="utf-8")

    ass = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,42,&H00F0F3F8,&H00F0F3F8,&H3326170E,&H3326170E,0,0,0,0,100,100,0,0,3,18,0,2,300,300,58,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ass_events) + "\n"
    (ROOT / "out" / "halio-demo.ass").write_text(ass, encoding="utf-8")

    md = ["# Naskah narasi · Video demo Halio", "",
          f"Durasi total: **{int(tl['duration'] // 60)} menit {tl['duration'] % 60:.0f} detik** (batas Rulebook: 10 menit).",
          "Kecepatan baca santai sekitar 14 karakter per detik. Subtitle di video mengikuti waktu di bawah ini,",
          "jadi rekam suara sambil memutar video tanpa musik (`halio-demo-tanpa-musik.mp4`) dan baca saat subtitle muncul.", "",
          "| Waktu | Scene | Narasi |", "|---|---|---|"]
    for sc in tl["scenes"]:
        for c in sc["cues"]:
            a = sc["start"] + c["t0"]
            md.append(f"| {int(a // 60)}:{a % 60:04.1f} | {sc['tag']} | {c['text']} |")
    md += ["", "Ubah narasi di `video/tools/build_timeline.py`, lalu render ulang (`video/README.md`)."]
    (ROOT / "NASKAH.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    tl = build()
    write(tl)
    print(f"{len(tl['scenes'])} scenes, {sum(len(s['cues']) for s in tl['scenes'])} cues, {tl['duration']:.1f} s")

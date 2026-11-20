"""Buat grafik SVG untuk README (docs/img/*.svg) dari data sungguhan di repo.

    python scripts/make_readme_charts.py

Angka yang diketik tangan (riwayat evaluasi, jumlah tes) tercatat di eval/RESULTS.md dan hasil pytest terakhir.
SVG memakai latar kartu putih sendiri supaya terbaca di tema gelap maupun terang GitHub.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)

BLUE, INK, MUTED, LINE, CREAM = "#014BAA", "#0E1726", "#5B6475", "#E7E1DC", "#F8F3F0"
RED, GREEN, ORANGE, SUN = "#B42318", "#067647", "#B54708", "#FFC83D"
FONT = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"
SERIF = "'Instrument Serif', Georgia, 'Times New Roman', serif"


def svg(w: int, h: int, body: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20" fill="#FFFFFF" stroke="{LINE}" stroke-width="2"/>'
            f'<g font-family="{FONT}" fill="{INK}">{body}</g></svg>\n')


def text(x, y, s, size=14, fill=INK, weight=400, anchor="start", family=None):
    fam = f' font-family="{family}"' if family else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"{fam}>{escape(str(s))}</text>'


# ---------- 1. angka kunci ----------
def tiles() -> str:
    items = [
        ("319", "tes otomatis lulus", BLUE), ("741", "vektor paritas Python ↔ JS, 0 beda", BLUE),
        ("0", "salah tuduh hoaks: 0/36 dev, 0/40 holdout", GREEN), ("0 / 27", "rilis resmi TNI & Kemhan dicap salah", GREEN),
        ("35", "entri korpus bantahan (dari 10)", BLUE), ("8", "serangan hidup di Medan Uji", BLUE),
        ("Ed25519", "tanda tangan Kartu Halio & LAPSUS", INK), ("≈2 ms", "median cek lokal (35 entri), tanpa AI", INK),
    ]
    w, h, cols, tw, th, pad = 1000, 366, 4, 226, 128, 22
    body = text(pad, 42, "Angka kunci Halio v1.0", 20, INK, 700)
    for i, (big, small, color) in enumerate(items):
        x, y = pad + (i % cols) * (tw + 16), 62 + (i // cols) * (th + 16)
        body += f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="14" fill="{CREAM}"/>'
        body += f'<rect x="{x}" y="{y}" width="6" height="{th}" rx="3" fill="{color}"/>'
        body += text(x + 22, y + 58, big, 38 if len(big) < 6 else 30, color, 800)
        # pecah label panjang jadi dua baris
        words, line1, line2 = small.split(), "", ""
        for wd in words:
            if not line2 and len(line1) + len(wd) < 24:
                line1 += wd + " "
            else:
                line2 += wd + " "
        body += text(x + 22, y + 88, line1.strip(), 13, MUTED) + (text(x + 22, y + 106, line2.strip(), 13, MUTED) if line2 else "")
    return svg(w, h, body, "Angka kunci Halio v1.0")


# ---------- 2. riwayat evaluasi ----------
def history() -> str:
    # eval/RESULTS.md (riwayat): salah-tuduh dev+holdout dan recall holdout. Baris v1.0 SUDAH DISETEL, ditandai.
    steps = [("Sebelum penjaga\ninti klaim", 11, 81), ("Setelah penjaga\ninti klaim", 1, 88), ("v1.0\n(disetel)", 0, 100)]
    w, h = 1000, 410
    body = text(24, 40, "Riwayat evaluasi pada set tulisan tim", 20, INK, 700)
    body += text(24, 62, "Batang biru: recall hoaks parafrase di holdout. Titik merah: jumlah pernyataan benar yang salah dicap hoaks (dev + holdout).", 13, MUTED)
    x0, base, ch = 90, 310, 190
    body += f'<line x1="{x0 - 20}" y1="{base}" x2="{w - 40}" y2="{base}" stroke="{LINE}" stroke-width="2"/>'
    for pct in (25, 50, 75, 100):
        y = base - ch * pct / 100
        body += f'<line x1="{x0 - 20}" y1="{y}" x2="{w - 40}" y2="{y}" stroke="{LINE}" stroke-dasharray="4 6"/>' + text(x0 - 30, y + 4, f"{pct}%", 12, MUTED, anchor="end")
    for i, (label, fh, rec) in enumerate(steps):
        cx = 210 + i * 300
        bh = ch * rec / 100
        color = BLUE if i < 2 else "#5C8FD6"
        body += f'<rect x="{cx - 56}" y="{base - bh}" width="112" height="{bh}" rx="10" fill="{color}"/>'
        body += text(cx, base - bh - 10, f"{rec}%", 20, INK, 700, "middle")
        body += f'<circle cx="{cx + 82}" cy="{base - 22}" r="15" fill="{RED if fh else GREEN}"/>' + text(cx + 82, base - 17, fh, 14, "#fff", 700, "middle")
        for j, ln in enumerate(label.split("\n")):
            body += text(cx, base + 26 + j * 18, ln, 13, MUTED, 500, "middle")
    body += text(w - 40, 392, "Holdout sudah tidak bersih: 100% adalah angka yang disetel, bukan estimasi akurasi.", 12, ORANGE, 600, "end")
    return svg(w, h, body, "Riwayat evaluasi Halio: recall holdout naik dari 81 ke 100 persen, salah tuduh turun dari 11 ke 0")


# ---------- 3. komposisi korpus ----------
def corpus() -> str:
    raw = json.loads((ROOT / "data" / "debunks.json").read_text(encoding="utf-8"))["debunks"]
    cats = Counter(d["kategori"] for d in raw)
    names = {"penipuan_catut_tni": "Catut TNI AD", "phishing": "Phishing & APK", "penipuan_rekrutmen": "Rekrutmen palsu", "penipuan_investasi": "Investasi & pinjol",
             "penipuan_telepon": "Penipuan telepon", "kesehatan": "Kesehatan", "penipuan_bansos": "Bansos palsu", "bencana": "Bencana", "keamanan_publik": "Keamanan publik"}
    palette = [BLUE, "#2F6FC4", "#5C8FD6", RED, ORANGE, GREEN, "#7A5AF8", "#667085", "#98A2B3"]
    w, h = 1000, 250
    body = text(24, 40, f"Korpus bantahan: {len(raw)} entri", 20, INK, 700)
    body += text(24, 62, "Setiap entri punya sumber bernama dan pola inti klaim (syarat) agar kabar benar tidak salah dituduh.", 13, MUTED)
    x, bw = 24, w - 48
    total = sum(cats.values())
    for (cat, n), color in zip(cats.most_common(), palette):
        seg = bw * n / total
        body += f'<rect x="{x:.1f}" y="82" width="{seg - 3:.1f}" height="44" rx="8" fill="{color}"/>'
        if seg > 34:
            body += text(x + seg / 2 - 1.5, 111, n, 17, "#fff", 700, "middle")
        x += seg
    lx, ly = 24, 168
    for (cat, n), color in zip(cats.most_common(), palette):
        body += f'<rect x="{lx}" y="{ly - 11}" width="14" height="14" rx="4" fill="{color}"/>' + text(lx + 22, ly + 1, f"{names.get(cat, cat)} ({n})", 13, INK)
        lx += 190
        if lx > w - 200:
            lx, ly = 24, ly + 28
    return svg(w, h, body, f"Komposisi korpus bantahan Halio: {len(raw)} entri menurut kategori")


# ---------- 4. kecepatan: luring vs AI (jalur) ----------
def lanes() -> str:
    w, h = 1000, 250
    body = text(24, 40, "Dua jalur, satu keputusan dari kode", 20, INK, 700)
    rows = [
        ("T1 luring", "TF-IDF + normalisasi frasa domain + registri buletin bertanda tangan", "tanpa AI, tanpa internet, ~2 ms", GREEN, 0.95),
        ("T2 opsional", "AI mencari halaman, kode menyalin kutipan lalu mencocokkan ulang kata per kata", "butuh jaringan dan kunci AI, 10 s - 3 menit", BLUE, 0.55),
    ]
    for i, (name, desc, cost, color, frac) in enumerate(rows):
        y = 78 + i * 76
        body += f'<rect x="24" y="{y}" width="{w - 48}" height="60" rx="12" fill="{CREAM}"/><rect x="24" y="{y}" width="{(w - 48) * frac:.0f}" height="60" rx="12" fill="{color}" opacity=".13"/>'
        body += f'<rect x="24" y="{y}" width="8" height="60" rx="4" fill="{color}"/>'
        body += text(48, y + 26, name, 16, color, 700) + text(48, y + 46, desc, 13, MUTED)
        body += text(w - 44, y + 36, cost, 13, INK, 600, "end")
    return svg(w, h, body, "Dua jalur pemeriksaan Halio: T1 luring dan T2 opsional dengan AI")


def main() -> None:
    for name, fn in [("angka-kunci", tiles), ("riwayat-evaluasi", history), ("komposisi-korpus", corpus), ("dua-jalur", lanes)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8", newline="\n")
        print("ditulis", f"docs/img/{name}.svg")


if __name__ == "__main__":
    main()

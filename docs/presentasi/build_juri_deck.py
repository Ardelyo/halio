"""Build the submission deck: the story deck (Halio_Deck_Cerita.pdf) plus a technical appendix taken from halio_deck_v2.html.

    python docs/presentasi/build_juri_deck.py      # needs pypdf and qrcode (pip install pypdf "qrcode[pil]") and Microsoft Edge

Order: story slides 1-10, an appendix divider that maps each appendix page to a judging criterion, nine technical slides from
the v2 deck (renumbered as appendix pages), a "try it" page with QR codes, then the story deck's closing slide.
Output: docs/presentasi/Halio_Deck_Juri.pdf (960x540 pt pages; appendix pages are scaled from 1440x810).
"""

from __future__ import annotations

import base64
import io
import re
import subprocess
import tempfile
from pathlib import Path

import qrcode
from pypdf import PdfReader, PdfWriter, Transformation

# lokasi berkas deck cerita, deck v2, sm path Edge buat render lampiran ke PDF
HERE = Path(__file__).parent
STORY = HERE / "Halio_Deck_Cerita.pdf"
V2 = HERE / "halio_deck_v2.html"
APPENDIX_HTML = HERE / "halio_lampiran.html"
UPDATE_HTML = HERE / "halio_slide_update.html"  # pengganti slide 9 & 10 (halaman asli gambar mentah, sumbernya ga ada)
OUT = HERE / "Halio_Deck_Juri.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# nomor slide dari deck v2 (mulai dari 1) sesuai urutan lampiran teknis buat dewan juri
PICK = [(5, "Arsitektur"), (12, "Cara kerja"), (13, "Sumber"), (9, "Halio Telusur"), (10, "Laporan analis"),
        (15, "Brief harian TNI AD"), (14, "Privasi"), (16, "Pengaman"), (17, "Hasil uji")]


# bikin QR code langsung jd data URI biar praktis ga perlu nyimpen file png sementra
def qr(url: str) -> str:
    img = qrcode.make(url, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# rakit HTML lampiran L1-L9 lengkap sm halaman pemetaan kriteria juri dan halaman QR coba langsung
def appendix_html() -> str:
    html = V2.read_text(encoding="utf-8")
    first = html.index('<section class="slide')
    last = html.rindex("</section>") + len("</section>")
    head, tail = html[:first], html[last:]
    slides = re.findall(r'<section class="slide.*?</section>', html, flags=re.S)
    assert len(slides) == 20, len(slides)
    n = len(PICK) + 1  # + halaman mode luring (L10) yg dirakit di bawah
    foot = '<div class="foot"><span>Halio · Lampiran teknis untuk Dewan Juri</span><span><b>L{k}</b> / L{n}</span></div>'

    pages = []
    for k, (idx, _label) in enumerate(PICK, 1):
        s = slides[idx - 1]
        s = re.sub(r'<div class="kicker">\d\d · ', f'<div class="kicker">Lampiran L{k} · ', s, count=1)
        s = re.sub(r'<div class="foot">.*?</div>\s*</section>', foot.format(k=k, n=n) + "\n</section>", s, count=1, flags=re.S)
        pages.append(s)

    divider = f'''<section class="slide blue">
  <div class="kicker">Lampiran teknis</div>
  <h2>Untuk Dewan Juri: <em>cara kerja di balik cerita.</em></h2>
  <div class="row" style="margin-top:52px;gap:28px;align-items:stretch;flex:1;margin-bottom:70px">
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Inovasi teknis · 25%</div><h3 style="color:#fff;margin-top:10px">L1 – L3</h3><p>Arsitektur dua pintu, cara AI dikekang (kode yang memutuskan), dan cara sumber dihitung adil.</p></div>
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Relevansi TNI AD · 25%</div><h3 style="color:#fff;margin-top:10px">L4 – L6</h3><p>Halio Telusur untuk analis, laporan yang bisa diaudit, dan brief harian narasi TNI AD.</p></div>
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Kelayakan · 15%</div><h3 style="color:#fff;margin-top:10px">L7, L8, L10</h3><p>Privasi sejak awal, batas yang dijaga, dan mode luring: tetap menjawab tanpa jaringan.</p></div>
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Fungsionalitas · 25%</div><h3 style="color:#fff;margin-top:10px">L9</h3><p>Hasil uji di server publik dan pada sampel publik TurnBackHoax, apa adanya.</p></div>
  </div>
  <div class="foot"><span>Semua angka bisa diperiksa di github.com/Ardelyo/halio</span><span>Lampiran</span></div>
</section>'''

    k_l = len(PICK) + 1
    luring = f'''<section class="slide">
  <div class="kicker">Lampiran L{k_l} · Mode luring</div>
  <h2>Tanpa sinyal, <em>Halio tetap menjawab.</em></h2>
  <div class="row" style="margin-top:44px;gap:28px;align-items:stretch;flex:1;margin-bottom:60px">
    <div class="card grow"><h3>Di perangkat</h3><p style="font-size:30px;line-height:1.4">Mesin pencocokan yang sama berjalan di browser dan PWA. Pesan tidak keluar dari perangkat; tanpa AI, tanpa web, tanpa server.</p></div>
    <div class="card grow"><h3>Identik dengan server</h3><p style="font-size:30px;line-height:1.4">603 vektor uji dan 3.900 judul nyata: <b>0 perbedaan</b> dengan Python. Diuji di Chrome dengan jaringan diputus.</p></div>
    <div class="card grow"><h3>Batasnya jujur</h3><p style="font-size:30px;line-height:1.4">Hanya mengenali 10 bantahan di korpus; di luar itu "belum ada pemeriksaan", bukan tebakan. Telegram tetap butuh internet.</p></div>
  </div>
  <p class="note" style="font-size:24px">Server T1 tanpa AI: median 0,5 ms per cek · jalur T1 diuji tanpa satu pun akses jaringan · rincian di <b>docs/LURING.md</b></p>
  {foot.format(k=k_l, n=n)}
</section>'''

    links = [("Cek pesan sekarang", "halio.ardelyo.com/cek.html", "https://halio.ardelyo.com/cek.html"),
             ("Video demo (5:01)", "youtu.be/s2EMpZI2r4g", "https://youtu.be/s2EMpZI2r4g"),
             ("Kode dan dokumen", "github.com/Ardelyo/halio", "https://github.com/Ardelyo/halio")]
    cards = "".join(
        f'<div class="card grow" style="text-align:center;display:flex;flex-direction:column;align-items:center;gap:18px">'
        f'<img src="{qr(u)}" alt="QR {t}" style="width:300px;height:300px;border-radius:12px">'
        f'<h3 style="font-size:38px;margin:0">{t}</h3><p style="font-size:26px;margin:0">{label}</p></div>'
        for t, label, u in links)
    try_it = f'''<section class="slide">
  <div class="kicker">Coba sendiri</div>
  <h2>Halio berjalan sekarang, <em>silakan dicoba.</em></h2>
  <div class="row" style="margin-top:44px;gap:30px;align-items:stretch">{cards}</div>
  <p class="note" style="margin-top:26px;font-size:24px">Bot Telegram <b>@halioid_bot</b> · Panduan juri: <b>docs/submission/UNTUK_JURI.md</b> · Rilis <b>v0.2.1-luring</b></p>
  <div class="foot"><span>Halio · Saring dulu, baru sharing</span><span>Ardellio S. A.</span></div>
</section>'''

    return head + "\n\n" + "\n\n".join([divider] + pages + [luring, try_it]) + "\n" + tail


def main() -> None:
    APPENDIX_HTML.write_text(appendix_html(), encoding="utf-8")
    # cetak lampiran HTML ke PDF via Edge headless, terus selipin sebelum slide penutup deck cerita
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "lampiran.pdf"
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--user-data-dir={tmp}\\edge", f"--print-to-pdf={pdf}", APPENDIX_HTML.resolve().as_uri()],
                       check=True, capture_output=True)
        # slide 9 (relevansi + luring) & 10 (bukti, batas) dirender ulang dr HTML biar angkanya mutakhir
        upd_pdf = Path(tmp) / "update.pdf"
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--user-data-dir={tmp}\\edge2", f"--print-to-pdf={upd_pdf}", UPDATE_HTML.resolve().as_uri()],
                       check=True, capture_output=True)
        story, appx, upd = PdfReader(STORY), PdfReader(pdf), PdfReader(upd_pdf)
        assert len(upd.pages) == 2, len(upd.pages)
        assert len(story.pages) == 11, len(story.pages)
        w = float(story.pages[0].mediabox.width)
        h = float(story.pages[0].mediabox.height)
        out = PdfWriter()
        replaced = {8: upd.pages[0], 9: upd.pages[1]}  # indeks 0: halaman 9 dan 10
        for i, p in enumerate(story.pages[:10]):
            out.add_page(replaced.get(i, p))
        for src in appx.pages:
            p = out.add_page(src)  # wajib transform salinan milik writer (pypdf 7 nolak ubah halaman reader langsung)
            k = w / float(p.mediabox.width)
            p.add_transformation(Transformation().scale(k, k))
            p.mediabox.lower_left = (0, 0)
            p.mediabox.upper_right = (w, h)
            p.cropbox.lower_left = (0, 0)
            p.cropbox.upper_right = (w, h)
        out.add_page(story.pages[10])
        out.add_metadata({"/Title": "Halio — Kartika Cyber Hackathon 2026", "/Author": "Ardellio S. A."})
        with OUT.open("wb") as f:
            out.write(f)
    print(f"{len(PdfReader(OUT).pages)} halaman -> {OUT}")


if __name__ == "__main__":
    main()

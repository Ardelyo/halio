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

HERE = Path(__file__).parent
STORY = HERE / "Halio_Deck_Cerita.pdf"
V2 = HERE / "halio_deck_v2.html"
APPENDIX_HTML = HERE / "halio_lampiran.html"
OUT = HERE / "Halio_Deck_Juri.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# v2 slide numbers (1-based) in appendix order, with the label that replaces the v2 kicker number
PICK = [(5, "Arsitektur"), (12, "Cara kerja"), (13, "Sumber"), (9, "Halio Telusur"), (10, "Laporan analis"),
        (15, "Brief harian TNI AD"), (14, "Privasi"), (16, "Pengaman"), (17, "Hasil uji")]


def qr(url: str) -> str:
    img = qrcode.make(url, box_size=10, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def appendix_html() -> str:
    html = V2.read_text(encoding="utf-8")
    first = html.index('<section class="slide')
    last = html.rindex("</section>") + len("</section>")
    head, tail = html[:first], html[last:]
    slides = re.findall(r'<section class="slide.*?</section>', html, flags=re.S)
    assert len(slides) == 20, len(slides)
    n = len(PICK)
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
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Kelayakan · 15%</div><h3 style="color:#fff;margin-top:10px">L7 – L8</h3><p>Privasi sejak awal dan batas yang dijaga: narasi dan klaim, bukan orang.</p></div>
    <div class="card grow"><div class="kicker" style="font-size:22px;color:var(--sun)">Fungsionalitas · 25%</div><h3 style="color:#fff;margin-top:10px">L9</h3><p>Hasil uji di server publik dan pada sampel publik TurnBackHoax, apa adanya.</p></div>
  </div>
  <div class="foot"><span>Semua angka bisa diperiksa di github.com/Ardelyo/halio</span><span>Lampiran</span></div>
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
  <p class="note" style="margin-top:26px;font-size:24px">Bot Telegram <b>@halioid_bot</b> · Panduan juri: <b>docs/submission/UNTUK_JURI.md</b> · Rilis <b>v0.2.0-submission</b></p>
  <div class="foot"><span>Halio · Saring dulu, baru sharing</span><span>Ardellio S. A.</span></div>
</section>'''

    return head + "\n\n" + "\n\n".join([divider] + pages + [try_it]) + "\n" + tail


def main() -> None:
    APPENDIX_HTML.write_text(appendix_html(), encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "lampiran.pdf"
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--user-data-dir={tmp}\\edge", f"--print-to-pdf={pdf}", APPENDIX_HTML.resolve().as_uri()],
                       check=True, capture_output=True)
        story, appx = PdfReader(STORY), PdfReader(pdf)
        assert len(story.pages) == 11, len(story.pages)
        w = float(story.pages[0].mediabox.width)
        h = float(story.pages[0].mediabox.height)
        out = PdfWriter()
        for p in story.pages[:10]:
            out.add_page(p)
        for src in appx.pages:
            p = out.add_page(src)  # transform the writer's copy (pypdf 7 refuses to edit reader pages)
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

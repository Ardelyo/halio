"""Uji tuduhan palsu pada rilis RESMI TNI/Kemhan: berapa yang salah dicap "terbukti salah"?

    python eval/eval_resmi_tni.py --ekstrak-saja   # cuma unduh dan tampilkan judul + paragraf pembuka (tanpa menjalankan Halio)
    python eval/eval_resmi_tni.py                  # jalankan Halio (tanpa AI, tanpa cek tautan), tulis eval/RESMI_TNI_RESULTS.md

Daftar rilis (eval/resmi_tni_urls.json) dipilih SEBELUM Halio dijalankan pada rilis itu, dari hasil pencarian di situs resmi.
Tiap rilis dipakai sbg "pesan" = judul + paragraf pembuka (maks. 2 paragraf, 600 karakter), seperti judul + awal berita yg diteruskan.
Semua rilis ini bukan hoaks, jadi setiap "terbukti_salah" dihitung tuduhan palsu dan dilaporkan apa adanya, ga disetel ulang.
Isi halaman ga disalin ke repo (cuma tautan + judul pendek); halaman diunduh saat dijalankan, seperti eval/eval_public.py.
"""

from __future__ import annotations

import collections
import html
import json
import re
import subprocess
import sys
import time
import urllib.request
from dataclasses import replace
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402

URLS = ROOT / "eval" / "resmi_tni_urls.json"
OUT = ROOT / "eval" / "RESMI_TNI_RESULTS.md"
UA = "halio-eval (riset anti-disinformasi; hanya halaman publik)"
MAX_CHARS = 600


class _Page(HTMLParser):
    """Ambil <title>, og:title, og:description, dan teks <p> (di luar script/style/nav/footer)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.og_title = ""
        self.og_desc = ""
        self.paras: list[str] = []
        self._in_title = False
        self._p: list[str] | None = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "nav", "footer", "header", "noscript"):
            self._skip += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            if a.get("property") == "og:title":
                self.og_title = a.get("content") or ""
            elif a.get("property") == "og:description" or a.get("name") == "description":
                self.og_desc = self.og_desc or (a.get("content") or "")
        elif tag == "p" and not self._skip:
            self._p = []

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "header", "noscript"):
            self._skip = max(0, self._skip - 1)
        elif tag == "title":
            self._in_title = False
        elif tag == "p" and self._p is not None:
            text = re.sub(r"\s+", " ", "".join(self._p)).strip()
            if text:
                self.paras.append(text)
            self._p = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._p is not None:
            self._p.append(data)


def fetch(url: str) -> str:
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"gagal mengunduh {url}")


_BOILER = re.compile(r"permohonan informasi publik|^copyright|^©|hak cipta|bagikan|baca juga", re.I)
_GENERIC_TITLE = re.compile(r"^(kementerian pertahanan|biro humas|ppid)", re.I)


def _clean(raw: str) -> str:
    raw = re.sub(r"<(script|style)[^>]*>.*?</>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<br\s*/?>|</p>|</div>|</li>", " ", raw, flags=re.I)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def extract(url: str) -> tuple[str, str]:
    raw = fetch(url)
    p = _Page()
    p.feed(raw)
    # judul: h1 artikel (bukan judul situs), lalu h2 pertama yg bukan widget, lalu og:title/<title>
    cands = [_clean(m) for m in re.findall(r"<h1[^>]*>(.*?)</h1>", raw, flags=re.S | re.I)]
    cands += [_clean(m) for m in re.findall(r"<h2(?![^>]*widget)[^>]*>(.*?)</h2>", raw, flags=re.S | re.I)]
    cands += [html.unescape(p.og_title).strip(), html.unescape(p.title).strip()]
    title = next((c for c in cands if c and not _GENERIC_TITLE.match(c)), cands[-1] if cands else "")
    title = re.sub(r"\s*[—|-]\s*(PPID TNI AD|PPID TNI|TNI Angkatan Darat)\s*$", "", title).strip()
    # isi: <div class="content"> (PPID), lalu paragraf <p> yg bukan boilerplate, lalu og:description
    body = ""
    m = re.search(r'<div class="content">(.*?)</div>', raw, flags=re.S | re.I)
    if m:
        body = _clean(m.group(1))
    if len(body) < 80:
        paras = [t for t in p.paras if len(t) >= 70 and not _BOILER.search(t)]
        body = " ".join(paras[:2]) if paras else ""
    if len(body) < 80:
        body = _clean(p.og_desc)
    sents = [x for x in re.split(r"(?<=[.!?])\s+", body) if x and not _BOILER.search(x)]
    lead = " ".join(sents)
    return title, re.sub(r"\s+", " ", lead).strip()


def unit_text(title: str, lead: str) -> str:
    text = f"{title}. {lead}".strip()
    return text[:MAX_CHARS].rsplit(" ", 1)[0] if len(text) > MAX_CHARS else text


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def wilson_upper(k: int, n: int, z: float = 1.96) -> float:
    if n == 0:
        return 0.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return (c + h) / d


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # konsol Windows (cp1252) gagal mencetak sebagian judul
    items = json.loads(URLS.read_text(encoding="utf-8"))["items"]
    only_extract = "--ekstrak-saja" in sys.argv
    cfg = replace(Settings(), google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)
    rows, failed = [], []
    for it in items:
        try:
            title, lead = extract(it["url"])
        except Exception as e:  # noqa: BLE001
            failed.append((it["kategori"], it["url"], str(e)[:80]))
            continue
        text = unit_text(title, lead)
        if only_extract:
            print(f"[{it['kategori']}] {title[:110]}\n    {lead[:230]}\n")
            continue
        r = pipeline.check(text, cfg)
        rows.append({"kategori": it["kategori"], "url": it["url"], "title": title, "chars": len(text), "status": r["status"],
                     "reason": r["reason"], "score": (r["match"] or {}).get("score"), "debunk": (r["match"] or {}).get("debunk_id"),
                     "kind": r["kind"]})
        time.sleep(0.8)
    if only_extract:
        print(f"diunduh {len(items) - len(failed)} dari {len(items)}; gagal: {failed}")
        return 0

    commit = git("rev-parse", "HEAD")
    dirty = bool(git("status", "--porcelain", "--", "backend", "data", "eval/eval_resmi_tni.py", "eval/resmi_tni_urls.json"))
    n = len(rows)
    false_acc = [r for r in rows if r["status"] == "terbukti_salah"]
    by_status = collections.Counter(r["status"] for r in rows)
    lines = [
        "# Uji tuduhan palsu pada rilis resmi TNI dan Kemhan",
        "",
        "> **Jenis:** Bukti · **Untuk:** juri dan pengembang · dibuat otomatis oleh `eval/eval_resmi_tni.py`",
        "",
        f"- Tanggal: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Commit yang diuji: `{commit[:10]}` (berkas backend, data, skrip, dan daftar tautan bersih dari perubahan yang belum di-commit: **{'tidak' if dirty else 'ya'}**)",
        f"- Rilis: {n} diuji dari {len(items)} di daftar ({len(failed)} gagal diunduh)",
        "- Daftar rilis dipilih sebelum Halio dijalankan pada rilis itu, dari pencarian di situs resmi (`tni.mil.id`, `ppid.tniad.mil.id`, `kemhan.go.id`). Tidak ada rilis yang dibuang atau diganti setelah melihat hasil",
        "- Pesan uji: judul + paragraf pembuka (maks. 600 karakter). Mode: pencocokan lokal tanpa AI dan tanpa cek tautan, korpus `data/debunks.json` apa adanya",
        "- Semua rilis ini bukan hoaks. Maka setiap \"terbukti salah\" dihitung tuduhan palsu dan dilaporkan di bawah, tidak disetel ulang",
        "",
        "## Hasil",
        "",
        "| Metrik | Nilai |",
        "|---|---|",
        f"| **Rilis resmi yang salah dicap \"terbukti salah\"** | **{len(false_acc)} dari {n}** |",
        f"| Batas atas 95% (Wilson) | {wilson_upper(len(false_acc), n):.1%} |",
        f"| Tidak yakin | {by_status['tidak_yakin']} |",
        f"| Belum ada pemeriksaan | {by_status['belum_ada_pemeriksaan']} |",
        f"| Alasan \"tampak meluruskan\" (penjaga klarifikasi bekerja) | {sum(1 for r in rows if r['reason'] == 'tampak_meluruskan')} |",
        "",
    ]
    if false_acc:
        lines += ["## Tuduhan palsu (dicatat terbuka)", "", "| Kategori | Bantahan yang cocok | Skor | Judul |", "|---|---|---|---|"]
        lines += [f"| {r['kategori']} | {r['debunk']} | {r['score']} | {r['title'][:100]} ([tautan]({r['url']})) |" for r in false_acc]
        lines.append("")
    lines += ["## Per rilis", "", "| Kategori | Status | Alasan | Skor | Judul |", "|---|---|---|---|---|"]
    lines += [f"| {r['kategori']} | {r['status']} | {r['reason']} | {r['score'] if r['score'] is not None else '-'} | [{r['title'][:80]}]({r['url']}) |" for r in rows]
    if failed:
        lines += ["", "## Gagal diunduh (dilewati, dicatat)", ""] + [f"- {k}: {u}" for k, u, _ in failed]
    lines += ["", f"{n} rilis dari tiga situs resmi bukan sampel acak dan bukan evaluasi independen; angkanya menunjukkan perilaku pada jenis teks yang paling berisiko (klarifikasi, rekrutmen), bukan akurasi umum.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"rilis {n}/{len(items)} | salah dicap terbukti_salah: {len(false_acc)} | batas atas {wilson_upper(len(false_acc), n):.1%} | {dict(by_status)} | commit {commit[:10]} bersih={not dirty}")
    return 1 if false_acc else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Bikin backend/tests/parity_vectors.json: hasil pipeline.check Python (mode T1) utk banyak teks, buat dibandingin sm mesin JS.

    python scripts/gen_parity_vectors.py           # tulis
    python scripts/gen_parity_vectors.py --check   # exit 1 kalo basi (dipake tes)

Isi vektor: seluruh item eval (dev + holdout), kasus tepi tulis tangan, dan variasi acak (seed tetap) dr korpus + set eval.
Mesin JS (web/engine/halio-local.js) wajib ngasih jawaban yg sama utk semuanya.
"""

from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402

OUT = ROOT / "backend" / "tests" / "parity_vectors.json"
CFG = replace(Settings(), google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)

HAND = [
    "Selamat pagi semua, semoga hari ini menyenangkan.",
    "INFO VALID!!! SEGERA SEBARKAN KE 10 GRUP!!! GEMPA BESAR DAN TSUNAMI AKAN MELANDA JAKARTA MINGGU DEPAN TANGGAL 12!!!",
    "Hati-hati penipuan bansos, itu hoaks. Pemerintah tidak pernah minta biaya admin lewat WhatsApp.",
    "BMKG membantah isu gempa besar akan terjadi minggu depan, itu hoaks dan tidak benar.",
    "Ada calo penerimaan TNI AD, bayar 90 juta dijamin lulus. Hubungi 0812-3456-7890 atau email budi@mail.com segera.",
    "Pendaftaran Bintara TNI AD 2026 dibuka di rekrutmen.tniad.mil.id, gratis tanpa biaya apa pun.",
    "Video Presiden bagi-bagi bantuan tunai, daftar lewat WA.\nBayar biaya admin Rp150 ribu.\nKuota hanya 100 orang hari ini terakhir.",
    "Gempa 8,5 SR akan terjadi tanggal 5 Desember menurut peramal. Sementara itu harga cabai naik 40 persen di Jawa Barat.",
    "Judul satu tanpa titik\nJudul dua juga pendek\nJudul tiga tetap pendek\nJudul empat lagi",
    "Klik https://bit.ly/abc123 untuk klaim saldo e-toll gratis Rp500 ribu, isi data sekarang juga",
    "cek bansos-kemensos.xyz/daftar dan kemensos.go.id.bansos.xyz untuk hadiah",
    "Menurut saya ini kayaknya cuma salam saja, amin.",
    "kapan bantuan cair?",
    "Air kelapa dicampur garam dan jeruk nipis bisa menyembuhkan covid, ampuh dan manjur!",
    "Air kelapa tidak bisa menyembuhkan covid, tidak ada bukti klinis dari Kemenkes.",
    "Penculik anak berkeliaran naik mobil, sebarkan ke semua grup sebelum terlambat!!!",
    "Info dari PMI: gempa dan tsunami akan terjadi bulan depan, sebarkan.",
    "tolong dong min, kuota gratis 30GB dari operator, klik link ini bagikan ke 5 grup",
    "Bapak/Ibu, mohon maaf mengganggu. Terima kasih atas perhatiannya.",
    "Dapatkan hadiah Rp 10.000.000 dari presiden. Transfer biaya administrasi ke rekening 1234567890123 sekarang.",
    "Pemerintah memberikan bantuan sosial tunai kepada keluarga penerima manfaat sesuai data resmi DTKS.",
    "ADA KABAR BAIK!!! BANSOS CAIR BESOK, DAFTAR WA 08123456789, BAYAR ADMIN, SEBARKAN!!!",
    "gempaaaa besaaar akan terjadiiii minggu depaaan!!!",
    "résumé café naïve — Gempa besar akan terjadi minggu depan tanggal 3",
    "😀😀😀 gempa tsunami akan terjadi tanggal 10 😱",
    "a",
    "Artikel “Berita Duka 😭 Salah Satu Personil Band” Kabar Duka Menyebar " + "😭 kabar duka menyebar luas " * 20,
    "Gempa besar tsunami akan terjadi minggu depan 😱 " * 12 + "tanggal 3.",
    "   ",
    "Harga BBM naik besok\nGunung Merapi erupsi lagi\nTimnas menang telak\nBanjir rendam Jakarta Utara",
    "Presiden resmikan jalan tol baru\nBMKG beri peringatan cuaca ekstrem\nHarga emas turun hari ini",
    "Gempa tsunami akan terjadi minggu depan\nSebarkan segera\nBMKG hoaks",
    "Judul pendek satu\n\nJudul pendek dua\n\n\nJudul pendek tiga",
    "Kemenkes sebut kasus naik\nPolri tangkap calo TNI\nKomdigi blokir situs judol\nOJK cabut izin pinjol\nBPJS luncurkan aplikasi baru\nBI tahan suku bunga",
    "Cek www.kemensos.go.id dan https://bit.ly/abc, juga http://user:pw@Contoh.COM:8080/path?x=1 ya.",
    "Prabowo bagi-bagi uang. Daftar lewat WhatsApp. Presiden Prabowo bagi-bagi uang. Daftar lewat WhatsApp.",
    "Sebuah kalimat yang sangat panjang " + "dan terus berlanjut tanpa henti " * 15 + "gempa akan terjadi tanggal 2.",
]


def _items() -> list[str]:
    texts: list[str] = []
    for name in ("testset.jsonl", "holdout.jsonl"):
        for line in (ROOT / "eval" / name).read_text(encoding="utf-8").splitlines():
            if line.strip():
                texts.append(json.loads(line)["text"])
    return texts


def _fuzz(base: list[str], corpus: list[str], n: int = 420) -> list[str]:
    rnd = random.Random(20261113)
    pool = base + corpus
    fillers = ["Mohon diteruskan.", "SEBARKAN!!!", "Info penting hari ini.", "Menurut saya ini bahaya.", "Cek https://bit.ly/x1 sekarang juga.",
               "Hubungi 081234567890.", "Terima kasih.", "Segera, hari ini terakhir!"]
    out: list[str] = []
    for _ in range(n):
        a, b = rnd.choice(pool), rnd.choice(pool)
        kind = rnd.randrange(6)
        if kind == 0:
            out.append(f"{a} {rnd.choice(fillers)}")
        elif kind == 1:
            out.append(f"{a}\n{b}")
        elif kind == 2:
            out.append(a.upper() if rnd.random() < 0.5 else a.lower())
        elif kind == 3:
            words = a.split()
            out.append(" ".join(words[: max(3, len(words) // 2)]))
        elif kind == 4:
            out.append(a.replace("a", "aa", 2).replace("yang", "yg"))
        else:
            out.append(f"{rnd.choice(fillers)} {a}. {b}")
    return out


def build() -> list[dict]:
    import json as _json

    corpus = _json.loads((ROOT / "data" / "debunks.json").read_text(encoding="utf-8"))["debunks"]
    corpus_texts = [t for d in corpus for t in [d["klaim"], *d.get("varian", [])]]
    base = _items()
    texts = list(dict.fromkeys(base + HAND + corpus_texts + _fuzz(base, corpus_texts)))
    vectors = []
    for text in texts:
        r = pipeline.check(text, CFG)
        v = {
            "text": text,
            "status": r["status"], "reason": r["reason"], "claim": r["claim"], "checkworthiness": r["checkworthiness"],
            "debunk_id": (r["match"] or {}).get("debunk_id"), "score": (r["match"] or {}).get("score"),
            "kind": r["kind"], "info": r["info"], "manipulation": r["manipulation"], "attribution": r["attribution"],
            "domains": r["links"]["domains"], "warnings": r["links"]["warnings"], "cari_sendiri": r["cari_sendiri"],
            "voice_script": r["voice_script"], "offer_human_review": r["offer_human_review"], "method": r["method"],
        }
        if r.get("claims"):
            v["claims"] = [{k: c.get(k) for k in ("claim", "status", "reason")} | {"debunk_id": (c.get("match") or {}).get("debunk_id")} for c in r["claims"]]
        vectors.append(v)
    return vectors


def render() -> str:
    return json.dumps({"note": "digenerate scripts/gen_parity_vectors.py dr pipeline.check python (T1), jgn diedit manual", "vectors": build()},
                      ensure_ascii=False, indent=0) + "\n"


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("parity_vectors.json basi: jalankan python scripts/gen_parity_vectors.py")
            return 1
        print("parity_vectors.json up to date")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    n = len(json.loads(text)["vectors"])
    print(f"ditulis {OUT.relative_to(ROOT)}: {n} vektor, {len(text) // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""The same investigation, told for a grandmother: one plain verdict sentence, what to know, since when, who already
debunked it, and what to do. Built only from the checked report (no new model call, no new facts)."""

from __future__ import annotations

from ..dates import human_date

SARAN = {
    "terbukti_salah": "Jangan diteruskan. Kalau sudah terlanjur, beri tahu grup bahwa kabar ini tidak benar.",
    "tidak_yakin": "Tahan dulu, jangan diteruskan. Tanyakan ke anak atau cucu, atau cek situs resmi.",
    "belum_ada_pemeriksaan": "Jangan diteruskan dulu. Kabar yang benar biasanya juga diberitakan media besar atau situs resmi.",
    "sejalan_dengan_sumber": "Boleh dibagikan, tetapi sertakan sumbernya dan cek tanggalnya.",
    "dilaporkan_media": "Boleh dibagikan dengan menyebut medianya. Ingat, ini berita, belum diperiksa pemeriksa fakta.",
}


def _who(rep: dict) -> list[str]:
    names: list[str] = []
    for b in rep.get("bukti", []):
        if b.get("hubungan") in ("refutes", "claimreview") and b["penerbit"] not in names:
            names.append(b["penerbit"])
    return names[:4]


def headline(rep: dict, who: list[str]) -> str:
    s, r = rep["status"], rep.get("reason", "")
    if s == "terbukti_salah":
        return "Kabar ini tidak benar."
    if r == "dibantah_versi_mirip":
        by = ", ".join(who[:2]) if who else "sumber resmi atau pemeriksa fakta"
        return f"Kabar yang sangat mirip sudah dinyatakan tidak benar oleh {by}."
    if s == "tidak_yakin":
        return "Halio belum bisa memastikan. Buktinya belum cukup atau saling bertentangan."
    if s == "sejalan_dengan_sumber":
        return "Kabar ini sejalan dengan keterangan sumber resmi."
    if s == "dilaporkan_media":
        return "Kabar ini diberitakan beberapa media, tetapi belum diperiksa pemeriksa fakta."
    return "Belum ada yang memeriksa kabar ini, jadi Halio tidak mau menebak."


def build(rep: dict) -> dict:
    who = _who(rep)
    L = rep.get("laporan") or {}
    points = [s["teks"] for s in (L.get("ringkasan") or [])[:3]] + [s["teks"] for s in (L.get("temuan") or [])[:1]]
    a = rep.get("asal")
    since = ""
    if a and a.get("pertama", {}).get("tanggal"):
        since = f"Kabar seperti ini sudah muncul di internet sejak {human_date(a['pertama']['tanggal'])}."
    head = headline(rep, who)
    advice = SARAN.get(rep["status"], SARAN["belum_ada_pemeriksaan"])
    spoken = " ".join([head, *points[:2], since, (f"Yang sudah membantah: {', '.join(who)}." if who else ""), advice]).strip()
    return {"judul": head, "poin": points, "sejak": since, "pembantah": who, "saran": advice, "suara": " ".join(spoken.split())}

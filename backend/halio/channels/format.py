"""Plain-language chat reply shared by all channels."""

from __future__ import annotations

from html import escape

from ..dates import human_date as _date
from ..outlets import is_not_a_source

ICON = {
    "terbukti_salah": "🔴",
    "sejalan_dengan_sumber": "🟢",
    "dilaporkan_media": "🔵",
    "tidak_yakin": "🟠",
    "belum_ada_pemeriksaan": "⚪",
}

REASON = {
    "satu_media_melaporkan": "Baru satu kelompok media yang melaporkan; belum cukup untuk dikatakan terkonfirmasi.",
    "laporan_media_tanpa_tanggal_baru": "Ada laporan media, tetapi tanggalnya tidak jelas atau sudah lama.",
    "tidak_ada_sumber_relevan": "Halio membuka beberapa halaman, tetapi tidak ada yang menyatakan klaim ini secara utuh.",
    "media_melaporkan_bantahan": "Media melaporkan adanya bantahan, tetapi belum ada pemeriksa fakta atau sumber resmi yang memeriksanya.",
    "sumber_resmi_tanpa_tanggal_atau_lama": "Ada sumber resmi yang mendukung, tetapi tanggalnya tidak jelas atau sudah lama.",
    "berita_media_dikenal": "Belum ada pemeriksa fakta yang membahas berita ini, dan itu wajar untuk berita biasa.",
    "kumpulan_judul": "Gambar ini berisi beberapa judul, bukan satu kabar.",
    "tidak_ada_bantahan": "Belum ada pemeriksa fakta yang membahas kabar ini.",
    "mirip_tapi_tidak_sama": "Topiknya mirip dengan kabar yang pernah dicek, tetapi isinya tidak sama persis.",
    "inti_klaim_tidak_ada": "Topiknya mirip dengan kabar yang pernah dicek, tetapi inti klaimnya berbeda.",
    "bukan_klaim_faktual": "Isinya lebih mirip pendapat atau salam, bukan kabar yang bisa dicek.",
    "tampak_meluruskan": "Pesan ini tampaknya justru meluruskan kabar bohong.",
    "bukti_bertentangan": "Sumber-sumber yang ditemukan saling bertentangan.",
    "tidak_ada_kutipan_terverifikasi": "Sumber dari pencarian web tidak bisa dibuktikan isinya.",
    "memerlukan_verifikasi_ai": "Ini informasi resmi, tetapi buktinya belum cukup untuk dinyatakan sejalan.",
}
HEADLINE = {
    "beberapa_klaim": ("🧩", "PESAN BERISI BEBERAPA KLAIM"),
    "berita_media_dikenal": ("📰", "BERITA DARI MEDIA DIKENAL"),
    "kumpulan_judul": ("🗂", "BEBERAPA JUDUL SEKALIGUS"),
}
ACTION_BY_REASON = {
    "berita_media_dikenal": "Ini bukan kabar mencurigakan. Halio belum menilai isinya; untuk hal penting, bandingkan dengan satu atau dua media lain.",
    "kumpulan_judul": "Kirim satu judul atau satu berita per pesan, supaya bisa diperiksa satu per satu.",
}
REJECTED = {
    "mesin_pencari_atau_pengalih": "tautannya hanya mesin pencari atau pengalih",
    "bukan_sumber_dikenal": "situsnya bukan sumber yang dikenal",
    "http_404": "halaman tidak ditemukan", "http_403": "situs menolak dibuka otomatis", "http_410": "halaman sudah dihapus",
    "domain_bukan_sumber_primer": "halamannya dari media biasa; Halio hanya menerima situs resmi dan pemeriksa fakta sebagai bukti",
    "kutipan_tidak_ada_di_halaman": "kutipan dari AI tidak cocok dengan isi halaman",
    "redirect_ke_domain_lain": "halaman dialihkan ke situs lain",
    "sumber_tidak_dapat_diakses": "halaman tidak bisa dibuka",
}
ACTION = {
    "dilaporkan_media": "Boleh dibagikan dengan menyebut sumbernya. Ini laporan media, bukan pemeriksaan fakta: cek tanggalnya dan bandingkan dulu.",
    "terbukti_salah": "Jangan diteruskan. Kirim kartu di bawah ke grup untuk meluruskan.",
    "sejalan_dengan_sumber": "Boleh dibagikan, tetapi cek tanggal dan konteksnya di sumber dulu.",
    "tidak_yakin": "Tahan dulu. Cari kabarnya di situs resmi, atau tanyakan ke pemeriksa manusia.",
    "belum_ada_pemeriksaan": "Jangan diteruskan dulu. Halio tidak mau menebak.",
}


def _how(result: dict) -> list[str]:
    """Short, true list of what Halio actually did for this message."""
    steps = []
    if result.get("media"):
        steps.append("Membaca isi foto/suara Anda (keasliannya tidak dinilai)")
    m = result.get("match")
    if result.get("claims"):
        steps.append(f"Pesan dipecah menjadi {len(result['claims'])} klaim; tiap klaim diperiksa sendiri")
    elif m:
        steps.append(f"Dicocokkan dengan bantahan terverifikasi: cocok ({round(m['score'] * 100)}%)")
    else:
        steps.append("Dicocokkan dengan bantahan terverifikasi: tidak ada yang cukup mirip")
    ev = result.get("evidence")
    if ev:
        q = f" (kata kunci: {', '.join(ev['dicari'][:2])})" if ev.get("dicari") else ""
        steps.append(f"AI mencari di web{q}; Halio membuka {ev['dibuka']} halaman, {ev['relevan']} berisi kalimat yang cocok dengan klaim (disalin oleh kode)")
        why = sorted({REJECTED.get(r["alasan"], "halaman tidak bisa dipakai") for r in ev.get("ditolak", [])})
        if ev.get("ditolak"):
            steps.append("Tidak dipakai: " + "; ".join(why[:2]))
    elif "gemini_search" in (result.get("method") or ""):
        n = result.get("llm") or {}
        found, ok = n.get("sumber_ditemukan", 0), n.get("sumber_terverifikasi", 0)
        steps.append(f"AI mencari di web: {found} sumber, {ok} lolos dicek ulang oleh kode")
        why = sorted({REJECTED.get(r["alasan"], "") for r in n.get("sumber_ditolak", [])} - {""})
        if found and not ok and why:
            steps.append("Tidak dipakai karena " + "; ".join(why[:2]))
    for c in [c for c in (result.get("links") or {}).get("checked", []) if not is_not_a_source(c["final_url"])][:2]:
        who = f" ({c['outlet']})" if c.get("outlet") else ""
        steps.append(f"Tautan {c['host']}{who}: " + ("terbuka" if c["state"] == "terbuka" else (c["note"] or c["state"])))
    return steps


def many_claims(result: dict) -> bool:
    return bool(result.get("claims"))


def reply_text(result: dict, html: bool = False) -> str:
    # In HTML mode every dynamic string is escaped: the sapaan and link hosts come from the user,
    # and a stray "<" makes Telegram reject the whole message.
    from .. import version_line

    e = (lambda s: escape(str(s), quote=False)) if html else str
    b = (lambda s: f"<b>{e(s)}</b>") if html else (lambda s: f"*{s}*")
    status = result["status"]
    icon, label = HEADLINE.get(result.get("reason", ""), (ICON[status], result["status_label"].upper()))
    lines = [f"{icon} {b(label)}", ""]
    match = None if many_claims(result) else result.get("match")
    info = result.get("info") or {}
    if result.get("kind") == "berita_media" and info:
        lines += [b(info["judul"] or "(tanpa judul)"), f"{e(info['penerbit'])}" + (f" · {e(_date(info['terbit']))}" if info.get("terbit") else "")]
        if info.get("ringkasan"):
            lines += ["", f"“{e(info['ringkasan'])}”", "<i>(ringkasan dari halaman itu sendiri, bukan penilaian Halio)</i>" if html else "(ringkasan dari halaman itu sendiri, bukan penilaian Halio)"]
        lines.append("")
    elif result.get("kind") == "kumpulan_judul" and info.get("judul_list"):
        lines += [f"{i}. {e(t)}" for i, t in enumerate(info["judul_list"], 1)] + [""]
    plain = result.get("reason", "") in ("berita_media_dikenal", "kumpulan_judul")
    many = result.get("claims")
    if many:
        for i, c in enumerate(many, 1):
            claim = c["claim"] if len(c["claim"]) <= 120 else c["claim"][:117].rsplit(" ", 1)[0] + "…"
            why = (c.get("match") or {}).get("sederhana") or (c.get("evidence") or {}).get("alasan") or REASON.get(c.get("reason", ""), "")
            src = ((c.get("match") or {}).get("sumber") or [None])[0]
            link = (f'\n    Sumber: <a href="{escape(src["url"])}">{e(src["nama"])}</a>' if html else f"\n    Sumber: {src['nama']} {src['url']}") if src else ""
            lines += [f"{i}. {ICON[c['status']]} {b(c['status_label'])}", f"   “{e(claim)}”", f"   {e(why[:240])}{link}", ""]
    elif not plain:
        lines.append(e(match["sederhana"]) if match else e(result["voice_script"]))
    reason = REASON.get(result.get("reason", ""))
    if reason and not match:
        lines += ["", f"📌 {e(reason)}"]
    if result.get("attribution"):
        lines += ["", "⚠️ " + b("Sumber yang disebut berbeda") + ": " + e(result["attribution"]["catatan"])]
    techs = result["manipulation"]["techniques"]
    if techs:
        lines += ["", "⚠️ " + b("Trik dalam pesan") + ": " + e(", ".join(t["label"].lower() for t in techs[:3]))]
    for w in result["links"]["warnings"][:2]:
        lines.append(f"🔗 {e(w)}")
    lines += ["", "🔎 " + b("Cara Halio memeriksa")] + [f"  ✓ {e(x)}" for x in _how(result)]
    if match:
        if html:
            links = " · ".join(f'<a href="{escape(s["url"])}">{e(s["nama"])}</a>' for s in match["sumber"][:2])
        else:
            links = "\n".join(f"{s['nama']}: {s['url']}" for s in match["sumber"][:2])
        lines += ["", "📚 " + b("Sumber") + ": " + links]
    ev = result.get("evidence")
    if ev and ev.get("items"):
        bar = "■" * ev["kekuatan"] + "□" * (4 - ev["kekuatan"])
        lines += ["", "🔍 " + b("Yang Halio temukan") + f"  ·  kekuatan bukti {bar} {ev['kekuatan']}/4"]
        for it in ev["items"][:3]:
            who = f"{it['penerbit']} ({it['tingkat_label']})" + (f", {_date(it['tanggal'])}" if it.get("tanggal") else "")
            quote = it["kutipan"] if len(it["kutipan"]) <= 220 else it["kutipan"][:217].rsplit(" ", 1)[0] + "…"
            head = f'<a href="{escape(it["url"])}">{e(who)}</a>' if html else f"{who}: {it['url']}"
            lines.append(f"  • {head}\n    “{e(quote)}”")
        lines.append("  " + e(ev["alasan"]))
        lines.append("  Kutipan disalin langsung dari halaman oleh kode; AI hanya menilai hubungannya.")
    items = (result.get("reading") or {}).get("items", [])[:3]
    if items:
        lines += ["", "📖 " + b("Bahan bacaan") + " (tautan sudah dibuka dan bisa diakses)"]
        for it in items:
            if html:
                lines.append(f'  • <a href="{escape(it["url"])}">{e(it["title"][:70])}</a> ({e(it["kind_label"])})')
            else:
                lines.append(f"  • {it['title'][:70]} ({it['kind_label']}): {it['url']}")
        lines.append("  Bacaan ini pelengkap, bukan dasar vonis.")
    lines += ["", "👉 " + b("Sebaiknya") + ": " + e(ACTION_BY_REASON.get(result.get("reason", ""), ACTION[status]))]
    if result["offer_human_review"]:
        lines.append("Tekan 🙋 di bawah untuk bertanya ke pemeriksa manusia.")
    lines += ["", f"<code>{e(version_line())}</code>" if html else version_line()]
    return "\n".join(lines)

"""Plain-language chat reply shared by all channels."""

from __future__ import annotations

from html import escape

ICON = {
    "terbukti_salah": "🔴",
    "sejalan_dengan_sumber": "🟢",
    "tidak_yakin": "🟠",
    "belum_ada_pemeriksaan": "⚪",
}

REASON = {
    "tidak_ada_bantahan": "Belum ada pemeriksa fakta yang membahas kabar ini.",
    "mirip_tapi_tidak_sama": "Topiknya mirip dengan kabar yang pernah dicek, tetapi isinya tidak sama persis.",
    "inti_klaim_tidak_ada": "Topiknya mirip dengan kabar yang pernah dicek, tetapi inti klaimnya berbeda.",
    "bukan_klaim_faktual": "Isinya lebih mirip pendapat atau salam, bukan kabar yang bisa dicek.",
    "tampak_meluruskan": "Pesan ini tampaknya justru meluruskan kabar bohong.",
    "bukti_bertentangan": "Sumber-sumber yang ditemukan saling bertentangan.",
    "tidak_ada_kutipan_terverifikasi": "Sumber dari pencarian web tidak bisa dibuktikan isinya.",
    "memerlukan_verifikasi_ai": "Ini informasi resmi, tetapi buktinya belum cukup untuk dinyatakan sejalan.",
}
ACTION = {
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
    if m:
        steps.append(f"Dicocokkan dengan bantahan terverifikasi: cocok ({round(m['score'] * 100)}%)")
    else:
        steps.append("Dicocokkan dengan bantahan terverifikasi: tidak ada yang cukup mirip")
    if "gemini_search" in (result.get("method") or ""):
        n = result.get("llm") or {}
        steps.append(f"AI mencari di web: {n.get('sumber_ditemukan', 0)} sumber, {n.get('sumber_terverifikasi', 0)} lolos dicek ulang oleh kode")
    for c in (result.get("links") or {}).get("checked", [])[:2]:
        steps.append(f"Tautan {c['host']}: " + ("terbuka" if c["state"] == "terbuka" else (c["note"] or c["state"])))
    return steps


def reply_text(result: dict, html: bool = False) -> str:
    # In HTML mode every dynamic string is escaped: the sapaan and link hosts come from the user,
    # and a stray "<" makes Telegram reject the whole message.
    from .. import version_line

    e = (lambda s: escape(str(s), quote=False)) if html else str
    b = (lambda s: f"<b>{e(s)}</b>") if html else (lambda s: f"*{s}*")
    status = result["status"]
    lines = [f"{ICON[status]} {b(result['status_label'].upper())}", ""]
    match = result.get("match")
    lines.append(e(match["sederhana"]) if match else e(result["voice_script"]))
    reason = REASON.get(result.get("reason", ""))
    if reason and not match:
        lines += ["", f"📌 {e(reason)}"]
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
    lines += ["", "👉 " + b("Sebaiknya") + ": " + e(ACTION[status])]
    if result["offer_human_review"]:
        lines.append("Tekan 🙋 di bawah untuk bertanya ke pemeriksa manusia.")
    lines += ["", f"<code>{e(version_line())}</code>" if html else version_line()]
    return "\n".join(lines)

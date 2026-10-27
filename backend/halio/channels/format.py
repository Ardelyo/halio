"""Plain-language chat reply shared by all channels."""

from __future__ import annotations

import html as _html

ICON = {"terbukti_salah": "🔴", "tidak_yakin": "🟠", "belum_ada_pemeriksaan": "⚪"}


def reply_text(result: dict, html: bool = False) -> str:
    # Telegram rejects the whole message if HTML mode text contains a stray "<" or "&".
    e = _html.escape if html else (lambda s: s)
    b = (lambda s: f"<b>{e(s)}</b>") if html else (lambda s: f"*{s}*")
    lines = [f"{ICON[result['status']]} {b(result['status_label'])}", ""]
    match = result.get("match")
    if match:
        lines.append(e(match["sederhana"]))
        src = match["sumber"][0]
        link = f'<a href="{e(src["url"])}">{e(src["nama"])}</a>' if html else f"{src['nama']}\n{src['url']}"
        lines += ["", f"Sumber: {link}"]
    else:
        lines.append(e(result["voice_script"]))
    techs = result["manipulation"]["techniques"]
    if techs:
        lines += ["", "⚠️ Trik dalam pesan ini: " + ", ".join(e(t["label"].lower()) for t in techs[:3])]
    for w in result["links"]["warnings"][:2]:
        lines.append(f"🔗 {e(w)}")
    if result["offer_human_review"]:
        lines += ["", "Mau ditanyakan ke pemeriksa manusia? Tekan tombol di bawah."]
    return "\n".join(lines)

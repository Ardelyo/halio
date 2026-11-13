"""Reverse image search with Cloud Vision WEB_DETECTION: which public pages carry the same (or a near-identical) picture.

Turns on by itself once the Cloud Vision API is enabled in the project; until then it reports itself as inactive (a blind
spot in the report), never as "no matches". It finds where a picture appeared, not whether it is real.
"""

from __future__ import annotations

import base64
import logging

import httpx

from ..config import Settings

log = logging.getLogger(__name__)
ENDPOINT = "https://vision.googleapis.com/v1/images:annotate"


def _token() -> str:
    import google.auth
    from google.auth.transport.requests import Request

    # tarik token ADC lokal/server buat autentikasi ke Cloud Vision API
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def web_detection(data: bytes, cfg: Settings, token=_token, transport: httpx.BaseTransport | None = None) -> dict:
    """{aktif, galat, label, entitas, sama, mirip, hits}. 'hits' are candidate pages for the shared pool."""
    out = {"aktif": False, "galat": "", "label": [], "entitas": [], "sama": 0, "mirip": 0, "hits": []}
    try:
        with httpx.Client(timeout=20, transport=transport) as client:
            resp = client.post(ENDPOINT, headers={"Authorization": f"Bearer {token()}", "x-goog-user-project": cfg.google_cloud_project},
                               json={"requests": [{"image": {"content": base64.b64encode(data).decode()},
                                                   "features": [{"type": "WEB_DETECTION", "maxResults": 40}]}]})
    except Exception as exc:  # kredensial blm ada atau koneksi jaringan putus
        out["galat"] = f"tidak_tersedia ({type(exc).__name__})"
        return out
    # kl Vision API blm dinyalain di proyek GCP, jujur laporin sbg titik buta jgn dianggap "0 kecocokan"
    if resp.status_code in (403, 404):
        out["galat"] = "Cloud Vision API belum diaktifkan di proyek ini"
        return out
    if resp.status_code != 200:
        out["galat"] = f"http_{resp.status_code}"
        return out
    web = (resp.json().get("responses") or [{}])[0].get("webDetection") or {}
    out["aktif"] = True
    out["label"] = [x.get("label", "") for x in web.get("bestGuessLabels", []) if x.get("label")][:3]
    out["entitas"] = [x["description"] for x in web.get("webEntities", []) if x.get("description")][:8]
    # masukin halaman publik yg muat gambar persis sama atau mirip ke kolam kandidat bareng
    for page in web.get("pagesWithMatchingImages", [])[:30]:
        url = page.get("url", "")
        if not url.startswith("https://"):
            continue
        full = bool(page.get("fullMatchingImages"))
        out["sama" if full else "mirip"] += 1
        # bersihin sisa tag <b> bawaan snippet judul dr Vision API
        title = page.get("pageTitle", "").replace("<b>", "").replace("</b>", "")
        out["hits"].append({"uri": url, "title": title, "via": "gambar", "gambar_sama": full})
    return out

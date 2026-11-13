"""API and store tests: check flow, card, Radar aggregation, k-anonymity, small-cell suppression, review tickets."""

import os
import tempfile

import pytest

# arahin db ke folder sementra dulu sblm import app biar ga nyentuh db lokal
os.environ["HALIO_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ.pop("GOOGLE_FACTCHECK_API_KEY", None)
os.environ.pop("HALIO_LLM", None)
os.environ.pop("RADAR_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

from halio import api as api_module  # noqa: E402
from halio.api import app  # noqa: E402
from halio.store import Store  # noqa: E402

client = TestClient(app)


def test_check_card_and_radar_flow():
    # tes alur utma: cek klaim -> render kartu PNG -> cek hitungan di radar ikut naik
    r = client.post("/api/check", json={"text": "Waspada gempa besar diprediksi minggu depan, sebarkan!", "channel": "demo"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "terbukti_salah"

    card = client.get(body["card_url"])
    assert card.status_code == 200 and card.content[:8] == b"\x89PNG\r\n\x1a\n"

    radar = client.get("/api/radar").json()
    assert radar["total_checks"] >= 1
    assert "emerging_rumours" in radar


def test_expired_check_returns_404():
    assert client.get("/api/card/doesnotexist.png").status_code == 404


def test_escalate_and_appeal():
    body = client.post("/api/check", json={"text": "Bank akan memblokir rekening tidak aktif mulai Januari"}).json()
    assert client.post("/api/escalate", json={"check_id": body["id"]}).json()["ok"]
    assert client.post("/api/appeal", json={"check_id": body["id"], "reason": "test"}).json()["ok"]


def test_review_web_response_is_recorded_without_fake_delivery():
    ticket = api_module.store.add_escalation("b" * 32, "Klaim web", "web", "web:test")
    response = client.post(f"/api/review/escalations/{ticket}/resolve", json={"response": "Jawaban analis", "send": False})
    assert response.status_code == 200
    assert response.json()["recorded"] and not response.json()["sent"]
    queue = client.get("/api/review/escalations?open_only=false").json()
    item = next(item for item in queue["items"] if item["id"] == ticket)
    assert item["status"] == "selesai"
    assert queue["events"][0]["response"] == "Jawaban analis"
    assert client.post(f"/api/review/escalations/{ticket}/resolve", json={"response": "Ulangi"}).status_code == 409


def test_failed_delivery_keeps_review_open(monkeypatch):
    # kl gagal dikrim balik ke Telegram, tiket eskalasinya jgn ditutup biar analis bisa kirim ulang
    ticket = api_module.store.add_escalation("c" * 32, "Klaim Telegram", "telegram", "tg:123")
    monkeypatch.setattr(api_module.review, "send_reply", lambda *_: (_ for _ in ()).throw(RuntimeError("Telegram menolak balasan")))
    response = client.post(f"/api/review/escalations/{ticket}/resolve", json={"response": "Jawaban analis"})
    assert response.status_code == 502
    assert response.json()["detail"] == "Telegram menolak balasan"
    items = api_module.store.review_items("escalations", open_only=False)
    assert next(item for item in items if item["id"] == ticket)["status"] == "menunggu"


def test_review_input_validation():
    assert client.get("/api/review/unknown").status_code == 404
    assert client.post("/api/review/appeals/0/resolve", json={"response": "Jawaban"}).status_code == 422
    assert client.post("/api/review/appeals/1/resolve", json={"response": " "}).status_code == 422
    assert client.post("/api/review/appeals/1/resolve", json={"response": "x" * 2001}).status_code == 422


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "k.db", k_anonymity=3)


def _unknown(claim):
    return {"status": "belum_ada_pemeriksaan", "claim": claim, "match": None, "manipulation": {"techniques": []}}


def test_rumour_text_hidden_until_k_distinct_reporters(store):
    claim = "Jembatan Suramadu akan ditutup total selama seminggu"
    for _ in range(5):
        store.record(_unknown(claim), "telegram", "tg:1")  # satu orang yg sama lapor berulang2 tetep diitung 1
    assert store.radar()["emerging_rumours"] == []
    assert store.radar()["rumours_below_k"] == 1

    store.record(_unknown(claim), "telegram", "tg:2")
    store.record(_unknown(claim), "telegram", "tg:3")
    emerging = store.radar()["emerging_rumours"]
    assert len(emerging) == 1 and emerging[0]["text"] == claim and emerging[0]["count"] == 3


def test_small_cells_are_suppressed(store):
    # angka di bawah ambang k-anonymity disembunyiin jadi "<3" biar aman privasinya
    store.record({"status": "terbukti_salah", "claim": "x", "match": {"debunk_id": "a", "kategori": "kesehatan"},
                  "manipulation": {"techniques": []}}, "web", None)
    assert store.radar()["by_kategori"][0]["n"] == "<3"


def test_store_retention_days_is_configurable(tmp_path):
    import sqlite3

    from halio.store import Store

    s = Store(tmp_path / "r.db", retention_days=3)
    with sqlite3.connect(tmp_path / "r.db") as c:
        c.execute("INSERT INTO appeals (created, check_id, status) VALUES ('2000-01-01T00:00:00+07:00','x','baru')")
    s.prune()
    assert sqlite3.connect(tmp_path / "r.db").execute("SELECT COUNT(*) FROM appeals").fetchone()[0] == 0


def test_radar_reports_seeded_demo_rows_and_the_page_labels_them(tmp_path):
    """Seeded rows (channel 'demo') are counted, and radar.js shows a banner for them; real rows alone do not."""
    from pathlib import Path

    from halio.store import Store

    s = Store(tmp_path / "d.db", k_anonymity=2)
    real = {"status": "belum_ada_pemeriksaan", "manipulation": {"techniques": []}, "reason": "x"}
    s.record(real, "web", None)
    assert s.radar(7)["demo_events"] == 0
    s.record(real, "demo", None)
    assert s.radar(7)["demo_events"] == 1

    web = Path(__file__).resolve().parents[2] / "web"
    js, page = (web / "radar.js").read_text(encoding="utf-8"), (web / "radar.html").read_text(encoding="utf-8")
    assert 'id="seed-notice"' in page and "radar.demo_events" in js and '"#seed-notice"' in js


def test_radar_categories_count_only_proven_false_checks(store):
    """A true message that merely resembles the TNI recruitment hoax (status 'tidak_yakin') is not 'Penipuan mencatut TNI'."""
    tni = {"debunk_id": "rekrutmen-tni-ad-berbayar", "kategori": "penipuan_catut_tni"}
    for _ in range(3):
        store.record({"status": "tidak_yakin", "reason": "inti_klaim_tidak_ada", "claim": "x", "match": tni,
                      "manipulation": {"techniques": []}}, "web", None)
    radar = store.radar()
    assert radar["by_kategori"] == [] and radar["top_debunks"] == []
    assert radar["by_status"]["tidak_yakin"] == 3
    for _ in range(3):
        store.record({"status": "terbukti_salah", "claim": "x", "match": tni, "manipulation": {"techniques": []}}, "web", None)
    radar = store.radar()
    assert radar["by_kategori"] == [{"kategori": "penipuan_catut_tni", "n": 3}]
    assert radar["top_debunks"][0]["debunk_id"] == "rekrutmen-tni-ad-berbayar"


def _tni_check(store, day, n):
    for _ in range(n):
        store.record({"status": "terbukti_salah", "claim": "x", "match": {"debunk_id": "rekrutmen-tni-ad-berbayar", "kategori": "penipuan_catut_tni"},
                      "manipulation": {"techniques": []}}, "demo", None, day=day)


def test_radar_flags_a_spike_in_scams_that_use_the_army_name(store):
    from datetime import date, timedelta

    base = date.fromisoformat(__import__("halio.store", fromlist=["today"]).today())
    for back in range(1, 7):                      # seminggu adem: cuma 1 laporan per hari
        _tni_check(store, (base - timedelta(days=back)).isoformat(), 1)
    quiet = store.radar(7)["catut_tni"]
    assert quiet["status"] == "tenang" and len(quiet["harian"]) == 7

    _tni_check(store, base.isoformat(), 9)         # hari ini tembus 9 laporan dibanding rata2 1 sehari sebelumnya
    spike = store.radar(7)["catut_tni"]
    assert spike["status"] == "naik" and spike["hari_ini"] == 9 and spike["rata_rata_sebelumnya"] == 1.0
    assert spike["harian"][-1] == {"day": base.isoformat(), "n": 9}


def test_tni_spike_needs_enough_checks_to_mean_anything(store):
    from datetime import date

    today = __import__("halio.store", fromlist=["today"]).today()
    _tni_check(store, today, 2)                    # cuma 2 laporan dr nol: msh di bawah batas sel kecil, belum diitung lonjakan
    r = store.radar(7)["catut_tni"]
    assert r["status"] == "tenang" and r["hari_ini"] == "<3"

import os
import tempfile

import pytest

os.environ["HALIO_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ.pop("GOOGLE_FACTCHECK_API_KEY", None)
os.environ.pop("HALIO_LLM", None)
os.environ.pop("RADAR_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

from halio.api import app  # noqa: E402
from halio.store import Store  # noqa: E402

client = TestClient(app)


def test_check_card_and_radar_flow():
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


@pytest.fixture
def store(tmp_path):
    return Store(tmp_path / "k.db", k_anonymity=3)


def _unknown(claim):
    return {"status": "belum_ada_pemeriksaan", "claim": claim, "match": None, "manipulation": {"techniques": []}}


def test_rumour_text_hidden_until_k_distinct_reporters(store):
    claim = "Jembatan Suramadu akan ditutup total selama seminggu"
    for _ in range(5):
        store.record(_unknown(claim), "telegram", "tg:1")  # same person repeatedly
    assert store.radar()["emerging_rumours"] == []
    assert store.radar()["rumours_below_k"] == 1

    store.record(_unknown(claim), "telegram", "tg:2")
    store.record(_unknown(claim), "telegram", "tg:3")
    emerging = store.radar()["emerging_rumours"]
    assert len(emerging) == 1 and emerging[0]["text"] == claim and emerging[0]["count"] == 3


def test_small_cells_are_suppressed(store):
    store.record({"status": "terbukti_salah", "claim": "x", "match": {"debunk_id": "a", "kategori": "kesehatan"},
                  "manipulation": {"techniques": []}}, "web", None)
    assert store.radar()["by_kategori"][0]["n"] == "<3"

import hashlib
import hmac

from fastapi.testclient import TestClient

from halio.api import app
from halio.factcheck_api import is_false_rating
from halio.security import RateLimiter, valid_meta_signature
from halio.store import Store

client = TestClient(app)


def test_meta_signature_requires_secret_and_exact_raw_body():
    body = b'{"entry":[]}'
    signature = "sha256=" + hmac.new(b"secret", body, hashlib.sha256).hexdigest()
    assert valid_meta_signature(body, signature, "secret")
    assert not valid_meta_signature(body + b" ", signature, "secret")
    assert not valid_meta_signature(body, signature, None)
    assert not valid_meta_signature(body, None, "secret")


def test_whatsapp_webhook_rejects_missing_signature():
    assert client.post("/webhook/whatsapp", json={"entry": []}).status_code == 403


def test_rate_limiter_is_bounded_per_key():
    limiter = RateLimiter(2)
    assert limiter.allow("a", now=1)
    assert limiter.allow("a", now=2)
    assert not limiter.allow("a", now=3)
    assert limiter.allow("b", now=3)
    assert limiter.allow("a", now=62)


def test_appeal_rejects_unknown_or_expired_check():
    response = client.post("/api/appeal", json={"check_id": "0" * 32, "reason": "salah"})
    assert response.status_code == 404


def test_public_result_does_not_include_delivery_metadata():
    body = client.post("/api/check", json={"text": "Jembatan Suramadu ditutup besok", "reporter": "web:test"}).json()
    fetched = client.get("/api/check/" + body["id"]).json()
    assert "_reporter" not in fetched and "_channel" not in fetched


def test_reviewer_workflow_tracks_origin_and_resolution(tmp_path):
    store = Store(tmp_path / "review.db")
    ticket = store.add_escalation("a" * 32, "Klaim", "telegram", "tg:123")
    item = store.review_items("escalations")[0]
    assert item["id"] == ticket and item["reporter"] == "tg:123"
    resolved = store.resolve_review("escalations", ticket, "Sudah diperiksa")
    assert resolved["claim"] == "Klaim"
    assert store.review_items("escalations") == []


def test_factcheck_rating_does_not_invert_negated_false_labels():
    assert is_false_rating("Salah")
    assert is_false_rating("Mostly false")
    assert not is_false_rating("Tidak salah")
    assert not is_false_rating("Not false")
    assert not is_false_rating(None)

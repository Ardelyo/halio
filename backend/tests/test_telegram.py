"""Telegram bot: the user is always answered, captions match the verdict, the poll loop never spins."""

import pytest

from halio.channels import telegram as t


class FakeResp:
    def __init__(self, status=200, data=None, content=b"x"):
        self.status_code, self._data, self.content = status, data, content

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise t.httpx.HTTPStatusError("boom", request=None, response=self)


@pytest.fixture
def sent(monkeypatch):
    calls = []
    monkeypatch.setattr(t, "tg", lambda method, **kw: calls.append((method, kw)) or {"ok": True})
    return calls


def texts(calls):
    return [(kw.get("json") or kw.get("data") or {}).get("text") or (kw.get("data") or {}).get("caption") for m, kw in calls]


def result(status="belum_ada_pemeriksaan"):
    return {"id": "a" * 32, "status": status, "status_label": status, "reason": "x", "claim": "c",
            "match": None, "manipulation": {"techniques": []}, "links": {"warnings": []},
            "voice_script": "Halo", "offer_human_review": True, "card_url": "/c.png", "voice_url": "/v.mp3"}


def test_api_down_still_answers_the_user(monkeypatch, sent):
    def down(*a, **k):
        raise t.httpx.ConnectError("refused")

    monkeypatch.setattr(t.httpx, "post", down)
    t.handle_message({"chat": {"id": 1}, "text": "Jembatan ditutup total besok pagi"})
    assert t.BUSY in texts(sent)


def test_rate_limit_gets_a_human_message(monkeypatch, sent):
    monkeypatch.setattr(t.httpx, "post", lambda *a, **k: FakeResp(429))
    t.handle_message({"chat": {"id": 1}, "text": "Jembatan ditutup total besok pagi"})
    assert any("Tunggu sebentar" in (x or "") for x in texts(sent))


@pytest.mark.parametrize("status", list(t.CARD_CAPTION))
def test_card_caption_matches_the_verdict(monkeypatch, sent, status):
    monkeypatch.setattr(t.httpx, "post", lambda *a, **k: FakeResp(200, result(status)))
    monkeypatch.setattr(t.httpx, "get", lambda *a, **k: FakeResp(200))
    t.handle_message({"chat": {"id": 1}, "text": "Jembatan ditutup total besok pagi"})
    assert t.CARD_CAPTION[status] in texts(sent)
    if status != "terbukti_salah":
        assert "meluruskan" not in t.CARD_CAPTION[status]


def test_card_failure_does_not_lose_the_text_answer(monkeypatch, sent):
    monkeypatch.setattr(t.httpx, "post", lambda *a, **k: FakeResp(200, result()))

    def broken(*a, **k):
        raise t.httpx.ReadTimeout("slow")

    monkeypatch.setattr(t.httpx, "get", broken)
    t.handle_message({"chat": {"id": 1}, "text": "Jembatan ditutup total besok pagi"})
    methods = [m for m, _ in sent]
    assert "sendMessage" in methods and "sendPhoto" not in methods


def test_bad_token_stops_with_a_clear_message(monkeypatch):
    monkeypatch.setattr(t.httpx, "get", lambda *a, **k: FakeResp(200, {"ok": False, "description": "Unauthorized"}))
    with pytest.raises(SystemExit, match="Token Telegram ditolak"):
        t.startup_checks()


def test_rejected_getupdates_sleeps_instead_of_spinning(monkeypatch):
    monkeypatch.setattr(t, "TOKEN", "123:abc")
    monkeypatch.setattr(t, "startup_checks", lambda: None)
    monkeypatch.setattr(t.httpx, "get", lambda *a, **k: FakeResp(200, {"ok": False, "description": "Conflict"}))
    slept = []

    def fake_sleep(sec):
        slept.append(sec)
        if len(slept) >= 2:
            raise KeyboardInterrupt

    monkeypatch.setattr(t.time, "sleep", fake_sleep)
    with pytest.raises(KeyboardInterrupt):
        t.main()
    assert slept == [5, 5]


def test_unexpected_error_in_one_update_apologises_and_continues(monkeypatch, sent):
    monkeypatch.setattr(t, "TOKEN", "123:abc")
    monkeypatch.setattr(t, "startup_checks", lambda: None)
    batches = iter([
        {"ok": True, "result": [{"update_id": 1, "message": {"chat": {"id": 9}, "text": "halo dunia"}}]},
        None,
    ])

    def get(*a, **k):
        data = next(batches)
        if data is None:
            raise KeyboardInterrupt
        return FakeResp(200, data)

    monkeypatch.setattr(t.httpx, "get", get)
    monkeypatch.setattr(t, "handle_message", lambda m: 1 / 0)
    with pytest.raises(KeyboardInterrupt):
        t.main()
    assert t.BUSY in texts(sent)

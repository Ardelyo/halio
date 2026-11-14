"""Rantai cadangan model: Vertex -> key Gemini API -> ON Token (semua dimock, ga ada panggilan jaringan)."""

from dataclasses import replace

import pytest

from halio import evidence, llmchain
from halio.config import Settings

CFG = replace(Settings(), gemini_api_key="g-key", ontoken_api_key="o-key")
PASSAGES = [evidence.Passage(id=1, text="Kemenkeu menyatakan tidak ada bansos tunai lewat WhatsApp.", url="https://kemenkeu.go.id/a",
                             host="kemenkeu.go.id", publisher="Kemenkeu", tier="A", published=None, group="g1")]


@pytest.fixture
def needs_genai():
    # CI tidak memasang google-genai (dependensi opsional); tes yg butuh SDK-nya dilewati di sana
    pytest.importorskip("google.genai")


@pytest.fixture(autouse=True)
def _fresh():
    llmchain.reset()
    yield
    llmchain.reset()


def _fake_client(monkeypatch, behaviour):
    """behaviour: {'vertex': exc|value, 'gemini_key': exc|value}. Client dibedakan dari argumennya."""
    from google import genai

    calls = []

    class Fake:
        def __init__(self, name):
            self.name = name

    def make(*args, **kwargs):
        return Fake("vertex" if kwargs.get("vertexai") else "gemini_key")

    monkeypatch.setattr(genai, "Client", make)
    return calls, behaviour


def _call(behaviour, calls):
    def run(client):
        calls.append(client.name)
        out = behaviour[client.name]
        if isinstance(out, Exception):
            raise out
        return out
    return run


def test_vertex_ok_does_not_touch_backup(needs_genai, monkeypatch):
    calls, b = _fake_client(monkeypatch, {"vertex": "V", "gemini_key": "K"})
    assert llmchain.run_genai(CFG, _call(b, calls), "t") == "V"
    assert calls == ["vertex"]


def test_vertex_rejected_falls_back_to_key_then_rests_vertex(needs_genai, monkeypatch):
    calls, b = _fake_client(monkeypatch, {"vertex": PermissionError("403"), "gemini_key": "K"})
    assert llmchain.run_genai(CFG, _call(b, calls), "t") == "K"
    assert calls == ["vertex", "gemini_key"]
    calls.clear()
    assert llmchain.run_genai(CFG, _call(b, calls), "t") == "K"   # Vertex lagi diistirahatkan, langsung ke key
    assert calls == ["gemini_key"]


def test_no_backup_key_raises_original_error(needs_genai, monkeypatch):
    calls, b = _fake_client(monkeypatch, {"vertex": PermissionError("403"), "gemini_key": "K"})
    with pytest.raises(PermissionError):
        llmchain.run_genai(replace(CFG, gemini_api_key=None), _call(b, calls), "t")
    assert calls == ["vertex"]


def test_judge_falls_to_ontoken_when_both_gemini_fail(needs_genai, monkeypatch):
    def boom(*a, **k):
        raise PermissionError("403")

    monkeypatch.setattr(llmchain, "run_genai", boom)
    seen = {}

    def fake_ont(cfg, system, user, max_tokens=1500):
        seen["user"] = user
        return {"penilaian": [{"id": 1, "relation": "refutes", "covers_all": True}]}

    monkeypatch.setattr(llmchain, "ontoken_json", fake_ont)
    out = evidence.gemini_judge("bansos tunai lewat WA", PASSAGES, CFG)
    assert [(j.id, j.relation, j.covers_all) for j in out] == [(1, "refutes", True)]
    assert "<klaim>bansos tunai lewat WA</klaim>" in seen["user"]


def test_judge_raises_when_no_ontoken_key(needs_genai, monkeypatch):
    def boom(*a, **k):
        raise PermissionError("403")

    monkeypatch.setattr(llmchain, "run_genai", boom)
    with pytest.raises(PermissionError):
        evidence.gemini_judge("x", PASSAGES, replace(CFG, ontoken_api_key=None))


def test_ontoken_json_parses_fenced_json_and_sends_key(monkeypatch):
    sent = {}

    class R:
        def raise_for_status(self): pass
        def json(self): return {"choices": [{"message": {"content": '```json\n{"a": 1}\n```'}}]}

    def post(url, headers, json, timeout):
        sent.update(url=url, auth=headers["Authorization"], model=json["model"])
        return R()

    monkeypatch.setattr(llmchain.httpx, "post", post)
    assert llmchain.ontoken_json(CFG, "s", "u") == {"a": 1}
    assert sent == {"url": "https://api.ontoken.id/v1/chat/completions", "auth": "Bearer o-key", "model": "deepseek-v4.1-flash"}


def test_ontoken_without_key_is_a_clear_error():
    with pytest.raises(RuntimeError):
        llmchain.ontoken_json(replace(CFG, ontoken_api_key=None), "s", "u")


def test_discover_uses_alternative_search_when_gemini_search_dies(needs_genai, monkeypatch):
    def boom(*a, **k):
        raise PermissionError("403")

    monkeypatch.setattr(llmchain, "run_genai", boom)
    monkeypatch.setattr(llmchain, "web_search", lambda cfg, claim: ([{"uri": "https://turnbackhoax.id/x", "title": "t"}], ["q"]))
    assert evidence.gemini_discover("klaim", CFG) == ([{"uri": "https://turnbackhoax.id/x", "title": "t"}], ["q"])


def test_web_search_prefers_tavily_then_serper(monkeypatch):
    cfg = replace(CFG, tavily_api_key="t", serper_api_key="s")
    monkeypatch.setattr(llmchain, "_search_tavily", lambda c, q: (_ for _ in ()).throw(RuntimeError("429")))
    monkeypatch.setattr(llmchain, "_search_serper", lambda c, q: [{"uri": "https://a.go.id/1", "title": ""}])
    monkeypatch.setattr(llmchain, "_search_ddg", lambda c, q: pytest.fail("ddg tidak boleh dipakai"))
    found, queries = llmchain.web_search(cfg, "BBM naik")
    assert found[0]["uri"] == "https://a.go.id/1" and "hoaks cek fakta" in queries[0]


def test_web_search_raises_when_everything_fails(monkeypatch):
    monkeypatch.setattr(llmchain, "_search_ddg", lambda c, q: [])
    with pytest.raises(RuntimeError):
        llmchain.web_search(CFG, "x")


def test_web_search_prefers_mughu_and_falls_back_to_tavily(monkeypatch):
    cfg = replace(CFG, mughu_api_key="m", tavily_api_key="t")
    monkeypatch.setattr(llmchain, "_search_mughu", lambda c, q: (_ for _ in ()).throw(RuntimeError("mughu_quota_exceeded")))
    monkeypatch.setattr(llmchain, "_search_tavily", lambda c, q: [{"uri": "https://kompas.com/cekfakta/1", "title": ""}])
    found, _ = llmchain.web_search(cfg, "bantuan beras")
    assert found[0]["uri"] == "https://kompas.com/cekfakta/1"
    # kuota habis => Mughu diistirahatkan lama, request berikutnya langsung ke Tavily tanpa memanggil Mughu lagi
    monkeypatch.setattr(llmchain, "_search_mughu", lambda c, q: pytest.fail("mughu masih diistirahatkan"))
    assert llmchain.web_search(cfg, "x")[0][0]["uri"].startswith("https://kompas.com")


def test_mughu_parses_results_and_sends_key(monkeypatch):
    seen = {}

    class R:
        def raise_for_status(self): pass
        def json(self): return {"ok": True, "results": [{"url": "https://komdigi.go.id/a", "title": "[HOAKS] x"}, {"title": "tanpa url"}]}

    def get(url, params, headers, timeout):
        seen.update(url=url, q=params["q"], key=headers["x-api-key"])
        return R()

    monkeypatch.setattr(llmchain.httpx, "get", get)
    out = llmchain._search_mughu(replace(CFG, mughu_api_key="m-key"), "klaim")
    assert out == [{"uri": "https://komdigi.go.id/a", "title": "[HOAKS] x"}]
    assert seen == {"url": "https://mughu.id/api/v1/web-search-api", "q": "klaim", "key": "m-key"}

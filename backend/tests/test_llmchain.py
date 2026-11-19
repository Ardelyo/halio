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
    def run(client, model=None):
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
        llmchain.run_genai(replace(CFG, gemini_api_key=None, llm_fallback_models=()), _call(b, calls), "t")
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
    monkeypatch.setattr(llmchain, "_search_claude", lambda c, q: [])
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


def test_web_search_merges_two_providers_interleaved_and_dedupes(monkeypatch):
    cfg = replace(CFG, mughu_api_key="m", tavily_api_key="t")
    monkeypatch.setattr(llmchain, "_search_mughu", lambda c, q: [{"uri": "https://a.go.id/1", "title": ""}, {"uri": "https://b.go.id/2", "title": ""}])
    monkeypatch.setattr(llmchain, "_search_tavily", lambda c, q: [{"uri": "https://c.id/3", "title": ""}, {"uri": "https://a.go.id/1/", "title": ""}])
    monkeypatch.setattr(llmchain, "_search_ddg", lambda c, q: pytest.fail("ddg tidak dipakai kalau sudah ada hasil"))
    found, _ = llmchain.web_search(cfg, "klaim")
    assert [x["uri"] for x in found] == ["https://a.go.id/1", "https://c.id/3", "https://b.go.id/2"]


def test_claude_search_parses_urls_and_uses_anthropic_endpoint(monkeypatch):
    seen = {}

    class R:
        def raise_for_status(self): pass
        def json(self): return {"content": [
            {"type": "thinking"}, {"type": "server_tool_use", "input": {"query": "q"}},
            {"type": "web_search_tool_result", "content": [
                {"type": "web_search_result", "url": "https://turnbackhoax.id/a", "title": "[HOAKS] a"},
                {"type": "web_search_result", "title": "tanpa url"}]},
            {"type": "text", "text": "ok"}]}

    def post(url, headers, json, timeout):
        seen.update(url=url, key=headers["x-api-key"], model=json["model"], tool=json["tools"][0]["type"])
        return R()

    monkeypatch.setattr(llmchain.httpx, "post", post)
    out = llmchain._search_claude(CFG, "klaim")
    assert out == [{"uri": "https://turnbackhoax.id/a", "title": "[HOAKS] a"}]
    assert seen == {"url": "https://api.ontoken.id/v1/messages", "key": "o-key", "model": "claude-haiku-5.5", "tool": "web_search_20250305"}


def test_claude_search_is_last_resort_only(monkeypatch):
    cfg = replace(CFG, mughu_api_key="m")
    monkeypatch.setattr(llmchain, "_search_mughu", lambda c, q: [{"uri": "https://a.go.id/1", "title": ""}])
    monkeypatch.setattr(llmchain, "_search_claude", lambda c, q: pytest.fail("Claude berbayar tidak boleh dipakai bila Mughu berhasil"))
    assert llmchain.web_search(cfg, "x")[0][0]["uri"] == "https://a.go.id/1"
    # semua mesin gratis gagal -> baru Claude
    llmchain.reset()
    monkeypatch.setattr(llmchain, "_search_mughu", lambda c, q: (_ for _ in ()).throw(RuntimeError("mughu_quota")))
    monkeypatch.setattr(llmchain, "_search_claude", lambda c, q: [{"uri": "https://infopublik.id/z", "title": ""}])
    monkeypatch.setattr(llmchain, "_search_ddg", lambda c, q: pytest.fail("ddg setelah Claude berhasil tidak boleh"))
    assert llmchain.web_search(cfg, "x")[0][0]["uri"] == "https://infopublik.id/z"


def test_model_fallback_order_and_thinking(needs_genai, monkeypatch):
    # model utama gagal di semua jalur -> pindah ke model cadangan; MINIMAL jadi LOW buat seri gemini-4
    calls, seen = [], []

    class Fake:
        name = "vertex"

    from google import genai
    monkeypatch.setattr(genai, "Client", lambda *a, **k: Fake())
    cfg = replace(CFG, gemini_api_key=None, llm_model="gemini-4-hydrogen", llm_fallback_models=("gemini-4-neon", "gemini-3.5-flash-lite"))

    def run(client, model):
        seen.append(model)
        if model != "gemini-3.5-flash-lite":
            raise RuntimeError("404")
        return model

    assert llmchain.run_genai(cfg, run, "t") == "gemini-3.5-flash-lite"
    assert seen == ["gemini-4-hydrogen", "gemini-4-neon", "gemini-3.5-flash-lite"]
    seen.clear()
    assert llmchain.run_genai(cfg, run, "t") == "gemini-3.5-flash-lite"   # dua model pertama lagi diistirahatkan
    assert seen == ["gemini-3.5-flash-lite"]
    assert llmchain.thinking("gemini-4-neon", "MINIMAL").thinking_level.value.endswith("LOW")
    assert llmchain.thinking("gemini-3.5-flash-lite", "MINIMAL") is not None
    assert llmchain.model_chain("a", ("a", "b", "")) == ["a", "b"]


def test_discover_empty_grounding_uses_alt_search(needs_genai, monkeypatch):
    class Resp:
        candidates = []

    monkeypatch.setattr(llmchain, "run_genai", lambda *a, **k: Resp())
    monkeypatch.setattr(llmchain, "web_search", lambda cfg, claim: ([{"uri": "https://x.go.id/a", "title": "A"}], ["q"]))
    found, q = evidence.gemini_discover("klaim", CFG)
    assert found and found[0]["uri"] == "https://x.go.id/a"


def test_effort_levels_pick_models_and_chains():
    from halio import investigate

    c = Settings()
    lo, me, hi = c.with_effort("low"), c.with_effort("medium"), c.with_effort("high")
    assert lo.llm_model == "gemini-3.5-flash-lite" and me.llm_model == "gemini-4-hydrogen" and hi.llm_model == "gemini-4-neon"
    for x in (lo, me, hi):   # tiap rantai memuat ketiga model tanpa duplikat
        assert sorted([x.llm_model, *x.llm_fallback_models]) == sorted(["gemini-3.5-flash-lite", "gemini-4-hydrogen", "gemini-4-neon"])
    assert lo.llm_fallback_models[0] == "gemini-4-hydrogen" and hi.llm_fallback_models[0] == "gemini-4-hydrogen"
    assert c.with_effort("aneh").llm_model == "gemini-4-hydrogen"
    assert Settings().llm_model == "gemini-4-hydrogen"   # cek hoaks biasa
    assert investigate.Budget.for_effort("low").pages < investigate.Budget().pages < investigate.Budget.for_effort("high").pages


def test_api_investigate_accepts_effort_only_valid(monkeypatch):
    from fastapi.testclient import TestClient
    from halio import api

    seen = {}

    class J:
        def submit(self, text, reporter, channel, image=None, effort="medium"):
            seen["effort"] = effort
            return "a" * 32

    monkeypatch.setattr(api, "jobs", lambda: J())
    monkeypatch.setattr(api, "settings", replace(api.settings, llm_enabled=True, llm_provider="google"))
    cl = TestClient(api.app)
    r = cl.post("/api/investigate", json={"text": "klaim yang cukup panjang sekali", "effort": "high"})
    assert r.status_code == 202 and seen["effort"] == "high"
    assert cl.post("/api/investigate", json={"text": "klaim yang cukup panjang sekali", "effort": "ultra"}).status_code == 422


def test_discover_tries_next_google_model_before_alt_search(needs_genai, monkeypatch):
    class Chunk:
        class web:
            uri = "https://cekfakta.go.id/a"
            title = "A"

    class Meta:
        web_search_queries = ["q"]
        grounding_chunks = [Chunk]

    class Cand:
        grounding_metadata = Meta

    class Full:
        candidates = [Cand]

    class Empty:
        candidates = []

    order = []

    def fake(cfg, call, label, models=None):
        order.append(models[0])
        return Empty() if models[0] == "gemini-4-neon" else Full()

    monkeypatch.setattr(llmchain, "run_genai", fake)
    monkeypatch.setattr(llmchain, "web_search", lambda *a, **k: (_ for _ in ()).throw(AssertionError("Mughu tidak boleh dipakai")))
    cfg = replace(CFG, llm_model="gemini-4-neon", llm_fallback_models=("gemini-4-hydrogen",))
    found, q = evidence.gemini_discover("klaim", cfg)
    assert order == ["gemini-4-neon", "gemini-4-hydrogen"] and found[0]["uri"].startswith("https://cekfakta")


def test_quota_error_retries_once_then_rests_briefly(needs_genai, monkeypatch):
    from google import genai
    monkeypatch.setattr(genai, "Client", lambda *a, **k: object())
    monkeypatch.setattr(llmchain.time, "sleep", lambda s: None)
    n = {"c": 0}

    def run(client, model):
        n["c"] += 1
        if n["c"] == 1:
            raise RuntimeError("429 RESOURCE_EXHAUSTED")
        return "ok"

    cfg = replace(CFG, gemini_api_key=None, llm_fallback_models=())
    assert llmchain.run_genai(cfg, run, "t") == "ok" and n["c"] == 2

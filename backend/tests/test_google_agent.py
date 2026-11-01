from datetime import date

import httpx
import pytest

from halio import google_agent, pipeline, source_verifier
from halio.config import Settings
from halio.google_agent import Investigation, SourceEvidence
from halio.source_verifier import Verification

QUOTE = "BMKG menyatakan bahwa hingga saat ini belum ada teknologi yang mampu memprediksi gempa secara pasti."
URL = "https://www.bmkg.go.id/siaran-pers/gempa"
CFG = Settings(google_factcheck_key=None, llm_enabled=True, llm_provider="google")


def evidence(relation="supports", url=URL, quote=QUOTE, published=date(2026, 1, 1)):
    return SourceEvidence(
        name="BMKG",
        url=url,
        quote=quote,
        relation=relation,
        published=published,
    )


def report(*sources):
    return Investigation(summary="Ringkasan bukti.", sources=list(sources))


def verified(item, kind="resmi"):
    return Verification(True, "terverifikasi", item, final_url=item.url, source_kind=kind)


def run_agent(sources):
    return google_agent.investigate(
        "BMKG menyatakan gempa belum dapat diprediksi secara pasti",
        CFG,
        request=lambda *args: report(*sources),
        verifier=lambda item: verified(item),
    )


def test_official_verified_supporting_quote_produces_positive_evidence():
    result = run_agent([evidence()])
    assert result.status == "sejalan_dengan_sumber"
    assert result.match.debunk.jenis == "verifikasi_positif"
    assert result.match.debunk.kutipan_sumber == QUOTE
    assert result.note["sumber_terverifikasi"] == 1


def test_verified_refutation_produces_bantahan():
    result = run_agent([evidence(relation="refutes")])
    assert result.status == "terbukti_salah"
    assert result.match.debunk.jenis == "bantahan"


def test_conflicting_verified_sources_fail_closed():
    result = run_agent([evidence(), evidence(relation="refutes", url="https://www.bmkg.go.id/lain")])
    assert result.status == "tidak_yakin"
    assert result.reason == "bukti_bertentangan"


def test_unverified_quote_never_becomes_evidence():
    item = evidence()
    result = google_agent.investigate(
        "Gempa belum dapat diprediksi secara pasti",
        CFG,
        request=lambda *args: report(item),
        verifier=lambda value: Verification(False, "kutipan_tidak_ada_di_halaman", value),
    )
    assert result.status == "tidak_yakin"
    assert result.match is None
    assert result.note["sumber_ditolak"][0]["alasan"] == "kutipan_tidak_ada_di_halaman"


def test_media_support_is_not_enough_for_green():
    item = evidence(url="https://news.example/fakta")
    result = google_agent.investigate(
        "Gempa belum dapat diprediksi secara pasti",
        CFG,
        request=lambda *args: report(item),
        verifier=lambda value: verified(value, kind="media"),
    )
    assert result.status == "tidak_yakin"
    assert result.reason == "sumber_bukan_resmi"


def test_pipeline_rechecks_agent_positive_validity(monkeypatch):
    agent = run_agent([evidence(published=None)])
    monkeypatch.setattr(pipeline.google_agent, "investigate", lambda *args, **kwargs: agent)
    result = pipeline.check("BMKG menyatakan gempa belum dapat diprediksi secara pasti", CFG)
    assert result["status"] == "tidak_yakin"
    assert result["reason"] == "sumber_kedaluwarsa"
    assert "gemini_search" in result["method"]


def test_agent_can_overrule_false_local_match(monkeypatch):
    agent = run_agent([evidence()])
    monkeypatch.setattr(pipeline.google_agent, "investigate", lambda *args, **kwargs: agent)
    result = pipeline.check("BMKG menyatakan belum ada teknologi yang mampu memprediksi gempa secara pasti", CFG)
    assert result["status"] == "sejalan_dengan_sumber"
    assert result["method"] == "lokal+gemini_search"


def test_visible_text_excludes_scripts_and_preserves_quote():
    text = source_verifier.visible_text(f"<html><script>karangan</script><p>{QUOTE}</p><style>x</style></html>")
    assert QUOTE in text
    assert "karangan" not in text


@pytest.mark.parametrize("url", ["http://www.bmkg.go.id/a", "https://localhost/a", "https://127.0.0.1/a", "https://user:pass@bmkg.go.id/a"])
def test_source_url_rejects_non_https_and_private_targets(url):
    with pytest.raises(source_verifier.SourceError):
        source_verifier.ensure_public_url(url)


def test_fetch_and_quote_verification(monkeypatch):
    monkeypatch.setattr(source_verifier, "ensure_public_url", lambda url: None)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, html=f"<main>{QUOTE}</main>"))
    result = source_verifier.verify_source(evidence(), transport=transport)
    assert result.ok
    assert result.source_kind == "resmi"


def test_fabricated_quote_is_rejected_from_real_page_shape(monkeypatch):
    monkeypatch.setattr(source_verifier, "ensure_public_url", lambda url: None)
    transport = httpx.MockTransport(lambda request: httpx.Response(200, html="<main>Isi halaman yang berbeda.</main>"))
    result = source_verifier.verify_source(evidence(), transport=transport)
    assert not result.ok
    assert result.reason == "kutipan_tidak_ada_di_halaman"


def test_agent_can_repair_quote_from_fetched_page():
    item = evidence(quote="Kutipan ringkasan yang tidak persis tetapi cukup panjang untuk diuji.")
    failed = Verification(
        False, "kutipan_tidak_ada_di_halaman", item,
        final_url=item.url, source_kind="resmi", page_text=QUOTE,
    )

    def repair(claim, check, cfg):
        assert check.page_text == QUOTE
        return verified(item)

    result = google_agent.investigate(
        "Gempa belum dapat diprediksi secara pasti",
        CFG,
        request=lambda *args: report(item),
        verifier=lambda value: failed,
        repairer=repair,
    )
    assert result.status == "sejalan_dengan_sumber"
    assert result.note["sumber_terverifikasi"] == 1

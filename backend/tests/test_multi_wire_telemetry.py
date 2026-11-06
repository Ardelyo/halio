"""Several claims in one message, agency copy counted once, and daily counts of why pages were not used."""

import sqlite3
import tempfile
from datetime import date, timedelta
from pathlib import Path

import pytest

from halio import claims, evidence, pipeline
from halio.channels.format import reply_text
from halio.config import Settings
from halio.evidence import Judgement, wire_group
from halio.source_verifier import Page
from halio.store import Store, today

CFG = Settings(google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)

THREE = ("Presiden bagi-bagi bantuan Rp10 juta untuk semua warga, daftar lewat WhatsApp dan bayar biaya admin. "
         "Pemerintah menaikkan tarif listrik rumah tangga mulai Desember 2026. "
         "Gempa M9 akan terjadi minggu depan di Jawa, menurut BMKG. Sebarkan ke semua grup!")


# ---- splitting --------------------------------------------------------------------------------------------------

def test_a_message_with_three_claims_becomes_three_units_with_their_context():
    units = claims.split_units(THREE)
    assert len(units) == 3
    assert "daftar lewat WhatsApp" in units[0] and "Sebarkan ke semua grup" in units[2]


@pytest.mark.parametrize("text", [
    "Hati-hati penculik anak naik mobil putih keliling sekolah. Sebarkan ke semua grup keluarga.",       # one claim + a push
    "Gempa M9 akan terjadi besok di Jawa, menurut BMKG. Gempa M9 akan terjadi besok di Jawa menurut BMKG!!",  # the same claim twice
    "Selamat pagi keluarga, semoga sehat selalu. Amin.",
])
def test_one_claim_is_never_split(text):
    assert claims.split_units(text) == []


def test_at_most_three_claims():
    text = ("Pemerintah menaikkan tarif listrik rumah tangga mulai Desember 2026. BMKG mencatat gempa magnitudo 5,1 di selatan Jawa pagi ini. "
            "Polisi menangkap pelaku penipuan rekrutmen di Bekasi kemarin. Harga beras naik dua kali lipat di pasar induk Jakarta. "
            "Kementerian Kesehatan membuka pendaftaran vaksin gratis tanggal 12 Januari.")
    assert len(claims.split_units(text)) == 3


def test_near_duplicate_sentences_are_one_claim():
    text = " ".join(f"Pemerintah menaikkan harga komoditas nomor {w} sebesar {n} persen mulai bulan depan." for w, n in [("beras", 10), ("gula", 20)])
    assert claims.split_units(text) == []


def test_each_claim_gets_its_own_answer_and_the_message_takes_the_worst():
    r = pipeline.check(THREE, CFG)
    assert r["reason"] == "beberapa_klaim" and r["status"] == "terbukti_salah" and len(r["claims"]) == 3
    assert [c["status"] for c in r["claims"]] == ["terbukti_salah", "belum_ada_pemeriksaan", "terbukti_salah"]
    assert "3 klaim" in r["voice_script"]
    out = reply_text(r, html=False)
    assert "PESAN BERISI BEBERAPA KLAIM" in out and "1. 🔴" in out and "2. ⚪" in out and "3. 🔴" in out
    assert out.count("Sumber:") == 2                       # only the two debunked claims have a source to cite


def test_a_message_with_a_link_is_not_split(monkeypatch):
    from halio import link_check

    monkeypatch.setattr(link_check, "check_links", lambda t: [])
    r = pipeline.check(THREE + " https://contoh.example/x", Settings(google_factcheck_key=None, llm_enabled=False, link_check_enabled=True))
    assert not r.get("claims")      # links are checked once for the whole message, not once per claim


# ---- agency copy ------------------------------------------------------------------------------------------------

def test_wire_dateline_is_detected_but_a_passing_mention_is_not():
    assert wire_group("Jakarta (ANTARA) - Pemerintah memastikan tarif listrik naik.") == "ANTARA"
    assert wire_group("JAKARTA (Reuters) - Tarif naik") == "Reuters"
    assert wire_group("Menurut ANTARA, tarif listrik naik. Foto: ANTARA FOTO/Aditya") is None


CLAIM = "Pemerintah menaikkan tarif listrik pelanggan rumah tangga mulai Desember 2026"
TODAY = date(2026, 11, 6)
ECFG = Settings(google_factcheck_key=None, llm_enabled=True, llm_provider="google", link_check_enabled=False, evidence_engine="v2")


def run(pages):
    return evidence.investigate_v2(
        CLAIM, ECFG, discover=lambda c, cfg: ([{"uri": u, "title": ""} for u in pages], []), fetch=lambda u: pages[u],
        judge=lambda c, ps, cfg: [Judgement(p.id, "supports", True) for p in ps], today=TODAY, extra_candidates=lambda c, cfg: [])


def page(host, body, published="2026-11-05"):
    return Page(text=body, final_url=f"https://{host}/a", title="t", published=published)


def test_outlets_printing_the_same_agency_copy_are_one_voice():
    wire = "Jakarta (ANTARA) - Pemerintah memastikan tarif listrik pelanggan rumah tangga naik mulai Desember 2026 menurut Kementerian ESDM."
    pages = {"https://www.tempo.co/1": page("www.tempo.co", wire), "https://news.detik.com/1": page("news.detik.com", wire.replace("memastikan", "menyatakan")),
             "https://www.antaranews.com/1": page("www.antaranews.com", wire)}
    r = run(pages)
    assert (r.status, r.reason) == ("belum_ada_pemeriksaan", "satu_media_melaporkan")
    assert {i["grup"] for i in r.items} == {"ANTARA"}


def test_agency_copy_plus_an_independent_report_is_two_voices():
    wire = "Jakarta (ANTARA) - Pemerintah memastikan tarif listrik pelanggan rumah tangga naik mulai Desember 2026 menurut Kementerian ESDM."
    own = "Tempo menelusuri bahwa tarif listrik pelanggan rumah tangga naik mulai Desember 2026 setelah rapat internal pemerintah."
    r = run({"https://news.detik.com/1": page("news.detik.com", wire), "https://www.tempo.co/1": page("www.tempo.co", own)})
    assert r.status == "dilaporkan_media" and {i["grup"] for i in r.items} == {"ANTARA", "Tempo"}


# ---- telemetry --------------------------------------------------------------------------------------------------

def store(k=2):
    return Store(Path(tempfile.mkdtemp()) / "t.db", k_anonymity=k)


def result_with_evidence(**over):
    ev = {"reason": "satu_media_melaporkan", "dibuka": 4, "relevan": 1,
          "ditolak": [{"host": "a", "alasan": "http_404"}, {"host": "b", "alasan": "bukan_sumber_dikenal"}, {"host": "c", "alasan": "http_404"}]}
    base = {"status": "belum_ada_pemeriksaan", "claim": "x", "reason": "satu_media_melaporkan", "match": None, "evidence": ev,
            "manipulation": {"techniques": []}}
    return {**base, **over}


def test_telemetry_counts_reasons_without_any_text():
    s = store()
    s.record(result_with_evidence(), "web", None)
    s.record(result_with_evidence(engine_fallback=True), "web", None)
    t = s.evidence_stats(1)
    assert t["pemeriksaan"] == 2 and t["halaman_dibuka"] == 8 and t["halaman_relevan"] == 2 and t["mesin_cadangan"] == 1
    assert {r["alasan"]: r["n"] for r in t["ditolak"]} == {"http_404": 4, "bukan_sumber_dikenal": 2}
    assert s.radar(1)["evidence_telemetry"]["pemeriksaan"] == 2
    with sqlite3.connect(s.path) as c:   # only counts are stored: no claim text anywhere in the telemetry table
        assert "x" not in " ".join(str(v) for row in c.execute("SELECT * FROM evidence_telemetry") for v in row if isinstance(v, str) and len(v) > 1 and v == "x")


def test_a_multi_claim_message_adds_each_claims_evidence():
    s = store()
    s.record({**result_with_evidence(evidence=None), "claims": [result_with_evidence(), result_with_evidence()]}, "web", None)
    assert s.evidence_stats(1)["pemeriksaan"] == 2


def test_old_events_and_telemetry_are_deleted_after_30_days():
    s = store()
    s.record(result_with_evidence(), "web", None)
    old = (date.fromisoformat(today()) - timedelta(days=45)).isoformat()
    with sqlite3.connect(s.path) as c:
        c.execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (old, "terbukti_salah", "x", "k", "", "web"))
        c.execute("INSERT INTO evidence_telemetry VALUES (?,?,?,?)", (old, "ditolak", "http_404", 9))
    s.prune()
    with sqlite3.connect(s.path) as c:
        assert c.execute("SELECT COUNT(*) FROM events WHERE day=?", (old,)).fetchone()[0] == 0
        assert c.execute("SELECT COUNT(*) FROM evidence_telemetry WHERE day=?", (old,)).fetchone()[0] == 0
    assert s.evidence_stats(1)["pemeriksaan"] == 1


def test_each_unknown_claim_of_a_multi_claim_message_is_counted():
    s = store(k=2)
    def msg(a, b):
        return {"status": "belum_ada_pemeriksaan", "claim": a, "reason": "tidak_ada_bantahan", "match": None, "manipulation": {"techniques": []},
                "claims": [{"status": "belum_ada_pemeriksaan", "claim": a, "reason": "tidak_ada_bantahan"},
                           {"status": "belum_ada_pemeriksaan", "claim": b, "reason": "tidak_ada_bantahan"}]}
    s.record(msg("Jembatan Barelang ditutup total lima hari mulai lusa", "Harga beras naik dua kali lipat bulan depan di Batam"), "telegram", "tg:1")
    s.record(msg("Harga beras naik dua kali lipat bulan depan di Batam", "Bandara ditutup karena kabut asap pekan depan"), "telegram", "tg:2")
    texts = [e["text"] for e in s.radar(1)["emerging_rumours"]]
    assert any("Harga beras" in t for t in texts)        # reached k=2 only because it was counted from inside the two messages

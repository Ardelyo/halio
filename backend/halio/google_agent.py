"""Gemini evidence discovery with independent URL and quote verification."""

from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

from .config import Settings
from .llm_verdict import LlmJudgement
from .retrieval import Debunk, Match
from . import reading
from .source_verifier import Verification, best_passage, quote_present, verify_source
from .store import WIB

log = logging.getLogger(__name__)


class SourceEvidence(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    url: str = Field(min_length=12, max_length=2000)
    quote: str = Field(min_length=40, max_length=1500)
    relation: Literal["supports", "refutes", "context"]
    published: date | None = None
    valid_until: date | None = None


class Investigation(BaseModel):
    summary: str = Field(max_length=800)
    sources: list[SourceEvidence] = Field(default_factory=list, max_length=3)


class FoundInvestigation(Investigation):
    """Investigation plus every page the search returned (the model's schema above does not include this)."""
    grounding: list[dict] = Field(default_factory=list)


@dataclass
class AgentResult:
    status: str
    reason: str
    match: Match | None
    judgement: LlmJudgement | None
    note: dict


SYSTEM = """Kamu adalah agen pengumpul bukti Halio untuk klaim berbahasa Indonesia.
Gunakan Google Search untuk menemukan sumber primer atau pemeriksa fakta yang benar-benar membahas klaim.
Jangan menilai dari pengetahuan internal. Jangan mengarang URL, penerbit, tanggal, atau kutipan.
Untuk setiap sumber, salin satu kutipan utuh minimal 40 karakter persis dari halaman yang membuktikan relasinya.
'supports' hanya jika kutipan mendukung seluruh klaim; 'refutes' hanya jika membantah klaim yang sama;
'context' jika hanya mirip topik, sebagian relevan, atau tidak cukup. Jangan memaksakan jawaban.
Utamakan situs resmi .go.id/.mil.id atau WHO. Untuk bantahan, pemeriksa fakta IFCN/TurnBackHoax juga boleh.
Sertakan tanggal publikasi hanya jika tertera. Sertakan valid_until hanya untuk informasi yang memang dibatasi tanggal.
Jika tidak menemukan bukti yang relevan, kembalikan daftar sources kosong. Maksimal tiga sumber terbaik."""


def request_investigation(claim: str, cfg: Settings, seed_urls=()) -> Investigation:
    from google import genai
    from google.genai import types

    client = genai.Client(vertexai=True, project=cfg.google_cloud_project, location=cfg.google_cloud_location)
    timeout = types.HttpOptions(timeout=cfg.agent_timeout_s * 1000)
    prompt = f"Tanggal pemeriksaan: {datetime.now(WIB).date().isoformat()}\nKlaim yang harus diperiksa:\n<klaim>{claim}</klaim>"
    discovery = client.models.generate_content(
        model=cfg.llm_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            max_output_tokens=3000,
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            http_options=timeout,
        ),
    )
    grounding = [f"Sumber kandidat lokal: {url}" for url in seed_urls]
    found: list[dict] = []
    for candidate in discovery.candidates or []:
        metadata = getattr(candidate, "grounding_metadata", None)
        for chunk in getattr(metadata, "grounding_chunks", None) or []:
            web = getattr(chunk, "web", None)
            if web and web.uri:
                grounding.append(f"{web.title or 'Sumber'}: {web.uri}")
                found.append({"title": web.title or "", "uri": web.uri})
    extraction = client.models.generate_content(
        model=cfg.llm_model,
        contents=(
            f"Klaim awal:\n<klaim>{claim}</klaim>\n\nLaporan pencarian:\n<laporan>{discovery.text}</laporan>\n\n"
            f"URL grounding yang boleh digunakan:\n{chr(10).join(grounding) or 'Tidak ada'}"
        ),
        config=types.GenerateContentConfig(
            system_instruction="Ubah laporan menjadi skema yang diminta. Jangan menambah sumber, kutipan, tanggal, atau fakta baru. Kosongkan sources jika laporan tidak memiliki bukti lengkap.",
            response_mime_type="application/json",
            response_schema=Investigation,
            max_output_tokens=3000,
            thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
            http_options=timeout,
        ),
    )
    base = Investigation.model_validate_json(extraction.text)
    return FoundInvestigation(**base.model_dump(), grounding=found)


def repair_source(claim: str, check: Verification, cfg: Settings) -> Verification:
    if check.reason != "kutipan_tidak_ada_di_halaman" or not check.page_text:
        return check
    # A debunk from an official or fact-check page: let CODE pick the page's own sentence, so the quote is verbatim by construction.
    if check.evidence.relation == "refutes" and check.source_kind in {"resmi", "cek_fakta"}:
        passage = best_passage(claim, check.page_text)
        if passage:
            fixed = check.evidence.model_copy(update={"quote": passage, "url": check.final_url})
            return Verification(True, "terverifikasi_dari_halaman", fixed, check.final_url, check.source_kind)
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project=cfg.google_cloud_project, location=cfg.google_cloud_location)
        response = client.models.generate_content(
            model=cfg.llm_model,
            contents=(
                f"Klaim:\n<klaim>{claim}</klaim>\n\nIsi halaman {check.final_url}:\n"
                f"<halaman>{check.page_text[:80000]}</halaman>"
            ),
            config=types.GenerateContentConfig(
                system_instruction=(
                    "Pilih satu kutipan persis dan berurutan dari isi halaman, bukan dari ingatan atau ringkasan. "
                    "Nilai apakah kutipan itu supports/refutes seluruh klaim, atau hanya context. "
                    "Ambil tanggal publikasi hanya jika terlihat di halaman. Jangan membuat atau memperbaiki ejaan kutipan."
                ),
                response_mime_type="application/json",
                response_schema=SourceEvidence,
                max_output_tokens=2000,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                http_options=types.HttpOptions(timeout=cfg.agent_timeout_s * 1000),
            ),
        )
        corrected = SourceEvidence.model_validate_json(response.text).model_copy(
            update={"url": check.final_url, "name": check.evidence.name}
        )
        if not quote_present(corrected.quote, check.page_text):
            return check
        return Verification(True, "terverifikasi_dari_halaman", corrected, check.final_url, check.source_kind)
    except Exception as exc:
        log.warning("Gemini source repair unavailable: %s", type(exc).__name__)
        return check


def _match(claim: str, verification: Verification, positive: bool) -> Match:
    evidence = verification.evidence
    digest = hashlib.sha256(verification.final_url.encode()).hexdigest()[:12]
    kind = "verifikasi_positif" if positive else "bantahan"
    wording = "sejalan dengan kutipan sumber ini" if positive else "membantah klaim ini"
    debunk = Debunk(
        id=f"gemini-{digest}",
        kategori="penelusuran_web",
        klaim=claim,
        varian=[],
        fakta=evidence.quote,
        sederhana=f"{evidence.name} menerbitkan keterangan yang {wording}. Buka sumber untuk membaca konteks lengkapnya.",
        sumber=[{"nama": evidence.name, "url": verification.final_url, "jenis": verification.source_kind}],
        jenis=kind,
        kutipan_sumber=evidence.quote,
        valid_from=evidence.published.isoformat() if evidence.published else None,
        valid_until=evidence.valid_until.isoformat() if evidence.valid_until else None,
    )
    return Match(debunk, 1.0, claim)


def investigate(
    claim: str,
    cfg: Settings,
    seed_urls=(),
    request=request_investigation,
    verifier=verify_source,
    repairer=repair_source,
) -> AgentResult | None:
    try:
        report = request(claim, cfg, seed_urls)
    except Exception as exc:
        log.warning("Gemini investigation unavailable: %s", type(exc).__name__)
        return None

    with ThreadPoolExecutor(max_workers=max(1, min(3, len(report.sources)))) as pool:
        checks = list(pool.map(verifier, report.sources))
        checks = list(pool.map(lambda check: repairer(claim, check, cfg), checks))
    verified = [check for check in checks if check.ok]
    note = {
        "penjelasan": f"Gemini menemukan {len(report.sources)} kandidat; backend memverifikasi {len(verified)} kutipan dari halaman sumber.",
        "sumber_ditemukan": len(report.sources),
        "sumber_terverifikasi": len(verified),
        "sumber_ditolak": [{"url": c.evidence.url, "alasan": c.reason} for c in checks if not c.ok],
        "bacaan": reading.build(getattr(report, "grounding", [])),
    }
    relations = {c.evidence.relation for c in verified}
    if not verified:
        return AgentResult("tidak_yakin", "tidak_ada_kutipan_terverifikasi", None, None, note)
    if {"supports", "refutes"} <= relations:
        match = _match(claim, verified[0], positive=False)
        return AgentResult("tidak_yakin", "bukti_bertentangan", match, None, note)

    positive = "supports" in relations
    eligible = [
        c for c in verified
        if c.evidence.relation == ("supports" if positive else "refutes")
        and (not positive or c.source_kind == "resmi")
    ]
    if not eligible:
        return AgentResult("tidak_yakin", "sumber_bukan_resmi", None, None, note)
    match = _match(claim, eligible[0], positive)
    evidence = eligible[0].evidence
    judgement = LlmJudgement("sama", match.debunk.id, evidence.quote, report.summary, True)
    note["kutipan"] = evidence.quote
    if positive:
        return AgentResult("sejalan_dengan_sumber", "cocok_dengan_sumber_resmi", match, judgement, note)
    return AgentResult("terbukti_salah", "cocok_dengan_bantahan_web", match, judgement, note)

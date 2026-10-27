# Third-party Components & Declaration

Rulebook §G: third-party libraries, frameworks, APIs, AI models and tools are allowed **with attribution**; pre-existing work must be **declared clearly**. Keep this file complete. Verify licence terms before submission (task D-1).

## Declaration of pre-existing work
The repository was created on 27 Oct 2026, within the programme period, from the team's own research report. No code from earlier projects was reused. *(Update this line if that changes.)*

## Software
| Component | Use | Licence (verify) |
|---|---|---|
| FastAPI, Starlette, Pydantic, Uvicorn | HTTP API | MIT / BSD |
| HTTPX | HTTP client | BSD-3 |
| Pillow | Halio Card rendering | MIT-CMU (HPND) |
| gTTS (optional) | Server-side Indonesian TTS (calls Google Translate TTS) | MIT; check the terms of the underlying service |
| anthropic SDK (optional) | T2 grounded LLM step | MIT |
| pytest | Tests | MIT |
| onnxruntime-web | On-device inference in the extension | MIT |

## Models & data
| Component | Use | Licence / terms |
|---|---|---|
| NudeNet 3.4 (320n ONNX) | Optional on-device adult-content screening | MIT (per PyPI listing) |
| Google Fact Check Tools API (optional) | ClaimReview lookup | Google API ToS; ClaimReview content belongs to publishers |
| LLM API (optional, `HALIO_LLM=1`) | Match confirmation with exact-quote verification | Provider terms |
| Debunk corpus (`data/debunks.json`) | Summaries in our own words + links to sources | Sources: Katadata, Bisnis.com, Investortrust, BMKG, Kompas TV, Republika, Liputan6 Cek Fakta (with Mafindo), MerahPutih, RRI, Kumparan. No article text copied |

## Research sources used in the narrative
See the research report's source list (Liputan6, CODEPOLITAN, Katadata, detikNews, Kemhan Pothan, Martel & Rand 2024, Cambridge prebunking studies, and others).

# Halio: Project Plan

**Kartika Cyber Hackathon 2026 · Siber Sosial · Plan v1, 27 Oct 2026**
Inputs: the official Rulebook (PUSSIBERAD × CODEPOLITAN) and the team research report *"Halio: jadikan keluarga lini pertahanan kognitif"* (27 Oct 2026).

> **Deadline: Sunday 15 Nov 2026, 23:59 WIB.** Late submissions are not processed "dalam keadaan apa pun". Our internal deadline is **Sat 14 Nov 20:00 WIB**. That leaves **19 calendar days** from today.

---

## 0. TL;DR

1. **Build the concept the research recommends ("Halio Keluarga")**: forward a suspicious message and get back a plain-language, sourced answer, a shareable Halio Card and a voice note. When there is no fact-check, Halio says so honestly ("belum ada pemeriksaan") and offers a human reviewer.
2. **Add one thing the rulebook makes necessary: "Radar Ketahanan Kognitif".** The official category definition is *"Pemantauan dan analisis ruang siber sosial untuk mendeteksi ancaman non-teknis"*, and 25% of the score is *"kesesuaian dengan kebutuhan keamanan siber TNI AD"*. A citizen-only app is weak on both. The Radar turns the same checks into an aggregate, k-anonymous early-warning view for a cyber unit. Examples: a rising wave of scams that impersonate TNI AD, or a new rumour spreading among many distinct people. That makes Halio both a family tool and a monitoring sensor, without surveilling anyone.
3. **Primary chat channel: Telegram. WhatsApp is a stretch goal.** Judges must be able to *try the work themselves* (Rulebook G.1: "link … yang memungkinkan Dewan Juri untuk mencoba"). A Telegram bot and a public web URL can be live within days. WhatsApp Cloud API access is unverified (task C-1).
4. **A working scaffold already exists in this repository** (see §4 status column). The plan below spends the remaining time on hosting, real data, hardening, the extension model, and above all the **video, slides and proposal**.

---

## 1. What the rulebook settled (vs. research assumptions)

| Topic | Research said | Rulebook says (authoritative) | Consequence |
|---|---|---|---|
| Deadline | "15 Nov, unofficial" | **15 Nov 2026, 23:59 WIB**, hard | Internal deadline 14 Nov 20:00 |
| Judging | unknown rubric | **Relevansi & Manfaat 25% · Inovasi Teknis 25% · Fungsionalitas Purwarupa 25% · Kelayakan Implementasi 15% · Dokumentasi 10%** | See §2. 40% of the score is about TNI AD fit and working software |
| Siber Sosial definition | "not found" | "Pemantauan dan analisis ruang siber sosial untuk mendeteksi ancaman non-teknis. Contoh: analisis sentimen, **deteksi disinformasi**" | Add the Radar (monitoring) layer |
| Deliverables | proposal + docs + video | **Public project link, thumbnail 1200×630 ≤500 KB, ≤5 screenshots, video ≤10 min on YouTube, slide deck** | §8 checklist; thumbnail script exists |
| Finalists | top 10 | Online judging 16 Nov, **finalists announced 20 Nov**, final **24 Nov** at Hotel Aston Kartika Jakarta, **10 min per team** (explanation + demo + Q&A), ≥1 member on site | Finals prep 20–24 Nov |
| Webinar | "two webinars" | Webinar 1: 19 Oct (recorded); **Webinar 2: 5 Nov** | Bring the §10 question list to 5 Nov |
| IP | "verify" | IP stays with the team; organiser gets a non-exclusive licence to showcase; PUSSIBERAD may adopt ideas "dengan diskusi bersama tim" | No licence decision needed before submission |
| Third-party | "verify" | Open-source/legal third-party libraries, APIs, models allowed **with attribution**; pre-existing work allowed **with explicit declaration** | `docs/THIRD_PARTY.md` must be complete |
| Content rules | n/a | No pornography, SARA, illegal content, third-party personal data | **Never put explicit test images in the repo or video.** Demo the blur with gambling banners. Fictional names only |
| Prizes | "Rp 100.7 jt" | Rp 20 jt / 12.5 jt / 7.5 jt + Golden Ticket (Bintara Siber recommendation, **only for winners under 26**) | — |
| Team | max 3 | max 3, one team per person, member changes ≥7 days before deadline with written approval | Lock roster by 8 Nov |

---

## 2. How we win each scoring criterion

| Criterion (weight) | What judges look for | Our answer | Evidence we must show |
|---|---|---|---|
| **Relevansi & Manfaat (25%)** | Fit with TNI AD cyber needs | (a) Siber Sosial = detecting non-technical threats. The Radar detects disinformation and scam campaigns early, especially ones **impersonating TNI AD** (recruitment scams, fake officer deepfakes). (b) **Soldiers' families** are a natural first cohort: frequent targets of scams and influence operations, and reachable through existing unit structures (e.g. family-support organisations) *(partnership hypothesis, not claimed)*. (c) Kemhan's "kedaulatan kognitif" framing: the family is the smallest unit of resilience. | Radar screen with the "Penipuan mencatut TNI" category; the TNI recruitment-scam demo claim; the 60-second story |
| **Inovasi Teknis (25%)** | Original idea, appropriate tech | We openly say we don't compete on "AI hoax detector + blur". Both exist (§5 of the research). What's new: (1) **abstain-first verdicts** with three honest states; (2) **core-claim guard** that stops true same-topic statements from being labelled hoaxes (eval: 0 false-hoax); (3) **grounded LLM** that can only confirm with an exact quote from a named source; (4) **k-anonymous rumour surfacing** (rumour text is stored only after ≥k distinct reporters); (5) **voice-first, elderly-friendly** UX; (6) **on-device image screening** (0 bytes of images sent). | `eval/RESULTS.md`, architecture diagram, the "true BMKG report is not called a hoax" demo moment |
| **Fungsionalitas Purwarupa (25%)** | It runs and can be demonstrated | Judges can use it themselves: public web app + Telegram bot + seeded Radar. The video shows real flows, labelled where simulated. | Live URL up from 14 Nov to 24 Nov; bot uptime; no fake screens |
| **Kelayakan Implementasi (15%)** | Can a unit actually deploy it? | Single Docker container, no GPU, no paid API required (LLM and ClaimReview optional), SQLite → Postgres path, runs on-prem. Debunk corpus can be fed by official clarifications (e.g. Dinas Penerangan). Human review queue for appeals and escalations. Cost per check ≈ 0 in retrieval-only mode. | `docs/ARCHITECTURE.md` deployment section; `docker compose up` in the video |
| **Kualitas Dokumentasi (10%)** | Proposal, technical docs, video clarity | README (ID), ARCHITECTURE, PRIVACY, eval results, THIRD_PARTY, video ≤10 min following the demo script | §8 checklist |

**Honesty rules (credibility is the product):** never claim deepfake detection; never call a statement a hoax without a named source; label every simulation; report eval numbers including failures; describe partner organisations as targets, not partners.

### 2.1 Evidence gate: prove one closed loop before adding features

See [RESEARCH_STANDOUT.md](RESEARCH_STANDOUT.md) for verified sources, competitor gaps, interview guides, and experiment protocols. The product position is **closed-loop cognitive resilience**: voluntary family signal → aggregate early warning → analyst triage/verification → sourced correction back to the family channel.

Two claims are still unproven: that the correction experience improves family decisions, and that Radar improves analyst work. Accuracy-nudge and prebunking studies justify testing these patterns, not claiming that Halio is effective. The preregistered accuracy-nudge replication found a failed first stage and only a small pooled effect; this is a reason to compare conditions honestly.

Before the next feature, run the approved research protocol:

1. **Family discovery:** 5–8 members, critical-incident interviews and observed tasks; no “do you like this idea?” validation.
2. **Operational discovery:** 3–5 prospective analysts and 2–3 fact-checkers; walk through real roles, evidence, authority, and response handoffs using synthetic scenarios.
3. **Formative family test:** correction card, accuracy pause, prebunking, and non-shaming tone. Report true/false sharing separately, discernment, comprehension, and time. Small samples are not effectiveness proof.
4. **Formative Radar test:** equivalent synthetic raw-feed and Radar scenarios, counterbalanced. Measure time-to-awareness, time-to-triage, triage precision, false alarms, correction time, and action clarity.
5. **Change the demo only after observing the loop:** family problem → voluntary signal → aggregate Radar → analyst decision → correction returned → evidence and limitations.

No interviews or human experiments have been completed by this planning work. Do not invent participants, access to TNI, findings, or endorsements. If time is insufficient, present the protocol and the working synthetic loop as such; do not substitute motivational quotations for evidence.

---

## 3. Product scope

### 3.1 Personas (synthetic; no Halio-specific user research has been completed)
- **Ibu Sri (68)**, the hero user: forwards messages to the family group out of love. Doesn't install apps and doesn't type much.
- **Dimas (34)**, the installer: Ibu Sri's son. Sets Halio up for her (the greeting, e.g. "Bu", and the family rules) and is tired of being the family "hoax police".
- **Analis Siber Satuan**, the Radar user: monitors trends, not individuals. Needs early warning of campaigns impersonating TNI AD.

These are hypotheses to test through §2.1, not discovered user needs.

### 3.2 Core flows (the only things the video must show)
1. **Family signal → answer**: forward/check voluntarily (Telegram or web), then voice note + Halio Card + source links.
2. **Honest abstain**: an unknown claim gets "Belum ada pemeriksaan" and an offer to ask a human reviewer.
3. **No false accusation**: a *true* statement on a hoax topic gets "Tidak yakin", not "Terbukti salah".
4. **Aggregate early warning → analyst triage**: Radar surfaces the synthetic scenario; the analyst inspects evidence, records a decision, and responds.
5. **Correction returns → evidence**: the sourced answer reaches the original channel; the demo closes with actual eval, limitations, and research status.

The extension is optional supporting footage, not part of the core story.

### 3.3 Feature matrix and repository status

Legend: ✅ working in repo · 🟡 code present, needs config/verification · ⬜ to do · 🎭 honest mock (labelled in demo)

| # | Feature | Plan | Status |
|---|---|---|---|
| 1 | Forward-to-check (Telegram bot) | MVP core | 🟡 code done; needs bot token + hosted API |
| 1b | Forward-to-check (WhatsApp Cloud API) | Stretch | 🟡 webhook written, untested; access unverified |
| 1c | Web app + Android share target (PWA) | MVP core | ✅ |
| 2 | Voice note (Halio Suara) | MVP core | 🟡 gTTS server-side (needs internet) + browser fallback ✅; pre-render demo clips ⬜ |
| 3 | Plain-language explanation ("sederhana") | MVP | ✅ per debunk |
| 4 | Source trail visualisation | Honest mock | ⬜ (show source list; trail graphic only in slides) |
| 5 | Abstain + human escalation | MVP core | ✅ API + queue; reviewer UI ⬜ (use DB/CLI for demo) |
| 6 | Manipulation-technique prebunking | MVP light | ✅ 6 techniques, ID lexicon |
| 7 | Family Guardian weekly summary | Roadmap | ⬜ |
| 8 | Voice-scam "kode keluarga" | Honest mock | ⬜ slide only |
| 9 | Halio Card (shareable image) | MVP | ✅ 1080×1080 PNG |
| 10 | Family filter profile (blur rules) | MVP feed layer | ✅ judol rule + modes; 🟡 NudeNet "pintar" mode needs model download |
| 11 | Disaster mode (BNPB/BMKG) | Roadmap | ⬜ |
| 12 | Pause before sharing | MVP | ✅ 10-second pause in web app |
| R | **Radar Ketahanan Kognitif** | MVP (new) | ✅ aggregates, k-anon rumours, small-cell suppression, demo banner |
| E | Offline eval + calibration | MVP | ✅ `eval/run_eval.py` |
| L | Grounded LLM (T2) | Optional | 🟡 code done, untested against live API |
| G | Google Fact Check ClaimReview (T1) | Optional | 🟡 code done; Indonesian coverage unknown |

**If time runs out, cut in this order:** WhatsApp → NudeNet "pintar" mode → LLM step → extension (keep a screen recording). **Never cut:** forward → voice + card, honest abstain, Radar.

---

## 4. Architecture (summary; full version in `docs/ARCHITECTURE.md`)

```
 Ibu Sri ──forward──► Telegram / WhatsApp / Web(PWA share)
                              │  (text only; user-initiated)
                              ▼
                     FastAPI  /api/check
   claim extraction → PII scrub (≤300 chars) → T1 local retrieval (TF-IDF + core-claim guard)
                    → [T1 ClaimReview] → [T2 grounded LLM, quote must match] → 3-state verdict
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
   voice script/MP3      Halio Card PNG      Radar store (aggregates only;
                                              rumour text only after k reporters)
 Chrome extension (feed layer): badges + image screening fully on-device; text sent only on click.
```

---

## 5. Team and roles (max 3)

| Role | Owns | Also |
|---|---|---|
| **A: Backend & AI lead** | `backend/` pipeline, corpus tooling, eval, LLM/ClaimReview, hosting/Docker | Technical documentation, architecture diagram |
| **B: Channels & Frontend** | Telegram bot, WhatsApp attempt, PWA, Radar UI, Chrome extension + model | Screenshots, screen recordings |
| **C: Product, Data & Story** | Debunk corpus (verify every URL), test set, demo script, video, slides, proposal, thumbnail | Webinar 2 questions, submission upload |

Daily 15-minute stand-up (WIB evening). Single source of truth: this file plus GitHub issues named by task ID.

---

## 6. Timeline (27 Oct → 15 Nov, then finals)

| Dates | Focus | Exit gate |
|---|---|---|
| **Tue 27 – Wed 28 Oct** | Read rulebook (done); lock concept + Radar; assign roles; register on CODEPOLITAN (team name, karya name, category **Siber Sosial**); create Telegram bot; try WhatsApp test number; email Mafindo/CekFakta asking for data access; apply for Google Fact Check API key | **G1 (28 Oct):** concept + channel decision written here |
| Thu 29 Oct – Mon 2 Nov | Deploy backend to a public URL (HTTPS); Telegram end-to-end; expand corpus to 20–30 verified debunks (priority: TNI-related scams, bansos, disaster, health); human-review CLI; pre-render voice for 5 demo claims | **G2 (Mon 2 Nov):** a judge-style tester forwards a message on their own phone and gets voice + card in under 10 s |
| Tue 3 – Sat 7 Nov | Extension: fetch model, test NudeNet on a *safe* balanced set (no explicit images in repo); test on demo feed + 1 real site; Radar polish; expand test set to 80+ items written by someone other than the corpus author; **Webinar 2 (Thu 5 Nov)**: ask the §10 questions | **G3 (Sat 7 Nov):** extension demo stable; eval re-run; roster locked (member changes must be made ≥7 days before the deadline) |
| Sun 8 – Wed 11 Nov | Hardening (rate limit, error states, uptime monitor); LLM step tested if key available; write proposal + technical docs; slide deck v1; record backup screen captures | **G4 (Wed 11 Nov 23:59):** code freeze except bug fixes |
| Thu 12 – Fri 13 Nov | Record and edit the video (target 6–8 min, ≤10); 5 screenshots; final slides; final README | Video unlisted on YouTube, reviewed by all 3 |
| **Sat 14 Nov** | Submit everything by 20:00 WIB; verify every link in a private browser window | **G5:** submission confirmed on platform |
| Sun 15 Nov | Buffer only. Updates allowed until 23:59; only the last submission is judged | — |
| 16 – 20 Nov | Online judging: **keep the URL, bot and Radar up** (uptime monitor, no risky deploys) | — |
| 20 – 24 Nov | If finalist: 10-minute pitch rehearsals (timer), offline fallback, travel for ≥1 member to Jakarta | Final 24 Nov |

---

## 7. Backlog (task IDs)

**A: Backend & AI**
- A-1 Deploy to a public HTTPS host (Docker); set `PUBLIC_BASE_URL`; health monitor. *Due 30 Oct.*
- A-2 Corpus loader for TurnBackHoax/Mafindo/CekFakta articles once access is granted; until then, curate by hand. *Due 2 Nov.*
- A-3 Pre-render voice MP3s for the 5 demo claims (no live TTS dependency in the video). *Due 2 Nov.*
- A-4 Rate limiting + input size guard on `/api/check`; error messages in Indonesian. *Due 8 Nov.*
- A-5 Human-review CLI: list escalations/appeals and send an answer back through the channel. *Due 6 Nov.*
- A-6 Test LLM step (`HALIO_LLM=1`) on the test set; record whether it ever upgrades without a quote (it must not). *Due 10 Nov.*
- A-7 Test ClaimReview coverage for 30 Indonesian claims; report the hit rate honestly. *Due 6 Nov.*
- A-8 Optional: embeddings retrieval behind the same interface if the corpus exceeds ~200 entries.

**B: Channels & Frontend**
- B-1 Create bot via @BotFather, set description/commands, run against hosted API. *Due 30 Oct.*
- B-2 WhatsApp Cloud API test number + webhook; **decision on 3 Nov**: go or demo with Telegram. *Due 3 Nov.*
- B-3 PWA: install test on 2 Android phones (share target), low-end phone timing. *Due 4 Nov.*
- B-4 `scripts/fetch_models.py`: verify URLs, load NudeNet in offscreen doc, measure ms/image. *Due 6 Nov.*
- B-5 Extension on one real site (selectors), plus the demo feed. *Due 7 Nov.*
- B-6 Radar: login token, mobile layout check. *Due 8 Nov.*

**C: Product, Data & Story**
- C-1 Verify official site items; register team; join official WhatsApp group. *Due 28 Oct.*
- C-2 **Open every URL in `data/debunks.json`**, confirm wording, replace with fact-checker URLs where possible; add 15–25 entries. *Due 2 Nov.*
- C-3 Write 50 more test items (true same-topic statements are the most important). *Due 6 Nov.*
- C-4 Finalise the 60-second story and the demo script (`docs/DEMO_SCRIPT.md`). *Due 5 Nov.*
- C-5 Slide deck (features, architecture, tech, rubric mapping, honesty, roadmap, business). *Due 12 Nov.*
- C-6 Proposal document (problem with sourced data, story, competitor table + "where we are not new", solution, TNI relevance, implementation, impact metrics, risks). *Due 11 Nov.*
- C-7 Video recording + edit, YouTube upload (unlisted or public as allowed). *Due 13 Nov.*
- C-8 Five screenshots + thumbnail (`scripts/make_thumbnail.py`). *Due 13 Nov.*

**D: Cross-cutting**
- D-1 Complete `docs/THIRD_PARTY.md` (attribution is a rule, not a nicety).
- D-2 Pre-existing work declaration: state that the repository was scaffolded on 27 Oct 2026 within the programme period, and list any reused code.
- D-3 Content review of everything public (no SARA, no explicit imagery, fictional names, no real phone numbers).

---

## 8. Submission checklist (Rulebook §G)

See `docs/SUBMISSION_CHECKLIST.md` for the full list. In short: public link (web + bot) · thumbnail 1200×630 ≤500 KB · ≤5 screenshots · YouTube video ≤10 min · slides · one submission, last version counts.

---

## 9. Risk register

| ID | Risk | Likelihood / impact | Trigger date | Mitigation / fallback |
|---|---|---|---|---|
| R1 | Not enough time | High / High | every gate | Cut list in §3.3; gates G1–G5; freeze 11 Nov |
| R2 | No access to fact-check data (Mafindo/CekFakta licence) | High / Med | 2 Nov | Hand-curated corpus with links only (no copied text); ClaimReview API; say so in docs |
| R3 | ClaimReview has poor Indonesian coverage | Med / Low | 6 Nov | Abstain is a feature; local corpus first |
| R4 | WhatsApp access not granted | High / Low | 3 Nov | Telegram is primary; show WhatsApp as roadmap, never fake it |
| R5 | **False "hoax" label on a true statement** | Med / **Very high** | continuous | Core-claim guard, three states, LLM may only downgrade without a quote, eval false-hoax metric must stay 0 on the expanded test set |
| R6 | Political-bias perception | Med / High | content review | Corpus excludes political opinion; topic-neutral technique labels; appeal button; transparency log |
| R7 | Privacy / UU PDP concerns, "is this surveillance?" | Med / High | pitch Q&A | Radar is aggregate + k-anonymous; no message storage; Radar is for trends, not prosecution; see PRIVACY.md |
| R8 | Hosting goes down during judging (16–20 Nov) | Low / High | 14 Nov | Uptime monitor; no deploys during judging; backup host; video already shows everything |
| R9 | Blur false positives / skin-tone bias | Med / Med | 7 Nov | Report FP rate on a balanced *safe* set; one-tap reveal; frame as user-chosen family rule |
| R10 | Rule violation through demo content | Low / **Disqualifying** | 13 Nov | D-3 content review; gambling banners for blur demo; no explicit images anywhere |
| R11 | "Why not just ChatGPT?" in Q&A | High / Med | finals | Prepared answer: proactive, sourced, abstains, family/voice UX, no message retention, runs on-prem without paid API |

---

## 10. Questions for Webinar 2 (Thu 5 Nov) or the committee

1. Is a Telegram bot plus a web URL an acceptable "Link Karya" for judges to try? Do judges need login-free access?
2. Must the live link stay online through 24 Nov, or only during online judging (16–20 Nov)?
3. May the Radar demo use clearly-labelled simulated data?
4. Final presentation: is the venue internet available for a live demo? Projector/HDMI? Can judges test on their own phones?
5. Slide format: PDF or link (Google Slides/Canva)? Any page limit?
6. Is the YouTube video allowed to be unlisted?
7. Any restrictions on calling third-party APIs (Google Fact Check, LLM providers) from the prototype?

---

## 11. Definition of done (submission)

- [ ] A tester outside the team can, using only the submitted link, check a message and receive a sourced answer, card and voice (or an honest abstain), within 10 s.
- [ ] `eval/RESULTS.md` regenerated on the final corpus and test set; false-hoax rate reported.
- [ ] Every debunk URL opened and verified by a human (C-2).
- [ ] Video ≤10 min shows the five core flows, with simulations labelled.
- [ ] THIRD_PARTY.md and pre-existing work declaration complete.
- [ ] All submission fields filled; links checked in a private window; submitted by 14 Nov 20:00 WIB.

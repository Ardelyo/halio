# Demo Script

Two cuts: the **submission video** (target 6–8 min, hard limit 10) and the **final pitch** (10 min total including Q&A, so ~6 min talk + demo). Narration in Bahasa Indonesia; stage notes in English. Rule from judges' experience: show one workflow, not a feature tour; be honest about what isn't built.

## A. Opening story (60 s), used in both

> (0–15) "Bayangkan Ibu Sri, 68 tahun. Setiap pagi ia meneruskan pesan ke grup keluarga, karena sayang, bukan karena jahat. Pagi ini: video Presiden yang membagikan bantuan tunai, lengkap dengan nomor WhatsApp untuk mendaftar."
>
> (15–35) "Itu bukan karangan. Awal 2025, video deepfake seperti itu menipu 100 orang di 20 provinsi, dengan 'biaya administrasi' yang terus naik. Kerugiannya Rp 65 juta, kecil per orang, berat bagi rumah tangga yang miskin."
>
> (35–50) "Dan penipuan hanya satu wajah dari masalah ini. Pada November 2018 di Kendal, pesan berantai tentang penculik anak berakhir dengan seorang pria, yang kemudian diketahui mengalami gangguan jiwa, dikeroyok massa."
>
> (50–60) "Empat dari sepuluh orang Indonesia ragu mampu mengenali hoaks. Ibu Sri tidak malas. Ia sendirian. Halio membuat Ibu Sri tidak sendirian."

Stage note: say "bayangkan". Ibu Sri is a persona. Facts: Katadata (100 victims / 20 provinces / Rp 65 jt), detikNews (Kendal 2018), Katadata LITDIG 2023 (40.2%). Refer to the Kendal victim respectfully; add no identifying details.

## B. Submission video (≈7 min)

| Time | Scene | Screen | Honesty note |
|---|---|---|---|
| 0:00–0:40 | **Family problem**: shortened story (A) and one synthetic suspicious message | B-roll / phone | Persona stated; do not present it as interview evidence |
| 0:40–1:00 | Siber Sosial framing and the differentiator: a closed loop, not another hoax classifier | One loop diagram | No claim of official doctrine, access, or partnership |
| 1:00–1:50 | **Voluntary family signal**: forward the message → sourced answer, Halio Card, voice note; explain the non-shaming correction language | Real phone recording | Demo claim is in the corpus; say so. Research-inspired design, not proven behaviour change |
| 1:50–2:20 | **Honest uncertainty**: unknown rumour → "Belum ada pemeriksaan" → human escalation; then a true same-topic statement is not called a hoax | Bot + web app | Both flows real; self-written test set limitation stated |
| 2:20–3:10 | **Aggregate early warning**: the voluntary reports appear as counts/trends in Radar; emerging rumour is shown only after the small-cell threshold | Radar | Simulated-data banner stays visible; k-anonymity reduces exposure but does not guarantee anonymity |
| 3:10–4:10 | **Analyst triage/verification**: select the issue, inspect evidence and coverage, record the reason, choose a response, and send/resolve the review | Radar + reviewer flow | No fake analyst identity. State exactly which actions are live |
| 4:10–4:50 | **Correction returns**: the analyst response and source arrive back in the original family channel; show the completed loop and its actual timestamps where available | Phone + loop diagram | If web follow-up remains manual, say so; never imply a response that was not sent |
| 4:50–5:30 | **Evidence and limitations**: actual eval, corpus size, synthetic/simulated data, privacy, known coverage gaps; show the research protocol and clearly label interviews/experiments as completed or pending | `eval/RESULTS.md` + evidence slide | No participant counts or impact claims until the studies are actually run |
| 5:30–6:10 | Deployment: on-premise, no GPU, no paid API required; close on the measured loop: "Dari sinyal keluarga, ke keputusan analis, kembali menjadi koreksi bersumber." | Architecture slide | Keep roadmap items out of the core demo; extension is optional backup footage, not a second feature tour |

**Backup plan for recording day:** pre-rendered voice MP3s; second phone as hotspot; recorded clips of every flow before 12 Nov; local server if hosting is flaky.

## C. Final pitch (10 min slot)

- 0:00–0:40 family problem and the closed-loop proposition
- 0:40–4:20 one live loop: voluntary family signal, honest answer, aggregate Radar, analyst triage, sourced correction returned
- 4:20–5:00 why this matters for Siber Sosial and how a unit could deploy it, without claiming access or partnership
- 5:00–5:30 evidence and credibility: sources, abstention, appeal, privacy, actual research status, and what we do not claim
- 5:30–10:00 Q&A

### Prepared Q&A
- **"Kenapa tidak pakai ChatGPT saja?"** Halio's proposed value is the integrated workflow: a bounded source corpus, explicit abstention, family-friendly correction, analyst handoff, and an on-premise deployment path. Do not claim that every general chatbot lacks these capabilities; show the working loop instead.
- **"Bukankah ini pengawasan warga?"** Signals are user-initiated and the Radar exposes aggregate trends with small-cell suppression. Rumour text appears only after ≥5 distinct reporters in the configured window and pseudonyms rotate daily. These controls reduce exposure; they do not guarantee anonymity or make private text "public by definition". Show `docs/PRIVACY.md` and the actual stored fields.
- **"Siapa yang menentukan benar/salah?"** Named fact-checkers and official sources. Halio only matches. When there is no source, it says so.
- **"Bagaimana kalau salah?"** Appeal button, human queue, the false-hoax metric is the one we optimise first, and verdicts fall back to "tidak yakin".
- **"Akurasinya berapa?"** Report `eval/RESULTS.md` numbers and say the test set is small and self-written. Then describe the plan for an independent test set.
- **"Apakah terbukti mengubah perilaku?"** Not yet. Accuracy-nudge and prebunking research informs the design, but Halio-specific interviews and human experiments remain pending until actually conducted. Show the protocol and never substitute intention-sharing results for real-world behaviour.
- **"Deteksi deepfake?"** Not claimed. We match the *claim* in the message to existing debunks.

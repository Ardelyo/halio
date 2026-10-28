# Demo Script

> **The submission video is built from code:** see `video/README.md`, the timed narration in `video/NASKAH.md`, and the brand rules in `video/BRAND.md`. The tables below remain the outline for the live final pitch.

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
| 0:00–1:00 | Story (A) | B-roll / slides | Persona stated |
| 1:00–1:30 | Problem + Siber Sosial framing: cognitive sovereignty, family as smallest unit of resilience, scams impersonating TNI AD | Slide | Avoid claiming "Siber Sosial" is official doctrine |
| 1:30–2:45 | **Flow 1**: forward the bansos message to the Telegram bot on a real phone → text answer, Halio Card, voice note | Phone screen recording | Real bot. Demo claims are in the corpus; say so |
| 2:45–3:30 | **Flow 1b**: TNI recruitment scam ("dijamin lulus, bayar 80 juta") → Terbukti salah + bit.ly link warning | Web app | — |
| 3:30–4:15 | **Flow 2 (honesty moment)**: unknown rumour → "Belum ada pemeriksaan, Halio tidak mau menebak" → tap "Tanya pemeriksa manusia" | Bot | Real, not mocked |
| 4:15–4:45 | **Flow 3**: true statement "BMKG mencatat gempa M5,1… tidak berpotensi tsunami" → *not* labelled hoax. Explain the core-claim guard and the eval (0 false-hoax on our test set, optimistic) | Web app + `eval/RESULTS.md` | Say the test set is self-written |
| 4:45–5:30 | **Flow 4**: extension on demo feed → "Perlu dicek?" badges, gambling banner blurred, popup "0 byte gambar dikirim" | Desktop | Demo feed is labelled "simulasi". No explicit images |
| 5:30–6:30 | **Flow 5**: Radar: categories ("Penipuan mencatut TNI" highlighted), techniques, trend, emerging rumour surfaced only after 5 distinct reporters; privacy panel | Radar | Simulated-data banner stays visible |
| 6:30–7:15 | Deployment: `docker compose up`, no GPU, no paid API; roadmap (WhatsApp, disaster mode, family weekly summary, voice-scam family code); close: "Ketahanan kognitif dimulai dari unit sosial terkecil: keluarga." | Terminal + slide | Roadmap items clearly labelled |

**Backup plan for recording day:** pre-rendered voice MP3s; second phone as hotspot; recorded clips of every flow before 12 Nov; local server if hosting is flaky.

## C. Final pitch (10 min slot)

- 0:00–0:45 story (shortened A)
- 0:45–4:00 live demo: hand a judge a phone with Telegram open (bot pinned), or ask a judge for any rumour and forward it. Then the honesty moment, then the Radar
- 4:00–5:00 why this matters for TNI AD (Siber Sosial monitoring, scams impersonating TNI, families of personnel) and how a unit deploys it
- 5:00–5:30 credibility: sources, three states, appeal, privacy, what we don't claim
- 5:30–10:00 Q&A

### Prepared Q&A
- **"Kenapa tidak pakai ChatGPT saja?"** Chatbots need the user to know to ask, don't flag proactively, don't restrict answers to verified Indonesian sources, and don't reliably say "not enough evidence". Halio is voice-first for parents, keeps no message history, and runs on-prem without a paid API.
- **"Bukankah ini pengawasan warga?"** No message is stored. The Radar holds counts only. Rumour text appears only after ≥5 distinct people sent it the same day (public by definition), and pseudonyms rotate daily. It cannot identify a person by design.
- **"Siapa yang menentukan benar/salah?"** Named fact-checkers and official sources. Halio only matches. When there is no source, it says so.
- **"Bagaimana kalau salah?"** Appeal button, human queue, the false-hoax metric is the one we optimise first, and verdicts fall back to "tidak yakin".
- **"Akurasinya berapa?"** Report `eval/RESULTS.md` numbers and say the test set is small and self-written. Then describe the plan for an independent test set.
- **"Deteksi deepfake?"** Not claimed. We match the *claim* in the message to existing debunks.

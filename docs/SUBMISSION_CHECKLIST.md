# Submission Checklist

Deadline: **15 Nov 2026, 23:59 WIB** (Rulebook §G). Internal target: **14 Nov 20:00 WIB**. Submit via the CODEPOLITAN platform (`codepolitan.com/dashboard/kartika-cyber-hackathon-2026`). One submission per team; updates allowed until the deadline; only the last one is judged.

## Registration (Rulebook §E)
- [ ] All members have active CODEPOLITAN accounts
- [ ] Team name, member data (max 3), WhatsApp number, address/province/city, occupation, institution
- [ ] Nama Karya: **Halio** · Deskripsi Karya (2–3 sentences, see below) · Kategori: **Siber Sosial**
- [ ] WNI confirmation + T&C accepted
- [ ] Joined the official WhatsApp group

> Deskripsi Karya (draft): *Halio adalah asisten cek pesan untuk keluarga Indonesia. Pengguna cukup meneruskan pesan meragukan lewat Telegram atau web, lalu menerima jawaban bersumber dalam bahasa sederhana, kartu yang bisa dibagikan, dan pesan suara. Bila belum ada pemeriksaan, Halio jujur tidak menebak. Agregat anonimnya membentuk Radar Ketahanan Kognitif untuk mendeteksi dini kampanye disinformasi dan penipuan yang mencatut TNI AD.*

## Deliverables (Rulebook §G)
| # | Item | Spec | Source in repo | Done |
|---|---|---|---|---|
| 1 | Link Karya | Public link judges can try | Hosted web URL + `t.me/<bot>` + GitHub repo link in README | [ ] |
| 2 | Thumbnail | 1200×630 px, JPG/PNG/WebP, ≤500 KB | `python scripts/make_thumbnail.py` → `docs/submission/thumbnail.jpg` | [ ] |
| 3 | Screenshots | Max 5 | 1) bot answer + card 2) web verdict 3) honest abstain 4) extension feed 5) Radar | [ ] |
| 4 | Video | ≤10 min, YouTube | Follow `docs/DEMO_SCRIPT.md` §B | [ ] |
| 5 | Slides | Features, architecture, tech, other info | Deck; export PDF too | [ ] |

## Rules compliance (Rulebook §G "Ketentuan Karya" & §N)
- [ ] Pre-existing work declared (`docs/THIRD_PARTY.md` §Declaration)
- [ ] All third-party libraries, APIs, models attributed (`docs/THIRD_PARTY.md`)
- [ ] No pornography, SARA, hate speech, illegal content anywhere (repo, video, slides, demo feed)
- [ ] No third-party personal data (fictional names, placeholder phone numbers only)
- [ ] No component violating others' IP (debunk corpus uses own-words summaries + links)

## Final verification (14 Nov)
- [ ] Open every submitted link in a private window on a phone and on a laptop
- [ ] Forward a fresh message to the bot from a non-team phone
- [ ] Radar loads; simulated-data banner visible
- [ ] Video plays, is ≤10:00, audio audible, captions readable
- [ ] Uptime monitor active through 24 Nov; no deploys 16–20 Nov

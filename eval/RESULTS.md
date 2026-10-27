# Halio offline evaluation

Test set: 32 hand-written items (16 paraphrases of known debunks, 12 true/unknown statements, 4 opinions/greetings). Written by the team, so results are optimistic. Not a benchmark.

Thresholds: match >= 0.4, unsure >= 0.26. Mode: retrieval only (no LLM, no ClaimReview).

| Metric | Value |
|---|---|
| False-hoax rate (true/unknown labelled 'terbukti salah') | **0%** (0/12) |
| Recall on paraphrased known hoaxes | 100% |
| Matched the wrong debunk | 0 |
| Correct abstain on true/unknown | 100% |
| Opinion/greeting detected | 100% |

## Per item

| ok | expected | status | reason | score | text |
|---|---|---|---|---|---|
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.424 | Bapak ibu, ada video Pak Prabowo bagi-bagi uang tunai buat rakyat, lan |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.56 | Daftar bantuan langsung tunai dari Presiden, cukup kirim KTP ke WhatsA |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.537 | INFO VALID!! Menteri keuangan umumkan bansos tunai, pendaftaran lewat  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.413 | Ada kenalan di kodam bisa bantu anak ibu lulus tes tamtama TNI AD, dij |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.553 | Jalur khusus masuk tentara, pasti lulus, bayar ke orang dalam |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.612 | Penerimaan bintara TNI AD tahun ini ada jalur titipan, hubungi saya, b |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.534 | Menurut BMKG akan terjadi gempa magnitudo 8,9 disertai tsunami tanggal |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.524 | WASPADA!!! gempa besar diprediksi terjadi minggu depan di pulau jawa,  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.451 | Prediksi gempa susulan lebih besar M9 akan datang dalam 3 hari |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.604 | Obat covid paling ampuh: air kelapa muda campur garam dan perasan jeru |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.519 | air klapa + garem + jeruk nipis bs nyembuhin corona, udh dibuktiin |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.569 | Selamat! Telkomsel XL Indosat bagi kuota gratis 50GB dalam rangka HUT  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.611 | Kominfo bagikan subsidi kuota internet gratis, daftar di tautan lalu b |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.608 | Jasa Marga kasih saldo e-toll gratis 100 ribu buat pengguna tol, klaim |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.575 | Hati-hati ada komplotan penculik anak naik mobil putih keliling sekola |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.59 | Waspada penculikan anak di kampung kita, pelaku menyamar jadi orang gi |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.394 | Pendaftaran rekrutmen TNI AD 2026 dibuka secara online dan tidak dipun |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.468 | BMKG mencatat gempa magnitudo 5,1 di selatan Jawa pagi ini, tidak berp |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.291 | Pemerintah menyalurkan bansos beras lewat kantor pos dan bank Himbara, |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.379 | Air kelapa mengandung elektrolit seperti kalium yang membantu menggant |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.36 | Jasa Marga memberlakukan diskon tarif tol 20 persen saat libur Natal |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.368 | Polisi menangkap pelaku penculikan anak di Bogor setelah laporan warga |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Harga cabai di pasar naik dua kali lipat karena musim hujan |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.321 | Minum air rebusan daun sirsak setiap hari bisa menyembuhkan kanker sta |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Vaksin terbaru mengandung chip untuk melacak masyarakat, sebarkan sebe |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Jembatan Suramadu akan ditutup total selama seminggu mulai besok |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Timnas Indonesia menang 2-0 tadi malam |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Bank akan memblokir semua rekening yang tidak aktif tiga bulan mulai J |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Selamat pagi keluarga, semoga hari ini penuh berkah. Amin |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Menurut saya pemerintah harus lebih memperhatikan petani |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Apa kabar semuanya? Sudah makan belum? |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Terima kasih atas doanya, mohon maaf lahir batin |

## Known limitations

- Same-topic TRUE statements score close to the threshold; that is why the 'tidak yakin' band exists.
- Retrieval is lexical; heavy paraphrase without shared words is missed (falls to 'belum ada pemeriksaan', which is safe).
- The T2 LLM step (HALIO_LLM=1) is not measured here; it may only downgrade or confirm with an exact quote.

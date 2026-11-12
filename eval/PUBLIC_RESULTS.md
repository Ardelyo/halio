# Evaluasi pada sampel publik: judul TurnBackHoax

> **Jenis:** Bukti · **Untuk:** juri dan pengembang · [Peta dokumen](../docs/README.md)

Sumber: dataset Hugging Face `Rifky/indonesian-hoax-news` (17.806 judul TurnBackHoax/Mafindo, rekaman 2022). Label diambil dari awalan judul. Tidak satu pun item dipakai untuk menulis korpus, aturan, atau ambang Halio. Data mentah tidak disalin ke repo; `python eval/eval_public.py` mengambilnya saat dijalankan. Mode: pencocokan lokal tanpa AI (sama dengan `eval/run_eval.py`).

**Cara membaca.** Ini judul artikel, bukan pesan berantai, jadi lebih sulit dan kurang alami daripada pemakaian nyata. Korpus Halio hanya 7 bantahan, jadi `[SALAH]` yang dikenali sedikit; itu angka **cakupan korpus**, bukan akurasi. Angka yang dijaga adalah **tuduhan palsu**: kabar benar yang dicap "terbukti salah".

## Tuduhan palsu (yang terpenting)

| Kelompok | Jumlah | Dicap "terbukti salah" | Tingkat | Batas atas 95% (Wilson) |
|---|---|---|---|---|
| `[BENAR]` (terverifikasi benar) | 467 | 0 | 0.0% | 0.8% |
| `[KLARIFIKASI]` (meluruskan hoaks) | 576 | 0 | 0.0% | 0.7% |
| **Gabungan** | **1043** | **0** | **0.0%** | **0.4%** |

## Sebaran jawaban Halio

| Jawaban | `[BENAR]` | `[KLARIFIKASI]` | `[SALAH]` (sampel) |
|---|---|---|---|
| terbukti_salah | 0 | 0 | 1 |
| tidak_yakin | 94 | 150 | 196 |
| belum_ada_pemeriksaan | 373 | 426 | 403 |
| sejalan_dengan_sumber | 0 | 0 | 0 |
| dilaporkan_media | 0 | 0 | 0 |

## Cakupan korpus pada hoaks (`[SALAH]`)

Dari **600** judul `[SALAH]` yang diambil merata dari dataset, Halio mengenali **1** (0.2%) sebagai "terbukti salah". Sisanya jatuh ke "tidak yakin" atau "belum ada pemeriksaan" (jujur, bukan menebak). Korpus kurasi sengaja kecil; di luar korpus, Halio memakai mesin bukti dan pencarian, yang tidak dijalankan pada evaluasi ini.

Bantahan yang paling sering cocok: `penculikan-anak-berantai` (1)

Hoaks yang salah diberi "sejalan dengan sumber" atau "dilaporkan media": **0** dari 600.

## Riwayat dan catatan integritas

Run pertama (12 Nov 2026) menemukan **1 judul** yang salah dicap "terbukti salah" (tampil pada dua label): *"BMKG Papua Mengklarifikasi Isu Akan Terjadi Tsunami di Papua"*. Pesan itu justru meluruskan hoaks, tetapi kata "mengklarifikasi" belum dikenali sebagai pelurusan. Pola pelurusan di `backend/halio/retrieval.py` diperluas (klarifikasi, meluruskan, menepis, menyangkal, dan sejenisnya), kasusnya ditambahkan ke `eval/testset.jsonl` dan `backend/tests/test_core.py`, lalu evaluasi dijalankan ulang: 0 tuduhan palsu. **Karena perbaikan dibuat setelah melihat sampel ini, hasil 0/1.043 tidak sepenuhnya independen untuk judul itu.** Rekaman 2022 ini juga belum menguji pesan berantai nyata.
## Keterbatasan

- Judul artikel bukan pesan berantai; hasil pada pesan nyata bisa berbeda.
- Rekaman 2022; banyak topik lama. Label berasal dari TurnBackHoax, bukan dari tim.
- Sampel `[SALAH]` diambil merata, bukan acak murni, dan dibatasi 600 item.
- Mode tanpa AI saja. Mesin bukti dan ClaimReview belum dievaluasi pada set ini.

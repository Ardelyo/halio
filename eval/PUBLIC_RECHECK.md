# Pemeriksaan ulang tuduhan palsu pada sampel publik TurnBackHoax

> **Jenis:** Bukti · **Untuk:** juri dan pengembang · dibuat otomatis oleh `eval/eval_public_recheck.py`

- Tanggal: 2026-11-13 22:18 UTC
- Commit yang diuji: `69d1020abe` (berkas backend/data bersih dari perubahan yang belum di-commit: **ya**)
- Sampel: 3700 judul dari `Rifky/indonesian-hoax-news` (halaman tersebar tiap 450 baris; 3 halaman gagal diunduh dan dilewati)
- Mode: pencocokan lokal tanpa AI dan tanpa cek tautan. Korpus: `data/debunks.json` apa adanya pada commit itu
- Protokol: kode dan korpus dibekukan sebelum skrip dijalankan; tidak ada penyetelan setelah melihat hasil

## Hasil

| Metrik | Nilai |
|---|---|
| Judul berlabel BENAR atau KLARIFIKASI | 197 |
| **Salah dicap "terbukti salah" (tuduhan palsu)** | **0** |
| Batas atas 95% (Wilson) tingkat tuduhan palsu | 1.91% |
| Judul berlabel SALAH | 2582 |
| SALAH yang dikenali "terbukti salah" (cakupan korpus, bukan akurasi) | 17 (0.7%) |

## Per status

| Label | Status | n |
|---|---|---|
| (tanpa label) | belum_ada_pemeriksaan | 384 |
| (tanpa label) | tidak_yakin | 112 |
| ACARA | belum_ada_pemeriksaan | 5 |
| ACARA | tidak_yakin | 3 |
| BENAR | belum_ada_pemeriksaan | 61 |
| BENAR | tidak_yakin | 18 |
| BERITA | belum_ada_pemeriksaan | 29 |
| BERITA | tidak_yakin | 12 |
| BERITA, EDUKASI | belum_ada_pemeriksaan | 2 |
| CLARIFICATION | belum_ada_pemeriksaan | 1 |
| DISINFOMASI | tidak_yakin | 1 |
| DISINFORMASI | belum_ada_pemeriksaan | 51 |
| DISINFORMASI | tidak_yakin | 14 |
| EDUKASI | belum_ada_pemeriksaan | 7 |
| EDUKASI | tidak_yakin | 4 |
| EVENT | belum_ada_pemeriksaan | 1 |
| FAKTA ATAU HOAKS | belum_ada_pemeriksaan | 3 |
| FAKTA ATAU HOAKS | tidak_yakin | 26 |
| FAKTA BICARA | belum_ada_pemeriksaan | 2 |
| FALSE | belum_ada_pemeriksaan | 18 |
| FALSE | tidak_yakin | 18 |
| FITNAH | belum_ada_pemeriksaan | 2 |
| HASUT+FITNAH | belum_ada_pemeriksaan | 1 |
| HOAKS | belum_ada_pemeriksaan | 83 |
| HOAKS | tidak_yakin | 27 |
| HOAX | belum_ada_pemeriksaan | 71 |
| HOAX | tidak_yakin | 28 |
| HOAX + HASUT | belum_ada_pemeriksaan | 1 |
| HOAX + HASUT | tidak_yakin | 1 |
| HOAX, HASUT | belum_ada_pemeriksaan | 1 |
| ISU | belum_ada_pemeriksaan | 1 |
| KLARIFIKASI | belum_ada_pemeriksaan | 98 |
| KLARIFIKASI | tidak_yakin | 20 |
| MISINFORMASI | belum_ada_pemeriksaan | 2 |
| MISINFORMASI | tidak_yakin | 1 |
| RILIS PERS | tidak_yakin | 1 |
| SALAH | belum_ada_pemeriksaan | 1710 |
| SALAH | terbukti_salah | 17 |
| SALAH | tidak_yakin | 855 |
| TOP 5 | belum_ada_pemeriksaan | 8 |

Ini judul artikel, bukan pesan berantai, jadi lebih sulit dan kurang alami daripada pemakaian nyata. Angka lama 0 dari 1.043 (`PUBLIC_RESULTS.md`) diukur dengan korpus 7 entri dan tidak dibuat ulang.

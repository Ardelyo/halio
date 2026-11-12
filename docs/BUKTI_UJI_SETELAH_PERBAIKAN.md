# Bukti Uji Setelah Perbaikan (kode lokal, lalu dideploy ke server publik)

> **Jenis:** Bukti · **Untuk:** juri dan pengembang · [Peta dokumen](README.md)

Tanggal: 10 Nov 2026. Melengkapi [BUKTI_UJI_DEMO.md](BUKTI_UJI_DEMO.md) (uji pada build publik `441f73e`, ada di PR #15). Semua angka di sini berasal dari kode cabang `fix/pra-submission-hardening` yang dijalankan lokal, mode `tanpa_ai` (pencocokan lokal tanpa web). **Dideploy ke server publik pada 10 Nov 2026 (build `e16d354-20261110-1151`); hasilnya ada di bagian terakhir.**

## Skenario 1 (calo TNI AD) sekarang 🔴
| # | Skenario | Build publik 7 Nov | Kode perbaikan |
|---|---|---|---|
| 1 | Calo/titipan TNI AD dengan kalimat ajakan di akhir | 🟠 skor 0,398 | 🔴 skor 0,44 |
| 2–7 | Bansos, gempa BMKG, air kelapa, kuota, e-toll, penculikan | 🔴 | 🔴 |
| 8 | Pesan benar pada topik rekrutmen | 🟠 | 🟠, naskah suara tidak lagi menyuruh menahan pesan |
| 9 | Kabar belum diperiksa | ⚪ | ⚪ |
| 10 | Tautan pendek dan domain tiruan | 🟠 + peringatan | 🟠 + peringatan |

## Uji tekanan baru (ditulis tim, tidak dipakai untuk menyetel apa pun sebelum dijalankan pertama kali)
Dua set kecil berisi pesan berkalimat banyak, seperti yang beredar di grup keluarga.

| Set | Sebelum | Sesudah |
|---|---|---|
| 16 pesan **benar** (berita, peringatan, klarifikasi pada topik yang sama dengan hoaks) dicap salah | 2 dari 15 (dua peringatan "hati-hati penipuan bansos" dan "Kodam menangkap calo") | **0 dari 16** |
| 10 parafrase **hoaks** baru (berkalimat ekor ajakan) dikenali dengan debunk yang benar | 8 dari 10 | **9 dari 10** |

Yang masih terlewat: "Mau anaknya jadi tentara? Ada orang dalam Kodam yang bisa jamin lulus Bintara, biaya 90 juta bisa dicicil…" menjadi ⚪ "belum ada pemeriksaan". Aman (tidak menuduh), tetapi Halio tidak mengenalinya di mode lokal. Di mode penuh, pencarian web membuka sumber; belum diuji untuk kalimat ini.

Catatan jujur: set ini ditulis setelah melihat kegagalan skenario 1, sehingga angka "sesudah" tidak independen sepenuhnya. Pengamannya adalah eval resmi: **0/32 dan 0/34 tuduhan palsu, recall tetap 100% dan 88%**, dengan satu label alasan berubah di `eval/RESULTS.md` (pernyataan benar Kodam kini `tampak_meluruskan`).

## Apa yang berubah di pencocokan lokal
1. Pesan yang memperingatkan hoaks ("hati-hati penipuan", "memakai video palsu", "jangan percaya calo", "menangkap calo") dikenali sebagai pelurusan, bukan hoaks.
2. Setiap kalimat klaim ikut dinilai, jadi kalimat ajakan di ekor tidak mengencerkan skor.
3. Dua kalimat yang baru cocok bila digabung tidak lagi dipecah menjadi dua klaim lemah.
4. Jawaban "tidak yakin" untuk pesan benar yang topiknya sama dengan hoaks tidak lagi berbunyi "lebih aman ditahan".
5. Radar menghitung kategori dan debunk hanya dari cek yang terbukti salah.

## Hasil di server publik setelah deploy (build `e16d354-20261110-1151`)
Diuji 10 Nov 2026 lewat `/api/check`, kedua mode, pesan buatan.

| Pemeriksaan | Hasil |
|---|---|
| 10 skenario, mode penuh dan tanpa AI | Skenario 1–7 🔴 di kedua mode (skenario 1 kini 🔴, `cocok_dengan_bantahan`); 8 🟠; 9 ⚪; 10 🟠 + peringatan tautan |
| Tuduhan palsu pada pesan benar | **0** |
| Header | `Content-Security-Policy` dan `X-Frame-Options: DENY` ada |
| Halaman `cek`, `radar`, `laporan`, `uji`, `coverage` | semuanya HTTP 200; Radar tanpa token HTTP 401 |
| `preflight.py` tanpa token bot | API, cek hoaks, kartu PNG, suara MP3, dan penguncian Radar PASS |
| Layanan | `halio-api` dan `halio-bot` `active`; sensor 23 feed tanpa galat |
| Latensi mode penuh | umumnya 4–9 detik; lonjakan sesekali 15–35 detik (variasi pencarian web/model). Tanpa AI: di bawah 1 detik |

Belum diuji setelah deploy: tampilan visual halaman di peramban sungguhan pada build publik (CSP sudah 0 pelanggaran di uji lokal), Telegram, panel Radar TNI AD (butuh token Radar), dan `eval_live.py`.

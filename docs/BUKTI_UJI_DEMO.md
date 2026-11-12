# Bukti Uji Demo pada Build Publik

> **Jenis:** Bukti · **Untuk:** juri dan pengembang · [Peta dokumen](README.md)

**Tanggal:** 10 Nov 2026 · **Server:** `https://34-101-109-211.sslip.io` · **Build:** `441f73e-20261107-2316` (`/health`: `llm:true`, `media:true`) · **Kanal:** API `/api/check` dengan `channel=demo`, jadi baris ini tercatat sebagai data simulasi di Radar · **Pesan:** semuanya buatan, nama dan nomor fiktif.

Setiap skenario dijalankan dua kali: mode penuh (AI aktif, mesin bukti v2) dan `mode=tanpa_ai` (tanpa model). Angka di bawah adalah keluaran server apa adanya.

## Hasil

| # | Skenario | Harapan | Mode penuh | Tanpa AI | Status |
|---|---|---|---|---|---|
| 1 | Calo/titipan rekrutmen TNI AD (parafrase baru, dengan kalimat ekor "Hubungi Pak Budi segera, kuota terbatas") | 🔴 | 🟠 `mirip_tapi_tidak_sama`, skor 0,398 | 🟠 sama | **GAGAL** (lihat analisis) |
| 1b | Calo TNI AD, **contoh bawaan web** ("Ada kenalan di kodam … dijamin lulus asal siapkan uang 80 juta …") | 🔴 | 🔴 `cocok_dengan_bantahan`, skor 0,553 | 🔴 sama | LULUS |
| 2 | Bansos deepfake Presiden | 🔴 | 🔴 skor 0,866; sumber Katadata (Bareskrim) | 🔴 | LULUS |
| 3 | Prediksi gempa "menurut BMKG" | 🔴 | 🔴 skor 0,67; sumber siaran pers BMKG | 🔴 | LULUS |
| 4 | Air kelapa + jeruk nipis + garam sembuhkan COVID-19 | 🔴 | 🔴 `dibantah_resmi`: mesin bukti membuka 7 halaman, 3 relevan, mengutip jalahoaks.jakarta.go.id | 🔴 dari korpus | LULUS |
| 5 | Kuota gratis 50GB "dari Kominfo" | 🔴 | 🔴 skor 0,614; sumber MerahPutih | 🔴 | LULUS |
| 6 | Saldo e-toll gratis Jasa Marga | 🔴 | 🔴 skor 0,806; sumber Kompas TV | 🔴 | LULUS |
| 7 | Penculikan anak berantai | 🔴 | 🔴 skor 0,695; sumber RRI Cek Fakta | 🔴 | LULUS |
| 8 | Pesan **benar** pada topik yang sama (pendaftaran Tamtama online, tanpa biaya) | bukan 🔴 | 🟠 `inti_klaim_tidak_ada` | 🟠 | LULUS, dengan catatan |
| 9 | Kabar yang belum diperiksa (pasar fiktif ditutup) | "tidak mau menebak" | ⚪ `tidak_ada_sumber_relevan`: "Halio mencari di web dan membuka 2 halaman, tetapi tidak menemukan laporan …" | ⚪ `tidak_ada_bantahan` | LULUS |
| 10 | Tautan pendek + domain tiruan (`bit.ly/…`, `tniad-rekrutmen-resmi.id-daftar.com`) | peringatan tautan | 🟠 + dua peringatan: bit.ly "tidak bisa dibuka (kode 404)", domain tiruan "nama situs ini tidak ada" | 🟠 + peringatan sama | LULUS |

Latensi mode penuh: 3,2–9,4 detik per cek. Tanpa AI: di bawah 0,5 detik.

**Tuduhan palsu: 0.** Pesan benar (skenario 8) tidak dicap salah pada kedua mode.

## Analisis skenario 1 (calo TNI AD), untuk keputusan pemilik

Penyebabnya ada dua, dan keduanya sudah diverifikasi:

1. **Skor leksikal tepat di bawah ambang.** Kalimat yang dipilih untuk diperiksa memuat ekor "Hubungi Pak Budi segera, kuota terbatas" sehingga skornya 0,398 (ambang 0,40). Tanpa kalimat ekor itu, pesan yang sama mendapat 0,44 dan 🔴. Contoh bawaan web mendapat 0,553 dan 🔴.
2. **Mesin bukti web tidak pernah membuka sumber kurasi entri ini.** `pipeline.check` hanya memakai sumber kurasi berjenis `resmi` atau `cek_fakta` sebagai titik awal pencarian. Kedua sumber `rekrutmen-tni-ad-berbayar` berjenis `media`, sehingga halaman Kodam XV/Pattimura di Investortrust (yang eksplisit menyatakan "tanpa titipan, tanpa jaminan lulus dengan uang") tidak dibuka. Pencarian web membuka 5 halaman lain dan tidak menemukan yang relevan.

**Yang sudah dicoba dan tidak dipakai:** menambah varian kalimat dari pernyataan Kodam ke salinan korpus. Skornya justru turun ke 0,386 karena bobot kata bergeser. Eval tetap 0 tuduhan palsu, tetapi skenario 1 tidak membaik. Korpus di repo tidak diubah.

**Usulan (belum dikerjakan, perlu persetujuan):**
- **(a) Untuk demo dan video sebelum 15 Nov:** pakai contoh bawaan web (skenario 1b) atau kalimat tanpa ekor ajakan. Ini tidak mengubah kode dan hasilnya 🔴 pada kedua mode.
- **(b) Tambahkan sumber resmi TNI AD** (`jenis: "resmi"`) ke entri ini. Mesin bukti akan membukanya sebagai titik awal. Pemilik perlu memilih URL resmi yang tegas (lihat [VERIFIKASI_KORPUS.md](VERIFIKASI_KORPUS.md) temuan 1). Setelah itu jalankan `eval/run_eval.py` sebelum dan sesudah. Eval offline tidak memakai web, jadi uji juga di server dengan `scripts/eval_live.py`.
- **(c) Pascafreeze:** sertakan sumber kurasi `media` sebagai titik awal mesin bukti, dan nilai kecocokan per kalimat agar kalimat ajakan di ekor tidak menurunkan skor. Keduanya mengubah perilaku dan butuh eval penuh.
- **Jangan menurunkan ambang** untuk menutup kasus ini. Pesan benar pada skenario 8 punya skor leksikal 0,567, lebih tinggi daripada pesan hoaks; yang menahannya adalah penjaga inti klaim, bukan ambang.

## Catatan skenario 8
Pesan benar tidak dicap salah, tetapi naskah suaranya berbunyi "Pesan ini mirip dengan kabar bohong yang pernah beredar … Lebih aman ditahan dulu". Untuk pesan yang benar, kalimat ini bisa membuat juri bertanya. Jangan memakai skenario 8 sebagai contoh "pesan benar" di video. Contoh yang lebih tepat adalah berita dari media dikenal (🔵) seperti di `docs/DEPLOY_UPDATE.md` §E.

## Catatan mesin bukti web
Pada 6 dari 7 hoaks, mesin bukti v2 membuka 4–8 halaman tetapi tidak menemukan kutipan relevan. Vonis 🔴 berasal dari korpus kurasi, dan web tidak menurunkannya (sesuai rancangan: bantahan kurasi hanya diturunkan oleh bukti yang bertentangan). Hanya skenario 4 yang dikuatkan oleh bukti web baru (jalahoaks.jakarta.go.id).

## Yang belum diuji (butuh pemilik)
| Uji | Alasan | Perintah/tindakan |
|---|---|---|
| Telegram, 10 skenario yang sama + `/tanpaai` | Butuh akun Telegram uji | Teruskan pesan di tabel ke `@halioid_bot` dari ponsel non-tim, lalu catat hasilnya di sini |
| `scripts/eval_live.py --news 10 --hoax 10` | Butuh ADC di VM | Perintah di `docs/DEPLOY_UPDATE.md` §E |
| `scripts/preflight.py` lengkap | Butuh `TELEGRAM_BOT_TOKEN` dan `HALIO_CHANNEL_KEY` | Dari mesin tim: `HALIO_API_URL=https://34-101-109-211.sslip.io python scripts/preflight.py`. Dari sini, tanpa token: API, cek hoaks, kartu PNG (86 KB), suara MP3 (79 KB), dan Radar menolak tanpa token semuanya **PASS**; pemeriksaan token bot **FAIL** karena token sengaja tidak dibaca |
| Build dengan perubahan Track B | Belum dideploy | Ulangi tabel ini setelah deploy |

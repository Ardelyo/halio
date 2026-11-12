# Evaluasi Radar untuk TNI AD: Berfungsi dan Bermanfaatkah?

> **Jenis:** Bukti · **Untuk:** juri dan analis · [Peta dokumen](README.md)

Tanggal: 10 Nov 2026. Dijalankan lokal pada kode cabang `fix/pra-submission-hardening` dengan **data nyata** dari 23 feed publik (sensor dijalankan sungguhan) dan **data simulasi** dari `scripts/seed_demo.py` untuk bagian cek warga. Tidak ada cek warga nyata yang tercatat di mana pun, jadi bagian itu hanya dibuktikan berfungsi, belum terbukti bermanfaat.

Radar punya dua sumber yang berbeda sifatnya. Keduanya dinilai terpisah.

## 1. Sensor dan Brief harian TNI AD (data nyata)

**Berfungsi?** Ya.

| Pemeriksaan | Hasil |
|---|---|
| 23 feed dipoll sekali | 23 berhasil, 0 galat, 1.322 item baru |
| Item yang cocok topik TNI AD/pertahanan | 55 dari 1.322 (40 dari feed resmi TNI AD/Kemhan, 15 dari media dan cek fakta) |
| Narasi (klaster judul mirip) | 51 |
| Narasi dengan tanda disinformasi | 2: "[SALAH] Panglima TNI Sebut Komnas HAM sebagai Musuh dalam Selimut" (dimuat CekFakta.com dan TurnBackHoax) dan "Ragam Hoaks Menerpa TNI, Simak Faktanya" (Liputan6 Cek Fakta) |
| Tampilan Radar | Brief, konteks resmi, dan banner data simulasi tampil benar (dicek di Edge headless) |

**Kesalahan yang ditemukan dan diperbaiki dalam evaluasi ini:**
1. Label pemeriksa fakta `[SALAH]` tidak dikenali sebagai sinyal hoaks, sehingga narasi paling penting tidak berlabel "kata hoaks/penipuan".
2. Tiga investigasi Telusur (yang memakai biaya model) bisa terpakai untuk rilis rutin seperti "Majalah Palagan Edisi September 2026". Sekarang hanya narasi yang punya sinyal (kata hoaks, pemeriksa fakta, atau dua sumber atau lebih) yang ditelusuri. Rilis resmi rutin ditampilkan terpisah sebagai "Konteks resmi, tidak ditelusuri".
3. Presisi filter topik: 3 dari 15 berita media yang cocok salah sasaran (Menteri Pertahanan AS dan Hegseth). Sekarang ditolak bila ada kata asing dan tidak ada penanda Indonesia di judul. Dari 29 item berkata militer yang tidak cocok, tidak ada yang jelas terlewat dan relevan (hanya Polri, gelar pahlawan, militer asing); satu cek fakta tentang Polisi Militer dan Seskab bisa dianggap batas.

**Bermanfaat?** Sebagian, dan dengan batas yang jelas:
- **Manfaat nyata:** analis tidak perlu membaca ~1.300 judul per dua hari. Brief menyaring ke 2 narasi bertanda dan 6 rilis resmi, dengan tautan ke setiap judul. Untuk narasi bertanda, Telusur (bila AI aktif) menyusun laporan bukti.
- **Batas yang harus dinyatakan terus terang:** brief ini bersifat **turunan**. Ia menaikkan apa yang sudah dilabeli pemeriksa fakta atau dimuat banyak media. Halio **belum mendeteksi hoaks TNI AD sebelum pemeriksa fakta**. Pada contoh hari ini, dua narasi bertanda berasal dari cek fakta yang sudah terbit.
- **Cakupan:** hanya feed publik. WhatsApp privat, Meta, TikTok, dan X adalah titik buta yang tercantum di halaman Cakupan.
- **Volume rendah:** 2 narasi bertanda dalam 48 jam. Itu realistis, bukan kekurangan, tetapi di demo bisa tampak sepi. Siapkan penjelasannya.
- Telusur untuk brief membutuhkan `HALIO_LLM=1`. Tanpa AI, brief tetap tersusun tetapi tanpa penelusuran (tertulis "Belum ditelusuri").

## 2. Radar dari cek warga (data simulasi)

**Berfungsi?** Ya, dan satu klaim di README dulu tidak didukung.

| Pemeriksaan | Hasil |
|---|---|
| Hitungan per kategori dan per debunk | Benar; sekarang hanya cek yang terbukti salah dihitung (sebelumnya pesan benar yang mirip hoaks rekrutmen ikut menaikkan "Penipuan mencatut TNI") |
| Kabar baru (k-anonimitas) | 1 kabar tampil, 3 di bawah ambang disembunyikan |
| Sel kecil | Angka di bawah 3 disamarkan menjadi "<3" |
| Banner data simulasi | Tampil di server sungguhan bila ada baris simulasi |
| **"Lonjakan penipuan yang mencatut TNI AD"** (klaim README) | **Dulu tidak ada.** Yang ada hanya total per kategori. Sekarang ada panel "Penipuan yang mencatut TNI AD": cek terbukti salah per hari, rata-rata hari sebelumnya, dan status "Naik" bila hari ini minimal 3 cek dan dua kali rata-rata. 2 tes mencakup lonjakan dan batas sel kecil |

**Bermanfaat?** **Belum terbukti.** Radar ini hanya berguna bila banyak keluarga memakai Halio. Pada saat ini tidak ada cek warga nyata di server, sehingga semua angka di panel ini adalah data simulasi dan diberi label. Kegunaan yang bisa diklaim jujur: rancangan, privasi (agregat, k-anonimitas, tanpa profil individu), dan mekanisme deteksi lonjakan yang diuji. Yang tidak bisa diklaim: bahwa Radar mendeteksi kampanye nyata.

Catatan metode: ambang "naik" (3 cek dan dua kali rata-rata) adalah pilihan kami, belum dikalibrasi dengan data nyata.

## 3. Rekomendasi untuk demo

1. Buka **Brief harian** dengan topik TNI AD. Tunjukkan narasi bertanda dengan label `[SALAH]`, lalu laporan Telusur-nya (butuh AI aktif di server).
2. Buka **Ringkasan** dan jelaskan panel TNI AD sebagai simulasi: banner kuning di atas halaman sudah menyatakannya. Jangan menyebut data itu sebagai kejadian nyata.
3. Katakan terus terang: "Radar bermanfaat bila dipakai banyak keluarga. Sekarang kami membuktikan mekanismenya, bukan skalanya."
4. Hindari klaim "mendeteksi lebih awal dari pemeriksa fakta".

## 4. Yang belum diuji
- Brief dengan Telusur aktif pada narasi bertanda (butuh server dengan Vertex AI; tidak dijalankan di evaluasi ini).
- Perilaku sensor selama berhari-hari (kestabilan feed, feed yang basi). Halaman Cakupan menunjukkannya, tetapi evaluasi ini hanya satu kali polling.
- Kalibrasi ambang lonjakan dengan data warga nyata.

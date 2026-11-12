# Rencana Penataan Dokumen

> **Jenis:** Panduan · **Untuk:** tim dan kontributor · [Peta dokumen](README.md)

Dokumen ini menjelaskan bagaimana dokumentasi Halio ditata, mengapa ditata begitu, dan aturan agar tetap rapi.

## Masalah yang ditemukan

| Masalah | Dampak bagi pembaca |
|---|---|
| 30 berkas di satu folder tanpa urutan baca | Juri tidak tahu harus mulai dari mana |
| Status dokumen tidak jelas: mana keadaan sekarang, mana catatan lama | Angka lama (mis. jumlah tes) terbaca seperti angka terkini |
| Jumlah keadaan vonis tertulis tiga, empat, dan lima di tempat berbeda | Pembaca ragu mana yang benar |
| README panjang dan datar: tabel, daftar, dan penjelasan bercampur | Pesan utama tenggelam |
| Dokumen strategi internal (riset agar menonjol, peta kompetitor, rencana unggul, rencana proyek, analisis dan rencana Radar) ikut terbit di repo publik | Memperlihatkan dapur internal, bukan karya; sebagian memuat angka dan tenggat usang |

## Keputusan

**1. Jalur berkas tidak dipindahkan.** Halaman situs yang sudah dideploy menaut ke `docs/PRIVACY.md`, `eval/RESULTS.md`, dan `data/debunks.json` di GitHub. Memindahkannya akan memutus tautan itu di server publik selama penjurian (16–20 Nov, tidak ada deploy). Penataan dilakukan lewat navigasi dan standar penulisan, bukan lewat folder baru.

**2. Setiap dokumen punya baris kepala** tepat di bawah judul: *Jenis* dan *Untuk*. Pembaca langsung tahu status dan sasarannya.

| Jenis | Artinya |
|---|---|
| Rujukan | Menggambarkan keadaan sekarang. Dijaga mutakhir; bila kode berubah, dokumen ikut diubah |
| Bukti | Hasil uji pada tanggal dan build yang disebut di dalamnya. Tidak diubah setelahnya, kecuali untuk menambah hasil baru |
| Panduan | Langkah kerja untuk menjalankan atau memperbarui sesuatu |
| Catatan bertanggal | Rencana atau riset saat ditulis. Angkanya riwayat, bukan keadaan sekarang |

**3. Dokumen strategi internal dihapus** dari pohon kerja (RESEARCH_STANDOUT, COMPETITORS, PLAN_UNGGUL, PROJECT_PLAN, PLAN_RADAR, ANALISIS_RADAR_DAN_TNI). Dokumen yang tersisa menjelaskan karya itu sendiri: cara kerja, bukti, dan batasnya. Riwayat git masih menyimpan versi lama; menghapusnya dari riwayat memerlukan penulisan ulang riwayat dan hanya dilakukan bila pemilik memintanya.

**4. Tiga jalur baca** di [peta dokumen](README.md), sesuai siapa pembacanya: juri, pengembang, dan analis atau satuan pengguna.

**5. README sebagai halaman depan**, bukan gudang tautan: masalah, solusi, cara kerja, lima keadaan jawaban, bukti, batas, lalu cara menjalankan. Detail ada di dokumen lain.

## Aturan perawatan

1. Satu istilah, satu arti. Lima keadaan jawaban selalu ditulis: Terbukti salah, Sejalan dengan sumber, Dilaporkan media, Halio tidak yakin, Belum ada pemeriksaan.
2. Angka diubah di sumbernya dulu (`eval/RESULTS.md`, `data/debunks.json`, dokumen bukti), baru di README dan dokumen lain.
3. Jangan memindahkan `docs/PRIVACY.md` dan berkas lain yang ditaut dari `web/`. Cek dengan `git grep "github.com/Ardelyo/halio/blob" -- web` sebelum memindahkan apa pun.
4. Dokumen baru wajib punya baris kepala dan didaftarkan di [peta dokumen](README.md).
5. Kalimat pendek, satu gagasan per kalimat, bahasa sehari-hari. Hindari kata yang tidak bisa dibuktikan ("canggih", "revolusioner", "terdepan").

## Pemeriksaan sebelum menggabung perubahan dokumen

- [ ] Tautan relatif Markdown tidak ada yang rusak.
- [ ] `python eval/run_eval.py` tidak mengubah `eval/RESULTS.md` (CI memeriksanya).
- [ ] Angka yang diubah sudah diubah di sumbernya.
- [ ] Baris kepala ada dan jenisnya benar.

# Recall bersih pada judul `[SALAH]` TurnBackHoax dalam cakupan korpus

Dataset `Rifky/indonesian-hoax-news` (rekaman 2022, label oleh Mafindo), mode lokal tanpa AI, korpus 35 entri bantahan. Pemilihan dalam cakupan memakai daftar kata kunci tetap di `eval/eval_public_scope.py`. **Judul = headline, bukan pesan berantai.**

- Judul `[SALAH]` unik di seluruh dataset: **7258**; dalam cakupan kata kunci: **636**
- Dikenali `terbukti_salah`: **10** (1.6%)
- Sebaran: tidak_yakin 329, belum_ada_pemeriksaan 297, terbukti_salah 10

Kata kunci cakupan itu longgar (mis. `gempa`, `paket`), jadi banyak judul yang cocok kata tetapi bukan topik penipuan yang dibantah korpus; angka ini batas bawah yang konservatif, bukan akurasi. Halio sengaja memilih diam daripada menebak.

## Yang dikenali: dinilai manusia, benar topiknya?

| Judul | Bantahan yang cocok | Skor | Topik benar? |
|---|---|---|---|
| Pesan WhatsApp Bantuan BPJS Kesehatan Sebesar Rp75 Juta | `bantuan-bpjs-puluhan-juta` | 0.497 | ya |
| Tautan 50 GB Kuota Gratis dari WhatsApp | `kuota-gratis-operator` | 0.414 | ya |
| Campuran Air Kelapa Muda, Jeruk Nipis, Garam, dan Madu dapat Mengobati Covid-19 | `air-kelapa-garam-obat` | 0.839 | ya |
| Campuran Air Kelapa Muda, Jeruk Nipis dan Garam dapat Menyembuhkan Covid-19 | `air-kelapa-garam-obat` | 1.0 | ya |
| Konsumsi Campuran Air Kelapa, Jeruk Nipis, Garam dan Madu Dapat Menyembuhkan Covid-19 | `air-kelapa-garam-obat` | 0.862 | ya |
| Link Untuk Mendapatkan 35 GB Kuota Gratis dari Operator | `kuota-gratis-operator` | 0.493 | ya |
| Daun Sisik Naga Dapat Menyembuhkan Kanker Payudara | `herbal-sembuhkan-semua-penyakit` | 0.474 | ya |
| Air Kelapa Muda, Jeruk Nipis, dan Garam Obat Covid-19 | `air-kelapa-garam-obat` | 0.784 | ya |
| “Penculikan anak remaja, diambil organnya & mayatnya setelah dijahit dibuang kekali depan Season City” | `penculikan-anak-berantai` | 0.425 | ya |
| “penculikan bayi di bangil, penculik kabur pakai mobil elf warna hitam” | `penculikan-anak-berantai` | 0.415 | ya |

**Penilaian topik:** kesepuluh judul dinilai oleh pembuat skrip dan seluruhnya sesuai topik bantahan yang cocok (10 dari 10). Ini penilaian satu orang, bukan dua penilai independen.

## Cara membaca dengan jujur

- **Cakupan rendah (10 dari 636, 1,6%)**: korpus 35 entri sengaja sempit (penipuan, APK, bansos, catut TNI AD). Judul TurnBackHoax 2022 didominasi COVID dan politik. Halio diam atau menjawab "tidak yakin" pada sisanya, bukan menebak. Angka ini adalah batas bawah, bukan akurasi.
- **Ketepatan tinggi pada yang dikenali**: 10 dari 10 sesuai topik, dan pada 1.043 judul benar/klarifikasi tidak ada satu pun dicap hoaks ([PUBLIC_RESULTS.md](PUBLIC_RESULTS.md)).
- **Tidak sepenuhnya independen**: entri `air-kelapa-garam-obat` dan `kuota-gratis-operator` disusun dari sumber cek fakta yang sejenis (Liputan6/MerahPutih), dan `bantuan-bpjs-puluhan-juta` ditulis setelah melihat judul klarifikasi Komdigi untuk klaim yang sama. Dataset 2022 itu sendiri tidak dipakai menyetel apa pun.

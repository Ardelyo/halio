# Halio Telusur: hasil evaluasi hidup (2026-11-07T08:52)

Model `gemini-3.5-flash-lite`, web dan Google Search sungguhan. 8 klaim hoaks, 10 judul berita.

| Ukuran | Nilai |
|---|---|
| Tuduhan palsu (berita dicap terbukti salah) | **0 / 10** |
| Hoaks yang keluar hijau | **0 / 8** |
| Waktu p50 / p90 | 38 s / 54 s |
| Halaman dibuka (rata-rata) | 38 |
| Kalimat laporan ditulis / dibuang pemeriksa | 50 / 5 |
| Kemunculan paling awal ditemukan | 18 / 18 |
| Galat | 0 |

Status hoaks: tidak_yakin 5, belum_ada_pemeriksaan 2, terbukti_salah 1

Status berita: belum_ada_pemeriksaan 8, tidak_yakin 2

| Set | Status | Detik | Dibuka | Bukti | Asal | Klaim |
|---|---|---|---|---|---|---|
| hoax | tidak_yakin | 86.4 | 46 | 20 | 2024-06-22 | Video Presiden Prabowo dan Menteri Keuangan membagikan bantuan tunai, daftar lewat nomor W |
| hoax | belum_ada_pemeriksaan | 48.2 | 37 | 4 | 2012/12/18 | Ada jalur khusus masuk TNI AD dijamin lulus dengan membayar sejumlah uang lewat orang dala |
| hoax | tidak_yakin | 33.8 | 48 | 20 | 2019-02-19 | Akan terjadi gempa besar dan tsunami pada tanggal tertentu menurut prediksi BMKG |
| hoax | terbukti_salah | 29.7 | 47 | 20 | 2021-07-07 | Campuran air kelapa muda, jeruk nipis, dan garam bisa menyembuhkan COVID-19 |
| hoax | tidak_yakin | 39.5 | 41 | 20 | 2025-01-25 | Operator seluler dan pemerintah membagikan kuota internet gratis puluhan GB, klik tautan d |
| hoax | tidak_yakin | 45.4 | 37 | 20 | 2025-01-22 | Jasa Marga membagikan saldo e-toll gratis, klik tautan untuk klaim |
| hoax | tidak_yakin | 38.4 | 50 | 20 | 2017/03/08 | Waspada penculikan anak, komplotan penculik berkeliaran di sekolah dan kampung, sebarkan k |
| hoax | belum_ada_pemeriksaan | 41.1 | 56 | 19 | 2026-04-30 | Kumpulan Hoaks Seputar Pajak, Simak Faktanya |
| news | belum_ada_pemeriksaan | 35.8 | 32 | 20 | 2026-10-20 | Eks Napiter yang Dibekuk di Solo Disebut Dalang Pembakaran Warung Mi Babi Sukoharjo |
| news | belum_ada_pemeriksaan | 53.9 | 38 | 20 | 2026-11-06 | Paguyuban Brimob Puji Ketegasan Kapolri Tindak Listyo dkk di Kasus Penyadapan |
| news | belum_ada_pemeriksaan | 45.5 | 45 | 1 | 2026-02-28 | Trump Says US Could Become an Occupying Force in Iran |
| news | tidak_yakin | 38.6 | 33 | 6 | 2021-10-26 | Iran Bantah Distribusi Tablet Yodium Terkait Ancaman Serangan AS |
| news | belum_ada_pemeriksaan | 38.2 | 21 | 0 | 2026-08-28 | Preview Bundesliga: RB Leipzig vs Augsburg, Misi Bangkit Die Roten Bullen |
| news | tidak_yakin | 36.7 | 28 | 20 | 2026-11-06 | Borneo FC vs PSM Makassar: Ambisi Pesut Etam Jaga Dominasi Kandang |
| news | belum_ada_pemeriksaan | 38.1 | 29 | 19 | 2023-01-08 | Satelit NASA Swift Jatuh ke Bumi, Masuk Atmosfer di Wilayah Sumatera Utara |
| news | belum_ada_pemeriksaan | 46.0 | 32 | 7 | 2026-11-05 | Livin’ MARKT: Destinasi Belanja Produk Lifestyle dengan Lebih dari 250 Brand Lokal |
| news | belum_ada_pemeriksaan | 28.4 | 26 | 10 | 2026-11-06 | Dari Akar Rumput, 12 Inovasi Terbaik GBIC 2026 Siap Bawa Perubahan |
| news | belum_ada_pemeriksaan | 36.1 | 31 | 14 | 2025-03-11 | Lebih dari 400.000 pekerja industri Jerman ikuti aksi protes upah |

Catatan jujur: set hoaks sebagian berasal dari judul artikel cek fakta, sehingga pencarian sering menemukan artikel itu sendiri;
ini mengukur jalur kerja (cari, buka, kutip, nilai, putuskan), bukan akurasi independen.

## Bacaan jujur atas hasil ini (ditulis 7 Nov 2026)
- **Aman:** 0 tuduhan palsu pada 10 berita, 0 hoaks yang keluar hijau. Pemeriksa kalimat membuang 5 dari 50 kalimat (10%): validator bekerja.
- **Lemah dalam memvonis:** hanya 1 dari 8 hoaks keluar 🔴; 5 keluar 🟠 ("dibantah untuk versi yang mirip"), 2 ⚪. Hoaks calo
  rekrutmen TNI AD ("jalur khusus dijamin lulus dengan membayar") keluar ⚪: celah penting untuk konteks TNI AD.
- **Set hoaks hanya 8** (korpus 7 entri + 1 judul cek fakta dari sensor); bukan 10 seperti yang diminta.
- **"Asal" 18/18 perlu dibaca hati-hati:** untuk berita biasa, halaman tertua yang ditemukan kadang membahas peristiwa lama yang
  mirip (mis. 2021 untuk berita Iran 2026), bukan kemunculan kabar yang sama. Laporan menyebutnya "kemunculan paling awal yang
  ditemukan", bukan asal-usul pasti.
- Uji ini berjalan sebelum perbaikan normalisasi tanggal (lihat "2012/12/18" di atas); perbaikan sudah di-deploy setelahnya.

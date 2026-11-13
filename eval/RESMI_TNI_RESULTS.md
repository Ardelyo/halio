# Uji tuduhan palsu pada rilis resmi TNI dan Kemhan

> **Jenis:** Bukti · **Untuk:** juri dan pengembang · dibuat otomatis oleh `eval/eval_resmi_tni.py`

- Tanggal: 2026-11-13 22:54 UTC
- Commit yang diuji: `4b829e7046` (berkas backend, data, skrip, dan daftar tautan bersih dari perubahan yang belum di-commit: **ya**)
- Rilis: 27 diuji dari 27 di daftar (0 gagal diunduh)
- Daftar rilis dipilih sebelum Halio dijalankan pada rilis itu, dari pencarian di situs resmi (`tni.mil.id`, `ppid.tniad.mil.id`, `kemhan.go.id`). Tidak ada rilis yang dibuang atau diganti setelah melihat hasil
- Pesan uji: judul + paragraf pembuka (maks. 600 karakter). Mode: pencocokan lokal tanpa AI dan tanpa cek tautan, korpus `data/debunks.json` apa adanya
- Semua rilis ini bukan hoaks. Maka setiap "terbukti salah" dihitung tuduhan palsu dan dilaporkan di bawah, tidak disetel ulang

## Hasil

| Metrik | Nilai |
|---|---|
| **Rilis resmi yang salah dicap "terbukti salah"** | **0 dari 27** |
| Batas atas 95% (Wilson) | 12.5% |
| Tidak yakin | 12 |
| Belum ada pemeriksaan | 15 |
| Alasan "tampak meluruskan" (penjaga klarifikasi bekerja) | 1 |
| **Skor leksikal di atas ambang vonis (0.4) tetapi tidak dicap salah** (ditahan penjaga inti klaim) | **3 dari 27** |

## Hampir salah tuduh (dicatat terbuka)

Skor kemiripan kata terhadap satu bantahan melewati ambang vonis, tetapi Halio tidak memvonis karena inti klaim palsu (mis. permintaan bayar) tidak ada pada rilis. Artinya perlindungan pada jenis teks ini bergantung pada penjaga itu, bukan pada skor.

| Skor | Bantahan terdekat | Status akhir | Judul |
|---|---|---|---|
| 0.402 | rekrutmen-tni-ad-berbayar | tidak_yakin (beberapa_klaim) | Pendaftaran Calon Bintara PK TNI AD Reguler Pria/Wanita dan Keahlian Pria TA. 2024 Telah R |
| 0.504 | rekrutmen-tni-ad-berbayar | tidak_yakin (beberapa_klaim) | PENERIMAAN CALON BINTARA (CABA) DAN CALON TAMTAMA (CATA) TNI AD GELOMBANG I - TA 2022 |
| 0.451 | rekrutmen-tni-ad-berbayar | tidak_yakin (beberapa_klaim) | Kodim 0624/Kab. Bandung Gelar Sosialisasi Penerimaan Prajurit TNI AD Di SMK Yadika |

## Per rilis

| Kategori | Status | Alasan | Skor | Judul |
|---|---|---|---|---|
| klarifikasi | tidak_yakin | beberapa_klaim | 0.334 | [Klarifikasi TNI Terkait Hoax Penetapan Masa Dinas Personel TNI](https://tni.mil.id/view-232317-klarifikasi-tni-terkait-hoax-penetapan-masa-dinas-personel-tni.html) |
| klarifikasi | belum_ada_pemeriksaan | beberapa_klaim | - | [Kapuspen TNI : Video Di Medsos Dukungan TNI Untuk Anies Adalah Hoax](https://tni.mil.id/view-227355-kapuspen-tni-video-di-medsos-dukungan-tni-untuk-anies-adalah-hoax.html) |
| klarifikasi | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Chanel Youtube Menara Istana berjudul “dipimpin Langsung Panglima yudo margono !](https://tni.mil.id/view-226204-chanel-youtube-menara-istana-berjudul-dipimpin-langsung-panglima-yudo-margono-ribuan-tni-resmi-deklarasi-anies-presiden-2024-adalah-hoaks.html) |
| klarifikasi | belum_ada_pemeriksaan | beberapa_klaim | - | [Kapuspen TNI :  Undangan Panglima TNI di Akun Twitter Ulama Lover ! â€œHOAXâ€](https://tni.mil.id/view-119802-kapuspen-tni-undangan-panglima-tni-di-akun-twitter-ulama-lover-hoax.html) |
| klarifikasi | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Isu Pembakaran Mama Hertina oleh TNI adalah Hoaks: Faktanya Dibunuh Kelompok Sep](https://tni.mil.id/view-255981-isu-pembakaran-mama-hertina-oleh-tni-adalah-hoaks-faktanya-dibunuh-kelompok-separatis-opm.html) |
| klarifikasi | belum_ada_pemeriksaan | beberapa_klaim | - | [Kapuspen TNI Beberkan Fakta-Fakta Terkait Tuduhan TNI Jadi Provokator Unjuk Rasa](https://tni.mil.id/view-258937-kapuspen-tni-beberkan-fakta-fakta-terkait-tuduhan-tni-jadi-provokator-unjuk-rasa.html) |
| klarifikasi | belum_ada_pemeriksaan | beberapa_klaim | - | [Terkait Pengumuman Casis yang Beredar di Medsos, ini klarifikasi Danrem 161/Wira](https://ppid.tniad.mil.id/i/26649/terkait%20-pengumuman%20-casis%20-yang%20-beredar%20-di%20-medsos%20-ini%20-klarifikasi%20-danrem%20-161wira%20-sakti.) |
| klarifikasi | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Kodam VI/Mulawarman Klarifikasi Insiden di Balikpapan, Dipastikan Bukan Aksi Beg](https://ppid.tniad.mil.id/i/35419/kodam-vimulawarman-klarifikasi-insiden-di-balikpapan-dipastikan-bukan-aksi-begal) |
| klarifikasi | belum_ada_pemeriksaan | beberapa_klaim | - | [Klarifikasi Isu Viral: Dandim 0612/Tasikmalaya Pastikan Tidak Ada Anggota Terlib](https://ppid.tniad.mil.id/index.php/i/34495/klarifikasi-isu-viral-dandim-0612tasikmalaya-pastikan-tidak-ada-anggota-terlibat) |
| klarifikasi | tidak_yakin | tampak_meluruskan | 0.267 | [TNI AD Tegaskan Seleksi Taruna Akmil Tidak Dipungut Biaya](https://ppid.tniad.mil.id/index.php/i/17096/tni%20-ad%20-tegaskan%20-seleksi%20-taruna%20-akmil%20-tidak%20-dipungut%20-biaya) |
| rekrutmen | tidak_yakin | mirip_tapi_tidak_sama | 0.385 | [Rekrutmen TNI Angkatan Darat](https://ppid.tniad.mil.id/index.php/i/22364/rekrutmen-tni-angkatan-darat) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.335 | [Pangdam Hasanuddin, Tegaskan Masuk TNI Gratis](https://ppid.tniad.mil.id/i/2668/pangdam-hasanuddin-tegaskan-masuk-tni-gratis) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.329 | [Kodim 0723/Klaten Sosialisasikan Penerimaan Calon Bintara PK Dan Calon Tamtama P](https://ppid.tniad.mil.id/index.php/i/38050/kodim-0723klaten-sosialisasikan-penerimaan-calon-bintara-pk-dan-calon-tamtama-pk-gel-iii-tahun-2026-di-smk-negeri-1-trucuk) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.327 | [Pangdam I/BB Pimpin Sidang Pantukhir Cata PK TNI AD Gel III, 2.171 Calon Ikuti S](https://ppid.tniad.mil.id/i/40150/pangdam-ibb-pimpin-sidang-pantukhir-cata-pk-tni-ad-gel-iii-2171-calon-ikuti-seleksi) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.402 | [Pendaftaran Calon Bintara PK TNI AD Reguler Pria/Wanita dan Keahlian Pria TA. 20](https://ppid.tniad.mil.id/index.php/i/16332/pendaftaran%20-calon%20-bintara%20-pk%20-tni%20-ad%20-reguler%20-priawanita%20-dan%20-keahlian%20-pria%20-ta.%20-2024%20-telah%20-resmi%20-dibuka%20-di%20-wilayah%20-kodam%20-xivhsn) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.504 | [PENERIMAAN CALON BINTARA (CABA) DAN CALON TAMTAMA (CATA) TNI AD GELOMBANG I - TA](https://ppid.tniad.mil.id/i/1675/penerimaan%20-calon%20-bintara%20-(caba)%20-dan%20-%20-calon%20-tamtama%20-(cata)%20-%20-tni%20-ad%20-gelombang%20-i%20--%20-ta%20-2022) |
| rekrutmen | tidak_yakin | beberapa_klaim | 0.451 | [Kodim 0624/Kab. Bandung Gelar Sosialisasi Penerimaan Prajurit TNI AD Di SMK Yadi](https://ppid.tniad.mil.id/i/1281/kodim%20-0624kab.%20-bandung%20-gelar%20-sosialisasi%20-penerimaan%20-prajurit%20-tni%20-ad%20-di%20-smk%20-yadika) |
| bencana_bakti | belum_ada_pemeriksaan | beberapa_klaim | - | [Wujud Kepedulian Terhadap Sesama, Kodam Hasanuddin Salurkan Bantuan bagi Korban ](https://ppid.tniad.mil.id/i/29867/wujud-kepedulian-terhadap-sesama-kodam-hasanuddin-salurkan-bantuan-bagi-korban-bencana-di-sumatera) |
| bencana_bakti | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Kodam III/Slw, Pasca Banjir Lakukan Karya Bakti Dan Dirikan Posko Bantuan](https://ppid.tniad.mil.id/i/3918/kodam%20-iiislw%20-pasca%20-banjir%20-lakukan%20-karya%20-bakti%20-dan%20-dirikan%20-posko%20-bantuan) |
| bencana_bakti | tidak_yakin | mirip_tapi_tidak_sama | 0.301 | [Kowad Kodam IX/Udayana Teguhkan Komitmen TNI AD Bersama Rakyat di Tengah Bencana](https://ppid.tniad.mil.id/index.php/i/29450/kowad%20-kodam%20-ixudayana%20-teguhkan%20-komitmen%20-tni%20-ad%20-bersama%20-rakyat%20-di%20-tengah%20-bencana) |
| bencana_bakti | tidak_yakin | beberapa_klaim | 0.306 | [HUT Ke-65, Yonif 320 Kostrad Tebar Kepedulian Lewat Karya Bakti dan Santunan](https://ppid.tniad.mil.id/index.php/i/24424/hut%20-ke-65%20-yonif%20-320%20-kostrad%20-tebar%20-kepedulian%20-lewat%20-karya%20-bakti%20-dan%20-santunan) |
| bencana_bakti | belum_ada_pemeriksaan | beberapa_klaim | - | [Tim Wasev TMMD ke-127 Kunjungi Kodim 0617/Majalengka, Pastikan Program Berjalan ](https://ppid.tniad.mil.id/i/33467/tim%20-wasev%20-tmmd%20-ke-127%20-kunjungi%20-kodim%20-0617majalengka%20-pastikan%20-program%20-berjalan%20-optimal%20-dan%20-tepat%20-sasaran) |
| bencana_bakti | tidak_yakin | beberapa_klaim | 0.27 | [Kodim 0617/Majalengka Gelar Baksos Kesehatan dan Bagi Sembako dalam Rangka HUT T](https://ppid.tniad.mil.id/i/28343/kodim%20-0617majalengka%20-gelar%20-baksos%20-kesehatan%20-dan%20-bagi%20-sembako%20-dalam%20-rangka%20-hut%20-tni%20-ke-80) |
| bencana_bakti | belum_ada_pemeriksaan | beberapa_klaim | - | [Jumat Berkah, Babinsa Desa Buhung Bundang Kodim 1411/Bulukumba Serahkan Bantuan ](https://ppid.tniad.mil.id/i/18978/jumat%20-berkah%20-babinsa%20-desa%20-buhung%20-bundang%20-kodim%20-1411bulukumba%20-serahkan%20-bantuan%20-sembako%20-kepada%20-warga%20-kurang%20-mampu) |
| kemhan | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Wamenhan RI : Keterbukaan Informasi Berperan Layaknya Vaksin untuk Menangkal Dis](https://www.kemhan.go.id/2025/09/29/wamenhan-ri-keterbukaan-informasi-berperan-layaknya-vaksin-untuk-menangkal-disinformasi.html) |
| kemhan | belum_ada_pemeriksaan | tidak_ada_bantahan | - | [Kemhan Perkuat Literasi Geopolitik Generasi Muda Lewat Company Government Visit ](https://www.kemhan.go.id/2026/05/19/kemhan-perkuat-literasi-geopolitik-generasi-muda-lewat-company-government-visit-bem-fisip-unpas.html) |
| kemhan | belum_ada_pemeriksaan | beberapa_klaim | - | [Karo Infohan Wakili Menhan Hadiri HUT Ke-3 Garuda TV Mahayuga](https://www.kemhan.go.id/roinfohan/2026/08/10/karo-infohan-wakili-menhan-hadiri-hut-ke-3-garuda-tv-mahayuga.html) |

27 rilis dari tiga situs resmi bukan sampel acak dan bukan evaluasi independen; angkanya menunjukkan perilaku pada jenis teks yang paling berisiko (klarifikasi, rekrutmen), bukan akurasi umum.

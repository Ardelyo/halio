# Halio: Ringkasan untuk Pengambil Keputusan

> **Jenis:** Rujukan · **Untuk:** komandan satuan, pejabat teknologi, dan Dewan Juri · dua halaman · [Panduan juri](UNTUK_JURI.md)

## 1. Masalah

Pesan berantai di grup keluarga dan grup alumni membawa penipuan yang mencatut nama TNI AD: calo rekrutmen, surat kelulusan palsu, "siaga" yang tidak pernah dikeluarkan. Bantahan resmi ada, tetapi jarang sampai ke grup tempat pesan itu menyebar. Tiga hal membuatnya sulit ditangani:

- **Yang dirugikan adalah keluarga prajurit dan calon prajurit**, bukan hanya satuan. Mereka tidak memakai alat analis.
- **Alat AI yang menebak berbahaya di sini.** Satu bantahan palsu pada pesan yang benar, misalnya imbauan resmi, merusak kepercayaan lebih cepat daripada hoaks yang lolos.
- **Satuan sering bekerja di jaringan terbatas atau tertutup**, sehingga alat yang selalu butuh cloud tidak bisa dipakai.

Satu catatan jujur: kami tidak menemukan sumber publik bahwa PUSSIBERAD meminta alat semacam ini. Kebutuhan ini kami simpulkan dari pola penipuan yang terdokumentasi dan dari sifat jaringan satuan, bukan dari permintaan resmi.

## 2. Opsi yang dipertimbangkan

| Opsi | Kelebihan | Kekurangan |
|---|---|---|
| **A. Hanya cek fakta manual** (pemeriksa fakta, siaran resmi) | Akurat, sudah ada | Lambat, tidak sampai ke grup keluarga, tidak ada gambaran agregat untuk analis |
| **B. Detektor hoaks berbasis AI penuh** | Cakupan luas, terlihat canggih | Bisa menebak keliru, butuh cloud, sulit diaudit, risiko tuduhan palsu |
| **C. Halio:** AI hanya mencari bukti, **kode yang memutuskan**; mesin cocok-bantahan dapat berjalan tanpa AI dan tanpa jaringan | Jawaban selalu bersumber; "belum ada pemeriksaan" bila tidak tahu; bisa luring; bisa diaudit | Hanya mengenali bantahan yang ada di korpus; korpus masih kecil |

## 3. Pilihan: C

Alasannya, dalam urutan bobot kerugian jika salah:

1. **Tuduhan palsu ditekan, bukan dijanjikan hilang.** Pada 197 judul TurnBackHoax berlabel BENAR atau KLARIFIKASI, Halio salah mencap "terbukti salah" **0** kali; batas atas 95% (Wilson) adalah 1,9%. Diuji pada commit yang dibekukan sebelum skrip dijalankan (`eval/PUBLIC_RECHECK.md`).
2. **Bisa dipakai tanpa jaringan.** Mesin yang sama berjalan di browser dan terbukti identik dengan versi Python pada 603 vektor uji (0 perbedaan). Paket folder sekitar 640 KB dapat dibuka dari flashdisk (`docs/LURING.md`).
3. **Jujur tentang batas.** Dari 2.582 judul berlabel SALAH pada sampel yang sama, hanya 17 (0,7%) dikenali. Itu **cakupan korpus**, bukan akurasi. Korpus saat ini 10 bantahan; hasil di luar korpus adalah "belum ada pemeriksaan".

Opsi C tidak menggantikan pemeriksa fakta. Ia membawa bantahan mereka ke tempat pesan itu beredar.

## 4. Linimasa implementasi (usulan)

| Tahap | Isi | Syarat lanjut |
|---|---|---|
| **0. Sekarang** | Purwarupa berjalan: server publik, bot Telegram, mode luring, Radar | CI hijau, 273 tes otomatis |
| **1. Uji lapangan terbatas** | Uji dengan keluarga dan lansia sungguhan memakai lembar uji yang sudah disiapkan; uji di HP fisik dan Safari/iOS | Temuan terdokumentasi, tuduhan palsu tetap 0 |
| **2. Perluasan korpus** | Tambah bantahan bersama pemeriksa fakta, tiap entri dibuka dan diverifikasi sumbernya (`docs/VERIFIKASI_KORPUS.md`); setiap penambahan diikuti evaluasi ulang | Evaluasi ulang pada commit beku |
| **3. Pilot satuan** | Server lokal di jaringan satuan dengan profil tanpa cloud; sinkronisasi korpus bertanda tangan (belum ada) | Persetujuan dan izin satuan |

Linimasa ini adalah rencana kerja, bukan komitmen yang sudah dijadwalkan. Tahap 3 membutuhkan keputusan pihak satuan.

## 5. Batas dan risiko yang kami tahu

- Set uji utama ditulis tim sendiri; angka bukan akurasi dunia nyata.
- Mode luring belum diuji di HP fisik atau Safari/iOS. Telegram selalu butuh internet.
- **Radar**: bagian sensor memakai 23 feed publik sungguhan, tetapi sifatnya turunan (menaikkan yang sudah dilabeli pemeriksa fakta); Halio belum mendeteksi hoaks sebelum pemeriksa fakta. Bagian cek warga pada demo adalah **simulasi** dan diberi label; belum ada cek warga nyata yang membuktikan manfaatnya.
- Tidak mendeteksi deepfake dan tidak menilai keaslian foto.
- Ambang lonjakan Radar (3 cek dan dua kali rata-rata) pilihan kami, belum dikalibrasi data nyata.

## 6. Keputusan yang diminta

1. **Izin uji lapangan terbatas** (tahap 1) dengan keluarga relawan, termasuk lansia.
2. **Mitra pemeriksa fakta** untuk memperluas korpus dengan sumber yang terverifikasi.
3. **Penunjukan satuan percontohan** bila tahap 1 menunjukkan tuduhan palsu tetap 0.

*Cara membuktikan sendiri dalam 30 detik: buka halaman cek sekali saat online, putus internet, lalu cek pesan lagi. Halio menjawab dari perangkat dengan label "Mode luring".*

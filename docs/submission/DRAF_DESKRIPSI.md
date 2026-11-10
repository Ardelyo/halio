# Draf Teks untuk Form Pengumpulan dan Tanya-Jawab Juri

Semua jawaban di bawah selaras dengan [PROFIL_PENERAPAN.md](../PROFIL_PENERAPAN.md), [BUKTI_UJI_DEMO.md](../BUKTI_UJI_DEMO.md), dan [eval/RESULTS.md](../../eval/RESULTS.md). Bila ada angka yang berubah, ubah di sumbernya dulu, lalu di sini.

## a. Deskripsi karya (untuk form, 3 kalimat)

> Halio adalah teman cek pesan untuk keluarga Indonesia: pengguna meneruskan pesan yang meragukan lewat Telegram atau web, lalu menerima jawaban bersumber dalam bahasa sederhana, kartu yang siap dibagikan ke grup keluarga, dan pesan suara. AI hanya membantu mencari dan membaca bukti, sedangkan vonis diputuskan kode berdasarkan kutipan yang benar-benar ada di halaman sumber; bila belum ada pemeriksaan, Halio berkata jujur bahwa ia tidak mau menebak. Dari cek-cek warga yang dianonimkan, Radar Ketahanan Kognitif menunjukkan tren hoaks dan penipuan yang mencatut TNI AD kepada analis, tanpa membaca pesan pribadi siapa pun.

## b. Mengapa relevan bagi TNI AD (satu paragraf)

> Penipuan yang mencatut nama TNI AD nyata dan terdokumentasi: pada 2026 Kodam XV/Pattimura memburu oknum calo penerimaan Tamtama dengan kerugian korban sekitar Rp112 juta, dan pimpinan Kodam berulang kali menegaskan bahwa rekrutmen gratis tanpa titipan. Pesan semacam ini menyebar di grup keluarga, tempat bantahan resmi jarang sampai. Halio membawa bantahan bersumber itu ke tempat pesan beredar, dalam bahasa yang dipahami orang tua, dan memberi analis gambaran agregat tentang narasi yang sedang naik melalui Radar dan brief harian. Halio dapat berjalan di server satuan tanpa layanan cloud (dengan cakupan terbatas pada korpus bantahan yang diisi sendiri), dan tidak memprofilkan orang, akun, atau prajurit; yang dipantau hanya narasi dan klaim. Kami tidak mengklaim mengetahui kebutuhan internal satuan di luar yang tercantum di Rulebook dan sumber publik.

## c. Jawaban untuk pertanyaan juri yang diduga

**1. Siapa pengguna pertamanya?**
Orang tua dan kakek-nenek di grup WhatsApp keluarga, lewat anggota keluarga yang lebih muda yang memasang bot atau membuka web. Pengguna kedua adalah analis (pemeriksa fakta, unit siber) yang membuka Radar. Uji dengan pengguna lansia sungguhan **belum dilakukan**; lembar uji sudah siap (`docs/LEMBAR_UJI_KELUARGA.pdf`).

**2. Mengapa perlu AI, bukan daftar hoaks saja?**
Untuk hoaks yang sudah dikurasi, Halio memang tidak butuh AI: pencocokan lokal berjalan sekitar 1 ms (median 0,9 ms di laptop pengembang) dan tetap bekerja dalam mode tanpa AI. AI dipakai untuk kabar di luar korpus: mencari halaman, membaca kutipan, dan menilai apakah kutipan itu membantah atau mendukung klaim. Model **tidak memutuskan vonis** dan **tidak menulis kutipan**; kutipan disalin kode dari halaman yang dibuka kode, dan status diputuskan kode.

**3. Data apa yang keluar ke cloud?**
Pada profil cloud: teks klaim yang sudah dibersihkan dari nomor, NIK, email, rekening, tautan, dan @akun (maksimal 300 karakter) ke Gemini; foto atau rekaman suara asli bila pengguna mengirimnya dan fitur media aktif; naskah suara jawaban ke Cloud TTS; kata kunci ke GDELT dan URL publik ke Internet Archive. ID Telegram, isi Radar, dan antrean tiket tidak dikirim. Pada profil tanpa cloud, tidak ada yang keluar. Rincian per layanan ada di `docs/PROFIL_PENERAPAN.md`.

**4. Bagaimana bila model salah atau mati?**
Bila mesin bukti gagal, Halio mencoba mesin cadangan. Bila itu juga gagal, hasil pencocokan lokal tetap berlaku: bantahan kurasi tetap tampil, dan kabar di luar korpus menjadi "belum ada pemeriksaan". Model tidak bisa mengubah pesan yang meluruskan hoaks menjadi vonis hoaks; ini dijaga tes. Batas harian dan batas waktu per panggilan mencegah biaya dan antrean tak terkendali.

**5. Apa yang disimulasikan?**
GitHub Pages hanya simulasi di peramban, berlabel. Data Radar dari `scripts/seed_demo.py` adalah simulasi dan diberi banner. Feed ekstensi di `demo-feed.html` adalah feed buatan. Server publik, bot Telegram, mesin bukti, kartu, suara, dan Telusur berjalan sungguhan.

**6. Korpusnya hanya 7 bantahan. Bukankah itu terlalu sedikit?**
Ya, untuk produksi itu terlalu sedikit, dan kami menyatakannya di README. Korpus kecil adalah pilihan sengaja: setiap entri diperiksa manusia dan bersumber (status 14 tautannya di `docs/VERIFIKASI_KORPUS.md`). Di luar korpus, Halio memakai arsip judul cek fakta dan pencarian web dengan kutipan terverifikasi, atau berkata tidak tahu. Jalur untuk menumbuhkan korpus adalah kemitraan dengan pemeriksa fakta (mis. Mafindo) dan tim penerangan, bukan menulis bantahan sendiri.

**7. Evaluasinya buatan tim sendiri. Seberapa bisa dipercaya?**
Tidak bisa dibaca sebagai akurasi dunia nyata, dan kami tidak mengklaimnya. Ada 108 item tulisan tim: set pengembangan 52 dan set holdout 56 (66 pernyataan benar/belum dikenal, 32 parafrase hoaks, 10 opini). Angka yang kami jaga adalah **tuduhan palsu**: 0 pada kedua set, diperiksa CI pada setiap perubahan. Recall holdout 88%. Pada uji demo 10 skenario di server publik, tuduhan palsu juga 0. Satu parafrase rekrutmen TNI AD hanya mendapat 🟠, dan kami mencatat penyebabnya. Set uji independen dari luar tim adalah langkah berikutnya.

**8. Bagaimana ketahanan terhadap prompt injection?**
Halaman web diperlakukan sebagai data, bukan instruksi. Model hanya mengembalikan penilaian berupa nomor bukti. Kalimat laporan yang tidak didukung kutipan, atau memuat angka yang tidak ada di kutipan, dibuang kode. Halaman dari situs tak dikenal tidak bisa menjadi bukti walaupun model tertipu. Uji keamanan langsung tersedia di `/uji.html`: halaman jebakan berisi "abaikan instruksi", domain palsu yang meniru situs pemerintah/TNI AD, dan kalimat laporan karangan. Ada tes yang memastikan uji jebakan bisa gagal bila model menurut.

**9. Bisakah Halio mendeteksi deepfake?**
Tidak. Halio mencocokkan **klaim** dalam pesan dengan bantahan yang sudah ada. Pencarian gambar terbalik hanya menunjukkan di mana gambar pernah muncul, bukan apakah gambar itu asli.

**10. Rencana setelah hackathon?**
(1) Uji dengan keluarga dan lansia memakai lembar uji yang sudah ada. (2) Set evaluasi independen dan pengukuran live. (3) Kemitraan data dengan pemeriksa fakta untuk korpus dan arsip. (4) Tinjauan hukum UU PDP dan akun analis individual. (5) Perbaikan teknis yang sudah tercatat: SSRF DNS rebinding, pencocokan per kalimat, dan sumber resmi untuk entri TNI AD. Semua risiko terbuka ada di `docs/LAUNCH_READINESS.md`.

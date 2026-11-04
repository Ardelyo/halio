# Analisis Radar dan alternatif untuk TNI AD

Disusun 4 Nov 2026. Radar dijalankan sungguhan (data demo 313 kejadian + uji alur nyata lewat API dan browser), bukan hanya dibaca kodenya.

## 1. Apakah Radar berfungsi?

**Ya, alur intinya berfungsi.** Hasil uji:

| Yang diuji | Hasil |
|---|---|
| Ringkasan: jumlah cek, sebaran status, tren harian, kategori, teknik manipulasi | Tampil benar dari data; tanpa error JavaScript |
| Kabar baru (belum ada bantahan) dengan ambang k-anonimitas | 6 pelapor Telegram berbeda → kabar muncul; 6 permintaan dari satu jaringan web dengan ID pelapor palsu → **tidak** muncul (benar) |
| Eskalasi → antrean → balasan | Tiket masuk; balasan ke Telegram tanpa token ditolak dengan pesan jelas dan **tiket tidak ditutup** (benar); mode "catat saja" menutup tiket dengan catatan |
| Banding | Tercatat, masuk antrean |
| Tab Cakupan sensor | 21 sumber hidup, 2 basi dari 23 |
| Tampilan seluler dan desktop | Rapi; konsisten dengan merek |

**Cacat yang ditemukan saat dijalankan (bukan dugaan):**

1. **Hitungan "pelapor berbeda" mentok di 5.** Di `store.py` pelapor baru hanya dicatat sampai jumlah ambang k. Kabar yang dikirim 6 orang dan yang dikirim 6.000 orang sama-sama tampil "5". Radar **tidak bisa mengukur kecepatan penyebaran**, padahal itu inti sebuah radar.
2. **Data simulasi tampil seperti data nyata pada mode API.** Banner "simulasi" hanya muncul di GitHub Pages. Saat server memakai data hasil `seed_demo.py` (313 kejadian berkanal `demo`), halaman tidak menandainya, meskipun API mengirim `demo_events` dan dokumentasi skrip menjanjikan banner. Ini soal kejujuran: harus diperbaiki sebelum demo.
3. **Pelapor web dihitung per jaringan /24.** Aman terhadap pemalsuan, tetapi pengguna seluler Indonesia sering berbagi alamat (CGNAT), sehingga banyak orang berbeda terhitung satu. Untuk pelapor web, kabar baru akan jarang melewati k=5. Pelapor Telegram tidak terdampak (ID chat tepercaya).
4. **Radar tidak terhubung ke Sensor.** Sensor mengumpulkan judul berita dan cek fakta; Radar menampung laporan warga. Tidak ada tampilan yang menyilangkannya ("kabar ini sudah dibantah di TurnBackHoax sejak jam X", "kabar ini belum diliput siapa pun").
5. **Satu token bersama untuk semua analis**, tanpa identitas atau jejak per orang (sudah tercatat di `LAUNCH_READINESS.md`).
6. **Pesan "Pelapor berbeda" untuk kabar yang sudah ada bantahan** tidak ada: Radar hanya menghitung kategori, tidak "siapa menyebarkan ke mana".

## 2. Apakah ada wow factor?

**Belum, secara jujur.** Radar saat ini rapi, jujur, dan menjaga privasi, tetapi ia sebuah **dasbor**. Dokumen riset hackathon yang Anda berikan menyebut "dashboard tanpa keputusan" sebagai pola yang sulit membedakan diri, sedangkan pemenang memakai pola **data → prioritas → tindakan** (Seattle Hotspotter). Satu-satunya "tindakan" di Radar sekarang adalah menjawab tiket secara manual.

### Usulan wow yang realistis: "Radar → Klarifikasi dalam menit"
Yang dijual bukan grafik, melainkan **waktu dari kabar muncul sampai klarifikasi bersumber terbit**.

Rujukan: Taiwan memakai format "2-2-2" (tanggapan dalam dua jam, ±200 kata, dua gambar) pada kampanye "humor over rumor"
([Al Jazeera](https://www.aljazeera.com/news/2021/5/28/disinformation-goes-viral-as-taiwan-battles-new-covid-surge), [GovTech](https://www.govtech.com/em/emergency-blogs/disaster-zone/countering-rumor-with-humor.html));
Pusat Penanggulangan Disinformasi Ukraina membantah video palsu yang menyamar sebagai prajurit
dan rumor soal pasukan untuk mencegah kesan kekacauan ([Mezha](https://mezha.net/eng/?p=3317811), [Ukrinform](https://www.ukrinform.net/rubric-ato/4045339-ccd-records-intensification-of-russian-propaganda-against-ukrainian-army.html)).
Laporan DFRLab/Hybrid CoE menyebut bantahan cepat itu perlu, namun tinjauan lain memperingatkan bahwa bantahan saja tidak membangun ketahanan jangka panjang
([DFRLab](https://dfrlab.org/2024/01/24/how-ukraine-fights-russian-disinformation-beehive-vs-mammoth/), [Temple Law](https://www2.law.temple.edu/lppp/wp-json/wp/v2/posts/2190)),
jadi Halio memasangkannya dengan prebunking (teknik manipulasi sudah ada).

Adegan demo (60–90 dtk, semua nyata, tanpa kecurangan):
1. Enam laporan masuk dari Telegram. Kabar naik ke daftar **Perlu tindakan** dengan label kecepatan ("naik 6× dalam 4 menit").
2. Halio mengisi **draf klarifikasi**: kartu Halio + teks ≤200 kata, hanya dari sumber yang kutipannya lolos verifikasi kode.
3. Analis menekan **Setujui** (satu orang, tercatat).
4. Kartu terbit ke kanal Telegram resmi; panel menunjukkan **waktu-ke-klarifikasi** (mis. 3 menit 20 detik).
5. Safeguard: bila tidak ada sumber yang lolos, tombol Setujui nonaktif dan tertulis "belum ada bukti, tidak ada draf."

Yang harus dibangun (urut): (a) hitungan pelapor tanpa batas k dengan privasi (mis. cacah per hari dengan estimator HyperLogLog, bukan daftar pseudonim) dan kecepatan per jam; (b) skor prioritas deterministik (kecepatan × kategori institusi × tidak ada bantahan × teknik manipulasi); (c) generator draf yang memakai pipeline verifikasi sumber yang sudah ada; (d) alur setujui→terbit→ukur waktu; (e) banner simulasi. Perkiraan: 3–4 hari kerja.

## 3. Alternatif untuk TNI AD selain Radar

Dasar masalah yang **terdokumentasi** (bukan dugaan):
- Calo dan penipuan rekrutmen berulang: surat kelulusan palsu dengan kerugian Rp310 juta di Kulon Progo
  ([Metro TV](https://www.metrotvnews.com/read/b3JCpAVL-korban-penipuan-rekrutmen-tni-di-kulon-progo-rugi-rp310-juta-tiga-pelaku-ditangkap)),
  dan prajurit yang diduga menjadi calo di Maluku Utara ([Investortrust](https://investortrust.id/national/118301/kodam-pattimura-buru-serma-su-buronan-kasus-calo-penerimaan-prajurit-tni-ad)).
  Rekrutmen resmi dinyatakan gratis; ada nomor pengaduan resmi yang disebut dalam pemberitaan.
- Hoaks yang menyasar citra institusi: setelah kerusuhan Agustus 2025, Puspen TNI menyatakan ada kabar palsu bahwa prajurit menjadi provokator
  ([Metro TV](https://www.metrotvnews.com/read/b2lCpnWA-tni-tegaskan-isu-prajurit-jadi-provokator-demo-hoaks)).
- Perintah berulang agar prajurit bijak bermedia sosial; pedoman melarang mengunggah informasi sensitif seperti data alutsista, doktrin, rencana operasi
  ([Tirto](https://tirto.id/panglima-tni-minta-jajarannya-bijak-gunakan-medsos-cmTG), [jurnal AKMIL](https://ojs.akmil.ac.id/index.php/administrsipertahanan/article/download/301/262/1631)).
- Satuan sandi dan siber TNI AD adalah **Pussansiad** (Pusat Sandi dan Siber Angkatan Darat); satu laporan lama menyebut 200–300 serangan siber per hari (2020, [iNews](https://www.inews.id/news/nasional/catat-200-300-serangan-siber-setiap-hari-ini-antisipasi-tni-ad)). Nama "Pussiberad" tidak saya temukan; sebut sesuai nama resmi dari panitia.
- **Tidak ditemukan** (jangan diklaim): kasus deepfake pejabat TNI 2026 atau akun palsu perwira 2026. Yang ada hanya kasus lama penyamar perwira tinggi (2016).

### Daftar alternatif, diurutkan

| # | Produk | Masalah nyata yang dijawab | Wow dalam demo | Kelayakan 8 hari | Risiko |
|---|---|---|---|---|---|
| **A** | **Cek Rekrutmen & Anti-Calo**: halaman publik "Cek tautan / nomor / surat ini resmi?" + laporan calo teragregasi per wilayah | Calo dan surat palsu berulang tiap gelombang | Tempel tautan/nomor → "BUKAN kanal resmi" atau "kanal resmi: tniad.mil.id"; surat berQR yang bisa diverifikasi | **Tinggi**: sudah ada pengecekan domain, korpus calo, kartu; tambah daftar kanal resmi dan verifikasi tanda tangan | Daftar kanal resmi harus datang dari TNI AD; kami hanya memakai sumber yang bisa dibuka publik |
| **B** | **Klarifikasi cepat untuk Penerangan** (kelanjutan Radar, bagian 2) | Hoaks yang menyasar citra institusi | Waktu-ke-klarifikasi dalam menit | Sedang: 3–4 hari | Wajib persetujuan manusia; tidak memberi vonis sendiri |
| **C** | **Pantauan pemberitaan institusi** (media-watch): memfilter 23 feed sensor untuk TNI/Kodam/Kodim, menandai item yang cocok dengan judul bantahan di TurnBackHoax/CekFakta, ringkasan harian | Citra dan kabar yang beredar di media | Satu halaman "Hari ini tentang TNI AD": berita, hoaks yang dibantah, hoaks yang belum | Tinggi (sensor sudah ada) | Hanya media publik, tanpa menilai pendapat warga; tidak memantau akun individu |
| **D** | **Cek sebelum unggah** (OPSEC mandiri untuk prajurit dan keluarga): unggah foto di perangkat → peringatan geotag/EXIF, lencana/nama/satuan terbaca, latar lokasi, lalu versi aman | Pedoman larangan info sensitif; keluarga sebagai sasaran | Foto → "ditemukan koordinat GPS dan papan nama" → klik hapus | Sedang (ekstensi sudah punya pipeline on-device) | **Tumpang tindih dengan proyek kompetitor "OPSEC Guard"** (YOLO-World + OCR + EXIF) di kategori yang sama; bedakan dengan sifat swalayan dan agregat, atau jangan jadi fokus |
| E | **Pembuktian dokumen resmi**: surat kelulusan bertanda tangan digital + pemindai verifikasi | Surat kelulusan palsu | Pindai QR → "terverifikasi/tidak" | Rendah: butuh TNI menerbitkan dokumen bertanda tangan; hanya bisa didemokan dengan penerbit simulasi | Ketergantungan institusi; harus dilabeli simulasi |
| F | **Antrean pengaduan terpadu**: Halio sebagai pintu depan nomor pengaduan (klasifikasi dan pengalihan) | Pengaduan manual | Pengaduan masuk → terklasifikasi → tiket | Sedang | Perlu kanal WhatsApp resmi (belum diuji) |

### Rekomendasi
1. **A + B** sebagai paket utama ("Anti-calo untuk calon prajurit dan keluarga" + "Klarifikasi cepat untuk Penerangan"). Keduanya memakai fondasi yang sudah ada dan punya masalah yang terdokumentasi.
2. **C** sebagai pelengkap murah (sensor sudah jalan).
3. **D** hanya bila ada waktu tersisa, dan dibedakan dari OPSEC Guard. **E, F** sebagai peta jalan, bukan demo.
4. Radar tetap dipertahankan, tetapi **jangan lagi dijual sebagai fitur utama** sampai bagian 2 selesai. Dijual sebagai "dasbor", ia hanya satu dari banyak.

## 4. Batas riset ini
- Tidak ada akses ke kebutuhan internal TNI AD; semua di atas dari berita dan sumber publik. Validasi dengan satu orang yang bekerja di sana sebelum menyebutnya "kebutuhan TNI AD".
- Contoh Taiwan dan Ukraina tentang kecepatan bantahan berasal dari konteks sipil/perang; tidak menunjukkan efek jangka panjang terhadap kepercayaan.
- Jumlah "200–300 serangan siber/hari" berasal dari laporan 2020 dan tidak untuk dipakai sebagai angka terkini.

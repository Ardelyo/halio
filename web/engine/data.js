// file ini digenerate otomatis lewat scripts/build_engine_data.py dr kode python + data/debunks.json, jgn diedit manual ya
globalThis.HalioEngineData = {
 "version": "luring-1",
 "corpusSha256": "74b9fda42b31b84413d88d46473fcd79de09edd8251d77d57d1e370dea9d2416",
 "registrySha256": "961b3233e6cf00e3482d37d21d38dd12dad79a4bbe516f1d26c8dcb3808e4a1e",
 "thresholds": {
  "match": 0.4,
  "unsure": 0.26
 },
 "corpus": [
  {
   "id": "bansos-deepfake-presiden",
   "kategori": "penipuan_bansos",
   "klaim": "Video Presiden Prabowo dan Menteri Keuangan membagikan bantuan tunai, daftar lewat nomor WhatsApp dan bayar biaya administrasi",
   "varian": [
    "Presiden bagi-bagi bantuan sosial tunai, hubungi nomor WhatsApp untuk mendaftar",
    "Prabowo bagikan bantuan Rp10 juta sampai Rp45 juta bagi yang follow dan share",
    "pendaftaran bansos tunai dari presiden lewat whatsapp, transfer biaya admin dulu",
    "video menteri keuangan umumkan bantuan, daftar lewat nomor wa",
    "bantuan tunai dari presiden untuk rakyat, chat nomor WhatsApp untuk mendaftar lalu bayar biaya admin",
    "video menteri bilang bansos tunai cair pekan ini, daftar lewat admin WhatsApp dan transfer biaya verifikasi",
    "pejabat negara dalam video umumkan bantuan sosial cair, hubungi nomor WA lalu bayar biaya admin",
    "pak presiden bagikan uang tunai jutaan rupiah lewat video, daftar WhatsApp, bayar admin dulu"
   ],
   "fakta": "Video semacam ini adalah deepfake (wajah dan suara buatan AI). Bareskrim Polri mengungkap penipuan yang memakai deepfake Presiden Prabowo dan Sri Mulyani: korban diarahkan ke WhatsApp lalu diminta membayar biaya administrasi berulang kali. Bantuannya tidak pernah ada.",
   "sederhana": "Itu video palsu buatan komputer. Bantuan resmi dari pemerintah tidak pernah meminta Ibu atau Bapak membayar biaya apa pun lewat WhatsApp.",
   "sumber": [
    {
     "nama": "Katadata (mengutip Bareskrim Polri)",
     "url": "https://katadata.co.id/amp/digital/teknologi/67a5dc910647b/penipuan-bansos-pakai-ai-wajah-prabowo-ratusan-korban-rugi-puluhan-juta/",
     "jenis": "media"
    }
   ],
   "syarat": [
    "(daftar|pendaftaran|hubungi|chat|japri|kontak|kirim)\\W+(\\w+\\W+){0,4}(whatsapp|\\bwa\\b|nomor|admin)|(biaya|bayar|transfer)\\W+(\\w+\\W+){0,2}(admin|administrasi|verifikasi|pendaftaran|pencairan)|\\b(follow|share)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "rekrutmen-tni-ad-berbayar",
   "kategori": "penipuan_catut_tni",
   "klaim": "Ada jalur khusus masuk TNI AD dijamin lulus dengan membayar sejumlah uang lewat orang dalam",
   "varian": [
    "dijamin lulus jadi tentara asal bayar uang pelicin",
    "jalur titipan penerimaan bintara tamtama TNI AD, transfer dulu biaya pendaftaran",
    "bisa bantu anak masuk TNI lewat kenalan di kodam, ada biayanya",
    "pendaftaran prajurit TNI AD berbayar lewat calo",
    "kenalan di kodam bisa bantu lulus tes tamtama TNI AD, dijamin lulus asal siapkan uang jutaan"
   ],
   "fakta": "Rekrutmen TNI AD dilaksanakan terbuka, transparan, dan tidak dipungut biaya. Kelulusan ditentukan hasil seleksi, bukan pembayaran. Pada 2026 Kodam XV/Pattimura memburu oknum yang diduga menjadi calo penerimaan Tamtama dengan kerugian korban Rp112 juta, dan menegaskan itu perbuatan pribadi, bukan atas nama institusi.",
   "sederhana": "Masuk TNI AD itu gratis dan lewat tes resmi. Siapa pun yang minta uang supaya 'dijamin lulus' adalah penipu.",
   "sumber": [
    {
     "nama": "Bisnis.com: Syarat dan Cara Daftar Rekrutmen TNI AD 2026",
     "url": "https://kabar24.bisnis.com/read/20260107/243/1942271/syarat-dan-cara-daftar-rekrutmen-tni-ad-2026-simak-beserta-jadwalnya",
     "jenis": "media"
    },
    {
     "nama": "Investortrust: Kodam Pattimura buru calo penerimaan prajurit",
     "url": "https://investortrust.id/national/118301/kodam-pattimura-buru-serma-su-buronan-kasus-calo-penerimaan-prajurit-tni-ad",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(bayar|biaya|uang|transfer|dp|titipan|calo|orang dalam|kenalan|pelicin|dicicil|\\d+ ?(juta|jt))\\b",
    "\\b(lulus|masuk|jalur|titipan|bantu|kenalan|orang dalam|calo|pelicin)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "bmkg-prediksi-gempa-tanggal",
   "kategori": "bencana",
   "klaim": "Akan terjadi gempa besar dan tsunami pada tanggal tertentu menurut prediksi BMKG",
   "varian": [
    "BMKG memprediksi gempa magnitudo 9 akan terjadi minggu depan",
    "waspada tsunami besar tanggal 20 desember sampai 23 januari",
    "akan ada gempa susulan M 9.0 setelah gempa banten",
    "prediksi gempa 7 SR dalam 10 hari ke depan, segera mengungsi",
    "kabar dari orang dalam BMKG gempa besar datang beberapa hari lagi, warga disuruh keluar rumah",
    "gempa susulan yang jauh lebih besar akan terjadi pekan depan, sebarkan ke keluarga",
    "katanya gempa dahsyat akan mengguncang dalam waktu seminggu, jangan tidur di dalam rumah",
    "ramalan gempa susulan yang lebih besar akan datang dalam beberapa hari",
    "waspada gempa besar diprediksi terjadi minggu depan, mohon sebarkan ke keluarga",
    "gempa megathrust besar pasti terjadi dalam waktu dekat, tinggal menunggu waktu"
   ],
   "fakta": "BMKG berulang kali menegaskan bahwa belum ada teknologi di dunia yang bisa memprediksi tanggal, lokasi, dan kekuatan gempa secara pasti, dan BMKG tidak pernah mengeluarkan prediksi semacam itu. Informasi gempa dan peringatan tsunami resmi hanya dari kanal BMKG. BMKG juga menegaskan informasi potensi gempa megathrust (misalnya M8,7 di selatan Jawa) bukan prediksi maupun peringatan dini.",
   "sederhana": "Tidak ada yang bisa tahu tanggal gempa, termasuk BMKG. Kalau ada pesan menyebut tanggal gempa, itu tidak benar. Cek info resmi di aplikasi atau situs BMKG.",
   "sumber": [
    {
     "nama": "BMKG: Siaran pers prediksi gempa 7,0 adalah hoaks",
     "url": "https://www.bmkg.go.id/siaran-pers/prediksi-gempa-7-0-earthquakes-weather-bmkg-sebut-itu-hoaks",
     "jenis": "resmi"
    },
    {
     "nama": "Kompas TV: BMKG soal isu gempa dan tsunami 20 Desember-23 Januari",
     "url": "https://www.kompas.tv/article/359382/beredar-di-medsos-ada-gempa-dan-tsunami-besar-di-20-desember-sampai-23-januari-ini-kata-bmkg",
     "jenis": "media"
    },
    {
     "nama": "Republika: BMKG sebut gempa susulan M 9,0 hoaks",
     "url": "https://news.republika.co.id/berita/pvntjd377/bmkg-sebut-gempa-susulan-m-90-hoaks",
     "jenis": "media"
    },
    {
     "nama": "Metro TV: Megathrust disebut hanya potensi, bukan prediksi",
     "url": "https://www.metrotvnews.com/read/NG9C36QD-megathrust-disebut-hanya-potensi-bukan-prediksi",
     "jenis": "media"
    },
    {
     "nama": "Setkab: Tidak bisa diprediksi, BMKG kembali minta masyarakat tenang hadapi isu megathrust",
     "url": "https://setkab.go.id/tidak-bisa-diprediksi-bmkg-kembali-minta-masyarakat-tenang-hadapi-isu-megathrust",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(gempa|tsunami)\\b",
    "\\b(akan|diprediksi|memprediksi|prediksi)\\b(\\W+\\w+){0,8}\\W+(terjadi|datang|melanda|minggu depan|bulan depan|tanggal|dalam \\d+ (hari|minggu))|\\b(minggu depan|bulan depan|tanggal \\d+|dalam \\d+ (hari|minggu))\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "air-kelapa-garam-obat",
   "kategori": "kesehatan",
   "klaim": "Campuran air kelapa muda, jeruk nipis, dan garam bisa menyembuhkan COVID-19",
   "varian": [
    "minum air kelapa dicampur garam dan jeruk nipis langsung sembuh dari corona",
    "ramuan air kelapa madu jeruk nipis garam obat covid paling manjur",
    "air kelapa muda dan garam menyembuhkan virus"
   ],
   "fakta": "Tidak ada bukti klinis bahwa campuran ini menyembuhkan COVID-19. Farmakolog UGM menyatakan belum ada pembuktian klinis, dan penelusuran Mafindo menilai klaim tersebut keliru. Air kelapa dan jeruk nipis boleh untuk kesehatan, tetapi bukan obat.",
   "sederhana": "Air kelapa itu menyegarkan, tapi bukan obat penyakit. Kalau sakit, periksakan ke puskesmas atau dokter.",
   "sumber": [
    {
     "nama": "Liputan6 Cek Fakta (dengan Mafindo)",
     "url": "https://www.liputan6.com/cek-fakta/read/4332289/cek-fakta-tidak-ada-bukti-air-kelapa-dicampur-jeruk-nipis-dan-garam-manjur-menyembuhkan-penderita-covid-19",
     "jenis": "cek_fakta"
    },
    {
     "nama": "Liputan6 Cek Fakta: belum terbukti",
     "url": "https://www.liputan6.com/cek-fakta/read/4676230/cek-fakta-belum-terbukti-mengonsumsi-air-kelapa-muda-madu-jeruk-nipis-dan-garam-bisa-sembuhkan-covid-19",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(sembuh|nyembuhin|menyembuhkan|mengobati|ampuh|manjur|penangkal)\\b|\\bobat (covid|corona|virus)",
    "\\b(covid|corona|virus)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "kuota-gratis-operator",
   "kategori": "phishing",
   "klaim": "Operator seluler dan pemerintah membagikan kuota internet gratis puluhan GB, klik tautan dan isi nomor HP",
   "varian": [
    "kuota gratis 30GB HUT RI dari semua operator, klik link ini",
    "subsidi kuota internet 75 GB dari kominfo, isi nomor hp lalu bagikan ke 10 grup",
    "ulang tahun whatsapp bagi kuota 20 GB gratis",
    "dapatkan kuota gratis dengan mengisi data di link berikut"
   ],
   "fakta": "Telkomsel, XL Axiata, dan Indosat membantah pembagian kuota gratis semacam ini. Tautan dalam pesan seperti ini biasanya mengarah ke situs yang meminta data pribadi (phishing) lalu menyuruh korban menyebarkan pesan ke kontak dan grup.",
   "sederhana": "Itu jebakan untuk mencuri data. Operator tidak membagi kuota lewat tautan berantai. Jangan klik dan jangan isi nomor HP.",
   "sumber": [
    {
     "nama": "MerahPutih: kuota gratis 30GB HUT RI dibantah operator",
     "url": "https://www.merahputih.com/post/read/hoaks-atau-fakta-kuota-internet-gratis-30gb-hut-ri-dibagikan-berbagai-operator-seluler",
     "jenis": "media"
    },
    {
     "nama": "Bisnis.com Cek Fakta: subsidi kuota 75 GB",
     "url": "https://kabar24.bisnis.com/read/20210208/621/1353735/cek-fakta-subsidi-kuota-internet-75-gb-kominfo-benar-atau-hoaks",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(klik|link|tautan|isi (nomor|data)|bagikan ke|sebarkan ke|share ke)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "saldo-etoll-gratis",
   "kategori": "phishing",
   "klaim": "Jasa Marga membagikan saldo e-toll gratis, klik tautan untuk klaim",
   "varian": [
    "klaim saldo e-money gratis dari jasa marga lewat link ini",
    "pengguna tol dapat saldo e-toll gratis, daftar di tautan berikut"
   ],
   "fakta": "Jasa Marga mengingatkan bahwa pesan saldo e-toll gratis adalah modus phishing, dan meminta masyarakat tidak membagikan data pribadi di situs yang tidak resmi.",
   "sederhana": "Tidak ada saldo tol gratis lewat tautan. Itu cara penipu mengambil data Ibu dan Bapak.",
   "sumber": [
    {
     "nama": "Kompas TV: phishing berkedok saldo e-toll gratis",
     "url": "https://www.kompas.tv/nasional/583065/phishing-berkedok-saldo-e-toll-gratis-marak-jasa-marga-ingatkan-pengguna-tol",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(gratis|cuma-cuma|hadiah)\\b",
    "\\b(klik|link|tautan|klaim|isi data)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "penculikan-anak-berantai",
   "kategori": "keamanan_publik",
   "klaim": "Waspada penculikan anak, komplotan penculik berkeliaran di sekolah dan kampung, sebarkan ke grup",
   "varian": [
    "ada penculik anak pakai mobil di dekat sekolah, culik anak untuk diambil organnya",
    "pesan berantai waspada penculikan anak di daerah kita",
    "komplotan penculik menyamar jadi orang gila keliling kampung"
   ],
   "fakta": "Pesan berantai tentang penculikan anak berulang kali dinyatakan hoaks oleh kepolisian setelah ditelusuri. Pesan semacam ini pernah memicu amuk massa terhadap orang tak bersalah. Laporkan kecurigaan ke polisi, jangan main hakim sendiri.",
   "sederhana": "Pesan seperti ini sering tidak benar dan pernah membuat orang tak bersalah dipukuli. Kalau curiga, lapor ke polisi atau RT, jangan disebar.",
   "sumber": [
    {
     "nama": "RRI Cek Fakta: tips menghindari hoaks penculikan anak",
     "url": "https://rri.co.id/tanjungpinang/cek-fakta/189264/4-tips-menghindari-berita-hoax-penculikan-anak",
     "jenis": "cek_fakta"
    },
    {
     "nama": "Kumparan: diamuk massa akibat kabar hoaks penculikan anak",
     "url": "https://kumparan.com/kumparannews/diamuk-massa-akibat-kabar-hoax-penculikan-anak",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(berkeliaran|keliling|menyamar|organ|organnya|komplotan|sindikat|mobil|mengincar|incar|sebarkan|sebarin|share)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-surat-tilang-whatsapp",
   "kategori": "phishing",
   "klaim": "Surat tilang atau e-tilang dikirim lewat WhatsApp dalam bentuk file APK yang harus dipasang untuk melihat dendanya",
   "varian": [
    "ada surat tilang digital dari polisi, install file apk ini untuk lihat pelanggaran dan bayar denda",
    "kamu kena etle, unduh aplikasi apk untuk cek surat tilang",
    "surat konfirmasi tilang elektronik berupa file apk, klik untuk bayar",
    "e-tilang masuk ke pesan, pasang apk dulu biar bisa lihat kode bayar"
   ],
   "fakta": "Kakorlantas Polri menyatakan Korlantas, Ditlantas, dan Satlantas hanya mengirim konfirmasi tilang ETLE lewat surat yang dikirim PT Pos Indonesia, dan menyebut pesan tilang berupa file APK sebagai modus pencurian data. Kominfo juga mengingatkan tidak ada e-tilang yang dikirim lewat WhatsApp. File APK dari pesan seperti ini bisa memasang program berbahaya di ponsel.",
   "sederhana": "Polisi tidak mengirim surat tilang lewat WhatsApp. Kalau ada file APK atau aplikasi yang katanya surat tilang, jangan dibuka dan jangan dipasang. Itu penipuan untuk mencuri data di ponsel.",
   "sumber": [
    {
     "nama": "RRI Cek Fakta: [SALAH] Surat Tilang Digital APK (mengutip Kakorlantas Polri)",
     "url": "https://rri.co.id/samarinda/cek-fakta/498916/salah-surat-tilang-digital-apk",
     "jenis": "cek_fakta"
    },
    {
     "nama": "detikInet: Awas, tidak ada e-tilang yang dikirim ke WhatsApp (mengutip Kominfo dan Kepolisian)",
     "url": "https://inet.detik.com/security/d-7305490/awas-tidak-ada-e-tilang-yang-dikirim-ke-whatsapp",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(tilang|etle|e-tilang|pelanggaran lalu lintas|kode bayar)\\b",
    "\\bapk\\b|\\b(unduh|download|install|pasang)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "calo-cpns-bayar-lulus",
   "kategori": "penipuan_rekrutmen",
   "klaim": "Ada orang dalam yang bisa menjamin lulus CPNS atau PPPK dengan membayar sejumlah uang",
   "varian": [
    "bisa bantu lulus cpns asal bayar, dijamin lolos lewat orang dalam bkn",
    "jalur khusus pppk dan cpns, transfer dulu puluhan juta pasti diangkat jadi asn",
    "calo cpns menjanjikan kelulusan tanpa tes, cukup bayar uang pelicin",
    "ada kenalan di instansi yang bisa meloloskan seleksi asn, biayanya dicicil"
   ],
   "fakta": "BKN mengingatkan pelamar agar tidak percaya pihak yang menjanjikan kelulusan CPNS atau PPPK, karena janji itu bohong. Plt Kepala BKN pada Oktober 2023 menegaskan pelamar tidak boleh tergiur oknum yang mengaku bisa meloloskan tanpa seleksi resmi, dan yang menyerahkan uang bisa terkena pidana. Pada 2021, Sekretaris Kementerian PAN-RB juga menyebut janji membantu lulus dengan imbalan uang sebagai penipuan.",
   "sederhana": "Lulus CPNS atau PPPK hanya lewat tes resmi, tidak bisa dibeli. Orang yang minta uang supaya \"dijamin lulus\" adalah penipu, dan yang membayar justru bisa ikut kena masalah hukum.",
   "sumber": [
    {
     "nama": "detikFinance: Nekat jadi ASN lewat jalur calo siap-siap dipidana (mengutip Plt Kepala BKN, Okt 2023)",
     "url": "https://finance.detik.com/cpns/d-6991690/nekat-jadi-asn-lewat-jalur-calo-siap-siap-dipidana",
     "jenis": "media"
    },
    {
     "nama": "Okezone: Peserta CPNS ditipu calo, BKN: seleksi transparan dan tidak bisa dimanipulasi (Sep 2021)",
     "url": "https://economy.okezone.com/read/2021/09/26/320/2477012/peserta-cpns-ditipu-calo-bkn-seleksi-transparan-dan-tidak-bisa-dimanipulasi",
     "jenis": "media"
    },
    {
     "nama": "DDTC News: Pemerintah pastikan tidak ada jalur instan lulus ASN (mengutip Sekretaris Kementerian PAN-RB, Sep 2021)",
     "url": "https://news.ddtc.co.id/berita/nasional/32595/pemerintah-pastikan-tidak-ada-jalur-instan-lulus-asn",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(cpns|pppk|asn|pns|honorer|bkn)\\b",
    "\\b(bayar|biaya|uang|transfer|calo|orang dalam|titip|titipan|pelicin|dicicil|\\d+ ?(juta|jt))\\b",
    "\\b(lulus|lolos|diangkat|pengangkatan|jalur|meloloskan|bantu)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "otp-petugas-bank",
   "kategori": "phishing",
   "klaim": "Petugas bank menghubungi nasabah lewat telepon atau pesan lalu meminta kode OTP, PIN, atau password untuk verifikasi",
   "varian": [
    "kami dari bank, ada transaksi mencurigakan, sebutkan kode otp yang dikirim ke hp bapak ibu",
    "customer service bank minta kirim kode otp dan pin untuk membatalkan transaksi",
    "petugas bank hubungi nasabah, mohon berikan kode verifikasi otp supaya rekening tidak diblokir",
    "akun mbanking anda akan diblokir, konfirmasi password dan otp ke petugas bank"
   ],
   "fakta": "BCA menyatakan di situs resminya bahwa pihaknya tidak pernah meminta kode OTP, PIN, atau password nasabah lewat telepon, SMS, email, atau media sosial, dan nasabah diminta berhenti berkomunikasi lalu memastikan lewat kanal resmi bank. OJK juga mengingatkan bahwa bank pada dasarnya tidak menghubungi nasabah lebih dulu, sehingga nasabah yang perlu urusan sebaiknya menghubungi bank sendiri.",
   "sederhana": "Bank tidak pernah meminta kode OTP, PIN, atau password lewat telepon atau pesan. Kalau ada yang mengaku petugas bank lalu memintanya, itu penipu. Putuskan dan hubungi nomor resmi bank sendiri.",
   "sumber": [
    {
     "nama": "BCA: Cukup kamu yang tahu, jangan bagikan kode OTP-mu (30 Okt 2026)",
     "url": "https://www.bca.co.id/en/informasi/awas-modus/2026/10/30/09/23/cukup-kamu-yang-tahu-jangan-bagikan-kode-otp-mu",
     "jenis": "resmi"
    },
    {
     "nama": "BCA: Waspada penipuan mengatasnamakan BCA (9 Jan 2025)",
     "url": "https://www.bca.co.id/en/informasi/awas-modus/2025/01/09/04/34/waspada-penipuan-mengatasnamakan-bca",
     "jenis": "resmi"
    },
    {
     "nama": "CNN Indonesia: Marak kasus fake BTS, OJK imbau nasabah waspada SMS OTP (12 Mar 2025)",
     "url": "https://www.cnnindonesia.com/ekonomi/20250311201554-78-1207681/marak-kasus-fake-bts-ojk-imbau-nasabah-waspada-sms-otp",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(otp|kode verifikasi|kode rahasia|pin|password|kata sandi)\\b",
    "\\b(minta|meminta|kirim|kirimkan|sebutkan|berikan|bagikan|konfirmasi|verifikasi)\\b",
    "\\b(bank|petugas|cs|customer service|call center|bca|bri|bni|mandiri|nasabah|rekening|mbanking)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "calo-akmil-akpol-bayar",
   "kategori": "penipuan_catut_tni",
   "klaim": "Ada jalur bayar atau orang dalam agar lulus seleksi Akmil atau Akpol",
   "varian": [
    "bisa dibantu lolos taruna Akmil asal siapkan uang ratusan juta lewat kenalan jenderal",
    "kuota susulan Akpol masih ada, transfer dulu biar dijamin lulus",
    "masuk Akademi Militer lewat jalur khusus orang dalam, ada biayanya",
    "calon taruna Akmil dijamin lulus kalau bayar ke panitia"
   ],
   "fakta": "Kadispenad menegaskan seleksi calon taruna Akmil tidak dipungut biaya sama sekali, dan Danrem 132/Tadulako menyebut siapa pun yang menawarkan jasa meloloskan Akmil dengan imbalan uang adalah penipu. Polri juga menyatakan masuk Akpol gratis dan mengimbau waspada penipuan berkedok kuota susulan.",
   "sederhana": "Seleksi Akmil dan Akpol gratis dan tidak ada jalur bayar. Orang yang menjanjikan lulus dengan uang adalah penipu.",
   "sumber": [
    {
     "nama": "Kumparan: Danrem 132/Tadulako, jangan percaya calo seleksi taruna Akmil",
     "url": "https://kumparan.com/paluposo/seleksi-taruna-akmil-danrem-132-tadulako-jangan-percaya-calo-mereka-penipu-1yBKnOz6UA8",
     "jenis": "media"
    },
    {
     "nama": "VOI: Kadispenad tegaskan seleksi Akmil gratis",
     "url": "https://voi.id/en/amp/403801",
     "jenis": "media"
    },
    {
     "nama": "Jawa Pos: Polri tegaskan tidak ada pungutan biaya masuk Akpol",
     "url": "https://www.jawapos.com/nasional/014716678/terapkan-prinsip-betah-polri-tegaskan-tidak-ada-pungutan-biaya-alias-gratis-untuk-masuk-akpol",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(bayar|membayar|setor|transfer|titip|titipan|calo|pelicin|orang dalam|ordal|dijamin lulus|pasti lulus|kuota susulan|\\d+ ?(juta|jt|miliar))\\b",
    "\\b(akmil|akpol|taruna|akademi militer|akademi kepolisian|catar)\\b",
    "\\b(lulus|masuk|diterima|lolos|kuota|jalur)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "surat-kelulusan-palsu-tni",
   "kategori": "penipuan_catut_tni",
   "klaim": "Surat kelulusan atau panggilan TNI yang meminta transfer biaya bertahap",
   "varian": [
    "selamat anda lulus tamtama TNI AD, ini surat kelulusannya, transfer biaya administrasi dulu",
    "surat panggilan pendidikan bintara resmi, bayar biaya pemberkasan sebelum berangkat",
    "pengumuman kelulusan prajurit TNI, harap transfer tahap kedua agar tidak digugurkan",
    "pelaku mencetak surat kelulusan TNI untuk meyakinkan korban lalu minta uang bertahap"
   ],
   "fakta": "Polisi menangkap tiga pelaku penipuan rekrutmen TNI di Kulon Progo yang mencetak surat kelulusan palsu seolah dari TNI dan meminta korban mentransfer uang bertahap hingga sekitar Rp310 juta. Di kasus lain, aparat gadungan menipu calon bintara.",
   "sederhana": "Surat kelulusan TNI yang disertai permintaan transfer pasti palsu. Kelulusan diumumkan lewat jalur resmi, tanpa biaya.",
   "sumber": [
    {
     "nama": "Metro TV: Korban penipuan rekrutmen TNI di Kulon Progo rugi Rp310 juta",
     "url": "https://www.metrotvnews.com/read/b3JCpAVL-korban-penipuan-rekrutmen-tni-di-kulon-progo-rugi-rp310-juta-tiga-pelaku-ditangkap",
     "jenis": "media"
    },
    {
     "nama": "Antara: Ini modus aparat gadungan tipu calon bintara",
     "url": "https://megapolitan.antaranews.com/berita/23840/ini-modus-aparat-gadungan-tipu-calon-bintara",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(surat|sk|panggilan|pengumuman)\\b[^.]{0,40}\\b(kelulusan|panggilan|lulus|penerimaan)\\b|\\b(kelulusan|lulus)\\b[^.]{0,30}\\b(surat|sk)\\b",
    "\\b(transfer|bayar|membayar|setor|biaya administrasi|biaya pemberkasan|biaya seragam|tahap kedua|cicil)\\b",
    "\\b(tni|tamtama|bintara|akmil|prajurit|secaba)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "akun-palsu-pejabat-militer",
   "kategori": "penipuan_catut_tni",
   "klaim": "Akun atau nomor WhatsApp yang mengaku Pangdam, perwira, atau pejabat satuan meminta uang atau bantuan",
   "varian": [
    "ini nomor baru Pangdam, tolong transfer dulu untuk keperluan dinas mendesak",
    "saya Kolonel komandan satuan, pinjam uang dulu nanti diganti, kirim ke rekening ini",
    "akun facebook atas nama Pangdam minta bantuan dana",
    "nomor wa baru Kasatker, mohon bantu transfer pulsa dan dana"
   ],
   "fakta": "Kodam III/Siliwangi pernah menemukan akun palsu yang mencatut nama Pangdam dan melaporkannya ke Puspen TNI dan Dispen TNI AD. Pola yang sama dipakai pada pejabat sipil: akun memakai foto dinas lalu meminta uang atau bantuan, dan instansi menegaskan itu penipuan.",
   "sederhana": "Pejabat tidak meminta uang lewat nomor atau akun baru. Hubungi satuannya lewat nomor resmi sebelum mentransfer apa pun.",
   "sumber": [
    {
     "nama": "Bisnis.com: Akun Facebook palsu catut nama Pangdam Siliwangi",
     "url": "https://kabar24.bisnis.com/read/20170409/78/643859/akun-facebook-palsu-catut-nama-pangdam-siliwangi",
     "jenis": "media"
    },
    {
     "nama": "Kemenkeu: Info waspada penipuan melalui WhatsApp",
     "url": "https://hai.kemenkeu.go.id/id/news/posts/pdf/info-waspada-penipuan-melalui-whatsapp",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(pangdam|danrem|dandim|kapendam|kasatker|perwira|jenderal|kolonel|letkol|panglima|komandan|kapolda|kapolres)\\b",
    "\\b(akun|nomor|no|wa|whatsapp|facebook|fb|instagram|dm|chat)\\b",
    "\\b(transfer|pinjam|pinjaman|uang|dana|bantuan|donasi|pulsa|sumbangan)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "lelang-kendaraan-dinas-palsu",
   "kategori": "penipuan_catut_tni",
   "klaim": "Mobil atau motor dinas TNI atau Polri dilelang atau dijual sangat murah, bayar DP dulu",
   "varian": [
    "lelang mobil dinas TNI murah banget, transfer DP untuk booking",
    "kendaraan inventaris Kodam dijual cepat harga miring, bayar uang muka dulu",
    "motor dinas polisi dijual murah, hubungi anggota, cod tidak bisa harus transfer",
    "obral mobil randis Kemhan, bayar panjar sekarang"
   ],
   "fakta": "DJKN mengingatkan lelang aset negara yang sah bisa dicek di lelang.go.id, dan salah satu tanda penipuan adalah janji pasti menang lelang atau penipu memakai nama KPKNL. Polisi di Jawa Barat membongkar sindikat penipu jual beli kendaraan yang berpura-pura sebagai anggota TNI dan memakai foto berseragam dinas.",
   "sederhana": "Lelang aset negara hanya lewat lelang.go.id. Penjual yang mengaku anggota TNI lalu minta DP lewat chat kemungkinan besar penipu.",
   "sumber": [
    {
     "nama": "DJKN: Waspada penipuan lelang, ikut lelang yang aman dan terpercaya",
     "url": "https://www.djkn.kemenkeu.go.id/artikel/baca/15257/Waspada-Penipuan-Lelang-Ayo-Ikut-Lelang-Yang-Aman-dan-Terpercaya.html",
     "jenis": "resmi"
    },
    {
     "nama": "DJKN: Cara mendapatkan mobil lewat lelang dan trik menghindari penipuan",
     "url": "https://www.djkn.kemenkeu.go.id/kpknl-pekanbaru/baca-artikel/13239/Cara-Mudah-Mendapatkan-Mobil-Melalui-Lelang-dengan-Harga-yang-Murah-Trik-Menghindari-Penipuan.html",
     "jenis": "resmi"
    },
    {
     "nama": "GridOto: 12 penipu jual beli kendaraan bekas di marketplace Facebook ditangkap Polda Jabar",
     "url": "https://www.gridoto.com/amp/224406385/akhirnya-12-orang-penipu-jual-beli-motor-dan-mobil-bekas-di-marketplace-facebook-dicekik-polda-jabar",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(lelang|obral|dijual|jual)\\b",
    "\\b(mobil|motor|kendaraan|randis)\\b",
    "\\b(tni|polri|polisi|kodam|kodim|kemhan|dinas|inventaris)\\b",
    "\\b(murah|dp|uang muka|transfer|booking|panjar|bayar)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-undangan-nikah-whatsapp",
   "kategori": "phishing",
   "klaim": "Undangan pernikahan digital berupa file APK yang dikirim lewat WhatsApp",
   "varian": [
    "kami mengundang bapak ibu ke pernikahan kami, silakan unduh undangan.apk",
    "undangan digital pernikahan, klik dan install aplikasi undangan di sini",
    "file undangan nikah.apk dikirim dari nomor tidak dikenal",
    "undangan resepsi pernikahan format aplikasi, pasang dulu untuk membukanya"
   ],
   "fakta": "OJK menyebut penipu menyisipkan file APK pada undangan pernikahan, tagihan BPJS, SPT pajak, hingga tilang elektronik; setelah terpasang, aplikasi bisa membaca SMS termasuk OTP dan membobol m-banking. BRI dan Bank Indonesia mengingatkan undangan digital yang sah berupa tautan, bukan file APK.",
   "sederhana": "Undangan nikah yang berupa file APK adalah jebakan. Jangan dibuka atau dipasang, hapus saja.",
   "sumber": [
    {
     "nama": "Bisnis.com: Penipu kirim WhatsApp APK bobol rekening ke Komisioner OJK",
     "url": "https://finansial.bisnis.com/read/20240313/55/1748953/nekat-penipu-kirim-whatsapp-apk-bobol-rekening-ke-komisioner-ojk",
     "jenis": "media"
    },
    {
     "nama": "Bank Indonesia: Modus penipuan online APK",
     "url": "https://www.bi.go.id/id/publikasi/ruang-media/cerita-bi/Pages/modus-penipuan-online-apk.aspx",
     "jenis": "resmi"
    },
    {
     "nama": "Bank Mandiri: Waspada modus pencurian data dengan unduh file",
     "url": "https://www.bankmandiri.co.id/waspada-modus-pencurian-data-dengan-unduh-file",
     "jenis": "resmi"
    },
    {
     "nama": "NU Online: Waspada modus penipuan undangan pernikahan bisa kuras rekening",
     "url": "https://nu.or.id/nasional/waspada-modus-penipuan-undangan-pernikahan-bisa-kuras-rekening-korban-wCg6H",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(undangan|nikah|pernikahan|resepsi|walimah|akad)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-resi-kurir-whatsapp",
   "kategori": "phishing",
   "klaim": "Kurir mengirim foto atau resi paket berupa file APK lewat WhatsApp",
   "varian": [
    "paket anda sudah sampai, lihat foto paket di file resi.apk",
    "saya kurir, ini bukti foto pengiriman, silakan install aplikasinya",
    "cek resi paket anda lewat aplikasi ini, unduh dulu",
    "kurir ekspedisi kirim file foto paket.apk dan minta bayar ulang"
   ],
   "fakta": "BCA mengingatkan penipuan kurir paket yang mengirim file APK dengan dalih foto paket; J&T Express juga memperingatkan pelanggan soal modus aplikasi palsu. OJK menyebut aplikasi itu bisa mencuri data m-banking (sniffing). Kurir resmi tidak meminta memasang aplikasi atau membayar ulang lewat chat.",
   "sederhana": "Kurir asli tidak mengirim file APK. Jangan dibuka, dan cek paket lewat aplikasi resmi ekspedisi.",
   "sumber": [
    {
     "nama": "BCA: Waspadai penipuan modus kurir paket yang mengirimkan file APK",
     "url": "https://www.bca.co.id/id/informasi/awas-modus/2022/12/14/10/11/waspadai-penipuan-dengan-modus-kurir-paket-yang-mengirimkan-file-apk",
     "jenis": "resmi"
    },
    {
     "nama": "Suara.com: J&T peringatkan pelanggan waspadai penipuan via aplikasi palsu",
     "url": "https://www.suara.com/tekno/2022/12/06/112300/jt-peringatkan-pelanggan-waspadai-viral-kasus-penipuan-via-aplikasi-palsu?page=all",
     "jenis": "media"
    },
    {
     "nama": "Bisnis.com: Viral penipuan mengaku jadi kurir paket, begini kata OJK",
     "url": "https://finansial.bisnis.com/read/20221211/90/1607375/viral-penipuan-mengaku-jadi-kurir-paket-begini-kata-ojk",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(kurir|paket|resi|ekspedisi|jnt|j&t|jne|sicepat|anteraja|pengiriman)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-tagihan-bpjs",
   "kategori": "phishing",
   "klaim": "Tagihan atau tunggakan iuran BPJS Kesehatan dikirim sebagai file APK lewat WhatsApp",
   "varian": [
    "tunggakan iuran BPJS anda, buka lembar tagihan instal.apk",
    "info tagihan BPJS Kesehatan, install aplikasi ini untuk melihat rinciannya",
    "pemberitahuan BPJS menunggak, unduh file berikut",
    "BPJS Kesehatan kirim aplikasi tagihan lewat WhatsApp"
   ],
   "fakta": "BPJS Kesehatan menyatakan pengingat tunggakan dari mereka tidak pernah disertai lampiran file; pesan dengan lampiran aplikasi atau APK tidak boleh dibuka atau diinstal. Salah satu contoh penipuan memakai file bernama 'Lembar tagihan instal.apk'.",
   "sederhana": "BPJS Kesehatan tidak mengirim tagihan berupa file atau aplikasi. Jangan dibuka dan jangan dipasang.",
   "sumber": [
    {
     "nama": "Bisnis.com: BPJS Kesehatan wanti-wanti modus penipu berkedok tagihan tunggakan iuran",
     "url": "https://finansial.bisnis.com/read/20230130/55/1622729/bpjs-kesehatan-wanti-wanti-modus-penipu-berkedok-tagihan-tunggakan-iuran",
     "jenis": "media"
    },
    {
     "nama": "Bisnis.com: Waspada WA atas nama BPJS Kesehatan yang bisa retas m-banking",
     "url": "https://finansial.bisnis.com/read/20230130/215/1622823/waspada-wa-atas-nama-bpjs-kesehatan-yang-bisa-retas-m-banking",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(bpjs|jkn|tunggakan iuran|iuran)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-surat-pajak-djp",
   "kategori": "phishing",
   "klaim": "Surat pajak atau SPT dari DJP dikirim sebagai file APK atau aplikasi lewat WhatsApp",
   "varian": [
    "SPT kurang bayar anda, buka file ini segera",
    "surat teguran pajak.apk dari kantor pajak",
    "install aplikasi coretax versi mobile dari link ini untuk lapor pajak",
    "surat tagihan pajak berformat pdf ternyata harus diinstal"
   ],
   "fakta": "Ditjen Pajak menegaskan tidak pernah mengirim file berekstensi APK; pesan seperti itu harus diabaikan, dan email resmi DJP hanya memakai domain @pajak.go.id. Penipu memberi nama file seperti 'SPT Kurang Bayar' atau 'Surat Teguran' agar penerima panik.",
   "sederhana": "DJP tidak pernah mengirim file APK. Pesan pajak yang meminta memasang aplikasi adalah penipuan.",
   "sumber": [
    {
     "nama": "DJP: Waspada penipuan, DJP selalu amankan seluruh data wajib pajak",
     "url": "https://pajak.go.id/id/artikel/waspada-penipuan-djp-selalu-amankan-seluruh-data-wajib-pajak",
     "jenis": "resmi"
    },
    {
     "nama": "Bisnis.com: Awas ada penipuan di musim lapor pajak berupa file APK",
     "url": "https://ekonomi.bisnis.com/read/20240124/259/1735083/waspada-awas-ada-penipuan-di-musim-lapor-pajak-berupa-file-apk",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(pajak|spt|djp|coretax|surat teguran)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-tagihan-pln",
   "kategori": "phishing",
   "klaim": "Tagihan listrik PLN dikirim sebagai file APK atau aplikasi lewat pesan",
   "varian": [
    "tagihan listrik anda menunggak, install aplikasi PLN dari file ini",
    "petugas PLN kirim lampiran tagihan.apk",
    "listrik akan diputus hari ini, unduh aplikasi pembayaran dari tautan"
   ],
   "fakta": "Media teknologi melaporkan pelaku yang mengaku petugas PLN mengirim APK berkedok tagihan listrik untuk mengambil data korban; saran umumnya memeriksa pengirim dan memverifikasi ke call center resmi. Catatan: sumber ini hanya media, bukan pernyataan PLN, jadi verifikasi lewat kanal resmi PLN.",
   "sederhana": "Tagihan listrik tidak datang berupa file APK. Cek tagihan hanya lewat aplikasi atau layanan resmi PLN.",
   "sumber": [
    {
     "nama": "VIVA: Hindari jebakan penipu, begini cara aman dari serangan file APK",
     "url": "https://techno.viva.co.id/lifestyle/2775-hindari-jebakan-penipu-begini-cara-aman-dari-serangan-file-apk?page=1",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(pln|listrik|token listrik)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "apk-undangan-pemilu-pps",
   "kategori": "phishing",
   "klaim": "Undangan PPS atau KPU untuk pemilu dikirim sebagai file APK lewat WhatsApp",
   "varian": [
    "undangan pencoblosan pemilu dari PPS, install aplikasinya",
    "surat undangan KPPS berbentuk apk dikirim ke WhatsApp warga",
    "pemberitahuan pemilih dari KPU, unduh aplikasi ini"
   ],
   "fakta": "Bisnis.com melaporkan modus undangan PPS Pemilu yang pola kerjanya sama dengan undangan pernikahan palsu: file APK yang bisa menguras rekening setelah dipasang.",
   "sederhana": "Undangan pemilu resmi tidak berupa file APK. Jangan dibuka dan jangan dipasang.",
   "sumber": [
    {
     "nama": "Bisnis.com: Waspada modus penipuan undangan PPS Pemilu di WA, lakukan ini jika telanjur klik",
     "url": "https://finansial.bisnis.com/read/20240115/90/1732310/waspada-modus-penipuan-undangan-pps-pemilu-di-wa-lakukan-ini-jika-telanjur-klik",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(pps|kpps|pemilu|pilkada|kpu|pencoblosan)\\b",
    "(\\.apk|\\bapk\\b|aplikasi|\\b(unduh|download|install|instal|pasang)\\w*)"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "deepfake-pejabat-saham-grup-wa",
   "kategori": "penipuan_investasi",
   "klaim": "Video pejabat bank sentral atau menteri keuangan merekomendasikan saham dan mengajak masuk grup WhatsApp",
   "varian": [
    "Deputi Gubernur BI rekomendasikan saham cuan, gabung grup WhatsApp ini",
    "Menteri Keuangan ajak masyarakat investasi, penghasilan Rp100 juta per bulan lewat grup WA",
    "video Menkeu bagikan tips trading saham, klik tautan grup",
    "pejabat negara umumkan program investasi, daftar lewat WhatsApp"
   ],
   "fakta": "Bank Indonesia menyatakan video yang mencatut Deputi Gubernur Senior adalah deepfake dan bahwa pejabat bank sentral tidak pernah memberi rekomendasi saham atau mengajak masuk grup WhatsApp pribadi; Kemenkeu juga menyebut video Menkeu sebagai hoaks deepfake.",
   "sederhana": "Itu video buatan AI. Pejabat tidak pernah mengajak masuk grup WhatsApp untuk investasi.",
   "sumber": [
    {
     "nama": "Katadata: Nama Deputi Gubernur BI dan Menkeu dicatut hoaks rekomendasi saham",
     "url": "https://katadata.co.id/digital/teknologi/6a60b3e6dca91/waspada-nama-deputi-gubernur-bi-dan-menkeu-dicatut-hoaks-rekomendasi-saham",
     "jenis": "media"
    },
    {
     "nama": "Bisnis.com: Bareskrim gandeng Komdigi cegah kasus video deepfake AI",
     "url": "https://kabar24.bisnis.com/read/20250123/16/1834393/bareskrim-gandeng-komdigi-cegah-kasus-video-deepfake-ai",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(deputi gubernur|gubernur bi|bank indonesia|menkeu|menteri keuangan|purbaya|destry|sri mulyani|presiden|prabowo|pejabat)\\b",
    "\\b(saham|investasi|trading|cuan|profit|keuntungan|penghasilan)\\b",
    "\\b(grup|group|gabung|join|whatsapp|wa|tautan|link|daftar)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "anak-kecelakaan-minta-transfer",
   "kategori": "penipuan_telepon",
   "klaim": "Telepon atau pesan mengabarkan anak atau keluarga kecelakaan atau ditangkap dan minta uang segera",
   "varian": [
    "bu anak ibu kecelakaan di sekolah harus dioperasi, tolong transfer sekarang",
    "suami ibu ditangkap polisi kasus narkoba, kirim uang damai agar dilepas",
    "kami dari rumah sakit, anak bapak celaka, transfer biaya operasi segera",
    "anak anda disandera, siapkan tebusan transfer sekarang juga"
   ],
   "fakta": "Polisi di sejumlah daerah memperingatkan modus 'anak kecelakaan': pelaku menelepon orang tua, berperan sebagai guru, dokter, atau polisi, lalu menekan korban agar transfer. Imbauannya, tutup telepon lalu hubungi anak, sekolah, atau keluarga lewat nomor yang sudah dikenal.",
   "sederhana": "Jangan panik dan jangan transfer. Tutup telepon, lalu hubungi anak atau keluarga lewat nomor yang Ibu atau Bapak kenal.",
   "sumber": [
    {
     "nama": "JPNN: Kombes Eko Saputro, waspada aksi penipuan modus kecelakaan",
     "url": "https://m.jpnn.com/news/kombes-eko-saputro-waspada-aksi-penipuan-modus-kecelakaan",
     "jenis": "media"
    },
    {
     "nama": "Jawa Pos: Penipuan modus baru, anak kecelakaan",
     "url": "https://www.jawapos.com/kasuistika/1611060159/penipuan-modus-baru-yakni-anak-kecelakaan",
     "jenis": "media"
    },
    {
     "nama": "BCA: Awas modus ngaku-ngaku orang yang kamu kenal padahal penipu",
     "url": "https://www.bca.co.id/id/informasi/awas-modus/2021/01/06/09/15/Awas-Modus-Ngaku-ngaku-Orang-Yang-Kamu-Kenal-Padahal-Penipu",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(anak|anaknya|suami|istri|ibu|bapak|keluarga|saudara|adik|kakak)\\b",
    "\\b(kecelakaan|celaka|ditangkap|ditahan|dioperasi|operasi|disandera|narkoba)\\b",
    "\\b(transfer|tebusan|kirim(kan)? uang|setor|uang damai)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "hadiah-undian-catut-ecommerce",
   "kategori": "phishing",
   "klaim": "Anda menang undian atau hadiah dari Shopee, bank, atau e-commerce, klik tautan untuk klaim",
   "varian": [
    "selamat anda pemenang undian Shopee, klaim hadiah lewat link ini",
    "voucher cashback Rp2 juta dari Shopee, klik tautan untuk mengambil",
    "pengumuman pemenang hadiah resmi, isi data dan bayar biaya admin",
    "anda terpilih menerima hadiah dari bank, konfirmasi lewat tautan berikut"
   ],
   "fakta": "Shopee Indonesia menyatakan pengumuman pemenang undian yang beredar bukan dari Shopee, dan domain resminya hanya shopee.co.id dan id.shp.ee; Shopee tidak meminta OTP atau data pribadi lewat telepon, pesan, atau email.",
   "sederhana": "Undian dadakan lewat tautan adalah penipuan. Pemenang resmi tidak diminta bayar atau mengisi data lewat link.",
   "sumber": [
    {
     "nama": "Kompas: Hoaks pengumuman pemenang hadiah undian Shopee 2021",
     "url": "https://www.kompas.com/tren/read/2021/03/29/123000965/-hoaks-pengumuman-pemenang-hadiah-undian-shopee-2021?page=all",
     "jenis": "cek_fakta"
    },
    {
     "nama": "RRI: Hoaks tautan untuk klaim voucher cashback Rp2 juta dari Shopee",
     "url": "https://rri.co.id/banjarmasin/cek-fakta/2177538/hoaks-tautan-untuk-klaim-voucher-cashback-rp2-juta-dari-shopee",
     "jenis": "cek_fakta"
    },
    {
     "nama": "detikInet: Kenali modus penipuan fake BTS yang catut nama Shopee",
     "url": "https://inet.detik.com/security/d-7988830/kenali-modus-penipuan-fake-bts-yang-catut-nama-shopee",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(selamat|pemenang|menang|terpilih|hadiah|undian|voucher|cashback)\\b",
    "\\b(shopee|tokopedia|tiktok shop|lazada|bank|bca|bri|bni|mandiri)\\b",
    "\\b(klik|tautan|link|isi data|klaim|konfirmasi|biaya|admin)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "investasi-pinjol-ilegal-untung-pasti",
   "kategori": "penipuan_investasi",
   "klaim": "Investasi atau pinjaman online tanpa izin OJK yang menjanjikan untung besar atau cair cepat tanpa syarat",
   "varian": [
    "investasi untung pasti 10 persen per hari tanpa risiko, modal kecil",
    "pinjaman online cair 5 menit tanpa jaminan tanpa survei",
    "member baru dapat bonus, profit harian dijamin berlipat",
    "gabung trading robot, keuntungan dijamin tiap minggu"
   ],
   "fakta": "OJK dan Satgas PASTI terus menghentikan ratusan entitas pinjol ilegal dan penawaran investasi ilegal, dan mengimbau waspada tawaran untung tinggi, pasti, dan cepat; legalitas bisa dicek lewat Kontak OJK 157, WhatsApp 081157157157, atau konsumen@ojk.go.id.",
   "sederhana": "Untung besar yang pasti dan cepat adalah tanda penipuan. Cek dulu izinnya di OJK (157) sebelum menyetor uang.",
   "sumber": [
    {
     "nama": "OJK: Satgas PASTI hentikan 953 entitas pinjol ilegal dan penawaran investasi ilegal (Mei 2026)",
     "url": "https://ojk.go.id/id/berita-dan-kegiatan/info-terkini/Pages/Satgas-PASTI-Hentikan-953-Entitas-Pinjol-Ilegal-dan-Penawaran-Investasi-Ilegal-Mei-2026.aspx",
     "jenis": "resmi"
    },
    {
     "nama": "OJK: Satgas PASTI blokir 585 pinjol ilegal dan pinpri serta 17 investasi ilegal",
     "url": "https://ojk.go.id/waspada-investasi/id/siaran-pers/Pages/Satgas-Pasti-Blokir-585-Pinjol-Ilegal-dan-Pinpri-serta-17-Investasi-Ilegal-.aspx",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(investasi|pinjaman|pinjol|dana tunai|modal|trading|member)\\b",
    "\\b(untung|profit|cuan|keuntungan|return|bagi hasil|bonus|cair)\\b",
    "\\b(pasti|dijamin|tanpa risiko|tanpa jaminan|tanpa survei|per hari|perhari|harian|mingguan|berlipat|5 menit|\\d+ ?%|\\d+ persen)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "lowongan-kerja-bumn-palsu-bayar",
   "kategori": "penipuan_rekrutmen",
   "klaim": "Lowongan kerja BUMN atau instansi pemerintah yang meminta biaya pendaftaran atau tes",
   "varian": [
    "lowongan Pertamina dibuka, transfer biaya tes kesehatan dulu",
    "rekrutmen BUMN lewat WhatsApp, bayar biaya administrasi untuk dipanggil",
    "lowongan BNN, hubungi nomor ini dan setor biaya pendaftaran",
    "info loker Telkom, ada biaya seragam dan pemberkasan"
   ],
   "fakta": "Liputan6 mencatat hoaks lowongan BUMN yang meminta korban mentransfer biaya transport atau tes kesehatan, dan Telkom memperingatkan agar waspada info lowongan yang memungut biaya. Rekrutmen Bersama BUMN dilakukan daring lewat situs resmi tanpa pungutan.",
   "sederhana": "Lowongan resmi BUMN dan instansi tidak memungut biaya. Yang meminta transfer adalah penipu.",
   "sumber": [
    {
     "nama": "Liputan6 Cek Fakta: Deretan hoaks lowongan kerja mengatasnamakan BUMN",
     "url": "https://www.liputan6.com/cek-fakta/read/4358081/deretan-hoaks-lowongan-kerja-mengatasnamakan-bumn",
     "jenis": "cek_fakta"
    },
    {
     "nama": "detikFinance: Hati-hati marak info loker bodong atas nama Telkom",
     "url": "https://finance.detik.com/bumn/d-7272271/hati-hati-marak-info-loker-bodong-atas-nama-telkom-ini-yang-benar",
     "jenis": "media"
    },
    {
     "nama": "Tirto: Hoaks lowongan kerja mengatasnamakan BNN",
     "url": "https://tirto.id/hoaks-lowongan-kerja-mengatasnamakan-bnn-g497",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(lowongan|rekrutmen|loker|lamaran|penerimaan pegawai)\\b",
    "\\b(bumn|pertamina|pln|telkom|kai|bni|bri|bnn|bnpb|kementerian|bpom|peruri|bappenas)\\b",
    "\\b(bayar|membayar|transfer|setor|biaya (administrasi|pendaftaran|tes|seleksi|seragam|pemberkasan|transport)|uang (muka|jaminan|pendaftaran)|deposit)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "cpns-portal-surat-panggilan-palsu",
   "kategori": "penipuan_rekrutmen",
   "klaim": "Link pendaftaran atau surat panggilan tes CPNS dari situs selain portal resmi SSCASN",
   "varian": [
    "link pendaftaran CPNS resmi di sscasn-bkn.com, isi data dan bayar biaya",
    "surat panggilan tes CPNS dikirim lewat WhatsApp, buka bknindonesia.id",
    "info pendaftaran CPNS dari poster ini, transfer biaya pendaftaran dulu",
    "panggilan palsu CPNS pengganti, hubungi nomor ini"
   ],
   "fakta": "BKN menegaskan informasi dan proses seleksi CPNS/PPPK hanya lewat portal resmi SSCASN (sscasn.bkn.go.id) dan kanal resmi pemerintah, tanpa biaya, serta mengimbau tidak percaya pada poster, broadcast, atau tautan dari sumber lain; BKN juga pernah mengingatkan soal panggilan palsu CPNS.",
   "sederhana": "Pendaftaran CPNS hanya lewat sscasn.bkn.go.id dan gratis. Link atau poster lain, apalagi yang minta bayar, adalah penipuan.",
   "sumber": [
    {
     "nama": "Setkab: Termasuk simulasi soal, BKN banyak modus penipuan jelang penerimaan CPNS",
     "url": "https://setkab.go.id/termasuk-simulasi-soal-bkn-banyak-modus-penipuan-jelang-penerimaan-cpns/",
     "jenis": "resmi"
    },
    {
     "nama": "detikFinance: Poster pendaftaran CPNS 2026 hoaks",
     "url": "https://finance.detik.com/berita-ekonomi-bisnis/d-8517357/poster-pendaftaran-cpns-2026-hoaks",
     "jenis": "cek_fakta"
    },
    {
     "nama": "Kompas TV: BKN minta masyarakat waspada panggilan palsu terkait CPNS pengganti",
     "url": "https://www.kompas.tv/article/298859/bkn-minta-masyarakat-waspada-panggilan-palsu-terkait-cpns-pengganti",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(cpns|casn|sscasn|pppk|bkn)\\b",
    "\\b(surat panggilan|panggilan tes|link pendaftaran|tautan pendaftaran|poster|pendaftaran dibuka|pendaftaran|panggilan)\\b",
    "\\b(bayar|membayar|transfer|biaya (pendaftaran|administrasi)|bknindonesia|bkn-gov|sscasn-bkn)\\b|\\b[a-z0-9-]+\\.(com|xyz|top|site|online|info|biz|cc)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "herbal-sembuhkan-semua-penyakit",
   "kategori": "kesehatan",
   "klaim": "Satu ramuan atau obat herbal bisa menyembuhkan kanker, diabetes, dan berbagai penyakit sekaligus",
   "varian": [
    "daun ajaib ini menyembuhkan kanker dan diabetes tanpa obat dokter",
    "ramuan herbal ampuh sembuhkan sepuluh penyakit sekaligus",
    "jamu alami hilangkan tumor stroke dan asam urat dalam seminggu",
    "satu produk suplemen bisa mengobati semua penyakit"
   ],
   "fakta": "Kemenkes menyebut klaim bahwa satu obat dapat menyembuhkan banyak penyakit sebagai hoaks dan menegaskan tidak mungkin ada satu obat untuk semua penyakit; obat herbal harus melalui pembuktian ilmiah. Mafindo menilai klaim rumput Paragis menyembuhkan kanker sebagai hoaks.",
   "sederhana": "Tidak ada satu ramuan yang menyembuhkan semua penyakit. Untuk kanker dan diabetes, tetap ikuti pengobatan dokter.",
   "sumber": [
    {
     "nama": "Kemenkes: Tidak ada satu obat yang menyembuhkan berbagai penyakit",
     "url": "https://kemkes.go.id/id/tidak-ada-satu-obat-yang-menyembuhkan-berbagai-penyakit",
     "jenis": "resmi"
    },
    {
     "nama": "MerahPutih: Hoaks atau fakta rumput paragis dapat obati kanker",
     "url": "https://merahputih.com/post/read/hoaks-atau-fakta-rumput-paragis-dapat-obati-kanker/",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(herbal|jamu|ramuan|obat alami|daun|rempah|suplemen|produk)\\b",
    "\\b(menyembuhkan|sembuhkan|mengobati|obati|menghilangkan|hilangkan|membasmi|sembuh)\\b",
    "\\b(kanker|diabetes|kencing manis|tumor|jantung|stroke|asam urat|alzheimer|semua penyakit|berbagai penyakit|sepuluh penyakit|10 penyakit)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "herbal-sembuhkan-tbc",
   "kategori": "kesehatan",
   "klaim": "Obat herbal atau ramuan bisa menyembuhkan TBC tanpa obat dari dokter",
   "varian": [
    "ramuan herbal ini sembuhkan TBC tanpa OAT",
    "jamu alami obati tuberkulosis tuntas, tidak perlu minum obat enam bulan",
    "TBC paru sembuh dengan rempah dapur"
   ],
   "fakta": "Juru bicara Kemenkes menegaskan belum ada bukti ilmiah bahwa obat herbal dapat menyembuhkan TBC; CNBC Indonesia (2026) juga mengulas klaim herbal TBC sebagai menyesatkan. Pengobatan TBC mengikuti terapi dari fasilitas kesehatan.",
   "sederhana": "Belum ada bukti herbal menyembuhkan TBC. Berobat ke puskesmas dan habiskan obat yang diberikan.",
   "sumber": [
    {
     "nama": "detikHealth: Video Kemenkes, belum ada bukti ilmiah obat herbal bisa sembuhkan TBC",
     "url": "https://health.detik.com/detiktv/d-8403254/video-kemenkes-belum-ada-bukti-ilmiah-obat-herbal-bisa-sembuhkan-tbc",
     "jenis": "media"
    },
    {
     "nama": "CNBC Indonesia: Jangan ikut tersesat klaim herbal bisa obati TBC",
     "url": "https://www.cnbcindonesia.com/lifestyle/20260321150733-33-720623/pokoknya-jangan-ikut-tersesat-klaim-herbal-bisa-obati-tbc-ini-faktanya",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(herbal|jamu|ramuan|obat alami|rempah)\\b",
    "\\b(menyembuhkan|sembuhkan|mengobati|obati|sembuh|tuntas)\\b",
    "\\b(tbc|tuberkulosis|tb paru)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "polisi-penyidikan-online-transfer",
   "kategori": "penipuan_telepon",
   "klaim": "Penelepon mengaku polisi, jaksa, atau penyidik, menyebut Anda terlibat kasus dan meminta uang jaminan atau denda",
   "varian": [
    "kami dari Bareskrim, rekening anda dipakai pencucian uang, transfer ke rekening aman",
    "anda tersangka kasus narkoba paket, penyidikan online lewat video call, setor uang jaminan",
    "penyidik kejaksaan hubungi anda, bayar denda agar kasus dihentikan"
   ],
   "fakta": "Metro TV melaporkan imbauan agar masyarakat waspada penipuan modus 'penyidikan online' yang menekan korban lewat telepon atau video call. Polisi tidak memeriksa atau menagih uang lewat telepon; Korlantas menyebut hal semacam itu hanya mungkin dilakukan oknum dan menyarankan melapor ke kantor polisi terdekat.",
   "sederhana": "Polisi atau jaksa tidak menyelidiki lewat telepon dan tidak minta transfer. Tutup telepon dan datangi kantor polisi.",
   "sumber": [
    {
     "nama": "Metro TV: Masyarakat diminta waspadai penipuan modus penyidikan online",
     "url": "https://www.metrotvnews.com/read/NOlC9Qar-masyarakat-diminta-waspadai-penipuan-modus-penyidikan-online",
     "jenis": "media"
    },
    {
     "nama": "GridOto: Awas modus baru penipuan mengatasnamakan polisi",
     "url": "https://www.gridoto.com/read/01227324/awas-modus-baru-penipuan-mengatasnamakan-polisi",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(polisi|polda|polres|penyidik|bareskrim|kejaksaan|jaksa|kepolisian|bnn|ojk|siber)\\b",
    "\\b(terlibat|tersangka|kasus|narkoba|pencucian uang|rekening anda|nama anda|paket)\\b",
    "\\b(transfer|setor|rekening aman|rekening penampungan|uang jaminan|jaminan|denda|uang damai|tebusan|penyidikan online|sidang online|video call)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "lowongan-mbg-tautan-palsu",
   "kategori": "penipuan_rekrutmen",
   "klaim": "Tautan pendaftaran lowongan kerja program Makan Bergizi Gratis (MBG) lewat link atau WhatsApp",
   "varian": [
    "pendaftaran lowongan SPPG program MBG 2026 klik link ini",
    "dibuka rekrutmen relawan makan bergizi gratis, isi formulir dan bayar admin",
    "loker ahli gizi MBG daftar lewat WhatsApp nomor ini"
   ],
   "fakta": "RRI Cek Fakta menandai tautan pendaftaran lowongan kerja untuk program MBG 2026 yang beredar sebagai hoaks.",
   "sederhana": "Tautan lowongan MBG yang beredar di pesan berantai itu hoaks. Cek lowongan hanya lewat kanal resmi instansi.",
   "sumber": [
    {
     "nama": "RRI Cek Fakta: Hoaks tautan pendaftaran lowongan kerja untuk program MBG 2026",
     "url": "https://rri.co.id/banjarmasin/cek-fakta/2177548/hoaks-tautan-pendaftaran-lowongan-kerja-untuk-program-mbg-2026",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(mbg|makan bergizi gratis|sppg|ahli gizi|relawan)\\b",
    "\\b(lowongan|rekrutmen|pendaftaran|daftar|loker)\\b",
    "\\b(tautan|link|klik|formulir|bayar|biaya|admin|whatsapp|wa)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "calo-akpol-bintara-polri",
   "kategori": "penipuan_rekrutmen",
   "klaim": "Ada jalur bayar atau orang dalam agar lulus Akpol atau bintara Polri",
   "varian": [
    "bisa bantu anak lulus Akpol, siapkan satu miliar lewat orang dalam",
    "bintara Polri dijamin lulus asal setor uang ke panitia",
    "kuota susulan Akpol masih tersedia, transfer dulu",
    "titip masuk polisi lewat kenalan di Polda, ada pelicinnya"
   ],
   "fakta": "Polri menegaskan tidak ada pungutan biaya untuk masuk Akpol dan mengimbau waspada penipuan modus kuota susulan. Polresta Pati pada 2026 mengungkap penipuan yang menjanjikan kelulusan Akpol dengan nilai transaksi Rp1,5 miliar.",
   "sederhana": "Masuk Akpol dan Polri gratis. Siapa pun yang menjanjikan lulus dengan uang adalah penipu.",
   "sumber": [
    {
     "nama": "Jawa Pos: Polri tegaskan tidak ada pungutan biaya masuk Akpol",
     "url": "https://www.jawapos.com/nasional/014716678/terapkan-prinsip-betah-polri-tegaskan-tidak-ada-pungutan-biaya-alias-gratis-untuk-masuk-akpol",
     "jenis": "media"
    },
    {
     "nama": "RMOL: Seleksi Catar Akpol rampung, Polri imbau waspada penipuan modus kuota susulan",
     "url": "https://rmol.id/read/2024/07/31/630762/seleksi-catar-akpol-rampung-polri-imbau-waspada-penipuan-modus-kuota-susulan",
     "jenis": "media"
    },
    {
     "nama": "RMOL: Warga Pati jadi korban penipuan masuk Akpol bayar Rp1,5 miliar",
     "url": "https://rmol.id/read/2026/05/27/708643/warga-pati-jadi-korban-penipuan-masuk-akpol-bayar-rp1-5-miliar",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(bayar|membayar|setor|transfer|titip|titipan|calo|pelicin|orang dalam|ordal|dijamin lulus|pasti lulus|kuota susulan|\\d+ ?(juta|jt|miliar))\\b",
    "\\b(akpol|bintara polri|tamtama polri|polri|polda|sepa|setukpa|calon polisi|masuk polisi|catar)\\b",
    "\\b(lulus|masuk|diterima|lolos|kuota|jalur)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "pembajakan-whatsapp-kode-verifikasi",
   "kategori": "phishing",
   "klaim": "Pesan meminta Anda mengirim kode verifikasi 6 digit WhatsApp yang 'salah kirim' atau untuk keperluan lain",
   "varian": [
    "maaf kode 6 digit WhatsApp nyasar ke nomor kamu, tolong kirimkan",
    "ini teman kamu, aku lagi ganti nomor, minta kode verifikasi yang masuk ke HP kamu",
    "saya petugas WhatsApp, sebutkan kode enam digit untuk verifikasi akun",
    "tolong teruskan kode yang baru masuk lewat SMS"
   ],
   "fakta": "Pelaku membajak akun WhatsApp lalu meminta kontak korban mengirim kode verifikasi 6 digit dengan alasan salah kirim atau mengaku staf WhatsApp; setelah akun diambil alih, korban dan kontaknya dimintai pulsa atau transfer. Jangan pernah membagikan kode 6 digit kepada siapa pun dan aktifkan verifikasi dua langkah.",
   "sederhana": "Kode 6 digit WhatsApp rahasia. Jangan dikirim ke siapa pun, termasuk yang mengaku teman atau petugas WhatsApp.",
   "sumber": [
    {
     "nama": "CNBC Indonesia: Kamu harus waspada, ini tanda WhatsApp mau dibajak",
     "url": "https://www.cnbcindonesia.com/tech/20210212061331-37-222897/kamu-harus-waspada-ini-tanda-whatsapp-mau-dibajak",
     "jenis": "media"
    },
    {
     "nama": "detikInet: Waspada penipuan teman gadungan di WhatsApp",
     "url": "https://inet.detik.com/security/d-4418667/waspada-penipuan-teman-gadungan-di-whatsapp",
     "jenis": "media"
    }
   ],
   "syarat": [
    "\\b(kode|otp|verifikasi|6 digit|enam digit)\\b",
    "\\b(whatsapp|wa|salah kirim|nyasar|terkirim)\\b",
    "\\b(tolong|minta|mohon|kirimkan|sebutkan|berikan|bagikan|teruskan|forward)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "biaya-masuk-akmil-hoaks",
   "kategori": "penipuan_catut_tni",
   "klaim": "Beredar poster atau rincian biaya pendaftaran dan pendidikan masuk Akmil atau TNI AD",
   "varian": [
    "rincian biaya masuk Akmil 2024 ratusan juta",
    "poster biaya pendaftaran taruna Akmil, ada tarif tiap tahap",
    "informasi biaya pendaftaran prajurit TNI AD jalur khusus"
   ],
   "fakta": "Dispenad membantah kabar biaya masuk Akmil dan menegaskan tidak ada pungutan biaya pendaftaran maupun pendidikan; pernyataan itu juga tercantum di situs resmi TNI.",
   "sederhana": "Tidak ada tarif masuk Akmil atau TNI AD. Rincian biaya yang beredar itu palsu.",
   "sumber": [
    {
     "nama": "VOI: Kadispenad tegaskan seleksi Akmil gratis, bantah masuk TNI berbayar",
     "url": "https://voi.id/en/amp/403801",
     "jenis": "media"
    },
    {
     "nama": "Kemhan: TNI AD bertekad berantas praktik percaloan seleksi tentara",
     "url": "https://www.kemhan.go.id/itjen/2015/01/15/tni-ad-bertekad-berantas-praktik-percaloan-seleksi-tentara.html",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(rincian|tarif|poster|daftar|informasi)\\b[^.]{0,30}\\bbiaya\\b|\\bbiaya (masuk|pendaftaran|pendidikan)\\b",
    "\\b(akmil|taruna|tni ad|prajurit|tamtama|bintara)\\b",
    "\\b\\d+ ?(juta|jt|ribu|rb|miliar)\\b|\\b(rp ?\\d|ratusan juta|jutaan)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "bantuan-bpjs-puluhan-juta",
   "kategori": "penipuan_bansos",
   "klaim": "BPJS Kesehatan membagikan bantuan atau hadiah puluhan juta rupiah kepada peserta lewat WhatsApp",
   "varian": [
    "peserta BPJS Kesehatan dapat bantuan Rp21 juta, daftar lewat WhatsApp",
    "hadiah dari BPJS Kesehatan untuk peserta aktif, hubungi nomor ini",
    "program bantuan BPJS puluhan juta, kirim KTP dan KK"
   ],
   "fakta": "Pimpinan BPJS Kesehatan mengingatkan peserta agar tidak tertipu penipuan berkedok hadiah, dan media cek fakta mencatat penipuan 'bantuan BPJS Kesehatan' senilai puluhan juta yang meminta data pribadi lewat WhatsApp.",
   "sederhana": "BPJS Kesehatan tidak membagi bantuan atau hadiah lewat WhatsApp. Jangan kirim KTP atau KK ke nomor itu.",
   "sumber": [
    {
     "nama": "Bisnis.com: Bos BPJS Kesehatan ingatkan peserta tidak tertipu penipuan berkedok hadiah",
     "url": "https://finansial.bisnis.com/read/20230202/215/1624163/bos-bpjs-kesehatan-ingatkan-peserta-tidak-tertipu-penipuan-berkedok-hadiah",
     "jenis": "media"
    },
    {
     "nama": "Tirto: Penipuan berkedok bantuan BPJS Kesehatan senilai puluhan juta",
     "url": "https://tirto.id/penipuan-berkedok-bantuan-bpjs-kesehatan-senilai-puluhan-juta-gYfk",
     "jenis": "cek_fakta"
    }
   ],
   "syarat": [
    "\\b(bpjs|jkn)\\b",
    "\\b(bantuan|hadiah|dana|santunan|bonus|cair)\\b",
    "\\b(whatsapp|wa|nomor|hubungi|daftar|kirim|ktp|kk|link|tautan)\\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "obat-cacing-imunisasi-virus-baru",
   "kategori": "kesehatan",
   "klaim": "Obat cacing dan imunisasi menyebarkan virus baru",
   "varian": [
    "imunisasi anak justru menyebarkan virus baru",
    "obat cacing dari puskesmas membawa virus baru",
    "program imunisasi dan obat cacing sengaja menularkan virus"
   ],
   "fakta": "Cek fakta Tirto menyimpulkan klaim bahwa obat cacing dan imunisasi menyebarkan virus baru tidak benar. Catatan: ringkasan ini hanya mengikuti judul cek fakta tersebut; buka artikelnya untuk rinciannya.",
   "sederhana": "Tidak benar. Obat cacing dan imunisasi tidak menyebarkan virus baru.",
   "sumber": [
    {
     "nama": "Tirto: Tidak benar obat cacing dan imunisasi sebarkan virus baru",
     "url": "https://tirto.id/tidak-benar-obat-cacing-dan-imunisasi-sebarkan-virus-baru-hhxJ",
     "jenis": "cek_fakta"
    },
    {
     "nama": "Kemenkes: Kemenkes serius perangi hoax kesehatan",
     "url": "https://www.kemkes.go.id/id/kemenkes-serius-perangi-hoax-kesehatan",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\b(obat cacing|imunisasi|vaksin|vaksinasi)\b",
    "\b(menyebarkan|sebarkan|menularkan|tularkan|virus baru|penyebab|sengaja)\b"
   ],
   "jenis": "bantahan",
   "kutipan_sumber": "",
   "valid_from": null,
   "valid_until": null,
   "wilayah": "",
   "tolak": [],
   "signed": false
  },
  {
   "id": "resmi-portal-rekrutmen-tni-ad",
   "kategori": "buletin_resmi",
   "klaim": "Pendaftaran calon Bintara dan Tamtama PK TNI AD lewat portal resmi ad.rekrutmen-tni.mil.id dan seluruh tahapan seleksinya gratis",
   "varian": [
    "pendaftaran bintara TNI AD 2027 dibuka lewat ad.rekrutmen-tni.mil.id, gratis",
    "rekrutmen tamtama TNI AD resmi di ad.rekrutmen-tni.mil.id tanpa biaya",
    "semua tahapan seleksi TNI AD gratis dan tidak dipungut biaya",
    "pendaftaran prajurit TNI AD gratis lewat situs rekrutmen resmi",
    "pendaftaran tamtama TNI AD dilakukan secara online melalui situs resmi penerimaan, seluruh tahapannya tidak dipungut biaya"
   ],
   "fakta": "Portal resmi rekrutmen TNI AD (ad.rekrutmen-tni.mil.id) menyatakan: \"Semua tahapan seleksi hingga kelulusan masuk pendidikan adalah Gratis dan tidak dipungut biaya\". Portal itu memuat pendaftaran calon Bintara PK dan Tamtama PK TNI AD gelombang I TA 2027.",
   "sederhana": "Pendaftaran resmi TNI AD hanya lewat ad.rekrutmen-tni.mil.id dan semua tahapannya gratis.",
   "sumber": [
    {
     "nama": "Portal Rekrutmen TNI AD (ad.rekrutmen-tni.mil.id)",
     "url": "https://ad.rekrutmen-tni.mil.id/",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(bintara|tamtama|prajurit|tni ad)\\b",
    "\\b(gratis|tidak dipungut biaya|tanpa biaya|bebas biaya)\\b"
   ],
   "jenis": "verifikasi_positif",
   "kutipan_sumber": "Semua tahapan seleksi hingga kelulusan masuk pendidikan adalah Gratis dan tidak dipungut biaya",
   "valid_from": "2026-11-20",
   "valid_until": "2027-02-06",
   "wilayah": "Nasional",
   "tolak": [
    "\\b(bayar|membayar|transfer|setor|calo|pelicin|orang dalam|ordal|titip|titipan|dp|uang muka|cicil)\\b",
    "\\b(rp ?\\d|\\d+ ?(juta|jt|ribu|rb|miliar))\\b"
   ],
   "signed": true
  },
  {
   "id": "resmi-ppid-tni-ad-seleksi-gratis",
   "kategori": "buletin_resmi",
   "klaim": "Seleksi calon Tamtama, Bintara, Catar Akademi TNI, dan Sepa PK TNI AD sama sekali tidak dipungut biaya",
   "varian": [
    "seleksi calon tamtama bintara dan akademi TNI AD tidak dipungut biaya",
    "proses seleksi prajurit TNI AD gratis, biaya pendidikan ditanggung negara",
    "masuk TNI AD tidak dipungut biaya sama sekali"
   ],
   "fakta": "PPID TNI AD menyatakan: \"Proses seleksi Calon Tamtama, Bintara, Catar Akademi TNI dan Sepa PK TNI AD sama sekali tidak dipungut biaya (GRATIS).\" Setelah dinyatakan lulus, seluruh biaya pendidikan ditanggung penuh oleh negara.",
   "sederhana": "Seleksi masuk TNI AD sama sekali tidak dipungut biaya, dan biaya pendidikan ditanggung negara.",
   "sumber": [
    {
     "nama": "PPID TNI AD: Rekrutmen TNI Angkatan Darat",
     "url": "https://ppid.tniad.mil.id/index.php/i/22364/rekrutmen-tni-angkatan-darat",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\b(bintara|tamtama|prajurit|akademi|tni ad)\\b",
    "\\b(gratis|tidak dipungut biaya|tanpa biaya|bebas biaya)\\b"
   ],
   "jenis": "verifikasi_positif",
   "kutipan_sumber": "Proses seleksi Calon Tamtama, Bintara, Catar Akademi TNI dan Sepa PK TNI AD sama sekali tidak dipungut biaya (GRATIS).",
   "valid_from": "2025-02-12",
   "valid_until": "2027-06-30",
   "wilayah": "Nasional",
   "tolak": [
    "\\b(bayar|membayar|transfer|setor|calo|pelicin|orang dalam|ordal|titip|titipan|dp|uang muka|cicil)\\b",
    "\\b(rp ?\\d|\\d+ ?(juta|jt|ribu|rb|miliar))\\b"
   ],
   "signed": true
  },
  {
   "id": "resmi-sscasn-portal-cpns",
   "kategori": "buletin_resmi",
   "klaim": "Portal seleksi CPNS dan PPPK resmi adalah sscasn.bkn.go.id",
   "varian": [
    "pendaftaran CPNS lewat sscasn.bkn.go.id",
    "portal resmi seleksi CASN BKN adalah sscasn.bkn.go.id",
    "daftar PPPK di sscasn.bkn.go.id"
   ],
   "fakta": "Situs sscasn.bkn.go.id memuat judul \"SSCASN - Sistem Seleksi Calon Aparatur Sipil Negara\" dan merupakan portal seleksi CASN milik BKN. Pernyataan ini hanya tentang alamat portal, bukan tentang jadwal atau formasi.",
   "sederhana": "Portal seleksi CASN yang resmi beralamat sscasn.bkn.go.id.",
   "sumber": [
    {
     "nama": "BKN: SSCASN - Sistem Seleksi Calon Aparatur Sipil Negara",
     "url": "https://sscasn.bkn.go.id/",
     "jenis": "resmi"
    }
   ],
   "syarat": [
    "\\bsscasn\\.bkn\\.go\\.id\\b",
    "\\b(cpns|pppk|casn|pendaftaran|seleksi|portal|daftar)\\b"
   ],
   "jenis": "verifikasi_positif",
   "kutipan_sumber": "SSCASN - Sistem Seleksi Calon Aparatur Sipil Negara",
   "valid_from": "2026-11-20",
   "valid_until": "2027-11-20",
   "wilayah": "Nasional",
   "tolak": [
    "\\b(bayar|membayar|transfer|setor|calo|pelicin|orang dalam|ordal|titip|titipan|dp|uang muka|cicil|biaya)\\b",
    "\\b(rp ?\\d|\\d+ ?(juta|jt|ribu|rb|miliar))\\b"
   ],
   "signed": true
  }
 ],
 "slang": {
  "yg": "yang",
  "dgn": "dengan",
  "utk": "untuk",
  "krn": "karena",
  "tdk": "tidak",
  "gak": "tidak",
  "ga": "tidak",
  "gk": "tidak",
  "nggak": "tidak",
  "engga": "tidak",
  "sdh": "sudah",
  "udah": "sudah",
  "blm": "belum",
  "bs": "bisa",
  "bisa2": "bisa",
  "org": "orang",
  "skrg": "sekarang",
  "hr": "hari",
  "jg": "juga",
  "aja": "saja",
  "dr": "dari",
  "pd": "pada",
  "sm": "sama",
  "bgt": "banget",
  "tsb": "tersebut",
  "pak": "bapak",
  "bu": "ibu",
  "wa": "whatsapp",
  "japri": "whatsapp",
  "chat": "whatsapp",
  "lwt": "lewat",
  "lewat2": "lewat",
  "klo": "kalau",
  "kalo": "kalau",
  "dlm": "dalam",
  "tmn": "teman",
  "trf": "transfer",
  "tf": "transfer",
  "covid19": "covid",
  "covid-19": "covid",
  "rb": "ribu",
  "jt": "juta"
 },
 "phrases": [
  [
   "(?<![a-z0-9])(?:orang\\s+dalam|ordal|kenalan\\s+(?:di\\s+)?(?:perwira|kodam|korem|kodim|tni|jenderal|petinggi|pejabat|panitia)|kenalan\\s+orang\\s+dalam|relasi\\s+(?:di\\s+)?(?:kodam|tni|panitia)|jalur\\s+(?:belakang|dalam|khusus|titipan)|titipan)(?![a-z0-9])",
   "caloordal"
  ],
  [
   "(?<![a-z0-9])(?:(?:dijamin|jamin|pasti|100\\s*%|seratus\\s+persen)\\s+(?:lulus|masuk|diterima|lolos)|lulus\\s+(?:pasti|dijamin|100\\s*%))(?![a-z0-9])",
   "jaminlulus"
  ],
  [
   "(?<![a-z0-9])(?:uang\\s+pelicin|pelicin|uang\\s+rokok|uang\\s+lelah|uang\\s+muka|uang\\s+jasa|uang\\s+administrasi\\s+khusus|mahar|setoran)(?![a-z0-9])",
   "biayailegal"
  ]
 ],
 "stopwords": [
  "ada",
  "adalah",
  "agar",
  "akan",
  "anda",
  "atau",
  "bahwa",
  "banyak",
  "berita",
  "besok",
  "bila",
  "bisa",
  "dalam",
  "dan",
  "dapat",
  "dari",
  "deh",
  "dengan",
  "di",
  "dong",
  "hanya",
  "hari",
  "info",
  "ingin",
  "ini",
  "itu",
  "jika",
  "juga",
  "kabar",
  "kah",
  "kalau",
  "kami",
  "kamu",
  "karena",
  "ke",
  "kemarin",
  "kemudian",
  "kita",
  "kok",
  "lah",
  "lalu",
  "lebih",
  "maka",
  "mau",
  "mereka",
  "mohon",
  "nih",
  "nya",
  "oleh",
  "pada",
  "paling",
  "para",
  "pun",
  "saja",
  "sana",
  "sangat",
  "saya",
  "sebagai",
  "sedikit",
  "semua",
  "serta",
  "setiap",
  "sih",
  "sini",
  "sudah",
  "supaya",
  "telah",
  "tersebut",
  "tidak",
  "tolong",
  "tuh",
  "untuk",
  "ya",
  "yah",
  "yang"
 ],
 "claimCues": [
  "akan",
  "bantuan",
  "biaya",
  "bmkg",
  "dibagikan",
  "diblokir",
  "dibuka",
  "dijamin",
  "dilarang",
  "diprediksi",
  "ditangkap",
  "ditemukan",
  "ditutup",
  "gempa",
  "gratis",
  "hadiah",
  "harga",
  "juta",
  "kalah",
  "kemenkes",
  "korban",
  "kuota",
  "lipat",
  "lulus",
  "membagikan",
  "memblokir",
  "menang",
  "mencatat",
  "mengandung",
  "mengobati",
  "meninggal",
  "menteri",
  "menyebabkan",
  "menyembuhkan",
  "miliar",
  "naik",
  "obat",
  "pemerintah",
  "penculik",
  "penculikan",
  "pendaftaran",
  "persen",
  "polri",
  "prediksi",
  "presiden",
  "resmi",
  "ribu",
  "saldo",
  "sudah",
  "tanggal",
  "telah",
  "terbukti",
  "terjadi",
  "tni",
  "transfer",
  "tsunami",
  "turun",
  "vaksin",
  "virus",
  "wajib"
 ],
 "opinionCues": [
  "menurut saya",
  "menurutku",
  "saya rasa",
  "aku rasa",
  "kayaknya",
  "semoga",
  "selamat pagi",
  "selamat siang",
  "selamat malam",
  "assalamualaikum",
  "amin",
  "salam sehat",
  "terima kasih",
  "mohon maaf"
 ],
 "regex": {
  "negation": "\\b(tidak|tak|tanpa|bukan|gak|nggak|belum|jangan)\\b[\\w\\s]{0,10}$",
  "defused": "^[\\s:,-]{0,3}(\\w+\\s){0,1}(gratis|nol rupiah|rp ?0\\b|tidak dipungut|tanpa (biaya|dipungut))",
  "correction": "\\b(hoaks|hoax|kabar bohong|berita bohong|disinformasi|misinformasi|tidak benar|membantah|dibantah|bantahan|(meng|di)?klarifikasi(kan)?|(me|di)?luruskan|pelurusan|menepis|ditepis|menyangkal|disangkal|(isu|kabar|informasi|video|pesan)( itu| tersebut)? (adalah |itu )?(tidak benar|hoaks|hoax|bohong|palsu)|tidak ada bukti|tidak terbukti|belum terbukti|modus penipuan|adalah (penipu|penipuan|calo)|itu (penipu|penipuan)|waspada (calo|penipu|penipuan|modus)|(hati-hati|hati hati|awas|waspadai) (terhadap )?(penipuan|penipu|calo|modus|hoaks|hoax|video palsu|akun palsu|tautan palsu)|(memakai|menggunakan|pakai|berupa) (video|foto|akun|suara) (palsu|rekayasa|deepfake)|jangan (mudah )?(percaya|tertipu|terkecoh)( (pada|kepada|dengan|sama))? (calo|penipu|oknum|tautan|link|pesan berantai)|(menangkap|meringkus|membekuk|memburu|menindak) (oknum |para |seorang )?(calo|penipu|pelaku penipuan|komplotan penipu))\\b",
  "notCorrection": "\\b(bukan|tidak|gak|nggak|bkn) (hoaks|hoax)\\b",
  "pipelineUrl": "https?://\\S+",
  "url": "https?://\\S+|www\\.\\S+",
  "bare": "(?<![\\w@.-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+(?:id|com|net|org|xyz|info|site|online|top|ly|me|io|co|click|link|biz|ee|at|gl))(?=[/:?#]|\\s|$|[.,)!])",
  "bareWithPath": "(?<![\\w@.-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+(?:id|com|net|org|xyz|info|site|online|top|ly|me|io|co|click|link|biz|ee|at|gl))(?=[/:?#]|\\s|$|[.,)!])(?:[/?#]\\S*)?"
 },
 "scrub": [
  [
   "\\b\\d{2}[\\s.-]?\\d{2}[\\s.-]?\\d{2}[\\s.-]?\\d{6}[\\s.-]?\\d{4}\\b",
   "[NIK]"
  ],
  [
   "[\\w.+-]+@[\\w-]+\\.[\\w.-]+",
   "[EMAIL]"
  ],
  [
   "(?:\\+?62[\\s.-]?|\\(?0)8\\d{1,3}\\)?(?:[\\s.-]?\\d{2,5}){2,3}\\b",
   "[NOMOR]"
  ],
  [
   "\\b\\d{10,15}\\b",
   "[REKENING]"
  ],
  [
   "(?<!\\w)@\\w{3,}",
   "[AKUN]"
  ]
 ],
 "techniques": [
  [
   "ajakan_sebar",
   "Desakan untuk menyebarkan",
   "Pesan ini menyuruh Anda meneruskannya. Info yang benar tidak perlu memaksa.",
   "Pesan yang berbunyi 'sebarkan!' atau 'jangan berhenti di Anda' sedang memakai Anda sebagai pengantar. Berhenti dulu, cek dulu.",
   [
    "\\bsebar(kan|luaskan)?\\b",
    "\\bviral(kan)?\\b",
    "\\bteruskan\\b",
    "\\bbagikan\\b",
    "jangan berhenti di",
    "kirim(kan)? ke \\d+",
    "\\bshare\\b",
    "broadcast"
   ]
  ],
  [
   "urgensi",
   "Dibuat terburu-buru",
   "Pesan ini membuat Anda merasa harus bertindak sekarang juga.",
   "Penipu ingin Anda bergerak sebelum berpikir. Batas waktu palsu seperti 'hari ini terakhir' adalah tanda bahaya.",
   [
    "\\bsegera\\b",
    "sekarang juga",
    "\\bburuan\\b",
    "hari ini terakhir",
    "batas (waktu|akhir)",
    "\\bcepat\\b",
    "terbatas",
    "\\b(hanya|cuma) \\d+ (jam|hari)"
   ]
  ],
  [
   "otoritas_palsu",
   "Mengaku dari orang penting",
   "Pesan ini mengaku berasal dari pejabat, dokter, atau 'orang dalam' tanpa sumber yang bisa dicek.",
   "Kalimat 'info dari teman di kepolisian' atau 'kata dokter' tanpa nama dan tautan resmi tidak bisa dipercaya begitu saja.",
   [
    "info (a1|valid|dari dalam)",
    "orang dalam",
    "kata (dokter|intel|teman)",
    "(dari|menurut) (grup|teman) sebelah",
    "sumber terpercaya",
    "info dari (polda|polres|kodim|kodam|mabes)",
    "\\bresmi dari\\b"
   ]
  ],
  [
   "rasa_takut",
   "Menakut-nakuti",
   "Pesan ini memakai rasa takut agar Anda tidak sempat berpikir jernih.",
   "Rasa takut membuat kita cepat percaya. Kata seperti 'waspada', 'bahaya', atau 'penculik' perlu dicek ke sumber resmi.",
   [
    "\\bwaspada\\b",
    "\\bbahaya\\b",
    "\\bawas\\b",
    "mematikan",
    "penculik",
    "\\bdarurat\\b",
    "\\bmencekam\\b",
    "tsunami besar",
    "gempa besar"
   ]
  ],
  [
   "iming_iming",
   "Iming-iming hadiah",
   "Pesan ini menjanjikan uang, hadiah, atau kelulusan dengan mudah.",
   "Kalau terdengar terlalu bagus untuk jadi kenyataan, biasanya memang tidak nyata. Bantuan resmi tidak meminta biaya.",
   [
    "\\bgratis\\b",
    "\\bhadiah\\b",
    "bantuan (tunai|langsung|sosial)",
    "\\bbansos\\b",
    "dijamin lulus",
    "kuota \\d+ ?gb",
    "saldo",
    "\\bbonus\\b",
    "rp ?\\d"
   ]
  ],
  [
   "minta_data_uang",
   "Meminta data atau uang",
   "Pesan ini meminta data pribadi, kode OTP, atau transfer uang.",
   "Lembaga resmi tidak pernah meminta kode OTP, PIN, atau 'biaya administrasi' lewat chat. Jangan isi tautan yang meminta data.",
   [
    "biaya (admin|administrasi|pendaftaran)",
    "\\btransfer\\b",
    "kode otp",
    "\\botp\\b",
    "\\bpin\\b",
    "isi (data|formulir)",
    "klik (link|tautan)",
    "\\bnik\\b",
    "nomor rekening"
   ]
  ]
 ],
 "orgs": {
  "BMKG": "bmkg|badan meteorologi",
  "BNPB": "bnpb|badan nasional penanggulangan bencana",
  "PMI": "pmi|palang merah",
  "WHO": "who|organisasi kesehatan dunia",
  "Kemenkes": "kemenkes|kementerian kesehatan",
  "Kemensos": "kemensos|kementerian sosial",
  "Komdigi": "komdigi|kominfo|kementerian komunikasi",
  "TNI": "tni|tentara nasional",
  "Polri": "polri|kepolisian",
  "BPOM": "bpom|badan pom",
  "OJK": "ojk|otoritas jasa keuangan",
  "BI": "bank indonesia",
  "BPJS": "bpjs",
  "KPU": "kpu|komisi pemilihan umum",
  "Presiden": "presiden|prabowo|jokowi",
  "Pemerintah": "pemerintah"
 },
 "statusLabel": {
  "terbukti_salah": "Terbukti salah",
  "sejalan_dengan_sumber": "Sejalan dengan sumber",
  "dilaporkan_media": "Dilaporkan media",
  "tidak_yakin": "Halio tidak yakin",
  "belum_ada_pemeriksaan": "Belum ada pemeriksaan"
 },
 "severity": [
  "terbukti_salah",
  "tidak_yakin",
  "belum_ada_pemeriksaan",
  "dilaporkan_media",
  "sejalan_dengan_sumber"
 ],
 "short": {
  "terbukti_salah": "sudah dibantah",
  "tidak_yakin": "belum bisa dipastikan",
  "belum_ada_pemeriksaan": "belum ada yang memeriksa",
  "dilaporkan_media": "dilaporkan beberapa media",
  "sejalan_dengan_sumber": "sejalan dengan sumber resmi"
 },
 "plainKinds": [
  "berita_media_dikenal",
  "kumpulan_judul"
 ],
 "shorteners": [
  "bit.ly",
  "cutt.ly",
  "linktr.ee",
  "rb.gy",
  "s.id",
  "shorturl.at",
  "t.ly",
  "tinyurl.com",
  "wa.me"
 ],
 "officialSuffixes": [
  ".go.id",
  ".mil.id"
 ],
 "disclaimer": "Halio tidak membuat vonis sendiri. Hasil ini berasal dari pemeriksa fakta atau sumber resmi yang disebutkan."
};

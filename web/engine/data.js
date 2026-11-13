// file ini digenerate otomatis lewat scripts/build_engine_data.py dr kode python + data/debunks.json, jgn diedit manual ya
globalThis.HalioEngineData = {
 "version": "luring-1",
 "corpusSha256": "d4ebb4bac9270fa530be6b5ebd9a7abb5202cab7c86db298ef2c420e6ca67926",
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
    "bantuan tunai dari presiden untuk rakyat, chat nomor WhatsApp untuk mendaftar lalu bayar biaya admin"
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
   ]
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
   ]
  },
  {
   "id": "bmkg-prediksi-gempa-tanggal",
   "kategori": "bencana",
   "klaim": "Akan terjadi gempa besar dan tsunami pada tanggal tertentu menurut prediksi BMKG",
   "varian": [
    "BMKG memprediksi gempa magnitudo 9 akan terjadi minggu depan",
    "waspada tsunami besar tanggal 20 desember sampai 23 januari",
    "akan ada gempa susulan M 9.0 setelah gempa banten",
    "prediksi gempa 7 SR dalam 10 hari ke depan, segera mengungsi"
   ],
   "fakta": "BMKG berulang kali menegaskan bahwa belum ada teknologi di dunia yang bisa memprediksi tanggal, lokasi, dan kekuatan gempa secara pasti, dan BMKG tidak pernah mengeluarkan prediksi semacam itu. Informasi gempa dan peringatan tsunami resmi hanya dari kanal BMKG.",
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
    }
   ],
   "syarat": [
    "\\b(gempa|tsunami)\\b",
    "\\b(akan|diprediksi|memprediksi|prediksi)\\b(\\W+\\w+){0,8}\\W+(terjadi|datang|melanda|minggu depan|bulan depan|tanggal|dalam \\d+ (hari|minggu))|\\b(minggu depan|bulan depan|tanggal \\d+|dalam \\d+ (hari|minggu))\\b"
   ]
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
   ]
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
   ]
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
   ]
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
   ]
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
   ]
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
   ]
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
   ]
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
  "covid19": "covid",
  "covid-19": "covid",
  "rb": "ribu",
  "jt": "juta"
 },
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

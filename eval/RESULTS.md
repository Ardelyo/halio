# Halio offline evaluation

Two hand-written sets, both by the team, so neither is a benchmark. The number to watch is the
false-hoax rate: a true statement labelled "terbukti salah". Retrieval only (no LLM, no ClaimReview).

## dev: testset.jsonl

Tuning set: the rules were adjusted while looking at these. 62 hand-written items (22 paraphrases of known debunks, 36 true/unknown statements, 4 opinions/greetings). Written by the team, so results are optimistic. Not a benchmark.

Thresholds: match >= 0.4, unsure >= 0.26. Mode: retrieval only (no LLM, no ClaimReview).

| Metric | Value |
|---|---|
| False-hoax rate (true/unknown labelled 'terbukti salah') | **0%** (0/36) |
| Recall on paraphrased known hoaxes | 100% |
| Matched the wrong debunk | 0 |
| Correct abstain on true/unknown | 100% |
| Opinion/greeting detected | 100% |

### Per item

| ok | expected | status | reason | score | text |
|---|---|---|---|---|---|
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.421 | Bapak ibu, ada video Pak Prabowo bagi-bagi uang tunai buat rakyat, lan |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.467 | Daftar bantuan langsung tunai dari Presiden, cukup kirim KTP ke WhatsA |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.491 | INFO VALID!! Menteri keuangan umumkan bansos tunai, pendaftaran lewat  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.884 | Ada kenalan di kodam bisa bantu anak ibu lulus tes tamtama TNI AD, dij |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.624 | Jalur khusus masuk tentara, pasti lulus, bayar ke orang dalam |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.622 | Penerimaan bintara TNI AD tahun ini ada jalur titipan, hubungi saya, b |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.496 | Menurut BMKG akan terjadi gempa magnitudo 8,9 disertai tsunami tanggal |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.865 | WASPADA!!! gempa besar diprediksi terjadi minggu depan di pulau jawa,  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.592 | Prediksi gempa susulan lebih besar M9 akan datang dalam 3 hari |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.601 | Obat covid paling ampuh: air kelapa muda campur garam dan perasan jeru |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.509 | air klapa + garem + jeruk nipis bs nyembuhin corona, udh dibuktiin |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.524 | Selamat! Telkomsel XL Indosat bagi kuota gratis 50GB dalam rangka HUT  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.616 | Kominfo bagikan subsidi kuota internet gratis, daftar di tautan lalu b |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.612 | Jasa Marga kasih saldo e-toll gratis 100 ribu buat pengguna tol, klaim |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.544 | Hati-hati ada komplotan penculik anak naik mobil putih keliling sekola |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.558 | Waspada penculikan anak di kampung kita, pelaku menyamar jadi orang gi |
| ✅ | not_debunked | sejalan_dengan_sumber | cocok_dengan_buletin_resmi | 0.437 | Pendaftaran rekrutmen TNI AD 2026 dibuka secara online dan tidak dipun |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.474 | BMKG mencatat gempa magnitudo 5,1 di selatan Jawa pagi ini, tidak berp |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Pemerintah menyalurkan bansos beras lewat kantor pos dan bank Himbara, |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.383 | Air kelapa mengandung elektrolit seperti kalium yang membantu menggant |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.301 | Jasa Marga memberlakukan diskon tarif tol 20 persen saat libur Natal |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.287 | Polisi menangkap pelaku penculikan anak di Bogor setelah laporan warga |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Harga cabai di pasar naik dua kali lipat karena musim hujan |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.371 | Minum air rebusan daun sirsak setiap hari bisa menyembuhkan kanker sta |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Vaksin terbaru mengandung chip untuk melacak masyarakat, sebarkan sebe |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Jembatan Suramadu akan ditutup total selama seminggu mulai besok |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Timnas Indonesia menang 2-0 tadi malam |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Bank akan memblokir semua rekening yang tidak aktif tiga bulan mulai J |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Selamat pagi keluarga, semoga hari ini penuh berkah. Amin |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Menurut saya pemerintah harus lebih memperhatikan petani |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Apa kabar semuanya? Sudah makan belum? |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Terima kasih atas doanya, mohon maaf lahir batin |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.292 | Pemerintah resmi membuka pendaftaran bansos PKH tahap 2, cek nama pene |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.432 | Presiden Prabowo membagikan bantuan sembako kepada warga di Jakarta ha |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.364 | BMKG: gempa magnitudo 5,3 mengguncang Cianjur, tidak berpotensi tsunam |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.277 | BMKG akan memperbarui peringatan dini cuaca ekstrem pekan depan, panta |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.269 | BMKG mengimbau masyarakat waspada potensi gempa besar di zona megathru |
| ✅ | not_debunked | sejalan_dengan_sumber | cocok_dengan_buletin_resmi | 0.463 | Pendaftaran Bintara TNI AD 2026 dibuka tanggal 5 Januari melalui pener |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.434 | Rekrutmen tamtama TNI AD gratis tidak dipungut biaya, waspada calo yan |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Kodam Jaya buka pendaftaran Bintara, hubungi panitia di kodam untuk in |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.542 | Air kelapa muda baik untuk menjaga hidrasi, bisa diminum dengan sediki |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.421 | Dokter menyarankan minum air kelapa dan jeruk nipis untuk menjaga daya |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.289 | Telkomsel memberi bonus kuota gratis 5GB untuk pelanggan setia yang me |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Telkomsel bagikan kuota gratis untuk korban banjir, daftar lewat aplik |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Kominfo meluncurkan program internet gratis di desa terpencil lewat sa |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.459 | Jasa Marga memberikan diskon tarif tol 20 persen, saldo e-toll bisa di |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.439 | Hati-hati penculikan anak, polisi sudah menangkap pelakunya di Bekasi, |
| ✅ | not_debunked | tidak_yakin | bukan_klaim_faktual | - | Waspada penipuan online yang mengatasnamakan bank, jangan bagikan kode |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.406 | Polisi mengimbau warga waspada berita hoaks penculikan anak yang bered |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.323 | Hubungi nomor 112 untuk layanan darurat, gratis dari semua operator |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.296 | Daftar BPJS Kesehatan gratis untuk warga kurang mampu lewat kantor des |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.265 | Pemerintah akan membagikan bantuan tunai Rp600 ribu untuk pekerja berg |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.387 | BMKG Papua Mengklarifikasi Isu Akan Terjadi Tsunami di Papua |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.398 | BMKG menepis kabar akan terjadi tsunami besar di Papua pekan depan |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.581 | Kemenkes meluruskan isu air kelapa campur garam bisa menyembuhkan covi |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.349 | Polres menyangkal kabar penculikan anak dengan mobil putih di Bekasi |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.615 | Pak, ada surat tilang digital dari polisi di WA, katanya harus install |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.655 | KAMU KENA E-TILANG! Unduh aplikasi APK ini di whatsapp untuk cek surat |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.697 | Bisa bantu anak lulus CPNS tahun ini lewat orang dalam, bayar dulu 80  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.631 | Ada jalur khusus PPPK, transfer uang pelicin ke kenalan di instansi pa |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.427 | Kami dari bank, ada transaksi mencurigakan di rekening Anda. Sebutkan  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.486 | Customer service bank menghubungi nasabah, minta kirim PIN dan passwor |

## holdout: holdout.jsonl

Held-out set: written before the guard fix and never tuned on. 62 hand-written items (16 paraphrases of known debunks, 40 true/unknown statements, 6 opinions/greetings). Written by the team, so results are optimistic. Not a benchmark.

Thresholds: match >= 0.4, unsure >= 0.26. Mode: retrieval only (no LLM, no ClaimReview).

| Metric | Value |
|---|---|
| False-hoax rate (true/unknown labelled 'terbukti salah') | **0%** (0/40) |
| Recall on paraphrased known hoaxes | 100% |
| Matched the wrong debunk | 0 |
| Correct abstain on true/unknown | 100% |
| Opinion/greeting detected | 83% |

### Per item

| ok | expected | status | reason | score | text |
|---|---|---|---|---|---|
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.535 | Bapak2 ibu2 ada bantuan tunai dari Pak Presiden 5 juta per KK, japri n |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.512 | Video Ibu Menkeu: bantuan sosial tunai cair minggu ini, daftar via Wha |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.518 | presiden prabowo bagi2 duit 10jt bagi yg follow & share video ini |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.43 | Mau anaknya jadi tentara? Saya punya orang dalam di Kodam, pasti lulus |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.499 | Dibuka jalur titipan Tamtama TNI AD, DP 20jt sisanya setelah pengumuma |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.433 | bisa bantu masuk bintara TNI lwt kenalan perwira, ada uang pelicin dik |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.413 | BMKG memprediksi gempa M8,7 dan tsunami akan melanda selatan Jawa tang |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.452 | Info dari teman di BMKG, gempa besar akan datang dalam 5 hari, jangan  |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.531 | akan ada gempa susulan lebih besar M9 minggu depan, sebarin ke keluarg |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.601 | Ramuan air kelapa hijau ditambah garam dan jeruk nipis terbukti menyem |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.482 | kalo kena corona minum aja air kelapa campur garem, manjur bgt |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.406 | Kuota gratis 40GB dari Telkomsel Indosat XL untuk merayakan ulang tahu |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.525 | Subsidi kuota internet dari pemerintah 50GB, isi data di link ini lalu |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.59 | Klaim saldo e-toll gratis Rp200.000 dari Jasa Marga, buka link dan isi |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.522 | Ada komplotan penculik anak keliling pakai mobil van hitam di dekat SD |
| ✅ | terbukti_salah | terbukti_salah | cocok_dengan_bantahan | 0.571 | Awas penculik anak menyamar jadi pengemis keliling kampung, share ke g |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Pemerintah mulai menyalurkan BLT Dana Desa bulan ini lewat kantor desa |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.387 | Presiden Prabowo meninjau penyaluran bantuan pangan beras di gudang Bu |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.36 | Kemensos mengingatkan bansos tidak pernah dipungut biaya dan tidak did |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.38 | Hati-hati video Presiden bagi-bagi uang itu hoaks buatan AI, jangan tr |
| ✅ | not_debunked | sejalan_dengan_sumber | cocok_dengan_buletin_resmi | 0.473 | Pendaftaran Tamtama TNI AD gelombang 2 dibuka mulai 1 Juli, seluruh ta |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.275 | Kodam XV Pattimura memburu oknum calo penerimaan prajurit yang merugik |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.319 | Awas penipuan rekrutmen TNI AD, siapa pun yang menjanjikan pasti lulus |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.342 | Seleksi Bintara TNI AD meliputi tes kesehatan, jasmani, psikologi, dan |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.346 | BMKG: gempa M4,8 guncang Sukabumi pukul 03.15 WIB, tidak berpotensi ts |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.433 | BMKG menegaskan sampai saat ini belum ada teknologi yang bisa mempredi |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.331 | BMKG memprakirakan hujan lebat akan terjadi di Jabodetabek pada Jumat  |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.486 | Pesan prediksi gempa besar minggu depan itu hoaks, BMKG sudah membanta |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.306 | Air kelapa bisa membantu mencegah dehidrasi saat diare, tapi bukan pen |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.523 | Tidak ada bukti air kelapa dan garam menyembuhkan covid, kata Kementer |
| ✅ | not_debunked | tidak_yakin | bukan_klaim_faktual | - | Jeruk nipis kaya vitamin C yang baik untuk daya tahan tubuh |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Indosat memberikan bonus kuota 10GB untuk pembelian paket tertentu di  |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.37 | Komdigi mengingatkan pesan kuota gratis dari pemerintah yang meminta k |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | XL Axiata memperluas jaringan 5G di 10 kota baru tahun ini |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.422 | Jasa Marga mengimbau pengguna tol memastikan saldo kartu e-toll cukup  |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.688 | Jasa Marga membantah membagikan saldo e-toll gratis lewat link, itu pe |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.29 | Polres Bekasi menangkap dua pelaku penculikan anak, korban sudah kemba |
| ✅ | not_debunked | tidak_yakin | tampak_meluruskan | 0.306 | Polisi memastikan kabar penculikan anak di grup WhatsApp warga tidak b |
| ✅ | not_debunked | tidak_yakin | bukan_klaim_faktual | - | Orang tua diimbau mengajari anak untuk tidak ikut orang asing |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | KPAI mencatat kasus kekerasan anak meningkat dibanding tahun lalu |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Mulai tahun depan semua kendaraan wajib memakai pelat nomor warna puti |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Garam beryodium wajib untuk mencegah gondok, kata Kemenkes |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Daftar ulang SIM Card wajib paling lambat akhir bulan atau nomor diblo |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Pemerintah akan menaikkan harga BBM bulan depan |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.3 | Ada promo tiket kereta gratis untuk lansia, cek di aplikasi Access by  |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Kapal Pelni tenggelam di perairan Maluku, 12 penumpang hilang |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Makan bawang putih mentah setiap pagi menyembuhkan darah tinggi |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Uang kertas Rp1.000 bergambar Pattimura akan ditarik dan tidak berlaku |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Kodim 0501 menggelar donor darah bersama warga dalam rangka HUT TNI |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.409 | Prajurit TNI AD membantu evakuasi korban banjir di Demak |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Selamat ulang tahun Pak RT, semoga sehat selalu |
| ❌ | opinion | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Saya kurang setuju kalau sekolah masuk jam 6 pagi |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Ada yang tahu bengkel motor yang buka hari Minggu? |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Semangat ya buat yang mau tes CPNS besok! |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Wah lucu banget kucingnya |
| ✅ | opinion | tidak_yakin | bukan_klaim_faktual | - | Mohon doanya untuk ibu saya yang sedang dirawat |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.37 | Polisi mengirim surat konfirmasi tilang ETLE lewat PT Pos Indonesia ke |
| ✅ | not_debunked | belum_ada_pemeriksaan | tidak_ada_bantahan | - | Cek status pelanggaran lalu lintas lewat situs resmi ETLE Korlantas Po |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.47 | Pendaftaran CPNS dilakukan lewat portal resmi SSCASN BKN dan tidak dip |
| ✅ | not_debunked | tidak_yakin | bukan_klaim_faktual | - | Pengumuman kelulusan seleksi PPPK akan diumumkan lewat akun SSCASN pes |
| ✅ | not_debunked | tidak_yakin | inti_klaim_tidak_ada | 0.504 | Bank tidak pernah meminta kode OTP lewat telepon, jangan berikan OTP k |
| ✅ | not_debunked | tidak_yakin | mirip_tapi_tidak_sama | 0.273 | Kode OTP Anda 482913, berlaku 5 menit. Jangan berikan kode ini kepada  |

## History (honest record)

| When | dev false-hoax | holdout false-hoax | holdout recall |
|---|---|---|---|
| Before the guard fix (audit, Oct 2026) | 6/32 | 5/34 | 81% |
| Guard fix, first holdout run | 0/32 | 1/34 | 88% |
| After adding "tidak ada bukti / tidak terbukti" as a correction cue | see above | see above | see above |
| v1.0: phrase canonicalisation (ordal, pelicin, pasti lulus...) + corpus 10 -> 35 + signed bulletin registry | 0/36 | 0/40 | 100% |

The last two rows were changed after looking at holdout failures (the two TNI AD broker paraphrases at 0.33 / 0.369, then three
holdout items that dropped under the threshold when the corpus grew and IDF shifted; the fix was extra paraphrase variants on the
older entries). The holdout is therefore NO LONGER CLEAN: its 100% recall is a tuned number, not an estimate. Do not quote it as accuracy.
The next fresh set should be written by someone outside the team, from real forwarded messages.

## Known limitations

- Both sets were written by the same people who wrote the corpus. Real forwarded messages will be messier.
- Same-topic TRUE statements score close to the threshold; that is why the 'tidak yakin' band exists.
- Retrieval is lexical; heavy paraphrase without shared words is missed (falls to 'belum ada pemeriksaan', which is safe).
- The optional LLM/web-agent step (HALIO_LLM=1) is not measured here. Live sources, quotes, latency and provider
  availability need a separate online evaluation. It may only confirm a hoax, or lift a 'mirip' case when the
  core-claim guard and the correction check both pass, with an exact quote.

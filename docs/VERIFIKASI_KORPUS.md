# Verifikasi Sumber Korpus Bantahan

> **Jenis:** Bukti · **Untuk:** juri · [Peta dokumen](README.md)

Tanggal pemeriksaan: **10 Nov 2026**. Berkas: `data/debunks.json` (7 entri awal, 14 tautan; tiga entri ditambah 13 Nov, lihat bagian akhir). Setiap tautan dibuka dengan program (HTTP GET, User-Agent beridentitas). Halaman yang menolak program dibaca dari salinan Internet Archive. Kolom "Eksplisit?" menjawab satu pertanyaan: **apakah halaman itu sendiri menyatakan klaim tersebut salah, bohong, hoaks, penipuan, atau tidak terbukti**, bukan sekadar membahas topiknya. Catatan berisi ringkasan dengan kata-kata kami sendiri; teks artikel tidak disalin.

Isi `data/debunks.json` **tidak diubah** dalam pemeriksaan ini. Usulan perubahan ada di bagian akhir.

| Entri | Sumber | HTTP | Eksplisit? | Catatan |
|---|---|---|---|---|
| `bansos-deepfake-presiden` | Katadata (mengutip Bareskrim Polri) | 200 | **Ya** | Bareskrim menjelaskan video bansos memakai wajah Presiden dan Menkeu hasil deepfake, korban diminta membayar biaya administrasi lewat WhatsApp; pelaku ditangkap dan dijerat pasal penipuan. |
| `rekrutmen-tni-ad-berbayar` | Bisnis.com: Syarat dan Cara Daftar Rekrutmen TNI AD 2026 | **403** (Cloudflare menolak program); dibaca dari Wayback 7 Jan 2026 | **Sebagian** | Artikel panduan pendaftaran, bukan cek fakta. Isinya menyebut seleksi tidak dipungut biaya, mengutip laman resmi TNI AD, meminta waspada calo, dan menyatakan tidak ada pihak yang bisa menjamin kelulusan. Jadi isinya bertentangan dengan klaim, tetapi bukan bantahan atas pesan yang beredar. Di server, mesin bukti akan jatuh ke salinan Wayback (berlabel). |
| `rekrutmen-tni-ad-berbayar` | Investortrust: Kodam Pattimura buru calo penerimaan prajurit | 200 | **Ya** | Kodam XV/Pattimura memburu oknum calo penerimaan Tamtama 2026 (kerugian korban sekitar Rp112 juta). Kapendam menegaskan masuk TNI AD gratis: tanpa pungutan, tanpa titipan, tanpa jaminan lulus dengan uang. |
| `bmkg-prediksi-gempa-tanggal` | BMKG: siaran pers prediksi gempa 7,0 adalah hoaks | 200 | **Ya** | Siaran pers resmi BMKG (18 Agu 2018): ramalan yang menyebut kapan dan seberapa kuat gempa terjadi dipastikan kabar bohong. |
| `bmkg-prediksi-gempa-tanggal` | Kompas TV: isu gempa dan tsunami 20 Des–23 Jan | 200 (dialihkan dari `/article/` ke `/info-publik/`) | **Ya** | BMKG memastikan perkiraan gempa dan tsunami besar Desember 2022–Januari 2023 adalah hoaks. |
| `bmkg-prediksi-gempa-tanggal` | Republika: BMKG sebut gempa susulan M 9,0 hoaks | 200 | **Ya** | BMKG membantah isu gempa susulan M 9,0 setelah gempa Banten. |
| `air-kelapa-garam-obat` | Liputan6 Cek Fakta (dengan Mafindo), 2020 | 200 | **Ya, sebagai "tidak terbukti"** | Kesimpulan cek fakta: klaim campuran air kelapa, jeruk nipis, dan garam menyembuhkan COVID-19 **belum terbukti secara klinis**. Lihat catatan label di bawah. |
| `air-kelapa-garam-obat` | Liputan6 Cek Fakta: belum terbukti, 2021 | 200 | **Ya, sebagai "tidak terbukti"** | Kesimpulan sama untuk varian dengan madu dan lemon; label cek fakta "unproven". |
| `kuota-gratis-operator` | MerahPutih: kuota gratis 30GB HUT RI | 200 | **Ya** | Mengutip penelusuran Kominfo: tautan kuota gratis 30GB HUT RI ke-77 adalah hoaks; tidak ada informasi dari akun resmi operator. |
| `kuota-gratis-operator` | Bisnis.com Cek Fakta: subsidi kuota 75 GB | **403** (Cloudflare); dibaca dari Wayback 11 Apr 2021 | **Ya** | Kominfo menyatakan pesan berantai subsidi kuota 75 GB atas nama Kominfo/Telkom University adalah hoaks. |
| `saldo-etoll-gratis` | Kompas TV: phishing berkedok saldo e-toll gratis | 200 | **Ya** | Jasa Marga membantah program saldo e-toll gratis Rp500 ribu lewat akun resminya dan menyebutnya hoaks/phishing. |
| `penculikan-anak-berantai` | RRI Cek Fakta: tips menghindari hoaks penculikan anak | 200 | **Sebagian** | Polisi mengonfirmasi satu pesan suara penculikan di Bintan tidak benar (2023), mengutip TurnBackHoax; sisanya tips umum. Membantah kejadian tertentu, bukan semua pesan berantai sejenis. |
| `penculikan-anak-berantai` | Kumparan: diamuk massa akibat kabar hoaks penculikan anak | 200 | **Sebagian** | Melaporkan amuk massa di Lhokseumawe akibat isu penculikan; polisi dan lembaga perlindungan anak menyebut isu yang beredar saat itu bohong. Konteks lokal dan lama. |

**Ringkasan:** 14 tautan, 12 terbuka langsung (HTTP 200), 2 ditolak Cloudflare (Bisnis.com) tetapi tersedia di Internet Archive. 10 tautan membantah secara eksplisit (2 di antaranya sebagai "tidak terbukti"), 4 hanya sebagian. Setiap entri punya setidaknya satu sumber yang eksplisit, kecuali `penculikan-anak-berantai`: kedua sumbernya membantah kejadian tertentu, bukan pola pesan umum.

## Temuan yang perlu keputusan pemilik

1. **`rekrutmen-tni-ad-berbayar`** (entri andalan demo TNI AD). Sumber Investortrust sudah eksplisit. Sumber Bisnis.com adalah artikel panduan dan menolak program, sehingga setiap cek di server bergantung pada salinan Wayback. **Usulan:** ganti sumber Bisnis.com dengan pernyataan resmi TNI AD atau Puspen/Dispenad yang secara tegas menyatakan rekrutmen gratis dan tanpa titipan (mis. laman penerimaan resmi TNI AD atau rilis Dispenad). Kami belum memilih URL pengganti karena belum ada yang terverifikasi; pemilik perlu memilih satu halaman resmi, lalu kami tambahkan dan jalankan `eval/run_eval.py` sebelum dan sesudahnya.
2. **`air-kelapa-garam-obat`**: sumbernya menyimpulkan **"belum terbukti secara klinis"**, sedangkan label vonis Halio adalah 🔴 **"Terbukti salah"**. Teks `fakta` di korpus sudah jujur ("tidak ada bukti klinis"), tetapi label merahnya lebih keras daripada sumbernya. **Usulan:** pertahankan entri, dan pertimbangkan kalimat penjelas pada kartu untuk entri berlabel "tidak terbukti". Ini perubahan perilaku, jadi tidak kami kerjakan sebelum freeze tanpa persetujuan.
3. **`penculikan-anak-berantai`**: tambahkan satu sumber cek fakta yang membantah **pola** pesan berantai penculikan (mis. artikel TurnBackHoax/Mafindo yang dirujuk RRI), bukan hanya kejadian lokal.
4. **Dua tautan Bisnis.com** menolak program. Pada demo langsung, bukti dari tautan ini akan berlabel "dibaca dari salinan arsip". Itu jujur, tetapi bisa memancing pertanyaan juri.

Cara mengulang pemeriksaan ini: buka setiap `sumber[].url` di `data/debunks.json`; bila HTTP 403/429/503, periksa `https://archive.org/wayback/available?url=<url>`.

## Penambahan 13 Nov 2026: tiga entri, delapan tautan baru

Setiap tautan baru **dibuka dan dibaca** pada 13 Nov (bukan hanya dilihat di hasil pencarian). `eval` dijalankan sebelum dan sesudah.

| Entri | Sumber | Eksplisit? | Catatan |
|---|---|---|---|
| `apk-surat-tilang-whatsapp` | RRI Cek Fakta: [SALAH] Surat Tilang Digital APK (31 Des 2023) | **Ya** | Kakorlantas Polri: Korlantas, Ditlantas, dan Satlantas hanya mengirim konfirmasi tilang ETLE lewat surat PT Pos; pesan APK disebut modus pencurian data |
| `apk-surat-tilang-whatsapp` | detikInet: Awas, tidak ada e-tilang yang dikirim ke WhatsApp (23 Apr 2024) | **Ya** | Kominfo: tidak ada e-tilang yang dikirim lewat WhatsApp; kepolisian mengimbau waspada modus APK |
| `calo-cpns-bayar-lulus` | detikFinance (19 Okt 2023), mengutip Plt Kepala BKN | **Ya** | Pelamar diminta tidak tergiur oknum yang mengaku bisa meloloskan tanpa seleksi resmi; yang menyerahkan uang dapat terkena pidana |
| `calo-cpns-bayar-lulus` | Okezone (26 Sep 2021), mengutip Wakil Kepala BKN | **Ya** | "Jangan percaya dengan pihak yang menjanjikan kelulusan karena itu pasti bohong"; hasil seleksi tidak bisa dimanipulasi |
| `calo-cpns-bayar-lulus` | DDTC News (6 Sep 2021), mengutip Sekretaris Kementerian PAN-RB | **Ya** | Janji membantu lulus dengan imbalan uang disebut penipuan |
| `otp-petugas-bank` | BCA: Cukup kamu yang tahu, jangan bagikan kode OTP-mu (30 Okt 2026) | **Ya, untuk BCA** | BCA tidak pernah meminta OTP, PIN, atau password lewat telepon, SMS, email, atau media sosial; WhatsApp tidak disebut eksplisit di halaman itu |
| `otp-petugas-bank` | BCA: Waspada penipuan mengatasnamakan BCA (9 Jan 2025) | **Sebagian** | BCA tidak pernah meminta nomor kartu, OTP, CVV, PIN, dan password; halaman tidak menyebut kanalnya |
| `otp-petugas-bank` | CNN Indonesia (12 Mar 2025), mengutip OJK | **Sebagian** | OJK: bank pada dasarnya tidak menghubungi nasabah lebih dulu; modus SMS OTP lewat BTS palsu. Imbauan umum, bukan bantahan atas satu pesan |

Catatan jujur: entri OTP ditulis sebagai **pola** ("petugas bank meminta OTP"), bukan klaim tentang bank tertentu, dan teks `fakta` menyebut BCA dan OJK apa adanya. Pernyataan BCA mewakili BCA saja.

**Kandidat yang ditolak.** (1) "Siaga 1 TNI": berdasarkan hasil pencarian, perintah aslinya ada dan komunikasi resmi TNI sendiri beragam; yang dibantah Komdigi hanya satu unggahan yang diubah. Bukan bantahan bersih, dan topiknya sensitif secara politik, jadi tidak dimasukkan (Halio tidak menuduh). Halaman Bisnis.com untuk topik ini menolak akses program, jadi tidak saya buka langsung. (2) "Kartu SIM diblokir bila tidak registrasi ulang": hanya ada pernyataan kebijakan Komdigi, tidak ada bantahan eksplisit atas pesan semacam itu. (3) Undangan nikah berformat APK (Kominfo, 2023): satu sumber terbuka dibaca, tetapi sumber Bisnis.com menolak program; tidak dimasukkan agar entri APK tetap sempit pada klaim yang terverifikasi (surat tilang).

**Dampak pada evaluasi.** Menambah dokumen mengubah bobot TF-IDF untuk semua entri. Dua item dev lama turun tipis di bawah ambang (0,385 dan 0,393 dari 0,424 dan 0,43) dan satu tes regresi (hoaks bansos dua kalimat) turun ke 0,398. Penanganannya, tanpa menyentuh ambang: dua varian umum ditambahkan ke entri bansos dan rekrutmen TNI, serta kata "whatsapp" dikurangi di entri baru. Satu percobaan varian yang terlalu mirip tes dibatalkan karena membuat pesan terbelah dua. Hasil akhir: dev false-hoax 0/36 (recall 100%), holdout false-hoax 0/40 (recall 88%, dua kegagalan yang sama seperti sebelumnya), 273 tes lulus. Set dev adalah set penyetelan; 12 item uji baru ditulis bersama entri baru, jadi tidak buta.

**Pemeriksaan ulang pada data independen (13 Nov).** Dijalankan dengan `eval/eval_public_recheck.py` pada commit beku `69d1020` (laporan: [PUBLIC_RECHECK.md](../eval/PUBLIC_RECHECK.md)): dari 197 judul berlabel BENAR atau KLARIFIKASI dalam sampel 3.700 judul, **0** dicap "terbukti salah" (batas atas 95%: 1,9%); 17 dari 2.582 judul SALAH dikenali (cakupan korpus, bukan akurasi). Tiga halaman unduhan gagal dan dilewati. Satu pengukuran awal pada korpus perantara (sebelum varian yang berlebihan dibatalkan) tidak dipakai. Angka 0/1.043 di `eval/PUBLIC_RESULTS.md` diukur dengan korpus 7 entri dan tidak dibuat ulang.

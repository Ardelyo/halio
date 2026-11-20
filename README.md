<div align="center">

<img src="web/icons/icon.svg" alt="Logo Halio" width="84" height="84">

# halio.

**Teman cek pesan untuk keluarga Indonesia.**<br>
Berhenti sebentar. Tanya Halio. Baru bagikan.

[![CI](https://github.com/Ardelyo/halio/actions/workflows/ci.yml/badge.svg)](https://github.com/Ardelyo/halio/actions/workflows/ci.yml)
[![Lisensi: Apache 2.0](https://img.shields.io/badge/lisensi-Apache%202.0-0B4EA2)](LICENSE)
![Python 3.12](https://img.shields.io/badge/python-3.12-0B4EA2)
![Status: purwarupa](https://img.shields.io/badge/status-purwarupa-B54708)
![Tes: 319 lulus](https://img.shields.io/badge/tes-319%20lulus-067647)
![Tanda tangan: Ed25519](https://img.shields.io/badge/tanda%20tangan-Ed25519-014BAA)
![Mode luring](https://img.shields.io/badge/mode-luring%20tanpa%20AI-014BAA)

[Tonton video demo](https://youtu.be/s2EMpZI2r4g) · [Coba sekarang](#coba-sekarang) · [Panduan untuk juri](docs/submission/UNTUK_JURI.md) · [Slide (PDF)](docs/presentasi/Halio_Deck_Juri.pdf) · [Rilis v0.2.1-luring](https://github.com/Ardelyo/halio/releases/tag/v0.2.1-luring) · [Semua dokumen](docs/README.md)

<img src="docs/submission/thumbnail_kolase.jpg" alt="Halio: berhenti sebentar, cek dulu. Kolase foto Nenek dan cucunya memakai Halio." width="760">

*Kartika Cyber Hackathon 2026 · Kategori Siber Sosial · dibuat oleh Ardellio S. A.*

</div>

## Masalah

Pesan berantai menyebar di grup keluarga karena orang peduli, bukan karena bodoh. Satu pesan yang salah, misalnya surat kelulusan palsu atau bantuan tunai palsu, bisa membuat keluarga panik atau kehilangan uang. Bantahan resmi jarang sampai ke tempat pesan itu beredar, dan penipuan yang mencatut nama TNI AD termasuk di antaranya.

## Solusi

Ibu atau Bapak cukup **meneruskan** pesan yang meragukan ke Halio lewat Telegram atau web. Halio menjawab dalam bahasa sehari-hari:

| | Yang diterima pengguna |
|---|---|
| 🔊 | **Pesan suara** yang ramah untuk orang tua |
| 🖼️ | **Kartu Halio** seukuran WhatsApp untuk meluruskan di grup keluarga |
| 📎 | **Sumber bernama** dari pemeriksa fakta atau lembaga resmi, bisa dibuka |
| 🧠 | **Trik manipulasi** yang dipakai pesan itu, supaya belajar mengenalinya |

Bila belum ada pemeriksaan, Halio berkata jujur: **"Halio tidak mau menebak"**, lalu menawarkan pemeriksa manusia.

Dari cek-cek warga itu, **Radar Ketahanan Kognitif** menunjukkan kepada analis kabar apa yang sedang naik dan trik apa yang dipakai, termasuk lonjakan penipuan yang mencatut TNI AD. Radar tidak membaca pesan pribadi: isi kabar baru muncul hanya setelah dilaporkan banyak orang berbeda (k-anonimitas).

## Lihat sekilas

<table>
<tr>
<td width="50%" valign="top">

**1. Tempel pesan, dapat jawaban bersumber**

<img src="docs/img/cek-calo-tni.png" alt="Halio memeriksa pesan calo rekrutmen TNI AD dan menjawab Terbukti salah dengan sumber" width="100%">

<sub>Calo rekrutmen TNI AD dengan bahasa chat ("lwt kenalan perwira", "uang pelicin") tertangkap mesin luring, tanpa AI dan tanpa internet.</sub>

</td>
<td width="50%" valign="top">

**2. Forensik lokal: domain tiruan dan berkas .apk**

<img src="docs/img/cek-apk-forensik.png" alt="Halio menandai domain rekrutmen-tniad.xyz sebagai tiruan dan SuratDinas_Kodam.apk sebagai aplikasi berbahaya" width="100%">

<sub>Halio tidak menebak vonis, tetapi menunjukkan indikator teknis: domain yang menyamar sebagai TNI AD dan berkas .apk berkedok surat dinas.</sub>

</td>
</tr>
</table>

<table>
<tr>
<td width="33%" valign="top" align="center">

**Kartu Halio bertanda tangan**

<img src="docs/img/kartu-halio-contoh.png" alt="Kartu Halio 1080x1080 berisi vonis, fakta, sumber, dan ID verifikasi Ed25519" width="100%">

<sub>Seukuran grup WhatsApp. Di footer ada ID Verifikasi; tanda tangan Ed25519 tertanam di PNG.</sub>

</td>
<td width="33%" valign="top" align="center">

**Ponsel dulu**

<img src="docs/img/cek-calo-tni-hp.png" alt="Tampilan Halio di layar ponsel 390 piksel" width="100%">

<sub>Halaman dirancang ponsel-dulu: Ibu dan Bapak biasanya membuka Halio dari grup WhatsApp di ponsel.</sub>

</td>
<td width="33%" valign="top" align="center">

**Radar untuk analis**

<img src="docs/img/radar-simulasi.png" alt="Radar Halio: jumlah cek, sebaran status, lonjakan penipuan yang mencatut TNI AD (data simulasi)" width="100%">

<sub>Data **simulasi** berlabel (`scripts/seed_demo.py`). Tombol <b>Ekspor LAPSUS</b> mengunduh laporan bertanda tangan.</sub>

</td>
</tr>
</table>

<details>
<summary><b>Alur penggunaan lima langkah</b> (tangkapan layar dari video demo)</summary>

<table>
<tr>
<td><img src="docs/submission/screenshot_01.png" alt="Langkah 1: tempel pesan yang meragukan" width="100%"></td>
<td><img src="docs/submission/screenshot_02.png" alt="Langkah 2: jawaban bersumber" width="100%"></td>
<td><img src="docs/submission/screenshot_03.png" alt="Langkah 3: dengarkan dan bagikan" width="100%"></td>
</tr>
<tr>
<td><img src="docs/submission/screenshot_04.png" alt="Langkah 4: jujur saat belum tahu" width="100%"></td>
<td><img src="docs/submission/screenshot_05.png" alt="Langkah 5: Radar untuk analis" width="100%"></td>
<td></td>
</tr>
</table>

</details>

## Cara kerja

```mermaid
flowchart TD
    IN["Pesan / foto / tautan / berkas<br>(Telegram · Web PWA · Ekstensi)"] --> PII["Hapus data pribadi<br>nomor · NIK · email · tautan"]
    PII --> FOR["Forensik zero-cloud<br>domain tiruan · .apk · metadata gambar"]
    PII --> T1["T1 luring<br>TF-IDF + normalisasi frasa domain"]
    T1 --> REG["Registri buletin resmi<br>bertanda tangan Ed25519"]
    T1 --> T2["T2 opsional: mesin bukti<br>AI mencari, kode menyalin kutipan"]
    FOR --> VER{"Kode memutuskan<br>5 keadaan jawaban"}
    REG --> VER
    T2 --> VER
    VER --> CARD["Kartu Halio PNG<br>bertanda tangan + suara + sumber"]
    VER -. "agregat anonim, k ≥ 5" .-> RAD["Radar + LAPSUS<br>bertanda tangan"]
    CARD -. "halio verify · /verifikasi.html" .-> CHK["Pemeriksa keaslian<br>SAH / TIDAK SAH"]
    RAD -.-> CHK
```

<p align="center"><img src="docs/img/dua-jalur.svg" alt="Dua jalur: T1 luring tanpa AI dan T2 opsional dengan AI, keduanya diputuskan kode" width="900"></p>


**AI hanya mencari dan membaca bukti. Vonis diputuskan kode.** Kutipan disalin kode dari halaman yang dibuka kode, lalu dicocokkan ulang kata per kata. Kalimat yang tidak didukung kutipan dibuang.

## Lima keadaan jawaban

| | Status | Artinya |
|---|---|---|
| 🔴 | **Terbukti salah** | Sudah dibantah oleh pemeriksa fakta atau sumber resmi yang disebutkan |
| 🟢 | **Sejalan dengan sumber** | Sumber resmi yang masih berlaku memuat kutipan yang mendukung seluruh klaim. Bukan stempel "pasti benar": cek tanggal dan konteksnya |
| 🔵 | **Dilaporkan media** | Diberitakan media, tetapi ini bukan pemeriksaan fakta |
| 🟠 | **Halio tidak yakin** | Mirip kabar bohong tapi tidak sama persis, bukti bertentangan atau kedaluwarsa, atau bukan klaim faktual |
| ⚪ | **Belum ada pemeriksaan** | Belum ada sumber yang cocok; Halio tidak menebak |

Ada lima keadaan karena kabar yang benar tidak boleh dicap hoaks, dan tidak ada bantahan bukan berarti benar. Alasannya ada di [Kalau informasinya benar, bagaimana?](docs/TRUE_INFORMATION.md). Pada mode tanpa AI, hanya tiga keadaan yang bisa muncul: terbukti salah, tidak yakin, dan belum ada pemeriksaan.

## Kenapa bisa dipercaya

| Prinsip | Bagaimana dijaga |
|---|---|
| **Sumber nyata** | Tautan hanya dari halaman yang benar-benar dibuka kode. Halaman dari situs tak dikenal tidak bisa menjadi bukti |
| **Berani bilang belum tahu** | "Belum ada pemeriksaan" adalah jawaban yang sah, bukan kegagalan |
| **Privasi sejak awal** | Nomor, NIK, email, rekening, tautan, dan @akun dihapus sebelum diproses. Maksimal 300 karakter klaim yang dikirim ke cloud |
| **Netral** | Halio memeriksa klaim, bukan orang. Tidak ada akun atau prajurit yang diprofilkan |

## Bukti dalam angka

<p align="center"><img src="docs/img/angka-kunci.svg" alt="Angka kunci Halio v1.0: 319 tes, 741 vektor paritas, 0 salah tuduh, 35 entri korpus, 8 uji hidup" width="900"></p>

<p align="center"><img src="docs/img/riwayat-evaluasi.svg" alt="Riwayat evaluasi: recall holdout 81, 88, 100 persen; salah tuduh 11, 1, 0" width="900"></p>


| Angka | Arti | Sumber |
|---|---|---|
| **319** | Tes otomatis lulus, dijalankan CI pada setiap perubahan | [CI](.github/workflows/ci.yml) |
| **0 dari 76** | Pernyataan benar atau belum dikenal yang salah dicap "terbukti salah" (dua set uji tulisan tim; batas atas 95%: 4,8%) | [eval/RESULTS.md](eval/RESULTS.md) |
| **0 dari 1.043** | Judul TurnBackHoax berlabel BENAR atau KLARIFIKASI yang salah dicap "terbukti salah", pada sampel publik yang tidak dipakai menyetel Halio (satu kesalahan ditemukan lalu diperbaiki, lihat catatan di laporan) | [eval/PUBLIC_RESULTS.md](eval/PUBLIC_RESULTS.md) |
| **0 dari 197** | Judul TurnBackHoax berlabel BENAR atau KLARIFIKASI yang salah dicap "terbukti salah", pada sampel 3.700 judul diuji ulang dengan korpus 10 entri (13 Nov, commit beku, batas atas 95%: 1,9%) | [eval/PUBLIC_RECHECK.md](eval/PUBLIC_RECHECK.md) |
| **0 dari 27** | Rilis resmi TNI dan Kemhan yang salah dicap "terbukti salah" (n kecil, batas atas 95%: 12,5%). **3 dari 27 melewati ambang skor dan hanya tertahan oleh penjaga inti klaim**; 12 dijawab "tidak yakin" dan 15 "belum ada pemeriksaan" | [eval/RESMI_TNI_RESULTS.md](eval/RESMI_TNI_RESULTS.md) |
| **100%** | Recall parafrase hoaks pada set holdout. **Disetel setelah melihat kegagalan, jadi bukan estimasi akurasi** (sebelumnya 88%) | [eval/RESULTS.md](eval/RESULTS.md) |
| **≈2 ms** | Median satu cek lokal tanpa AI di laptop pengembang (ARM64): 300 pemanggilan, korpus 35 entri, forensik ikut jalan, p95 3,7 ms (20 Nov 2026). Sebelumnya 0,5 ms pada korpus 10 entri | [Arsitektur](docs/ARCHITECTURE.md) |
| **23** | Feed terbuka yang dipantau sensor (opsional) | [Arsitektur sensor](docs/ARCHITECTURE_SENSOR.md) |

## Bisa jalan luring

Jalur pencocokan (T1) tidak butuh AI maupun internet, jadi Halio bisa dipakai di satuan dengan jaringan terbatas atau tertutup, dan tidak ada data yang keluar dari perangkat. Ada tiga bentuk: server on-premise tanpa AI, mesin yang sama di browser/PWA (dijaga identik dengan Python lewat uji paritas pada 603 vektor, dan 3.900 judul nyata), serta ekstensi Chrome yang sebagian sudah di perangkat. Batasnya ditulis terus terang: kabar di luar korpus tidak dikenali, dan Telegram butuh internet. Rincian dan buktinya di [Mode luring](docs/LURING.md).

## Bukti keaslian dan Medan Uji (v1.0)

### Tanda tangan Ed25519: asli atau dipalsukan?

Setiap Kartu Halio dan laporan LAPSUS ditandatangani **Ed25519**. Tanda tangan mengikat teks vonis **dan** hash piksel gambar, jadi mengubah 1 byte, 1 piksel, atau vonisnya langsung ditolak. Kartu tetap PNG biasa: amplopnya ada di chunk `halio-sig-v1`.

<table>
<tr>
<td width="50%" valign="top">

**Kartu asli → SAH**

<img src="docs/img/verifikasi-sah.png" alt="Halaman verifikasi menampilkan SAH untuk kartu asli" width="100%">

</td>
<td width="50%" valign="top">

**Diubah 1 byte → TIDAK SAH**

<img src="docs/img/verifikasi-ditolak.png" alt="Halaman verifikasi menampilkan TIDAK SAH untuk kartu yang diubah satu byte" width="100%">

</td>
</tr>
</table>

```bash
python -m halio.verify kartu.png        # exit 0 = SAH, exit 1 = TIDAK SAH / DIMODIFIKASI
python -m halio.verify lapsus.json --pubkey kunci_publik.pem
```

Juga lewat halaman `/verifikasi.html`, `POST /api/verify`, dan `GET /api/pubkey`. Kartu contoh di atas ([`docs/img/kartu-halio-contoh.png`](docs/img/kartu-halio-contoh.png)) ditandatangani kunci pengembang; versi yang diubah 1 byte ada di [`kartu-halio-diubah.png`](docs/img/kartu-halio-diubah.png).

> Simpan kunci privat di tempat tetap lewat `HALIO_SIGN_KEY_FILE` (atau `HALIO_SIGN_KEY`). Tanpa itu, kunci dibuat di `~/.halio/` dan kartu lama menjadi tidak sah bila kunci berganti. Skema ML-DSA-65 (pasca-kuantum) baru titik colok di `crypto_sign.ALGORITHMS`, belum diimplementasikan.

### Medan Uji: 8 serangan hidup

`/uji.html` memanggil fungsi asli Halio, bukan tiruan. Tujuh uji berjalan lokal tanpa AI dan tanpa jaringan; uji 1 (prompt injection) memanggil model sungguhan (Gemini lewat Vertex) dan butuh `HALIO_LLM=1`. Tangkapan di bawah diambil dengan AI aktif: kedelapan uji **lulus**, dan pada uji 1 model menilai halaman jebakan sebagai `unrelated` dalam 10,6 detik, vonis akhir `tidak_yakin`, tidak pernah hijau.

<img src="docs/img/medan-uji.png" alt="Medan Uji: delapan serangan hidup beserta langkah-langkah buktinya" width="100%">

| # | Serangan | Yang dibuktikan |
|---|---|---|
| 1 | Halaman yang menyuruh AI berbohong | Perintah di halaman hanya data; halaman situs tak dikenal tidak pernah jadi bukti |
| 2 | Alamat palsu / homograph | `tni.mil.id.promo.xyz`, `b4nk-bca.top`, punycode dikenali bukan sumber resmi |
| 3 | AI mengarang angka dan sumber | Kalimat tanpa dukungan kutipan dibuang kode |
| 4 | Kartu Halio dipalsukan | 1 byte, 1 piksel, atau vonis diganti: ditolak |
| 5 | Rilis resmi TNI AD | Kata sensitif tidak dicap hoaks; "gratis" yang disisipi uang tidak dihijaukan |
| 6 | Calo berbahasa chat | Parafrase berat tertangkap mesin luring |
| 7 | Berkas `.apk` berkedok surat dinas/tilang | Terdeteksi modul forensik lokal |
| 8 | Privasi k-anonimitas | Laporan di bawah k=5 ditahan; teks Radar bebas nomor HP dan e-mail |

### Registri buletin resmi: konfirmasi luring yang tetap hati-hati

`data/official_bulletins.json` (3 buletin, bertanda tangan) memungkinkan pernyataan resmi TNI AD dikonfirmasi **luring** sebagai "sejalan dengan sumber". Semua penjaga harus lolos: buletin masih berlaku, inti klaim ada, **tidak ada** unsur bayar/calo/angka rupiah, dan **tidak ada** tautan di luar `.go.id`/`.mil.id`. Tanda tangan salah berarti seluruh registri diabaikan. Tandatangani ulang dengan `python scripts/sign_bulletins.py` dan ganti `data/registry_pubkey.pem` bila satuan Anda memakai kunci sendiri.

### Forensik zero-cloud dan LAPSUS

- **Forensik** (`backend/halio/forensics.py`): domain tiruan/homograph/punycode, jebakan `.apk`/`.exe`, dan metadata gambar (tag generator AI, C2PA, jejak editor). Selalu dilaporkan sebagai **indikator teknis, bukan vonis**; metadata mudah dihapus atau dipalsukan.
- **LAPSUS Siber Sosial** (`GET /api/radar/lapsus`, tombol *Ekspor LAPSUS* di Radar): lonjakan topik dengan z-score, sebaran trik, dan tren penipuan yang mencatut TNI AD. Hanya agregat, tanpa teks pesan atau identitas pelapor, ditandatangani Ed25519.

### Korpus 35 entri

<p align="center"><img src="docs/img/komposisi-korpus.svg" alt="Komposisi korpus bantahan 35 entri menurut kategori" width="900"></p>

> **Catatan jujur:** 25 entri tambahan dikumpulkan dari hasil pencarian dan **belum dibuka satu per satu**; lihat [`docs/VERIFIKASI_KORPUS.md`](docs/VERIFIKASI_KORPUS.md). Recall holdout 100% sudah disetel, jadi bukan estimasi akurasi.

<sub>Gambar dibuat ulang dengan `python scripts/make_readme_shots.py` (server dev harus jalan) dan `python scripts/make_readme_charts.py`.</sub>

## Batas yang kami akui

- Ini purwarupa. Set uji ditulis tim sendiri, jadi angkanya **bukan** akurasi dunia nyata.
- Korpus bantahan kurasi baru **35 entri** (25 di antaranya belum diverifikasi satu per satu). Di luar korpus, Halio memakai pencarian bukti atau berkata belum tahu.
- Belum ada uji dengan pengguna lansia sungguhan; lembar ujinya sudah siap.
- Pada rilis resmi rekrutmen TNI AD, Halio di mode lokal menjawab "tidak yakin" (7 dari 7), bukan mengenalinya sebagai benar: ia tidak menuduh, tetapi juga belum bisa membenarkan tanpa mesin bukti. Rincian di [eval/RESMI_TNI_RESULTS.md](eval/RESMI_TNI_RESULTS.md).
- Data Radar pada demo adalah **simulasi** dan diberi label.
- Halio membaca isi teks, foto, dan suara, tetapi **tidak menilai keaslian** foto atau video, dan tidak mendeteksi deepfake.
- Telegram dan web aktif. Kode kanal WhatsApp (webhook Meta) tersedia dan membutuhkan token Meta milik pemakai.

## Coba sekarang

| Kanal | Tautan |
|---|---|
| Server publik (API, kartu, suara, dan Telusur berjalan sungguhan) | [Cek pesan](https://halio.ardelyo.com/cek.html) · [Uji keamanan](https://halio.ardelyo.com/uji.html) |
| Bot Telegram | [@halioid_bot](https://t.me/halioid_bot) (aktif selama proses bot dan API berjalan) |
| Landing page | [ardelyo.github.io/halio](https://ardelyo.github.io/halio/) |
| Demo di GitHub Pages (Cek pesan: mesin Halio sungguhan di browser, tanpa server; Radar dan Cakupan: simulasi) | [Cek pesan](https://ardelyo.github.io/halio/cek.html) · [Radar](https://ardelyo.github.io/halio/radar.html) · [Cakupan sensor](https://ardelyo.github.io/halio/coverage.html) · [Feed untuk ekstensi](https://ardelyo.github.io/halio/demo-feed.html) |

GitHub Pages menjalankan mesin pencocokan Halio di browser (mode luring, hanya mengenali isi korpus) dan tidak mengirim pesan ke server. Radar dan Cakupan di sana tetap data simulasi berlabel. Situs dideploy otomatis dari `web/` oleh `.github/workflows/pages.yml`.

## Jalankan sendiri

<details>
<summary><b>Backend dan web</b></summary>

```bash
cd backend
pip install -r requirements.txt            # opsional: pip install -r requirements-optional.txt
uvicorn halio.api:app --reload             # http://localhost:8000 , /radar , /demo-feed.html

python ../scripts/seed_demo.py             # isi Radar dengan data SIMULASI (diberi label)
python -m pytest                           # tes unit dan API
python ../eval/run_eval.py                 # evaluasi jujur → eval/RESULTS.md
```

</details>

<details>
<summary><b>Bot Telegram</b></summary>

Token didapat dari @BotFather.

```bash
cd backend
set TELEGRAM_BOT_TOKEN=...      # PowerShell: $env:TELEGRAM_BOT_TOKEN="..."
python -m halio.channels.telegram
```

</details>

<details>
<summary><b>Docker (server satuan, tanpa GPU)</b></summary>

```bash
cp .env.example .env
docker compose up -d
```

Profil tanpa cloud dan cloud opsional dijelaskan di [Profil penerapan](docs/PROFIL_PENERAPAN.md).

</details>

<details>
<summary><b>Antrean pemeriksa manusia</b></summary>

Tersedia di **Radar analis** (`/radar` atau `radar.html`): buka tiket, tulis respons, kirim bila kanal mendukung, dan periksa riwayat tindakan. Endpoint review memakai token Radar yang sama; jangan membukanya tanpa `RADAR_TOKEN` di server publik. CLI tersedia di server tepercaya:

```bash
python scripts/review.py list escalations
python scripts/review.py resolve escalations ID --response "Jawaban pemeriksa"
```

Balasan Telegram atau WhatsApp dikirim sebelum tiket ditutup, dan kegagalan pengiriman membuat tiket tetap terbuka. Kanal web memerlukan tindak lanjut manual dengan nomor tiket. Batas risiko dan gerbang peluncuran ada di [Kesiapan demo dan peluncuran](docs/LAUNCH_READINESS.md).

</details>

<details>
<summary><b>Sensor feed terbuka dan ekstensi Chrome</b></summary>

Halio dapat memantau **23 feed terbuka** (berita, cek fakta, sumber resmi) hampir realtime dengan `HALIO_SENSOR=1`. Halaman **Cakupan** menunjukkan terus terang mana yang hidup, mana yang basi, dan titik buta yang diakui (WhatsApp privat, Meta, TikTok, X, dan lainnya). Rancangannya ada di [Arsitektur sensor](docs/ARCHITECTURE_SENSOR.md). Ekstensi Chrome: [extension/README.md](extension/README.md).

</details>

## Isi repositori

```
backend/halio/       pipeline cek (klaim, PII, retrieval, mesin bukti, vonis), kartu, suara, Radar, kanal
backend/halio/ingest/  sensor: polling feed terbuka dan laporan cakupan
backend/tests/       273 tes otomatis
data/debunks.json    korpus bantahan bersumber
eval/                set uji dan evaluasi (tingkat salah tuduh hoaks)
web/                 PWA cek pesan, Radar, laporan analis, feed simulasi
extension/           ekstensi Chrome MV3 (lencana dan blur di perangkat)
scripts/             seed data simulasi, preflight, antrean review, thumbnail
deploy/              skrip dan unit layanan server (GCE, Caddy, systemd)
docs/                arsitektur, privasi, bukti uji, panduan, materi pengumpulan
```

## Dokumentasi

Pilih jalur sesuai kebutuhan. Peta lengkap beserta jenis tiap dokumen ada di [docs/README.md](docs/README.md).

| Saya ingin... | Mulai dari |
|---|---|
| Menilai karya ini | [Halio dalam lima menit](docs/submission/UNTUK_JURI.md), lalu [Arsitektur](docs/ARCHITECTURE.md) dan [Bukti uji](docs/BUKTI_UJI_DEMO.md) |
| Memahami cara kerja dan batasnya | [Arsitektur](docs/ARCHITECTURE.md), [Halio Telusur](docs/ARCHITECTURE_AGENT.md), [Privasi](docs/PRIVACY.md) |
| Menerapkan di satuan | [Profil penerapan](docs/PROFIL_PENERAPAN.md), [Kesiapan peluncuran](docs/LAUNCH_READINESS.md), [Pembaruan deploy](docs/DEPLOY_UPDATE.md) |
| Berkontribusi | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Hak kekayaan intelektual dan lisensi

Sesuai Rulebook §N, HKI atas karya ini tetap milik tim. Kode dan dokumen di repo ini dirilis dengan [Lisensi Apache 2.0](LICENSE). Lisensi ini tidak mengalihkan HKI. Penyelenggara tetap berhak menampilkan dan memublikasikan karya untuk keperluan lomba, dan PUSSIBERAD dapat mengadopsi idenya melalui diskusi dengan tim (Rulebook §N).

Komponen pihak ketiga (pustaka, API, model, font, sumber korpus) memakai lisensi masing-masing; lihat [Atribusi pihak ketiga](docs/THIRD_PARTY.md). Isi artikel sumber bantahan tidak termasuk dalam lisensi ini: korpus hanya memuat ringkasan kata sendiri dan tautan.

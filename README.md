# Halio: Keluarga sebagai Lini Pertama Pertahanan Kognitif

**Kartika Cyber Hackathon 2026 · Kategori Siber Sosial**

Halio adalah teman cek pesan untuk keluarga Indonesia. Ibu atau Bapak cukup **meneruskan** pesan yang meragukan, lalu menerima:

- 🔊 **pesan suara** dalam bahasa sederhana ("Bu, pesan ini sudah dicek dan ternyata tidak benar…"),
- 🖼️ **Kartu Halio** seukuran WhatsApp untuk meluruskan di grup keluarga,
- 🧠 penjelasan **trik manipulasi** yang dipakai pesan itu,
- 📎 **sumber bernama** dari pemeriksa fakta atau lembaga resmi.

Bila belum ada pemeriksaan, Halio berkata jujur: **"Halio tidak mau menebak"**, lalu menawarkan pemeriksa manusia.

Dari cek-cek warga itu, **Radar Ketahanan Kognitif** menampilkan tren agregat yang anonim: kategori hoaks, trik yang sering dipakai, lonjakan penipuan yang **mencatut TNI AD**, dan kabar baru yang mulai beredar luas. Isi kabar baru hanya muncul setelah dikirim banyak orang berbeda (k-anonimitas), sehingga tidak ada pesan pribadi yang terbaca.

> Prototipe. Korpus demo masih kecil (7 bantahan bersumber) dan hasil evaluasi berasal dari set uji buatan tim. Lihat [Keterbatasan](docs/ARCHITECTURE.md#7-keterbatasan-yang-kami-akui).

**Untuk Dewan Juri:** [Halio dalam lima menit](docs/submission/UNTUK_JURI.md) memetakan karya ini ke lima kriteria penilaian, lengkap dengan tautan bukti dan daftar hal yang belum kami buktikan.

![Halio: berhenti sebentar, cek dulu](docs/submission/thumbnail_kolase.jpg)

## Sekilas

| | |
|---|---|
| Masalah | Pesan berantai dan penipuan yang mencatut nama TNI AD menyebar di grup keluarga, tempat bantahan resmi jarang sampai |
| Solusi | Teman cek pesan lewat Telegram dan web: jawaban bersumber, kartu, dan suara, ditambah Radar tren anonim untuk analis |
| Peran AI | Mencari dan membaca bukti. Vonis diputuskan kode dari kutipan yang benar-benar ada di halaman sumber |
| Keselamatan | 0 dari 66 pernyataan benar yang salah dicap hoaks pada set uji tim ([hasil](eval/RESULTS.md)); "belum ada pemeriksaan" adalah jawaban yang sah |
| Privasi | Nomor, NIK, email, rekening, tautan, dan @akun dihapus sebelum diproses; Radar memakai k-anonimitas |
| Penerapan | Satu kontainer Docker; profil tanpa cloud untuk server satuan, cloud opsional ([profil](docs/PROFIL_PENERAPAN.md)) |

## Coba sekarang

| Kanal | Tautan |
|---|---|
| Server publik (API, kartu, suara, dan Telusur berjalan sungguhan) | [Buka cek pesan](https://34-101-109-211.sslip.io/cek.html) · [uji keamanan](https://34-101-109-211.sslip.io/uji.html) |
| Landing page | [ardelyo.github.io/halio](https://ardelyo.github.io/halio/) |
| Demo cek pesan (PWA, mendukung menu *Bagikan*) | [Buka demo](https://ardelyo.github.io/halio/cek.html) |
| Bot Telegram | [@halioid_bot](https://t.me/halioid_bot) (aktif selama proses bot dan API berjalan) |
| Radar (data simulasi pada GitHub Pages) | [Buka Radar](https://ardelyo.github.io/halio/radar.html) |
| Cakupan sensor (contoh tampilan pada GitHub Pages) | [Buka cakupan](https://ardelyo.github.io/halio/coverage.html) |
| Feed simulasi untuk ekstensi | [Buka feed](https://ardelyo.github.io/halio/demo-feed.html) |

GitHub Pages menjalankan skenario lokal berlabel simulasi tanpa mengirim pesan ke server. Untuk pemeriksaan API, penyimpanan tiket, dan data Radar nyata, jalankan backend seperti petunjuk di bawah. Situs dideploy otomatis dari direktori `web/` oleh workflow `.github/workflows/pages.yml`.

## Sensor: apa yang dipantau, dan apa yang tidak

"Semua berita, realtime" tidak mungkin. Halio memantau **23 feed terbuka** (berita, cek fakta, sumber resmi) hampir realtime, dan halaman **Cakupan** menunjukkan terus terang mana yang hidup, mana yang basi, dan titik buta yang diakui (WhatsApp privat, Meta, TikTok, X, dll.). Aktifkan dengan `HALIO_SENSOR=1`. Rancangan dan bukti riset: [docs/ARCHITECTURE_SENSOR.md](docs/ARCHITECTURE_SENSOR.md). Lapisan deteksi narasi (klaster, sinyal kecepatan, triase) belum dibangun.

## Lima keadaan jawaban

| | Status | Artinya |
|---|---|---|
| 🔴 | **Terbukti salah** | Sudah dibantah oleh pemeriksa fakta atau sumber resmi yang disebutkan |
| 🟢 | **Sejalan dengan sumber** | Sumber resmi yang masih berlaku memuat kutipan yang mendukung seluruh klaim. Bukan stempel "pasti benar": cek tanggal dan konteksnya |
| 🔵 | **Dilaporkan media** | Diberitakan media, tetapi ini bukan pemeriksaan fakta |
| 🟠 | **Halio tidak yakin** | Mirip kabar bohong tapi tidak sama persis, bukti bertentangan atau kedaluwarsa, atau bukan klaim faktual |
| ⚪ | **Belum ada pemeriksaan** | Belum ada sumber yang cocok; Halio tidak menebak |

Alasan di balik lima keadaan ini ada di [Kalau informasinya benar, bagaimana?](docs/TRUE_INFORMATION.md). Bagian 2 pada dokumen arsitektur masih menjelaskan tiga keadaan awal dari jalur pencocokan lokal.

## Jalankan secara lokal

```bash
cd backend
pip install -r requirements.txt            # opsional: pip install -r requirements-optional.txt
uvicorn halio.api:app --reload             # http://localhost:8000 , /radar , /demo-feed.html

python ../scripts/seed_demo.py             # isi Radar dengan data SIMULASI (diberi label)
python -m pytest                           # uji unit
python ../eval/run_eval.py                 # evaluasi jujur → eval/RESULTS.md
```

Bot Telegram (token dari @BotFather):

```bash
cd backend
set TELEGRAM_BOT_TOKEN=...      # PowerShell: $env:TELEGRAM_BOT_TOKEN="..."
python -m halio.channels.telegram
```

Docker (penerapan di server satuan, tanpa GPU):

```bash
cp .env.example .env
docker compose up -d
```

Ekstensi Chrome: lihat [extension/README.md](extension/README.md).

Antrean pemeriksa manusia tersedia di **Radar analis** (`/radar` atau `radar.html`): buka tiket, tulis respons, kirim bila kanal mendukung, dan periksa riwayat tindakan. Endpoint review memakai token Radar yang sama; jangan membukanya tanpa `RADAR_TOKEN` pada server publik. CLI tetap tersedia di server tepercaya:

```bash
python scripts/review.py list escalations
python scripts/review.py resolve escalations ID --response "Jawaban pemeriksa"
```

Balasan Telegram/WhatsApp dikirim sebelum tiket ditutup. Kegagalan pengiriman membuat tiket tetap terbuka. Kanal web memerlukan tindak lanjut manual dengan nomor tiket. Pada GitHub Pages, penyelesaian tiket hanya simulasi lokal selama sesi dan tidak mengirim balasan. Batas risiko dan gerbang peluncuran ada di [Kesiapan demo dan peluncuran](docs/LAUNCH_READINESS.md).

## Struktur

```
backend/halio/      pipeline cek (klaim, PII, retrieval, LLM terkekang, vonis), kartu, suara, Radar, kanal
backend/halio/ingest/  sensor: polling feed terbuka + laporan cakupan
data/debunks.json   korpus bantahan bersumber
eval/               set uji + evaluasi (tingkat salah tuduh hoaks)
web/                PWA (index), Radar, feed simulasi
extension/          ekstensi Chrome MV3 (lencana + blur di perangkat)
scripts/            seed data simulasi, unduh model, thumbnail, preflight, antrean review
deploy/             skrip dan unit layanan untuk server (GCE, Caddy, systemd)
video/              sumber video demo (naskah, panduan merek, aset)
docs/               rencana proyek, arsitektur, privasi, naskah demo, checklist
docs/submission/    materi pengumpulan: panduan juri, thumbnail, screenshot, draf deskripsi
docs/presentasi/    slide presentasi (HTML dan PDF)
```

## Dokumen

**Mulai dari sini**

- [Halio dalam lima menit (untuk Dewan Juri)](docs/submission/UNTUK_JURI.md): peta ke kriteria penilaian dan tautan bukti
- [Draf deskripsi dan jawaban untuk pertanyaan juri](docs/submission/DRAF_DESKRIPSI.md)
- [Checklist pengumpulan](docs/SUBMISSION_CHECKLIST.md)

**Arsitektur dan penerapan**

- [Arsitektur teknis](docs/ARCHITECTURE.md)
- [Halio Telusur: investigasi untuk analis](docs/ARCHITECTURE_AGENT.md)
- [Arsitektur sensor (pemantauan narasi)](docs/ARCHITECTURE_SENSOR.md)
- [Profil penerapan: tanpa cloud vs cloud opsional, dan data apa yang keluar](docs/PROFIL_PENERAPAN.md)
- [Privasi & aturan netral](docs/PRIVACY.md)
- [Kalau informasinya benar, bagaimana?](docs/TRUE_INFORMATION.md)
- [Kesiapan demo dan peluncuran](docs/LAUNCH_READINESS.md)
- [Pembaruan deploy](docs/DEPLOY_UPDATE.md)

**Bukti dan evaluasi**

- [Hasil evaluasi](eval/RESULTS.md)
- [Bukti uji demo di server publik](docs/BUKTI_UJI_DEMO.md)
- [Bukti uji setelah perbaikan](docs/BUKTI_UJI_SETELAH_PERBAIKAN.md)
- [Verifikasi tautan korpus](docs/VERIFIKASI_KORPUS.md)
- [Evaluasi Radar untuk TNI AD: berfungsi dan bermanfaatkah?](docs/EVALUASI_RADAR_TNI.md)
- [Analisis Radar dan TNI AD](docs/ANALISIS_RADAR_DAN_TNI.md)

**Riset dan rencana**

- [Rencana proyek](docs/PROJECT_PLAN.md): jadwal, peran, risiko, pemetaan ke kriteria penilaian
- [Riset agar Halio menonjol](docs/RESEARCH_STANDOUT.md): bukti ilmiah, peta kompetitor, protokol wawancara dan eksperimen, serta metrik dampak
- [Peta kompetitor](docs/COMPETITORS.md)
- [Rencana Radar](docs/PLAN_RADAR.md) · [Rencana verifikasi AI](docs/PLAN_VERIFIKASI_AI.md) · [Rencana unggul](docs/PLAN_UNGGUL.md)

**Demo dan video**

- [Naskah demo & video](docs/DEMO_SCRIPT.md)
- [Runbook demo](docs/RUNBOOK_DEMO.md)
- [Naskah syuting bersama Nenek](docs/NASKAH_SYUTING_NENEK.md)
- [Atribusi pihak ketiga & deklarasi](docs/THIRD_PARTY.md)

## Hak kekayaan intelektual

Sesuai Rulebook §N, HKI atas karya ini tetap milik tim. Kode dan dokumen di repo ini dirilis dengan [Lisensi Apache 2.0](LICENSE). Lisensi ini tidak mengalihkan HKI. Penyelenggara tetap berhak menampilkan dan memublikasikan karya untuk keperluan lomba, dan PUSSIBERAD dapat mengadopsi idenya melalui diskusi dengan tim (Rulebook §N).

Komponen pihak ketiga (pustaka, API, model, font, sumber korpus) memakai lisensi masing-masing; lihat [docs/THIRD_PARTY.md](docs/THIRD_PARTY.md). Isi artikel sumber bantahan tidak termasuk dalam lisensi ini: korpus hanya memuat ringkasan kata sendiri dan tautan.

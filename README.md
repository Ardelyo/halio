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

## Coba sekarang

| Kanal | Tautan |
|---|---|
| Web (bisa dipasang di Android, mendukung menu *Bagikan*) | `https://<isi-setelah-deploy>` |
| Bot Telegram | `https://t.me/<isi-nama-bot>` |
| Radar | `https://<isi-setelah-deploy>/radar` |
| Cakupan sensor | `https://<isi-setelah-deploy>/coverage` |
| Feed simulasi untuk ekstensi | `https://<isi-setelah-deploy>/demo-feed.html` |

## Sensor: apa yang dipantau, dan apa yang tidak

"Semua berita, realtime" tidak mungkin. Halio memantau **23 feed terbuka** (berita, cek fakta, sumber resmi) hampir realtime, dan halaman **Cakupan** menunjukkan terus terang mana yang hidup, mana yang basi, dan titik buta yang diakui (WhatsApp privat, Meta, TikTok, X, dll.). Aktifkan dengan `HALIO_SENSOR=1`. Rancangan dan bukti riset: [docs/ARCHITECTURE_SENSOR.md](docs/ARCHITECTURE_SENSOR.md). Lapisan deteksi narasi (klaster, sinyal kecepatan, triase) belum dibangun.

## Tiga keadaan vonis

| | Status | Artinya |
|---|---|---|
| 🔴 | **Terbukti salah** | Sudah dibantah oleh pemeriksa fakta atau sumber resmi yang disebutkan |
| 🟠 | **Halio tidak yakin** | Mirip kabar bohong tapi tidak sama persis, atau bukan klaim faktual |
| ⚪ | **Belum ada pemeriksaan** | Belum ada bantahan; Halio tidak menebak |

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

## Struktur

```
backend/halio/      pipeline cek (klaim, PII, retrieval, LLM terkekang, vonis), kartu, suara, Radar, kanal
backend/halio/ingest/  sensor: polling feed terbuka + laporan cakupan
data/debunks.json   korpus bantahan bersumber
eval/               set uji + evaluasi (tingkat salah tuduh hoaks)
web/                PWA (index), Radar, feed simulasi
extension/          ekstensi Chrome MV3 (lencana + blur di perangkat)
scripts/            seed data simulasi, unduh model, thumbnail
docs/               rencana proyek, arsitektur, privasi, naskah demo, checklist
```

## Dokumen

- [Rencana proyek](docs/PROJECT_PLAN.md): jadwal, peran, risiko, pemetaan ke kriteria penilaian
- [Arsitektur teknis](docs/ARCHITECTURE.md)
- [Arsitektur sensor (pemantauan narasi)](docs/ARCHITECTURE_SENSOR.md)
- [Privasi & aturan netral](docs/PRIVACY.md)
- [Naskah demo & video](docs/DEMO_SCRIPT.md)
- [Checklist pengumpulan](docs/SUBMISSION_CHECKLIST.md)
- [Atribusi pihak ketiga & deklarasi](docs/THIRD_PARTY.md)
- [Hasil evaluasi](eval/RESULTS.md)

## Hak kekayaan intelektual

Sesuai Rulebook §N, HKI atas karya ini milik tim. Lisensi sumber terbuka belum ditentukan.

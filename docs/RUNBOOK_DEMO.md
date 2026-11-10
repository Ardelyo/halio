# Menjalankan Halio untuk demo dan rekaman (Telegram, web, Radar)

Bot Telegram **hanya hidup selama dua proses ini berjalan**: API dan bot. GitHub Pages tidak menjalankan keduanya.
Panduan ini membuat semuanya hidup di satu laptop (tanpa Docker). Untuk server yang selalu menyala, lihat `PLAN_UNGGUL.md` bagian 4.1.

## 1. Sekali saja
1. Python 3.11+ dan pasang paket: `cd backend && pip install -r requirements.txt -r requirements-optional.txt`
2. Salin `.env.example` menjadi `.env` di akar repo, lalu isi:
   - `TELEGRAM_BOT_TOKEN` (dari @BotFather)
   - `HALIO_CHANNEL_KEY` = teks acak panjang (sama untuk API dan bot; tanpa ini tombol "Tanya pemeriksa manusia" tidak bisa membalas)
   - `RADAR_TOKEN` = teks acak (dipakai membuka Radar dari luar laptop)
   - `HALIO_LLM=0` untuk rekaman supaya jawaban stabil dan tidak bergantung pada Google. Nyalakan `HALIO_LLM=1` hanya bila Anda sudah login `gcloud auth application-default login`.
3. Di @BotFather: `/setcommands` lalu tempel
   ```
   start - Mulai dan cara pakai
   privasi - Apa yang Halio simpan
   sapaan - Atur cara Halio memanggil Anda
   ```
   Opsional: `/setdescription` ("Teruskan pesan yang meragukan, Halio bantu cek."), `/setuserpic` (pakai `web/icons/icon-512.png`).

## 2. Setiap kali (tiga terminal, dari akar repo)
```bash
# 1) API
set -a; . ./.env; set +a
cd backend && uvicorn halio.api:app --port 8000

# 2) Bot  (terminal lain, setelah `set -a; . ./.env; set +a`)
cd backend && HALIO_API_URL=http://localhost:8000 python -m halio.channels.telegram

# 3) Pemeriksaan sebelum merekam  (terminal lain, dengan env yang sama)
python scripts/preflight.py
```
Semua baris harus **PASS**. `WARN` boleh bila Anda mengerti artinya (mis. Radar terbuka di laptop sendiri).
Bila bot menulis "getUpdates ditolak: Conflict" atau `409`: ada bot kedua yang memakai token yang sama (laptop lain, terminal lama). Hentikan yang lain.

## 3. Pesan uji yang hasilnya sudah dipastikan
Gunakan pesan buatan seperti ini saat merekam; jangan memakai pesan asli dari grup keluarga (lihat bagian 5).

| Kirim ke bot | Hasil yang diharapkan |
|---|---|
| `/start` | Sambutan dan petunjuk |
| `/sapaan Nenek` | "Baik, saya akan memanggil Anda “Nenek”." |
| `Bapak ibu, ada video Pak Presiden bagi-bagi bantuan tunai! Langsung chat nomor WA 0812-3456-7890 untuk daftar, bayar biaya admin 150rb dulu. SEBARKAN!!` | 🔴 **Terbukti salah**, sumber bernama, kartu, suara, tombol "Kenali triknya" dan "Ajukan banding"; nomor telepon tidak ikut tersimpan |
| `Jembatan Suramadu akan ditutup total selama seminggu mulai besok. Tolong sebarkan.` | ⚪ **Belum ada pemeriksaan** ("Halio tidak mau menebak"), tombol "Tanya pemeriksa manusia" |
| `Pendaftaran Bintara TNI AD 2026 dibuka lewat penerimaan.tniad.mil.id, biaya gratis` | 🟠 **Halio tidak yakin** (topik mirip, bukan penipuan). Contoh bagus untuk menjelaskan "tidak langsung dicap hoaks" |
| `ok`, sebuah foto, atau pesan suara | "Untuk sekarang saya baru bisa membaca teks." |
| Tekan "Tanya pemeriksa manusia" | Nomor tiket; tiket muncul di Radar → Antrean |
| Tekan "Kenali triknya" | Penjelasan teknik manipulasi |

Bila API mati atau terlalu sibuk, bot **tetap membalas** dengan permintaan maaf (sudah diuji), bukan diam.

## 4. Yang bisa dan belum bisa (jujur)
**Sudah berfungsi** (diuji dengan Telegram tiruan terhadap API sungguhan; 106 tes): perintah, pengecekan teks, tiga hasil + "sejalan dengan sumber", kartu PNG, suara MP3, tombol trik/banding/eskalasi, pesan panjang, HTML liar di pesan, hasil kedaluwarsa, API mati, batas laju.

**Belum / terbatas:**
- **Hanya teks.** Foto, tangkapan layar, pesan suara, dan video belum diperiksa (rencana: `PLAN_UNGGUL.md` bagian 3). Bila Nenek memotret layar, bot akan meminta teksnya.
- **Belum diuji dengan Telegram asli dari sini.** Token tidak ada di lingkungan saya; yang diuji adalah seluruh logika bot terhadap API nyata. Uji pertama dengan akun Anda sendiri sebelum merekam.
- Suara server (Cloud TTS Chirp 3 HD, cadangan gTTS) butuh internet. Di halaman web, tombol "Dengarkan" memakai suara perangkat bila server gagal.
- Sapaan (`/sapaan`) hilang saat bot dimulai ulang.
- Bot mati bila laptop tidur atau jaringan putus. Matikan mode tidur saat merekam.
- **Balasan tiket ke Telegram** hanya jalan bila `TELEGRAM_BOT_TOKEN` juga terisi pada proses API dan `HALIO_CHANNEL_KEY` sama di API dan bot.
- Ekstensi Chrome: lencana teks dan penyamaran judi online jalan; model gambar "pintar" belum terpasang (jalankan `python scripts/fetch_models.py`).
- Web: buka `http://localhost:8000/cek.html` (API sungguhan: kartu, suara, Radar berisi data nyata). `ardelyo.github.io/halio` hanya simulasi di browser.
- Docker: berkas `Dockerfile` dan `docker-compose.yml` ada, tetapi saya tidak bisa membangun image di lingkungan ini (tanpa daemon Docker), jadi belum terbukti.

## 5. Merekam Nenek (Kania Wijayanti): hal yang perlu diperhatikan
- **Persetujuan** Nenek untuk direkam dan dipublikasikan, lebih baik tertulis atau terekam di awal. Lomba melarang data pribadi pihak ketiga; wajah dan suara Nenek adalah data pribadinya, jadi izinnya harus jelas.
- **Jangan tampilkan** nomor telepon, nama kontak, foto kontak, isi grup keluarga, atau notifikasi dari orang lain di layar ponsel Nenek. Aktifkan mode jangan ganggu, tutup aplikasi lain, dan gunakan akun Telegram yang bersih.
- **Pakai pesan buatan** (tabel di atas), bukan pesan asli dari grup.
- Besarkan huruf di pengaturan Telegram (Settings → Chat Settings → Text size) dan layar agar terbaca kamera.
- Ceritakan Halio sebagai teman bertanya, bukan pengganti penilaian Nenek, sesuai kalimat di situs: "bukan menggantikan penilaian Anda".
- Cadangkan rekaman layar ponsel (bukan hanya kamera), karena bot bisa terlambat membalas bila internet lambat.

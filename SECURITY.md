# Kebijakan keamanan Halio

Halio adalah purwarupa lomba yang dikerjakan satu orang. Dokumen ini menjelaskan cara melapor, model ancaman satu halaman, dan celah yang sudah kami ketahui. Tidak ada jaminan waktu tanggapan atau hadiah temuan; kami berusaha sebaik mungkin.

## Cara melapor kerentanan

1. **Jalur privat (disarankan):** tab **Security** repo ini, lalu **Report a vulnerability** (GitHub Security Advisories), bila tombol itu tersedia.
2. Bila tombol itu tidak ada: buka *issue* berjudul **"Kontak keamanan"** **tanpa detail teknis atau cara eksploitasi**. Kami akan menghubungi balik lewat GitHub untuk menerima detailnya secara privat.
3. Jangan mengirim data pribadi orang lain, dan jangan menguji dengan pesan pengguna sungguhan.

Versi yang didukung: `main` dan rilis terbaru. Halaman uji keamanan publik ada di `/uji.html` pada server demo (tiga uji hidup: halaman yang menyuruh AI berbohong, alamat palsu mirip situs pemerintah, dan kalimat karangan AI).

Penelitian beritikad baik diterima: jangan melakukan DoS, jangan mengakses data milik orang lain, dan hentikan bila menemukan data pribadi.

## Model ancaman satu halaman

**Yang dilindungi:** (1) teks pesan pengguna (dibersihkan dari nomor, NIK, email, rekening, tautan, @akun dan dipotong 300 karakter sebelum diproses), (2) integritas vonis (Halio tidak boleh menuduh kabar benar atau mengarang sumber), (3) Radar agregat dan tiket eskalasi, (4) rahasia (kunci API, token bot, `HALIO_CHANNEL_KEY`, `RADAR_TOKEN`).

**Batas kepercayaan:** klien internet → Caddy (TLS) → API di `127.0.0.1` → layanan pihak ketiga (model AI, suara, cek fakta, arsip, situs sumber). Bot Telegram → API memakai kunci kanal bersama. Analis → Radar memakai token.

| Ancaman | Pertahanan di kode | Bukti |
|---|---|---|
| **SSRF dan DNS rebinding** saat membuka halaman bukti | Nama di-resolve sekali, ditolak bila ada jawaban non-global, lalu koneksi dibuat ke IP itu (Host dan SNI tetap nama asli); hanya HTTPS publik | `backend/halio/safefetch.py` (`PinnedTransport`), `test_safefetch.py`, `test_hardening.py` |
| **Prompt injection** lewat isi halaman | Model hanya memilih kandidat bernomor. Kutipan disalin dan dicocokkan ulang kata per kata oleh kode; kalimat tanpa dukungan kutipan dibuang; vonis ditetapkan kode | `backend/halio/evidence.py`, halaman `/uji.html` |
| **Memalsukan jumlah pelapor** agar kabar lolos k-anonimitas Radar | ID pelapor dari klien tidak dipercaya; dihitung dari awalan jaringan (/24 IPv4, /48 IPv6) dan di-hash dengan garam harian; hanya bot dengan `HALIO_CHANNEL_KEY` boleh menyebut pelapor | `backend/halio/netguard.py`, `store.py` |
| **Webhook palsu** (WhatsApp) | Tanda tangan HMAC-SHA256 atas isi mentah; tanpa app secret berarti ditolak; pesan ber-ID dideduplikasi 24 jam | `backend/halio/security.py` |
| **Penyalahgunaan dan biaya** | Batas laju per kunci per menit, kuota harian untuk panggilan berbayar, batas ukuran isi permintaan | `security.py` (`RateLimiter`, `DailyBudget`), `api.py` |
| **XSS dan clickjacking** | CSP: `script-src 'self'` ditambah satu hash, `object-src 'none'`, `frame-ancestors 'none'`; keluaran di UI di-escape | `backend/halio/api.py` (`CSP`), `web/app.js` |
| **Akses Radar dan antrean review** | Tertutup dari jaringan kecuali `RADAR_TOKEN` diisi; permintaan lewat proxy tidak dianggap lokal; `HALIO_RADAR_PUBLIC=1` harus dinyalakan eksplisit | `netguard.py` (`is_direct_local`) |
| **Kebocoran data pribadi** | Pembersihan PII sebelum proses; hasil cek disimpan di memori paling lama 1 jam; Radar hanya menyimpan agregat; data tak dikenal, banding, dan audit dihapus setelah `HALIO_RETENTION_DAYS` (bawaan 30) | `pii.py`, `store.py`, [docs/PRIVACY.md](docs/PRIVACY.md) |
| **Rantai pasok** | Dependensi Python di-pin, aksi GitHub di-pin ke SHA, `pip-audit` dan Dependabot berjalan | `backend/requirements.txt`, `.github/workflows/ci.yml`, `.github/dependabot.yml` |
| **Kode jarak jauh** | Mesin luring di browser dan ekstensi MV3 hanya memakai berkas yang dibundel; ekstensi tidak memuat kode dari CDN | `web/engine/`, [extension/README.md](extension/README.md) |

## Celah yang kami ketahui (belum diperbaiki)

- **Satu token Radar bersama**, belum ada akun dan peran per analis; rotasi token manual.
- **Batas laju, kuota harian, dan cache berlaku per proses**, bukan bersama; bila dijalankan lebih dari satu proses, batasnya tidak dibagi.
- **Egress server belum dibatasi di firewall VM.** Pertahanan lapis pertama ada di kode (`PinnedTransport`), lapis kedua belum dipasang (lihat [docs/LAUNCH_READINESS.md](docs/LAUNCH_READINESS.md) dan [docs/DEPLOY_UPDATE.md](docs/DEPLOY_UPDATE.md)).
- **K-anonimitas bukan jaminan anonimitas.** Belum ada uji serangan korelasi atau komposisi.
- **Tinjauan hukum pelindungan data pribadi belum dilakukan**; belum ada uji penetrasi oleh pihak ketiga.
- **Tiket eskalasi menyimpan tujuan balasan mentah** (mis. ID obrolan Telegram) sampai tiket selesai dan masa retensi lewat, karena dibutuhkan untuk mengirim jawaban.
- **Di mode cloud**, foto atau suara asli dikirim utuh ke layanan AI bila `HALIO_MEDIA=1`, dan foto investigasi ke Cloud Vision bila diaktifkan (lihat [docs/PROFIL_PENERAPAN.md](docs/PROFIL_PENERAPAN.md)).
- Mesin luring di browser dijaga identik dengan Python oleh uji paritas, tetapi **belum diaudit keamanannya secara terpisah**.

Sebagian celah ini bisa dihindari dengan profil tanpa cloud (`HALIO_LLM=0`, `HALIO_MEDIA=0`; lihat [docs/LURING.md](docs/LURING.md)).

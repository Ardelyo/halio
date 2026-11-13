# Status Pengumpulan Karya

> **Jenis:** Rujukan · **Untuk:** tim dan juri · [Peta dokumen](README.md)

Batas: **15 Nov 2026, 23.59 WIB** (Rulebook §G). Target internal: **14 Nov 20.00 WIB**. Kirim lewat platform CODEPOLITAN (`codepolitan.com/dashboard/kartika-cyber-hackathon-2026`). Satu pengiriman per tim. Pembaruan boleh sampai batas waktu; hanya yang terakhir dinilai. Penjurian online 16 Nov, finalis diumumkan 20 Nov, final fisik 24 Nov di Jakarta (minimal satu perwakilan hadir).

Aturan dokumen ini: hanya tandai **SELESAI** bila ada bukti yang bisa dibuka. Sisanya **BELUM TERVERIFIKASI** sampai pemilik tindakan mengisi buktinya.

Pemeriksaan terakhir: 12 Nov 2026, dari `main` (kode dan server publik build `281dc9e`, rilis `v0.2.0-submission`). Pada 12 Nov: 266 tes lulus, `eval/RESULTS.md` identik dengan hasil run baru, semua tautan publik di dokumen ini menjawab HTTP 200, dan `/health` server publik melaporkan build `e16d354`.

## Pendaftaran (Rulebook §E)

| Item | Status | Bukti/URL | Pemilik tindakan |
|---|---|---|---|
| Semua anggota punya akun CODEPOLITAN aktif | BELUM TERVERIFIKASI | | Ketua tim |
| Nama tim, data anggota (maks. 3), nomor WhatsApp, alamat/provinsi/kota, pekerjaan, institusi | BELUM TERVERIFIKASI | | Ketua tim |
| Nama Karya **Halio**, Kategori **Siber Sosial**, Deskripsi Karya | BELUM TERVERIFIKASI | Draf: [submission/DRAF_DESKRIPSI.md](submission/DRAF_DESKRIPSI.md) | Ketua tim |
| Konfirmasi WNI dan persetujuan S&K | BELUM TERVERIFIKASI | | Semua anggota |
| Bergabung di grup WhatsApp resmi | BELUM TERVERIFIKASI | | Semua anggota |
| Usia anggota dicatat (Golden Ticket hanya untuk pemenang < 26 tahun, menurut Rulebook) | BELUM TERVERIFIKASI | | Ketua tim |

## Berkas wajib (Rulebook §G)

| # | Item | Spesifikasi | Status | Bukti/URL | Pemilik tindakan |
|---|---|---|---|---|---|
| 1 | Link Karya | Tautan publik yang bisa dicoba juri | SELESAI (12 Nov): tautan utama dipilih | **Dipakai di form:** `https://halio.ardelyo.com/cek.html` (HTTP 200, HTTPS valid, `/health` build `281dc9e-20261112-1423`, `llm:true`, `media:true`). Cadangan, mengikuti IP VM: `https://34-101-109-211.sslip.io/cek.html`. Pages (simulasi): `https://ardelyo.github.io/halio/` (200). Bot: `t.me/halioid_bot` (200). Repo publik: `github.com/Ardelyo/halio` (200) | Pemilik: isi tautan utama di form |
| 2 | Thumbnail | 1200×630 px, JPG/PNG/WebP, ≤ 500 KB | SELESAI (resmi: kolase, 12 Nov) | **Dipakai:** `docs/submission/thumbnail_kolase.jpg`, 1200×630, JPEG, 181 KB (foto Nenek dan cucu, sama dengan gambar di README). Cadangan: `docs/submission/thumbnail.jpg`, 1200×630, JPEG, 183 KB | Pemilik: unggah |
| 3 | Screenshot | Maks. 5 | SELESAI (berkas ada, 12 Nov) | `docs/submission/screenshot_01.png` sampai `screenshot_05.png` (1920×1080, dari rekaman layar build `e16d354`): 1) tempel pesan, 2) jawaban bersumber, 3) suara, trik, dan kartu, 4) "tidak mau menebak", 5) Radar (angka simulasi, disebut di gambar) | Pemilik: tinjau, unggah |
| 4 | Video | ≤ 10 menit, YouTube | SELESAI (12 Nov) | [youtu.be/s2EMpZI2r4g](https://youtu.be/s2EMpZI2r4g): publik (bukan unlisted), durasi 5:01, tayang 12 Nov 2026 | Pemilik: tonton ulang (lihat baris verifikasi akhir) |
| 5 | Slide | Fitur, arsitektur, teknologi, info lain; PDF | SELESAI (resmi: deck juri, 13 Nov) | **Dipakai:** `docs/presentasi/Halio_Deck_Juri.pdf` (23 halaman): deck cerita bersama Nenek (`Halio_Deck_Cerita.pdf`, slide 1-10 dan penutup) ditambah lampiran teknis L1-L10 (L10: mode luring) dari `Halio_Presentasi_v2.pdf` (arsitektur, cara kerja, sumber, Telusur, laporan analis, brief harian TNI AD, privasi, pengaman, hasil uji) dan halaman QR. Dibangun ulang dengan `python docs/presentasi/build_juri_deck.py`; angka dicek terhadap kode 13 Nov | Pemilik: unggah |

## Kepatuhan aturan (Rulebook §G "Ketentuan Karya" dan §N)

| Item | Status | Bukti | Pemilik tindakan |
|---|---|---|---|
| Karya yang sudah ada dideklarasikan | SELESAI | [THIRD_PARTY.md](THIRD_PARTY.md) §Deklarasi | |
| Bantuan AI dalam pengembangan dideklarasikan | SELESAI | [THIRD_PARTY.md](THIRD_PARTY.md) §Deklarasi pengembangan dengan bantuan AI | |
| Semua pustaka, API, model pihak ketiga diatribusi | SELESAI (diperiksa dari kode 10 Nov) | [THIRD_PARTY.md](THIRD_PARTY.md) | |
| Lisensi dan HKI dinyatakan | SELESAI | [LICENSE](../LICENSE) (Apache-2.0), README §Hak kekayaan intelektual | |
| Tidak ada pornografi, SARA, ujaran kebencian, konten ilegal (repo, video, slide, feed demo) | BELUM TERVERIFIKASI untuk video final | Repo dan slide tidak memuatnya menurut pemeriksaan tim; YouTube menandai video "family safe", tetapi isinya belum ditinjau pemilik | Pemilik: tonton ulang video final |
| Tidak ada data pribadi pihak ketiga | SEBAGIAN | Nama Nenek disamarkan di repo (md + PDF); persetujuan tertulis disimpan di luar repo (menurut pemilik). Nama itu masih ada di riwayat git lama | Pemilik: pastikan video tidak menampilkan nomor/kontak/notifikasi orang lain |
| Tidak melanggar HKI pihak lain | SELESAI untuk korpus | Korpus memakai ringkasan kata sendiri + tautan; arsip crawler tidak di-commit. Status tautan: [VERIFIKASI_KORPUS.md](VERIFIKASI_KORPUS.md) | |

## Verifikasi akhir (14 Nov)

| Item | Status | Pemilik tindakan |
|---|---|---|
| Buka setiap tautan di jendela privat, di ponsel dan laptop | BELUM | Pemilik |
| Teruskan pesan baru ke bot dari ponsel non-tim | BELUM | Pemilik |
| Radar terbuka; banner data simulasi tampil bila datanya simulasi | BELUM (perbaikan banner di Track B, perlu deploy) | Pemilik |
| Video bisa diputar, ≤ 10.00, audio terdengar, teks terbaca | Sebagian: bisa dibuka tanpa masuk akun, publik, 5:01. Audio dan teks belum ditonton ulang | Pemilik |
| Proyek GCP `gemma4good-494311` aktif dan berbayar sampai 24 Nov; pemantau uptime aktif; tidak ada deploy 16–20 Nov | BELUM TERVERIFIKASI | Pemegang proyek GCP |
| Hasil uji demo pada build final dicatat | Lihat [BUKTI_UJI_DEMO.md](BUKTI_UJI_DEMO.md) | |

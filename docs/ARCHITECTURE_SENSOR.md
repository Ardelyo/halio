# Arsitektur Sensor Halio: pemantauan narasi yang sadar cakupan

Dokumen rancangan dan bukti riset (28 Okt 2026). Bagian bertanda **(terukur)** berasal dari uji kami sendiri; **(vendor)** dari blog pihak ketiga yang belum diverifikasi ke sumber resmi; **(belum diverifikasi)** belum kami uji sama sekali.

## 1. Pertanyaan yang dijawab

> Apakah bisa memantau disinformasi *benar-benar realtime* sehingga *semua berita terlihat*?

**Tidak.** Yang mungkin: **near-realtime (menit) pada sumber terbuka yang dipilih, dengan cakupan yang diukur dan titik buta yang diakui.** Sensor ini memantau *narasi dan pola penyebarannya*, bukan akun warga, dan tidak menyatakan sesuatu benar atau salah. Itu tetap tugas pemeriksa fakta bernama (lihat `docs/PRIVACY.md`).

Kategori resmi Siber Sosial adalah "pemantauan disinformasi, propaganda, dan opini publik" (kartikacyberhackathon.id). Sensor inilah yang menjawabnya; aplikasi keluarga Halio menjadi salah satu sumber sinyalnya.

## 2. Tiga tingkat kelayakan

| Tingkat | Sumber | Status |
|---|---|---|
| **A: bisa sekarang, gratis** | RSS berita, feed cek fakta, kanal resmi, laporan pengguna Halio | Dipasang (`halio/ingest/sources.py`) |
| **B: butuh anggaran atau izin** | X API berbayar, YouTube (kuota), Telegram publik, Meta Content Library (mitra akademik), vendor | Belum dipasang; tampil sebagai titik buta |
| **C: tidak mungkin** | WhatsApp dan obrolan privat, "semua" | Dinyatakan terbuka |

Alasan untuk tingkat B dan C:

- **X:** sumber vendor menyebut sekitar US$0,005 per post dibaca, batas 3 juta baca per bulan, enterprise mulai sekitar US$42.000 per bulan **(vendor, saling bertentangan)**. Hitungan kasar dari angka itu: membaca 3 juta post sekitar US$15.000 per bulan; sampling 10.000 post per hari sekitar US$50 per hari.
- **Meta Content Library:** hanya untuk lembaga riset nirlaba yang disetujui. **TikTok Research API:** daftar negara yang kami temukan tidak memuat Indonesia dan non-komersial.
- **YouTube Data API:** kuota bawaan 10.000 unit per hari, satu pencarian 100 unit (sekitar 100 pencarian per hari).
- **Telegram publik:** satu analisis pihak ketiga menyebut ketentuan layanan melarang scraping **(belum diverifikasi ke teks resmi)**.
- **Pembanding institusi:** mesin AIS Komdigi berbasis kata kunci dan pada 2019 mengais situs tiap sekitar dua jam, lalu diverifikasi manusia. Jadi "realtime penuh" bukan standar bahkan bagi pemerintah.
- **Verifikasi adalah penghambat sebenarnya:** pemeriksa fakta butuh jam sampai hari. Realtime hanya berlaku untuk *deteksi penyebaran*.

## 3. Uji sumber 28 Okt 2026 (terukur, satu cuplikan, IP bersama)

54 kandidat diuji; **23 dipasang**. Sisanya gagal atau basi:

| Hasil | Kandidat |
|---|---|
| Hidup dan dipasang (22) | ANTARA terkini, CNN Indonesia (nasional, internasional, teknologi, ekonomi), CNBC Indonesia, detikNews, Liputan6 (news, tekno, cek fakta), Republika, Okezone, VIVA, kumparan, Media Indonesia, SINDOnews, Tempo terkini, Alinea, TurnBackHoax, CekFakta.com, Kemhan, TNI AD |
| Dipasang sebagai contoh feed basi (1) | Mafindo: entri terbarunya sekitar 195 hari |
| Dibuang: menolak User-Agent jujur kami | Tribunnews (HTTP 403 pada polling nyata, padahal lolos pada uji awal dengan UA mirip browser). Kami tidak menyamar sebagai browser |
| Dibuang: basi | ANTARA per rubrik (politik, hukum, ekonomi, tekno, humaniora: sekitar 1,6 sampai 13 hari tanpa isi baru), Tempo nasional (sekitar 66 jam) |
| Dibuang: 404/403/galat | Kompas (RSS), Komdigi (RSS), Detik (feed semua), Suara, Merdeka, JawaPos, IDN Times, Bisnis.com, Beritasatu, RMOL, BBC Indonesia, BNPB, Polri, Tirto, Inilah, Kominfo lama, TNI (tni.mil.id) |
| Format lain, adapter menyusul | BMKG gempa terkini (`data.bmkg.go.id/DataMKG/TEWS/autogempa.xml`, XML bukan RSS) |
| Kosong atau tidak terbaca | DW Indonesia, VOA Indonesia, Kontan, Gatra |

Temuan desain dari uji ini:

1. **Feed TurnBackHoax dan CekFakta.com tidak punya tanggal terbit.** Waktu "pertama terlihat" dicatat terpisah dari waktu terbit, dan feed tanpa tanggal tidak ikut metrik keterlambatan.
2. **Feed bisa membisu tanpa galat** (rubrik ANTARA, Tempo nasional). Status "basi" wajib dibedakan dari "mati".
3. **Volume sumber utama ringan:** ANTARA terkini sekitar 34 item per jam. Komputasi bukan hambatan; cakupan dan keandalan feed yang menjadi hambatan.
4. **GDELT** diperbarui tiap 15 menit untuk data massal, tetapi satu permintaan kami kena 429 (batas 1 per 5 detik) dan pencarian bahasa Indonesia mengembalikan kosong. Cakupan Indonesia **belum terbukti**, jadi tidak dipasang.
5. Bluesky (pencarian publik) dan Reddit memberi 403 dari lingkungan uji kami; Mastodon dan pratinjau web Telegram terjangkau tetapi tidak dipasang (lihat tingkat B).

### Hasil polling nyata pertama (terukur, ±5 menit, 28 Okt 2026)

Server dijalankan dengan `HALIO_SENSOR=1` terhadap 24 feed (termasuk Tribunnews sebelum dikeluarkan). Siklus pertama mengambil 1.322 judul (semua ditandai riwayat), 23 dari 24 sumber menjawab. Setelah dua siklus: 22 sumber `hidup`, 1 `basi` (Mafindo, sesuai harapan), 1 ditolak (Tribunnews). Median keterlambatan lihat sekitar 2,5 menit (153,5 detik) dari 8 feed bertanggal yang menerbitkan item baru selama pengamatan; angka ini dari jendela yang sangat pendek dan **belum dapat dijadikan klaim kinerja**. Item per jam belum dihitung karena pengamatan kurang dari satu jam.

## 4. Lapisan arsitektur

```
L0 Sumber     RSS/Atom berita, cek fakta, kanal resmi, tipline Halio, (opsional) X/YouTube, impor CSV mitra
L1 Ingest     penjadwal per sumber (cadence, GET bersyarat ETag/Last-Modified, backoff), metadata minimal    [SELESAI]
L2 Normalisasi  textnorm + sidik jari judul (near-duplicate)                                                  [sidik jari SELESAI]
L3 Narasi     embedding multilingual + klaster inkremental; klaim dari claims.py                              [BELUM]
L4 Verifikasi pencocokan ke korpus cek fakta + sumber resmi (retrieval.py), tiga keadaan + abstain           [pipeline ada; belum disambung ke sensor]
L5 Sinyal     kecepatan per jam, keberagaman sumber, sinkronisasi judul nyaris identik antar-sumber           [BELUM]
L6 Triase     skor ancaman institusi x keyakinan x kecepatan; analis manusia; paket bukti + log audit         [BELUM]
L7 Tampilan   panel cakupan dan titik buta                                                                   [SELESAI: /coverage]
              Radar v2 (narasi, garis waktu, waktu-ke-sinyal)                                                [BELUM]
```

Yang sudah berjalan di repo (`backend/halio/ingest/`):

| Berkas | Fungsi |
|---|---|
| `sources.py` | Registri 23 sumber dan 7 titik buta, tiap sumber dengan cadence dan batas "diam" sendiri |
| `parse.py` | Parser RSS dan Atom. Menolak feed yang mendeklarasikan entity (perlindungan billion-laughs) atau lebih dari 3 MB. Hanya judul, tautan, waktu, cuplikan 200 karakter |
| `fetcher.py` | GET bersyarat, backoff eksponensial sampai 1 jam, `run_once` (thread untuk jaringan, tulis DB di satu thread), `Poller` latar belakang (`HALIO_SENSOR=1`) |
| `store.py` | Tabel `sensor_state`, `sensor_items`, `sensor_log`. Item riwayat saat polling pertama ditandai `backfill` dan tidak dihitung dalam statistik |
| `coverage.py` | Status `hidup / basi / tertunda / mati / belum`, item per jam, median respons, median keterlambatan lihat, daftar titik buta |

Antarmuka: `GET /api/sensor/coverage`, `GET /api/sensor/items`, halaman `/coverage`. Keduanya mengikuti `RADAR_TOKEN` yang sama dengan Radar.

### Dua rancangan yang menjadi pembeda

- **Panel cakupan dan titik buta.** Menjawab "apakah semua berita terlihat" dengan jujur: sumber mana yang hidup, seberapa segar, dan apa yang tidak dilihat.
- **Waktu-ke-sinyal** (rencana): berapa menit dari kemunculan sebuah narasi sampai sensor menandainya. Dapat diukur, tidak memerlukan klaim akurasi.

## 5. Tata kelola: pagar yang melekat pada rancangan

Pada September 2025 patroli siber Satsiber TNI terhadap seorang kreator konten dikritik koalisi sipil sebagai militerisasi ruang siber; SETARA menilai UU TNI 2025 hanya memberi mandat *pertahanan siber*, bukan penegakan hukum. Rancangan ini dibuat agar tidak jatuh ke wilayah itu:

1. **Ruang lingkup:** ancaman terhadap institusi (penipuan dan akun yang mencatut TNI, pernyataan atau video palsu atas nama pejabat, kebocoran informasi operasional dari sumber publik, rumor yang mengganggu satuan). Bukan kritik atau opini warga.
2. **Sumber:** media dan lembaga, bukan akun pribadi. Tidak ada profil akun individu secara default.
3. **Tingkat narasi dan agregat.** Halio melaporkan *bahwa* sebuah narasi menyebar, tidak menunjuk siapa pelakunya.
4. **Tanpa takedown, tanpa pelaporan otomatis.** Eskalasi hanya lewat analis manusia dan jalur formal.
5. **Retensi pendek:** metadata item 30 hari, log pengambilan 7 hari (`SensorStore.prune`).
6. **Log audit dan tinjauan analis** sebelum alert dianggap temuan (L6).
7. **Tinjauan hukum UU PDP diperlukan** sebelum penerapan sungguhan. Ringkasan sumber yang kami baca menyebut kewajiban pejabat pelindungan data untuk pemantauan sistematis berskala besar, tetapi dasar hukum pemrosesan oleh instansi **belum kami verifikasi ke teks undang-undang**.

## 6. Evaluasi yang jujur (rencana)

| Metrik | Cara |
|---|---|
| Latensi respons dan ketersediaan per sumber | Sudah terukur otomatis (`/api/sensor/coverage`) |
| Keterlambatan lihat (terbit ke terlihat) | Sudah terukur untuk feed yang bertanggal |
| Presisi alert | Sampel alert diberi label oleh manusia, laporkan termasuk kegagalan |
| Tingkat alert palsu | Dari sampel yang sama |
| Waktu-ke-sinyal | Catat prospektif 1 sampai 12 Nov, bandingkan dengan tanggal bantahan di TurnBackHoax |
| Mutu embedding Bahasa Indonesia | Uji sendiri pada data kami; pencarian kami tidak menemukan angka khusus Bahasa Indonesia |

## 7. Batas dan hal yang belum diverifikasi

- Uji sumber adalah **satu cuplikan** dari satu lingkungan; ketersediaan feed berubah-ubah dan sebagian media bisa memblokir pengambilan otomatis.
- Setiap media punya ketentuan penggunaan sendiri; kami hanya membaca feed publik dengan User-Agent yang jelas dan frekuensi sopan. Tinjauan ketentuan per sumber belum dilakukan.
- Lapisan L3 sampai L6 belum dibangun. Sampai itu selesai, sensor baru dapat menunjukkan *cakupan dan kesegaran*, belum *deteksi narasi*.
- Angka harga X, kuota YouTube, dan status Telegram/TikTok/Meta berasal dari pencarian web dan perlu dikonfirmasi ke dokumentasi resmi masing-masing.

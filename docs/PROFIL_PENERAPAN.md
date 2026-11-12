# Profil Penerapan: T1 Tanpa Cloud dan T2 Cloud Opsional

Halio bisa dijalankan dalam dua profil. Keduanya memakai kode yang sama. Bedanya hanya variabel lingkungan dan apakah server boleh memanggil layanan cloud. Dokumen ini menjelaskan apa yang tersedia di tiap profil dan **data apa yang keluar dari server**. Semua pernyataan di bawah merujuk ke berkas kode. Halio belum disertifikasi atau disetujui pihak mana pun untuk dipakai di lingkungan TNI AD.

## T1: on-premise, tanpa cloud AI

Konfigurasi: `HALIO_LLM=0` (bawaan), `HALIO_MEDIA=0`, tanpa `GOOGLE_FACTCHECK_API_KEY`. Per permintaan juga bisa dengan `mode=tanpa_ai` (API), `/tanpaai` (Telegram), atau centang "tanpa AI" di web. Mode ini tidak pernah memanggil model.

**Yang bisa:**
- Mencocokkan pesan dengan korpus bantahan lokal `data/debunks.json`: TF-IDF kata + trigram huruf, ditambah penjaga inti klaim dan negasi (`retrieval.py`). Tanpa jaringan; median 0,9 ms di laptop pengembang.
- Tiga dari lima keadaan vonis (terbukti salah, tidak yakin, belum ada pemeriksaan). Dua lainnya butuh mesin bukti pada profil T2.
- Menghapus data pribadi (`pii.py`), mendeteksi trik manipulasi (`manipulation.py`), membuat Kartu Halio (`card.py`).
- Radar agregat, k-anonimitas, antrean eskalasi dan banding, Radar analis (`store.py`, `review.py`).
- Suara: bila Cloud TTS dan gTTS tidak bisa dihubungi, API menjawab 501 dan web memakai suara bawaan perangkat.
- Ekstensi Chrome: lencana dan penyaringan gambar sepenuhnya di perangkat.

**Yang tidak bisa:**
- Memeriksa kabar yang belum ada di korpus. Hasilnya selalu "belum ada pemeriksaan". Cakupan sama persis dengan isi korpus (7 bantahan pada prototipe ini), jadi korpus perlu diisi tim penerangan atau pemeriksa fakta.
- Halio Telusur dan brief harian (butuh Gemini).
- Membaca foto dan rekaman suara.
- Pencarian gambar terbalik.

Sensor feed (`HALIO_SENSOR=1`) dan cek tautan (`HALIO_LINK_CHECK`) tidak memakai AI, tetapi butuh akses internet keluar ke situs publik. Di jaringan tertutup, matikan keduanya.

## T2: cloud opsional (Google Cloud, Vertex AI)

Konfigurasi: `HALIO_LLM=1`, `HALIO_LLM_PROVIDER=google`, opsional `HALIO_MEDIA=1`, kredensial akun layanan VM (ADC) dengan peran Vertex AI User. Server publik demo memakai profil ini.

### Data yang keluar dari server

| Tujuan | Data yang dikirim | Kapan | Kode |
|---|---|---|---|
| Gemini (Vertex AI) | Teks klaim yang sudah dibersihkan (nomor, NIK, email, rekening, tautan, @akun dihapus; maks. 300 karakter), kueri pencarian turunannya, dan potongan kutipan dari halaman publik yang dibuka | Setiap cek dengan `HALIO_LLM=1` yang perlu mencari bukti; setiap investigasi Telusur | `claims.py`, `pii.py`, `evidence.py`, `google_agent.py`, `investigate/` |
| Gemini, media | **Berkas foto atau rekaman suara asli** dari pengguna. Gambar tidak disaring PII sebelum dikirim | Hanya bila `HALIO_MEDIA=1` dan pengguna mengirim media | `media.py` |
| Cloud Vision | **Foto asli** yang dilampirkan ke investigasi | Hanya Telusur dengan foto, dan bila Vision API aktif di proyek | `investigate/reverse_image.py` |
| Cloud Text-to-Speech | Naskah suara yang disusun Halio dari hasil cek (sapaan, vonis, ringkasan bantahan, nama sumber). Bukan pesan asli pengguna | Saat pengguna menekan "Dengarkan" | `voice.py`, `pipeline._voice` |
| Google Fact Check Tools | Kueri klaim maks. 200 karakter | Hanya bila kunci API diisi | `factcheck_api.py`, `investigate/tools.py` |
| GDELT DOC API | Empat kata kunci yang berbeda dari klaim | Telusur | `investigate/tools.py` |
| Internet Archive | URL halaman publik | Halaman bukti diblokir, atau mencari tangkapan pertama | `source_verifier.py`, `investigate/tools.py` |
| Situs sumber | Permintaan HTTP biasa dari IP server untuk membuka halaman bukti | Setiap cek bukti dan Telusur | `source_verifier.py`, `link_check.py` |

Yang **tidak** dikirim: pesan asli utuh (hanya klaim terpilih yang dibersihkan), nomor telepon atau ID Telegram pelapor, isi Radar, dan data antrean eskalasi.

Yang **disimpan** di server sendiri (SQLite) dijelaskan di [PRIVACY.md](PRIVACY.md).

### Batas biaya dan beban
`HALIO_AGENT_DAILY_CAP` dan `HALIO_AGENT_PER_REPORTER` membatasi Telusur. `HALIO_RATE_LIMIT` membatasi permintaan per menit per klien. Rekomendasi nilai untuk masa penjurian ada di `.env.example`.

### Bila model salah, lambat, atau mati
Model tidak pernah memutuskan vonis. Kode yang memutuskan berdasarkan kutipan yang disalin kode dari halaman yang dibuka kode (`evidence.decide`). Bila mesin bukti v2 gagal, Halio mencoba agen lama (`mesin cadangan`). Bila itu juga gagal atau tidak menemukan apa-apa, hasil T1 lokal tetap berlaku: bantahan kurasi yang cocok tidak hilang, dan kabar di luar korpus menjadi "belum ada pemeriksaan" (`pipeline.check`). Halio tidak menebak.

## Matriks fitur × profil

| Fitur | T1 tanpa cloud | T2 cloud |
|---|---|---|
| Cocokkan dengan korpus bantahan lokal | ✅ | ✅ |
| Hapus data pribadi, trik manipulasi, Kartu Halio | ✅ | ✅ |
| Radar agregat, k-anonimitas, antrean manusia | ✅ | ✅ |
| Bukti web untuk kabar di luar korpus (kutipan disorot) | ❌ "belum ada pemeriksaan" | ✅ |
| Halio Telusur, brief harian | ❌ | ✅ |
| Baca foto dan suara | ❌ | ✅ bila `HALIO_MEDIA=1` |
| Pencarian gambar terbalik | ❌ | ✅ bila Vision API aktif |
| Suara resmi (Chirp 3 HD) | ❌ suara perangkat | ✅ |
| Sensor feed publik, cek tautan | Butuh internet keluar, tanpa AI | ✅ |
| Ekstensi Chrome (di perangkat) | ✅ | ✅ |

## Catatan kedaulatan data
- T1 dapat berjalan di server satuan dalam satu kontainer Docker, tanpa GPU dan tanpa layanan pihak ketiga. Data tetap di server itu.
- Pada T2, data di tabel di atas diproses Google Cloud menurut ketentuannya. Lokasi Vertex AI saat ini `global` (`GOOGLE_CLOUD_LOCATION`). Kami belum memeriksa apakah ada lokasi regional Indonesia untuk model yang dipakai, dan apakah pemrosesan di sana memenuhi kebijakan satuan.
- Kepatuhan pada UU PDP (UU 27/2022) belum ditinjau ahli hukum. Lihat [LAUNCH_READINESS.md](LAUNCH_READINESS.md).
- Untuk lingkungan yang tidak boleh memakai cloud publik, jalur yang realistis adalah T1 dengan korpus yang diisi pemeriksa internal. Mengganti Gemini dengan model yang di-hosting sendiri belum diuji.

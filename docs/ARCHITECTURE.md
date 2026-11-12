# Arsitektur Teknis Halio

> **Jenis:** Rujukan · **Untuk:** juri dan pengembang · [Peta dokumen](README.md)

Dokumen teknis untuk Dewan Juri dan pengembang. Bagian bertanda **(estimasi)** belum diukur.

## 1. Gambaran umum

```
                ┌───────────────────────── Perangkat pengguna ─────────────────────────┐
 Ibu Sri ──────►│ Telegram / WhatsApp / Web (PWA, share target Android)                 │
                │ Ekstensi Chrome: lencana "Perlu dicek?" + blur gambar (di perangkat)  │
                └───────────────┬──────────────────────────────────────────────────────┘
                                │ hanya teks yang DITERUSKAN/DIKLIK pengguna
                                ▼
 ┌──────────────────────────── Server Halio (1 kontainer Docker) ────────────────────────────┐
 │ /api/check                                                                                │
 │  1. Ekstraksi klaim  (claims.py: kalimat paling layak-cek, buang salam/opini)             │
 │  2. Hapus data pribadi (pii.py: nomor, NIK, email, tautan, @akun; maks. 300 karakter)     │
 │  3. T1 lokal: TF-IDF kata + trigram huruf atas korpus bantahan (retrieval.py)             │
 │     + penjaga inti klaim (syarat + deteksi negasi)                                        │
 │  4. T1 jarak jauh (opsional): Google Fact Check Tools / ClaimReview                       │
 │  5. T2 (opsional): LLM hanya memilih kandidat + wajib kutipan persis → diverifikasi       │
 │  6. Vonis 5 keadaan + teks suara + trik manipulasi + peringatan tautan                    │
 │                                                                                           │
 │ /api/card/{id}.png  Kartu Halio (Pillow)     /api/voice/{id}.mp3  Halio Suara (Cloud TTS*) │
 │ /api/escalate, /api/appeal  antrean pemeriksa manusia                                      │
 │ /api/radar  agregat anonim (SQLite → Postgres)                                             │
 └───────────────────────────────────────────────────────────────────────────────────────────┘
```

\* Suara: Google Cloud Text-to-Speech (Chirp 3 HD, `voice.py`) dengan kredensial VM. Bila tidak tersedia, cadangan gTTS; bila itu juga gagal, API menjawab 501 dan web memakai suara bawaan peramban.

| Tingkat | Tempat | Fungsi | Latensi | Biaya |
|---|---|---|---|---|
| T0 | Perangkat | Lencana trik manipulasi, deteksi judol, blur gambar NudeNet (opsional) | puluhan ms/gambar **(estimasi)** | 0 |
| T1 | Server | Pencocokan dengan korpus bantahan lokal, opsional ClaimReview | median 0,9 ms, p95 1,6 ms (diukur 27 Okt di laptop pengembang, korpus 7 bantahan, tanpa jaringan) | ≈ 0 |
| T2 | Cloud (opsional) | LLM menimbang klaim vs kandidat, wajib kutipan | 3–8 s **(estimasi)** | per panggilan; mati secara default |

## 2. Lima keadaan vonis

Jalur pencocokan lokal (tanpa AI) menghasilkan tiga keadaan pertama di bawah ini. Dua keadaan lainnya, `sejalan_dengan_sumber` dan `dilaporkan_media`, hanya muncul bila mesin bukti aktif. Alasannya dijelaskan di [TRUE_INFORMATION.md](TRUE_INFORMATION.md).

| Status | Kapan | Yang dikatakan Halio |
|---|---|---|
| `terbukti_salah` | Skor kemiripan ≥ ambang **dan** inti klaim palsu hadir tanpa negasi (atau dikonfirmasi LLM dengan kutipan) | Penjelasan sederhana + nama sumber + tautan |
| `tidak_yakin` | Mirip topik tapi tidak sama; inti klaim tidak ada/dinegasikan; bukti bertentangan atau kedaluwarsa; atau bukan klaim faktual | Jujur bahwa Halio ragu; tawarkan pemeriksa manusia |
| `belum_ada_pemeriksaan` | Tidak ada bantahan yang cocok | "Halio tidak mau menebak"; sebut trik manipulasi bila ada; tawarkan pemeriksa manusia |
| `sejalan_dengan_sumber` | Sumber resmi yang masih berlaku memuat kutipan yang mendukung seluruh klaim, dan kutipan itu dicek ulang oleh kode | Boleh dibagikan, tetapi cek tanggal dan konteksnya di sumber dulu |
| `dilaporkan_media` | Beberapa media independen memberitakannya dan tidak ada yang membantah | Ini laporan media, bukan pemeriksaan fakta; sebut sumbernya dan cek tanggalnya |

**Penjaga inti klaim.** Kemiripan kata saja tidak bisa membedakan "BMKG *memprediksi* gempa tanggal 12" (hoaks) dari "BMKG *mencatat* gempa M5,1 pagi ini" (fakta). Setiap bantahan memuat `syarat`: pola inti klaim palsu (memprediksi tanggal, membayar agar lulus, dsb.). Bila pola itu tidak ada, atau didahului "tidak/tanpa/bukan", hasil dibatasi menjadi `tidak_yakin`. Pada set uji, penjaga ini menurunkan tingkat "salah tuduh hoaks" dari 8% menjadi 0% (lihat `eval/RESULTS.md`).

**LLM terkekang (anti-halusinasi).** LLM tidak boleh memberi vonis dari pengetahuannya sendiri. LLM hanya memilih apakah klaim sama dengan salah satu kandidat bantahan, dan harus menyalin kutipan persis dari teks "fakta" kandidat. Server memeriksa kutipan sebagai substring; jika gagal, vonis tidak pernah dinaikkan. LLM hanya dapat **mengonfirmasi dengan bukti** atau **menurunkan** vonis.

## 3. Radar Ketahanan Kognitif

Tujuan: pemantauan ruang siber sosial (definisi kategori Siber Sosial) tanpa memata-matai warga.

- Setiap cek mencatat **hanya**: tanggal, status, id bantahan, kategori, daftar trik, kanal. Tidak ada isi pesan, identitas, atau lokasi.
- Kabar yang belum dikenal dihitung dengan **hash** isi yang dinormalisasi. Pelapor dihitung dengan **nama samaran harian** (`sha256(garam_harian + id)`); garam hari sebelumnya dihapus sehingga tidak bisa ditautkan antarhari.
- Isi kabar baru disimpan **hanya setelah ≥ k pelapor berbeda** (default k = 5) mengirim kabar yang sama di hari yang sama, yaitu ketika kabar itu terbukti beredar publik dan bukan pesan pribadi.
- Sel agregat < 3 ditampilkan sebagai "<3".
- Kategori `penipuan_catut_tni` disorot: penipuan rekrutmen, akun palsu perwira, dan deepfake pejabat TNI AD adalah ancaman non-teknis yang langsung relevan bagi satuan.
- Data simulasi (kanal `demo`) selalu diberi spanduk di halaman Radar.

## 4. Ekstensi Chrome (lapisan feed)

- **Manifest V3**: content script mengamati DOM (`[role=article]`, `article`), service worker mengatur pesan, offscreen document menjalankan inferensi (izin `offscreen`).
- **Teks**: analisis trik manipulasi berjalan di halaman. Teks hanya dikirim ke server saat pengguna menekan "Cek dengan Halio", setelah dibersihkan (maks. 300 karakter).
- **Gambar**: mode `judol` (kata kunci pada alt/tautan/teks sekitar), `pintar` (NudeNet 320n ONNX via onnxruntime-web di offscreen document, *fail-closed*), `semua`, atau `mati`. Gambar diambil dan dianalisis di dalam ekstensi; **tidak ada byte gambar yang dikirim**. Popup menampilkan penghitung transparansi.
- Aturan kode jarak jauh MV3: runtime WASM dan bobot model dipaketkan lokal (`scripts/fetch_models.py`), tidak dimuat dari CDN saat berjalan.
- Keterbatasan: DOM platform berubah-ubah; WebGPU tidak dipakai (WASM satu thread); NudeNet tidak mendeteksi kekerasan; belum ada angka akurasi publik. OCR banner judol ada di peta jalan.

## 4a. Halio Telusur (investigasi untuk analis)

Jalur kedua di samping `/api/check`, untuk analis di Radar (`/api/investigate`, `/api/brief`). Butuh `HALIO_LLM=1`. Kode ada di `backend/halio/investigate/`.

1. **Arsip "sudah diperiksa"** (`archive.py`): klaim dicocokkan dulu dengan judul cek fakta dari sensor dan `data/arsip.jsonl`. Kecocokan hanya **petunjuk**: URL-nya tetap dibuka dan dikutip oleh mesin bukti.
2. **Rencana kueri** (`planner.py`): model mengusulkan kueri; kode membatasi, membersihkan, dan menyediakan cadangan.
3. **Swarm** (`roles.py`, `tools.py`): beberapa agen pencari berjalan bersamaan (Google via grounding Gemini, arsip sensor, ClaimReview, GDELT, gambar terbalik Cloud Vision) dan mengisi satu kolam bukti yang dideduplikasi. Tiap agen adalah strategi pencarian, bukan model yang bebas bertindak. Sumber yang mati dilaporkan sebagai titik buta.
4. **Buka halaman dan kutip** (kode, fetch aman): kutipan disalin kode, bukan ditulis model. Halaman yang diblokir boleh diganti salinan Wayback, dengan label.
5. **Model menilai relasi** klaim–kutipan per nomor bukti; **kode** yang memutuskan status (`evidence.decide`).
6. **Asal-usul** (`origin.py`, tanpa model): lini masa, kemunculan paling awal yang *ditemukan* (bukan "asal"), dan varian kalimat.
7. **Laporan** (`dossier.py`): model menulis kalimat; kode hanya menyimpan kalimat yang kata isi dan setiap angkanya ada di kutipan yang dirujuk. Jumlah kalimat yang dibuang ikut dilaporkan.
8. **Versi keluarga** (`keluarga.py`) disusun dari laporan yang sudah diperiksa, tanpa panggilan model baru.

Batas keras: kueri, halaman, detik per investigasi; `HALIO_AGENT_DAILY_CAP` per hari dan `HALIO_AGENT_PER_REPORTER` per pelapor. Pekerjaan disimpan di SQLite (`jobs.py`) sehingga bertahan saat restart. **Brief harian** (`brief.py`) mengelompokkan judul feed publik 48 jam terakhir (topik TNI AD/pertahanan atau feed cek fakta), lalu menjalankan Telusur pada narasi teratas. Yang diprofilkan hanya narasi dan klaim, bukan orang, akun, atau prajurit.

## 5. Penerapan di lingkungan satuan

```bash
docker compose up -d          # API + web + Radar di port 8000
python -m halio.channels.telegram   # bot (atau sebagai layanan kedua di compose)
```

- Tanpa GPU, tanpa API berbayar (LLM & ClaimReview opsional). Dapat berjalan on-premise di server satuan; apa yang hilang tanpa cloud dijelaskan di [PROFIL_PENERAPAN.md](PROFIL_PENERAPAN.md).
- Penyimpanan: SQLite (prototipe) → Postgres untuk produksi; skema kecil di `store.py`.
- Korpus bantahan berupa JSON yang dapat diisi tim penerangan/pemeriksa fakta; setiap entri wajib bersumber.
- Konfigurasi lewat variabel lingkungan (`.env.example`). Radar dapat dikunci dengan `RADAR_TOKEN`.
- Peta jalan produksi: autentikasi peninjau, log transparansi publik, Postgres, pemantauan, uji beban.

## 6. Pengujian

- `pytest` (backend/tests): 265 tes lulus per 12 Nov 2026, dijalankan CI pada setiap perubahan. Cakupan: PII, ekstraksi klaim, trik manipulasi, keadaan vonis, negasi, k-anonimitas, supresi sel kecil, alur API.
- `python eval/run_eval.py`: metrik jujur termasuk tingkat salah tuduh hoaks; `--sweep` untuk kalibrasi ambang.

## 7. Keterbatasan yang kami akui

- Korpus demo kecil (7 bantahan) dan kedua set uji (108 item: dev 52, holdout 56) ditulis tim sendiri, sehingga hasilnya optimistis.
- Pencocokan bersifat leksikal; parafrase berat tanpa kata yang sama akan jatuh ke "belum ada pemeriksaan" (aman, tapi recall turun).
- Kualitas LLM berbahasa Indonesia dan cakupan ClaimReview Indonesia belum diukur.
- Tidak ada uji pengguna lansia Indonesia; efek label peringatan (~25% pengurangan berbagi) berasal dari studi laboratorium Barat (Martel & Rand 2024).
- Halio **tidak** mendeteksi deepfake. Ia mencocokkan klaim dengan bantahan yang sudah ada.

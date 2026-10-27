# Arsitektur Teknis Halio

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
 │  6. Vonis 3 keadaan + teks suara + trik manipulasi + peringatan tautan                    │
 │                                                                                           │
 │ /api/card/{id}.png  Kartu Halio (Pillow)     /api/voice/{id}.mp3  Halio Suara (gTTS)       │
 │ /api/escalate, /api/appeal  antrean pemeriksa manusia                                      │
 │ /api/radar  agregat anonim (SQLite → Postgres)                                             │
 └───────────────────────────────────────────────────────────────────────────────────────────┘
```

| Tingkat | Tempat | Fungsi | Latensi | Biaya |
|---|---|---|---|---|
| T0 | Perangkat | Lencana trik manipulasi, deteksi judol, blur gambar NudeNet (opsional) | puluhan ms/gambar **(estimasi)** | 0 |
| T1 | Server | Pencocokan dengan korpus bantahan lokal, opsional ClaimReview | median 0,9 ms, p95 1,6 ms (diukur 27 Okt di laptop pengembang, korpus 7 bantahan, tanpa jaringan) | ≈ 0 |
| T2 | Cloud (opsional) | LLM menimbang klaim vs kandidat, wajib kutipan | 3–8 s **(estimasi)** | per panggilan; mati secara default |

## 2. Tiga keadaan vonis

| Status | Kapan | Yang dikatakan Halio |
|---|---|---|
| `terbukti_salah` | Skor kemiripan ≥ ambang **dan** inti klaim palsu hadir tanpa negasi (atau dikonfirmasi LLM dengan kutipan) | Penjelasan sederhana + nama sumber + tautan |
| `tidak_yakin` | Mirip topik tapi tidak sama; inti klaim tidak ada/dinegasikan; atau bukan klaim faktual | Jujur bahwa Halio ragu; tawarkan pemeriksa manusia |
| `belum_ada_pemeriksaan` | Tidak ada bantahan yang cocok | "Halio tidak mau menebak"; sebut trik manipulasi bila ada; tawarkan pemeriksa manusia |

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

## 5. Penerapan di lingkungan satuan

```bash
docker compose up -d          # API + web + Radar di port 8000
python -m halio.channels.telegram   # bot (atau sebagai layanan kedua di compose)
```

- Tanpa GPU, tanpa API berbayar (LLM & ClaimReview opsional). Dapat berjalan on-premise di server satuan.
- Penyimpanan: SQLite (prototipe) → Postgres untuk produksi; skema kecil di `store.py`.
- Korpus bantahan berupa JSON yang dapat diisi tim penerangan/pemeriksa fakta; setiap entri wajib bersumber.
- Konfigurasi lewat variabel lingkungan (`.env.example`). Radar dapat dikunci dengan `RADAR_TOKEN`.
- Peta jalan produksi: autentikasi peninjau, log transparansi publik, Postgres, pemantauan, uji beban.

## 6. Pengujian

- `pytest` (backend/tests): PII, ekstraksi klaim, trik manipulasi, tiga keadaan vonis, negasi, k-anonimitas, supresi sel kecil, alur API.
- `python eval/run_eval.py`: metrik jujur termasuk tingkat salah tuduh hoaks; `--sweep` untuk kalibrasi ambang.

## 7. Keterbatasan yang kami akui

- Korpus demo kecil (7 bantahan) dan set uji ditulis tim sendiri, sehingga hasilnya optimistis.
- Pencocokan bersifat leksikal; parafrase berat tanpa kata yang sama akan jatuh ke "belum ada pemeriksaan" (aman, tapi recall turun).
- Kualitas LLM berbahasa Indonesia dan cakupan ClaimReview Indonesia belum diukur.
- Tidak ada uji pengguna lansia Indonesia; efek label peringatan (~25% pengurangan berbagi) berasal dari studi laboratorium Barat (Martel & Rand 2024).
- Halio **tidak** mendeteksi deepfake. Ia mencocokkan klaim dengan bantahan yang sudah ada.

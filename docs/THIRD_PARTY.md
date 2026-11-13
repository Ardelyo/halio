# Komponen Pihak Ketiga & Deklarasi

> **Jenis:** Rujukan · **Untuk:** juri dan panitia · [Peta dokumen](README.md)

Rulebook §G: pustaka, framework, API, model AI, dan alat pihak ketiga boleh dipakai **dengan atribusi**, dan karya yang sudah ada sebelumnya wajib **dideklarasikan dengan jelas**. Berkas ini disusun dari kode di repo (per commit `78b865c`), bukan dari ingatan. Lisensi di bawah adalah yang tercantum pada halaman resmi/PyPI masing-masing; tim belum melakukan tinjauan hukum.

Lisensi karya Halio sendiri: [Apache 2.0](../LICENSE). HKI tetap milik tim (Rulebook §N).

## Deklarasi karya yang sudah ada
Repo dibuat pada 27 Okt 2026 (commit pertama), di dalam periode lomba, berangkat dari laporan riset tim sendiri. Tidak ada kode dari proyek sebelumnya yang dipakai ulang.

## Deklarasi pengembangan dengan bantuan AI
Sebagian besar kode, tes, dan dokumen ditulis bersama agen coding AI (Claude, melalui Claude Code). Angka dari riwayat git `main` per `2561b37` (81 commit non-merge, dihitung 13 Nov 2026):

| | Jumlah |
|---|---|
| Commit berpenulis "Claude" | 19 |
| Commit berpenulis Ardelyo yang memuat trailer `Co-Authored-By: Claude` | 55 |
| Commit berpenulis Ardelyo tanpa trailer AI | 7 |

Pembagian peran:
- **Dikerjakan dengan bantuan AI:** penulisan kode backend, web, dan ekstensi; tes unit; set evaluasi awal; draf dokumen, slide, dan naskah.
- **Keputusan dan tinjauan manusia (tim):** masalah yang dipilih dan pengguna sasarannya; aturan produk inti (vonis diputuskan kode, bukan model; abstain eksplisit; tanpa pemindaian chat); pemilihan dan pemeriksaan sumber korpus bantahan; persetujuan merge setiap PR; deploy server; syuting dan materi video; pengiriman karya.

Model AI juga dipakai **di dalam produk** (bagian "Model & layanan" di bawah). Itu berbeda dari bantuan AI saat pengembangan.

## Perangkat lunak
| Komponen | Kegunaan | Lisensi |
|---|---|---|
| FastAPI, Starlette, Pydantic, Uvicorn | API HTTP | MIT / BSD |
| HTTPX | Klien HTTP | BSD-3 |
| Pillow | Render Kartu Halio | MIT-CMU (HPND) |
| google-genai SDK (+ google-auth) | Panggilan Gemini via Vertex AI; kredensial VM untuk Cloud TTS dan Cloud Vision | Apache-2.0 |
| gTTS (opsional, cadangan) | Suara bila Cloud TTS tidak tersedia (memanggil layanan Google Translate TTS) | MIT; ketentuan layanan di baliknya berlaku |
| anthropic SDK (opsional, penyedia lama) | Konfirmasi kecocokan via Anthropic API | MIT |
| pytest | Tes | MIT |
| onnxruntime-web | Inferensi di perangkat pada ekstensi (dibundel lokal oleh `scripts/fetch_models.py`) | MIT |
| Instrument Serif, Archivo, Inter (Google Fonts) | Tipografi merek di web, ekstensi, Kartu Halio, dan thumbnail | SIL Open Font License 1.1 |
| Playwright + Chromium | Render PDF presentasi (`docs/presentasi/build_deck.py`) | Apache-2.0 / BSD |

## Model & layanan (dipakai saat produk berjalan)
| Komponen | Kegunaan | Di kode | Ketentuan |
|---|---|---|---|
| Google Vertex AI: Gemini 3.5 Flash-Lite (`HALIO_LLM=1`) | Mencari bukti dan menilai relasi klaim–sumber; backend membuka dan memverifikasi setiap URL dan kutipan | `google_agent.py`, `llm_verdict.py` | Ketentuan Google Cloud |
| Grounding Google Search (alat Gemini) | Menemukan halaman kandidat bukti | `google_agent.py` (`types.GoogleSearch`) | Ketentuan Google Cloud |
| Gemini untuk foto & suara (`HALIO_MEDIA=1`) | Membaca teks/klaim dari gambar dan rekaman suara | `media.py` | Ketentuan Google Cloud |
| Google Cloud Text-to-Speech, suara Chirp 3 HD (`id-ID-Chirp3-HD-Aoede`) | Pesan suara bahasa Indonesia | `voice.py` | Ketentuan Google Cloud |
| Google Cloud Vision, WEB_DETECTION | Pencarian gambar terbalik di Telusur (aktif bila API dinyalakan di proyek) | `investigate/reverse_image.py` | Ketentuan Google Cloud |
| Google Fact Check Tools API (opsional) | Pencarian ClaimReview | `factcheck_api.py`, `investigate/tools.py` | Ketentuan Google API; isi ClaimReview milik penerbitnya |
| GDELT DOC 2.0 API | Lini masa kemunculan berita di Telusur | `investigate/tools.py` | Akses publik GDELT Project; sitasi GDELT diminta |
| Internet Archive (Wayback availability + CDX) | Salinan arsip untuk halaman yang diblokir (diberi label) dan tanggal tangkapan pertama | `source_verifier.py`, `investigate/tools.py` | Ketentuan penggunaan Internet Archive |
| Anthropic API (penyedia lama, opsional) | Konfirmasi kecocokan dengan verifikasi kutipan persis | `llm_verdict.py` | Ketentuan penyedia |
| NudeNet 3.4 (ONNX 320n) | Penyaringan gambar dewasa di perangkat (opsional) | `extension/offscreen.js` | MIT (menurut PyPI) |
| 23 feed RSS/Atom terbuka (`HALIO_SENSOR=1`) | Sensor tren; hanya judul, tautan, waktu | `ingest/` | Feed publik; daftar di `docs/ARCHITECTURE_SENSOR.md` |

## Data
| Data | Isi | Catatan |
|---|---|---|
| Korpus bantahan `data/debunks.json` (7 entri) | Ringkasan kata sendiri + tautan sumber | Sumber: Katadata, Bisnis.com, Investortrust, BMKG, Kompas TV, Republika, Liputan6 Cek Fakta (dengan Mafindo), MerahPutih, RRI, Kumparan. Tidak ada teks artikel yang disalin. Status tiap tautan: [VERIFIKASI_KORPUS.md](VERIFIKASI_KORPUS.md) |
| Arsip judul cek fakta `data/arsip.jsonl` | Judul, tautan, dan metadata daftar dari turnbackhoax.id (Mafindo) | Dikumpulkan oleh `scripts/crawl_arsip.py`: `robots.txt` mengizinkan (diperiksa 7 Nov 2026), jeda 2 detik per permintaan, User-Agent beridentitas, tanpa teks artikel. Ketentuan penggunaan Mafindo **tidak ditemukan**, jadi berkas ini **tidak di-commit** (`.gitignore`). Untuk pemakaian di luar demo perlu kemitraan data dengan Mafindo |

## Aset video dan materi pengumpulan
Video demo ([YouTube](https://youtu.be/s2EMpZI2r4g)) memakai rekaman nyata keluarga tim, tangkapan layar asli aplikasi yang berjalan, logo Halio (`web/icons/icon.svg`), dan huruf merek di atas. Musik dan efek suaranya disintesis oleh tim, dan tidak ada foto stok atau musik berlisensi. Satu-satunya logo pihak ketiga adalah logo Kartika Cyber Hackathon 2026 dari situs resmi lomba (`kartikacyberhackathon.id`), dipakai pada penutup video dan thumbnail untuk menandai karya ini sebagai peserta lomba. Rekaman Nenek dibuat dengan persetujuan tertulis yang disimpan di luar repo. Latar `scripts/assets/field-day.jpg` dibuat tim untuk `scripts/make_thumbnail.py`.

## Sumber riset dalam narasi
Dokumen riset internal tim tidak disertakan di repo ini. Artikel yang dikutip dalam demo (mis. Metro TV dan detikNews) disebut langsung pada materi yang memakainya.

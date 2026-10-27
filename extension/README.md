# Ekstensi Chrome Halio (lapisan feed)

Lencana **"Perlu dicek?"** pada postingan yang memakai trik manipulasi, dan blur gambar sesuai **aturan keluarga**. Semua analisis gambar berjalan di perangkat.

## Pasang (mode pengembang)
1. (Opsional, untuk mode `pintar`) `python scripts/fetch_models.py` untuk mengunduh onnxruntime-web + NudeNet 320n ke `extension/vendor` dan `extension/models` (tidak masuk git).
2. Buka `chrome://extensions`, aktifkan **Developer mode**, klik **Load unpacked**, lalu pilih folder `extension/`.
3. Jalankan server Halio (`uvicorn halio.api:app` di `backend/`), lalu buka `http://localhost:8000/demo-feed.html`.

## Mode gambar
| Mode | Perilaku |
|---|---|
| `judol` (default) | Sembunyikan gambar yang konteksnya (alt, tautan, teks sekitar) memakai kosakata judi online |
| `pintar` | `judol` + NudeNet di offscreen document; gambar diburamkan dulu (fail-closed) dan dibuka bila aman. Tanpa model, gambar tetap buram dengan keterangan "belum bisa diperiksa" |
| `semua` | Semua gambar buram; ketuk untuk melihat |
| `off` | Tidak ada blur |

## Privasi
- Teks hanya dikirim saat menekan "Cek dengan Halio", setelah dibersihkan (≤ 300 karakter).
- Gambar diambil dan dianalisis di dalam ekstensi; penghitung "Byte gambar dikirim keluar" selalu 0.
- **Jangan** menguji atau merekam demo dengan gambar eksplisit (dilarang Rulebook). Gunakan banner judi di feed simulasi.

## Status
- Situs: Facebook, Instagram, X, TikTok, YouTube, localhost. Selektor generik (`[role=article]`, `article`); DOM platform bisa berubah.
- Belum diuji: performa NudeNet di laptop kelas bawah, OCR banner judol (peta jalan).

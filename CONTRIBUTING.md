# Berkontribusi ke Halio

## Menjalankan tes dan evaluasi

```bash
cd backend
pip install -r requirements.txt pytest==9.2.0
python -m pytest                    # semua tes unit dan API
cd ..
python eval/run_eval.py             # evaluasi offline -> eval/RESULTS.md
git diff --exit-code -- eval/RESULTS.md   # CI gagal bila hasil berubah
```

CI (`.github/workflows/ci.yml`) juga menjalankan `compileall`, `node --check` untuk `web/*.js` dan `extension/*.js`, dan `docker build`.

## Aturan

1. **Setiap entri korpus wajib bersumber.** Entri `data/debunks.json` harus menaut ke pemeriksa fakta atau lembaga resmi yang **secara eksplisit** membantah klaim itu. Tulis ringkasan dengan kata sendiri; jangan menyalin teks artikel.
2. **Jangan mengubah ambang** (`HALIO_MATCH_THRESHOLD`, `HALIO_UNSURE_THRESHOLD`, penjaga inti klaim) tanpa menjalankan `eval/run_eval.py`. Ukuran utamanya adalah **tuduhan palsu** (pernyataan benar yang dicap "terbukti salah"). Angka itu harus tetap 0 pada set dev dan holdout. Bila `eval/RESULTS.md` berubah, jelaskan alasannya di PR.
3. **Model tidak memutuskan vonis.** Model hanya boleh mencari, mengusulkan, dan menilai relasi per nomor bukti. Kutipan disalin oleh kode, dan status diputuskan oleh kode. Perubahan yang melanggar ini tidak diterima.
4. **Jangan menambah klaim yang tidak bisa dibuktikan** di README, dokumen, atau slide (misalnya "deteksi deepfake", "semua platform", "akurasi dunia nyata").
5. **Rahasia dan data:** jangan commit `.env`, `*.db`, atau `data/arsip.jsonl`. Pakai nama dan nomor fiktif di tes, contoh, dan demo.
6. Kerjakan di cabang dan buka PR ke `main`; jangan push langsung ke `main`.

## Lisensi

Dengan berkontribusi, Anda setuju kontribusi Anda dirilis dengan [Lisensi Apache 2.0](LICENSE).

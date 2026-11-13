# Mode luring: Halio tanpa jaringan

> **Jenis:** Rujukan · **Untuk:** juri, pengelola, dan satuan dengan jaringan terbatas · [Peta dokumen](README.md)

Halio sudah dirancang agar jalur pencocokan (T1) tidak butuh AI. Dokumen ini menjelaskan tiga bentuk luring yang tersedia, bukti yang menopangnya, dan batasnya. Semua angka berasal dari pengukuran 13 Nov 2026 pada laptop pengembang (Windows); bagian yang belum diuji ditulis apa adanya.

## Tiga bentuk luring

| Bentuk | Apa yang berjalan tanpa internet | Status |
|---|---|---|
| **Server on-premise (T1)** | API, web, kartu, Radar di satu mesin; `HALIO_LLM=0`, `HALIO_MEDIA=0`, `HALIO_LINK_CHECK=0`, `HALIO_SENSOR=0`. Profil: [`.env.offline.example`](../.env.offline.example) dan [`docker-compose.offline.yml`](../docker-compose.offline.yml) | Dibuktikan dengan tes yang memblokir semua akses jaringan dan dengan server uvicorn sungguhan memakai profil itu. **Compose belum diuji**: Docker tidak terpasang di mesin pengembang |
| **Mesin di perangkat (browser/PWA)** | Pencocokan klaim, deteksi trik manipulasi, penjaga salah-tuduh, kartu, dan suara bawaan perangkat, semuanya di browser. Kode: [`web/engine/`](../web/engine/) | Dibuktikan dengan uji paritas terhadap Python dan uji Chrome dengan jaringan diputus |
| **Paket folder (flashdisk)** | `python scripts/make_luring_package.py` membuat `dist/Halio-Luring.zip` (sekitar 640 KB): folder `web/`, peluncur Windows/macOS/Linux, `PANDUAN.txt`, `VERSI.txt`. Dibuka langsung dari berkas (`file://`), tanpa instalasi dan tanpa server | Diuji (`--selftest`): hasil ekstraksi dibuka dari `file://` di Chrome dengan jaringan diputus, tiga pesan dijawab benar. Belum diuji di mesin Windows lain atau Firefox/Safari |
| **Ekstensi Chrome** | Lencana trik manipulasi dan blur gambar sudah sepenuhnya di perangkat | Belum memakai mesin cek yang sama (peta jalan) |

Telegram **tidak** bisa luring: bot memakai long-polling ke server Telegram. Di jaringan tertutup, pakai antarmuka web di server lokal.

## Cara kerja mesin di perangkat

1. **Satu sumber kebenaran.** `scripts/build_engine_data.py` mengekspor korpus, kosakata, daftar kata, dan pola regex dari modul Python ke `web/engine/data.js`. Tes gagal bila file itu basi (pola yang sama dengan `sync_lexicon.py`).
2. **Logika ditulis ulang, bukan disalin.** `web/engine/halio-local.js` memuat normalisasi teks, TF-IDF kata dan trigram huruf, penjaga negasi dan koreksi, ekstraksi klaim, pemecahan pesan berisi beberapa klaim, trik manipulasi, tangga vonis, dan naskah suara. Tanpa dependensi baru.
3. **Dijaga identik.** `scripts/gen_parity_vectors.py` menjalankan `pipeline.check` Python pada 603 teks (set uji, kasus tepi, variasi acak bersemai tetap), lalu `web/engine/parity.test.mjs` memastikan JS memberi status, alasan, bantahan terpilih, skor, trik, klaim, dan naskah suara yang sama. Satu perbedaan pun membuat CI gagal.
4. **Dipakai hanya bila perlu.** Saat server tersedia, web memakai server seperti biasa. Mesin lokal masuk bila browser offline atau permintaan gagal karena jaringan (bukan karena jawaban error server). Di GitHub Pages (tanpa server), mesin ini menggantikan 4 skenario tulis-tangan lama.
5. **Hasil luring diberi label.** Banner "Mode luring" menyebut jumlah bantahan yang dipakai, bahwa tidak ada AI, web, atau server, dan bahwa kabar di luar daftar tidak dikenali. Tombol banding dan pemeriksa manusia tidak tampil karena butuh server.

## Bukti

| Bukti | Hasil | Cara mengulang |
|---|---|---|
| Jalur T1 tidak menyentuh jaringan | Tes memblokir `socket`, DNS, dan `httpx`; set dev dan holdout berjalan penuh, false-hoax 0. Tes yang sama gagal bila link check dinyalakan (diverifikasi) | `cd backend && python -m pytest tests/test_offline.py` |
| Server sungguhan dengan profil luring | `/health` melapor `llm:false`, `media:false`; `/api/check` menjawab `terbukti_salah` dengan metode `lokal` | lihat `docs/LURING.md` bagian Menjalankan |
| Paritas JS dan Python | 603 vektor, 0 perbedaan | `node web/engine/parity.test.mjs` |
| Paritas pada teks dunia nyata | 3.900 judul TurnBackHoax (sampel tersebar, satu kali jalan 13 Nov dengan korpus 10 entri, data tidak disimpan di repo): 0 perbedaan. Uji ini menemukan satu kelemahan (pemotongan teks ber-emoji) yang sudah diperbaiki dan dikunci di vektor | skrip sementara, tidak di repo |
| Uji paritas sanggup mendeteksi kesalahan | Tiga kerusakan kecil sengaja disisipkan (ambang, urutan pengurutan, kamus slang): ketiganya tertangkap (128, 12, dan 140 perbedaan) | ubah satu baris di `halio-local.js` lalu jalankan uji |
| Browser sungguhan tanpa jaringan | Chrome (viewport HP 390x844): beranda dan halaman cek dimuat, service worker aktif, jaringan diputus, reload, tiga pesan dijawab di perangkat dengan vonis sama seperti server | `python scripts/e2e_offline.py` (butuh `pip install playwright`) |
| Tuduhan palsu pada data independen, korpus 10 entri | 0 dari 197 judul TurnBackHoax berlabel BENAR/KLARIFIKASI (sampel 3.700 judul, commit beku `69d1020`, batas atas 95%: 1,9%) | `python eval/eval_public_recheck.py` (laporan: [PUBLIC_RECHECK.md](../eval/PUBLIC_RECHECK.md)) |
| Kecepatan | Median 0,52 ms, p95 0,56 ms per cek (300 pemanggilan, korpus 10 entri, Windows) | lihat `tests/test_offline.py` (batas longgar 50 ms) |

## Yang tidak bisa (dan tidak diklaim)

- **Kabar di luar korpus tidak dikenali.** Korpus kini 10 bantahan. Hasilnya "belum ada pemeriksaan", bukan tebakan. Nilai luring sepenuhnya ditentukan oleh isi dan kesegaran korpus.
- Tanpa tautan: cek tautan, bukti web, Telusur, brief, Gemini, baca foto dan suara, dan jenis `berita_media` butuh jaringan atau server.
- Korpus di perangkat adalah salinan saat build. Belum ada sinkronisasi korpus bertanda tangan; memperbarui berarti men-deploy ulang `web/`.
- Browser lama tanpa dukungan regex lookbehind (mis. Safari sebelum 16.4) tidak memuat mesin; halaman memakai jalur lama.
- Perilaku kasus sulit identik dengan mode tanpa AI di server, termasuk kelemahannya (mis. parafrase berat rekrutmen TNI AD masih "tidak yakin", lihat [BUKTI_UJI_SETELAH_PERBAIKAN.md](BUKTI_UJI_SETELAH_PERBAIKAN.md)).
- Belum diuji: HP fisik, Safari/iOS, penggunaan memori di HP kelas bawah, Docker/compose, mesin tanpa Node (tes paritas dilewati otomatis).

## Menjalankan

```bash
# server luring lokal (tanpa AI, tanpa internet keluar)
cd backend
HALIO_LLM=0 HALIO_MEDIA=0 HALIO_LINK_CHECK=0 HALIO_SENSOR=0 uvicorn halio.api:app   # lalu buka /cek.html

# setelah mengubah data/debunks.json atau aturan python:
python scripts/build_engine_data.py        # data mesin JS
python scripts/gen_parity_vectors.py       # vektor paritas
python eval/run_eval.py                    # wajib: false-hoax tetap 0
node web/engine/parity.test.mjs            # wajib: 0 perbedaan
```

## Peta jalan

Sinkronisasi korpus berversi dan bertanda tangan; ekstensi Chrome memakai mesin yang sama; uji di HP fisik dan iOS; uji compose dengan egress diblokir; perluasan korpus bersama pemeriksa fakta (lihat [VERIFIKASI_KORPUS.md](VERIFIKASI_KORPUS.md)).

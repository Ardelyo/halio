# Video demo Halio

Video produk untuk pengumpulan Kartika Cyber Hackathon 2026 (Rulebook §G.4: maks. 10 menit, unggah ke YouTube).
Semua yang tampil dibuat dari kode di folder ini; tangkapan layar aplikasi diambil dari aplikasi yang benar-benar berjalan.

## Hasil (`video/out/`)
| File | Isi | Untuk |
|---|---|---|
| `halio-demo.mp4` | Subtitle tertanam + musik latar | Diunggah ke YouTube setelah suara narasi ditambahkan |
| `halio-demo-tanpa-musik.mp4` | Subtitle tertanam, tanpa audio | Diputar saat merekam narasi |
| `halio-demo-tanpa-subtitle.mp4` | Musik saja | Diunggah bersama `halio-demo.srt` sebagai teks YouTube |
| `halio-demo.srt` | Subtitle | Unggah ke YouTube (Subtitle → Unggah file) |
| `../NASKAH.md` | Narasi + kode waktu | Dibaca saat merekam |

## Merekam narasi
1. Putar `halio-demo-tanpa-musik.mp4`, baca setiap baris saat subtitlenya muncul (`NASKAH.md` memuat waktunya).
2. Gabungkan rekaman suara dengan video bermusik, musik otomatis direndahkan saat ada suara:
   ```bash
   ffmpeg -i video/out/halio-demo.mp4 -i narasi.wav -filter_complex \
     "[1:a]volume=1.0[v];[0:a][v]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[m];[m][v]amix=inputs=2:duration=first[a]" \
     -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k video/out/halio-demo-final.mp4
   ```

## Render ulang
```bash
python video/tools/make_fields.py        # latar padang rumput (sekali saja)
python video/tools/render_all.py         # timeline -> frame -> mp4 (sekitar 5 menit dengan 4 core)
```
- Ubah narasi di `tools/build_timeline.py`; waktu animasi dan subtitle ikut menyesuaikan.
- Ubah isi "Status jujur prototipe" di `src/scenes.js` (`STATUS`) setiap kali status berubah.
- Tangkapan layar aplikasi ada di `assets/shots/`; ambil ulang setelah aplikasi berubah.
- Pratinjau satu frame: `node tools/render.js stills /tmp/stills 12.5,80`.

## Merek
Lihat `BRAND.md`. Font (SIL OFL) ada di `fonts/`, latar padang dibuat prosedural (`tools/make_fields.py`),
musik disintesis sendiri (`tools/make_music.py`). Tidak ada foto, musik, atau logo pihak ketiga.

## Story Instagram 9:16 "Segera hadir" (25 detik)
```bash
python video/tools/render_story.py --music path/ke/backsound.mp3   # sekitar 4 menit
```
- Sumber animasi: `story/` (1080×1920). Potongan mengikuti ketukan lagu: 1 ketukan = 0,4 dtk, hentakan bar di 0,41 + 1,6k dtk; reveal logo di 22,81 dtk.
- Efek suara disintesis di `tools/story_sfx.py` dengan waktu yang sama dengan potongan di `story/story.js`.
- Dirender 60 fps lalu digabung ke 30 fps (motion blur). Audio dinormalkan ke −14 LUFS.
- Hasil: `out/halio-story-segera-hadir.mp4` (musik + efek) dan `out/halio-story-segera-hadir-sfx.mp4` (efek saja).
- Lagu latar tidak disimpan di repo karena hak ciptanya milik pihak lain.

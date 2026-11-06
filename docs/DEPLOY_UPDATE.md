# Memperbarui Telegram, situs, dan lainnya (checklist)

Sumber kebenaran: `deploy/deploy_gce.sh` mengemas folder **yang ada di laptop Anda saat itu** (bukan dari GitHub). Jadi langkah pertama selalu memastikan
checkout lokal berisi kode yang diinginkan.

## A. Dapatkan kode yang benar di laptop
Pilih satu:
- **Cepat (uji dulu):** `git fetch && git checkout ccr-9a966766-0ke2xe && git pull` (isi PR #7).
- **Rapi:** gabungkan PR #7 ke `feat/media-links-gce`, lalu buat PR `feat/media-links-gce` → `main`, gabungkan, dan `git checkout main && git pull`.
Cek: `git log --oneline -1` harus menunjukkan commit terbaru, dan `git status` bersih.

## B. Periksa `.env` di akar repo (nilai rahasia tetap di laptop, jangan di-commit)
| Variabel | Nilai |
|---|---|
| `TELEGRAM_BOT_TOKEN` | token dari @BotFather |
| `HALIO_CHANNEL_KEY` | teks acak panjang (sama untuk API dan bot; satu `.env`) |
| `RADAR_TOKEN` | teks acak (tanpa ini Radar dan antrean tertutup dari luar) |
| `HALIO_LLM` | `1` |
| `HALIO_ENGINE` | `v2` (bawaan; `v1` untuk mundur ke agen lama) |
| `HALIO_MEDIA` | `1` (baca foto/suara) |
| `HALIO_LLM_MODEL` / `HALIO_MEDIA_MODEL` | `gemini-3.5-flash-lite` |
| `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` | `gemma4good-494311` / `global` |
| `HALIO_SENSOR` | `1` (arsip pemeriksa fakta untuk kandidat bukti, dan panel Cakupan) |

Pastikan di proyek GCP: **Vertex AI API aktif**, dan akun layanan VM punya peran `Vertex AI User` (VM dibuat dengan `--scopes cloud-platform`).

## C. Deploy ke server (dari akar repo, sudah `gcloud auth login`)
```bash
HOST=<hostname-publik-anda> PROJECT=gemma4good-494311 ZONE=asia-southeast2-a bash deploy/deploy_gce.sh
```
Skrip mengirim `backend data web deploy scripts eval`, memasang paket, menulis ulang unit `systemd`, dan memulai ulang `halio-api` dan `halio-bot`.
Akhir keluarannya harus `active` `active` lalu JSON dari `/health` (`"llm":true`).

## D. Pastikan yang berjalan memang versi baru
1. Di Telegram kirim `/versi`: angka hash dalam kurung harus sama dengan `git rev-parse --short HEAD` di laptop.
2. `curl https://<HOST>/health` → `"version":"0.2.0"` dan `"build":"<hash>-<tanggal>"`.
3. Bila berbeda: ulangi C, atau di VM `sudo systemctl restart halio-api halio-bot` lalu `journalctl -u halio-bot -n 50`.

## E. Uji sebelum dipercaya (di Telegram)
1. Tempel artikel detik yang tadi → harus **📰 BERITA DARI MEDIA DIKENAL**, tanpa "jangan diteruskan", tanpa kartu/suara.
2. Foto berisi beberapa judul → **🗂 BEBERAPA JUDUL SEKALIGUS**.
3. Pesan hadiah/bansos → 🔴 atau ⚪ dengan penjelasan; tombol "Tanya pemeriksa manusia" membalas dengan nomor tiket.
4. Pesan berisi tiga klaim (contoh di `docs/RUNBOOK_DEMO.md`) → **🧩 PESAN BERISI BEBERAPA KLAIM**, jawaban per klaim.
5. Kabar yang dimuat beberapa media (mis. berita besar hari ini) → 🔵 **Dilaporkan media** atau ⚪ "baru satu media", dengan kutipan, penerbit, tanggal.
6. Tekan tombol pada pesan lama setelah restart → tetap bekerja (membaca ulang pesan yang dibalas).

Lalu, di VM, ukur dengan data nyata (membutuhkan ADC VM, sehingga dijalankan di sana):
```bash
gcloud compute ssh halio --zone asia-southeast2-a --command \
 "sudo -u halio bash -c 'set -a; . /opt/halio/.env.systemd; set +a; cd /opt/halio && .venv/bin/python scripts/eval_live.py --news 10 --hoax 10'"
```
Hasilnya di `/opt/halio/eval/LIVE_RESULTS.md`; **berita benar dituduh salah harus 0**. Kirim isinya ke saya bila ada yang janggal.

## F. Situs (GitHub Pages)
- Pages hanya berisi **demo simulasi** dan **diperbarui otomatis** oleh workflow `pages.yml` ketika `main` berubah di `web/**`. Jadi situs publik baru berubah **setelah PR digabung ke `main`**.
- Bila tidak mau menunggu: Actions → "Deploy GitHub Pages" → *Run workflow* (dari `main`).
- Versi sungguhan (bukti web, kartu, suara, Radar) ada di server: `https://<HOST>/cek.html`, `/radar`, `/coverage`. Radar dari luar butuh `Authorization: Bearer <RADAR_TOKEN>`; halaman Radar memintanya.
- Cache: cache layanan (`halio-shell-v5`) sudah dinaikkan; bila halaman lama masih tampil, muat ulang paksa (Ctrl+Shift+R) atau hapus data situs.

## G. Yang lain
| Hal | Tindakan |
|---|---|
| Ekstensi Chrome | `chrome://extensions` → muat ulang ekstensi (popup memakai font merek; kamus teks dibangkitkan dari Python: `python scripts/sync_lexicon.py` bila `manipulation.py` berubah) |
| Menu bot | @BotFather → `/setcommands`: `start`, `bantuan`, `sapaan`, `privasi`, `versi` (uraian: sebut "Halio memberi bukti, bukan vonis") |
| Video demo dan story | Masih menampilkan empat keadaan; belum menampilkan 🔵 Dilaporkan media dan pesan berisi beberapa klaim. Render ulang hanya bila diperlukan (`python video/tools/render_all.py`) |
| Dokumen juri | `docs/PLAN_VERIFIKASI_AI.md` (status 2b), `eval/LIVE_RESULTS.md` setelah dijalankan |

## H. Mundur bila ada masalah
```bash
# mesin lama saja (tanpa mengganti kode)
gcloud compute ssh halio --zone asia-southeast2-a --command "echo HALIO_ENGINE=v1 | sudo tee -a /opt/halio/.env.systemd && sudo systemctl restart halio-api halio-bot"
# atau deploy ulang dari commit sebelumnya: git checkout <commit> && bash deploy/deploy_gce.sh
```
Bila pencarian atau penilaian v2 gagal sendiri, sistem otomatis memakai agen lama (`mesin cadangan` di panel Radar).

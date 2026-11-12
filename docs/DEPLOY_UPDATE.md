# Memperbarui Telegram, situs, dan lainnya (checklist)

> **Jenis:** Panduan · **Untuk:** pengelola server · [Peta dokumen](README.md)

Sumber kebenaran: `deploy/deploy_gce.sh` mengemas folder **yang ada di laptop Anda saat itu** (bukan dari GitHub). Jadi langkah pertama selalu memastikan
checkout lokal berisi kode yang diinginkan.

## A. Dapatkan kode yang benar di laptop
Deploy dari `main` setelah PR digabung: `git fetch && git checkout main && git pull`.
Untuk menguji cabang PR yang belum digabung: `git checkout <nama-cabang> && git pull`, lalu kembali ke `main` setelah selesai.
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
| `HALIO_AGENT_DAILY_CAP` | `200` selama penjurian 16–24 Nov (bawaan 60), agar juri tidak ditolak |
| `HALIO_LLM_DAILY_CAP` / `HALIO_MEDIA_DAILY_CAP` | pagar biaya, mis. `1500` / `300`; `0` = tanpa batas. Lewat batas: cek tetap jalan dari korpus (berlabel "mode tanpa AI"), foto/suara dijawab 429 |
| `HALIO_RETENTION_DAYS` | `30` (retensi data, lihat `docs/PRIVACY.md`) |
| `HALIO_MAX_BODY_MB` | `16`; samakan dengan `request_body max_size` di Caddy (`deploy/Caddyfile.example`) |

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
- Cache: cache layanan (`halio-shell-v14`) sudah dinaikkan; bila halaman lama masih tampil, muat ulang paksa (Ctrl+Shift+R) atau hapus data situs.

## G. Yang lain
| Hal | Tindakan |
|---|---|
| Ekstensi Chrome | `chrome://extensions` → muat ulang ekstensi (popup memakai font merek; kamus teks dibangkitkan dari Python: `python scripts/sync_lexicon.py` bila `manipulation.py` berubah) |
| Menu bot | @BotFather → `/setcommands`: `start`, `bantuan`, `sapaan`, `privasi`, `versi` (uraian: sebut "Halio memberi bukti, bukan vonis") |
| Video demo | Video di YouTube sudah terbit dan tidak dibangun dari kode repo ini. Bila tampilan aplikasi berubah, rekam ulang bagian yang berubah; tampilan keadaan jawaban mengikuti `backend/halio/card.py` |
| Dokumen juri | `docs/ARCHITECTURE_AGENT.md`, `eval/LIVE_RESULTS.md` setelah dijalankan |

## H2. Lapis jaringan: batasi lalu lintas keluar proses Halio (SSRF)

**Celah (sudah ditutup di kode).** `link_check.py` dan `source_verifier.py` dulu memeriksa bahwa nama situs mengarah ke IP publik, lalu `httpx` me-resolve nama itu **lagi** saat terhubung, sehingga DNS rebinding bisa mengarahkan koneksi ke alamat internal. Sekarang keduanya memakai `PinnedTransport` (`backend/halio/safefetch.py`): nama di-resolve sekali, permintaan ditolak bila **salah satu** jawaban bukan alamat global, lalu koneksi dibuat ke IP itu juga, dengan Host dan SNI tetap nama aslinya (sertifikat tetap diverifikasi terhadap nama itu; diuji dengan mengarahkan `www.bmkg.go.id` ke IP lain: ditolak "Hostname mismatch"). 9 tes baru, dan halaman nyata BMKG, Liputan6, Kompas TV, dan Investortrust tetap terbaca.

Firewall di bawah tetap dianjurkan sebagai lapis kedua (pertahanan berlapis), bukan lagi satu-satunya penutup.

**Mitigasi yang dianjurkan (dijalankan pemilik di VM):** tolak lalu lintas keluar pengguna `halio` ke rentang privat. Loopback (bot → API) dan server metadata (token ADC untuk Vertex AI dan Cloud TTS) **tetap dibuka**, karena keduanya dibutuhkan.

```bash
gcloud compute ssh halio --zone asia-southeast2-a --command 'sudo bash -c "
for net in 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16 100.64.0.0/10 169.254.0.0/16; do
  [ \$net = 169.254.0.0/16 ] && iptables -A OUTPUT -m owner --uid-owner halio -d 169.254.169.254 -j ACCEPT
  iptables -A OUTPUT -m owner --uid-owner halio -d \$net -j REJECT
done
iptables -L OUTPUT -n --line-numbers"'
```

Aturan `iptables` di atas hilang saat VM di-reboot. Untuk permanen, pasang `iptables-persistent` (`sudo apt-get install -y iptables-persistent && sudo netfilter-persistent save`). Setelah dipasang, uji: `/health` tetap `"llm":true`, satu cek dengan bukti web berhasil, dan `/versi` di Telegram menjawab.

## H. Mundur bila ada masalah
```bash
# mesin lama saja (tanpa mengganti kode)
gcloud compute ssh halio --zone asia-southeast2-a --command "echo HALIO_ENGINE=v1 | sudo tee -a /opt/halio/.env.systemd && sudo systemctl restart halio-api halio-bot"
# atau deploy ulang dari commit sebelumnya: git checkout <commit> && bash deploy/deploy_gce.sh
```
Bila pencarian atau penilaian v2 gagal sendiri, sistem otomatis memakai agen lama (`mesin cadangan` di panel Radar).

## Domain dan HTTPS
- Alamat utama: `https://halio.ardelyo.com` (record A `halio` di DNS Hostinger menuju IP statis `halio-ip` = `34.101.109.211`, TTL 300).
- Caddy di VM melayani dua nama dalam satu blok: `halio.ardelyo.com` dan `34-101-109-211.sslip.io` (cadangan, mengikuti IP). Sertifikat Let's Encrypt diterbitkan dan diperbarui otomatis; porta 80 dan 443 harus tetap terbuka.
- Contoh konfigurasi: `deploy/Caddyfile.example`. Setelah mengubah `/etc/caddy/Caddyfile`: `sudo caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` lalu `sudo systemctl reload caddy`.
- Record `@` dan `www` milik `ardelyo.com` tidak berhubungan dengan Halio; jangan diubah dan jangan menekan "Reset DNS record" di Hostinger.
- Bot Telegram memakai polling, jadi tidak bergantung pada nama domain.

## Catatan deploy terakhir
- 12 Nov 2026: server diperbarui ke `281dc9e-20261112-1423` (perubahan perilaku: pola pelurusan di `retrieval.py`; dependensi tidak berubah). Dilakukan **tanpa** `deploy_gce.sh`: skrip itu menimpa `/opt/halio/.env.systemd` dari `.env` lokal, jadi untuk pembaruan kode saja gunakan prosedur ini.
- Prosedur aman: cadangkan `backend data web deploy scripts eval .env.systemd` ke `/opt/halio-backups`, ekstrak tarball (`git archive HEAD backend data web deploy scripts eval`) ke `/opt/halio` tanpa menghapus `halio.db` dan `data/arsip.jsonl`, perbarui `HALIO_BUILD` di `.env.systemd`, `systemctl restart halio-api halio-bot`, uji `/health` dan dua pesan contoh, dan kembalikan cadangan bila gagal.
- Cadangan sebelum deploy ini: `/opt/halio-backups/pre-281dc9e--20261112-142256.tgz` (hanya dapat dibaca root).
- Selama penjurian (16-20 Nov) tidak ada deploy.

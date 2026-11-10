# Privasi & Aturan Netral Halio

Ringkasan aturan yang ditegakkan di kode, bukan sekadar janji. Tinjauan hukum UU PDP (UU 27/2022) masih diperlukan sebelum produksi; pasal spesifik belum kami kaji.

## Yang Halio lakukan
| Aturan | Di mana ditegakkan |
|---|---|
| Hanya memeriksa pesan yang **diteruskan/diklik pengguna**. Tidak pernah memindai chat. | Kanal bot/web; ekstensi mengirim teks hanya saat tombol ditekan (`extension/content.js`) |
| Nomor telepon, NIK, email, nomor rekening, tautan, @akun dihapus; klaim dipotong ≤ 300 karakter | `backend/halio/pii.py`, `extension/lexicon.js` |
| Hasil cek disimpan di memori paling lama 1 jam (untuk kartu & suara), lalu hilang | `store.ResultCache` |
| Radar hanya menyimpan agregat (tanggal, status, kategori, trik, kanal) | `store.Store.record` |
| Isi kabar tak dikenal baru disimpan setelah ≥ k pelapor berbeda (k-anonimitas), nama samaran berganti harian | `store._count_unknown` |
| Angka agregat < 3 disamarkan | `store._suppress` |
| Ekstensi Chrome: gambar diperiksa di perangkat; 0 byte gambar dikirim | `extension/offscreen.js` |
| Foto dan rekaman suara yang **dikirim pengguna** ke bot/web dikirim utuh ke Gemini untuk dibaca (hanya bila `HALIO_MEDIA=1`), lalu tidak disimpan | `media.py`, `/api/check-media` |
| Foto yang dilampirkan ke investigasi Telusur hanya ada di memori selama investigasi; bila Cloud Vision aktif, foto itu dikirim ke Cloud Vision | `investigate/jobs.py`, `investigate/reverse_image.py` |
| Eskalasi ke manusia menyimpan klaim yang sudah dibersihkan dan tujuan balasan kanal, atas permintaan eksplisit pengguna | `/api/escalate`, `store.Store.add_escalation` |
| Kabar tak dikenal, banding, tiket selesai, dan audit reviewer dihapus setelah `HALIO_RETENTION_DAYS` hari (bawaan 30); tiket menunggu tetap disimpan | `store.Store.prune`, dipanggil harian saat ada cek |
| Investigasi Telusur yang selesai atau gagal (klaim terbersih + laporan) dihapus setelah `HALIO_RETENTION_DAYS` hari | `investigate.jobs.Jobs.prune`, dipanggil harian saat ada investigasi baru |
| Pelapor investigasi disimpan sebagai nama samaran dengan garam harian, cukup untuk menghitung batas per hari; tidak bisa ditautkan lagi setelah garam berganti | `investigate.jobs.Jobs._pseudonym`, `store.daily_salt` |
| Tiket eskalasi menyimpan tujuan balasan **mentah** (mis. `tg:<chat>`) karena dibutuhkan untuk mengirim jawaban; dihapus setelah tiket selesai dan masa retensi lewat | `store.Store.add_escalation`, `store.Store.prune` |
| Nama samaran harian dibatasi maksimal k per hash; reporter web adalah ID perangkat yang dapat dihapus pengguna, bukan identitas terverifikasi | `store._count_unknown`, `web/app.js` |
| Webhook WhatsApp wajib lolos HMAC app secret dan pesan ber-ID dideduplikasi selama 24 jam | `security.valid_meta_signature`, `/webhook/whatsapp` |

Data yang keluar ke layanan cloud pada profil T2 dirinci di [PROFIL_PENERAPAN.md](PROFIL_PENERAPAN.md).

## Aturan netral topik
1. Halio hanya memeriksa **klaim faktual** yang dapat diverifikasi, bukan opini atau pandangan politik.
2. Halio **tidak membuat vonis sendiri**. Setiap "terbukti salah" menaut ke pemeriksa fakta atau sumber resmi bernama.
3. "Tidak yakin" dan "belum ada pemeriksaan" adalah hasil kelas satu, bukan kegagalan.
4. Tombol banding selalu tersedia untuk vonis "terbukti salah".
5. Lapisan trik manipulasi menamai **teknik** (desakan, iming-iming, otoritas palsu), bukan topik atau kelompok.
6. Filter gambar adalah **aturan keluarga** yang dipilih pengguna, lokal, dan dapat dibuka dengan satu ketukan. Bahasa yang dipakai adalah "aturan keluarga kita", bukan label agama.
7. Radar adalah alat pemantauan **tren** untuk pemeriksa fakta dan satuan siber, bukan alat penindakan individu. Radar tidak memiliki data yang memungkinkan hal itu.

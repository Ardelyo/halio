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
| Gambar diperiksa di perangkat; 0 byte gambar dikirim | `extension/offscreen.js` |
| Eskalasi ke manusia menyimpan klaim yang sudah dibersihkan, atas permintaan eksplisit pengguna | `/api/escalate` |

## Aturan netral topik
1. Halio hanya memeriksa **klaim faktual** yang dapat diverifikasi, bukan opini atau pandangan politik.
2. Halio **tidak membuat vonis sendiri**. Setiap "terbukti salah" menaut ke pemeriksa fakta atau sumber resmi bernama.
3. "Tidak yakin" dan "belum ada pemeriksaan" adalah hasil kelas satu, bukan kegagalan.
4. Tombol banding selalu tersedia untuk vonis "terbukti salah".
5. Lapisan trik manipulasi menamai **teknik** (desakan, iming-iming, otoritas palsu), bukan topik atau kelompok.
6. Filter gambar adalah **aturan keluarga** yang dipilih pengguna, lokal, dan dapat dibuka dengan satu ketukan. Bahasa yang dipakai adalah "aturan keluarga kita", bukan label agama.
7. Radar adalah alat pemantauan **tren** untuk pemeriksa fakta dan satuan siber, bukan alat penindakan individu. Radar tidak memiliki data yang memungkinkan hal itu.

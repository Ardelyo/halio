# Rencana Radar: agar benar-benar berfungsi, punya wow factor, dan teruji

Disusun 4 Nov 2026 setelah menjalankan Radar sungguhan dan mengujinya dengan kasus tepi (bukan hanya membaca kode).
Pelengkap `PLAN_UNGGUL.md` (rencana umum) dan `ANALISIS_RADAR_DAN_TNI.md` (audit awal dan alternatif TNI AD).

## 0. Ringkasan

Radar hari ini **benar secara teknis tetapi belum berguna secara fungsional**: ia menghitung kabar yang kata-katanya *persis sama*,
tidak bisa mengukur kecepatan, tidak terhubung ke Sensor, dan tidak menghasilkan tindakan. Itu penyebab ia terasa seperti dasbor biasa.
Perbaikan bukan menambah grafik, melainkan tiga hal: **(1) mengenali kabar yang sama walau ditulis berbeda, (2) mengukur kecepatan,
(3) mengubah sinyal menjadi tindakan yang bisa diukur (klarifikasi bersumber dalam menit).**

---

## 1. Hasil pencarian bug (dibuktikan dengan uji, 4 Nov)

| # | Bug / cacat | Bukti | Tingkat | Perbaikan |
|---|---|---|---|---|
| R1 | **Radar dan antrean tiket terbuka bila diakses lewat proxy di mesin yang sama** (nginx, Cloudflare Tunnel) tanpa `RADAR_TOKEN` | Permintaan dari `127.0.0.1` dengan `X-Forwarded-For`/`CF-Connecting-IP` mengembalikan 200 pada `/api/radar` dan `/api/review/escalations` | **Kritis** (akses admin, termasuk menyuruh bot mengirim pesan) | **Sudah diperbaiki** hari ini: loopback dipercaya hanya bila tidak ada header proxy dan `HALIO_TRUST_PROXY` mati; ada tes regresi (96 tes lulus) |
| R2 | **Kabar yang diparafrase tidak pernah dikenali sebagai sama** | 6 pelapor, 6 redaksi dari satu rumor → 3 hash berbeda, 0 kabar muncul | **Tinggi** (fungsi inti "kabar baru" hanya bekerja untuk teks salin-tempel identik) | Pengelompokan mirip-duplikat (bagian 3.1) |
| R3 | **Hitungan pelapor mentok di k (=5)** | 3 hari × 50 pelapor → count 15; satu hari → 5 | **Tinggi** (tidak ada ukuran kecepatan) | Penghitung tanpa batas dengan privasi (HyperLogLog), kecepatan per jam (3.2) |
| R4 | Data simulasi tampil seperti data nyata pada mode API | 313 kejadian `demo` tanpa banner; `seed_demo.py` menjanjikan banner | Sedang (kejujuran) | Banner dari `demo_events`; pisahkan data demo (3.7) |
| R5 | `events` tidak pernah dihapus | Baris tahun 2025 bertahan setelah `prune()`; dokumen menyebut retensi 30 hari | Sedang | Tambahkan ke `prune`, uji |
| R6 | ID chat Telegram mentah terlihat oleh analis | `/api/review/escalations` mengembalikan `tg:987654321` | Sedang (data pribadi, UU PDP) | Kembalikan ID buram; hanya server yang memegang ID asli; hapus saat tiket selesai; TTL tiket menunggu |
| R7 | Pelapor web dihitung per jaringan /24 | CGNAT seluler Indonesia → banyak orang terhitung satu | Sedang (kabar dari web jarang melewati k) | Pelapor web memakai kombinasi jaringan + penanda perangkat berpelindung (bagian 3.5); atau tidak dihitung sebagai bukti k |
| R8 | SQLite tanpa WAL padahal Sensor dan API menulis bersamaan | `journal_mode=delete` | Sedang (kunci basis data saat beban) | `PRAGMA journal_mode=WAL`, indeks pada `events(day)`, `unknown_claims(last_seen)` |
| R9 | Penyamaran sel kecil tidak konsisten | Hanya `by_kategori` dan `top_debunks` yang disamarkan; `by_status`, `daily`, `techniques` tidak, padahal UI menjanjikannya | Rendah-sedang (privasi) | Terapkan aturan yang sama; atau perbaiki teks UI. Catat: selisih jendela waktu tetap bisa menyingkap satu entri |
| R10 | Metadata dinamis mengotori kategori | Entri agen web berkategori `penelusuran_web`, id `gemini-<hash>` | Sedang saat korpus tumbuh | Petakan ke kategori baku; kelompokkan per klaim |
| R11 | `k=1` tidak membuka teks setelah laporan pertama | Uji: `text` tetap NULL | Rendah (kasus tepi konfigurasi) | Buka saat `len(reporters) >= k` juga pada pelapor pertama |
| R12 | "Pesan diperiksa" menghitung sapaan dan opini | Status `tidak_yakin/bukan_klaim_faktual` ikut `total_checks` | Rendah | Hitung terpisah |
| R13 | Satu token untuk semua analis, tanpa jejak per orang | Sudah dicatat di `LAUNCH_READINESS` | Tinggi untuk institusi | Token per analis + log audit + peran (3.6) |
| R14 | XSS pada tampilan | `esc()` dipakai konsisten (diperiksa) | — **aman** | Pertahankan; tambahkan tes |

Hal yang diperiksa dan **baik**: balasan gagal tidak menutup tiket; Sybil dari satu jaringan tidak memunculkan kabar; semua alur API/UI berjalan tanpa galat JavaScript.

---

## 2. Cara membuat Radar "benar-benar berfungsi"

### 2.1 Masalah data (kenyataan yang harus diterima)
Radar yang hanya memakai laporan keluarga akan sepi: puluhan pengguna tidak menghasilkan "tren". Maka Radar harus punya **dua jalur sinyal**:

| Jalur | Isi | Privasi | Volume |
|---|---|---|---|
| **A. Laporan keluarga** | pesan yang dicek lewat web/Telegram | k-anonim, tanpa teks sebelum ambang | kecil (pilot 10–20 orang) |
| **B. Pantauan publik** | 23 feed sensor: berita, cek fakta, sumber resmi | publik, tanpa ambang k | besar, hampir waktu nyata |

Nilai Radar muncul di **persilangan keduanya**: "kabar yang warga laporkan" × "apa yang media dan pemeriksa fakta sudah katakan".
Tanpa Jalur B, demo Radar akan terlihat kosong; tanpa Jalur A, ia hanya pembaca berita.

### 2.2 Syarat agar tidak sepi saat demo dan pilot
- Bot Telegram **harus hidup** (sekarang mati; lihat `PLAN_UNGGUL` bagian 4.1). Tanpa itu tidak ada laporan nyata.
- Jalur B dihidupkan (`HALIO_SENSOR=1`) pada satu instance dengan penyimpanan tetap.
- Bedakan tegas **data nyata** dan **data simulasi** (R4). Mode peragaan memakai label dan kanal `demo`, tidak bercampur dengan angka nyata.

---

## 3. Rancangan teknis

### 3.1 Pengelompokan kabar (menyelesaikan R2)
Tujuan: kabar yang sama diparafrase tetap satu kelompok, **tanpa menyimpan teks sebelum ambang k**.

- Tanda tangan **MinHash** (64 hash, gabungan shingle kata bigram + trigram karakter) dihitung dari klaim yang sudah dibersihkan PII. Disimpan hanya tanda tangan (bilangan), bukan teks.
- Kelompok baru bila Jaccard-estimasi terhadap semua kelompok aktif (7 hari) < 0,55; selain itu bergabung ke yang terdekat. Indeks LSH (band) agar cepat.
- Teks perwakilan baru disimpan setelah k pelapor berbeda terkumpul (aturan sekarang dipertahankan).
- Pencocokan semantik opsional (embedding) hanya untuk pemeriksaan kualitas offline, bukan alur utama (hemat kuota dan privasi).
- **Kriteria lulus:** set uji 30 kelompok rumor × 6 redaksi (ditulis tim, diparafrase pihak lain): recall ≥ 0,8, presisi ≥ 0,95, tidak ada penggabungan dua rumor berbeda pada 20 pasangan jebakan (topik sama, klaim beda).

### 3.2 Penghitungan pelapor dan kecepatan (R3)
- Jumlah pelapor berbeda per kelompok per hari memakai **HyperLogLog** kecil (≈ 100 byte), tanpa daftar pseudonim: hitungan tak terbatas dan tidak bisa dibalik menjadi identitas. Daftar pseudonim berbatas k tetap dipakai hanya untuk membuka teks.
- **Kecepatan** = jumlah pelapor berbeda per jam (HLL per jam), dengan penyamaran sel kecil. Tampilkan "naik N× dibanding 3 jam sebelumnya" hanya bila ≥ k pelapor.
- Retensi: sinyal per jam dihapus setelah 7 hari; per hari 30 hari.

### 3.3 Prioritas deterministik (kode, bukan model)
`skor = w1·kecepatan + w2·kategori institusi (mis. pencatutan TNI) + w3·tidak ada bantahan + w4·teknik manipulasi (urgensi, ajakan sebar, otoritas palsu) + w5·belum diliput media`. Bobot tertulis dan dapat diaudit; setiap kartu prioritas menampilkan **alasan skor** (kejelasan > kepintaran).

### 3.4 Sensor × Radar: "siapa lebih dulu"
- Untuk tiap kelompok, cari kecocokan pada item sensor 7 hari (judul, tautan, jam): *sudah dibantah di cek fakta? sudah diliput media? belum ada?*
- Metrik jujur untuk pilot: **selisih waktu** antara laporan keluarga pertama dan publikasi bantahan pertama (bisa positif atau negatif). Dilaporkan apa adanya; bila Halio sering tertinggal dari pemeriksa fakta, itu temuan, bukan kegagalan yang disembunyikan.
- Panel "Cakupan" tetap menampilkan titik buta, termasuk bahwa WhatsApp privat tidak terlihat.

### 3.5 Pelapor web (R7)
Hitung pelapor web dari gabungan prefiks jaringan dan penanda perangkat yang di-hash dengan garam harian; tolak penanda yang muncul dari satu jaringan dalam jumlah tidak wajar. Tidak sempurna terhadap penyerang; sebab itu pelapor web **tidak** dijadikan satu-satunya dasar kabar prioritas tinggi. Telegram dengan ID chat tepercaya (kunci kanal) tetap sumber paling kuat.

### 3.6 Akses dan tata kelola institusi (R13, R6)
- Token per analis (ditandatangani, dapat dicabut), peran: *analis* (tulis), *pimpinan* (baca saja), *admin*.
- Log audit: siapa membuka tiket, menyetujui klarifikasi, menerbitkan. Tidak menyimpan isi pesan warga.
- Tampilan analis tidak menampilkan ID pelapor; tiket menampilkan "kanal Telegram" saja.
- Dokumen tata kelola satu halaman dipasang di Radar ("Tren, bukan pengawasan" sudah ada; tambahkan apa yang tidak dilakukan).

### 3.7 Demo vs nyata (R4)
Kolom `is_demo` (bukan hanya kanal), banner otomatis saat ada data demo, dan perintah `seed_demo.py --label` yang menulis ke basis data terpisah.

---

## 4. Wow factor dan pemikiran inovatif

Kriteria dari dokumen riset: **satu momen yang benar-benar berfungsi**, bukti nyata, fallback, keluaran konkret (bukan dasbor).

| # | Gagasan | Apa yang terlihat juri | Kelayakan | Risiko | Skor (1–5) inovasi / demo |
|---|---|---|---|---|---|
| **W1** | **Radar → Klarifikasi dalam menit.** Kabar naik → draf klarifikasi dari sumber terverifikasi → satu analis menyetujui → kartu terbit → panel menunjukkan **waktu-ke-klarifikasi** | Angka menit, bukan grafik; ada tombol Setujui yang mati bila bukti tidak ada | 3–4 hari | Draf harus dari sumber yang lolos verifikasi kode; manusia memutuskan | 4 / 5 |
| **W2** | **Siapa lebih dulu?** (Sensor × Radar) bagan selisih waktu antara laporan keluarga dan bantahan publik | Satu bagan yang jujur menunjukkan kapan Halio unggul atau tertinggal | 2 hari setelah 3.4 | Data pilot sedikit; harus diberi label | 4 / 3 |
| **W3** | **Latihan reaksi (drill) untuk satuan**: skenario hoaks bersumber dari kasus sejarah nyata, disuntikkan berlabel "LATIHAN"; analis diukur waktu-ke-klarifikasinya | Institusi militer paham latihan dan evaluasi; demo aman dan bisa diulang | 2 hari | Harus selalu berlabel agar tidak tertukar dengan nyata | 5 / 5 |
| W4 | **Peta wilayah (Kodam/Korem/Kodim)** dari nama tempat yang disebut di klaim, teragregasi | Kesadaran wilayah, sesuai struktur teritorial | 2–3 hari | Hanya akurat bila klaim menyebut tempat; tidak memakai lokasi pengguna | 3 / 4 |
| W5 | **Deteksi koordinasi laporan** (lonjakan dari sedikit jaringan dalam waktu sempit) untuk menahan banjir laporan palsu | Radar yang tahu ia bisa dimanipulasi | 1–2 hari | Positif palsu; hanya sebagai penanda, tidak memblokir | 4 / 2 |
| W6 | **Prebunking terarah**: kartu "waspada tren" ke pelanggan sukarela sebelum kabar sampai ke mereka | Mencegah, bukan hanya membantah | 2 hari | Tidak boleh menjadi spam; opt-in; baru bila bukti kuat | 4 / 3 |
| W7 | **Ringkasan harian 1 halaman** untuk pimpinan | Keluaran yang dipakai orang nyata | 1 hari | — | 2 / 3 |
| W8 | **Transparansi publik**: halaman angka agregat dan tingkat kesalahan Halio | Kepercayaan, kejujuran terlihat | 1 hari | — | 3 / 3 |

**Pilihan:** **W1 + W3 sebagai inti**, **W2 sebagai pembeda** (hanya bila ada data pilot), W5 sebagai tambahan murah. W4, W6, W7, W8 menjadi peta jalan.
Cerita satu kalimat untuk juri: *"Radar Halio tidak menunjukkan seberapa banyak hoaks; ia menunjukkan seberapa cepat satuan Anda meluruskannya, dan melatih Anda agar lebih cepat."*

### Adegan demo (60–90 detik, tanpa kecurangan)
1. Mode LATIHAN dinyalakan (label besar). Skenario: "markas Kodim ditutup, prajurit dipindah" (rumor nyata dari arsip bantahan).
2. Enam pelapor Telegram mengirim redaksi berbeda → Radar mengelompokkannya menjadi satu kabar, bukan enam (**membuktikan R2 selesai**).
3. Kabar naik dengan lencana kecepatan dan alasan skor; Sensor menunjukkan "belum ada di media".
4. Draf klarifikasi muncul dengan kutipan sumber resmi (lolos verifikasi). Seorang analis menekan **Setujui**; kartu terbit ke kanal.
5. Panel menampilkan **waktu-ke-klarifikasi: mm:dd**, dibandingkan dengan target (mis. 2 jam/20 menit).
6. **Safeguard**: skenario kedua tanpa sumber → tombol Setujui nonaktif, "belum ada bukti, tidak ada draf".
7. **Fallback**: model dimatikan → draf tetap terbentuk dari entri korpus (tanpa pencarian web).

---

## 5. Strategi pengujian: bagaimana membuktikan "berfungsi"

### 5.1 Tes otomatis
| Area | Tes | Syarat lulus |
|---|---|---|
| Pengelompokan | 30 kelompok × 6 redaksi + 20 pasangan jebakan | recall ≥ 0,8; presisi ≥ 0,95 |
| HLL | 10.000 pelapor sintetis | galat ≤ 5%; tidak ada pseudonim tersimpan |
| Privasi | Tidak ada teks sebelum k; tidak ada PII pada teks perwakilan; ID pelapor tidak keluar di API analis | 0 pelanggaran pada 1.000 kasus acak |
| Akses | Tanpa token, via proxy, header palsu, token salah/cabut | 100% ditolak (R1 sudah punya tes) |
| Retensi | Data > 30 hari terhapus di semua tabel | 0 baris tersisa |
| Alur klarifikasi | draf → setuju → terbit → ukur waktu; mati-model; tanpa sumber | Status dan tombol sesuai; waktu tercatat |
| Beban | 1.000 laporan/menit selama 5 menit, Sensor aktif | p95 < 300 ms; tanpa "database is locked" |
| UI | Playwright: tiap tab, resolve, setujui, mobile; tanpa galat konsol | Hijau |

### 5.2 Uji dengan manusia
- **Drill nyata**: dua orang di luar tim memainkan analis pada skenario yang belum pernah mereka lihat; ukur waktu dan kebingungan. Perbaiki satu hambatan terbesar sebelum menambah fitur (saran dokumen riset).
- **Pilot**: laporkan "N laporan, M kelompok, K klarifikasi" apa adanya, termasuk kegagalan.

### 5.3 Kriteria "Radar berfungsi" (gerbang rilis)
1. Paraphrase satu rumor oleh 6 pelapor → **satu** kabar (bukan 6).
2. Hitungan pelapor tumbuh melewati k dan kecepatan terukur.
3. Tidak ada akses tanpa token dari jaringan (termasuk lewat tunnel).
4. Data demo selalu berlabel.
5. Klarifikasi hanya dari sumber yang lolos verifikasi kode; manusia menyetujui.
6. Semua tes di 5.1 hijau.

---

## 6. Jadwal (menyatu dengan `PLAN_UNGGUL`)

| Tanggal | Radar | Gerbang |
|---|---|---|
| 4 Nov | R1 diperbaiki (selesai). Cacat R5, R8, R6, R11, R4: perbaikan cepat dan tes | Tes hijau |
| 5–6 Nov | MinHash/LSH pengelompokan + HLL + kecepatan; set uji parafrase | Kriteria 3.1 |
| 7 Nov | Skor prioritas + Sensor × Radar | Tampilan "kabar × media" |
| 8 Nov | Klarifikasi: draf (korpus + agen web), setujui, terbit, ukur waktu | Adegan demo 1–7 berjalan |
| 9 Nov | Mode LATIHAN + skenario dari arsip bantahan; drill dengan orang luar | Satu hambatan terbesar diperbaiki |
| 10 Nov | Token per analis + log audit; uji beban; dokumentasi | 5.3 hijau |
| 11 Nov | **Code freeze** | — |

**Ketergantungan:** bot Telegram dan API harus hidup (deploy) sebelum 6 Nov; tanpa itu hanya mode LATIHAN yang bisa didemokan, dan harus dikatakan terus terang.

---

## 7. Risiko yang diakui
- Data nyata akan kecil; angka tren bisa sepi. Mitigasi: Jalur B dan mode LATIHAN berlabel; jangan klaim tren nasional.
- Pengelompokan bisa salah (menggabungkan rumor berbeda). Mitigasi: ambang konservatif, analis dapat memisahkan, uji jebakan.
- Radar bisa dimanipulasi (banjir laporan). Mitigasi: ambang k pelapor tepercaya, penanda koordinasi (W5), keputusan akhir manusia.
- Klarifikasi otomatis berisiko salah. Mitigasi: hanya sumber yang lolos verifikasi kode, manusia menyetujui, tombol mati bila bukti tidak ada.
- Radar tidak membuktikan perubahan perilaku; tidak diklaim.
- Salah baca institusi: kebutuhan TNI AD di sini dari sumber publik. Validasi dengan satu orang dalam sebelum menyebutnya kebutuhan mereka.

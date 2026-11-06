# Rencana Mesin Bukti v2: jawaban yang informatif, AI yang bisa dipakai, sumber yang benar

Disusun 6 Nov 2026 dari tiga jawaban bot nyata (v0.2.0) yang Anda tempel: artikel detik, kumpulan judul dari foto, dan pesan hadiah.
Semua jawaban itu berakhir sama: "⚪ Belum ada pemeriksaan … jangan diteruskan dulu", dengan "AI mencari di web: N sumber, 0 lolos", tautan
"google.com" sebagai bahan bacaan, dan peringatan "bukan situs pemerintah" untuk situs berita. Anda benar: jawaban itu kosong.

## 1. Diagnosis (dibuktikan dari kode, bukan dugaan)

| # | Akar masalah | Bukti di kode | Dampak yang terlihat |
|---|---|---|---|
| D1 | **Mesin bukti hanya menerima situs resmi dan pemeriksa fakta.** | `source_verifier.verify_source` menolak domain apa pun yang `source_kind()` kosong (`domain_bukan_sumber_primer`) | Berita dari detik, Kompas, dll **tidak pernah** lolos: "0 lolos" selalu |
| D2 | **Ruang jawaban terlalu kecil.** Semua yang tidak terbukti jatuh ke "belum ada pemeriksaan, jangan diteruskan". | `pipeline.check` hanya punya 4 status; ringkasan model (`report.summary`) dibuang | Berita biasa dan kabar mencurigakan diperlakukan sama |
| D3 | **Informasi yang sudah ditemukan tidak ditampilkan** (judul, penerbit, tanggal, ringkasan halaman). | `link_check` hanya mengambil `<title>` | Pengguna tidak belajar apa pun dari jawaban |
| D4 | **Kutipan diminta dari model, lalu dicocokkan huruf demi huruf.** Sedikit beda spasi atau ejaan membuat sumber gugur. | `quote_present` mensyaratkan kecocokan persis; jalur `best_passage` baru ada untuk bantahan | Banyak sumber benar gugur tanpa alasan yang terlihat |
| D5 | **Alasan penolakan tidak terlihat** pengguna maupun tim. | `sumber_ditolak` tersimpan di catatan tetapi tidak ditampilkan | "0 lolos" tanpa penjelasan |
| D6 | **Tautan grounding Google tidak diuraikan**; judul menjadi "google.com". | `reading.build` memakai `web.title` bila halaman tak terbaca | Daftar bacaan berisi mesin pencari |
| D7 | **Satu pesan = satu klaim.** Gambar berisi banyak judul, atau artikel dengan beberapa klaim, dipaksa jadi satu. | `claims.extract` | Jawaban tidak mengarah ke apa pun |
| D8 | **Tidak ada tingkat sumber atau kemandirian.** Dua berita dari satu grup media terlihat sama dengan dua media berbeda. | Tidak ada struktur | Tidak bisa menyatakan "dilaporkan beberapa media" dengan jujur |
| D9 | **Tombol kedaluwarsa setelah bot dimulai ulang** (hasil hanya di memori). | `ResultCache` TTL 1 jam, hilang saat deploy | "Maaf, hasil cek sudah kedaluwarsa" |
| D10 | **Tidak ada evaluasi pada pesan nyata dan terkini**, tidak ada telemetri alasan penolakan. | `eval/` memakai set buatan tim | Perbaikan tidak terukur |

## 2. Yang sudah diperbaiki hari ini (diuji, 138 tes lulus)

- **Jenis pesan.** `pipeline` kini membedakan `berita_media` (tautan ke artikel media dikenal), `kumpulan_judul`, dan `pesan` biasa. Artikel dari media dikenal
  ditampilkan apa adanya: **judul, penerbit, tanggal terbit, ringkasan dari halaman itu sendiri**, dan dinyatakan jujur: "Halio belum menilai isinya;
  untuk hal penting, bandingkan dengan satu atau dua media lain." Tidak ada lagi "jangan diteruskan" untuk berita biasa.
- **Daftar media dikenal** (`outlets.py`) dengan kelompok pemilik, agar dua media satu grup tidak dihitung dua suara. Daftar kerja; perlu ditinjau terhadap daftar media terverifikasi Dewan Pers.
- **Peringatan tautan** tidak lagi mengatakan "bukan situs pemerintah" untuk media berita. Situs tak dikenal tetap diperingatkan.
- **Agen web tidak dijalankan** untuk artikel media dan kumpulan judul (selalu "0 lolos", hanya membuang 30 detik dan kuota).
- **Alasan penolakan AI ditampilkan** dalam bahasa biasa ("halamannya dari media biasa; Halio hanya menerima situs resmi dan pemeriksa fakta sebagai bukti").
- **Daftar bacaan** membuang mesin pencari, pengalih, dan tautan promo aplikasi; memberi nama penerbit yang benar.
- **Telegram:** tombol kini hanya yang bermakna; berita biasa tidak lagi mengirim kartu koreksi dan suara; tombol tetap bekerja setelah bot dimulai ulang
  (jawaban bot membalas pesan pengguna, sehingga teks asli dapat dibaca kembali tanpa menyimpan apa pun).
- **Pelindung:** pesan berantai hoaks yang ditulis per baris pendek tidak salah dikira "kumpulan judul"; artikel pemeriksa fakta tentang hoaks yang sama tetap divonis.

**Belum diuji dengan Vertex AI sungguhan** (tidak ada kredensial di lingkungan saya). Seluruh perubahan di atas bersifat deterministik dan diuji dengan tiruan.

## 2b. Mesin Bukti v2: status implementasi (6 Nov, malam)

**Sudah dibangun dan diuji dengan tiruan (173 tes):** `backend/halio/evidence.py`, aktif secara bawaan (`HALIO_ENGINE=v2`; `v1` mengembalikan agen lama; bila pencarian atau penilaian v2 gagal, sistem otomatis jatuh ke v1).

| Bagian rancangan | Status |
|---|---|
| S2 kutipan dipilih **kode** (kalimat salinan dengan tumpang-tindih kata kunci), selalu utuh | Selesai, diuji |
| S3 model hanya mengembalikan `{nomor, hubungan, covers_all}`; nomor palsu, duplikat, hubungan aneh dibuang | Selesai, diuji |
| S4 kebijakan tingkat A/B/C/D dan kemandirian grup (dua media satu grup, atau kalimat yang sama di dua situs = satu suara) | Selesai, 16 skenario kebijakan diuji |
| Status baru 🔵 **Dilaporkan media** (kartu, bot, web, Radar) | Selesai |
| Kekuatan bukti 0–4 yang dapat dijelaskan | Selesai |
| Kebijakan kesegaran: sumber resmi ≤180 hari untuk "sejalan"; laporan media ≤30 hari untuk "dilaporkan" | Selesai |
| Arsip pemeriksa fakta Sensor sebagai kandidat gratis (tanpa model) | Selesai |
| Halaman web tidak dapat mengubah keputusan (hanya kutipan bernomor masuk ke model; keputusan di kode) | Diuji dengan halaman berisi instruksi |
| Alasan penolakan terlihat (jawaban bot dan web) | Selesai |
| Skrip evaluasi langsung dari judul Sensor (`scripts/eval_live.py`) | Selesai; **harus dijalankan di server** |

**Dibangun 6 Nov malam (diuji, 188 tes):**
- **Pecah pesan menjadi ≤3 klaim** (`claims.split_units`): kalimat layak-periksa yang berbeda (kemiripan <0,6), lengkap dengan kalimat konteks setelahnya. Satu klaim yang diulang, atau satu klaim dengan ajakan sebar, tidak dipecah; pesan bertautan tidak dipecah. Status pesan = klaim yang paling mengkhawatirkan; jawaban per klaim di bot, web, dan kartu.
- **Kantor berita lewat teks**: dateline `(ANTARA) -`, `(Reuters) -`, `(AFP) -`, `(AP) -` pada halaman membuat media yang menerbitkan ulang salinannya dihitung **satu suara**; sebutan sambil lalu dan kredit foto diabaikan.
- **Telemetri harian** (`evidence_telemetry`, hanya hitungan, tanpa teks, 30 hari): alasan halaman ditolak, bagaimana pemeriksaan berakhir, jumlah halaman dibuka/relevan, pemakaian mesin cadangan. Tampil di Radar ("Mengapa AI gagal memakai sebuah sumber"). Sekaligus menutup temuan R5: tabel `events` kini ikut dihapus setelah 30 hari.
- Klaim yang belum dikenal dari pesan beberapa klaim kini dihitung satu per satu untuk Radar.

**Masih belum:** tinjauan daftar media terhadap Dewan Pers; deteksi kantor berita tanpa dateline; biaya: pesan dengan 3 klaim menjalankan pencarian 3 kali (paralel).

**Belum teruji dengan Vertex AI sungguhan.** Dua panggilan model baru (`gemini_discover`, `gemini_judge`) hanya diuji lewat tiruan. Yang harus dipastikan di server, berurutan:
1. `HALIO_LLM=1 python scripts/eval_live.py --news 10 --hoax 10`: apakah ada berita benar yang dituduh salah (harus 0), dan apakah jawaban informatif.
2. Bila "0 halaman relevan" mendominasi, periksa `ditolak` di jawaban: biasanya tautan pengalih Google gagal dibuka atau situs menolak pengambil kami.
3. Bila pengalih Google tidak bisa diuraikan, kandidat hanya datang dari arsip Sensor dan korpus; laporkan ke saya.

## 3. Rancangan: Mesin Bukti v2

Prinsip dari dokumen riset Anda: **AI menafsirkan, kode memverifikasi dan memutuskan.** Model tidak pernah memberi vonis dan tidak pernah menjadi sumber kutipan.

```
pesan / tautan / foto / suara
  S0 Pahami   jenis pesan; pecah menjadi ≤3 klaim atomik; entitas, waktu, tempat; lewati yang bukan klaim            (kode + model kecil)
  S1 Cari     (a) korpus terverifikasi (b) ClaimReview (c) arsip pemeriksa fakta yang sudah dipantau Sensor
              (d) pencarian web ber-grounding, URL diuraikan dan dikanonkan                                           (kode + Gemini)
  S2 Baca     ambil halaman (publik, tanpa skrip); KODE memotong kalimat dan memilih 1–3 kutipan terbaik per halaman
              lengkap dengan tanggal dan penerbit. Kutipan selalu utuh karena disalin kode, bukan model.             (kode)
  S3 Nilai    model menerima kutipan BERNOMOR dan hanya mengembalikan nomor + hubungan (mendukung / membantah / konteks /
              tak terkait) untuk tiap klaim atomik. Nomor palsu otomatis ditolak.                                      (Gemini, dikunci skema)
  S4 Putuskan KODE menerapkan kebijakan tingkat sumber (di bawah). Tidak ada vonis dari model.                          (kode)
  S5 Jelaskan templat tetap: apa yang ditemukan, dari siapa, kapan, apa yang belum diketahui, apa yang bisa dilakukan   (kode)
```

### 3.1 Tingkat sumber dan kemandirian (menyelesaikan D1, D8)
| Tingkat | Contoh | Boleh menjadi |
|---|---|---|
| **A. Resmi** | `.go.id`, `.mil.id`, WHO, BMKG, Bank Indonesia | Dasar "sejalan" dan "terbukti salah" |
| **B. Pemeriksa fakta** | TurnBackHoax, CekFakta.com, Kompas/Liputan6/Tempo Cek Fakta, AFP | Dasar "terbukti salah"; pendukung "benar" bila bantahan atas kebalikannya |
| **C. Media dikenal** | detik, Kompas, ANTARA, Tempo, CNN Indonesia, BBC … (`outlets.py`) | **Bukti pelaporan**, bukan bukti kebenaran |
| **D. Lain** | blog, media sosial, mesin pencari | Tidak pernah bukti; hanya "bahan bacaan" bila terbuka |

Kemandirian: dua laporan dari satu **grup** (mis. detik dan CNN Indonesia) dihitung satu suara; salinan kantor berita yang sama (ANTARA) dihitung satu suara.

### 3.2 Hasil baru yang jujur: "Dilaporkan media" (menyelesaikan D2)
Tambah satu status di samping empat yang ada, dengan makna yang tegas dan terpisah dari "terbukti benar":

| Status | Syarat (diputuskan kode) | Kalimat |
|---|---|---|
| 🔴 Terbukti salah | tingkat A atau B membantah klaim yang sama (kutipan utuh) | "Dibantah oleh …" |
| 🟢 Sejalan dengan sumber | tingkat A masih berlaku mendukung seluruh klaim atomik | "Sesuai keterangan …" |
| 🔵 **Dilaporkan media** (baru) | ≥2 **grup** media berbeda melaporkan inti yang sama dalam jendela waktu wajar, tidak ada bantahan A/B, tidak ada laporan yang bertentangan | "Dilaporkan oleh 3 media berbeda (detikNews, ANTARA, Tempo). Ini bukan pemeriksaan fakta." |
| 🟠 Tidak yakin | sumber saling bertentangan, kedaluwarsa, atau hanya sebagian klaim didukung | menampilkan **apa yang bertentangan**, bukan "tidak yakin" kosong |
| ⚪ Belum ada pemeriksaan | tidak ada sumber yang layak | menyebut **apa yang dicari dan di mana**, bukan "jangan diteruskan" tanpa dasar |

Tanda kekuatan bukti memakai skala 0–4 yang dapat dijelaskan (jumlah grup mandiri, adanya sumber resmi, kesegaran), bukan persentase "keyakinan" model.

### 3.3 Kebijakan rekomendasi (menyelesaikan "jangan diteruskan" untuk semuanya)
"Jangan diteruskan" hanya muncul bila ada **sinyal bahaya yang terukur**: dibantah, atau gabungan minta uang/data + tekanan waktu + sumber tak dikenal.
Pesan netral tanpa bukti mendapat "Belum ada yang memeriksa; belum ada bukti dan belum ada bantahan. Cek di … sebelum meneruskan." Berita dari media dikenal mendapat saran membandingkan, bukan peringatan.

### 3.4 Higiene sumber (menyelesaikan D5, D6)
- Uraikan tautan pengalih Google (`vertexaisearch.cloud.google.com/grounding-api-redirect/...`) dengan pengambil kami (publik saja, batas hop), simpan URL akhir; buang bila ujungnya mesin pencari.
- Kanonkan URL (hapus `utm_*`, `amp`), deteksi soft-404 dan paywall, dan simpan **alasan** setiap penolakan.
- Telemetri tanpa isi pesan: jumlah penolakan per alasan per hari, tampil di panel "Cakupan" agar tim melihat mengapa AI gagal.

### 3.5 Keamanan dari sumber yang tidak tepercaya
Halaman web adalah data, bukan perintah: hanya kutipan bernomor yang masuk ke model, tanpa HTML, dan keluaran model hanya nomor. Upaya penyisipan instruksi di halaman tidak dapat mengubah keputusan karena keputusan dipegang kode. Uji dengan halaman berisi "abaikan aturan di atas".

### 3.6 Banyak klaim dalam satu pesan (menyelesaikan D7)
Pecah menjadi ≤3 klaim atomik; periksa paralel; jawab per klaim dengan ikon, atau minta pengguna memilih satu (mis. foto berisi lima judul → daftar bernomor dengan tombol "periksa nomor 2"). Hari ini hanya kasus kumpulan judul yang ditangani dengan meminta satu per satu.

### 3.7 Biaya dan kecepatan
Anggaran 20–30 detik, kuota harian per pengguna. Cache per klaim 24 jam (kunci: hash klaim ternormalisasi, bukan teks). Gemini 3.5 Flash-Lite dengan `thinking_level=MINIMAL` untuk S0 dan S1; `LOW`/`MEDIUM` hanya untuk S3 saat kutipan bertentangan. Ukur biaya per pemeriksaan, tampilkan di catatan evaluasi.

## 4. Pengukuran: bagaimana tahu AI benar-benar berguna

Set evaluasi nyata dan terkini, bukan buatan tim (disusun dari data yang sudah dikumpulkan Sensor):
- 40 berita benar dari 2 minggu terakhir (judul dari feed media), 30 hoaks yang sudah dibantah (judul dari feed pemeriksa fakta), 30 kabar tak terverifikasi/opini/berantai.
- Metrik wajib: **tuduhan palsu = 0** (berita benar tidak boleh jadi "salah"); cakupan (% pesan dengan jawaban informatif); ketepatan sumber (tautan terbuka dan relevan); latensi p50/p95; biaya per pemeriksaan; alasan penolakan teratas.
- `scripts/eval_live.py` (sudah ada, lihat 2b) menjalankan set terhadap API sungguhan dan menulis laporan; dijalankan di server GCE Anda karena kredensial Vertex ada di sana.
- Uji manusia: dua orang di luar tim menilai 30 jawaban: "apakah Anda paham, dan apakah Anda tahu langkah berikutnya?"

## 5. Urutan kerja (selaras dengan `PLAN_UNGGUL` dan code freeze 11 Nov)

| Tanggal | Pekerjaan | Gerbang |
|---|---|---|
| 6 Nov (hari ini) | Perbaikan deterministik di bagian 2; PR | 138 tes hijau |
| 7 Nov | S2/S3: kutipan bernomor oleh kode, penilaian per nomor, uraian tautan grounding, alasan penolakan terlihat | Tes tiruan: nomor palsu ditolak; kutipan selalu utuh |
| 8 Nov | Tingkat sumber dan kemandirian, status "Dilaporkan media", kebijakan rekomendasi; templat jawaban | Tes: dua media satu grup = satu suara |
| 9 Nov | Evaluasi nyata (set 100) di server; perbaiki dua penyebab penolakan terbesar | Tuduhan palsu 0; cakupan dilaporkan jujur |
| 10 Nov | Pecah klaim (≤3) dan pilihan per klaim; telemetri di panel Cakupan; dokumentasi | Dokumen bukti terisi |
| 11 Nov | **Code freeze** | — |

## 6. Risiko dan batas yang diakui
- Peringkat media bukan kebenaran: "dilaporkan media" tidak berarti benar. Kalimat jawaban harus selalu menyebut itu.
- Daftar media dan kelompok pemilik adalah daftar kerja dari pengetahuan umum; harus ditinjau terhadap daftar Dewan Pers sebelum dipakai sebagai klaim di dokumen juri.
- Banyak berita beredar tanpa pernah diperiksa pemeriksa fakta. Wajar bila "belum ada pemeriksaan" tetap sering muncul; yang berubah adalah apa yang kami katakan sesudahnya.
- Pencarian web ber-grounding bisa meleset atau memberi sumber lama; kebijakan kesegaran dan tanggal wajib.
- Kami tidak menguji ke Vertex dari lingkungan ini. Setiap langkah yang memanggil model harus diuji di server Anda sebelum dipercaya.
- Foto: Halio hanya membaca tulisan/ucapan; keaslian gambar tidak dinilai (lihat `PLAN_UNGGUL.md` bagian 3 untuk rencana asal-usul media).

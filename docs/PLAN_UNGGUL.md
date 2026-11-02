# Rencana: membuat sistem Halio unggul (3 – 14 Nov 2026)

Disusun 3 Nov 2026. Deadline resmi 15 Nov 23:59 WIB, target internal kirim 14 Nov 20:00, **code freeze 11 Nov**
(hanya perbaikan bug sesudahnya). Sisa waktu kerja: 8 hari efektif.

Fokus: **sistem**, bukan video. Bobot juri: Relevansi 25, Inovasi 25, Fungsionalitas 25, Kelayakan 15, Dokumentasi 10.

Dasar rencana: dua dokumen riset hackathon yang Anda berikan ("Rahasia Menang Hackathon…" 2 Nov dan "Ensiklopedia Ekspansi…" 3 Nov),
riset deteksi AI (bagian 3), dan data sensor kami sendiri.

---

## 0. Yang dikatakan riset hackathon, dan posisi Halio

| Pola pemenang (dari dokumen riset) | Keadaan Halio sekarang | Tindakan |
|---|---|---|
| Satu masalah yang dipahami, satu pengguna spesifik | Ada (keluarga + unit siber), tetapi belum divalidasi dengan orang nyata | Wawancara dan pilot kecil (bagian 4) |
| **AI menafsirkan, kode biasa mengukur, memverifikasi, membatasi** (Conductr, Pulse, Sentinel, Echo Canvas) | **Sudah**: model hanya mencari, kode memeriksa ulang tautan dan kutipan, ada policy dan guard | Pertahankan; jadikan inti cerita teknis |
| Satu momen "wow" yang benar-benar berfungsi | Belum ada satu adegan yang tak bisa dipalsukan | Adegan "gambar" (bagian 3.4) |
| Fallback: "the engine never waits for the AI" | Retrieval lokal tetap jalan tanpa model | Tunjukkan mati-API di demo (GagalTangguh) |
| Bukti, bukan klaim: before/after, 5–10 test case, satu kasus gagal | Evaluasi hanya buatan tim (108 item) | Evaluasi independen (bagian 2.5) |
| Merah juri: ambiguitas, detail tipis, "wrapper", repo kosong, template | Repo kuat; korpus tipis | Korpus (bagian 2) |
| Juri sering mengecek: video, repo, API wajib, README, format | Ada daftar `SUBMISSION_CHECKLIST` | Gerbang kepatuhan (bagian 6) |

Satu kalimat posisi (format dari dokumen riset):
> Untuk **keluarga dan unit siber** yang kewalahan oleh pesan berantai, Halio mengubah **pesan, gambar, atau suara** menjadi
> **jawaban bersumber atau pengakuan "belum tahu"**, sehingga **tidak ada kabar yang dicap tanpa bukti**.

---

## 1. Tiga hal yang membuat Halio unggul (bukan "lebih banyak fitur")

1. **Bukti, bukan tebakan** (pembeda utama terhadap CekSumber yang sendiri mengakui "AI punya potensi keliru"):
   asal-usul media (SynthID, Content Credentials), kutipan sumber yang dicek ulang oleh kode, dan status "belum tahu".
2. **Cakupan nyata**: korpus 7 → 300+ entri terverifikasi, otomatis dari sumber yang sudah kami pantau.
3. **Satu alur keluarga → analis**: kartu, suara, Radar agregat, antrean triase, tata kelola. Tidak ada pesaing yang kami temukan menyatukan keduanya.

---

## 2. Korpus: dari 7 menjadi 300+ entri bersumber (target: 9 Nov)

Mafindo punya lebih dari 6.000 entri hasil kerja relawan bertahun-tahun. Kami tidak bisa menyamainya dengan menulis tangan.
Yang bisa kami lakukan: **mengindeks pemeriksaan yang sudah dipublikasikan pihak lain, dengan tautan, tanpa menyalin teks.**

Bukti kelayakan dari sensor kami (sampel 2 Nov): feed `turnbackhoax`, `cekfakta.com`, dan `liputan6-cekfakta` sudah menghasilkan judul
terstruktur seperti `[PENIPUAN] Akun Telegram Pendaftaran Program Bedah Rumah…`, `Hoaks! Pemerintah akan hapus BPJS Kesehatan`,
`Cek Fakta: Hoaks Video Menkeu… Bantuan Dana Hibah Lewat WhatsApp`.

### 2.1 Pipeline "calon bantahan → terverifikasi"
```
item sensor (judul, url, tanggal)            [sudah ada]
  → pengklasifikasi label (aturan: [HOAKS]/[PENIPUAN]/"Hoaks!"/"Cek Fakta:"/[FAKTA]/[KLARIFIKASI])
  → ekstrak klaim (buang prefiks), jenis = bantahan | klarifikasi | fakta(positif)
  → status "calon"
  → verifikasi otomatis: ambil halaman, kutipan persis ≥40 karakter, tanggal terbit     [source_verifier.py sudah ada]
  → ringkasan dalam kata kami sendiri (model, dikunci schema) + sumber + tanggal
  → status "terverifikasi" masuk indeks; yang gagal tetap "calon" (tidak dipakai menghukum pesan)
```
Aturan lisensi: simpan **judul, URL, tanggal, kutipan pendek, ringkasan buatan sendiri**; tidak menyalin isi artikel.
Cek `robots.txt` dan syarat layanan tiap situs sebelum mengambil arsip lama (halaman bernomor); bila ada larangan, hanya pakai item feed.

### 2.2 Sumber tambahan
- **Google Fact Check Tools API** (ClaimReview): kunci sudah didukung di kode (`factcheck_api.py`). Tarik per kategori bahasa `id`; tampilkan atribusi penerbit.
- **Kemitraan Mafindo**: sebut sebagai langkah lanjut, bukan klaim. Jangan menulis seolah sudah bermitra.
- **Korpus TNI AD** (tulis tangan, sumber resmi, 15+ entri): rekrutmen, calo/titipan, pencatutan nama pejabat/seragam, hoaks mobilisasi, tautan pendaftaran palsu. Setiap URL dibuka dan dicek.

### 2.3 Retrieval
TF-IDF + guard inti klaim tetap. Tambah **embedding** (Gemini embedding via Vertex, atau EmbeddingGemma bila ingin lokal) sebagai
penjaring kandidat, lalu guard dan agen web menentukan status. Kriteria lolos: **false-hoax tetap 0** pada kedua set uji.

### 2.4 Positif (sejalan dengan sumber)
Entri `[FAKTA]`/klarifikasi resmi masuk sebagai kandidat positif hanya bila sumber `.go.id/.mil.id` dan masih berlaku (aturan `valid_from/valid_until` sudah ada).

### 2.5 Evaluasi independen (menjawab "belum ada pengguna nyata" dan "evaluasi buatan tim")
- Kumpulkan **100 pesan nyata** (dianonimkan, tanpa data pribadi pihak ketiga) dari 8–10 orang di luar tim, termasuk keluarga dan kolega.
- Dua orang melabeli terpisah; sengketa diselesaikan. Ukur: cakupan (% yang mendapat jawaban bersumber), presisi, false-hoax, waktu respons.
- Laporkan apa adanya, termasuk "belum ada pemeriksaan" yang tinggi. Angka jujur lebih kuat daripada angka bagus.

Gerbang: bila korpus < 150 entri terverifikasi pada 8 Nov, hentikan perluasan dan perbaiki kualitas; jangan memaksa jumlah.

---

## 3. Deteksi AI dan asal-usul media: harus benar

### 3.1 Kebenaran yang harus diterima dulu
- **Tidak ada detektor "AI atau bukan" yang benar 100%.** Benchmark *Deepfake-Eval-2024* (arXiv 2503.02857) pada konten yang benar-benar beredar:
  detektor open-source turun AUC sekitar 45–50% dibanding data akademik, dan yang terbaik hanya 0,58. Detektor komersial lebih baik tetapi masih di bawah analis forensik.
- **SynthID bukan detektor universal.** Ia hanya menemukan watermark pada konten dari generator yang memasangnya: Google (Gemini/Nano Banana, Veo, Lyria, Imagen),
  dan, menurut laporan Google/TechCrunch, mitra seperti OpenAI, NVIDIA, Kakao (Apple menyusul). Gambar dari generator lain **tidak akan terdeteksi**, dan hasil negatif **bukan bukti asli**.
- **Content Credentials (C2PA) mudah hilang.** Pengiriman lewat WhatsApp dan platform lain mengompresi ulang dan membuang metadata (laporan sekunder; periksa dokumen resmi sebelum diklaim). Tidak adanya kredensial tidak membuktikan apa pun.

Karena itu klaim "benar" yang bisa kami pertanggungjawabkan bukan "kami mendeteksi AI", melainkan **"kami menunjukkan bukti asal-usul bila ada, dan mengaku bila tidak ada."**

### 3.2 Akses SynthID: apa yang pasti dan apa yang belum
| Jalur | Status (per riset 3 Nov) | Rencana |
|---|---|---|
| synthid.com / Detector (publik sejak Okt 2026), app Gemini, Chrome | Gratis; gambar, video, audio; kuota Gemini sekitar 10 gambar/hari; **tidak ada API publik yang terkonfirmasi** | Jalur pemeriksa manusia (3.3, lapis B) |
| **AI Content Detection API** (Google Cloud, REST: JPEG/PNG/WebP) | **Preview untuk mitra tepercaya**; organisasi dapat mendaftar early access; tidak menyimpan gambar; deteksi tidak hanya Google | **Daftar early access hari ini** (butuh akun Google Cloud organisasi Anda). Jangan dijadikan dasar demo sebelum akses benar-benar ada |
| Verifikasi watermark Imagen di Vertex AI | Lewat konsol; API belum terkonfirmasi (ada laporan error izin) | Jangan diandalkan |
| SynthID Text (kode terbuka) | Hanya teks yang dibuat dengan watermark; tidak relevan untuk pesan berantai biasa | Abaikan |

Gerbang keputusan **8 Nov**: bila akses API belum diberikan, SynthID otomatis **tidak** dijanjikan; ia muncul sebagai peta jalan dan jalur verifikasi oleh pemeriksa manusia.

### 3.3 Arsitektur media (pola "constrained AI + deterministic" dari dokumen riset)
```
unggahan gambar/audio/video (hanya atas klik pengguna, persetujuan eksplisit)
  ├─ Lapis A (lokal, deterministik, gratis)
  │    • C2PA: verifikasi manifest tertandatangan (pustaka terbuka CAI: c2pa-python / c2patool)
  │    • EXIF/metadata dasar; hash persepsi (pHash/dHash) terhadap gambar arsip bantahan
  │    • OCR teks-dalam-gambar → masuk alur teks yang sudah ada
  ├─ Lapis B (asal-usul watermark)
  │    • AI Content Detection API bila akses ada; bila tidak: tombol "Minta pemeriksa memverifikasi dengan SynthID"
  │      (antrean analis, hasil dicatat sebagai bukti manusia)
  ├─ Lapis C (indikasi forensik, hanya bila tersedia; tidak pernah vonis)
  │    • layanan komersial/Google bila ada; keluaran dikalibrasi, ada ambang abstain
  └─ Policy engine (kode): menetapkan status dan kalimat; model tidak ikut memutus
```

### 3.4 Status hasil media (jujur dan tidak mencampur dua pertanyaan)
Dua pertanyaan berbeda: **"dibuat AI?"** dan **"klaimnya benar?"**. AI-generated bukan otomatis hoaks (bisa ilustrasi). Klaim tetap dicek lewat alur teks/bantahan.

| Status media | Syarat (diputuskan kode) | Kalimat |
|---|---|---|
| **Terbukti dibuat/diubah AI** | Watermark SynthID terdeteksi **atau** manifest C2PA tertandatangan menyatakan generatif | "Gambar ini membawa tanda asal-usul AI." |
| **Asal-usul terverifikasi** | C2PA valid dari kamera/penerbit, belum diubah | "Direkam oleh … pada …, belum diubah." |
| **Pernah dibantah** | Hash persepsi cocok dengan gambar pada arsip bantahan (+ tautan) | "Gambar ini dipakai dalam kabar yang sudah dibantah: [tautan]." |
| **Indikasi AI, belum terbukti** | Hanya lapis C tinggi, tanpa bukti asal-usul | "Ada tanda yang mirip hasil AI, tetapi belum cukup untuk menyatakannya." + rujuk manusia |
| **Tidak ada tanda asal-usul** | Tidak ada sinyal sama sekali | "Tidak ditemukan tanda. Ini **tidak** membuktikan asli atau palsu." |

**Jawaban untuk "harus benar":** yang paling bisa dijamin benar dan paling berguna di konteks Indonesia adalah status **"Pernah dibantah"** (kecocokan hash
terhadap arsip bantahan). Banyak hoaks adalah foto/video lama dengan konteks baru, bukan hasil generatif. Ini deterministik, murah, dan tidak perlu menebak.

### 3.5 Evaluasi media (wajib ada angkanya)
- 30 gambar buatan Gemini/Imagen (ground truth pasti, kami yang membuat; tanpa orang nyata pihak ketiga).
- 30 foto asli milik tim.
- 20 salinan setelah dikirim lewat WhatsApp/screenshot (**uji ketahanan: berapa persen SynthID/C2PA bertahan**).
- 10 gambar dari generator tanpa watermark (uji "tidak mampu": hasil harus "tidak ada tanda", bukan "asli").
- Laporkan recall, false-positive, dan ketahanan setelah kompresi. Satu kasus gagal ditampilkan di dokumen.

### 3.6 Privasi dan risiko
- Gambar yang dikirim ke Google = data keluar. Default: lapis A berjalan di server kami; kirim ke Google **hanya setelah pengguna menekan setuju**, dan dicatat di kebijakan privasi/UU PDP.
- Tidak menyimpan media; hash saja untuk pencocokan.
- Hasil yang bisa menuduh seseorang (mis. "deepfake tokoh X") **tidak ditulis sebagai vonis**.
- Biaya/kuota: hitung dulu sebelum demo.

---

## 4. Pengguna nyata dan deploy (Kelayakan 15, Relevansi 25)

### 4.1 Deploy publik (syarat G.1: tautan yang bisa dicoba juri)
Opsi yang disarankan: **Cloud Run** pada proyek GCP yang sudah dipakai (Vertex dan ADC sudah satu akun), atau Render/Fly bila ingin cepat.
Butuh **akses dari Anda** (saya tidak bisa membuat akun hosting dari sini). Daftar set-up: HTTPS; `RADAR_TOKEN`; `HALIO_CHANNEL_KEY` (sama di API dan bot Telegram);
`HALIO_TRUST_PROXY=1`; volume untuk SQLite (atau Cloud SQL); `HALIO_SENSOR=1` pada satu instance; `HALIO_LLM=1` dengan ADC; domain/URL di README dan form submission.
Gerbang: tautan publik hidup **6 Nov**, diuji dari ponsel di luar jaringan tim.

### 4.2 Pilot kecil dan jujur (5 hari, mulai 7 Nov)
10–20 orang, termasuk 3–5 keluarga/kolega yang relevan dengan TNI AD. Ukur: jumlah cek, % terjawab bersumber, % "belum ada", dan tiga pertanyaan umpan balik
("apakah jawabannya Anda pahami / apakah Anda meneruskan pesannya / apa yang membingungkan"). Persetujuan tertulis singkat, tanpa menyimpan isi pesan.
Laporkan apa adanya: "N orang, M pesan". Itu cukup menjawab "belum ada pengguna nyata".

### 4.3 Wawancara masalah (1 jam, 3 orang)
Satu orangtua pengguna WhatsApp, satu anggota/keluarga TNI AD, satu analis media sosial/siber. Pertanyaan dari dokumen riset: workflow terakhir yang menyebalkan,
data yang tersedia saat itu, keputusan apa yang tidak boleh diotomatisasi, bukti apa yang membuat mereka percaya.

---

## 5. Relevansi TNI AD dan unit siber (Relevansi 25)
- Korpus TNI (bagian 2.2) dan kategori Radar: `pencatutan_tni`, `calo_rekrutmen`, `tautan_pendaftaran_palsu`, `kebocoran_opsec` (agregat, sumber publik saja).
- Panel cakupan sensor tetap menampilkan titik buta. Tambah sumber resmi `.mil.id` bila punya feed publik.
- Larangan tertulis: tidak melacak akun/prajurit tertentu, tidak menilai opini, hanya sumber publik dan agregat (`docs/` tata kelola).
- Dokumen tata kelola dan UU PDP/ITE satu halaman, dibaca juri dan institusi.

---

## 6. Dokumentasi dan submission (10% + penentu kelolosan)
- README: satu kalimat produk, masalah, GIF/screenshot, arsitektur, demo path, setup, teknologi wajib, batasan, evaluasi, pembagian kontribusi.
- Dokumen bukti: `eval/RESULTS.md` (dev + holdout + independen + media), `docs/COMPETITORS.md`, `docs/TRUE_INFORMATION.md`.
- Slide 10–12 halaman, diagram arsitektur "AI vs kode" (halaman terpenting untuk juri teknis).
- Siapkan jawaban 10 pertanyaan juri (dari dokumen riset): pengguna pertama, mengapa AI, data dan izin, evaluasi, saat model salah/mati, persetujuan manusia, mana yang mock, metrik pasca-hackathon, kontribusi.
- Demo **60–90 detik sebagai bukti**, bukan tur fitur: masalah → input nyata → transformasi terlihat → aksi bernilai → safeguard → hasil. Adegan wajib: model dimatikan, tetap jalan.
- Gerbang kepatuhan 10 Nov: thumbnail 1200×630 ≤500 KB, ≤5 screenshot, video YouTube ≤10 menit, slide, tautan publik, atribusi pihak ketiga (`THIRD_PARTY.md`), tanpa data pribadi pihak ketiga, tanpa SARA/pornografi.

---

## 7. Jadwal dan urutan kerja

| Tanggal | Target | Pemilik | Gerbang |
|---|---|---|---|
| 3–4 Nov | Daftar early access AI Content Detection API; spike C2PA (verifikasi file contoh); spike pipeline korpus (100 calon dari feed); siapkan deploy (butuh akses Anda) | Saya (kode) + Anda (akun, pendaftaran, hosting) | C2PA membaca 1 file contoh; 100 calon terklasifikasi |
| 5–6 Nov | Korpus 150+ terverifikasi; **deploy publik hidup**; UI unggah gambar; hash persepsi + arsip bantahan bergambar | Saya | Tautan publik dicoba dari ponsel |
| 7–8 Nov | Retrieval embedding; korpus TNI; mulai pilot; gerbang akses SynthID | Saya + Anda (pilot) | **8 Nov**: akses API ada atau SynthID turun ke peta jalan |
| 9–10 Nov | Evaluasi independen (100 pesan) dan evaluasi media; kebijakan privasi dan tata kelola; slide v1 | Saya + Anda | False-hoax tetap 0; angka final |
| 11 Nov | **Code freeze** | — | Hanya perbaikan bug |
| 12–13 Nov | Dokumen, slide final, latihan pitch/Q&A, rekaman cadangan | Anda + saya | Orang di luar tim menonton tanpa penjelasan dan bisa menjawab "siapa pengguna dan apa yang dilakukan produk" |
| 14 Nov | Kirim sebelum 20:00 WIB | Anda | Form dicocokkan dengan rubrik |

Prinsip dari dokumen riset: **stop menambah fitur lebih awal**, satu orang memegang UI/demo, kontrak API tetap, dan setiap gerbang yang gagal berarti menurunkan lingkup, bukan menambah risiko.

---

## 8. Yang saya butuhkan dari Anda
1. Pendaftaran early access **AI Content Detection API** (akun Google Cloud organisasi) dan konfirmasi siapa yang mengurusnya.
2. Keputusan hosting dan akses deploy (Cloud Run di proyek `gemma4good-494311`, atau lain).
3. 8–10 orang untuk pilot dan evaluasi independen, termasuk 3–5 yang relevan dengan TNI AD.
4. Persetujuan urutan prioritas: **korpus → deploy → media (lapis A) → SynthID bila akses ada → evaluasi → dokumen**.

## 9. Risiko yang diakui
- Akses SynthID API tidak pasti; rencana tetap utuh tanpanya.
- Korpus otomatis bisa salah mengklasifikasi; sebab itu hanya entri yang kutipannya lolos verifikasi yang dipakai.
- Evaluasi pilot kecil tidak membuktikan dampak perilaku; kami tidak mengklaimnya.
- Ketahanan watermark/C2PA setelah WhatsApp belum diukur; angkanya baru ada setelah evaluasi 3.5.
- Hukum: tinjauan UU PDP oleh ahli tetap diperlukan sebelum dipakai institusi.

## 10. Sumber riset deteksi (3 Nov 2026)
- Google, ekspansi SynthID dan Content Credentials, 19 Mei 2026: <https://blog.google/innovation-and-ai/products/identifying-ai-generated-media-online/>
- TechCrunch, 7 Okt 2026, situs SynthID terbuka untuk umum: <https://techcrunch.com/2026/10/07/googles-new-synthid-website-can-identify-ai-generated-media/>
- InfoQ, Mei 2026, pratinjau AI Content Detection API untuk mitra: <https://www.infoq.com/news/2026/05/google-synthid-content-detection/>
- Bantuan Gemini, verifikasi SynthID dan kuota: <https://support.google.com/gemini/answer/16722517>
- Deepfake-Eval-2024, Chandra dkk.: <https://arxiv.org/abs/2503.02857>
- Pustaka terbuka Content Authenticity Initiative: <https://opensource.contentauthenticity.org/>
Catatan: klaim bahwa WhatsApp membuang C2PA berasal dari sumber sekunder; ukur sendiri sebelum dipakai di dokumen juri.

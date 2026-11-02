# Riset agar Halio menonjol: dari inspirasi menjadi bukti

**Kartika Cyber Hackathon 2026 · Siber Sosial · 31 Oktober 2026**

Dokumen ini menerjemahkan nasihat produk, TED Talk, dan penelitian menjadi keputusan yang dapat diuji. Kutipan inspiratif bukan bukti efektivitas. Wawancara dan eksperimen di bawah adalah **protokol yang belum dijalankan**, bukan hasil pengguna.

## 1. Keputusan utama

Posisi Halio: **closed-loop ketahanan kognitif**.

```text
Sinyal sukarela keluarga
  → early warning agregat
  → triase dan verifikasi analis
  → koreksi bersumber kembali ke kanal keluarga
  → pengukuran apakah koreksi dipahami dan keputusan berbagi membaik
```

Yang harus menonjol bukan “AI paling besar”, melainkan:

1. satu alur kerja yang selesai, bukan kumpulan fitur;
2. Halio berani **abstain** ketika bukti belum cukup;
3. privasi dan kemampuan on-premise sebagai batas desain;
4. dampak pada keluarga dan manfaat operasional analis yang diukur.

Dua gap bukti terbesar saat ini:

- **Gap keluarga:** belum ada bukti bahwa Kartu Halio, jeda, atau prebunking mengubah pemahaman dan keputusan berbagi pada keluarga Indonesia.
- **Gap analis:** belum ada bukti bahwa Radar mempersingkat waktu menemukan, menriase, dan menjawab isu dibanding cara kerja yang sudah ada.

Karena itu, prioritas berikutnya adalah **bukti dari satu loop kecil**, bukan sentiment analysis, propaganda classifier, buzzer detection, atau model baru.

### Relevansi ke penilaian

Situs resmi lomba menempatkan pemantauan/analisis disinformasi, propaganda, buzzer, opini publik, dan early warning isu viral dalam Siber Sosial. Bobotnya: relevansi 25%, inovasi 25%, fungsionalitas 25%, implementasi 15%, dokumentasi 10%. Halio tidak harus membangun semua contoh tersebut. Loop keluarga–Radar memenuhi inti deteksi ancaman non-teknis bila alurnya benar-benar berfungsi dan data simulasi diberi label.[1]

## 2. Apa kata inspirator, profesional, dan penelitian

### 2.1 Inspirasi yang boleh membentuk pertanyaan, bukan menggantikan riset

| Sumber | Kutipan/gagasan | Makna untuk Halio | Batas penggunaan |
|---|---|---|---|
| Claire Wardle, TED 2019[7] | “Can we build out a coordinated, ambitious response that matches the scale and complexity of the problem? … Together, let’s rebuild our information commons.” | Masalah informasi bukan hanya pekerjaan individu atau classifier. Hubungkan keluarga, pemeriksa fakta, dan analis dalam loop yang jelas. | Kutipan pendek telah diverifikasi dari catatan resmi TED; ini visi, bukan bukti bahwa desain Halio efektif. |
| Steve Jobs, WWDC 1997 | Gagasan yang sering dikutip: mulai dari pengalaman pengguna, lalu bekerja mundur ke teknologi. | Mulai dari momen keluarga menerima pesan dan analis harus mengambil keputusan; jangan mulai dari model yang tersedia. | Rekaman primer penuh belum diverifikasi dalam riset ini. **Jangan tampilkan sebagai kutipan terverifikasi di slide** sebelum sumber primer diperiksa. |
| Simon Sinek | Gagasan “Start With Why” populer sebagai nasihat positioning. | “Mengapa” Halio adalah membantu keluarga merespons tanpa saling mempermalukan dan membantu analis melihat pola, bukan “memakai AI”. | Transkrip primer gagal diambil; **tidak ada kutipan Sinek yang diverifikasi di sini**. |

Prinsip yang dipakai seterusnya: inspirasi menghasilkan hipotesis; penelitian membantu memilih desain; hanya pengujian pada konteks Halio yang dapat menjawab apakah desain ini bekerja.

### 2.2 Bukti ilmiah dan implikasinya

| Sumber | Populasi dan metode | Temuan yang relevan | Keterbatasan | Hipotesis yang harus diuji Halio |
|---|---|---|---|---|
| Pennycook, Rand, dkk., MIT IDE[2] | Dua eksperimen, total lebih dari 1.700 orang dewasa AS; intervensi pengingat akurasi seputar misinformasi COVID-19. | Pengingat akurasi hampir melipatgandakan **truth discernment** pada niat berbagi dalam studi tersebut. | Niat berbagi bukan perilaku nyata; populasi dan konteks berbeda; hasil tidak otomatis berlaku pada keluarga Indonesia. | Jeda singkat “Apakah pesan ini akurat?” dapat memperbesar selisih niat berbagi konten benar versus salah, tanpa menekan berbagi konten benar. |
| Roozenbeek, Freeman, van der Linden, replikasi praregistrasi[3] | Tahap pertama `n=701`; gabungan `N=1.583`. | Tahap pertama gagal mereplikasi efek (`p=.67`); gabungan hanya efek kecil (`p=.017`; treatment `d=.14`, control `d=.10`). | Efek kecil dan bergantung pengukuran; bukan jaminan intervensi satu kali bekerja di lapangan. | Jeda Halio wajib dibandingkan dengan kartu tanpa jeda. Jangan mengklaim “terbukti mengubah perilaku”. |
| Roozenbeek dkk., *Science Advances* 2022[4] | Lima video prebunking; enam RCT `n=6.464` dan studi lapangan YouTube `n=22.632`. | Meningkatkan pengenalan teknik manipulasi, discernment, dan kualitas keputusan berbagi pada sejumlah ukuran. | Tidak setiap teknik menghasilkan perbaikan signifikan pada setiap ukuran; transfer ke format teks/kartu keluarga perlu diuji. | “Kenali triknya” mungkin membantu pengguna mengenali teknik pada pesan baru, bukan hanya menghafal satu hoaks. |
| Rohim & Alimudin, Indonesia, 2026[5] | Mixed methods; survei 228 responden urban/semi-urban Jakarta/Bekasi dan 15 wawancara. | Komunikasi sosial dan literasi digital saling melengkapi dalam respons terhadap disinformasi. | Cross-sectional; tidak dapat digeneralisasi ke seluruh Indonesia; bukan evaluasi Halio. | Koreksi yang dapat dibawa kembali ke percakapan keluarga layak diuji, bukan hanya skor personal di aplikasi. |
| Bad News lintas budaya[6] | Studi `n=5.061`, convenience/self-selected sample, empat bahasa non-Inggris. | Permainan menurunkan perceived reliability konten manipulatif; penulis menegaskan pendekatan ini bukan *silver bullet*. | Sampel tidak representatif; permainan bukan kartu koreksi; pengukuran persepsi bukan perilaku jangka panjang. | Prebunking hanya lapisan pendukung. Ukur apakah pengguna tetap memercayai konten benar dan memahami ketidakpastian. |

**Kesimpulan penting:** bukti mendukung pengujian accuracy nudge dan prebunking, tetapi tidak mendukung klaim bahwa keduanya pasti efektif pada Halio. Replikasi yang lemah justru menjadi alasan untuk mengukur, bukan menambah klaim.

### 2.3 Nasihat profesional yang menjadi aturan kerja

- **Observasi sebelum opini.** Tanyakan kejadian terakhir dan minta partisipan memperagakan alurnya; jangan bertanya “apakah Anda suka ide ini?”.
- **Ukur outcome, bukan output.** Jumlah cek dan jumlah kartu bukan dampak. Ukur discernment, pemahaman, koreksi yang kembali ke grup, waktu triase, dan false alarm.
- **Desain ketidakpastian.** “Belum ada pemeriksaan” harus tetap memberi langkah aman tanpa menyamakan tidak ditemukannya bukti dengan kesalahan klaim.
- **Uji pesan koreksi sebagai perilaku sosial.** Penerima harus dapat memahami dan membagikan koreksi tanpa merasa dirinya atau anggota keluarganya dipermalukan.
- **Jangan mengutip riset di luar cakupannya.** Sampel AS, niat berbagi, atau hasil video prebunking tidak boleh dipresentasikan sebagai bukti dampak Halio pada masyarakat Indonesia.

## 3. Peta kompetitor dan ruang pembeda

Tingkat bukti: **A** = halaman primer berhasil diperiksa; **B** = sumber sekunder yang kredibel; **C** = cuplikan pencarian atau belum dapat diperiksa penuh. Fitur bertanda C tidak boleh dipakai sebagai fakta mutlak dalam proposal.

| Alternatif | Yang sudah tersedia | Bukti | Jangan klaim sebagai hal baru | Gap yang masih dapat diuji Halio |
|---|---|---|---|---|
| Mafindo / TurnBackHoax / kanal cek fakta | Arsip bantahan; kanal WhatsApp/chatbot dan ekstensi pernah dipublikasikan. Halaman produk resmi yang berhasil diperiksa menampilkan Lentera Litera. | Arsip: A; kanal lama: B/C melalui dokumentasi GitBook, Nieman Lab, dan hasil pencarian.[8][9] | Chatbot WhatsApp, pencarian bantahan, atau cek fakta itu sendiri. | Alur keluarga → agregasi sukarela → triase analis → koreksi kembali; bukan menggantikan pemeriksa fakta. |
| Google Fact Check Explorer | Antarmuka pencarian pemeriksaan fakta masih dapat dibuka saat riset. | A untuk antarmuka.[10] | Pencocokan klaim atau penggunaan ClaimReview. | Integrasi sumber dengan abstain, tindakan keluarga, dan loop operasional. |
| Social listening komersial, mis. Isentia | Pemantauan/social listening ditawarkan di pasar. | C: hasil pencarian menyebut social listening, tetapi halaman penuh menghasilkan 403 dalam riset ini. | Dashboard tren, monitoring, atau analisis media. | Sinyal berbasis laporan sukarela dengan small-cell suppression dan tindakan koreksi, bukan pemantauan semua percakapan. |
| Chatbot/model generatif umum | Pengguna dapat meminta penjelasan tentang suatu pesan. | Perbandingan kategori, bukan benchmark produk; jangan menyatakan semua model selalu gagal abstain. | “AI penjawab hoaks”. | Grounding pada korpus bernama, keadaan abstain eksplisit, kanal keluarga, koreksi bersumber, dan deployment on-premise. |

**Positioning yang dapat dipertahankan:** “Halio menghubungkan sinyal sukarela keluarga dengan triase analis dan koreksi bersumber, sambil mengukur kualitas keputusan dan membatasi data.” Ini adalah hipotesis pembeda kombinasi alur, bukan klaim bahwa tidak ada produk lain di dunia dengan seluruh kemampuan tersebut.

### Risiko dependensi sumber

News Literacy Project melaporkan Google sedang menghentikan penggunaan ClaimReview dalam programnya; ClaimReview sendiri tetap format terbuka.[11] Ini sumber sekunder dan **bukan** bukti bahwa setiap API sudah dimatikan. Tindakan Halio: uji ketersediaan dan cakupan secara aktual, sediakan korpus lokal, dan jangan menjadikan satu layanan eksternal sebagai satu-satunya sumber kebenaran.

## 4. Matriks gap → pertanyaan → metode → keputusan

| Gap | Pertanyaan yang harus dijawab | Metode minimum | Metrik | Hubungan dengan lomba / keputusan |
|---|---|---|---|---|
| Masalah keluarga belum terverifikasi | Bagaimana koreksi terakhir benar-benar terjadi di grup? Siapa memulai, apa hambatannya? | 5–8 wawancara anggota keluarga lintas usia; critical incident, bukan opini umum. | Hambatan berulang; langkah yang dilewati; kebutuhan bahasa/kanal. | Relevansi: ubah persona dan alur berdasarkan bukti, bukan imajinasi tim. |
| Koreksi mungkin mempermalukan | Nada mana yang membuat penerima paham dan bersedia meneruskan koreksi? | Uji kartu faktual vs faktual + empati; tanya maksud dan perasaan, bukan preferensi saja. | Pemahaman benar; niat berbagi koreksi; perasaan dipermalukan; waktu baca. | Inovasi + relevansi: pilih nada paling aman; hentikan copy yang menghakimi. |
| Jeda belum tentu efektif | Apakah accuracy pause meningkatkan discernment tanpa mengurangi berbagi konten benar? | Perbandingan kartu dengan/tanpa jeda pada konten sintetis benar dan salah. | Discernment; sharing konten benar/salah terpisah; waktu keputusan. | Fungsionalitas: pertahankan hanya bila ada sinyal manfaat dan tidak ada kerugian jelas. |
| Prebunking mungkin hanya dekorasi | Apakah “Kenali triknya” membantu mengenali teknik pada pesan baru? | Item transfer yang belum pernah dilihat; kartu dengan/tanpa penjelasan teknik. | Identifikasi teknik; penjelasan alasan; false suspicion pada konten benar. | Inovasi: ringkas/hapus bila tidak menambah pemahaman. |
| Closed loop belum dibuktikan | Apakah laporan keluarga menghasilkan tindakan analis dan jawaban yang kembali? | Satu skenario end-to-end dengan data sintetis; catat setiap handoff dan kegagalan. | Completion rate; waktu loop; tiket tanpa respons; sumber koreksi. | Fungsionalitas 25%: demo utama harus menunjukkan loop selesai. |
| Nilai Radar belum terbukti | Apakah Radar lebih berguna daripada daftar laporan mentah? | 3–5 calon analis; dua skenario counterbalanced, Radar vs feed mentah dengan isi setara. | Time-to-awareness; time-to-triage; precision triase; false alarm; kejelasan tindakan. | Relevansi + inovasi: sederhanakan Radar bila tidak mempercepat/memperjelas keputusan. |
| Privasi dapat disalahpahami | Apakah pengguna mengira Halio membaca semua chat atau mengidentifikasi pelapor? | Wawancara pemahaman + inspeksi data aktual. | Jawaban benar tentang data; data yang tersimpan; small-cell yang bocor. | Implementasi: perbaiki copy/data flow sebelum menambah sumber data. |
| Fit operasional belum diketahui | Siapa memverifikasi, dengan otoritas apa, dan bagaimana koreksi dikirim? | 3–5 calon analis + 2–3 pemeriksa fakta; walkthrough tugas. | Peran, beban, izin, sumber, SLA yang realistis. | Implementasi 15%: jangan klaim akses/kerja sama TNI; tetapkan kebutuhan nyata. |
| Abstain mungkin dianggap gagal | Apakah “belum ada pemeriksaan” tetap memberi langkah yang berguna? | Skenario klaim tak dikenal dan klaim benar satu topik dengan hoaks. | Kepatuhan tidak menebak; tindakan aman; kepercayaan yang terkalibrasi. | Dokumentasi + fungsionalitas: perbaiki copy, bukan memaksa verdict. |

## 5. Protokol wawancara

### 5.1 Partisipan dan etika

Target eksploratif: **5–8 anggota keluarga**, **3–5 calon analis**, **2–3 pemeriksa fakta**. Variasikan usia dan pengalaman; jangan hanya teman satu tim. Sampel ini untuk menemukan masalah dan kegunaan, bukan estimasi prevalensi nasional atau bukti statistik efektivitas.

- Gunakan rekrutmen sukarela, persetujuan lisan/tertulis, dan izin terpisah untuk merekam.
- Jelaskan tujuan, durasi, hak berhenti, hak melewati pertanyaan, penyimpanan, dan cara menarik data.
- Jangan meminta chat pribadi asli, nomor telepon, identitas anggota keluarga, data operasional, atau informasi TNI yang tidak publik.
- Gunakan pesan dan skenario sintetis. Anonimkan catatan; pisahkan persetujuan dari jawaban; batasi akses dan tetapkan tanggal hapus.
- Tidak ada klaim akses, endorsement, atau kerja sama TNI. Calon analis bukan otomatis perwakilan resmi institusi.
- Uji manusia belum dilakukan sampai persetujuan etik internal tim dan instrumen ini disepakati.

### 5.2 Anggota keluarga, 25–30 menit

1. “Ceritakan pesan terakhir di grup keluarga yang membuat Anda ragu. Apa yang Anda lakukan setelahnya?”
2. “Kapan terakhir Anda atau anggota keluarga meluruskan pesan? Apa yang terjadi kemudian?”
3. “Apa yang paling sulit: mengetahui kebenarannya, menjelaskannya, atau menjaga perasaan pengirim?”
4. “Peragakan apa yang biasanya Anda lakukan dengan pesan seperti ini.” Gunakan stimulus sintetis.
5. “Di titik mana Anda akan berhenti memakai alur tadi? Mengapa?”
6. Bacakan status abstain: “Menurut Anda, apa arti jawaban ini? Apa tindakan Anda berikutnya?”
7. Setelah kartu: “Dengan kata Anda sendiri, apa yang dikatakan kartu ini? Bagian mana yang masih meragukan?”
8. “Jika Anda meneruskan kartu ini, apa yang mungkin dirasakan pengirim pesan awal?”
9. “Data apa yang Anda kira disimpan? Bagian mana yang membuat Anda tidak nyaman?”
10. “Apa yang akan membuat Anda tidak menggunakannya lagi?”

Catat perilaku aktual, kutipan anonim, dan hambatan. Jangan menghitung “suka” sebagai validasi dampak.

### 5.3 Calon analis, 30–40 menit

1. “Ceritakan terakhir kali sebuah isu sosial/disinformasi menjadi prioritas. Bagaimana Anda mengetahuinya?”
2. “Apa yang membuat isu layak naik menjadi perhatian, dan apa yang hanya menjadi noise?”
3. “Siapa memverifikasi, siapa memutuskan, dan siapa boleh mengirim respons?”
4. “Informasi minimum apa yang dibutuhkan sebelum tindakan?”
5. “Tunjukkan bagaimana Anda menriase skenario sintetis ini menggunakan daftar mentah.”
6. Ulangi dengan Radar setara: “Apa tindakan berikutnya? Informasi apa yang hilang?”
7. “Apa arti lonjakan ini? Apa alternatif penjelasannya?”
8. “False alarm seperti apa yang paling mahal? Koreksi terlambat seperti apa yang paling berisiko?”
9. “Data apa yang tidak boleh masuk sistem? Bagaimana aturan retensi/audit yang Anda harapkan?”
10. “Di mana loop ini akan gagal pada hari kerja nyata?”

### 5.4 Pemeriksa fakta, 30 menit

1. “Apa yang membuat klaim dapat diperiksa dan layak diprioritaskan?”
2. “Bukti apa yang cukup untuk status ‘terbukti salah’, dan kapan harus abstain?”
3. “Bagaimana menangani klaim campuran, konteks berubah, atau sumber yang memperbarui koreksi?”
4. “Apa bahaya terbesar ketika sistem otomatis mencocokkan pesan dengan bantahan lama?”
5. “Bagaimana atribusi, lisensi, tautan, tanggal, dan pembaruan sumber seharusnya dikelola?”
6. “Apa yang membuat kartu koreksi mudah dipahami tetapi tetap setia pada bukti?”
7. “Bagaimana proses banding dan koreksi atas kesalahan Halio seharusnya bekerja?”

### 5.5 Cara menganalisis tanpa mengarang kepastian

Dua anggota tim mengodekan catatan secara independen ke tema: hambatan, strategi, kebutuhan, risiko, dan kutipan pendukung. Bedakan temuan yang berulang dari satu opini menarik. Catat disconfirming evidence. Keluaran setiap sesi: observasi, interpretasi, keputusan desain, dan pertanyaan yang masih terbuka.

## 6. Desain eksperimen keluarga

### 6.1 Tahap A — usability dan pemahaman dahulu

Gunakan 5–8 partisipan untuk menemukan masalah parah pada loop. Ini bukan RCT dan tidak menghasilkan klaim efektivitas. Tugas: menerima pesan sintetis, memeriksa, menjelaskan jawaban, memutuskan berbagi, dan mengirim koreksi.

Catat:

- berhasil menyelesaikan tugas tanpa bantuan;
- salah mengartikan abstain sebagai “hoaks” atau “aman”;
- mampu menyebut sumber dan alasan;
- salah menekan/tidak menemukan eskalasi;
- waktu dan titik bantuan;
- merasa dipermalukan atau khawatir diawasi.

Gerbang tim sebelum eksperimen komparatif: semua masalah kritis diperbaiki; tidak ada partisipan yang pulang dengan salah tafsir tanpa klarifikasi.

### 6.2 Tahap B — eksplorasi komparatif

**Pertanyaan:** intervensi mana yang layak dipertahankan untuk uji lebih besar?

- **Correction card:** (A) verdict + sumber; (B) A + penjelasan singkat + langkah aman; (C) B + nada empati non-menghakimi.
- **Accuracy pause:** kartu terpilih dengan/tanpa pertanyaan singkat “Menurut Anda, apakah pesan ini akurat?” sebelum pilihan berbagi.
- **Prebunking:** dengan/tanpa “Kenali triknya”; gunakan item transfer untuk teknik yang sama tetapi klaim berbeda.
- **Nada koreksi:** “Pesan ini salah” vs “Banyak orang menerima pesan serupa; pemeriksaan sumber X menunjukkan…”. Jangan menyembunyikan verdict demi keramahan.

Jangan menguji seluruh kombinasi sekaligus pada sampel kecil. Pilih satu pertanyaan per putaran. Gunakan desain within-subject dengan urutan counterbalanced bila cocok; acak kondisi dan pasangkan tingkat kesulitan item. Catat bahwa repeated exposure dapat menyebabkan learning effects.

**Stimulus:** minimal 12 pesan sintetis per bentuk yang setara: setengah benar, setengah salah; topik dan gaya diseimbangkan; sumber fiktif yang jelas untuk latihan, sumber nyata terverifikasi bila menilai kartu aktual. Jangan memakai korban, identitas, SARA, atau konten eksplisit.

**Ukuran utama:**

- `discernment = rata-rata skor niat berbagi konten benar − rata-rata skor niat berbagi konten salah`; skor dan arah harus dilaporkan.
- Sharing konten benar dan salah dilaporkan **terpisah**, agar kenaikan discernment bukan akibat menolak semuanya.
- Pemahaman: jawaban benar atas isi, sumber, dan ketidakpastian.
- Pengenalan teknik pada item baru.
- Waktu membaca/keputusan dan keberhasilan mengirim koreksi.
- Niat berbagi tetap proksi, bukan perilaku nyata.

Dengan 5–8 orang, laporkan respons individual, distribusi, dan kejadian kegagalan; jangan memakai `p < .05` sebagai gerbang. Eksperimen confirmatori berikutnya membutuhkan power analysis, praregistrasi outcome/eksklusi, dan sampel yang sesuai.

### 6.3 Kartu hasil yang wajib dicatat

Untuk setiap kondisi simpan versi kartu, ID stimulus sintetis, kondisi, urutan, jawaban, waktu, dan observasi. Jangan simpan identitas pada file respons. Publikasikan agregat kecil hanya bila tidak memungkinkan re-identifikasi.

## 7. Desain evaluasi Radar

Gunakan 3–5 calon analis untuk uji formatif. Buat dua paket skenario sintetis setara yang berisi sinyal relevan, duplikat, rumor ambigu, dan distraktor. Bandingkan **daftar laporan mentah** dengan **Radar**; counterbalance urutan agar hasil tidak sekadar efek belajar.

| Metrik | Definisi operasional |
|---|---|
| Time-to-awareness | Waktu dari skenario dibuka sampai partisipan menandai isu prioritas yang telah ditentukan. |
| Time-to-triage | Waktu sampai kategori, alasan, dan tingkat keyakinan dicatat. |
| Precision triase | Isu prioritas yang benar ÷ semua isu yang ditandai prioritas. |
| False alarm | Distraktor/laporan tidak layak yang dinaikkan sebagai prioritas; laporkan jumlah dan kasusnya. |
| Waktu koreksi | Waktu dari isu dipilih sampai rancangan koreksi bersumber siap dikirim. |
| Kejelasan tindakan | Partisipan dapat menyebut tindakan, pemilik, dan alasan tanpa ditebakkan oleh fasilitator. |
| Loop selesai | Koreksi benar-benar tiba kembali di kanal keluarga dan dapat dipahami penerima. |

Jangan hanya bertanya “Radar ini berguna?”. Minta keputusan nyata dan bandingkan jejak waktunya. Pada sampel kecil, satu false alarm serius lebih informatif daripada skor kepuasan tinggi.

## 8. Prioritas implementasi dan bukti untuk demo

### P0 — sebelum menambah fitur

1. **Instrumentasi loop:** timestamp laporan, agregasi, triase, jawaban analis, dan koreksi kembali; semua demo berlabel simulasi bila datanya sintetis.
2. **Kartu koreksi yang diuji:** verdict, alasan, sumber bernama/tautan, langkah aman, dan nada tidak mempermalukan.
3. **Tugas analis yang nyata:** alasan triase, sumber, pemilik tindakan, dan status jawaban kembali.
4. **Bukti keterbatasan:** klaim tak dikenal abstain, klaim benar satu topik tidak disebut hoaks, data simulasi terlihat, dan korpus kecil diakui.

### P1 — hanya jika loop sudah berjalan

- Accuracy pause sebagai kondisi yang dapat dimatikan untuk evaluasi.
- Prebunking singkat dengan item transfer.
- Laporan hasil formatif dan perubahan desain berdasarkan temuan.
- Uji privasi dan retensi pada data aktual, bukan hanya pernyataan di slide.

### Tidak diprioritaskan

Buzzer detection, sentiment analysis, propaganda classifier, integrasi kanal baru, dan deepfake detection. Penyebutan contoh di situs lomba bukan kewajiban membangun semuanya; fitur-fitur ini menambah risiko dan mengaburkan loop.

### Bukti yang boleh diklaim sekarang vs setelah riset

| Sekarang | Hanya setelah data benar-benar dikumpulkan |
|---|---|
| “Prototipe menjalankan loop dengan data demo/sintetis.” | “Partisipan menyelesaikan tugas X/Y; hambatan utama …” |
| “Desain terinspirasi riset accuracy nudge dan prebunking.” | “Dalam uji eksploratif kami, kondisi … menunjukkan …; belum generalizable.” |
| “Radar dirancang untuk membantu triase agregat.” | “Pada skenario ini, median waktu triase berubah dari … menjadi …” |
| “Korpus dan evaluasi tim masih terbatas.” | “Pemeriksa fakta merekomendasikan …; bukan endorsement kecuali tertulis.” |

## 9. Rekomendasi alur demo

1. **Masalah keluarga:** persona menerima pesan sintetis; sebutkan persona dan data, jangan memakai cerita sebagai hasil wawancara.
2. **Sinyal sukarela:** pengguna memeriksa/melaporkan; tekankan tindakan pengguna, bukan pembacaan semua chat.
3. **Early warning agregat:** Radar menunjukkan pola dari beberapa laporan simulasi, dengan banner simulasi.
4. **Triase analis:** analis memilih isu, memeriksa sumber, dan memutuskan respons; abstain bila bukti kurang.
5. **Koreksi kembali:** jawaban dan Kartu Halio tiba lagi di kanal keluarga.
6. **Bukti dan batas:** tampilkan waktu loop aktual, status sumber, hasil evaluasi yang ada, korpus kecil, dan riset manusia yang masih harus dilakukan.

Satu loop ini lebih kuat daripada feature tour. Jika wawancara/eksperimen belum selesai, katakan demikian; jangan menggantinya dengan kutipan motivator.

## 10. Referensi dan status verifikasi

1. **Kartika Cyber Hackathon 2026**, kategori Siber Sosial dan kriteria penilaian. https://kartikacyberhackathon.id/ — situs resmi, diperiksa.
2. **MIT Initiative on the Digital Economy**, “Fighting COVID-19 Misinformation on Social Media: Experimental Evidence for a Scalable Accuracy-Nudge Intervention.” https://ide.mit.edu/research/fighting-covid-19-misinformation-on-social-media-experimental-evidence-for-a-scalable-accuracy-nudge-intervention/ — ringkasan riset primer/institusional, diperiksa.
3. **Roozenbeek, Freeman & van der Linden**, replikasi praregistrasi intervensi pengingat akurasi. https://pmc.ncbi.nlm.nih.gov/articles/PMC8641132/ — teks penuh dan detail numerik diperiksa dari artikel.
4. **Roozenbeek dkk.**, “Psychological inoculation improves resilience against misinformation on social media,” *Science Advances* (2022). https://www.science.org/doi/10.1126/sciadv.abo6254 — artikel primer, diperiksa.
5. **Rohim & Alimudin**, studi komunikasi sosial dan literasi digital di Indonesia, *Frontiers in Communication* (2026). https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2026.1816038/full — teks penuh, diperiksa.
6. **Bad News cross-cultural study**, *Misinformation Review*. https://misinforeview.hks.harvard.edu/article/global-vaccination-badnews/ — teks penuh, diperiksa.
7. **TED**, catatan resmi TED 2019 dengan kutipan Claire Wardle. https://blog.ted.com/mindshift-notes-from-session-5-of-ted2019/ — sumber resmi sekunder terhadap talk, kutipan diperiksa.
8. **Mafindo**, WhatsApp Hoax Buster introduction (GitBook). https://mafindo.gitbook.io/ — dokumentasi proyek ditemukan melalui pencarian; status layanan saat ini belum diverifikasi.
9. **TurnBackHoax**, arsip pemeriksaan fakta. https://turnbackhoax.id/ — sumber primer untuk arsip; bukan bukti fitur chatbot aktif.
10. **Google Fact Check Explorer**. https://toolbox.google.com/factcheck/explorer — antarmuka berhasil dibuka; cakupan Indonesia tetap harus diuji.
11. **News Literacy Project**, perubahan program ClaimReview Google. https://newslit.org/updates/how-to-find-better-search-results-as-ai-summaries-take-over-and-google-ends-claimreview-fact-checking-program/ — sumber sekunder; jangan ditafsirkan sebagai konfirmasi semua API telah dimatikan.

### Sumber yang sengaja tidak dipakai untuk klaim kuat

- Artikel Nature Martel/Rand dan artikel Malhotra tentang koreksi dalam grup keluarga WhatsApp belum berhasil diperiksa dari teks penuh. Tidak ada detail sampel/hasil yang dikutip.
- Cuplikan hasil pencarian bukan pengganti halaman primer. Ini berlaku khusus untuk fitur kompetitor dan kutipan tokoh.
- Steve Jobs dan Simon Sinek tidak digunakan sebagai bukti ilmiah atau kutipan terverifikasi dalam materi lomba sampai sumber primernya diperiksa.

# Posisi Halio dibanding yang sudah ada

Disusun 2 Nov 2026 dari sumber publik. Hal yang tidak bisa kami buktikan ditandai **(belum terverifikasi)**.
Jumlah bintang GitHub diambil dari pelacak pihak ketiga, bukan dari GitHub langsung, jadi hanya perkiraan.

## 1. Lanskap

### Indonesia (pemakai nyata, jadi pembanding yang paling penting)
| Proyek | Yang dilakukan | Kekuatan | Celah yang terlihat |
|---|---|---|---|
| **CekSumber** (pengembang Andrew Daniel, bermitra Mafindo; [Antara, 11 Agu 2025](https://jogja.antaranews.com/berita/760569/masyarakat-bisa-deteksi-hoaks-lewat-wa-gunakan-ceksumber)) | Chatbot WhatsApp berbasis AI: teks, gambar, video; hasil dengan tautan sumber | Sudah hidup di kanal yang dipakai orang; tanpa pendaftaran; menerima gambar/video | Mengakui bisa salah ("AI punya potensi keliru"); tidak bisa membuka tautan media sosial; tidak ada keadaan "belum tahu" yang eksplisit **(belum terverifikasi)**; tidak ada sisi analis/agregat yang terlihat |
| **Mafindo**: CekFakta.com, Kalimasada (basis data lebih dari 6.000 entri per [detik](https://inet.detik.com/security/d-5261709/cara-mudah-cek-hoax-tinggal-wa-chatbot-ini-saja)) | Basis data pemeriksaan oleh relawan dan redaksi | Otoritas, jaringan relawan, basis data besar | Pencarian berbasis kata kunci; status terkini tiap layanan **(belum terverifikasi)** |
| **Chatbot Kominfo/Prosa.ai (2019)** | Bot Telegram atas mesin AIS dan basis data Mafindo | Pernah memakai sumber resmi | Tidak ada bukti masih aktif |

### Global, kode terbuka
| Proyek | Yang dilakukan | Catatan |
|---|---|---|
| **Cofacts** (g0v, Taiwan) | Bot LINE: pesan diteruskan, relawan menulis balasan, data terbuka CC BY-SA ([IJNet](https://ijnet.org/en/story/taiwanese-cofacts-fact-checks-information-line)) | Model komunitas terbukti; 46.000 pesan dalam tiga bulan pertama, 35.180 terjawab otomatis (laporan 2018). Bintang GitHub: tidak terverifikasi |
| **Meedan Check** | Platform tipline WhatsApp untuk pemeriksa fakta, kode terbuka ([Meedan](https://meedan.org/post/insights-from-5-700-fact-checks-on-the-whatsapp-business-api)) | Dipakai di India, Brasil, Afrika; berorientasi pemeriksa, bukan keluarga |
| **Loki / OpenFactVerification** (Libr-AI) | Pipeline: pecah klaim, cek layak-periksa, buat kueri, ambil bukti, verifikasi ([repo](https://github.com/Libr-AI/OpenFactVerification)) | Sekitar 1,1 ribu bintang (pelacak pihak ketiga, perkiraan); komitmen terakhir diperkirakan lebih dari setahun lalu |
| **Aos Fatos "Fátima/FátimaGPT"** (Brasil) | Bot WhatsApp/Telegram; versi baru memakai RAG atas arsip sendiri ([Nieman Lab](https://www.niemanlab.org/2024/01/this-brazilian-fact-checking-org-uses-a-chatgpt-esque-bot-to-answer-reader-questions/)) | Pola yang sama dengan Halio (jawab hanya dari arsip bersumber); ukuran akurasi independen tidak ditemukan |

### Kompetisi dan hackathon
- **Kartika Cyber Hackathon 2026, Siber Sosial** (repo publik yang kami temukan): NARADA (Electron), CakraWatch
  (IndoBERT, F1 0,9953 pada 224 item, 2 komit), OPSEC Guard (YOLO-World + OCR + EXIF). Tidak ada demo publik atau video yang kami temukan.
- **TruthTell Hackathon, WAVES Summit 2025 (India)**: pemenang yang tercatat, tim Alchemist (VeriStream), memakai NLP
  LangChain, graf pengetahuan, dan AI yang dapat dijelaskan untuk siaran langsung ([CXO Digital Pulse](https://www.cxodigitalpulse.com/icea-announces-top-5-winners-of-truthtell-hackathon-as-part-of-upcoming-waves-summit-2025/)). Juara satu: tidak terkonfirmasi.
- **Canadian #AI Misinformation Hackathon 2023**: juara satu ReadProbe, alat membaca lateral ([Social Media Lab](https://socialmedialab.ca/2023/03/27/2023-canadian-ai-misinformation-hackathon-winners-announced/)).
- **Newsmatics Hackathon 2025 (Brno)**: alat cek pernyataan tokoh publik hanya juara ketiga ([Newsmatics](https://www.newsmatics.com/press/794504983-students-shine-with-innovative-solutions-at-newsmatics-inaugural-hackathon-winning-team-takes-home-25-000-czk)).
- Bukti pola kemenangan tipis. Yang terlihat: pemenang menunjukkan **satu pengguna spesifik**, **penjelasan yang bisa dipahami**, dan **demo yang berjalan**. Jangan mengklaim lebih dari itu.

## 2. Posisi Halio, tanpa dibagus-baguskan

### Sudah lebih baik atau berbeda
1. **Berani bilang "belum tahu"** dan tidak mengisi kekosongan dengan tebakan (lima keadaan, bukan benar/salah).
2. **Verifikasi positif yang ketat**: hijau hanya dari sumber resmi yang masih berlaku, kutipan dicek ulang oleh kode di halamannya.
3. **Privasi yang bisa diperiksa**: data pribadi dibersihkan sebelum diproses, Radar k-anonim, jumlah byte yang dikirim ekstensi terukur.
4. **Panel cakupan sensor yang jujur**: sumber hidup/basi/mati dan titik buta dinyatakan, bukan disembunyikan.
5. **Satu alur dari keluarga ke analis**: kartu dan suara untuk keluarga; antrean triase dan Radar untuk unit siber.
6. **Tertulis dan teruji untuk kesalahan yang paling merusak** (menuduh kabar benar sebagai hoaks): 0 dari 66 item benar/belum dikenal di dua set uji tim.

### Masih tertinggal (jangan ditutupi di depan juri)
| Celah | Pembanding | Dampak |
|---|---|---|
| Korpus 7 bantahan | Mafindo > 6.000 entri | Hampir semua pesan nyata jatuh ke "belum ada pemeriksaan" |
| Teks saja | CekSumber menerima gambar dan video | Banyak hoaks berbentuk gambar/video |
| Belum ada pengguna nyata | CekSumber, Mafindo, Cofacts | Tidak ada bukti manfaat |
| Evaluasi buatan tim | (semua) | Angka kami optimistis; belum benchmark independen |
| WhatsApp belum diuji dengan Meta | CekSumber hidup di WhatsApp | Telegram siap; WhatsApp belum |
| Belum di-deploy publik (syarat G.1) | (semua yang hidup) | Juri tidak bisa mencoba bila tidak ada tautan |

## 3. Cara menutup celah (dengan sumber ide)
1. **Korpus**: ambil dari Google Fact Check Tools API (ClaimReview, termasuk pemeriksa Indonesia) yang sudah ada kuncinya di kode; impor data terbuka dengan lisensi yang jelas (mis. Cofacts CC BY-SA, periksa syaratnya dulu dan beri atribusi).
2. **Pecah klaim** seperti pipeline Loki (dekomposisi dan layak-periksa) sebelum pencarian; Halio sudah punya ekstraksi klaim sederhana.
3. **RAG atas arsip sendiri** seperti Fátima: sudah menjadi arah agen Gemini kami, dengan tambahan pemeriksaan kutipan oleh kode.
4. **Jangan bersaing di WhatsApp dengan CekSumber**: posisikan Halio sebagai lapisan *keluarga + institusi* (kartu, suara, Radar, triase, tata kelola), dan kanal pertamanya Telegram yang sudah hidup.
5. **Gambar**: ekstensi sudah menyaring gambar di perangkat; teks-dalam-gambar (OCR) lalu masuk alur teks adalah langkah terdekat. Deteksi deepfake **tidak** diklaim.

## 4. Kalimat posisi untuk juri
> Mafindo dan CekSumber menjawab "apakah ini hoaks?" untuk satu orang. Halio menjawab "apakah kita cukup tahu untuk
> bilang?" untuk satu keluarga, lalu mengubah laporan keluarga menjadi sinyal agregat tanpa profil bagi unit siber.

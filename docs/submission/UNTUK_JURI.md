# Halio dalam Lima Menit: Panduan untuk Dewan Juri

> **Jenis:** Rujukan · **Untuk:** juri · [Peta dokumen](../README.md)

Halaman ini memetakan Halio ke lima kriteria penilaian Kartika Cyber Hackathon 2026 (Syarat dan Ketentuan pasal 9.2). Setiap klaim menunjuk ke bukti yang bisa dibuka. Yang belum terbukti ditulis apa adanya.

**Satu kalimat:** Halio adalah teman cek pesan untuk keluarga Indonesia yang menjawab pesan berantai dengan sumber nyata, kartu, dan suara; AI hanya mencari dan membaca bukti, sedangkan vonis diputuskan kode.

**Uji mode luring dalam 30 detik:** buka halaman cek sekali saat online, putus internet, lalu cek pesan lagi. Halio menjawab di perangkat (hanya dari korpus), dengan label "Mode luring". Rincian: [Mode luring](../LURING.md).

**Coba langsung:** [server publik](https://halio.ardelyo.com/cek.html) (build `281dc9e`, rilis [v0.2.0-submission](https://github.com/Ardelyo/halio/releases/tag/v0.2.0-submission)) · [bot Telegram @halioid_bot](https://t.me/halioid_bot) · [uji keamanan langsung](https://halio.ardelyo.com/uji.html) · [versi simulasi di GitHub Pages](https://ardelyo.github.io/halio/) · [video demo (5:01)](https://youtu.be/s2EMpZI2r4g)

## Peta ke kriteria penilaian

| Kriteria (bobot) | Yang Halio tawarkan | Bukti |
|---|---|---|
| **Relevansi dan manfaat** (25%) | Penipuan yang mencatut nama TNI AD (calo rekrutmen, surat kelulusan palsu) menyebar di grup keluarga, tempat bantahan resmi jarang sampai. Halio membawa bantahan bersumber ke sana, dan Radar memberi analis gambaran agregat narasi yang naik. Mode luring membuatnya tetap bisa dipakai di tempat tanpa sinyal atau jaringan tertutup, tanpa data keluar perangkat. | [Relevansi bagi TNI AD](DRAF_DESKRIPSI.md), [Evaluasi Radar untuk TNI AD](../EVALUASI_RADAR_TNI.md) |
| **Inovasi teknis berbasis AI** (25%) | AI dikekang: model hanya memilih kandidat bukti. Kutipan disalin kode dari halaman yang dibuka kode, lalu dicocokkan ulang kata per kata. Kalimat tanpa dukungan kutipan dibuang. Lima jawaban, termasuk "belum ada pemeriksaan". Mesin keputusan yang sama ditulis ulang agar berjalan di perangkat, dijaga identik dengan Python lewat uji paritas. | [Arsitektur](../ARCHITECTURE.md), [Halio Telusur](../ARCHITECTURE_AGENT.md), [Kabar benar bukan hoaks](../TRUE_INFORMATION.md) |
| **Fungsionalitas purwarupa** (25%) | Server publik, bot Telegram, kartu, suara, Telusur, dan Radar berjalan sungguhan. 273 tes otomatis dan evaluasi dijalankan CI pada setiap perubahan. Mode luring diuji di Chrome dengan jaringan diputus ([Mode luring](../LURING.md)). | [Bukti uji demo](../BUKTI_UJI_DEMO.md), [Bukti uji setelah perbaikan](../BUKTI_UJI_SETELAH_PERBAIKAN.md), [Hasil evaluasi](../../eval/RESULTS.md), [CI](../../.github/workflows/ci.yml) |
| **Kelayakan implementasi** (15%) | Satu kontainer Docker. Profil tanpa cloud untuk server satuan (tidak ada data keluar), dan profil cloud opsional. Pencocokan lokal sekitar 1 ms tanpa AI, dan mesin yang sama bisa berjalan di browser tanpa jaringan ([Mode luring](../LURING.md)). | [Profil penerapan](../PROFIL_PENERAPAN.md), [Kesiapan peluncuran](../LAUNCH_READINESS.md), [Skrip deploy](../../deploy/) |
| **Kualitas dokumentasi** (10%) | Arsitektur, privasi, atribusi pihak ketiga, deklarasi bantuan AI, naskah demo, dan daftar keterbatasan tersedia di repo. | [README](../../README.md), [Privasi](../PRIVACY.md), [Atribusi dan deklarasi](../THIRD_PARTY.md), [Checklist pengumpulan](../SUBMISSION_CHECKLIST.md) |

## Angka yang kami pegang

| Angka | Arti | Sumber |
|---|---|---|
| **0 dari 76** | Pernyataan benar atau belum dikenal yang salah dicap "terbukti salah", pada dua set uji tulisan tim (pengembangan dan holdout) | [eval/RESULTS.md](../../eval/RESULTS.md) |
| **0 dari 1.043** | Judul TurnBackHoax berlabel BENAR atau KLARIFIKASI yang salah dicap "terbukti salah", pada sampel publik di luar set tim. Evaluasi ini pernah menemukan satu kesalahan (pesan yang meluruskan hoaks), yang sudah diperbaiki dan dicatat terbuka | [eval/PUBLIC_RESULTS.md](../../eval/PUBLIC_RESULTS.md) |
| **0 dari 197** | Judul TurnBackHoax berlabel BENAR atau KLARIFIKASI yang salah dicap "terbukti salah", diuji ulang dengan korpus 10 entri pada commit beku (13 Nov); batas atas 95%: 1,9% | [eval/PUBLIC_RECHECK.md](../../eval/PUBLIC_RECHECK.md) |
| **88%** | Recall parafrase hoaks pada set holdout | [eval/RESULTS.md](../../eval/RESULTS.md) |
| **0,5 ms** | Median pencocokan lokal tanpa AI (laptop pengembang Windows, 300 pemanggilan, korpus 10 bantahan, jaringan diblokir oleh tes) | [Arsitektur §1](../ARCHITECTURE.md) |
| **5** | Ambang bawaan k-anonimitas Radar (`HALIO_K_ANON`): isi kabar baru hanya disimpan setelah dilaporkan sejumlah itu pelapor berbeda | [Privasi](../PRIVACY.md) |

## Yang belum kami buktikan

- Set uji ditulis tim sendiri, jadi angkanya bukan akurasi dunia nyata.
- Korpus bantahan kurasi masih 10 entri; kabar di luar korpus tidak dikenali di mode luring.
- Mode luring belum diuji di HP fisik atau Safari/iOS, dan Telegram tetap butuh internet.
- Uji dengan pengguna lansia sungguhan belum dilakukan; lembar ujinya sudah siap ([PDF](../LEMBAR_UJI_KELUARGA.pdf)).
- Data Radar pada demo adalah simulasi dan diberi label.
- Halio tidak mendeteksi deepfake dan tidak menilai keaslian foto.

Jawaban untuk sepuluh pertanyaan juri yang diduga ada di [DRAF_DESKRIPSI.md](DRAF_DESKRIPSI.md).

## Materi pengumpulan

| Materi | Lokasi |
|---|---|
| Thumbnail (1200×630) | [thumbnail_kolase.jpg](thumbnail_kolase.jpg) (cadangan: [thumbnail.jpg](thumbnail.jpg)) |
| Screenshot alur penggunaan (5) | [01 Tempel pesan](screenshot_01.png) · [02 Jawaban bersumber](screenshot_02.png) · [03 Dengarkan dan bagikan](screenshot_03.png) · [04 Jujur saat belum tahu](screenshot_04.png) · [05 Radar](screenshot_05.png) |
| Slide | [Halio_Deck_Juri.pdf](../presentasi/Halio_Deck_Juri.pdf): 11 slide cerita dan 10 halaman lampiran teknis (termasuk mode luring) yang dipetakan ke kriteria penilaian, plus QR code ke aplikasi, video, dan repo |
| Video demo | [youtu.be/s2EMpZI2r4g](https://youtu.be/s2EMpZI2r4g) (YouTube, publik, 5:01) |

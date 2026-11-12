# Halio dalam Lima Menit: Panduan untuk Dewan Juri

> **Jenis:** Rujukan · **Untuk:** juri · [Peta dokumen](../README.md)

Halaman ini memetakan Halio ke lima kriteria penilaian Kartika Cyber Hackathon 2026 (Syarat dan Ketentuan pasal 9.2). Setiap klaim menunjuk ke bukti yang bisa dibuka. Yang belum terbukti ditulis apa adanya.

**Satu kalimat:** Halio adalah teman cek pesan untuk keluarga Indonesia yang menjawab pesan berantai dengan sumber nyata, kartu, dan suara; AI hanya mencari dan membaca bukti, sedangkan vonis diputuskan kode.

**Coba langsung:** [server publik](https://34-101-109-211.sslip.io/cek.html) (build `e16d354`) · [bot Telegram @halioid_bot](https://t.me/halioid_bot) · [uji keamanan langsung](https://34-101-109-211.sslip.io/uji.html) · [versi simulasi di GitHub Pages](https://ardelyo.github.io/halio/) · [video demo (5:01)](https://youtu.be/s2EMpZI2r4g)

## Peta ke kriteria penilaian

| Kriteria (bobot) | Yang Halio tawarkan | Bukti |
|---|---|---|
| **Relevansi dan manfaat** (25%) | Penipuan yang mencatut nama TNI AD (calo rekrutmen, surat kelulusan palsu) menyebar di grup keluarga, tempat bantahan resmi jarang sampai. Halio membawa bantahan bersumber ke sana, dan Radar memberi analis gambaran agregat narasi yang naik. | [Relevansi bagi TNI AD](DRAF_DESKRIPSI.md), [Evaluasi Radar untuk TNI AD](../EVALUASI_RADAR_TNI.md) |
| **Inovasi teknis berbasis AI** (25%) | AI dikekang: model hanya memilih kandidat bukti. Kutipan disalin kode dari halaman yang dibuka kode, lalu dicocokkan ulang kata per kata. Kalimat tanpa dukungan kutipan dibuang. Lima jawaban, termasuk "belum ada pemeriksaan". | [Arsitektur](../ARCHITECTURE.md), [Halio Telusur](../ARCHITECTURE_AGENT.md), [Kabar benar bukan hoaks](../TRUE_INFORMATION.md) |
| **Fungsionalitas purwarupa** (25%) | Server publik, bot Telegram, kartu, suara, Telusur, dan Radar berjalan sungguhan. 265 tes otomatis dan evaluasi dijalankan CI pada setiap perubahan. | [Bukti uji demo](../BUKTI_UJI_DEMO.md), [Bukti uji setelah perbaikan](../BUKTI_UJI_SETELAH_PERBAIKAN.md), [Hasil evaluasi](../../eval/RESULTS.md), [CI](../../.github/workflows/ci.yml) |
| **Kelayakan implementasi** (15%) | Satu kontainer Docker. Profil tanpa cloud untuk server satuan (tidak ada data keluar), dan profil cloud opsional. Pencocokan lokal sekitar 1 ms tanpa AI. | [Profil penerapan](../PROFIL_PENERAPAN.md), [Kesiapan peluncuran](../LAUNCH_READINESS.md), [Skrip deploy](../../deploy/) |
| **Kualitas dokumentasi** (10%) | Arsitektur, privasi, atribusi pihak ketiga, deklarasi bantuan AI, naskah demo, dan daftar keterbatasan tersedia di repo. | [README](../../README.md), [Privasi](../PRIVACY.md), [Atribusi dan deklarasi](../THIRD_PARTY.md), [Checklist pengumpulan](../SUBMISSION_CHECKLIST.md) |

## Angka yang kami pegang

| Angka | Arti | Sumber |
|---|---|---|
| **0 dari 66** | Pernyataan benar atau belum dikenal yang salah dicap "terbukti salah", pada dua set uji tulisan tim (pengembangan dan holdout) | [eval/RESULTS.md](../../eval/RESULTS.md) |
| **88%** | Recall parafrase hoaks pada set holdout | [eval/RESULTS.md](../../eval/RESULTS.md) |
| **0,9 ms** | Median pencocokan lokal tanpa AI (laptop pengembang, korpus 7 bantahan) | [Arsitektur §1](../ARCHITECTURE.md) |
| **5** | Ambang bawaan k-anonimitas Radar (`HALIO_K_ANON`): isi kabar baru hanya disimpan setelah dilaporkan sejumlah itu pelapor berbeda | [Privasi](../PRIVACY.md) |

## Yang belum kami buktikan

- Set uji ditulis tim sendiri, jadi angkanya bukan akurasi dunia nyata.
- Korpus bantahan kurasi masih 7 entri.
- Uji dengan pengguna lansia sungguhan belum dilakukan; lembar ujinya sudah siap ([PDF](../LEMBAR_UJI_KELUARGA.pdf)).
- Data Radar pada demo adalah simulasi dan diberi label.
- Halio tidak mendeteksi deepfake dan tidak menilai keaslian foto.

Jawaban untuk sepuluh pertanyaan juri yang diduga ada di [DRAF_DESKRIPSI.md](DRAF_DESKRIPSI.md).

## Materi pengumpulan

| Materi | Lokasi |
|---|---|
| Thumbnail (1200×630) | [thumbnail_kolase.jpg](thumbnail_kolase.jpg), alternatif [thumbnail.jpg](thumbnail.jpg) |
| Screenshot alur penggunaan (5) | [01 Tempel pesan](screenshot_01.png) · [02 Jawaban bersumber](screenshot_02.png) · [03 Dengarkan dan bagikan](screenshot_03.png) · [04 Jujur saat belum tahu](screenshot_04.png) · [05 Radar](screenshot_05.png) |
| Slide | [Halio_Presentasi_v2.pdf](../presentasi/Halio_Presentasi_v2.pdf) |
| Video demo | [youtu.be/s2EMpZI2r4g](https://youtu.be/s2EMpZI2r4g) (YouTube, publik, 5:01) |

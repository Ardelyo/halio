# Kesiapan demo dan peluncuran

Dokumen ini memisahkan pekerjaan teknis yang sudah diverifikasi dari risiko yang masih memerlukan manusia, kredensial, perangkat, atau lingkungan produksi.

## Gerbang demo

- Jalankan seluruh tes dan evaluasi dari clone bersih.
- Uji alur web: klaim dikenal, klaim benar pada topik yang sama, klaim belum dikenal, kartu, suara/fallback, banding, eskalasi, dan hasil kedaluwarsa.
- Uji Telegram dengan akun uji; jangan memakai pesan pengguna nyata.
- Uji alur analis di Radar: buka eskalasi/banding, tulis respons, kirim melalui kanal yang mendukung, dan periksa riwayat. Tiket hanya ditutup setelah balasan kanal berhasil; pencatatan tanpa pengiriman memerlukan tindak lanjut manual. Lindungi API publik dengan `RADAR_TOKEN`. CLI `scripts/review.py` tetap tersedia di server tepercaya.
- Tampilkan data Radar simulasi dengan label. Jangan menyebut deteksi deepfake, cakupan semua platform, atau akurasi dunia nyata.
- Siapkan rekaman cadangan dan uji semua tautan dari jendela privat.

## Gerbang peluncuran publik yang masih terbuka

| Prioritas | Risiko yang tersisa | Bukti yang diperlukan |
|---|---|---|
| Kritis | Evaluasi hanya 108 item buatan tim (dev 52 + holdout 56: 66 pernyataan benar/belum dikenal, 32 parafrase hoaks, 10 opini/sapaan) dan tujuh bantahan | Set held-out independen, data nyata yang dianonimkan, metrik per kategori dan interval kepercayaan |
| Kritis | Pemeriksaan hukum UU PDP belum dilakukan | Dasar pemrosesan, persetujuan, hak pengguna, prosesor pihak ketiga, respons insiden dan retensi ditinjau ahli hukum |
| Tinggi | WhatsApp belum diuji dengan Meta | Uji sandbox signature, retry, deduplikasi, outbound media, kegagalan API dan izin bisnis |
| Tinggi | LLM dan ClaimReview belum dievaluasi live | Ukur cakupan, kegagalan grounding, injeksi prompt, biaya dan latensi pada set independen |
| Tinggi | Rate limit dan cache lokal hanya berlaku per proses | Batas pada reverse proxy/gateway dan strategi cache bersama sebelum multi-instance |
| Tinggi | UI analis memakai satu token Radar bersama, bukan akun individual | Akun dan peran individual, rotasi token, audit terikat identitas, kontrol akses server dan prosedur operasional |
| Tinggi | K-anonimitas bukan jaminan anonimitas | Tinjauan privasi, uji korelasi/serangan komposisi, persetujuan dan minimisasi data tambahan |
| Sedang | Akurasi NudeNet dan kompatibilitas DOM belum diukur | Safe-set seimbang, bias/false-positive report, uji situs nyata, model berversi dan deklarasi Chrome Web Store |
| Sedang | Aksesibilitas lansia belum diuji pengguna | Audit WCAG dan sesi usability dengan pengguna lansia Indonesia |
| Sedang | Operasi produksi belum dibuktikan | Load test, HTTPS edge, monitoring alert, backup/restore, rollback dan latihan insiden |

## Referensi praktik

- OWASP API Security Top 10: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- IFCN Code of Principles: https://www.ifcncodeofprinciples.poynter.org/know-more/the-commitments-of-the-code-of-principles
- W3C, kebutuhan pengguna lansia: https://www.w3.org/WAI/older-users/
- Chrome Web Store publishing: https://developer.chrome.com/docs/webstore/publish

Referensi ini adalah baseline rekayasa dan editorial, bukan sertifikasi Halio.

## Catatan setelah audit 28 Okt – 2 Nov

- Guard tuduhan palsu diperketat dan diuji pada dua set (`eval/testset.jsonl`, `eval/holdout.jsonl`): 0 tuduhan palsu di kedua set. Holdout tidak sepenuhnya bersih karena satu cue koreksi ditambahkan setelah melihat satu kegagalannya; set independen dari luar tim tetap diperlukan.
- Agen web dan LLM tidak bisa lagi mengubah pesan yang meluruskan hoaks ("itu hoaks, BMKG membantah") menjadi vonis hoaks.
- ID pelapor dari klien tidak dipercaya. Hanya bot kami, dengan `HALIO_CHANNEL_KEY` yang sama di API dan bot, boleh menyebut pelapor (`tg:<chat>`); tanpa itu balasan eskalasi Telegram tidak bisa diarahkan dan semua pengguna Telegram terhitung satu pelapor.
- Di belakang reverse proxy set `HALIO_TRUST_PROXY=1`, kalau tidak semua klien berbagi satu batas laju.
- Radar, antrean review, dan data sensor tertutup untuk akses jarak jauh kecuali `RADAR_TOKEN` diisi atau `HALIO_RADAR_PUBLIC=1`.
- Model: `gemini-3.5-flash-lite` di lokasi `global` (bukan `us-central1`); parameter `thinking_level="MINIMAL"` menggantikan `thinking_budget`. Belum diuji langsung ke Vertex dari sandbox ini.

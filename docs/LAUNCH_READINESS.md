# Kesiapan demo dan peluncuran

Dokumen ini memisahkan pekerjaan teknis yang sudah diverifikasi dari risiko yang masih memerlukan manusia, kredensial, perangkat, atau lingkungan produksi.

## Gerbang demo

- Jalankan seluruh tes dan evaluasi dari clone bersih.
- Uji alur web: klaim dikenal, klaim benar pada topik yang sama, klaim belum dikenal, kartu, suara/fallback, banding, eskalasi, dan hasil kedaluwarsa.
- Uji Telegram dengan akun uji; jangan memakai pesan pengguna nyata.
- Jalankan `python scripts/review.py list escalations` dan `python scripts/review.py resolve escalations ID --response "Jawaban pemeriksa"` pada server tepercaya. Tiket hanya ditutup setelah balasan kanal berhasil; `--no-send` memerlukan tindak lanjut manual.
- Tampilkan data Radar simulasi dengan label. Jangan menyebut deteksi deepfake, cakupan semua platform, atau akurasi dunia nyata.
- Siapkan rekaman cadangan dan uji semua tautan dari jendela privat.

## Gerbang peluncuran publik yang masih terbuka

| Prioritas | Risiko yang tersisa | Bukti yang diperlukan |
|---|---|---|
| Kritis | Evaluasi hanya 32 kasus buatan tim dan tujuh bantahan | Set held-out independen, data nyata yang dianonimkan, metrik per kategori dan interval kepercayaan |
| Kritis | Pemeriksaan hukum UU PDP belum dilakukan | Dasar pemrosesan, persetujuan, hak pengguna, prosesor pihak ketiga, respons insiden dan retensi ditinjau ahli hukum |
| Tinggi | WhatsApp belum diuji dengan Meta | Uji sandbox signature, retry, deduplikasi, outbound media, kegagalan API dan izin bisnis |
| Tinggi | LLM dan ClaimReview belum dievaluasi live | Ukur cakupan, kegagalan grounding, injeksi prompt, biaya dan latensi pada set independen |
| Tinggi | Rate limit dan cache lokal hanya berlaku per proses | Batas pada reverse proxy/gateway dan strategi cache bersama sebelum multi-instance |
| Tinggi | Autentikasi reviewer mengandalkan akses lokal server | Kontrol akses server, akun individual, audit dan prosedur operasional; UI reviewer berautentikasi untuk penggunaan non-teknis |
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

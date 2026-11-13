# Halio Telusur: swarm investigasi (arsitektur dan batas jujur)

> **Jenis:** Rujukan · **Untuk:** juri, analis, dan pengembang · [Peta dokumen](README.md)

Disusun 7 Nov 2026. Hasil ukur ada di `eval/AGENT_RESULTS.md` (dibuat oleh `eval/eval_agent.py` di server, data nyata).

## Untuk siapa
| Pengguna | Pintu masuk | Yang diterima |
|---|---|---|
| Keluarga, nenek, masyarakat | Telegram (tombol 🔬 atau `/telusur`), `cek.html` | Satu kalimat vonis dengan bahasa sehari-hari, 2–3 hal yang perlu diketahui, "sudah beredar sejak …", siapa yang sudah membantah, saran, tombol **Dengarkan** |
| Analis siber / TNI AD | `laporan.html` (tampilan analis), Radar → **Brief harian** | Bukti bernomor dengan kutipan, linimasa, kemunculan paling awal, tanggapan resmi pertama, versi kalimat, cakupan sumber, hasil gambar terbalik, kontribusi tiap agen, titik buta, metodologi dan anggaran |

Satu laporan, dua tampilan. Tampilan keluarga dibangun dari laporan yang sudah diperiksa (`investigate/keluarga.py`), tanpa panggilan model baru dan tanpa fakta baru.

## Alur
```
pesan / foto
  └─ planner (Gemini): 8–12 kueri + "inti klaim" (hanya boleh memakai kata dari pesan; dicek kode)
  └─ SWARM, paralel, satu kumpulan kandidat bersama (dedup per URL kanonik)
       Perencana · Penelusur pemeriksa fakta · Penelusur sumber resmi · Penelusur media
       Penelusur arsip (sensor realtime + GDELT) · Penelusur gambar (Cloud Vision) · ClaimReview
  └─ kode membuka halaman (aman SSRF, tanpa skrip, ≤ 60 halaman, 8 paralel) dan MENYALIN kutipan
  └─ Gemini menilai hubungan tiap kutipan BERNOMOR (mendukung / membantah / konteks)
  └─ KODE memutuskan status (evidence.decide)
  └─ Penelusur asal-usul: putaran kedua bila waktu tersisa
  └─ kode: linimasa, kemunculan paling awal, tangkapan pertama Wayback, varian kalimat, cakupan
  └─ Gemini menulis kalimat laporan; KODE membuang kalimat yang nomor sumbernya tidak ada,
     katanya tidak beririsan dengan kutipan, atau memuat angka/tanggal yang tidak ada di kutipan
```
Anggaran keras: 10 kueri umum + 5 kueri peran + 4 kueri asal-usul, 60 halaman, 150 detik. Batas harian
`HALIO_AGENT_DAILY_CAP` (bawaan 60) dan per pelapor `HALIO_AGENT_PER_REPORTER` (bawaan 8).

## Brief harian (Radar)
Setiap pagi (06.00 WIB, `HALIO_BRIEF=1`) atau dengan tombol: berita, cek fakta, dan feed resmi (termasuk **TNI AD
`tniad.mil.id`** dan **Kemhan**) 48 jam terakhir → saring topik → kelompokkan judul yang mirip → skor (sumber berbeda,
pemeriksa fakta terlibat, kata hoaks, kebaruan) → **tiga narasi teratas ditelusuri swarm** → tampil di Radar dengan
vonis, ringkasan, asal paling awal, dan tautan laporan. Topik: `tni` (TNI AD dan pertahanan) dan `umum` (yang sedang diperiksa pemeriksa fakta).

## Aturan keselamatan vonis
- Agen tidak pernah memberi vonis dan tidak pernah menulis kutipan.
- **Bantahan apa pun dari sumber resmi atau pemeriksa fakta memblokir hijau.** (Ditemukan saat uji: kalimat Polri yang hanya
  merujuk artikel cek fakta dinilai "mendukung", sehingga hoaks bansos sempat hijau. Sekarang dicegah dan diuji.)
- Kutipan dari halaman yang membahas topik sebagai hoaks tidak bisa dihitung "mendukung".
- Akibatnya hoaks yang jelas sering keluar 🟠 "dibantah untuk versi yang mirip", bukan 🔴: aman, analis membaca bantahannya.

## Tata kelola (konteks TNI AD)
Narasi dan klaim, **bukan orang**. Tidak ada profil warga, akun, atau prajurit; tidak menilai pendapat politik; hanya
sumber publik; statistik agregat; tidak ada tindakan tanpa persetujuan manusia. Foto dari pengguna hanya disimpan di
memori selama penelusuran dan tidak ditulis ke basis data. Lihat juga `docs/PRIVACY.md`.

## Batas yang jujur
- **Web terbuka saja.** Grup WhatsApp/Telegram privat, TikTok, Instagram, Facebook, X tidak ditelusuri; "asal-usul" berarti
  kemunculan paling awal yang *ditemukan*, bukan pasti asalnya.
- **Situs menolak server.** Pada uji di VM sekitar sepertiga sampai separuh halaman menolak dibuka (HTTP 403/202 tantangan bot).
  Kami tidak menyamar sebagai peramban; halaman itu ditulis sebagai titik buta.
- **Korpus bantahan kurasi masih kecil (10 entri).** Kekuatan datang dari pencarian langsung, bukan dari korpus.
- **Kabar yang sangat baru** (jam-jaman) biasanya belum ditulis siapa pun: hasil ⚪ dengan tautan pencarian.
- **Gambar terbalik** aktif hanya setelah Cloud Vision API diaktifkan di proyek; ia menunjukkan di mana gambar pernah muncul,
  bukan apakah gambar asli. Deteksi deepfake/AI tidak ada (SynthID tanpa API publik yang terkonfirmasi).
- **Biaya**: setiap investigasi ±20 panggilan model ber-grounding. Harga grounding per permintaan tidak kami verifikasi;
  pasang peringatan anggaran.
- **Video** belum.

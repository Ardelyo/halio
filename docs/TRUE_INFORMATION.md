# Kalau informasinya benar, bagaimana?

> **Jenis:** Rujukan · **Untuk:** juri dan pengembang · [Peta dokumen](README.md)

Singkat: **kabar yang benar bukan hoaks.** Halio tidak boleh menyebutnya begitu, dan tidak boleh pula
menyatakan "pasti benar" hanya karena tidak menemukan bantahan.

## Tiga jenis "kabar bermasalah" (Wardle & Derakhshan, Council of Europe, 2017)
| Jenis | Isi | Contoh | Perlakuan Halio |
|---|---|---|---|
| Misinformasi | Salah, disebarkan tanpa niat jahat | Pesan berantai gempa tanggal tertentu | Terbukti salah, bila ada bantahan bersumber |
| Disinformasi | Salah, disebarkan dengan sengaja | Video palsu "bansos dari Presiden" | Terbukti salah, plus nama triknya |
| Malinformasi | **Benar**, tetapi dipakai untuk merugikan atau dikeluarkan dari konteks | Berita lama dipajang seolah baru; data pribadi yang bocor; rincian operasional yang sensitif | Bukan "hoaks". Halio menandai konteksnya (tanggal, masa berlaku), bukan benar/salahnya |

## Lima keadaan jawaban Halio
1. **Terbukti salah**: ada bantahan dari pemeriksa fakta atau sumber resmi, dengan tautan.
2. **Sejalan dengan sumber**: hanya bila sumber *resmi*, *masih berlaku*, memuat kutipan yang mendukung *seluruh*
   klaim, kutipan itu ada persis di halamannya (dicek ulang oleh backend, bukan oleh model), dan tidak ada
   bukti lain yang bertentangan. Ini bukan stempel "pasti benar": pengguna tetap diminta mengecek tanggal dan konteks.
3. **Dilaporkan media**: beberapa media independen memberitakannya dan tidak ada yang membantah. Ini laporan media,
   bukan pemeriksaan fakta, jadi Halio meminta pengguna menyebut sumbernya dan mengecek tanggalnya.
4. **Halio tidak yakin**: topik mirip tetapi inti klaim berbeda, bukti bertentangan, kedaluwarsa, atau pesan hanya meluruskan hoaks.
5. **Belum ada pemeriksaan**: tidak ada sumber yang cocok. "Belum tahu" adalah jawaban yang sah.

## Mengapa begitu
- **Tidak ada bantahan ≠ benar.** Kebanyakan kabar baru memang belum diperiksa siapa pun. Melabeli itu "aman" akan
  menjadi kesalahan yang lebih berbahaya daripada menahan jawaban.
- **Topik sama ≠ klaim sama.** "Rekrutmen TNI AD tidak dipungut biaya" (benar, resmi) berbagi hampir semua kata dengan
  "jalur titipan bayar sekian juta" (penipuan). Karena itu ada penjaga inti klaim (`syarat`), pengecekan
  negasi dan "biaya gratis", dan pengecekan pesan yang justru meluruskan hoaks.
- **Benar tetapi kedaluwarsa.** Sumber resmi punya `valid_from` / `valid_until` dan wilayah. Pendaftaran yang sudah
  ditutup tidak boleh tampil hijau.
- **Model tidak memberi vonis.** Model hanya mencari dan mengklasifikasi; setiap URL dan kutipan diambil dan dicocokkan
  ulang oleh kode kami. Bila model dan kode tidak sepakat, jawabannya turun ke "tidak yakin".

## Batas yang jujur
Halio belum menilai konteks visual (foto lama dipajang sebagai baru), belum menilai video atau suara sintetis,
dan korpusnya masih kecil. Pada pesan seperti itu jawabannya "tidak yakin" atau "belum ada pemeriksaan", dan
tombol "tanya pemeriksa manusia" tersedia.

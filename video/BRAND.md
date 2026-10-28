# Halio · Identitas Merek (v1, 28 Okt 2026)

Satu sistem untuk video, aplikasi, Kartu Halio, slide, dan thumbnail.

## Gagasan
**Padang rumput yang tenang, bukan ruang kontrol yang menakutkan.** Halio menenangkan keluarga, lalu
meluruskan kabar. Foto padang yang luas dan hening dipadukan dengan tipografi editorial yang tegas.

## Warna
| Token | Hex | Pakai untuk |
|---|---|---|
| Royal Blue | `#014BAA` | Warna utama: latar merek, tombol, aksen kata |
| Light Cream | `#F8F3F0` | Latar terang, teks di atas biru/foto |
| Ink | `#0E1726` | Teks utama, latar gelap |
| Sun | `#FFC83D` | Titik pada logo dan wordmark, sorotan kecil |
| Meadow | `#3F7D26` | Padang rumput, tanda "aman" |
| Sky | `#9CC3EB` | Langit, aksen sekunder |
| Confetti | `#8B5CF6` ungu · `#FF8A3D` jingga · `#2FBF71` hijau · `#FFC83D` kuning | Hanya untuk ilustrasi "pesan berantakan" |
| Vonis | Terbukti salah `#B42318` · Tidak yakin `#B54708` · Belum ada pemeriksaan `#475467` | Tiga keadaan, selalu dengan label teks (sama dengan aplikasi dan Kartu Halio) |

## Tipografi (semua SIL OFL, lihat `fonts/LICENSES.md`)
| Peran | Font | Aturan |
|---|---|---|
| Judul editorial | **Instrument Serif** (reguler + *italic*) | Huruf kecil boleh; kata kunci dalam *italic* Royal Blue |
| Pernyataan & angka | **Archivo** ExtraBold–Black, lebar 112–125 | HURUF KAPITAL, tracking rapat (−2%) |
| Teks, UI, subtitle | **Inter** 500–700 | Kalimat biasa |
| Label mikro | **Inter** 600, kapital, tracking +18% | Label scene, sumber, metadata |

## Logo
- **Tanda:** gelembung pesan berwajah, senyumnya tanda centang ("sudah dicek"), dengan titik Sun. File: `assets/halio-mark.svg`.
- **Wordmark:** `halio.` dalam Instrument Serif huruf kecil; titiknya Sun di latar gelap/biru, Royal Blue di latar terang.
- Ruang kosong minimal = tinggi titik. Jangan diberi bayangan, gradasi, atau diputar.

## Gerak
Teks muncul dari blur ke tajam (0,6–0,9 dtk, ease-out), kata per kata untuk kalimat penting. Kartu UI
masuk dengan geser 24 px + bayangan lembut. Satu warna aksen per layar. Label scene kecil di kiri atas.

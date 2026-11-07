"""Build halio_deck_v2.html from the 14-slide deck (kept slides) plus the new slides below, then number everything.

    python docs/presentasi/build_deck.py
    # PDF (1920x1080, one slide per page):
    msedge --headless --disable-gpu --no-pdf-header-footer --print-to-pdf=Halio_Presentasi_v2.pdf file:///.../halio_deck_v2.html

Every number on the new slides comes from a measured result in this repository (eval/AGENT_RESULTS.md, the server logs and the
test suite) as of 8 Nov 2026. Nothing here is a target presented as a result.
"""

import re
from pathlib import Path

HERE = Path(__file__).parent
old = (HERE / "halio_deck.html").read_text(encoding="utf-8")
head = old[: old.index('<div class="deck" id="deck">') + len('<div class="deck" id="deck">')]
# The screen script scales the deck to the window (transform on .deck). A headless print runs that script first with a small
# window, so without this the printed pages hold the slide at ~40% size in the top-left corner. Printing must ignore it.
PRINT_FIX = "@media print{.deck{transform:none!important;position:static!important;left:auto!important;top:auto!important;width:1920px!important}}"
head = head.replace("</style>", PRINT_FIX + "\n</style>", 1)
tail = old[old.index('</div>\n<div class="hud">'):]
old_slides = re.findall(r"<section class=\"slide.*?</section>", old, flags=re.S)
assert len(old_slides) == 14, len(old_slides)
S = {i + 1: s for i, s in enumerate(old_slides)}

FOOT = '<div class="foot"><span>Halio · Saring dulu, baru sharing</span><span><b>@@</b> / @@</span></div>'

# ---- kept slides, lightly updated -----------------------------------------------------------------------------
cover = S[1].replace(
    '<p class="lede" style="max-width:1000px">Teman cek pesan untuk keluarga Indonesia.</p>',
    '<p class="lede" style="max-width:1200px">Satu mesin bukti, <b style="color:#fff">dua pintu</b>: keluarga yang ingin jawaban sederhana, '
    'dan analis yang butuh investigasi.</p>',
).replace("Prototipe · bukan produk jadi", "Prototipe hidup · diperbarui 8 Nov 2026")

cara_pakai = S[5].replace(
    '<p>Kartu untuk grup keluarga, atau pesan suara.</p>', '<p>Kartu untuk grup keluarga, atau pesan suara dengan suara manusia.</p>'
).replace(
    "Pesan, foto, atau suara yang meragukan ke Halio di Telegram.", "Pesan, foto, atau pesan suara yang meragukan ke Halio di Telegram."
).replace(
    '<b>Halio teman bertanya,</b> bukan pengganti penilaian Anda.',
    '<b>Halio teman bertanya,</b> bukan pengganti penilaian Anda. Ingin tahu lebih jauh? Satu tombol <b>🔬 Telusuri mendalam</b>.',
)

cara_kerja = S[8].replace(
    '<b>Halaman web tidak bisa menyuruh Halio</b> memutuskan sesuatu. Perintah di dalam halaman hanya dianggap teks.',
    '<b>Halaman web tidak bisa menyuruh Halio</b> memutuskan sesuatu. Dan setiap kalimat laporan diperiksa ulang oleh kode: '
    'yang tidak didukung kutipan dibuang.',
)

# ---- new slides ----------------------------------------------------------------------------------------------
apa_itu = f'''<section class="slide">
  <div class="kicker">## · Halio itu apa</div>
  <h2>Satu mesin bukti, <em>dua pintu.</em></h2>
  <div class="row" style="margin-top:56px;gap:30px;align-items:stretch;flex:1;margin-bottom:70px">
    <div class="card" style="flex:1;border-top:10px solid var(--sun);display:flex;flex-direction:column">
      <div class="kicker" style="font-size:22px;color:var(--ragu)">Pintu 1 · Keluarga</div>
      <h3 style="margin-top:12px;font-size:46px">Teman cek pesan</h3>
      <p>Telegram dan web. Teruskan pesan, foto, atau suara. Dapat jawaban bahasa sehari-hari, suara, dan kartu untuk grup keluarga.</p>
      <p class="note" style="margin-top:auto">Untuk Nenek, orang tua, dan siapa saja.</p>
    </div>
    <div class="arrow" style="color:var(--blue)">⇄</div>
    <div class="card" style="flex:1.1;background:var(--blue);color:#fff;border-color:transparent;display:flex;flex-direction:column">
      <div class="kicker" style="font-size:22px;color:var(--sun)">Mesin Bukti</div>
      <h3 style="margin-top:12px;font-size:46px;color:#fff">AI mencari. Kode memutuskan.</h3>
      <p style="color:#DCE8F8">Kutipan disalin kata per kata oleh kode. Vonis ditetapkan aturan atas tingkat sumber. "Belum tahu" adalah jawaban yang sah.</p>
      <p class="note" style="margin-top:auto;color:#9FBDE6">Bukan sekadar pendeteksi hoaks: ia menyusun bukti.</p>
    </div>
    <div class="arrow" style="color:var(--blue)">⇄</div>
    <div class="card" style="flex:1;border-top:10px solid var(--blue);display:flex;flex-direction:column">
      <div class="kicker" style="font-size:22px">Pintu 2 · Analis</div>
      <h3 style="margin-top:12px;font-size:46px">Telusur dan Radar</h3>
      <p>Swarm agen menelusuri satu klaim jadi laporan bernomor, dengan linimasa dan asal-usul. Radar menyusun brief harian narasi TNI AD.</p>
      <p class="note" style="margin-top:auto">Narasi dan klaim, bukan orang.</p>
    </div>
  </div>
  {FOOT}
</section>'''

swarm = f'''<section class="slide deep">
  <div class="kicker">## · Halio Telusur</div>
  <h2>Tujuh agen, <em>bekerja bersamaan.</em></h2>
  <div class="row" style="margin-top:36px;gap:20px;flex-wrap:wrap">
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Perencana</h3><p style="font-size:22px">Menyusun kueri pencarian yang beragam.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Pemeriksa fakta</h3><p style="font-size:22px">TurnBackHoax, Kompas, Liputan6, Tempo.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Sumber resmi</h3><p style="font-size:22px">.go.id, .mil.id, situs TNI AD dan Kemhan.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Media</h3><p style="font-size:22px">Pemberitaan dan salinan kantor berita.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Arsip</h3><p style="font-size:22px">Bantahan lama dan feed sensor waktu nyata.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Asal-usul</h3><p style="font-size:22px">Kemunculan paling awal dan salinan Wayback.</p></div>
    <div class="card" style="flex:1 1 22%;padding:22px 28px"><h3 style="font-size:30px">Gambar</h3><p style="font-size:22px">Pencarian gambar terbalik (Cloud Vision).</p></div>
  </div>
  <div class="row" style="margin-top:28px;gap:30px">
    <div class="card grow" style="text-align:center;padding:22px"><div class="big" style="color:var(--sun);font-size:96px">±40<span style="font-size:40px"> detik</span></div><p style="font-size:24px">median satu penelusuran</p></div>
    <div class="card grow" style="text-align:center;padding:22px"><div class="big" style="color:var(--sun);font-size:96px">±38</div><p style="font-size:24px">halaman dibuka per klaim</p></div>
    <div class="card grow" style="text-align:center;padding:22px"><div class="big" style="color:var(--sun);font-size:96px">1</div><p style="font-size:24px">kumpulan bukti bersama, tanpa duplikat</p></div>
  </div>
  <p class="note" style="margin-top:14px;font-size:20px">Terukur pada 18 klaim nyata di server, 7 Nov 2026. Angka tepat di eval/AGENT_RESULTS.md. Pencarian gambar aktif setelah Cloud Vision dinyalakan.</p>
  {FOOT}
</section>'''

laporan = f'''<section class="slide">
  <div class="kicker">## · Laporan untuk analis</div>
  <h2>Bukan vonis. <em>Dosir yang bisa diaudit.</em></h2>
  <div class="row" style="margin-top:36px;gap:32px;align-items:flex-start;margin-bottom:0">
    <div class="card" style="flex:1.15;padding:30px 40px">
      <div class="kicker" style="font-size:20px">Laporan Halio Telusur</div>
      <p style="font-family:var(--serif);font-size:44px;line-height:1.2;color:var(--ink);margin:14px 0">“Ada jalur khusus masuk TNI AD dijamin lulus dengan membayar uang.”</p>
      <div class="pill" style="background:var(--ragu-bg);color:var(--ragu);font-size:26px;padding:10px 24px">🟠 Tidak yakin · dibantah untuk versi yang mirip</div>
      <div style="margin-top:26px;border-left:4px solid var(--salah);padding-left:20px"><p style="font-size:26px"><b style="color:var(--ink)">[1] Kompas.com</b> · membantah<br><i>“…telah berulang kali mengingatkan bahwa tidak ada jalur khusus…”</i></p></div>
      <div style="margin-top:14px;border-left:4px solid var(--salah);padding-left:20px"><p style="font-size:26px"><b style="color:var(--ink)">[2] Jawa Pos</b> · membantah<br><i>“…tidak benar jika ada yang mengatakan bahwa menjadi prajurit TNI AD harus membayar…”</i></p></div>
      <p class="note">Potongan kata per kata dari hasil nyata di server (7 Nov 2026), disalin oleh kode. Nomor sumber mengarah ke tautan yang bisa dibuka.</p>
    </div>
    <div class="col" style="flex:1;gap:16px">
      <div class="card" style="padding:20px 34px"><h3 style="font-size:30px">Linimasa</h3><p style="font-size:26px">Urutan tanggal dari halaman, sensor, GDELT, dan tangkapan pertama Internet Archive.</p></div>
      <div class="card" style="padding:20px 34px"><h3 style="font-size:30px">Kemunculan paling awal yang <u>ditemukan</u></h3><p style="font-size:26px">Batas bawah, bukan klaim asal-usul pasti.</p></div>
      <div class="card" style="padding:20px 34px"><h3 style="font-size:30px">Versi kalimat</h3><p style="font-size:26px">Bagaimana klaim bermutasi atau disalin antarsitus.</p></div>
      <div class="card" style="padding:20px 34px;background:var(--sun-soft);border-color:transparent"><h3 style="font-size:30px;color:var(--ragu)">Titik buta</h3><p style="font-size:26px;color:var(--ink)">Grup WhatsApp privat, media sosial, halaman berbayar, situs yang memblokir.</p></div>
    </div>
  </div>
  {FOOT}
</section>'''

nenek = f'''<section class="slide deep">
  <div class="row center" style="gap:90px;height:100%">
    <div class="col" style="flex:1">
      <div class="kicker">## · Untuk Nenek</div>
      <h2 style="font-size:96px">Hasil yang <em>mudah didengar.</em></h2>
      <ul class="clean" style="margin-top:40px">
        <li><b>Huruf besar</b>, satu kalimat jawaban di atas.</li>
        <li>Tombol <b>🔊 Dengarkan</b> dengan suara Indonesia alami.</li>
        <li>Sapaan sesuai pilihan: <b>“Nenek, …”</b></li>
        <li><b>Saran</b> yang jelas: tahan dulu, tanyakan ke cucu.</li>
      </ul>
      <p class="note">Tampilan keluarga dibangun dari laporan analis yang sama, tanpa fakta baru.</p>
    </div>
    <div class="phone"><div class="screen">
      <div class="bar"><i></i>Halio</div>
      <div class="msgs">
        <div class="m bot" style="font-size:31px"><span class="tag" style="background:var(--ragu-bg);color:var(--ragu)">🟠 Nenek, belum pasti</span><br><b>Kabar yang sangat mirip sudah dinyatakan tidak benar oleh Kompas.com.</b><br><br>Sudah beredar sejak Maret 2025.<br><br><b>Sebaiknya:</b> tahan dulu, jangan diteruskan. Tanyakan ke anak atau cucu.
          <div class="btns"><span>🔊 Dengarkan</span><span>🔬 Telusuri</span></div></div>
      </div>
    </div></div>
  </div>
  <div class="foot"><span>Tampilan contoh dari hasil nyata · kalimat disederhanakan</span><span><b>@@</b> / @@</span></div>
</section>'''

radar = f'''<section class="slide">
  <div class="kicker">## · Untuk unit siber</div>
  <h2>Brief harian, <em>bukan pengawasan.</em></h2>
  <div class="row" style="margin-top:44px;gap:36px;align-items:stretch;flex:1;margin-bottom:70px">
    <div class="card" style="flex:1.2;padding:34px 44px">
      <div class="kicker" style="font-size:20px">Radar · Brief harian TNI AD</div>
      <p class="note" style="margin:8px 0 18px">Setiap pagi 06.00 WIB · 1.512 berita dibaca dalam 48 jam · 65 cocok topik</p>
      <div class="st" style="background:var(--belum-bg);padding:14px 26px"><div class="ic" style="background:var(--blue);width:58px;height:58px;font-size:30px">1</div><div><h4 style="font-size:30px">Ragam hoaks menerpa TNI</h4><p style="font-size:22px">skor 9 · pemeriksa fakta terlibat · ditelusuri</p></div></div>
      <div class="st" style="background:var(--belum-bg);padding:14px 26px"><div class="ic" style="background:var(--blue);width:58px;height:58px;font-size:30px">2</div><div><h4 style="font-size:30px">Menhan kumpulkan pejabat Kemhan</h4><p style="font-size:22px">skor 8 · 2 sumber · ditelusuri</p></div></div>
      <div class="st" style="background:var(--belum-bg);padding:14px 26px"><div class="ic" style="background:var(--blue);width:58px;height:58px;font-size:30px">3</div><div><h4 style="font-size:30px">Lahan eks tambang ke Kopassus</h4><p style="font-size:22px">skor 8 · 2 sumber · ditelusuri</p></div></div>
      <p class="note">Tampilan dari brief nyata di server (7 Nov 2026). Tiga narasi teratas ditelusuri swarm otomatis.</p>
    </div>
    <div class="col" style="flex:1;gap:22px">
      <div class="card" style="padding:28px 38px"><h3 style="font-size:34px">Sensor 23 sumber publik</h3><p style="font-size:27px">Berita, pemeriksa fakta, dan situs resmi (termasuk tniad.mil.id dan Kemhan), dengan panel cakupan dan titik buta.</p></div>
      <div class="card" style="padding:28px 38px"><h3 style="font-size:34px">Antrean triase</h3><p style="font-size:27px">Untuk pemeriksa manusia. Tiket ditutup setelah balasan terkirim.</p></div>
      <div class="card" style="padding:28px 38px;background:var(--sun-soft);border-color:transparent"><h3 style="font-size:34px;color:var(--ragu)">Narasi, bukan orang</h3><p style="font-size:27px;color:var(--ink)">Tidak ada pelacakan akun, warga, atau prajurit tertentu.</p></div>
    </div>
  </div>
  {FOOT}
</section>'''

etika = f'''<section class="slide blue">
  <div class="kicker">## · Pengaman</div>
  <h2>Yang <em>tidak akan</em> dilakukan Halio.</h2>
  <div class="row" style="margin-top:60px;gap:36px;flex:1;margin-bottom:70px">
    <ul class="clean" style="flex:1.2">
      <li>Memantau <b>individu, akun, atau prajurit</b>. Yang dipantau: narasi dan sumber publik.</li>
      <li>Menilai <b>pendapat politik</b> atau melabeli kritik sebagai hoaks.</li>
      <li>Menurunkan konten atau membuat <b>kontra-narasi otomatis</b>.</li>
      <li>Mengklaim <b>mendeteksi bot</b> atau deepfake: datanya tidak ada.</li>
      <li>Bertindak tanpa <b>persetujuan manusia</b>.</li>
    </ul>
    <div class="card" style="flex:.9;display:flex;flex-direction:column;justify-content:center">
      <h3 style="color:#fff">Yang dilakukan</h3>
      <p>Bukti bernomor dan tingkat keyakinan di setiap kesimpulan.</p>
      <p style="margin-top:14px">Data pribadi dihapus sebelum diproses; statistik agregat.</p>
      <p style="margin-top:14px">Metodologi, batas, dan titik buta ditulis di setiap laporan.</p>
    </div>
  </div>
  <div class="foot"><span>Selaras dengan UU PDP dan prinsip ketahanan informasi</span><span><b>@@</b> / @@</span></div>
</section>'''

hasil = f'''<section class="slide">
  <div class="kicker">## · Hasil uji, apa adanya</div>
  <h2>Diukur di server, <em>dengan web sungguhan.</em></h2>
  <div class="row" style="margin-top:50px;gap:30px;align-items:stretch">
    <div class="card grow" style="text-align:center"><div class="big" style="font-size:150px">0<span style="font-size:60px"> / 10</span></div><p style="font-size:28px">berita benar dituduh hoaks</p></div>
    <div class="card grow" style="text-align:center"><div class="big" style="font-size:150px">0<span style="font-size:60px"> / 8</span></div><p style="font-size:28px">hoaks yang keluar hijau</p></div>
    <div class="card grow" style="text-align:center;background:var(--ragu-bg);border-color:transparent"><div class="big" style="font-size:150px;color:var(--ragu)">1<span style="font-size:60px"> / 8</span></div><p style="font-size:28px">hoaks yang sampai merah</p></div>
    <div class="card grow" style="text-align:center"><div class="big" style="font-size:150px">5<span style="font-size:60px"> / 50</span></div><p style="font-size:28px">kalimat laporan dibuang pemeriksa</p></div>
  </div>
  <div class="card" style="margin-top:34px;padding:30px 44px"><p style="font-size:30px;color:var(--ink)"><b>Artinya:</b> Halio aman, tetapi masih <b>terlalu hati-hati</b>. Hoaks yang jelas sering berhenti di “tidak yakin, dibantah untuk versi yang mirip”, karena bantahannya datang dari media, bukan sumber resmi. Kami lebih memilih ini daripada menuduh kabar benar.</p></div>
  <p class="note" style="margin-top:14px">Sumber: eval/AGENT_RESULTS.md (18 klaim, 7 Nov 2026) dan evaluasi lanjutan (7 hoaks + 4 berita). 0 / 66 dari uji tim terdahulu pada data buatan sendiri. Bukan evaluasi independen.</p>
  {FOOT}
</section>'''

batas = f'''<section class="slide blue">
  <div class="kicker">## · Jujur soal batas</div>
  <h2>Yang <em>belum</em> bisa kami janjikan.</h2>
  <ul class="clean" style="margin-top:60px">
    <li>Masih <b>prototipe</b>. Belum ada pengguna nyata; pilot keluarga akan dicatat apa adanya.</li>
    <li>Korpus bantahan kurasi <b>baru 7 entri</b>; arsip judul cek fakta ±6.000 dan bertambah.</li>
    <li>Sekitar <b>sepertiga halaman</b> menolak dibaca server; sebagian dibaca dari salinan arsip dan diberi label.</li>
    <li>“Kemunculan paling awal” berarti <b>yang kami temukan</b> di web terbuka, bukan asal pesan WhatsApp.</li>
    <li>Halio membaca <b>isi</b> foto; tidak menilai asli atau tidaknya. <b>Video</b> belum didukung.</li>
  </ul>
  <div class="foot"><span>Lebih baik jujur belum tahu daripada asal bicara</span><span><b>@@</b> / @@</span></div>
</section>'''

langkah = f'''<section class="slide">
  <div class="kicker">## · Langkah berikutnya</div>
  <h2>Dari prototipe <em>ke pilot.</em></h2>
  <div class="row" style="margin-top:60px;gap:26px;align-items:stretch;flex:1;margin-bottom:70px">
    <div class="card grow" style="border-top:10px solid var(--blue)"><div class="kicker" style="font-size:20px">Segera</div><h3 style="margin-top:12px;font-size:36px">Arsip bantahan penuh</h3><p style="font-size:26px">Riwayat pemeriksa fakta dan dataset BRIN; pencocokan klaim dengan embedding.</p></div>
    <div class="card grow" style="border-top:10px solid var(--blue-2)"><div class="kicker" style="font-size:20px">Berikutnya</div><h3 style="margin-top:12px;font-size:36px">Pilot kecil</h3><p style="font-size:26px">Keluarga dan satu unit siber, dengan evaluasi independen.</p></div>
    <div class="card grow" style="border-top:10px solid var(--sky)"><div class="kicker" style="font-size:20px">Lalu</div><h3 style="margin-top:12px;font-size:36px">Asal usul gambar</h3><p style="font-size:26px">Cloud Vision, hash gambar, Content Credentials.</p></div>
    <div class="card grow" style="border-top:10px solid var(--sun)"><div class="kicker" style="font-size:20px">Juga</div><h3 style="margin-top:12px;font-size:36px">Taksonomi DISARM</h3><p style="font-size:26px">Label teknik di brief analis, bahasa keyakinan bergaya intelijen.</p></div>
    <div class="card grow" style="border-top:10px solid #3F7D26"><div class="kicker" style="font-size:20px">Kemudian</div><h3 style="margin-top:12px;font-size:36px">Mode on-premise</h3><p style="font-size:26px">Model lokal untuk Radar internal; WhatsApp setelah verifikasi.</p></div>
  </div>
  {FOOT}
</section>'''

order = [cover, S[2], S[3], S[4], apa_itu, cara_pakai, S[6], S[7], swarm, laporan, nenek, cara_kerja, S[9], S[10], radar, etika, hasil, batas, langkah, S[14]]
html = []
for idx, sl in enumerate(order, 1):
    html.append(sl)

body = "\n\n".join(html)
n_total = len(order)
# number kickers (cover and closing have none) and footers
counter = iter(range(1, 100))
body = re.sub(r'<div class="kicker">(?:\d\d|##) · ', lambda m: f'<div class="kicker">{next(counter):02d} · ', body)
pages = iter(range(1, n_total + 1))


def foot(m):
    return m.group(0)


# footers: replace both the new placeholders and the old "NN / 14" per section, in slide order
parts = re.split(r"(?=<section class=\"slide)", body)
out = []
for i, part in enumerate(parts):
    if not part.strip():
        continue
    num = len([p for p in out if p.startswith("<section")]) + 1
    part = re.sub(r"<b>(?:@@|\d\d)</b> / (?:@@|14)", f"<b>{num:02d}</b> / {n_total:02d}", part)
    out.append(part)
(HERE / "halio_deck_v2.html").write_text(head + "\n\n" + "".join(out) + "\n" + tail, encoding="utf-8")
print("slides:", n_total, "->", HERE / "halio_deck_v2.html")

// Static hosting uses explicit local scenarios, never a fabricated API response.
window.HALIO_STATIC_DEMO = location.hostname.endsWith(".github.io") || new URLSearchParams(location.search).has("static");

(() => {
  const source = {
    nama: "Katadata (mengutip Bareskrim Polri)",
    url: "https://katadata.co.id/amp/digital/teknologi/67a5dc910647b/penipuan-bansos-pakai-ai-wajah-prabowo-ratusan-korban-rugi-puluhan-juta/",
  };
  const techniques = [{
    label: "Iming-iming dan permintaan uang",
    lesson: " Bantuan dijadikan umpan sebelum pengirim meminta biaya administrasi.",
    evidence: ["bantuan tunai", "biaya admin"],
  }, {
    label: "Desakan menyebarkan",
    lesson: " Pesan mendesak penerima agar tidak sempat memeriksa sumbernya.",
    evidence: ["SEBARKAN"],
  }];

  function known(kind) {
    const records = {
      bansos: {
        claim: "Video Presiden membagikan bantuan tunai dengan pendaftaran dan biaya lewat WhatsApp",
        simple: "Itu video palsu buatan komputer. Bantuan resmi dari pemerintah tidak pernah meminta Ibu atau Bapak membayar biaya apa pun lewat WhatsApp.",
        fact: "Video semacam ini adalah deepfake. Korban diarahkan ke WhatsApp lalu diminta membayar biaya administrasi berulang kali. Bantuannya tidak pernah ada.",
        source,
      },
      tni: {
        claim: "Jalur khusus masuk TNI AD dijamin lulus setelah membayar orang dalam",
        simple: "Masuk TNI AD itu gratis dan lewat tes resmi. Siapa pun yang minta uang supaya dijamin lulus adalah penipu.",
        fact: "Rekrutmen TNI AD dilaksanakan terbuka, transparan, dan tidak dipungut biaya. Kelulusan ditentukan hasil seleksi, bukan pembayaran.",
        source: { nama: "Bisnis.com: Syarat dan Cara Daftar Rekrutmen TNI AD 2026", url: "https://kabar24.bisnis.com/read/20260107/243/1942271/syarat-dan-cara-daftar-rekrutmen-tni-ad-2026-simak-beserta-jadwalnya" },
      },
      gempa: {
        claim: "BMKG memprediksi gempa dan tsunami pada tanggal tertentu",
        simple: "Tidak ada yang bisa tahu tanggal gempa, termasuk BMKG. Cek informasi resmi di aplikasi atau situs BMKG.",
        fact: "Belum ada teknologi yang dapat memprediksi tanggal, lokasi, dan kekuatan gempa secara pasti.",
        source: { nama: "BMKG: Siaran pers prediksi gempa 7,0 adalah hoaks", url: "https://www.bmkg.go.id/siaran-pers/prediksi-gempa-7-0-earthquakes-weather-bmkg-sebut-itu-hoaks" },
      },
      kesehatan: {
        claim: "Air kelapa, garam, dan jeruk nipis dapat menyembuhkan COVID-19",
        simple: "Air kelapa itu menyegarkan, tapi bukan obat penyakit. Kalau sakit, periksakan ke puskesmas atau dokter.",
        fact: "Tidak ada bukti klinis bahwa campuran tersebut menyembuhkan COVID-19.",
        source: { nama: "Liputan6 Cek Fakta (dengan Mafindo)", url: "https://www.liputan6.com/cek-fakta/read/4332289/cek-fakta-tidak-ada-bukti-air-kelapa-dicampur-jeruk-nipis-dan-garam-manjur-menyembuhkan-penderita-covid-19" },
      },
    };
    return records[kind];
  }

  window.HalioStaticDemo = {
    check(text) {
      const lower = text.toLowerCase();
      let kind;
      if (/bantuan|bansos|presiden/.test(lower)) kind = "bansos";
      else if (/tni|kodam|tentara/.test(lower)) kind = "tni";
      else if (/gempa|tsunami|bmkg/.test(lower)) kind = "gempa";
      else if (/kelapa|covid|corona/.test(lower)) kind = "kesehatan";

      if (kind) {
        const item = known(kind);
        return {
          id: `static-${kind}`, status: "terbukti_salah", status_label: "Terbukti salah",
          claim: item.claim, method: "simulasi_lokal_korpus_demo",
          match: { sederhana: item.simple, fakta: item.fact, sumber: [item.source] },
          manipulation: { techniques: kind === "bansos" ? techniques : [] },
          links: { warnings: [] }, llm: null, card_url: "", voice_url: "",
          voice_script: item.simple, offer_human_review: false,
          disclaimer: "Simulasi lokal dengan jawaban dari korpus demo; bukan pemeriksaan langsung oleh server.",
        };
      }

      const greeting = /selamat pagi|selamat siang|selamat malam/.test(lower);
      const script = greeting
        ? "Ini sapaan, bukan klaim faktual yang perlu diperiksa."
        : "Halio belum menemukan pemeriksaan yang cocok. Jangan teruskan dulu; pada penginstalan dengan backend, pesan ini dapat dikirim ke antrean pemeriksa manusia.";
      return {
        id: "static-unknown", status: greeting ? "tidak_yakin" : "belum_ada_pemeriksaan",
        status_label: greeting ? "Halio tidak yakin" : "Belum ada pemeriksaan",
        claim: text, method: "simulasi_lokal_abstention", match: null,
        manipulation: { techniques: [] }, links: { warnings: [] }, llm: null,
        card_url: "", voice_url: "", voice_script: script, offer_human_review: !greeting,
        disclaimer: "Simulasi lokal untuk memperlihatkan perilaku saat Halio tidak mempunyai sumber.",
      };
    },
    radar: {
      window_days: 7, since: "2026-10-26", total_checks: 24, demo_events: 24,
      by_status: { terbukti_salah: 15, tidak_yakin: 5, belum_ada_pemeriksaan: 4 },
      open_appeals: 1, open_escalations: 3, k_anonymity: 5, rumours_below_k: 2,
      by_kategori: [
        { kategori: "penipuan_bansos", n: 8 }, { kategori: "penipuan_catut_tni", n: 5 },
        { kategori: "bencana", n: 4 }, { kategori: "kesehatan", n: 3 }, { kategori: "phishing", n: 2 },
      ],
      techniques: { ajakan_sebar: 12, urgensi: 9, minta_data_uang: 8, otoritas_palsu: 6, iming_iming: 5 },
      daily: [
        { day: "2026-10-26", n: 2 }, { day: "2026-10-27", n: 3 }, { day: "2026-10-28", n: 2 },
        { day: "2026-10-29", n: 4 }, { day: "2026-10-30", n: 5 }, { day: "2026-10-31", n: 6 }, { day: "2026-11-01", n: 2 },
      ],
      emerging_rumours: [{ text: "SIMULASI: kabar penutupan jalan yang belum diperiksa", count: 5, first_seen: "2026-10-31" }],
      top_debunks: [
        { debunk_id: "bansos-deepfake-presiden", kategori: "penipuan_bansos", n: 8 },
        { debunk_id: "rekrutmen-tni-ad-berbayar", kategori: "penipuan_catut_tni", n: 5 },
        { debunk_id: "bmkg-prediksi-gempa-tanggal", kategori: "bencana", n: 4 },
      ],
    },
    coverage: {
      coverage: {
        generated: "2026-11-01T08:00:00Z", polling: false, sources_total: 3,
        counts: { hidup: 1, basi: 1, mati: 1, tertunda: 0, belum: 0 },
        live_share: 1 / 3, seen_delay_s_median: 120,
        disclaimer: "SIMULASI STATIS: contoh tampilan cakupan, bukan hasil pemantauan feed saat ini.",
        sources: [
          { name: "BMKG (contoh)", kind_label: "Sumber resmi · simulasi", status: "hidup", last_error: "", newest_item_age_s: 240, items_per_hour: 4, latency_ms_median: 180, seen_delay_s_median: 120 },
          { name: "TurnBackHoax (contoh)", kind_label: "Cek fakta · simulasi", status: "basi", last_error: "", newest_item_age_s: 90000, items_per_hour: 1, latency_ms_median: 240, seen_delay_s_median: 300 },
          { name: "Feed contoh tidak aktif", kind_label: "Media terbuka · simulasi", status: "mati", last_error: "Kesalahan sintetis untuk demonstrasi", newest_item_age_s: null, items_per_hour: null, latency_ms_median: null, seen_delay_s_median: null },
        ],
        blind_spots: [
          { name: "WhatsApp privat", tier: "C", reason: "Halio tidak membaca grup atau percakapan pribadi." },
          { name: "TikTok dan X", tier: "B", reason: "Cakupan memerlukan izin dan integrasi yang belum tersedia dalam demo statis." },
        ],
      },
      recent: { items: [
        { title: "SIMULASI: judul artikel untuk memperlihatkan tampilan sensor", url: "https://github.com/Ardelyo/halio", source_id: "contoh", first_seen: "2026-11-01T07:58:00Z" },
      ] },
    },
  };
})();

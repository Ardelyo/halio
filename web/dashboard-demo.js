(() => {
  const items = {
    escalations: [
      { id: 103, created: "2026-11-01T08:20:00+07:00", check_id: "d1030000000000000000000000000000", claim: "SIMULASI: Bantuan tunai dapat diambil setelah membayar biaya pencairan melalui tautan pribadi.", status: "menunggu", channel: "web", reporter: "web:demo" },
      { id: 102, created: "2026-11-01T07:45:00+07:00", check_id: "d1020000000000000000000000000000", claim: "SIMULASI: Jalur khusus rekrutmen menjamin kelulusan dengan biaya tertentu.", status: "menunggu", channel: "telegram", reporter: "tg:demo" },
      { id: 101, created: "2026-10-31T16:10:00+07:00", check_id: "d1010000000000000000000000000000", claim: "SIMULASI: Penutupan jalan selama sepekan yang belum memiliki konfirmasi resmi.", status: "menunggu", channel: "web", reporter: "web:demo" },
    ],
    appeals: [
      { id: 21, created: "2026-11-01T08:35:00+07:00", check_id: "d0210000000000000000000000000000", debunk_id: "bansos-deepfake-presiden", reason: "SIMULASI: Konteks tanggal pada pesan perlu diperiksa ulang.", status: "baru" },
    ],
  };
  const events = { escalations: [], appeals: [] };
  const categories = ["penipuan_bansos", "penipuan_catut_tni", "bencana", "kesehatan", "phishing"];
  const categoryTotals = { penipuan_bansos: 38, penipuan_catut_tni: 23, bencana: 19, kesehatan: 14, phishing: 12 };

  function dateAt(offset) {
    const date = new Date();
    date.setUTCDate(date.getUTCDate() - offset);
    return date.toISOString().slice(0, 10);
  }

  function radar(days) {
    const daily = [];
    let total = 0;
    let falseCount = 0;
    let uncertain = 0;
    let unknown = 0;
    for (let offset = days - 1; offset >= 0; offset--) {
      const n = 2 + ((offset * 3 + 2) % 7);
      const falseDaily = Math.max(1, Math.round(n * 0.58));
      const uncertainDaily = Math.max(1, Math.round(n * 0.2));
      const unknownDaily = Math.max(0, n - falseDaily - uncertainDaily);
      daily.push({ day: dateAt(offset), status: "terbukti_salah", n: falseDaily });
      daily.push({ day: dateAt(offset), status: "tidak_yakin", n: uncertainDaily });
      if (unknownDaily) daily.push({ day: dateAt(offset), status: "belum_ada_pemeriksaan", n: unknownDaily });
      total += n;
      falseCount += falseDaily;
      uncertain += uncertainDaily;
      unknown += unknownDaily;
    }
    return {
      window_days: days, since: dateAt(days - 1), total_checks: total, demo_events: total,
      by_status: { terbukti_salah: falseCount, tidak_yakin: uncertain, belum_ada_pemeriksaan: unknown },
      by_kategori: categories.map((kategori) => ({ kategori, n: Math.max(2, Math.round(categoryTotals[kategori] * days / 30)) })),
      techniques: { ajakan_sebar: Math.round(54 * days / 30), urgensi: Math.round(43 * days / 30), minta_data_uang: Math.round(37 * days / 30), otoritas_palsu: Math.round(28 * days / 30), iming_iming: Math.round(21 * days / 30) },
      daily,
      emerging_rumours: [
        { hash: "demo-1", text: "SIMULASI: kabar penutupan jalan yang belum diperiksa", count: 7, first_seen: dateAt(1), last_seen: dateAt(0) },
        { hash: "demo-2", text: "SIMULASI: tawaran bantuan dengan biaya pencairan", count: 5, first_seen: dateAt(2), last_seen: dateAt(0) },
      ],
      top_debunks: [
        { debunk_id: "bansos-deepfake-presiden", kategori: "penipuan_bansos", n: Math.round(38 * days / 30) },
        { debunk_id: "rekrutmen-tni-ad-berbayar", kategori: "penipuan_catut_tni", n: Math.round(23 * days / 30) },
        { debunk_id: "bmkg-prediksi-gempa-tanggal", kategori: "bencana", n: Math.round(19 * days / 30) },
      ],
      rumours_below_k: 2, k_anonymity: 5,
      open_appeals: items.appeals.filter((item) => item.status === "baru").length,
      open_escalations: items.escalations.filter((item) => item.status === "menunggu").length,
    };
  }

  window.HalioDashboardDemo = {
    radar,
    reviews(type, openOnly) {
      const pending = type === "appeals" ? "baru" : "menunggu";
      return {
        items: items[type].filter((item) => !openOnly || item.status === pending),
        events: events[type],
      };
    },
    resolve(type, id, response) {
      const item = items[type].find((entry) => entry.id === id);
      if (!item || item.status === "selesai") throw new Error("Tiket tidak tersedia atau sudah selesai.");
      item.status = "selesai";
      events[type].unshift({ id: Date.now(), created: new Date().toISOString(), item_type: type, item_id: id, action: "resolved", response });
      return { ok: true, sent: false, recorded: true, message: "Tersimpan untuk sesi demo ini saja. Tidak ada balasan yang dikirim; perubahan hilang saat halaman dimuat ulang." };
    },
    coverage: window.HalioStaticDemo.coverage,
  };
})();

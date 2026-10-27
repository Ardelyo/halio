// On-device text heuristics. Port of backend/halio/manipulation.py; keep in sync.
// Runs entirely in the page; nothing is sent anywhere by this file.
(() => {
  const TECHNIQUES = [
    ["ajakan_sebar", "Desakan menyebarkan", [/\bsebar(kan|luaskan)?\b/, /\bviral(kan)?\b/, /\bteruskan\b/, /\bbagikan\b/, /jangan berhenti di/, /kirim(kan)? ke \d+/, /\bshare\b/]],
    ["urgensi", "Dibuat terburu-buru", [/\bsegera\b/, /sekarang juga/, /\bburuan\b/, /hari ini terakhir/, /batas (waktu|akhir)/, /\bcepat\b/, /terbatas/]],
    ["otoritas_palsu", "Mengaku orang penting", [/info (a1|valid|dari dalam)/, /orang dalam/, /kata (dokter|intel|teman)/, /sumber terpercaya/, /info dari (polda|polres|kodim|kodam|mabes)/]],
    ["rasa_takut", "Menakut-nakuti", [/\bwaspada\b/, /\bbahaya\b/, /\bawas\b/, /mematikan/, /penculik/, /\bdarurat\b/, /tsunami besar/, /gempa besar/]],
    ["iming_iming", "Iming-iming hadiah", [/\bgratis\b/, /\bhadiah\b/, /bantuan (tunai|langsung|sosial)/, /\bbansos\b/, /dijamin lulus/, /kuota \d+ ?gb/, /\bbonus\b/]],
    ["minta_data_uang", "Minta data atau uang", [/biaya (admin|administrasi|pendaftaran)/, /\btransfer\b/, /kode otp/, /\botp\b/, /isi (data|formulir)/, /klik (link|tautan)/, /nomor rekening/]],
  ];

  // Online gambling (judol) vocabulary common in Indonesian banners and links.
  const JUDOL = /\b(slot|gacor|maxwin|togel|scatter|rtp|zeus|olympus|mahjong ways|bonus new member|depo(sit)? \d|wd cepat|situs (resmi|terpercaya) \d*|link alternatif)\b/i;

  function fold(s) {
    return s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase();
  }

  function analyze(text) {
    const low = fold(text);
    const techniques = [];
    for (const [id, label, patterns] of TECHNIQUES) {
      if (patterns.some((p) => p.test(low))) techniques.push({ id, label });
    }
    const letters = text.replace(/[^A-Za-z]/g, "");
    const caps = letters.length > 30 && letters.replace(/[^A-Z]/g, "").length / letters.length > 0.6;
    const shouting = caps || text.includes("!!!");
    const score = Math.min(1, 0.25 * techniques.length + (shouting ? 0.15 : 0));
    return { techniques, shouting, score, needsCheck: score >= 0.5 };
  }

  function isJudol(text) {
    return JUDOL.test(fold(text || ""));
  }

  // Same rules as backend/halio/pii.py: only scrubbed text (<=300 chars) may leave the device.
  function scrub(text) {
    return text
      .replace(/https?:\/\/\S+|www\.\S+/gi, "[TAUTAN]")
      .replace(/\b\d{6}[\s.-]?\d{6}[\s.-]?\d{4}\b/g, "[NIK]")
      .replace(/[\w.+-]+@[\w-]+\.[\w.-]+/g, "[EMAIL]")
      .replace(/(?:\+?62|0)8\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,5}/g, "[NOMOR]")
      .replace(/\b\d{10,15}\b/g, "[REKENING]")
      .replace(/(^|\s)@\w{3,}/g, "$1[AKUN]")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 300);
  }

  globalThis.HalioLexicon = { analyze, isJudol, scrub };
})();

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const reveals = document.querySelectorAll(".reveal");

if (reducedMotion || !("IntersectionObserver" in window)) {
  reveals.forEach((element) => element.classList.add("is-visible"));
} else {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    });
  }, { threshold: 0.12 });
  reveals.forEach((element) => observer.observe(element));
}

const screens = [
  `<div class="device-header"><span class="avatar">K</span><span><b>Keluarga Besar</b><small>6 anggota · pesan diteruskan</small></span><span>08.42</span></div>
   <div class="device-chat"><p>Ada video Presiden bagi-bagi bantuan tunai! Langsung chat nomor WA untuk daftar, <mark>bayar biaya admin 150rb dulu.</mark> SEBARKAN!!</p><small>Pesan sintetis untuk demonstrasi</small></div>
   <p class="device-tip"><span aria-hidden="true">△</span> Desakan menyebarkan dan permintaan uang perlu dicurigai.</p>`,
  `<div class="checking-screen"><div class="scanner-mark"><svg viewBox="0 0 50 50" fill="none" aria-hidden="true"><circle cx="21" cy="21" r="13" stroke="#0E1726" stroke-width="2"/><path d="m31 31 10 10" stroke="#0E1726" stroke-width="2" stroke-linecap="round"/><path d="M14 21h14M21 14v14" stroke="#0E1726" stroke-width="1.5" stroke-linecap="round"/></svg><span class="scanner-line"></span></div><h3>Memeriksa klaimnya</h3><p>Bukan menilai pengirimnya.</p><ul class="check-list"><li><span>✓</span> Nomor telepon dan tautan disaring</li><li><span>✓</span> Inti klaim dicocokkan dengan korpus bantahan</li><li><span>✓</span> Sumber diperiksa sebelum memberi vonis</li></ul></div>`,
  `<div class="result-screen"><div class="result-brand"><img src="icons/icon.svg" alt="">halio.<small>HASIL PEMERIKSAAN</small></div><div class="result-status"><span class="answer-symbol" aria-hidden="true">!</span><span><small>Berdasarkan bantahan yang cocok</small><h3>Terbukti salah</h3></span></div><p class="result-explanation">Itu video palsu buatan komputer. Bantuan resmi tidak meminta Ibu atau Bapak membayar biaya apa pun lewat WhatsApp.</p><div class="result-trick"><b>Kenali triknya:</b> iming-iming bantuan, desakan segera, lalu permintaan biaya administrasi.</div><div class="result-source"><span><small>Sumber pemeriksaan</small><b>Katadata · mengutip Bareskrim Polri</b></span><span aria-hidden="true">↗</span></div></div>`,
  `<div class="correction-screen"><div class="device-header"><span class="avatar">K</span><span><b>Keluarga Besar</b><small>Koreksi siap dibagikan</small></span><span>08.44</span></div><div class="device-chat"><div class="correction-label"><img src="icons/icon.svg" alt="">Kartu Halio</div><h3>Terbukti salah</h3><p>Bantu jaga grup kita tetap aman. Video bantuan ini palsu. Bantuan resmi tidak meminta biaya administrasi lewat WhatsApp, jadi jangan transfer atau sebarkan nomornya.</p><div class="correction-source">Sumber: Katadata, mengutip Bareskrim Polri ↗</div></div><div class="loop-complete"><span>✓</span> Koreksi bersumber kembali ke keluarga</div></div>`,
];

const screen = document.querySelector("#demo-screen");
const steps = [...document.querySelectorAll(".demo-step")];
const next = document.querySelector("#demo-next");
const nextLabels = ["Lanjut: periksa klaim", "Lanjut: lihat jawaban", "Lanjut: bagikan koreksi", "Putar ulang demonstrasi"];
let activeStep = 0;

function showStep(index, focus = false) {
  activeStep = index;
  steps.forEach((step, i) => {
    const active = i === index;
    step.classList.toggle("is-active", active);
    step.setAttribute("aria-selected", String(active));
    step.tabIndex = active ? 0 : -1;
    if (active && focus) step.focus();
  });
  screen.classList.remove("is-changing");
  screen.innerHTML = screens[index];
  requestAnimationFrame(() => screen.classList.add("is-changing"));
  next.innerHTML = `${nextLabels[index]} <span aria-hidden="true">→</span>`;
}

steps.forEach((step, index) => {
  step.addEventListener("click", () => showStep(index));
  step.addEventListener("keydown", (event) => {
    let target;
    if (event.key === "ArrowDown" || event.key === "ArrowRight") target = (index + 1) % steps.length;
    if (event.key === "ArrowUp" || event.key === "ArrowLeft") target = (index - 1 + steps.length) % steps.length;
    if (event.key === "Home") target = 0;
    if (event.key === "End") target = steps.length - 1;
    if (target === undefined) return;
    event.preventDefault();
    showStep(target, true);
  });
});

next.addEventListener("click", () => showStep((activeStep + 1) % steps.length));
showStep(0);

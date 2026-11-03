// Frame-exact renderer. Usage:
//   node video/tools/render.js stills <outdir> <t1,t2,...>        -> PNG stills for review
//   node video/tools/render.js frames <out.mp4> <fromFrame> <toFrame>  -> H.264 segment (no audio)
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const PAGE = "file://" + path.resolve(__dirname, "../src/index.html");

async function open() {
  const browser = await chromium.launch({ args: ["--force-color-profile=srgb", "--disable-gpu-vsync"] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(PAGE);
  await page.evaluate(() => Engine.ready());
  return { browser, page, errors };
}

async function stills(outdir, times) {
  const { browser, page, errors } = await open();
  fs.mkdirSync(outdir, { recursive: true });
  for (const t of times) {
    await page.evaluate((t) => Engine.seek(t), t);
    await page.screenshot({ path: path.join(outdir, `t${t.toFixed(1).padStart(6, "0")}.png`) });
  }
  if (errors.length) console.error("PAGE ERRORS:", errors);
  await browser.close();
}

async function frames(out, from, to) {
  const { browser, page, errors } = await open();
  const fps = await page.evaluate(() => Engine.TL.fps);
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], { stdio: ["pipe", "inherit", "inherit"] });
  const t0 = Date.now();
  for (let f = from; f < to; f++) {
    await page.evaluate(([t, f]) => Engine.seek(t, f), [f / fps, f]);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    if ((f - from) % 300 === 0) console.log(`[${path.basename(out)}] frame ${f}/${to} (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  if (errors.length) console.error("PAGE ERRORS:", errors);
  await browser.close();
}

const [mode, a, b, c] = process.argv.slice(2);
if (mode === "stills") stills(a, b.split(",").map(Number));
else if (mode === "frames") frames(a, +b, +c);
else { console.error("usage: render.js stills|frames ..."); process.exit(2); }

// Renderer for the 9:16 story teaser. Usage:
//   node video/tools/render_story.js stills <outdir> <t1,t2,...>
//   node video/tools/render_story.js frames <out.mp4> <fromFrame> <toFrame> [fps=60]
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");
const PAGE = "file://" + path.resolve(__dirname, "../story/index.html");

async function open() {
  const browser = await chromium.launch({ args: ["--force-color-profile=srgb"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(PAGE);
  await page.evaluate(() => Story.ready());
  return { browser, page, errors };
}

(async () => {
  const [mode, a, b, c, d] = process.argv.slice(2);
  const { browser, page, errors } = await open();
  if (mode === "stills") {
    fs.mkdirSync(a, { recursive: true });
    for (const t of b.split(",").map(Number)) {
      await page.evaluate((t) => Story.seek(t), t);
      await page.screenshot({ path: path.join(a, `s${t.toFixed(2).padStart(6, "0")}.png`) });
    }
  } else {
    const fps = +(d || 60);
    const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", a], { stdio: ["pipe", "inherit", "inherit"] });
    for (let f = +b; f < +c; f++) {
      await page.evaluate(([t, f]) => Story.seek(t, f), [f / fps, f]);
      const buf = await page.screenshot({ type: "jpeg", quality: 95 });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
    }
    ff.stdin.end();
    await new Promise((r) => ff.on("close", r));
  }
  if (errors.length) console.error("PAGE ERRORS:", errors);
  await browser.close();
})();

// On-device image classification with NudeNet (YOLOv8n, 320px, MIT licence).
// The image is fetched and analysed inside the extension; no pixels leave the device.
const MODEL = "models/320n.onnx";
const SIZE = 320;
// Class order from NudeNet 3.4 (nudenet/nudenet.py). Verify when upgrading the model.
const LABELS = [
  "FEMALE_GENITALIA_COVERED", "FACE_FEMALE", "BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED",
  "FEMALE_GENITALIA_EXPOSED", "MALE_BREAST_EXPOSED", "ANUS_EXPOSED", "FEET_EXPOSED", "BELLY_COVERED",
  "FEET_COVERED", "ARMPITS_COVERED", "ARMPITS_EXPOSED", "FACE_MALE", "BELLY_EXPOSED",
  "MALE_GENITALIA_EXPOSED", "ANUS_COVERED", "FEMALE_BREAST_COVERED", "BUTTOCKS_COVERED",
];
const UNSAFE = new Set(["BUTTOCKS_EXPOSED", "FEMALE_BREAST_EXPOSED", "FEMALE_GENITALIA_EXPOSED", "ANUS_EXPOSED", "MALE_GENITALIA_EXPOSED"]);
const THRESHOLD = 0.45;

let sessionPromise = null;

function session() {
  if (!sessionPromise) {
    if (typeof ort === "undefined") return Promise.reject(new Error("onnxruntime-web belum dipasang (jalankan scripts/fetch_models.py)"));
    ort.env.wasm.wasmPaths = chrome.runtime.getURL("vendor/");
    ort.env.wasm.numThreads = 1; // offscreen documents are not cross-origin isolated
    sessionPromise = ort.InferenceSession.create(chrome.runtime.getURL(MODEL), { executionProviders: ["wasm"] });
  }
  return sessionPromise;
}

async function toTensor(src) {
  const blob = await (await fetch(src)).blob();
  const bmp = await createImageBitmap(blob);
  const scale = Math.min(SIZE / bmp.width, SIZE / bmp.height);
  const w = Math.round(bmp.width * scale), h = Math.round(bmp.height * scale);
  const canvas = new OffscreenCanvas(SIZE, SIZE);
  const ctx = canvas.getContext("2d");
  ctx.fillStyle = "#000";
  ctx.fillRect(0, 0, SIZE, SIZE);
  ctx.drawImage(bmp, 0, 0, w, h); // letterbox top-left, as NudeNet pads right/bottom
  const { data } = ctx.getImageData(0, 0, SIZE, SIZE);
  const chw = new Float32Array(3 * SIZE * SIZE);
  for (let i = 0; i < SIZE * SIZE; i++) {
    chw[i] = data[i * 4] / 255;
    chw[SIZE * SIZE + i] = data[i * 4 + 1] / 255;
    chw[2 * SIZE * SIZE + i] = data[i * 4 + 2] / 255;
  }
  return new ort.Tensor("float32", chw, [1, 3, SIZE, SIZE]);
}

async function classify(src) {
  const s = await session();
  const out = await s.run({ [s.inputNames[0]]: await toTensor(src) });
  const t = out[s.outputNames[0]]; // [1, 4 + classes, anchors]
  const [, rows, anchors] = t.dims;
  let worst = { label: null, score: 0 };
  for (let a = 0; a < anchors; a++) {
    for (let c = 4; c < rows; c++) {
      const score = t.data[c * anchors + a];
      const label = LABELS[c - 4];
      if (UNSAFE.has(label) && score > worst.score) worst = { label, score };
    }
  }
  return { ok: true, unsafe: worst.score >= THRESHOLD, label: worst.label, score: Number(worst.score.toFixed(3)) };
}

chrome.runtime.onMessage.addListener((msg, _sender, reply) => {
  if (msg.target !== "offscreen") return false;
  const job = msg.type === "model-status"
    ? session().then(() => ({ ok: true, model: MODEL }))
    : classify(msg.src);
  job.then(reply, (e) => reply({ ok: false, error: String(e.message || e) }));
  return true;
});

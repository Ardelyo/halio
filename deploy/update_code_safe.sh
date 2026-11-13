#!/usr/bin/env bash
# deploy PEMBARUAN KODE aman ke VM (bukan deploy_gce.sh, yg menimpa .env.systemd). cara pakai dari akar repo:
#   git archive HEAD backend data web deploy scripts eval -o /tmp/halio_release.tgz --format=tar.gz
#   gcloud compute scp /tmp/halio_release.tgz deploy/update_code_safe.sh halio:/tmp/ --project gemma4good-494311 --zone asia-southeast2-a
#   gcloud compute ssh halio --project gemma4good-494311 --zone asia-southeast2-a --command "sudo bash /tmp/update_code_safe.sh $(git rev-parse --short HEAD)"
# deploy kode+data+web dgn prosedur aman (docs/DEPLOY_UPDATE.md): backup, ekstrak tanpa nyentuh halio.db / data/arsip.jsonl / .env.systemd
# (cuma HALIO_BUILD yg diganti), restart, cek kesehatan; rollback otomatis kalo ada langkah gagal. jalanin sbg root.
set -euo pipefail
SHA="$1"
TS=$(date -u +%Y%m%d-%H%M%S)
BK="/opt/halio-backups/pre-${SHA}-${TS}.tgz"
mkdir -p /opt/halio-backups
tar -czf "$BK" -C /opt/halio backend data web deploy scripts eval .env.systemd
chmod 600 "$BK"
echo "backup: $BK ($(du -h "$BK" | cut -f1))"

rollback() {
  echo "!!! GAGAL, rollback dari $BK"
  tar -xzf "$BK" -C /opt/halio
  chown -R halio:halio /opt/halio/backend /opt/halio/data /opt/halio/web /opt/halio/deploy /opt/halio/scripts /opt/halio/eval
  systemctl restart halio-api halio-bot || true
  echo "rollback selesai"
}
trap rollback ERR

sudo -u halio tar -xzf /tmp/halio_release.tgz -C /opt/halio
BUILD="${SHA}-$(date -u +%Y%m%d-%H%M)"
if grep -q '^HALIO_BUILD=' /opt/halio/.env.systemd; then
  sed -i "s/^HALIO_BUILD=.*/HALIO_BUILD=${BUILD}/" /opt/halio/.env.systemd
else
  echo "HALIO_BUILD=${BUILD}" >> /opt/halio/.env.systemd
fi
systemctl restart halio-api halio-bot
for i in $(seq 1 30); do sleep 2; curl -sf localhost:8000/health >/dev/null && break; done
HEALTH=$(curl -sf localhost:8000/health); echo "$HEALTH"
grep -q "\"build\":\"${BUILD}\"" <<<"$HEALTH"

# tanpa pipa ke grep -q (SIGPIPE + pipefail bikin gagal palsu): hasil ditangkap ke variabel dulu
check() { local r; r=$(curl -sf -m "$3" -X POST localhost:8000/api/check -H 'content-type: application/json' -d "$1"); grep -q "$2" <<<"$r"; }
check '{"text":"Ada video Presiden bagi-bagi bantuan tunai, daftar lewat WA dan bayar biaya admin Rp150 ribu. SEBARKAN!!","mode":"tanpa_ai"}' '"terbukti_salah"' 30
echo "tes1 (bansos, lokal): ok"
check '{"text":"Polisi kirim surat tilang digital lewat WhatsApp, pasang file apk ini untuk lihat dendanya","mode":"tanpa_ai"}' '"terbukti_salah"' 30
echo "tes2 (tilang APK, entri baru): ok"
check '{"text":"Besok Jakarta akan diguyur hujan es sebesar bola tenis menurut ramalan warga.","mode":"tanpa_ai"}' '"belum_ada_pemeriksaan"' 30
echo "tes3 (di luar korpus): ok"
check '{"text":"Pemerintah akan membagikan bantuan sembako gratis, daftar lewat link ini dan transfer biaya admin"}' '"status"' 120
echo "tes4 (mode penuh dengan AI): ok"
PAGE=$(curl -sf localhost:8000/cek.html); grep -q 'engine/halio-local.js' <<<"$PAGE"
DATA=$(curl -sf localhost:8000/engine/data.js); grep -q HalioEngineData <<<"${DATA:0:200}"
echo "tes5 (cek.html dan engine tersaji): ok"
systemctl is-active halio-api halio-bot
trap - ERR
echo "SELESAI build ${BUILD}"

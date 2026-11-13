#!/usr/bin/env bash
# deploy Halio (API + bot Telegram) nyala terus di satu VM kecil GCE; jalanin dr root repo abis `gcloud auth login`:
#   PROJECT=gemma4good-494311 ZONE=asia-southeast2-a bash deploy/deploy_gce.sh
# wajib ada .env yg udah keisi. Sengaja pake VM bukan Cloud Run soalnya bot long-polling ga boleh mati kena scale-to-zero.
set -euo pipefail
PROJECT=${PROJECT:-gemma4good-494311}; ZONE=${ZONE:-asia-southeast2-a}; VM=${VM:-halio}
[ -f .env ] || { echo ".env missing"; exit 1; }
# cek dulu VM-nya udah ada blm, kl blm sekalian bikinin e2-small di jakarta
gcloud compute instances describe "$VM" --project "$PROJECT" --zone "$ZONE" >/dev/null 2>&1 || \
  gcloud compute instances create "$VM" --project "$PROJECT" --zone "$ZONE" --machine-type e2-small \
    --image-family debian-12 --image-project debian-cloud --boot-disk-size 20GB --scopes cloud-platform
# bungkus kode tanpa kebawa database lokal ato .venv, tahan napas dulu sebelom kirim ke vm
tar --exclude=.venv --exclude=.git --exclude=halio.db --exclude='__pycache__' -czf /tmp/halio.tgz backend data web deploy scripts eval
gcloud compute scp /tmp/halio.tgz .env deploy/remote_install.sh "$VM":/tmp/ --project "$PROJECT" --zone "$ZONE"
HOST=${HOST:-}   # domain publik di belakang Caddy, misal halio.ardelyo.com
BUILD="$(git rev-parse --short HEAD 2>/dev/null || echo dev)-$(date -u +%Y%m%d-%H%M)"
gcloud compute ssh "$VM" --project "$PROJECT" --zone "$ZONE" --command "sudo bash /tmp/remote_install.sh '$HOST' '$BUILD'"

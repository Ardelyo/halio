#!/usr/bin/env bash
# Always-on Halio (API + Telegram bot) on one small GCE VM. Run from the repo root, after `gcloud auth login`.
#   PROJECT=gemma4good-494311 ZONE=asia-southeast2-a bash deploy/deploy_gce.sh
# Needs a filled .env at the repo root. A VM, not Cloud Run: the bot long-polls and must never scale to zero.
set -euo pipefail
PROJECT=${PROJECT:-gemma4good-494311}; ZONE=${ZONE:-asia-southeast2-a}; VM=${VM:-halio}
[ -f .env ] || { echo ".env missing"; exit 1; }
gcloud compute instances describe "$VM" --project "$PROJECT" --zone "$ZONE" >/dev/null 2>&1 || \
  gcloud compute instances create "$VM" --project "$PROJECT" --zone "$ZONE" --machine-type e2-small \
    --image-family debian-12 --image-project debian-cloud --boot-disk-size 20GB --scopes cloud-platform
tar --exclude=.venv --exclude=.git --exclude=halio.db --exclude='__pycache__' -czf /tmp/halio.tgz backend data web deploy scripts eval
gcloud compute scp /tmp/halio.tgz .env deploy/remote_install.sh "$VM":/tmp/ --project "$PROJECT" --zone "$ZONE"
HOST=${HOST:-}   # public hostname behind Caddy, e.g. halio.ardelyo.com
BUILD="$(git rev-parse --short HEAD 2>/dev/null || echo dev)-$(date -u +%Y%m%d-%H%M)"
gcloud compute ssh "$VM" --project "$PROJECT" --zone "$ZONE" --command "sudo bash /tmp/remote_install.sh '$HOST' '$BUILD'"

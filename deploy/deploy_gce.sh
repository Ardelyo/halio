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
tar --exclude=.venv --exclude=.git --exclude=halio.db --exclude='__pycache__' -czf /tmp/halio.tgz backend data web deploy
gcloud compute scp /tmp/halio.tgz .env "$VM":/tmp/ --project "$PROJECT" --zone "$ZONE"
gcloud compute ssh "$VM" --project "$PROJECT" --zone "$ZONE" --command '
set -e
sudo apt-get update -qq && sudo apt-get install -y -qq python3-venv fonts-dejavu-core
id halio >/dev/null 2>&1 || sudo useradd --system --home /opt/halio halio
sudo mkdir -p /opt/halio && sudo tar -xzf /tmp/halio.tgz -C /opt/halio
# systemd EnvironmentFile: no "export", no quotes needed; the DB lives on the VM disk
grep -v "^#" /tmp/.env | sed "s/^\([A-Z_]*\)=\"\(.*\)\"$/\1=\2/; s|^HALIO_DB=.*|HALIO_DB=/opt/halio/halio.db|" | sudo tee /opt/halio/.env.systemd >/dev/null
sudo chmod 600 /opt/halio/.env.systemd; rm -f /tmp/.env
sudo python3 -m venv /opt/halio/.venv
sudo /opt/halio/.venv/bin/pip install -q -r /opt/halio/backend/requirements.txt -r /opt/halio/backend/requirements-optional.txt
sudo chown -R halio:halio /opt/halio
sudo cp /opt/halio/deploy/*.service /etc/systemd/system/ && sudo systemctl daemon-reload
sudo systemctl enable --now halio-api halio-bot
sleep 5; systemctl is-active halio-api halio-bot; curl -s localhost:8000/health'

#!/usr/bin/env bash
# Runs on the VM as root: bash remote_install.sh <public-host-or-empty>
HOST=${1:-}
set -e
apt-get update -qq && apt-get install -y -qq python3-venv fonts-dejavu-core
id halio >/dev/null 2>&1 || useradd --system --home /opt/halio halio
mkdir -p /opt/halio && tar -xzf /tmp/halio.tgz -C /opt/halio
# systemd EnvironmentFile: no "export", no quotes needed; the DB lives on the VM disk
grep -v "^#" /tmp/.env | sed "s/^\([A-Z_]*\)=\"\(.*\)\"$/\1=\2/; s|^HALIO_DB=.*|HALIO_DB=/opt/halio/halio.db|" > /opt/halio/.env.systemd
if [ -n "$HOST" ]; then sed -i "s|^HALIO_TRUST_PROXY=.*|HALIO_TRUST_PROXY=1|; s|^PUBLIC_BASE_URL=.*|PUBLIC_BASE_URL=https://$HOST|" /opt/halio/.env.systemd; fi
chmod 600 /opt/halio/.env.systemd; rm -f /tmp/.env
python3 -m venv /opt/halio/.venv
/opt/halio/.venv/bin/pip install -q -r /opt/halio/backend/requirements.txt -r /opt/halio/backend/requirements-optional.txt
chown -R halio:halio /opt/halio
cp /opt/halio/deploy/*.service /etc/systemd/system/ && systemctl daemon-reload
systemctl enable halio-api halio-bot && systemctl restart halio-api halio-bot
sleep 5; systemctl is-active halio-api halio-bot; curl -s localhost:8000/health

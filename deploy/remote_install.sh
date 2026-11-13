#!/usr/bin/env bash
# dijalanin di dalem VM sebagai root: bash remote_install.sh <domain-publik-ato-kosong> <build-id>
HOST=${1:-}
BUILD=${2:-dev}
set -e
apt-get update -qq && apt-get install -y -qq python3-venv fonts-dejavu-core
id halio >/dev/null 2>&1 || useradd --system --home /opt/halio halio
mkdir -p /opt/halio && tar -xzf /tmp/halio.tgz -C /opt/halio
# format EnvironmentFile systemd: tanpa "export", tanda kutip dibiarin biar tetep bisa di-source dr bash, & path db diarahin ke disk VM
grep -v "^#" /tmp/.env | sed "s|^HALIO_DB=.*|HALIO_DB=/opt/halio/halio.db|" > /opt/halio/.env.systemd
if [ -n "$HOST" ]; then sed -i "s|^HALIO_TRUST_PROXY=.*|HALIO_TRUST_PROXY=1|; s|^PUBLIC_BASE_URL=.*|PUBLIC_BASE_URL=https://$HOST|" /opt/halio/.env.systemd; fi
echo "HALIO_BUILD=$BUILD" >> /opt/halio/.env.systemd
# kunci akses file env trus langsung hapus sisa /tmp/.env biar aman
chmod 600 /opt/halio/.env.systemd; rm -f /tmp/.env
python3 -m venv /opt/halio/.venv
/opt/halio/.venv/bin/pip install -q -r /opt/halio/backend/requirements.txt -r /opt/halio/backend/requirements-optional.txt
chown -R halio:halio /opt/halio
# pasang ulang service systemd trus cek beneran hidup ga abis restart
cp /opt/halio/deploy/*.service /etc/systemd/system/ && systemctl daemon-reload
systemctl enable halio-api halio-bot && systemctl restart halio-api halio-bot
sleep 5; systemctl is-active halio-api halio-bot; curl -s localhost:8000/health

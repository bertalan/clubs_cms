#!/bin/bash
# ClubCMS — Deploy script per clubs.betabi.it (aaPanel, bare metal)
# Eseguire dalla macchina locale: bash deploy/clubs.betabi.it/deploy.sh
#
# Server bare metal: Python venv + gunicorn + systemd
# Nessun Docker in produzione.
#
# Prima installazione sul server:
#   bash deploy/clubs.betabi.it/deploy.sh --setup
set -euo pipefail

# ── Configurazione ──────────────────────────────────────────────────────────
REMOTE_HOST="guzzi-days.net"
REMOTE_PORT="100"
DOMAIN_DIR="/www/wwwroot/clubs.betabi.it"
REMOTE_REPO="$DOMAIN_DIR/clubcms"
REMOTE_PATH="$REMOTE_REPO/clubcms"
VENV_DIR="$DOMAIN_DIR/venv"
REPO_URL="https://github.com/bertalan/clubs_cms.git"
BACKUP_DIR="$DOMAIN_DIR/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SSH_CMD="ssh -p $REMOTE_PORT -i ~/.ssh/id_rsa $REMOTE_HOST"

echo "=== ClubCMS Deploy → clubs.betabi.it — $TIMESTAMP ==="
echo "    Server: $REMOTE_HOST (porta $REMOTE_PORT) — bare metal"

# ── Prima installazione ──────────────────────────────────────────────────────
if [[ "${1:-}" == "--setup" ]]; then
    echo ""
    echo "[SETUP] Prima installazione su $REMOTE_HOST..."

    $SSH_CMD bash <<'ENDSSH'
set -euo pipefail

DOMAIN_DIR="/www/wwwroot/clubs.betabi.it"

# Crea directory
mkdir -p "$DOMAIN_DIR"/{staticfiles,media,backups}

# Clona il repository
if [ ! -d "$DOMAIN_DIR/clubcms" ]; then
    git clone https://github.com/bertalan/clubs_cms.git "$DOMAIN_DIR/clubcms"
    echo "  Repo clonato."
else
    echo "  Repo già presente, skip clone."
fi

cd "$DOMAIN_DIR/clubcms"
git fetch origin
git reset --hard origin/main
echo "  Codice aggiornato."

# ── Python venv ──────────────────────────────────────────────────────────────
if [ ! -d "$DOMAIN_DIR/venv" ]; then
    python3 -m venv "$DOMAIN_DIR/venv"
    echo "  Virtualenv creato."
fi
source "$DOMAIN_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$DOMAIN_DIR/clubcms/clubcms/requirements.txt"
echo "  Dipendenze installate."

# ── .env ─────────────────────────────────────────────────────────────────────
ENV_FILE="$DOMAIN_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    cp "$DOMAIN_DIR/clubcms/clubcms/deploy/clubs.betabi.it/.env.example" "$ENV_FILE"
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo ""
    echo "  .env creato in: $ENV_FILE  (chmod 600)"
    echo "  ATTENZIONE: modifica con i valori reali (DATABASE_URL, EMAIL, ecc.)"
else
    echo "  .env già presente: $ENV_FILE"
fi

# ── systemd: gunicorn ────────────────────────────────────────────────────────
cat > /etc/systemd/system/clubcms.service <<SYSTEMD
[Unit]
Description=ClubCMS Gunicorn (clubs.betabi.it)
After=network.target postgresql.service

[Service]
Type=notify
User=www
Group=www
WorkingDirectory=$DOMAIN_DIR/clubcms/clubcms
EnvironmentFile=$DOMAIN_DIR/.env
ExecStart=$DOMAIN_DIR/venv/bin/gunicorn clubcms.wsgi:application \
    --bind 127.0.0.1:8001 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SYSTEMD

# ── systemd: django-q2 ──────────────────────────────────────────────────────
cat > /etc/systemd/system/clubcms-qcluster.service <<SYSTEMD
[Unit]
Description=ClubCMS Django-Q2 Worker (clubs.betabi.it)
After=network.target postgresql.service clubcms.service

[Service]
Type=simple
User=www
Group=www
WorkingDirectory=$DOMAIN_DIR/clubcms/clubcms
EnvironmentFile=$DOMAIN_DIR/.env
ExecStart=$DOMAIN_DIR/venv/bin/python manage.py qcluster
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
SYSTEMD

systemctl daemon-reload
systemctl enable clubcms clubcms-qcluster
echo "  Servizi systemd installati e abilitati."

# ── Nginx vhost aaPanel ──────────────────────────────────────────────────────
VHOST_DIR="/www/server/panel/vhost/nginx"
if [ -d "$VHOST_DIR" ]; then
    cp "$DOMAIN_DIR/clubcms/clubcms/deploy/clubs.betabi.it/nginx.conf" \
       "$VHOST_DIR/clubs.betabi.it.conf"
    echo "  Nginx vhost installato."
    echo "  Riavvia nginx: /etc/init.d/nginx reload"
fi

ENDSSH

    echo ""
    echo "[SETUP] Completato. Prossimi passi:"
    echo "  1. Modifica /www/wwwroot/clubs.betabi.it/.env con i valori reali"
    echo "  2. Configura SSL in aaPanel per clubs.betabi.it"
    echo "  3. Esegui: bash deploy/clubs.betabi.it/deploy.sh"
    exit 0
fi

# ── Deploy standard ──────────────────────────────────────────────────────────
$SSH_CMD bash <<EOF
set -euo pipefail

DOMAIN_DIR="/www/wwwroot/clubs.betabi.it"
cd "\$DOMAIN_DIR/clubcms/clubcms"
source "\$DOMAIN_DIR/venv/bin/activate"
set -a; source "\$DOMAIN_DIR/.env"; set +a

echo "[1/7] Backup database..."
mkdir -p "\$DOMAIN_DIR/backups"
_DB_URL=\$(grep '^DATABASE_URL=' "\$DOMAIN_DIR/.env" | cut -d= -f2-)
_DB_USER=\$(echo "\$_DB_URL" | sed 's|postgres://||' | cut -d: -f1)
_DB_PASS=\$(echo "\$_DB_URL" | sed 's|postgres://[^:]*:||' | cut -d@ -f1)
_DB_NAME=\$(echo "\$_DB_URL" | awk -F/ '{print \$NF}')
PGPASSWORD="\$_DB_PASS" pg_dump -U "\$_DB_USER" -h 127.0.0.1 -p 5432 "\$_DB_NAME" 2>/dev/null \
    | gzip > "\$DOMAIN_DIR/backups/db_${TIMESTAMP}.sql.gz" \
    && echo "  Backup OK" \
    || echo "  AVVISO: backup fallito, continuo..."

echo "[2/7] Pull codice..."
cd "\$DOMAIN_DIR/clubcms"
git pull --ff-only
cd "\$DOMAIN_DIR/clubcms/clubcms"

echo "[3/7] Aggiornamento dipendenze..."
pip install -r requirements.txt --quiet

echo "[4/7] Migrazioni database..."
python manage.py migrate --noinput

echo "[5/9] Collect static files..."
python manage.py collectstatic --noinput

echo "[6/9] Configurazione dominio Sites..."
python manage.py configure_sites

echo "[7/9] Compilazione traduzioni..."
python manage.py compilemessages

echo "[8/9] Correzione permessi..."
chown -R www:www "\$DOMAIN_DIR"
echo "  Permessi OK (www:www su \$DOMAIN_DIR)"

echo "[9/9] Riavvio servizi..."
systemctl restart clubcms clubcms-qcluster

# Health check
sleep 3
HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" -H "Host: clubs.betabi.it" http://127.0.0.1:8001/it/ || echo "000")
if [ "\$HTTP_CODE" = "200" ] || [ "\$HTTP_CODE" = "301" ]; then
    echo "  Health check PASSED (HTTP \$HTTP_CODE)"
else
    echo "  ERRORE: Health check FAILED (HTTP \$HTTP_CODE)"
    echo "  Log: journalctl -u clubcms --no-pager -n 50"
    exit 1
fi

# Pulizia backup vecchi (mantieni ultimi 30)
find "\$DOMAIN_DIR/backups" -name "db_*.sql.gz" -mtime +30 -delete 2>/dev/null || true
EOF

echo ""
echo "=== Deploy completato: https://clubs.betabi.it ==="

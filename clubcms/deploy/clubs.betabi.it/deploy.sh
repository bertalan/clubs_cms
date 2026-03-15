#!/bin/bash
# ClubCMS — Deploy script per clubs.betabi.it (aaPanel)
# Eseguire dalla macchina locale: bash deploy/clubs.betabi.it/deploy.sh
#
# Prerequisiti locali:
#   - Accesso SSH al server: ssh -p YOUR_SSH_PORT root@YOUR_SERVER_HOST
#   - La chiave SSH deve essere autorizzata sul server
#
# Prima installazione sul server, eseguire:
#   bash deploy/clubs.betabi.it/deploy.sh --setup
set -euo pipefail

# ── Configurazione ──────────────────────────────────────────────────────────
REMOTE_HOST="YOUR_SERVER_HOST"
REMOTE_PORT="YOUR_SSH_PORT"
REMOTE_USER="${DEPLOY_USER:-root}"
REMOTE_PATH="/www/wwwroot/clubs.betabi.it/clubcms"
REPO_URL="https://github.com/bertalan/clubs_cms.git"
COMPOSE_FILE="deploy/clubs.betabi.it/docker-compose.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"
BACKUP_DIR="/www/wwwroot/clubs.betabi.it/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SSH_CMD="ssh -p $REMOTE_PORT $REMOTE_USER@$REMOTE_HOST"

echo "=== ClubCMS Deploy → clubs.betabi.it — $TIMESTAMP ==="
echo "    Server: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PORT"

# ── Prima installazione ──────────────────────────────────────────────────────
if [[ "${1:-}" == "--setup" ]]; then
    echo ""
    echo "[SETUP] Prima installazione su $REMOTE_HOST..."

    $SSH_CMD bash <<EOF
set -euo pipefail

# Crea directory
mkdir -p /www/wwwroot/clubs.betabi.it/{staticfiles,media,backups}

# Clona il repository
if [ ! -d "$REMOTE_PATH" ]; then
    git clone $REPO_URL $REMOTE_PATH
    echo "  Repo clonato in $REMOTE_PATH"
else
    echo "  Repo già presente, skip clone."
fi

cd $REMOTE_PATH

# Verifica .env
if [ ! -f ".env" ]; then
    cp deploy/clubs.betabi.it/.env.example .env
    echo ""
    echo "  ATTENZIONE: copia .env.example → .env creata."
    echo "  Modifica /www/wwwroot/clubs.betabi.it/clubcms/.env con i valori reali!"
    echo "  Poi esegui: bash deploy/clubs.betabi.it/deploy.sh"
else
    echo "  .env già presente."
fi

# Nginx vhost aaPanel
VHOST_DIR="/www/server/panel/vhost/nginx"
if [ -d "\$VHOST_DIR" ]; then
    cp deploy/clubs.betabi.it/nginx.conf \$VHOST_DIR/clubs.betabi.it.conf
    echo "  Nginx vhost installato in \$VHOST_DIR/clubs.betabi.it.conf"
    echo "  Riavvia nginx dal pannello aaPanel o: /etc/init.d/nginx reload"
else
    echo "  AVVISO: directory vhost nginx non trovata (\$VHOST_DIR)."
    echo "  Copia manuale: deploy/clubs.betabi.it/nginx.conf → vhost aaPanel"
fi
EOF

    echo ""
    echo "[SETUP] Completato. Prossimi passi:"
    echo "  1. Modifica il file .env sul server"
    echo "  2. Configura SSL in aaPanel per clubs.betabi.it"
    echo "  3. Esegui: bash deploy/clubs.betabi.it/deploy.sh"
    exit 0
fi

# ── Deploy standard ──────────────────────────────────────────────────────────
$SSH_CMD bash <<EOF
set -euo pipefail

cd $REMOTE_PATH

echo "[1/7] Backup database (pg_dump via aaPanel PostgreSQL)..."
mkdir -p $BACKUP_DIR
PGPASSWORD=\$(grep POSTGRES_PASSWORD .env | cut -d= -f2) \
    pg_dump -U YOUR_DB_NAME -h 127.0.0.1 YOUR_DB_NAME 2>/dev/null \
    | gzip > $BACKUP_DIR/db_${TIMESTAMP}.sql.gz \
    && echo "  Backup: $BACKUP_DIR/db_${TIMESTAMP}.sql.gz" \
    || echo "  AVVISO: backup fallito, continuo deploy..."

echo "[2/7] Pull codice aggiornato..."
git pull --ff-only

echo "[3/7] Build immagine Docker..."
$COMPOSE build web

echo "[4/7] Migrazioni database..."
$COMPOSE run --rm web python manage.py migrate --noinput

echo "[5/7] Collect static files..."
$COMPOSE run --rm web python manage.py collectstatic --noinput

echo "[6/7] Compilazione traduzioni..."
$COMPOSE run --rm web python manage.py compilemessages

echo "[7/7] Riavvio servizi..."
$COMPOSE up -d --remove-orphans

# Health check
sleep 5
HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health/ || echo "000")
if [ "\$HTTP_CODE" = "200" ]; then
    echo "  Health check PASSED (HTTP \$HTTP_CODE)"
else
    echo "  ERRORE: Health check FAILED (HTTP \$HTTP_CODE)"
    echo "  Log: docker compose -f $COMPOSE_FILE logs web --tail=50"
    exit 1
fi

# Pulizia backup vecchi (mantieni ultimi 30)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete 2>/dev/null || true
EOF

echo ""
echo "=== Deploy completato: https://clubs.betabi.it ==="

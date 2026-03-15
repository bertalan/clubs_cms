#!/bin/bash
# ClubCMS — Deploy script per clubs.betabi.it (aaPanel)
# Eseguire dalla macchina locale: bash deploy/clubs.betabi.it/deploy.sh
#
# Prerequisiti locali:
#   - Accesso SSH: ssh -p YOUR_SSH_PORT YOUR_SERVER_HOST  (utente root configurato in ~/.ssh/config)
#   - Chiave SSH: ~/.ssh/id_rsa
#
# Prima installazione sul server, eseguire:
#   bash deploy/clubs.betabi.it/deploy.sh --setup
set -euo pipefail

# ── Configurazione ──────────────────────────────────────────────────────────
REMOTE_HOST="guzzi-days.net"
REMOTE_PORT="100"
REMOTE_REPO="/www/wwwroot/clubs.betabi.it/clubcms"
REMOTE_PATH="/www/wwwroot/clubs.betabi.it/clubcms/clubcms"
REPO_URL="https://github.com/bertalan/clubs_cms.git"
COMPOSE_FILE="deploy/clubs.betabi.it/docker-compose.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"
BACKUP_DIR="/www/wwwroot/clubs.betabi.it/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
# Utente root già nel ~/.ssh/config per YOUR_SERVER_HOST
SSH_CMD="ssh -p $REMOTE_PORT -i ~/.ssh/id_rsa $REMOTE_HOST"

echo "=== ClubCMS Deploy → clubs.betabi.it — $TIMESTAMP ==="
echo "    Server: $REMOTE_HOST (porta $REMOTE_PORT)"

# ── Prima installazione ──────────────────────────────────────────────────────
if [[ "${1:-}" == "--setup" ]]; then
    echo ""
    echo "[SETUP] Prima installazione su $REMOTE_HOST..."

    $SSH_CMD bash <<'ENDSSH'
set -euo pipefail

# Crea directory webroot
mkdir -p /www/wwwroot/clubs.betabi.it/{staticfiles,media,backups}

# Clona il repository
if [ ! -d "/www/wwwroot/clubs.betabi.it/clubcms" ]; then
    git clone https://github.com/bertalan/clubs_cms.git /www/wwwroot/clubs.betabi.it/clubcms
    echo "  Repo clonato."
else
    echo "  Repo già presente, skip clone."
fi

cd /www/wwwroot/clubs.betabi.it/clubcms
git fetch origin
git reset --hard origin/main
echo "  Codice aggiornato."

# ── .env nella cartella del dominio, fuori dal repo git ──────────────────────
# Posizione: /www/wwwroot/clubs.betabi.it/.env  (una dir sopra il repo clubcms/)
ENV_FILE="/www/wwwroot/clubs.betabi.it/.env"

if [ ! -f "$ENV_FILE" ]; then
    cp deploy/clubs.betabi.it/.env.example "$ENV_FILE"
    # Genera SECRET_KEY Django/Wagtail sicura (50 byte → 67 char base64url)
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" "$ENV_FILE"
    chmod 600 "$ENV_FILE"
    echo ""
    echo "  .env creato in: $ENV_FILE  (chmod 600)"
    echo "  SECRET_KEY generata automaticamente."
    echo ""
    echo "  ATTENZIONE: modifica $ENV_FILE con i valori reali:"
    echo "    - DATABASE_URL (password del DB)"
    echo "    - ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS"
    echo "    - EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD"
    echo "  Poi esegui: bash deploy/clubs.betabi.it/deploy.sh"
else
    echo "  .env già presente: $ENV_FILE"
    # Ruota la SECRET_KEY ad ogni setup (sicurezza)
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" "$ENV_FILE"
    echo "  SECRET_KEY ruotata."
fi

# Nginx vhost aaPanel
VHOST_DIR="/www/server/panel/vhost/nginx"
if [ -d "$VHOST_DIR" ]; then
    cp deploy/clubs.betabi.it/nginx.conf $VHOST_DIR/clubs.betabi.it.conf
    echo "  Nginx vhost installato in $VHOST_DIR/clubs.betabi.it.conf"
    echo "  Riavvia nginx dal pannello aaPanel o: /etc/init.d/nginx reload"
else
    echo "  AVVISO: directory vhost nginx non trovata ($VHOST_DIR)."
    echo "  Copia manuale: deploy/clubs.betabi.it/nginx.conf → vhost aaPanel"
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

cd $REMOTE_PATH

echo "[1/7] Backup database (pg_dump — PostgreSQL locale aaPanel)..."
mkdir -p $BACKUP_DIR
# Estrae user, password e dbname da DATABASE_URL in /www/wwwroot/clubs.betabi.it/.env
# pg_dump gira sul bare metal → host sempre 127.0.0.1 (non host.docker.internal)
_DB_URL=\$(grep '^DATABASE_URL=' /www/wwwroot/clubs.betabi.it/.env | cut -d= -f2-)
_DB_USER=\$(echo "\$_DB_URL" | sed 's|postgres://||' | cut -d: -f1)
_DB_PASS=\$(echo "\$_DB_URL" | sed 's|postgres://[^:]*:||' | cut -d@ -f1)
_DB_NAME=\$(echo "\$_DB_URL" | awk -F/ '{print \$NF}')
PGPASSWORD="\$_DB_PASS" pg_dump -U "\$_DB_USER" -h 127.0.0.1 -p 5432 "\$_DB_NAME" 2>/dev/null \
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

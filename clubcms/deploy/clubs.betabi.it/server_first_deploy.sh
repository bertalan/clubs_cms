#!/bin/bash
# Script eseguito sul server per il primo deploy di clubs.betabi.it
# Copiato via SCP e lanciato da remoto — non committare
set -euo pipefail

DJANGO_DIR="/www/wwwroot/clubs.betabi.it/clubcms/clubcms"
COMPOSE="docker compose -f deploy/clubs.betabi.it/docker-compose.yml"

cd "$DJANGO_DIR"

echo "[1/6] Build immagine Docker..."
$COMPOSE build web

echo "[2/6] Migrazioni database..."
$COMPOSE run --rm web python manage.py migrate --noinput

echo "[3/6] Collect static files..."
$COMPOSE run --rm web python manage.py collectstatic --noinput

echo "[4/6] Compilazione traduzioni..."
$COMPOSE run --rm web python manage.py compilemessages

echo "[5/6] Avvio servizi..."
$COMPOSE up -d --remove-orphans

echo "[6/6] Health check..."
sleep 6
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/health/ || echo "000")
if [ "$HTTP_CODE" = "200" ]; then
    echo "  Health check PASSED (HTTP $HTTP_CODE)"
else
    echo "  Health check FAILED (HTTP $HTTP_CODE)"
    echo "  Log: $COMPOSE logs web --tail=50"
    exit 1
fi

echo ""
echo "=== Deploy completato: https://clubs.betabi.it ==="

#!/bin/bash
# ClubCMS — Production deploy script
# Usage: ./deploy/deploy.sh
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== ClubCMS Deploy — $TIMESTAMP ==="

# 1. Backup database
echo "[1/8] Backing up database..."
mkdir -p "$BACKUP_DIR"
$COMPOSE exec -T db pg_dump -U "${POSTGRES_USER:-postgres}" "${POSTGRES_DB:-clubcms}" \
  | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"
echo "  Backup saved: $BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

# 2. Pull latest code
echo "[2/8] Pulling latest code..."
git pull --ff-only

# 3. Build new image
echo "[3/8] Building Docker image..."
$COMPOSE build web

# 4. Run migrations
echo "[4/8] Running migrations..."
$COMPOSE run --rm web python manage.py migrate --noinput

# 5. Collect static files
echo "[5/8] Collecting static files..."
$COMPOSE run --rm web python manage.py collectstatic --noinput

# 6. Compile translations
echo "[6/8] Compiling translations..."
$COMPOSE run --rm web python manage.py compilemessages

# 7. Restart services
echo "[7/8] Restarting services..."
$COMPOSE up -d --remove-orphans

# 8. Health check
echo "[8/8] Running health check..."
sleep 5
HTTP_CODE=$($COMPOSE exec web python -c "
import urllib.request
try:
    r = urllib.request.urlopen('http://localhost:8000/health/')
    print(r.getcode())
except Exception as e:
    print(f'FAIL: {e}')
")

if [ "$HTTP_CODE" = "200" ]; then
    echo "  Health check PASSED"
else
    echo "  Health check FAILED: $HTTP_CODE"
    echo "  Rolling back..."
    $COMPOSE down
    echo "  Check logs: $COMPOSE logs web"
    exit 1
fi

# Cleanup old backups (keep last 30)
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +30 -delete 2>/dev/null || true

echo "=== Deploy complete ==="

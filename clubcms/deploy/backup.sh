#!/bin/bash
# ClubCMS — Database backup (cron daily)
# Usage: crontab -e → 0 3 * * * /path/to/deploy/backup.sh
set -euo pipefail

COMPOSE="docker compose -f docker-compose.prod.yml"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

$COMPOSE exec -T db pg_dump -U "${POSTGRES_USER:-postgres}" "${POSTGRES_DB:-clubcms}" \
  | gzip > "$BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

# Keep last 30 days
find "$BACKUP_DIR" -name "db_*.sql.gz" -mtime +30 -delete 2>/dev/null || true

echo "Backup completed: $BACKUP_DIR/db_${TIMESTAMP}.sql.gz"

#!/usr/bin/env bash
# Rigenera requirements.lock da requirements.txt in un venv pulito, dentro
# l'immagine Docker (Python 3.12, Linux x86_64 come la produzione).
#
#   bash clubcms/scripts/lock.sh
#
# Poi: ricostruire l'immagine (docker compose up -d --build) e lanciare la CI.
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
docker compose -f "$APP_DIR/docker-compose.yml" run --rm -T --no-deps --entrypoint sh web -c '
    set -e
    python -m venv /tmp/lockenv
    /tmp/lockenv/bin/pip install -q --upgrade pip
    /tmp/lockenv/bin/pip install -q -r requirements.txt
    {
        echo "# Versioni esatte risolte da requirements.txt (Python 3.12, Linux x86_64)."
        echo "# Rigenerare con: bash scripts/lock.sh  - non modificare a mano."
        /tmp/lockenv/bin/pip freeze --exclude-editable | sort -f
    } > requirements.lock
'
echo "requirements.lock aggiornato: $(grep -vc '^#' "$APP_DIR/requirements.lock") pacchetti"

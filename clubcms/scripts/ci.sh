#!/usr/bin/env bash
# ClubCMS — controlli CI. Stessi controlli in locale (make ci, hook pre-push)
# e su GitHub Actions. Tutto gira nel container `web` del compose di sviluppo.
#
#   bash clubcms/scripts/ci.sh
#
# Se lo stack non è attivo lo avvia (e lo ferma alla fine).
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
COMPOSE=(docker compose -f "$APP_DIR/docker-compose.yml")
EXEC=("${COMPOSE[@]}" exec -T web)
LOCALES=(it en de fr es)

# Regole ruff bloccanti: errori di sintassi e Pyflakes, tranne quelle
# cosmetiche ancora da ripulire (vedi idea/tasks/BACKLOG.md, P1 Ruff).
RUFF_SELECT="E9,F"
RUFF_IGNORE="F401,F841,F541"

STARTED_HERE=0
cleanup() {
    if [[ "$STARTED_HERE" == "1" ]]; then
        "${COMPOSE[@]}" stop >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

step() { printf '\n== [%s] %s\n' "$1" "$2"; }

step 0 "Stack Docker"
if [[ -z "$("${COMPOSE[@]}" ps -q --status running web 2>/dev/null)" ]]; then
    "${COMPOSE[@]}" up -d --build --quiet-pull
    STARTED_HERE=1
fi
"${EXEC[@]}" python --version

step 1 "Sintassi script di deploy"
while IFS= read -r -d '' f; do
    bash -n "$f"
done < <(find "$APP_DIR/deploy" -name '*.sh' -print0)
echo "ok"

step 2 "Ruff ($RUFF_SELECT, ignora $RUFF_IGNORE)"
"${EXEC[@]}" ruff check apps/ clubcms/ \
    --select "$RUFF_SELECT" --ignore "$RUFF_IGNORE" \
    --exclude "**/migrations/**" --output-format concise

step 3 "Django system check (dev + prod --deploy)"
"${EXEC[@]}" python manage.py check --fail-level WARNING
"${EXEC[@]}" env \
    DJANGO_SETTINGS_MODULE=clubcms.settings.prod \
    SECRET_KEY="ci-only-$(date +%s)-not-a-real-secret-key-0123456789abcdef" \
    ALLOWED_HOSTS=example.com \
    CSRF_TRUSTED_ORIGINS=https://example.com \
    python manage.py check --deploy --fail-level WARNING

step 4 "Migrazioni mancanti"
"${EXEC[@]}" python manage.py makemigrations --check --dry-run

step 5 "Cataloghi .po"
for l in "${LOCALES[@]}"; do
    "${EXEC[@]}" msgfmt --check -o /dev/null "locale/$l/LC_MESSAGES/django.po"
    printf '%s ' "$l"
done
echo "ok"

step 6 "Test"
"${EXEC[@]}" pytest apps/ -q -p no:cacheprovider --tb=short

printf '\nCI OK\n'

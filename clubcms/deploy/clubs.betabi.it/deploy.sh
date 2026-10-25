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

# ── Log ─────────────────────────────────────────────────────────────────────
# Tutto l'output (locale e remoto) va anche in deploy/clubs.betabi.it/logs/
# (non versionato). Il server tiene una copia in /var/log/clubcms/.
LOG_DIR="$(cd "$(dirname "$0")" && pwd)/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/deploy-$TIMESTAMP.log"
exec > >(tee -a "$LOG_FILE") 2>&1
trap 'rc=$?; if [[ $rc -ne 0 ]]; then echo ""; echo "=== DEPLOY FALLITO (exit $rc) — log: $LOG_FILE ==="; fi' EXIT

echo "=== ClubCMS Deploy → clubs.betabi.it — $TIMESTAMP ==="
echo "    Server: $REMOTE_HOST (porta $REMOTE_PORT) — bare metal"
echo "    Avviato da: $(whoami)@$(hostname -s)  argomenti: ${*:-(nessuno)}"
echo "    Log: $LOG_FILE"

# ── Controllo stato git locale ───────────────────────────────────────────────
# Lo script esegue sul server la SUA copia dei comandi, ma il server scarica
# sempre origin/main: si deploya solo da main allineato a origin/main.
# --force permette soltanto modifiche locali non committate.
if [[ "${1:-}" != "--setup" ]]; then
    GIT_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || true)"

    if [[ -n "$GIT_ROOT" ]]; then
        git -C "$GIT_ROOT" fetch -q origin main
        BRANCH=$(git -C "$GIT_ROOT" rev-parse --abbrev-ref HEAD)
        LOCAL_HEAD=$(git -C "$GIT_ROOT" rev-parse HEAD)
        REMOTE_HEAD=$(git -C "$GIT_ROOT" rev-parse origin/main)

        if [[ "$BRANCH" != "main" || "$LOCAL_HEAD" != "$REMOTE_HEAD" ]]; then
            echo ""
            echo "  ERRORE: il deploy parte solo da 'main' allineato a origin/main."
            echo "    branch locale: $BRANCH ($(git -C "$GIT_ROOT" rev-parse --short HEAD))"
            echo "    origin/main:   $(git -C "$GIT_ROOT" rev-parse --short origin/main)"
            AHEAD=$(git -C "$GIT_ROOT" log --oneline origin/main..HEAD)
            BEHIND=$(git -C "$GIT_ROOT" log --oneline HEAD..origin/main)
            [[ -n "$AHEAD" ]] && { echo "  Commit locali non su origin/main:"; echo "$AHEAD" | sed 's/^/    /'; }
            [[ -n "$BEHIND" ]] && { echo "  Commit di origin/main mancanti in locale:"; echo "$BEHIND" | sed 's/^/    /'; }
            echo "  Fai merge su main, 'git switch main && git pull', poi rilancia."
            exit 1
        fi

        DIRTY=$(git -C "$GIT_ROOT" status --porcelain 2>/dev/null)
        if [[ -n "$DIRTY" ]]; then
            echo ""
            echo "  ATTENZIONE: ci sono modifiche locali non committate:"
            git -C "$GIT_ROOT" status --short
            echo "  Il server riceve solo origin/main, ma le modifiche a questo script"
            echo "  verrebbero eseguite comunque sul server."
            if [[ "${1:-}" != "--force" ]]; then
                echo "  Esegui 'git add' + 'git commit' prima del deploy (o: bash $0 --force)."
                exit 1
            fi
            echo "  --force: proseguo con il working tree non pulito."
        fi

        echo "    Git: main @ $(git -C "$GIT_ROOT" rev-parse --short HEAD) = origin/main ✓"
    fi
fi

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
pip install -r "$DOMAIN_DIR/clubcms/clubcms/requirements.lock"
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

# ── Utente di servizio ───────────────────────────────────────────────────────
# L'app NON gira come www: www è riservato al web server (le protezioni
# del pannello gli vietano di eseguire programmi). www legge static/media
# tramite il gruppo.
if ! id clubcms >/dev/null 2>&1; then
    useradd --system --gid www --home-dir "$DOMAIN_DIR" --no-create-home \
        --shell /usr/sbin/nologin clubcms
    echo "  Utente di servizio clubcms creato."
fi
chown -R -h clubcms:www "$DOMAIN_DIR/clubcms" "$DOMAIN_DIR/venv" "$DOMAIN_DIR/backups"
chown clubcms:www "$ENV_FILE"; chmod 600 "$ENV_FILE"

# ── systemd: gunicorn ────────────────────────────────────────────────────────
cat > /etc/systemd/system/clubcms.service <<SYSTEMD
[Unit]
Description=ClubCMS Gunicorn (clubs.betabi.it)
After=network.target postgresql.service

[Service]
Type=notify
User=clubcms
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
User=clubcms
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

mkdir -p /var/log/clubcms && chmod 700 /var/log/clubcms
REMOTE_LOG="/var/log/clubcms/deploy-${TIMESTAMP}.log"
exec > >(tee -a "\$REMOTE_LOG") 2>&1
echo "  Log sul server: \$REMOTE_LOG (commit in arrivo: $(git -C "$(dirname "$0")" rev-parse --short origin/main 2>/dev/null || echo '?'))"

DOMAIN_DIR="/www/wwwroot/clubs.betabi.it"
cd "\$DOMAIN_DIR/clubcms/clubcms"
source "\$DOMAIN_DIR/venv/bin/activate"
set -a; source "\$DOMAIN_DIR/.env"; set +a

echo "[1/10] Backup database..."
mkdir -p "\$DOMAIN_DIR/backups"
_DB_URL=\$(grep '^DATABASE_URL=' "\$DOMAIN_DIR/.env" | cut -d= -f2-)
_DB_USER=\$(echo "\$_DB_URL" | sed 's|postgres://||' | cut -d: -f1)
_DB_PASS=\$(echo "\$_DB_URL" | sed 's|postgres://[^:]*:||' | cut -d@ -f1)
_DB_NAME=\$(echo "\$_DB_URL" | awk -F/ '{print \$NF}')
PGPASSWORD="\$_DB_PASS" pg_dump -U "\$_DB_USER" -h 127.0.0.1 -p 5432 "\$_DB_NAME" 2>/dev/null \
    | gzip > "\$DOMAIN_DIR/backups/db_${TIMESTAMP}.sql.gz" \
    && echo "  Backup OK" \
    || echo "  AVVISO: backup fallito, continuo..."

echo "[2/10] Pull codice..."
cd "\$DOMAIN_DIR/clubcms"
git pull --ff-only
cd "\$DOMAIN_DIR/clubcms/clubcms"

echo "[3/10] Aggiornamento dipendenze..."
pip install -r requirements.lock --quiet

echo "[4/10] Migrazioni database..."
python manage.py migrate --noinput
python manage.py createcachetable

echo "[5/10] Collect static files..."
python manage.py collectstatic --noinput

echo "[6/10] Configurazione dominio Sites..."
python manage.py configure_sites

echo "[7/10] Compilazione traduzioni..."
python manage.py compilemessages

echo "[8/10] Correzione permessi..."
# Solo i file dell'app: il resto della document root resta al pannello (www).
chown -R -h clubcms:www "\$DOMAIN_DIR/clubcms" "\$DOMAIN_DIR/venv" "\$DOMAIN_DIR/backups"
chown clubcms:www "\$DOMAIN_DIR/.env"; chmod 600 "\$DOMAIN_DIR/.env"
chmod -R o-w "\$DOMAIN_DIR/clubcms" "\$DOMAIN_DIR/venv"
echo "  Permessi OK (clubcms:www sull'app)"

echo "[9/10] Riavvio servizi..."
# Prova di avvio nello stesso contesto delle unit (utente, env, cwd) PRIMA
# di fermare i processi attivi: se un permesso o un plugin di sicurezza
# blocca l'esecuzione, ci si ferma con il sito ancora su.
if ! systemd-run --quiet --wait --pipe --uid=clubcms --gid=www \
        -p EnvironmentFile="\$DOMAIN_DIR/.env" -p WorkingDirectory="\$(pwd)" \
        "\$DOMAIN_DIR/venv/bin/python" manage.py check; then
    echo "  ERRORE: l'app non si avvia come clubcms. Servizi NON riavviati."
    exit 1
fi
systemctl restart clubcms clubcms-qcluster
for _i in \$(seq 1 15); do
    sleep 2
    systemctl is-active --quiet clubcms && systemctl is-active --quiet clubcms-qcluster && break
done
for _u in clubcms clubcms-qcluster; do
    if ! systemctl is-active --quiet "\$_u"; then
        echo "  ERRORE: \$_u non è attivo (\$(systemctl is-active \$_u))."
        journalctl -u "\$_u" --no-pager -n 20
        exit 1
    fi
done
echo "  Servizi attivi (utente: \$(ps -o user= -p \$(systemctl show -p MainPID --value clubcms)))"

echo "[10/10] Verifica frontend nginx..."
# aaPanel spesso gestisce nginx via init.d; su altri host puo' essere systemd.
if [ -x /etc/init.d/nginx ]; then
    /etc/init.d/nginx status >/dev/null 2>&1 || /etc/init.d/nginx start >/dev/null 2>&1 || true
else
    systemctl is-active nginx >/dev/null 2>&1 || systemctl restart nginx >/dev/null 2>&1 || true
fi

# Health check
sleep 3
HTTP_CODE=\$(curl -s -o /dev/null -w "%{http_code}" -H "Host: clubs.betabi.it" http://127.0.0.1:8001/it/ || echo "000")
EDGE_CODE=\$(curl -k -s -o /dev/null -w "%{http_code}" --resolve clubs.betabi.it:443:127.0.0.1 https://clubs.betabi.it/it/ || echo "000")
if { [ "\$HTTP_CODE" = "200" ] || [ "\$HTTP_CODE" = "301" ]; } \
   && { [ "\$EDGE_CODE" = "200" ] || [ "\$EDGE_CODE" = "301" ] || [ "\$EDGE_CODE" = "302" ]; }; then
    echo "  Health check PASSED (app=\$HTTP_CODE, edge=\$EDGE_CODE)"
else
    echo "  ERRORE: Health check FAILED (app=\$HTTP_CODE, edge=\$EDGE_CODE)"
    echo "  Log: journalctl -u clubcms --no-pager -n 50"
    exit 1
fi

# Pulizia backup vecchi (mantieni ultimi 30)
find "\$DOMAIN_DIR/backups" -name "db_*.sql.gz" -mtime +30 -delete 2>/dev/null || true
# Log di deploy sul server: tieni gli ultimi 50
ls -1t /var/log/clubcms/deploy-*.log 2>/dev/null | tail -n +51 | xargs -r rm -f
EOF

echo ""
echo "=== Deploy completato: https://clubs.betabi.it ==="

# Production Deployment

## Overview

Production uses a traditional server setup:
- **GitHub** as code repository
- **Deploy script** on server pulls and restarts services
- **Gunicorn** as WSGI server
- **Nginx** as reverse proxy
- **PostgreSQL** as database
- **Let's Encrypt** for SSL

---

## Server Requirements

| Component | Version | Purpose |
|-----------|---------|---------|
| Ubuntu | 22.04+ | Operating system |
| Python | 3.11+ | Runtime |
| PostgreSQL | 15+ | Database |
| Nginx | Latest | Reverse proxy |
| Gunicorn | Latest | WSGI server |
| Git | Latest | Code deployment |

---

## Deployment Workflow

```
Developer → GitHub → Server (deploy.sh) → Live Site
```

| Step | Actor | Action |
|------|-------|--------|
| 1 | Developer | Push to GitHub (main branch) |
| 2 | Server | Run deploy.sh (manual or webhook) |
| 3 | Script | Pull latest code |
| 4 | Script | Install dependencies |
| 5 | Script | Run migrations |
| 6 | Script | Collect static files |
| 7 | Script | Restart Gunicorn |
| 8 | Script | Reload Nginx |

---

## Deploy Script Configuration

At the beginning of the deploy script, configure these variables:

### Required Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `SITE_PATH` | `/var/www/sitename` | Project root directory |
| `GUNICORN_SERVICE` | `gunicorn` | Systemd service name |
| `NGINX_CONF` | `/etc/nginx/sites-available/sitename` | Nginx config path |

### Database Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `DB_NAME` | `clubcms` | PostgreSQL database name |
| `DB_USER` | `dbuser` | Database user |

### Backup Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `BACKUP_PATH` | `$SITE_PATH/backups` | Backup storage location |
| `BACKUP_KEEP` | `10` | Number of backups to retain |

### Git Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `GIT_BRANCH` | `main` | Branch to deploy |
| `GIT_REMOTE` | `origin` | Git remote name |

### Virtual Environment

| Variable | Example | Description |
|----------|---------|-------------|
| `VENV_PATH` | `$SITE_PATH/venv` | Virtual environment path |
| `PYTHON` | `$VENV_PATH/bin/python` | Python executable |
| `PIP` | `$VENV_PATH/bin/pip` | Pip executable |

---

## Deploy Script Steps

The deploy script executes these steps **in order**:

| Order | Step | Command |
|-------|------|---------|
| 1 | Enter project directory | `cd /var/www/sitename` |
| 2 | Activate virtualenv | `source venv/bin/activate` |
| 3 | **Backup database** | `pg_dump > backups/pre_deploy_$(date).sql` |
| 4 | **Backup code** | `git stash` or `cp -r` to backup folder |
| 5 | Pull from GitHub | `git pull origin main` |
| 6 | Install dependencies | `pip install -e .` |
| 7 | Make migrations | `python manage.py makemigrations` |
| 8 | Apply migrations | `python manage.py migrate` |
| 9 | Collect static files | `python manage.py collectstatic --noinput` |
| 10 | Restart Gunicorn | `sudo systemctl restart gunicorn` |
| 11 | Reload Nginx | `sudo systemctl reload nginx` |
| 12 | **Rotate backups** | Keep last 10, delete older |

---

## Pre-Deploy Backup

### Backup Before Each Deploy

| Backup Type | Path | Content |
|-------------|------|---------|
| Database | `backups/db/pre_deploy_YYYYMMDD_HHMMSS.sql` | Full database dump |
| Code | `backups/code/pre_deploy_YYYYMMDD_HHMMSS/` | Current code state |

### Backup Rotation (Keep Last 10)

| Action | Purpose |
|--------|---------|
| Create backup | Before git pull |
| Count backups | List files in backup folder |
| If > 10 | Delete oldest |
| Keep 10 | Always have 10 rollback points |

### Rotation Logic

| Step | Action |
|------|--------|
| 1 | List backups sorted by date (oldest first) |
| 2 | Count total backups |
| 3 | If count > 10, calculate excess |
| 4 | Delete oldest (count - 10) backups |

---

## Deploy Script Location

| Path | Purpose |
|------|---------|
| `/var/www/sitename/deploy.sh` | Main deploy script |
| `/var/www/sitename/venv/` | Python virtual environment |
| `/var/www/sitename/staticfiles/` | Collected static files |
| `/var/www/sitename/media/` | User uploads |

---

## Environment Variables (Production)

Store in `/var/www/sitename/.env`:

| Variable | Purpose |
|----------|---------|
| DEBUG | False |
| SECRET_KEY | Secure random key |
| ALLOWED_HOSTS | domain.com,www.domain.com |
| DATABASE_URL | postgres://user:pass@localhost/dbname |
| DB_NAME | Database name |
| DB_USER | Database user |
| DB_PASSWORD | Database password |

---

## Gunicorn Configuration

### Systemd Service

Location: `/etc/systemd/system/gunicorn.service`

| Setting | Value |
|---------|-------|
| User | www-data |
| Group | www-data |
| WorkingDirectory | /var/www/sitename |
| ExecStart | gunicorn command |
| Restart | always |

### Gunicorn Settings

| Setting | Value | Purpose |
|---------|-------|---------|
| Workers | 3-4 | CPU cores × 2 + 1 |
| Bind | unix:/run/gunicorn.sock | Socket for Nginx |
| Timeout | 30 | Request timeout |

---

## Nginx Configuration

### Server Block

Location: `/etc/nginx/sites-available/sitename`

| Section | Purpose |
|---------|---------|
| listen 80 | HTTP (redirect to HTTPS) |
| listen 443 ssl | HTTPS |
| server_name | Domain name |
| ssl_certificate | Let's Encrypt cert |
| location /static/ | Serve static files |
| location /media/ | Serve uploads |
| location / | Proxy to Gunicorn |

### Static Files

| Path | Nginx Alias |
|------|-------------|
| /static/ | /var/www/sitename/staticfiles/ |
| /media/ | /var/www/sitename/media/ |

### Caching Headers

| File Type | Cache Duration |
|-----------|----------------|
| CSS, JS | 30 days |
| Images | 30 days |
| Fonts | 1 year |

---

## SSL Certificate

Using Let's Encrypt with Certbot:

| Action | Command |
|--------|---------|
| Install | `sudo apt install certbot python3-certbot-nginx` |
| Obtain cert | `sudo certbot --nginx -d domain.com` |
| Auto-renew | Automatic via systemd timer |

---

## Database Setup

### PostgreSQL

| Step | Action |
|------|--------|
| Create user | `CREATE USER dbuser WITH PASSWORD 'pass';` |
| Create database | `CREATE DATABASE dbname OWNER dbuser;` |
| Grant privileges | `GRANT ALL ON DATABASE dbname TO dbuser;` |

---

## Backup Strategy

### Database Backup

| Schedule | Action |
|----------|--------|
| Daily | pg_dump to /var/backups |
| Retention | 30 days |
| Off-site | Copy to external storage |

### Media Backup

| Schedule | Action |
|----------|--------|
| Daily | Rsync media folder |
| Retention | 30 days |

---

## Security Checklist

### Django Settings

| Setting | Value |
|---------|-------|
| DEBUG | False |
| SECRET_KEY | Unique, 50+ chars |
| ALLOWED_HOSTS | Specific domains |
| SECURE_SSL_REDIRECT | True |
| SESSION_COOKIE_SECURE | True |
| CSRF_COOKIE_SECURE | True |
| X_FRAME_OPTIONS | DENY |

### Server Security

| Item | Status |
|------|--------|
| Firewall (ufw) | Allow 22, 80, 443 only |
| SSH key auth | Password auth disabled |
| Fail2ban | Installed and configured |
| Updates | Automatic security updates |

---

## Monitoring

### Health Check Endpoint

| URL | Response |
|-----|----------|
| /health/ | {"status": "ok"} |

### Log Locations

| Log | Path |
|-----|------|
| Gunicorn | /var/log/gunicorn/ |
| Nginx access | /var/log/nginx/access.log |
| Nginx error | /var/log/nginx/error.log |
| Django | /var/www/sitename/logs/ |

---

## Rollback Procedure

If deployment fails:

| Step | Action |
|------|--------|
| 1 | Identify last working backup |
| 2 | Restore database from backup |
| 3 | Restore code from backup or `git checkout` |
| 4 | `pip install -e .` |
| 5 | `python manage.py migrate` |
| 6 | `sudo systemctl restart gunicorn` |

### Quick Rollback (Using Backups)

| Step | Command |
|------|---------|
| 1 | `cd /var/www/sitename` |
| 2 | `source venv/bin/activate` |
| 3 | `psql -U dbuser dbname < backups/db/pre_deploy_LATEST.sql` |
| 4 | `git checkout HEAD~1` or restore from code backup |
| 5 | `pip install -e .` |
| 6 | `python manage.py migrate` |
| 7 | `sudo systemctl restart gunicorn` |

### Rollback from Specific Backup

| Step | Action |
|------|--------|
| 1 | List available backups: `ls -la backups/db/` |
| 2 | Choose timestamp to restore |
| 3 | Restore DB: `psql < backups/db/pre_deploy_CHOSEN.sql` |
| 4 | Restore code: `cp -r backups/code/pre_deploy_CHOSEN/* .` |

---

## Initial Server Setup

### First-Time Setup Steps

| Order | Step |
|-------|------|
| 1 | Create system user |
| 2 | Clone repository |
| 3 | Create virtualenv |
| 4 | Install dependencies |
| 5 | Configure .env |
| 6 | Setup PostgreSQL |
| 7 | Run migrations |
| 8 | Collect static |
| 9 | Setup Gunicorn service |
| 10 | Setup Nginx config |
| 11 | Obtain SSL cert |
| 12 | Enable and start services |

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| 502 Bad Gateway | Gunicorn running? Socket exists? |
| Static files 404 | Collectstatic run? Nginx config? |
| Database error | Connection settings? User permissions? |
| SSL error | Certificate valid? Certbot renew? |

---

## Related Documentation

| Doc | Topic |
|-----|-------|
| [50-DOCKER.md](50-DOCKER.md) | Development environment |

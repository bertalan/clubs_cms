# ClubCMS — Installation Guide

ClubCMS is a multilingual CMS for clubs and associations, built on
**Django 5.x** and **Wagtail 7.x**. It provides membership management,
event registration with payments (Stripe/PayPal), 6 switchable themes,
a mutual-aid network, inter-club event federation, and push notifications.

## Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **Git**

No other software is required — Python, PostgreSQL, and all dependencies
run inside Docker containers.

---

## 1. Clone the repository

```bash
git clone <repository-url>
cd federated-sites/clubcms
```

All commands below assume you are inside the `clubcms/` directory.

---

## 2. Development setup

### Start the services

```bash
docker compose up -d
```

This starts two containers:

| Service | Description                | Port             |
| ------- | -------------------------- | ---------------- |
| `web`   | Django/Wagtail dev server  | `localhost:8888` |
| `db`    | PostgreSQL 15              | internal only    |

### Run migrations

```bash
docker compose exec web python manage.py migrate
```

### Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Load demo content (optional)

Build and load per-language demo fixtures (available: `en`, `it`):

```bash
# Build fixtures (both languages)
docker compose exec web python manage.py build_demo_db

# Load English as the primary site
docker compose exec web python manage.py load_demo --lang en --primary --flush

# Add Italian pages alongside English
docker compose exec web python manage.py load_demo --lang it
```

The `--primary` flag creates the Site, shared snippets (categories,
FAQs, testimonials, press releases, brand assets), and the root page
tree. A secondary load (without `--primary`) adds translated pages
and products while reusing shared content.

### Access the site

The default language is English, so the homepage redirects to `/en/`.

| URL                                   | Description          |
| ------------------------------------- | -------------------- |
| <http://localhost:8888/en/>           | Frontend (English)   |
| <http://localhost:8888/it/>           | Frontend (Italian)   |
| <http://localhost:8888/admin/>        | Wagtail admin panel  |
| <http://localhost:8888/django-admin/> | Django admin         |

Login and signup pages are provided by django-allauth at
`/<lang>/account/login/` and `/<lang>/account/signup/`.

---

## 3. Running tests

```bash
docker compose exec web pytest apps/ -v
```

The suite includes 500+ tests covering models, views, security,
i18n, payments, and federation.

---

## 4. Internationalization

ClubCMS supports 5 languages: **EN** (default), **IT**, **DE**, **FR**, **ES**.

URL paths are translated per language (e.g. `/it/eventi/` vs `/en/events/`,
`/it/soccorso-stradale/` vs `/en/mutual-aid/`).

After modifying translatable strings, regenerate the catalogs:

```bash
docker compose exec web python manage.py makemessages -l it -l en -l de -l fr -l es --no-wrap
docker compose exec web python manage.py compilemessages
```

---

## 5. Themes

Six CSS themes are available, switchable from the Wagtail admin
(Settings > Color Scheme):

**Velocity** (modern), **Heritage** (classic), **Terra** (earthy),
**Zen** (minimal), **Clubs** (premium), **Tricolore** (Italian pride).

All themes support dark mode via the `.dark-mode` class on `<html>`.

---

## 6. Production deployment

### Environment variables

```bash
cp .env.prod.example .env
```

Edit `.env` and fill in all required values:

| Variable                | Description                        |
| ----------------------- | ---------------------------------- |
| `SECRET_KEY`            | Random 50+ character string        |
| `ALLOWED_HOSTS`         | Your domain(s), comma-separated    |
| `CSRF_TRUSTED_ORIGINS`  | `https://yourdomain.com`           |
| `DATABASE_URL`          | PostgreSQL connection string       |
| `POSTGRES_PASSWORD`     | Database password                  |
| `EMAIL_HOST`            | SMTP server                        |
| `EMAIL_PASSWORD`        | SMTP password                      |
| `WAGTAILADMIN_BASE_URL` | Public URL of the site             |
| `DOMAIN`                | Domain for nginx/SSL               |

Optional variables for federation, push notifications (VAPID), and
payments are documented in `.env.prod.example`.

### Start production stack

```bash
docker compose -f docker-compose.prod.yml up -d
```

| Service    | Description                              |
| ---------- | ---------------------------------------- |
| `web`      | Gunicorn (3 workers) behind nginx        |
| `db`       | PostgreSQL 15 with health checks         |
| `nginx`    | Reverse proxy with SSL (Let's Encrypt)   |
| `qcluster` | Django-Q2 task worker (emails, push)     |

### Post-deploy commands

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py compilemessages
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

### SSL certificates

The nginx config expects Let's Encrypt certificates. Use the included
deploy script or set up certbot manually:

```bash
./deploy/deploy.sh
```

---

## 7. Project structure

```text
clubcms/
├── apps/
│   ├── core/           # Search, SEO, anti-spam, PWA, shared utilities
│   ├── website/        # Wagtail pages, StreamField blocks, snippets
│   ├── members/        # ClubUser model, profiles, membership cards
│   ├── events/         # Registration, payments (Stripe/PayPal/bank)
│   ├── federation/     # Inter-club event sharing via signed API
│   ├── notifications/  # Email, push (VAPID), SMS, digest
│   └── mutual_aid/     # Roadside assistance with geo-search
├── clubcms/
│   └── settings/
│       ├── base.py     # Shared settings
│       ├── dev.py      # Development (DEBUG, SQLite fallback)
│       └── prod.py     # Production (Gunicorn, security)
├── static/css/
│   ├── base.css        # Structural styles (shared)
│   └── themes/         # 6 theme stylesheets
├── templates/          # Django/Wagtail templates
├── locale/             # .po/.mo files (IT, EN, DE, FR, ES)
├── deploy/             # nginx.conf, deploy.sh, backup.sh
├── Dockerfile
├── docker-compose.yml      # Development
├── docker-compose.prod.yml # Production
└── entrypoint.sh           # DB wait + migrate on startup
```

---

## 8. Useful commands

```bash
# Django shell
docker compose exec web python manage.py shell

# Database shell
docker compose exec db psql -U postgres clubcms

# Check for missing migrations
docker compose exec web python manage.py makemigrations --check

# Collect static files (production)
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Backup database (production)
./deploy/backup.sh
```

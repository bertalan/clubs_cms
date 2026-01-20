# Docker Development Environment

## Overview

Docker is used exclusively for **local development**. Production deployment uses a traditional server setup with Gunicorn and Nginx.

## Development Stack

| Service | Image | Purpose |
|---------|-------|---------|
| web | python:3.11-slim | Django application |
| db | postgres:15-alpine | PostgreSQL database |

---

## Docker Compose Services

### Web Service

| Setting | Value |
|---------|-------|
| Build | From project Dockerfile |
| Port | 8000 (mapped to host) |
| Volumes | Project directory mounted |
| Command | Django runserver (dev) |

### Database Service

| Setting | Value |
|---------|-------|
| Image | postgres:15-alpine |
| Port | 5432 (internal only) |
| Volume | Persistent data volume |

---

## Environment Variables (Development)

| Variable | Value | Purpose |
|----------|-------|---------|
| DEBUG | True | Enable debug mode |
| SECRET_KEY | dev-secret-key | Django secret (dev only) |
| DATABASE_URL | postgres://postgres:postgres@db:5432/clubcms | DB connection |
| POSTGRES_DB | clubcms | Database name |
| POSTGRES_USER | postgres | Database user |
| POSTGRES_PASSWORD | postgres | Database password |

---

## Volume Mounts

| Volume | Path | Purpose |
|--------|------|---------|
| Project | .:/app | Live code reload |
| postgres_data | /var/lib/postgresql/data | Database persistence |
| static | /app/staticfiles | Static files |
| media | /app/media | User uploads |

---

## Entrypoint Script

The entrypoint runs on container start:

| Step | Action |
|------|--------|
| 1 | Wait for database to be ready |
| 2 | Run Django migrations |
| 3 | Create cache table |
| 4 | Start application |

---

## Common Commands

### Container Management

| Action | Command |
|--------|---------|
| Build | `docker compose build` |
| Start | `docker compose up -d` |
| Stop | `docker compose down` |
| Rebuild | `docker compose up --build -d` |
| Logs | `docker compose logs -f web` |

### Django Commands

| Action | Command |
|--------|---------|
| Shell | `docker compose exec web python manage.py shell` |
| Migrate | `docker compose exec web python manage.py migrate` |
| Superuser | `docker compose exec web python manage.py createsuperuser` |
| Collectstatic | `docker compose exec web python manage.py collectstatic` |

### Database Commands

| Action | Command |
|--------|---------|
| DB Shell | `docker compose exec db psql -U postgres clubcms` |
| Backup | `docker compose exec db pg_dump -U postgres clubcms > backup.sql` |
| Restore | `docker compose exec -T db psql -U postgres clubcms < backup.sql` |

---

## Makefile Shortcuts

| Target | Action |
|--------|--------|
| `make build` | Build containers |
| `make up` | Start containers |
| `make down` | Stop containers |
| `make logs` | View logs |
| `make shell` | Django shell |
| `make migrate` | Run migrations |
| `make test` | Run tests |

---

## Development Workflow

| Step | Action |
|------|--------|
| 1 | `docker compose up -d` to start |
| 2 | Edit code locally (auto-reload) |
| 3 | View at http://localhost:8000 |
| 4 | Check logs if issues |
| 5 | `docker compose down` when done |

---

## Dockerfile Layers

| Layer | Purpose |
|-------|---------|
| Base image | Python 3.11 slim |
| System deps | libpq, gcc, libjpeg, zlib |
| Python deps | From pyproject.toml |
| App code | Project files |
| Entrypoint | Startup script |

---

## System Dependencies

Required for production-like environment:

| Package | Purpose |
|---------|---------|
| libpq-dev | PostgreSQL client |
| gcc | Compile Python packages |
| libjpeg-dev | Image processing |
| zlib1g-dev | Compression |

---

## Differences: Dev vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Container | Docker Compose | No Docker |
| Server | runserver | Gunicorn |
| Database | Containerized PostgreSQL | Server PostgreSQL |
| Static | Django serves | Nginx serves |
| Debug | True | False |
| SSL | None | Let's Encrypt |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection error | Wait, check `docker compose logs db` |
| Permission denied | Check volume permissions |
| Port in use | Stop other services on 8000 |
| Slow on Mac | Use cached volumes |

---

## .env.example

Create `.env` file with:

| Variable | Example |
|----------|---------|
| DEBUG | True |
| SECRET_KEY | your-dev-secret-key |
| DATABASE_URL | postgres://postgres:postgres@db:5432/clubcms |

---

## Related Documentation

| Doc | Topic |
|-----|-------|
| [51-PRODUCTION.md](51-PRODUCTION.md) | Production deployment |

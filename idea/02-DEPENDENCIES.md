# Dependencies

## Core

```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "django>=5.0,<6.0",
    "wagtail>=7.0,<8.0",
    "wagtail-localize>=1.9",
    "psycopg[binary]>=3.0",
    "pillow>=10.0",
    "django-taggit>=5.0",
    "django-modelcluster>=6.0",
]
```

## Member Features

```toml
[project.optional-dependencies]
members = [
    "qrcode>=7.4",           # QR code generation for member cards
    "python-barcode>=0.15",  # Barcode generation for member cards
    "django-allauth>=0.60",  # User authentication
]
```

## Notifications & Background Tasks

```toml
[project.optional-dependencies]
notifications = [
    "django-q2>=1.6",        # Background task queue
    "pywebpush>=1.14",       # Web Push notifications
    "croniter>=2.0",         # Cron scheduling for django-q
]
```

## Event Federation

```toml
[project.optional-dependencies]
federation = [
    "httpx>=0.27",           # Async HTTP client for API calls
    "django-ratelimit>=4.1", # Rate limiting for API endpoints
]
```

## Production

```toml
[project.optional-dependencies]
prod = [
    "gunicorn>=21.0",
    "whitenoise>=6.0",
    "sentry-sdk>=1.0",
    "django-storages[s3]>=1.14",
]
```

## Development

```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-django>=4.5",
    "factory-boy>=3.3",
    "django-debug-toolbar>=4.0",
    "ruff>=0.1",
]
```

## Full Installation

```toml
[project.optional-dependencies]
all = [
    "clubcms[members,notifications,federation,prod]",
]
```

## Differences from Current

| Current | New | Notes |
|---------|-----|-------|
| coderedcms | wagtail | Pure Wagtail |
| django-jinja | - | Django templates |
| - | django-q2 | Background tasks |
| - | pywebpush | Push notifications |
| - | qrcode | Member cards |
| - | python-barcode | Member cards |
| - | httpx | Federation API calls |
| - | django-ratelimit | Federation rate limiting |

## Install

```bash
pip install -e ".[dev]"              # Dev only
pip install -e ".[members,dev]"      # Dev + member features
pip install -e ".[all]"              # Everything
```

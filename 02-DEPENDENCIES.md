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

## Production

```toml
[project.optional-dependencies]
prod = ["gunicorn>=21.0", "whitenoise>=6.0", "sentry-sdk>=1.0", "django-storages[s3]>=1.14"]
```

## Development

```toml
[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-django>=4.5", "factory-boy>=3.3", "django-debug-toolbar>=4.0", "ruff>=0.1"]
```

## Differences from Current

| Current | New | Notes |
|---------|-----|-------|
| coderedcms | wagtail | Pure Wagtail |
| django-jinja | - | Django templates |

## Install

```bash
pip install -e ".[dev]"     # Dev
pip install -e ".[prod]"    # Prod
```

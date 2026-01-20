# Django/Wagtail Settings

## Structure

```
clubcms/settings/
├── __init__.py   # Import from environment
├── base.py       # Common settings
├── dev.py        # Development
└── prod.py       # Production
```

## INSTALLED_APPS

```python
INSTALLED_APPS = [
    # Django
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    # Wagtail
    "wagtail.contrib.forms", "wagtail.contrib.redirects", "wagtail.contrib.settings",
    "wagtail.embeds", "wagtail.sites", "wagtail.users", "wagtail.snippets",
    "wagtail.documents", "wagtail.images", "wagtail.search", "wagtail.admin", "wagtail",
    # Multi-language
    "wagtail_localize", "wagtail_localize.locales",
    # Utils
    "taggit", "modelcluster",
    # Project
    "apps.core", "apps.website",
]
```

## Wagtail Settings

```python
WAGTAIL_SITE_NAME = "Club CMS"
WAGTAILADMIN_BASE_URL = "https://example.com"
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("it", "Italiano"), ("en", "English"), ("de", "Deutsch"),
    ("fr", "Français"), ("es", "Español"),
]
LANGUAGE_CODE = "it"
```

## Templates (Django, NO Jinja2)

```python
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "wagtail.contrib.settings.context_processors.settings",
        "apps.core.context_processors.theme_context",
    ]},
}]
```

## Static & Media

```python
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## Context Processor Tema

```python
def theme_context(request):
    from apps.website.models import SiteSettings
    settings = SiteSettings.for_request(request)
    return {"theme": settings.theme, "colors": settings.get_colors()}
```

| Current | New |
|---------|-----|
| django-jinja | Django templates |
| CodeRedCMS | Pure Wagtail |

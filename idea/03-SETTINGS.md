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
    "apps.core", "apps.website", "apps.federation",
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

---

## Email Configuration

### Development

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

### Production

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "noreply@example.com")
```

---

## Push Notifications (VAPID)

```python
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": env("VAPID_PUBLIC_KEY"),
    "VAPID_PRIVATE_KEY": env("VAPID_PRIVATE_KEY"),
    "VAPID_ADMIN_EMAIL": env("VAPID_ADMIN_EMAIL"),
}
```

Generate VAPID keys once and store in environment variables.

---

## Background Tasks (Django-Q)

```python
Q_CLUSTER = {
    "name": "clubcms",
    "workers": 2,
    "recycle": 500,
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",  # Use database as broker
}
```

### Scheduled Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| process_notification_queue | Every 5 min | Send pending notifications |
| send_daily_digest | 08:00 daily | Compile daily digests |
| send_weekly_digest | 08:00 Monday | Compile weekly digests |
| send_weekend_reminder | 09:00 Thursday | Weekend favorites email |
| check_expiring_memberships | 09:00 daily | Queue expiry reminders |
| cleanup_old_notifications | 03:00 daily | Delete old notifications |
| sync_federation | Every 2 hours | Fetch events from partners |
| sync_interest_counts | Every 15 min | Send interest counts to partners |

---

## Event Federation

```python
FEDERATION_SETTINGS = {
    # Sync frequency in seconds (default 2 hours)
    "SYNC_INTERVAL": 60 * 60 * 2,
    
    # How long before request expires (seconds)
    "REQUEST_MAX_AGE": 300,
    
    # Max events to fetch per partner
    "MAX_EVENTS_PER_SYNC": 100,
    
    # Enable interest sync back to partners
    "SHARE_INTEREST_COUNTS": True,
    
    # Batch interest updates interval (seconds)
    "INTEREST_SYNC_INTERVAL": 60 * 15,
    
    # Days of future events to fetch
    "FETCH_FUTURE_DAYS": 365,
    
    # Rate limit per partner per hour
    "RATE_LIMIT_REQUESTS": 60,
}

# Federation identity (from environment)
FEDERATION_ENABLED = env.bool("FEDERATION_ENABLED", False)
FEDERATION_OUR_CLUB_CODE = env("FEDERATION_OUR_CLUB_CODE", "")
FEDERATION_OUR_CLUB_NAME = env("FEDERATION_OUR_CLUB_NAME", "")
```

---

## Authentication (django-allauth)

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USERNAME_REQUIRED = False
LOGIN_REDIRECT_URL = "/my-profile/"
LOGOUT_REDIRECT_URL = "/"
```

---

| Current | New |
|---------|-----|
| django-jinja | Django templates |
| CodeRedCMS | Pure Wagtail |
| - | django-q2 (background tasks) |
| - | django-allauth (auth) |
| - | pywebpush (push notifications) |

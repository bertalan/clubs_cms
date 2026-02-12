# CONTRACT: Settings
# Version: 1.0
# Agent: AG-0
# Date: 2025-02-11

## AUTH_USER_MODEL
`members.ClubUser` (AbstractUser extension)

## INSTALLED_APPS
```
django.contrib.admin, auth, contenttypes, sessions, messages, staticfiles
wagtail.contrib.forms, redirects, settings
wagtail.embeds, sites, users, snippets, documents, images, search, admin, wagtail
wagtail_localize, wagtail_localize.locales
taggit, modelcluster
apps.core, apps.website, apps.members, apps.events
apps.federation, apps.notifications, apps.mutual_aid
```

## DATABASES
PostgreSQL via DATABASE_URL env var. Fallback: SQLite.

## LANGUAGES
```python
LANGUAGES = [("it","Italiano"), ("en","English"), ("de","Deutsch"), ("fr","Francais"), ("es","Espanol")]
LANGUAGE_CODE = "it"
```

## TEMPLATES
- Backend: Django templates (NOT Jinja2)
- DIRS: `[BASE_DIR / "templates"]`
- APP_DIRS: True
- Context processors: debug, request, auth, messages, wagtail.settings, apps.core.context_processors.theme_context

## STATIC / MEDIA
- STATIC_URL: /static/
- STATICFILES_DIRS: [BASE_DIR / "static"]
- MEDIA_URL: /media/

## URL Namespaces
- `django-admin/` -> django admin
- `admin/` -> wagtail admin
- `documents/` -> wagtail documents
- `account/` -> apps.members.urls (namespace="account") [pending]
- `api/federation/` -> apps.federation.urls_api (namespace="federation_api") [pending]
- `eventi/partner/` -> apps.federation.urls_frontend (namespace="federation") [pending]
- `mutual-aid/` -> apps.mutual_aid.urls (namespace="mutual_aid") [pending]
- `notifications/` -> apps.notifications.urls (namespace="notifications") [pending]
- `""` -> wagtail.urls (catch-all, MUST be last)

## WAGTAIL
- WAGTAIL_SITE_NAME = "Club CMS"
- WAGTAIL_I18N_ENABLED = True
- WAGTAILADMIN_BASE_URL from env

## AUTH (allauth, to be enabled by AG-6)
- ACCOUNT_EMAIL_REQUIRED = True
- ACCOUNT_EMAIL_VERIFICATION = "mandatory"
- ACCOUNT_AUTHENTICATION_METHOD = "email"
- ACCOUNT_USERNAME_REQUIRED = False
- LOGIN_REDIRECT_URL = "/my-profile/"
- LOGOUT_REDIRECT_URL = "/"

## PASSWORD VALIDATION
MinimumLengthValidator(min_length=12), CommonPasswordValidator, NumericPasswordValidator, UserAttributeSimilarityValidator

## FEDERATION
```python
FEDERATION_ENABLED = bool from env
FEDERATION_OUR_CLUB_CODE = str from env
FEDERATION_OUR_CLUB_NAME = str from env
FEDERATION_SETTINGS = {
    "SYNC_INTERVAL": 7200,
    "REQUEST_MAX_AGE": 300,
    "MAX_EVENTS_PER_SYNC": 100,
    "SHARE_INTEREST_COUNTS": True,
    "INTEREST_SYNC_INTERVAL": 900,
    "FETCH_FUTURE_DAYS": 365,
    "RATE_LIMIT_REQUESTS": 60,
}
```

## BACKGROUND TASKS
```python
Q_CLUSTER = {"name":"clubcms", "workers":2, "recycle":500, "timeout":60, "retry":120, "queue_limit":50, "bulk":10, "orm":"default"}
```

## PUSH NOTIFICATIONS
```python
WEBPUSH_SETTINGS = {"VAPID_PUBLIC_KEY":"", "VAPID_PRIVATE_KEY":"", "VAPID_ADMIN_EMAIL":""}
```

## SECURITY (prod.py)
- SECURE_SSL_REDIRECT = True
- SECURE_HSTS_SECONDS = 31536000
- SESSION_COOKIE_SECURE = True
- CSRF_COOKIE_SECURE = True
- X_FRAME_OPTIONS = "DENY"
- SECURE_CONTENT_TYPE_NOSNIFF = True

## APP CONFIG LABELS
- core -> CoreConfig (apps.core)
- website -> WebsiteConfig (apps.website)
- members -> MembersConfig (apps.members)
- events -> EventsConfig (apps.events)
- federation -> FederationConfig (apps.federation)
- notifications -> NotificationsConfig (apps.notifications)
- mutual_aid -> MutualAidConfig (apps.mutual_aid)

## PAGE TEMPLATE CONVENTION
`website/pages/{model_name_snake_case}.html` (e.g. `website/pages/home_page.html`)

## BLOCK TEMPLATE CONVENTION
`website/blocks/{block_name_snake_case}.html` (e.g. `website/blocks/hero_slider_block.html`)

## CSS CLASS CONVENTION
`block-{block-name}` (kebab-case, e.g. `block-hero-slider`)

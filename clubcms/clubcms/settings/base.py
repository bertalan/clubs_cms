"""
Base settings for ClubCMS project.
Common settings shared across all environments.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-change-me-in-production"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# --------------------------------------------------------------------------
# Application definition
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.sitemaps",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.admin",
    "wagtail",
    # Multi-language
    "wagtail_localize",
    "wagtail_localize.locales",
    # Utilities
    "taggit",
    "modelcluster",
    # Project apps
    "apps.core",
    "apps.website",
    "apps.members",
    "apps.events",
    "apps.federation",
    "apps.notifications",
    "apps.mutual_aid",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "clubcms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "apps.core.context_processors.theme_context",
            ],
        },
    },
]

WSGI_APPLICATION = "clubcms.wsgi.application"

# --------------------------------------------------------------------------
# Database
# --------------------------------------------------------------------------

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgres://postgres:postgres@db:5432/clubcms"
)

# Parse DATABASE_URL
_db_url = DATABASE_URL
if _db_url.startswith("postgres://"):
    _db_url_parts = _db_url.replace("postgres://", "").split("@")
    _user_pass = _db_url_parts[0].split(":")
    _host_db = _db_url_parts[1].split("/")
    _host_port = _host_db[0].split(":")

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _host_db[1] if len(_host_db) > 1 else "clubcms",
            "USER": _user_pass[0],
            "PASSWORD": _user_pass[1] if len(_user_pass) > 1 else "",
            "HOST": _host_port[0],
            "PORT": _host_port[1] if len(_host_port) > 1 else "5432",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --------------------------------------------------------------------------
# Custom user model
# --------------------------------------------------------------------------

AUTH_USER_MODEL = "members.ClubUser"

# --------------------------------------------------------------------------
# Password validation
# --------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------------------------------
# Authentication backends
# --------------------------------------------------------------------------

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# --------------------------------------------------------------------------
# django-allauth (optional — activated if installed)
# --------------------------------------------------------------------------

try:
    import allauth  # noqa: F401

    INSTALLED_APPS += [
        "django.contrib.sites",
        "allauth",
        "allauth.account",
        "allauth.socialaccount",
    ]

    AUTHENTICATION_BACKENDS += [
        "allauth.account.auth_backends.AuthenticationBackend",
    ]

    MIDDLEWARE += [
        "allauth.account.middleware.AccountMiddleware",
    ]

    SITE_ID = 1

    # allauth configuration
    ACCOUNT_LOGIN_METHODS = {"email", "username"}
    ACCOUNT_SIGNUP_FIELDS = [
        "email*",
        "username*",
        "password1*",
        "password2*",
    ]
    ACCOUNT_EMAIL_VERIFICATION = "optional"
    ACCOUNT_SESSION_REMEMBER = True
    ACCOUNT_UNIQUE_EMAIL = True
    ACCOUNT_LOGIN_ON_PASSWORD_RESET = True
    ACCOUNT_LOGOUT_ON_GET = False
    ACCOUNT_FORMS = {
        "signup": "apps.members.forms.RegistrationForm",
    }

except ImportError:
    pass

# --------------------------------------------------------------------------
# Internationalization
# --------------------------------------------------------------------------

LANGUAGE_CODE = "it"
TIME_ZONE = "Europe/Rome"
USE_I18N = True
USE_L10N = True
USE_TZ = True

WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("it", "Italiano"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("fr", "Francais"),
    ("es", "Espanol"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# --------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# --------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# --------------------------------------------------------------------------
# Default primary key field type
# --------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------------------------------
# Wagtail settings
# --------------------------------------------------------------------------

WAGTAIL_SITE_NAME = "Club CMS"
WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL", "http://localhost:8000"
)

# --------------------------------------------------------------------------
# Email
# --------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "noreply@example.com"
)

# --------------------------------------------------------------------------
# Federation settings
# --------------------------------------------------------------------------

FEDERATION_ENABLED = os.environ.get(
    "FEDERATION_ENABLED", "False"
).lower() in ("true", "1", "yes")

FEDERATION_OUR_CLUB_CODE = os.environ.get("FEDERATION_OUR_CLUB_CODE", "")
FEDERATION_OUR_CLUB_NAME = os.environ.get("FEDERATION_OUR_CLUB_NAME", "")

FEDERATION_SETTINGS = {
    "SYNC_INTERVAL": 60 * 60 * 2,
    "REQUEST_MAX_AGE": 300,
    "MAX_EVENTS_PER_SYNC": 100,
    "SHARE_INTEREST_COUNTS": True,
    "INTEREST_SYNC_INTERVAL": 60 * 15,
    "FETCH_FUTURE_DAYS": 365,
    "RATE_LIMIT_REQUESTS": 60,
}

# --------------------------------------------------------------------------
# Background tasks (django-q2)
# --------------------------------------------------------------------------

Q_CLUSTER = {
    "name": "clubcms",
    "workers": 2,
    "recycle": 500,
    "timeout": 60,
    "retry": 120,
    "queue_limit": 50,
    "bulk": 10,
    "orm": "default",
}

# --------------------------------------------------------------------------
# Push notifications (VAPID)
# --------------------------------------------------------------------------

WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": os.environ.get("VAPID_PUBLIC_KEY", ""),
    "VAPID_PRIVATE_KEY": os.environ.get("VAPID_PRIVATE_KEY", ""),
    "VAPID_ADMIN_EMAIL": os.environ.get("VAPID_ADMIN_EMAIL", ""),
}

# --------------------------------------------------------------------------
# Login / Logout
# --------------------------------------------------------------------------

LOGIN_REDIRECT_URL = "/account/profile/"
LOGOUT_REDIRECT_URL = "/"

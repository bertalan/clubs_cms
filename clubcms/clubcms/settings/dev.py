"""
Development settings for ClubCMS.
"""

from .base import *  # noqa: F401, F403
from pathlib import Path

DEBUG = True

ALLOWED_HOSTS = ["*"]

SECRET_KEY = "django-insecure-dev-only-key-do-not-use-in-production"

# Use SQLite for local development unless DATABASE_URL is set (e.g. Docker)
import os
if not os.environ.get("DATABASE_URL", "").startswith("postgres"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(__file__).resolve().parent.parent.parent / "db.sqlite3",
        }
    }

# Console email in development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Debug toolbar (when installed)
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

"""
Production deployment readiness checks.

Verifies that prod settings are secure and all deployment
prerequisites are met without actually loading prod settings.
"""

import os
from pathlib import Path

import pytest
from django.test import TestCase


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class TestProductionSettings(TestCase):
    """Verify production settings file has required security settings."""

    def setUp(self):
        prod_path = BASE_DIR / "clubcms" / "settings" / "prod.py"
        self.prod_content = prod_path.read_text()

    def test_debug_false(self):
        self.assertIn("DEBUG = False", self.prod_content)

    def test_secret_key_from_env(self):
        # Must use env var, not hardcoded
        self.assertIn('os.environ["SECRET_KEY"]', self.prod_content)
        self.assertNotIn("django-insecure", self.prod_content)

    def test_ssl_redirect(self):
        self.assertIn("SECURE_SSL_REDIRECT = True", self.prod_content)

    def test_hsts(self):
        self.assertIn("SECURE_HSTS_SECONDS", self.prod_content)
        # Must be at least 1 year
        self.assertIn("31536000", self.prod_content)

    def test_secure_cookies(self):
        self.assertIn("SESSION_COOKIE_SECURE = True", self.prod_content)
        self.assertIn("CSRF_COOKIE_SECURE = True", self.prod_content)

    def test_csrf_cookie_httponly(self):
        self.assertIn("CSRF_COOKIE_HTTPONLY = True", self.prod_content)

    def test_x_frame_options(self):
        self.assertIn('X_FRAME_OPTIONS = "DENY"', self.prod_content)

    def test_allowed_hosts_from_env(self):
        self.assertIn("ALLOWED_HOSTS", self.prod_content)
        self.assertIn("os.environ", self.prod_content)

    def test_email_backend_smtp(self):
        self.assertIn("smtp.EmailBackend", self.prod_content)

    def test_whitenoise_configured(self):
        self.assertIn("WhiteNoiseMiddleware", self.prod_content)
        self.assertIn("CompressedManifestStaticFilesStorage", self.prod_content)


class TestStaticFiles(TestCase):
    """Verify static assets exist for deployment."""

    def test_base_css_exists(self):
        css = BASE_DIR / "static" / "css" / "base.css"
        self.assertTrue(css.exists(), "base.css must exist")

    def test_all_theme_css_exist(self):
        themes = ["velocity", "heritage", "terra", "zen", "clubs", "tricolore"]
        for theme in themes:
            css = BASE_DIR / "static" / "css" / "themes" / theme / "main.css"
            self.assertTrue(css.exists(), f"Theme CSS missing: {theme}")


class TestTranslations(TestCase):
    """Verify translation files are compiled."""

    def test_mo_files_exist(self):
        languages = ["it", "en", "de", "fr", "es"]
        for lang in languages:
            mo = BASE_DIR / "locale" / lang / "LC_MESSAGES" / "django.mo"
            self.assertTrue(mo.exists(), f"Compiled translation missing: {lang}")

    def test_po_files_exist(self):
        languages = ["it", "en", "de", "fr", "es"]
        for lang in languages:
            po = BASE_DIR / "locale" / lang / "LC_MESSAGES" / "django.po"
            self.assertTrue(po.exists(), f"Source translation missing: {lang}")


class TestDockerfiles(TestCase):
    """Verify Docker deployment files exist."""

    def test_dockerfile_exists(self):
        self.assertTrue(
            (BASE_DIR / "Dockerfile").exists(),
            "Dockerfile must exist",
        )

    def test_docker_compose_exists(self):
        self.assertTrue(
            (BASE_DIR / "docker-compose.yml").exists(),
            "docker-compose.yml must exist",
        )

    def test_entrypoint_exists(self):
        self.assertTrue(
            (BASE_DIR / "entrypoint.sh").exists(),
            "entrypoint.sh must exist",
        )

    def test_requirements_exists(self):
        self.assertTrue(
            (BASE_DIR / "requirements.txt").exists(),
            "requirements.txt must exist",
        )


class TestSecurityMiddleware(TestCase):
    """Verify security middleware is in dev settings (base)."""

    def test_security_middleware_present(self):
        from django.conf import settings
        self.assertIn(
            "django.middleware.security.SecurityMiddleware",
            settings.MIDDLEWARE,
        )

    def test_csrf_middleware_present(self):
        from django.conf import settings
        self.assertIn(
            "django.middleware.csrf.CsrfViewMiddleware",
            settings.MIDDLEWARE,
        )

    def test_clickjacking_middleware_present(self):
        from django.conf import settings
        self.assertIn(
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            settings.MIDDLEWARE,
        )

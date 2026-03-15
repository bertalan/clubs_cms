"""
T08 — Test fix critici: django_q, health endpoint, email verification, WSGI.

Verifica:
- django_q in INSTALLED_APPS
- /health/ risponde 200 con JSON {"status": "ok"}
- ACCOUNT_EMAIL_VERIFICATION = "mandatory"
- WSGI default punta a settings.prod
"""

import json

import pytest
from django.conf import settings
from django.test import TestCase, override_settings


@pytest.mark.django_db
class TestDjangoQInstalled(TestCase):
    """django_q must be in INSTALLED_APPS for background tasks."""

    def test_django_q_in_installed_apps(self):
        self.assertIn("django_q", settings.INSTALLED_APPS)

    def test_q_cluster_configured(self):
        self.assertTrue(hasattr(settings, "Q_CLUSTER"))
        self.assertEqual(settings.Q_CLUSTER["name"], "clubcms")
        self.assertEqual(settings.Q_CLUSTER["orm"], "default")


class TestHealthEndpoint(TestCase):
    """GET /health/ must return 200 with JSON status."""

    def test_health_returns_200(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp.status_code, 200)

    def test_health_returns_json(self):
        resp = self.client.get("/health/")
        data = json.loads(resp.content)
        self.assertEqual(data["status"], "ok")

    def test_health_content_type(self):
        resp = self.client.get("/health/")
        self.assertEqual(resp["Content-Type"], "application/json")

    def test_health_includes_db_check(self):
        resp = self.client.get("/health/")
        data = json.loads(resp.content)
        self.assertIn("database", data)
        self.assertEqual(data["database"], "ok")


class TestEmailVerification(TestCase):
    """Email verification should be mandatory for production readiness."""

    def test_email_verification_mandatory(self):
        verification = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", None)
        self.assertEqual(
            verification,
            "mandatory",
            "ACCOUNT_EMAIL_VERIFICATION must be 'mandatory' for production",
        )


class TestWSGIDefault(TestCase):
    """WSGI must default to prod settings, not dev."""

    def test_wsgi_defaults_to_prod(self):
        import ast
        from pathlib import Path

        wsgi_path = Path(settings.BASE_DIR).parent / "clubcms" / "wsgi.py"
        if not wsgi_path.exists():
            wsgi_path = Path(settings.BASE_DIR) / "clubcms" / "wsgi.py"

        content = wsgi_path.read_text()
        self.assertIn(
            "clubcms.settings.prod",
            content,
            "wsgi.py should default to prod settings",
        )
        self.assertNotIn(
            'setdefault("DJANGO_SETTINGS_MODULE", "clubcms.settings.dev")',
            content,
            "wsgi.py must NOT default to dev settings",
        )

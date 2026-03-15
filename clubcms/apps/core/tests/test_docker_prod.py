"""
T09 — Test configurazione Docker produzione.

Verifica che i file di deploy esistano e siano correttamente configurati.
"""

from pathlib import Path

from django.conf import settings
from django.test import TestCase


class TestDockerProdFiles(TestCase):
    """Verify production deployment files exist and are correct."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # In Docker: BASE_DIR=/app (files mounted here).
        # Locally: BASE_DIR=.../clubcms, files also inside clubcms/.
        cls.base = Path(settings.BASE_DIR)

    def test_docker_compose_prod_exists(self):
        path = self.base / "docker-compose.prod.yml"
        self.assertTrue(path.exists(), "docker-compose.prod.yml missing")

    def test_docker_compose_prod_has_gunicorn(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("gunicorn", content)

    def test_docker_compose_prod_has_healthcheck(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("healthcheck", content)
        self.assertIn("/health/", content)

    def test_docker_compose_prod_has_qcluster(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("qcluster", content)
        self.assertIn("manage.py qcluster", content)

    def test_docker_compose_prod_uses_prod_settings(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("clubcms.settings.prod", content)

    def test_docker_compose_prod_has_env_file(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("env_file", content)

    def test_docker_compose_prod_restart_policy(self):
        content = (self.base / "docker-compose.prod.yml").read_text()
        self.assertIn("unless-stopped", content)

    def test_nginx_conf_exists(self):
        path = self.base / "deploy" / "nginx.conf"
        self.assertTrue(path.exists(), "deploy/nginx.conf missing")

    def test_nginx_has_ssl(self):
        content = (self.base / "deploy" / "nginx.conf").read_text()
        self.assertIn("ssl_certificate", content)
        self.assertIn("443", content)

    def test_nginx_has_static_media(self):
        content = (self.base / "deploy" / "nginx.conf").read_text()
        self.assertIn("/static/", content)
        self.assertIn("/media/", content)

    def test_nginx_has_security_headers(self):
        content = (self.base / "deploy" / "nginx.conf").read_text()
        self.assertIn("X-Frame-Options", content)
        self.assertIn("X-Content-Type-Options", content)
        self.assertIn("Strict-Transport-Security", content)

    def test_nginx_proxies_to_django(self):
        content = (self.base / "deploy" / "nginx.conf").read_text()
        self.assertIn("proxy_pass", content)
        self.assertIn("X-Forwarded-For", content)

    def test_deploy_script_exists(self):
        path = self.base / "deploy" / "deploy.sh"
        self.assertTrue(path.exists(), "deploy/deploy.sh missing")

    def test_deploy_script_executable(self):
        import os
        path = self.base / "deploy" / "deploy.sh"
        self.assertTrue(os.access(path, os.X_OK), "deploy.sh not executable")

    def test_deploy_script_has_backup(self):
        content = (self.base / "deploy" / "deploy.sh").read_text()
        self.assertIn("pg_dump", content)
        self.assertIn("backup", content.lower())

    def test_deploy_script_has_migrate(self):
        content = (self.base / "deploy" / "deploy.sh").read_text()
        self.assertIn("migrate", content)

    def test_deploy_script_has_collectstatic(self):
        content = (self.base / "deploy" / "deploy.sh").read_text()
        self.assertIn("collectstatic", content)

    def test_deploy_script_has_health_check(self):
        content = (self.base / "deploy" / "deploy.sh").read_text()
        self.assertIn("health", content.lower())

    def test_backup_script_exists(self):
        path = self.base / "deploy" / "backup.sh"
        self.assertTrue(path.exists(), "deploy/backup.sh missing")

    def test_env_prod_example_exists(self):
        path = self.base / ".env.prod.example"
        self.assertTrue(path.exists(), ".env.prod.example missing")

    def test_env_prod_has_required_vars(self):
        content = (self.base / ".env.prod.example").read_text()
        for var in ["SECRET_KEY", "POSTGRES_PASSWORD", "DATABASE_URL",
                     "ALLOWED_HOSTS", "EMAIL_HOST", "DOMAIN"]:
            self.assertIn(var, content, f"{var} missing from .env.prod.example")

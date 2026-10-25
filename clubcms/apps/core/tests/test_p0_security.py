"""
P0 security fixes (2026-10-25).

- Shared cache: rate limits must work across gunicorn workers and qcluster,
  so the default cache cannot be per-process (LocMemCache).
- Client IP: only trust X-Real-IP set by a local reverse proxy; the
  client-controlled X-Forwarded-For must never be used.
- Photo upload: the format is decided by the file content (Pillow), never by
  the declared content type or the file extension.
- Production settings: empty env values must not produce [""] lists.
"""

import io
from pathlib import Path

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from PIL import Image

from apps.core.http import get_client_ip
from apps.website.forms import PhotoUploadForm
from clubcms.settings.base import env_list

APP_DIR = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Shared cache
# ---------------------------------------------------------------------------


def test_default_cache_is_shared_database_cache():
    assert (
        settings.CACHES["default"]["BACKEND"]
        == "django.core.cache.backends.db.DatabaseCache"
    )


def test_deploy_creates_cache_table():
    deploy = (APP_DIR / "deploy" / "clubs.betabi.it" / "deploy.sh").read_text()
    assert "manage.py createcachetable" in deploy


# ---------------------------------------------------------------------------
# env_list
# ---------------------------------------------------------------------------


def test_env_list_drops_empty_values(monkeypatch):
    monkeypatch.setenv("CLUBCMS_TEST_LIST", "")
    assert env_list("CLUBCMS_TEST_LIST") == []
    monkeypatch.setenv("CLUBCMS_TEST_LIST", " a.example , ,b.example,")
    assert env_list("CLUBCMS_TEST_LIST") == ["a.example", "b.example"]


def test_env_list_default(monkeypatch):
    monkeypatch.delenv("CLUBCMS_TEST_LIST", raising=False)
    assert env_list("CLUBCMS_TEST_LIST", "x,y") == ["x", "y"]


def test_prod_settings_use_env_list():
    prod = (APP_DIR / "clubcms" / "settings" / "prod.py").read_text()
    assert 'ALLOWED_HOSTS = env_list("ALLOWED_HOSTS")' in prod
    assert 'CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")' in prod


# ---------------------------------------------------------------------------
# Client IP
# ---------------------------------------------------------------------------


@override_settings(TRUSTED_PROXY_IPS=["127.0.0.1", "::1"])
class TestGetClientIp(TestCase):
    def setUp(self):
        self.rf = RequestFactory()

    def test_direct_client_uses_remote_addr(self):
        request = self.rf.get("/", REMOTE_ADDR="203.0.113.9")
        self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_spoofed_forwarded_for_is_ignored(self):
        request = self.rf.get(
            "/",
            REMOTE_ADDR="127.0.0.1",
            HTTP_X_FORWARDED_FOR="198.51.100.66, 203.0.113.9",
            HTTP_X_REAL_IP="203.0.113.9",
        )
        self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_real_ip_from_trusted_proxy(self):
        request = self.rf.get("/", REMOTE_ADDR="::1", HTTP_X_REAL_IP="2001:db8::7")
        self.assertEqual(get_client_ip(request), "2001:db8::7")

    def test_real_ip_from_untrusted_peer_is_ignored(self):
        request = self.rf.get(
            "/", REMOTE_ADDR="203.0.113.9", HTTP_X_REAL_IP="198.51.100.66"
        )
        self.assertEqual(get_client_ip(request), "203.0.113.9")

    def test_invalid_real_ip_falls_back(self):
        request = self.rf.get("/", REMOTE_ADDR="127.0.0.1", HTTP_X_REAL_IP="nope")
        self.assertEqual(get_client_ip(request), "127.0.0.1")


# ---------------------------------------------------------------------------
# Photo upload format detection
# ---------------------------------------------------------------------------


def _image_bytes(fmt):
    buf = io.BytesIO()
    Image.new("RGB", (4, 4), (200, 30, 30)).save(buf, format=fmt)
    return buf.getvalue()


def _clean(files):
    form = PhotoUploadForm(data={}, files={"photos": files})
    form.cleaned_data = {"photos": files}
    return form.clean_photos()


@pytest.mark.parametrize(
    "fmt,name,ctype",
    [
        ("PNG", "a.png", "image/png"),
        ("JPEG", "a.jpg", "image/jpeg"),
        ("WEBP", "a.webp", "image/webp"),
    ],
)
def test_real_allowed_images_pass(fmt, name, ctype):
    files = [SimpleUploadedFile(name, _image_bytes(fmt), content_type=ctype)]
    assert _clean(files) == files
    assert files[0].tell() == 0


@pytest.mark.parametrize(
    "payload,name,ctype",
    [
        # Declared as PNG by the client, but it is not an image.
        (b"<?php system($_GET['c']); ?>", "shell.png", "image/png"),
        # Unknown content with an allowed extension.
        (b"just some text", "evil.jpg", "application/octet-stream"),
    ],
)
def test_non_images_are_rejected(payload, name, ctype):
    with pytest.raises(ValidationError):
        _clean([SimpleUploadedFile(name, payload, content_type=ctype)])


def test_real_but_disallowed_format_is_rejected():
    gif = SimpleUploadedFile("a.gif", _image_bytes("GIF"), content_type="image/png")
    with pytest.raises(ValidationError):
        _clean([gif])


def test_forms_module_no_longer_uses_imghdr():
    forms_src = (APP_DIR / "apps" / "website" / "forms.py").read_text()
    assert "imghdr" not in forms_src


# ---------------------------------------------------------------------------
# Demo members: no password published in the repository
# ---------------------------------------------------------------------------


def test_demo_member_password_from_env(monkeypatch):
    from apps.core.demo.loader import demo_member_password

    monkeypatch.setenv("DEMO_MEMBER_PASSWORD", "local-only-secret")
    assert demo_member_password() == "local-only-secret"


def test_demo_member_password_absent_means_no_login(monkeypatch):
    from apps.core.demo.loader import demo_member_password

    monkeypatch.delenv("DEMO_MEMBER_PASSWORD", raising=False)
    assert demo_member_password() is None
    monkeypatch.setenv("DEMO_MEMBER_PASSWORD", "  ")
    assert demo_member_password() is None


def test_loader_has_no_hardcoded_member_password():
    loader_src = (APP_DIR / "apps" / "core" / "demo" / "loader.py").read_text()
    assert 'set_password("' not in loader_src

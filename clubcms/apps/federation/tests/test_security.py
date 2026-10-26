"""
Tests for federation API security (HMAC signing/verification, v2),
HTML sanitization (bleach), and API key generation.

These are unit tests — no Django database required.
"""

from datetime import datetime, timedelta, timezone

import pytest

from apps.federation.api.security import build_signed_request, sign_request, verify_request
from apps.federation.utils import (
    generate_public_key,
    generate_secret_key,
    sanitize_html,
)

PATH = "/api/federation/events/?from_date=2026-01-01"
NONCE = "n" * 24


def _ts(seconds=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat()


# ──────────────────────────────────────────────────────────────────────
# 1. sign_request
# ──────────────────────────────────────────────────────────────────────


class TestSignRequest:
    """Tests for HMAC-SHA256 request signing."""

    def test_produces_sha256_prefix(self):
        assert sign_request("secret", "GET", PATH, _ts(), NONCE).startswith("sha256=")

    def test_deterministic(self):
        ts = _ts()
        assert sign_request("k", "POST", PATH, ts, NONCE, b"x") == sign_request(
            "k", "POST", PATH, ts, NONCE, b"x"
        )

    @pytest.mark.parametrize(
        "changed",
        [
            {"secret": "other"},
            {"method": "POST"},
            {"path": "/api/federation/interest/"},
            {"path": "/api/federation/events/?from_date=2020-01-01"},
            {"nonce": "m" * 24},
            {"body": b"{}"},
        ],
    )
    def test_every_part_is_signed(self, changed):
        ts = _ts()
        base = {"secret": "k", "method": "GET", "path": PATH, "nonce": NONCE, "body": b""}
        other = {**base, **changed}
        assert sign_request(timestamp=ts, **base) != sign_request(timestamp=ts, **other)


# ──────────────────────────────────────────────────────────────────────
# 2. verify_request
# ──────────────────────────────────────────────────────────────────────


class TestVerifyRequest:
    """Tests for HMAC-SHA256 request verification."""

    def _verify(self, secret="secret", method="GET", path=PATH, ts=None, nonce=NONCE,
                body=b"", sig=None, **kwargs):
        ts = ts or _ts()
        sig = sig or sign_request("secret", "GET", PATH, ts, NONCE, b"")
        return verify_request(secret, method, path, ts, nonce, sig, body, **kwargs)

    def test_valid(self):
        assert self._verify() is True

    def test_wrong_secret(self):
        assert self._verify(secret="wrong") is False

    def test_wrong_signature(self):
        assert self._verify(sig="sha256=0000bad") is False

    def test_signature_bound_to_path(self):
        assert self._verify(path="/api/federation/interest/") is False

    def test_signature_bound_to_method(self):
        assert self._verify(method="POST") is False

    def test_tampered_body(self):
        assert self._verify(body=b'{"ok":false}') is False

    def test_expired_timestamp(self):
        ts = _ts(-600)
        sig = sign_request("secret", "GET", PATH, ts, NONCE)
        assert self._verify(ts=ts, sig=sig) is False

    def test_future_timestamp(self):
        ts = _ts(600)
        sig = sign_request("secret", "GET", PATH, ts, NONCE)
        assert self._verify(ts=ts, sig=sig) is False

    def test_invalid_timestamp_format(self):
        assert self._verify(ts="not-a-date") is False

    @pytest.mark.parametrize("nonce", ["", "short", "x" * 65, "bad nonce with spaces!"])
    def test_malformed_nonce(self, nonce):
        ts = _ts()
        sig = sign_request("secret", "GET", PATH, ts, nonce)
        assert self._verify(ts=ts, nonce=nonce, sig=sig) is False

    @pytest.mark.parametrize("secret", ["", "   "])
    def test_empty_secret_never_authenticates(self, secret):
        ts = _ts()
        sig = sign_request(secret, "GET", PATH, ts, NONCE)
        assert verify_request(secret, "GET", PATH, ts, NONCE, sig) is False

    def test_custom_max_age(self):
        ts = _ts(-10)
        sig = sign_request("secret", "GET", PATH, ts, NONCE)
        assert self._verify(ts=ts, sig=sig, max_age=60) is True
        assert self._verify(ts=ts, sig=sig, max_age=1) is False


class TestBuildSignedRequest:
    def test_round_trip(self):
        req = build_signed_request(
            "https://partner.example" + PATH, "pk_x", "sk_x", method="POST", body=b'{"a":1}'
        )
        assert req.get_header("X-federation-key") == "pk_x"
        assert req.get_header("Content-type") == "application/json"
        assert verify_request(
            "sk_x", "POST", PATH,
            req.get_header("X-timestamp"), req.get_header("X-nonce"),
            req.get_header("X-signature"), b'{"a":1}',
        )

    def test_nonce_changes_every_request(self):
        url = "https://partner.example" + PATH
        first = build_signed_request(url, "pk_x", "sk_x").get_header("X-nonce")
        second = build_signed_request(url, "pk_x", "sk_x").get_header("X-nonce")
        assert first != second


# ──────────────────────────────────────────────────────────────────────
# 3. sanitize_html (bleach-based — validates FIX C-1)
# ──────────────────────────────────────────────────────────────────────


class TestSanitizeHtml:
    """Tests for bleach-based HTML sanitization of federated content."""

    def test_strips_script(self):
        result = sanitize_html('<p>Hello</p><script>alert(1)</script>')
        assert "<script>" not in result
        assert "</script>" not in result
        # bleach strips tags but leaves text content (safe as plain text)
        assert "<p>Hello</p>" in result

    def test_strips_onerror(self):
        result = sanitize_html('<img onerror="alert(1)" src="x">')
        assert "onerror" not in result
        assert "alert" not in result

    def test_strips_iframe(self):
        result = sanitize_html('<iframe src="https://evil.com"></iframe>')
        assert "<iframe" not in result

    def test_strips_style(self):
        result = sanitize_html('<style>body{display:none}</style><p>Ok</p>')
        assert "<style>" not in result
        assert "<p>Ok</p>" in result

    def test_strips_svg(self):
        result = sanitize_html('<svg onload="alert(1)"><circle/></svg>')
        assert "<svg" not in result
        assert "onload" not in result

    def test_strips_javascript_uri(self):
        result = sanitize_html('<a href="javascript:alert(1)">Click</a>')
        assert "javascript:" not in result

    def test_preserves_allowed_tags(self):
        html = '<p>Hello <b>world</b></p><a href="https://example.com">link</a>'
        result = sanitize_html(html)
        assert "<p>" in result
        assert "<b>" in result
        assert '<a href="https://example.com">' in result

    def test_preserves_allowed_attributes(self):
        html = '<a href="https://ex.com" title="Example" rel="noopener">go</a>'
        result = sanitize_html(html)
        assert 'title="Example"' in result
        assert 'rel="noopener"' in result

    def test_strips_data_uri(self):
        result = sanitize_html('<a href="data:text/html,<script>alert(1)</script>">x</a>')
        assert "data:" not in result

    def test_empty_input(self):
        assert sanitize_html("") == ""

    def test_none_input(self):
        assert sanitize_html(None) == ""

    def test_nested_xss(self):
        # Nested / obfuscated XSS attempts
        payloads = [
            '<div onmouseover="alert(1)">hover</div>',
            '<img src=x onerror=alert(1)>',
            '<body onload="alert(1)">',
            '<object data="javascript:alert(1)">',
            '<embed src="javascript:alert(1)">',
            '<form action="javascript:alert(1)"><input type=submit></form>',
            '<math><mtext><table><mglyph><style><!--</style>'
            '<img title="--&gt;&lt;img src=1 onerror=alert(1)&gt;">',
        ]
        for payload in payloads:
            result = sanitize_html(payload)
            assert "alert(1)" not in result, f"XSS not stripped: {payload}"
            assert "javascript:" not in result, f"JS URI not stripped: {payload}"


# ──────────────────────────────────────────────────────────────────────
# 4. Key generation
# ──────────────────────────────────────────────────────────────────────


class TestKeyGeneration:
    """Tests for federation API key generation."""

    def test_public_key_prefix(self):
        assert generate_public_key().startswith("pk_")

    def test_secret_key_prefix(self):
        assert generate_secret_key().startswith("sk_")

    def test_public_key_unique(self):
        k1 = generate_public_key()
        k2 = generate_public_key()
        assert k1 != k2

    def test_secret_key_longer_than_public(self):
        pk = generate_public_key()
        sk = generate_secret_key()
        assert len(sk) > len(pk)

    def test_generated_values_fit_the_model_fields(self):
        from apps.federation.models import FederatedClub

        for name, value in [
            ("inbound_key", generate_public_key()),
            ("outbound_key", generate_public_key()),
            ("inbound_secret", generate_secret_key()),
            ("outbound_secret", generate_secret_key()),
        ]:
            assert len(value) <= FederatedClub._meta.get_field(name).max_length, name

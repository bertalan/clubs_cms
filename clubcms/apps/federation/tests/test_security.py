"""
Tests for federation API security (HMAC signing/verification),
HTML sanitization (bleach), and API key generation.

These are unit tests — no Django database required.
"""

from datetime import datetime, timedelta, timezone

import pytest

from apps.federation.api.security import sign_request, verify_request
from apps.federation.utils import (
    generate_api_key_pair,
    generate_public_key,
    generate_secret_key,
    sanitize_html,
)


# ──────────────────────────────────────────────────────────────────────
# 1. sign_request
# ──────────────────────────────────────────────────────────────────────


class TestSignRequest:
    """Tests for HMAC-SHA256 request signing."""

    def test_produces_sha256_prefix(self):
        sig = sign_request("secret", "2025-01-01T00:00:00Z")
        assert sig.startswith("sha256=")

    def test_deterministic(self):
        sig1 = sign_request("key", "2025-06-01T12:00:00Z", "body")
        sig2 = sign_request("key", "2025-06-01T12:00:00Z", "body")
        assert sig1 == sig2

    def test_different_keys_different_sigs(self):
        ts = "2025-06-01T12:00:00Z"
        sig_a = sign_request("alpha", ts)
        sig_b = sign_request("bravo", ts)
        assert sig_a != sig_b

    def test_with_body(self):
        ts = "2025-06-01T12:00:00Z"
        sig_empty = sign_request("key", ts, "")
        sig_body = sign_request("key", ts, '{"event_id":"1"}')
        assert sig_empty != sig_body

    def test_empty_body(self):
        sig = sign_request("key", "2025-06-01T00:00:00Z", "")
        assert isinstance(sig, str)
        assert len(sig) > len("sha256=")


# ──────────────────────────────────────────────────────────────────────
# 2. verify_request
# ──────────────────────────────────────────────────────────────────────


class TestVerifyRequest:
    """Tests for HMAC-SHA256 request verification."""

    def _fresh_ts(self):
        """Return a current UTC ISO timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def test_valid(self):
        key = "test-secret-key"
        ts = self._fresh_ts()
        body = '{"hello":"world"}'
        sig = sign_request(key, ts, body)
        assert verify_request(key, ts, sig, body) is True

    def test_wrong_key(self):
        ts = self._fresh_ts()
        sig = sign_request("correct-key", ts)
        assert verify_request("wrong-key", ts, sig) is False

    def test_wrong_signature(self):
        ts = self._fresh_ts()
        assert verify_request("key", ts, "sha256=0000bad") is False

    def test_tampered_body(self):
        key = "secret"
        ts = self._fresh_ts()
        sig = sign_request(key, ts, '{"ok":true}')
        assert verify_request(key, ts, sig, '{"ok":false}') is False

    def test_expired_timestamp(self):
        key = "secret"
        old_ts = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
        sig = sign_request(key, old_ts)
        assert verify_request(key, old_ts, sig, max_age=300) is False

    def test_future_timestamp(self):
        key = "secret"
        future_ts = (datetime.now(timezone.utc) + timedelta(seconds=600)).isoformat()
        sig = sign_request(key, future_ts)
        assert verify_request(key, future_ts, sig, max_age=300) is False

    def test_invalid_timestamp_format(self):
        assert verify_request("key", "not-a-date", "sha256=abc") is False

    def test_replay_attack(self):
        """Same signature cannot authenticate a different body."""
        key = "secret"
        ts = self._fresh_ts()
        sig = sign_request(key, ts, "legit-body")
        assert verify_request(key, ts, sig, "evil-body") is False

    def test_custom_max_age(self):
        key = "secret"
        ts = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
        sig = sign_request(key, ts)
        # Should pass with large max_age
        assert verify_request(key, ts, sig, max_age=60) is True
        # Should fail with tiny max_age
        assert verify_request(key, ts, sig, max_age=1) is False


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

    def test_api_key_pair_returns_tuple(self):
        pair = generate_api_key_pair()
        assert isinstance(pair, tuple)
        assert len(pair) == 2
        pk, sk = pair
        assert pk.startswith("pk_")
        assert sk.startswith("sk_")

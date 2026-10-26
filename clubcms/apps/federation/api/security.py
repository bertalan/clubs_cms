"""
Federation API security: request signing and verification.

Every request carries four headers:

- ``X-Federation-Key``: the access key the receiving club issued to us.
- ``X-Timestamp``: ISO 8601 UTC time of the request.
- ``X-Nonce``: random value, accepted only once.
- ``X-Signature``: ``sha256=`` + HMAC-SHA256, with the secret paired to the
  key, of the canonical string::

      METHOD \\n PATH?QUERY \\n TIMESTAMP \\n NONCE \\n SHA256(BODY)

Signing method, path and query binds a signature to one endpoint and one
set of parameters; the nonce stops replays within the timestamp window.
"""

import hashlib
import hmac
import re
import secrets
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

from django.core.cache import cache

MAX_AGE = 300  # seconds a signed request stays valid
NONCE_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")
USER_AGENT = "ClubCMS-Federation/2.0"


def _canonical(method, path, timestamp, nonce, body):
    body_hash = hashlib.sha256(body or b"").hexdigest()
    return "\n".join([method.upper(), path, timestamp, nonce, body_hash])


def sign_request(secret, method, path, timestamp, nonce, body=b""):
    """
    HMAC-SHA256 signature of a federation request.

    ``path`` includes the query string (``/api/federation/events/?from_date=…``);
    ``body`` is the raw request body in bytes.
    """
    message = _canonical(method, path, timestamp, nonce, body)
    digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def verify_request(secret, method, path, timestamp, nonce, signature, body=b"", max_age=MAX_AGE):
    """
    True if the signature matches and the timestamp is within ``max_age``.

    Does not check the nonce for reuse: see ``claim_nonce``.
    """
    # An empty secret authenticates nothing.
    if not secret or not secret.strip():
        return False
    if not NONCE_RE.match(nonce or ""):
        return False

    try:
        request_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - request_time).total_seconds()
        if abs(age) > max_age:
            return False
    except (ValueError, TypeError, AttributeError):
        return False

    expected = sign_request(secret, method, path, timestamp, nonce, body)
    return hmac.compare_digest(signature or "", expected)


def claim_nonce(club_pk, nonce, max_age=MAX_AGE):
    """
    Record a nonce for this partner. False if it was already used.

    The nonce is kept for twice ``max_age``, enough to cover any timestamp
    still accepted by ``verify_request``. Needs the shared cache.
    """
    return cache.add(f"federation_nonce_{club_pk}_{nonce}", True, timeout=2 * max_age)


def build_signed_request(url, key, secret, method="GET", body=None):
    """``urllib`` request to a partner, signed with the credential it issued us."""
    parts = urlsplit(url)
    path = parts.path + (f"?{parts.query}" if parts.query else "")
    timestamp = datetime.now(timezone.utc).isoformat()
    nonce = secrets.token_urlsafe(18)
    headers = {
        "X-Federation-Key": key,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": sign_request(secret, method, path, timestamp, nonce, body or b""),
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    return urllib.request.Request(url, data=body, headers=headers, method=method)

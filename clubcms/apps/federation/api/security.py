"""
Federation API security: request signing and verification.
"""

import hashlib
import hmac
from datetime import datetime, timezone


def sign_request(secret_key: str, timestamp: str, body: str = "") -> str:
    """
    Create HMAC-SHA256 signature for a federation API request.
    """
    message = f"{timestamp}:{body}"
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={signature}"


def verify_request(api_key: str, timestamp: str, signature: str, body: str = "", max_age: int = 300) -> bool:
    """
    Verify a signed federation API request.

    Args:
        api_key: The shared secret key.
        timestamp: ISO 8601 timestamp from the request header.
        signature: The provided signature from the request header.
        body: The request body as string.
        max_age: Maximum allowed age of the request in seconds.

    Returns:
        True if the request is valid, False otherwise.
    """
    # Check timestamp age
    try:
        request_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - request_time).total_seconds()
        if abs(age) > max_age:
            return False
    except (ValueError, TypeError):
        return False

    # Verify signature
    expected = sign_request(api_key, timestamp, body)
    return hmac.compare_digest(signature, expected)

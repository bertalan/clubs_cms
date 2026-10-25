"""
HTTP helpers shared across apps.
"""

import ipaddress

from django.conf import settings


def _valid_ip(value):
    try:
        return str(ipaddress.ip_address(value.strip()))
    except (AttributeError, ValueError):
        return None


def get_client_ip(request):
    """
    Return the client IP address.

    X-Real-IP is trusted only when the direct peer is a configured reverse
    proxy (settings.TRUSTED_PROXY_IPS), which overwrites it with the real
    peer address. X-Forwarded-For is never used: its first value is set by
    the client and can be spoofed.
    """
    remote_addr = _valid_ip(request.META.get("REMOTE_ADDR", "")) or "0.0.0.0"
    if remote_addr in getattr(settings, "TRUSTED_PROXY_IPS", []):
        real_ip = _valid_ip(request.META.get("HTTP_X_REAL_IP", ""))
        if real_ip:
            return real_ip
    return remote_addr

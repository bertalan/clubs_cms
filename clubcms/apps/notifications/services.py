"""
Notification service layer.

Core functions for creating notifications, sending via email/push,
managing unsubscribe tokens, and checking user preferences.
"""

import hashlib
import hmac
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from .models import (
    NOTIFICATION_PREFERENCE_MAP,
    NotificationQueue,
    PushSubscription,
    UnsubscribeToken,
)

logger = logging.getLogger(__name__)

User = get_user_model()


# ---------------------------------------------------------------------------
# User preference checks
# ---------------------------------------------------------------------------


def check_user_preference(user, notification_type, channel):
    """
    Return True if *user* has opted in to *notification_type* via *channel*.

    The check follows two levels:
    1. Master channel switch (``email_notifications`` / ``push_notifications``).
    2. Per-type preference field from ``NOTIFICATION_PREFERENCE_MAP``.
    """
    # Master switch
    if channel == "email" and not getattr(user, "email_notifications", True):
        return False
    if channel == "push" and not getattr(user, "push_notifications", False):
        return False

    # Per-type preference
    pref_field = NOTIFICATION_PREFERENCE_MAP.get(notification_type)
    if pref_field and not getattr(user, pref_field, True):
        return False

    return True


# ---------------------------------------------------------------------------
# Rate limiting helpers
# ---------------------------------------------------------------------------


def _email_count_today(user):
    """Number of email notifications sent to *user* in the current day."""
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return NotificationQueue.objects.filter(
        recipient=user,
        channel="email",
        status="sent",
        sent_at__gte=today_start,
    ).count()


def _push_count_last_hour(user):
    """Number of push notifications sent to *user* in the last 60 minutes."""
    one_hour_ago = timezone.now() - timedelta(hours=1)
    return NotificationQueue.objects.filter(
        recipient=user,
        channel="push",
        status="sent",
        sent_at__gte=one_hour_ago,
    ).count()


# ---------------------------------------------------------------------------
# Notification creation
# ---------------------------------------------------------------------------


def create_notification(
    notification_type,
    title,
    body,
    url="",
    recipients=None,
    channels=None,
    content_object=None,
    scheduled_for=None,
):
    """
    Create ``NotificationQueue`` entries for each recipient x channel pair.

    Parameters
    ----------
    notification_type : str
        One of the keys in ``NOTIFICATION_TYPE_CHOICES``.
    title : str
        Short title displayed in notification.
    body : str
        Full body content.
    url : str, optional
        Click-through destination URL.
    recipients : queryset or list of User, optional
        Defaults to all active users.
    channels : list of str, optional
        Subset of ``["email", "push", "in_app"]``.  Defaults to
        ``["email", "push"]``.
    content_object : Model instance, optional
        Triggering content for generic-foreign-key.
    scheduled_for : datetime, optional
        Delay delivery until this time.

    Returns
    -------
    list[NotificationQueue]
        The created (but not yet sent) entries.
    """
    from django.contrib.contenttypes.models import ContentType

    if channels is None:
        channels = ["email", "push"]

    if recipients is None:
        recipients = User.objects.filter(is_active=True)

    ct = None
    obj_id = None
    if content_object is not None:
        ct = ContentType.objects.get_for_model(content_object)
        obj_id = content_object.pk

    created = []
    for user in recipients:
        # Determine effective scheduling based on digest preference
        effective_scheduled = scheduled_for
        if effective_scheduled is None and hasattr(user, "digest_frequency"):
            digest = getattr(user, "digest_frequency", "immediate")
            if digest == "daily":
                # Schedule for next digest window (processed by daily digest task)
                effective_scheduled = _next_digest_time("daily")
            elif digest == "weekly":
                effective_scheduled = _next_digest_time("weekly")
            # "immediate" -> None (send now)

        for channel in channels:
            if not check_user_preference(user, notification_type, channel):
                continue

            notification = NotificationQueue(
                notification_type=notification_type,
                content_type=ct,
                object_id=obj_id,
                recipient=user,
                channel=channel,
                status="pending",
                title=title,
                body=body,
                url=url,
                scheduled_for=effective_scheduled,
            )
            created.append(notification)

    # Bulk create for efficiency
    if created:
        NotificationQueue.objects.bulk_create(created)

    return created


def _next_digest_time(frequency):
    """
    Return the datetime for the next digest window.

    Daily digests are compiled at 07:00 local time.
    Weekly digests are compiled on Monday at 07:00.
    """
    now = timezone.now()
    tomorrow = (now + timedelta(days=1)).replace(
        hour=7, minute=0, second=0, microsecond=0
    )
    if frequency == "daily":
        return tomorrow
    # weekly -> next Monday 07:00
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.hour >= 7:
        days_until_monday = 7
    return (now + timedelta(days=days_until_monday)).replace(
        hour=7, minute=0, second=0, microsecond=0
    )


# ---------------------------------------------------------------------------
# Email delivery
# ---------------------------------------------------------------------------


def build_email_html(notification):
    """
    Render the HTML version of an email notification.
    """
    unsubscribe_token = generate_unsubscribe_token(
        notification.recipient, notification.notification_type
    )
    context = {
        "notification": notification,
        "unsubscribe_token": unsubscribe_token,
        "site_name": getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS"),
        "base_url": getattr(settings, "WAGTAILADMIN_BASE_URL", ""),
    }
    return render_to_string("notifications/emails/single.html", context)


def build_digest_html(user, notifications):
    """
    Render the HTML for a digest email containing multiple notifications.
    """
    # Use a single unsubscribe token for digest (generic type "digest")
    unsubscribe_token = generate_unsubscribe_token(user, "news_published")
    context = {
        "user": user,
        "notifications": notifications,
        "unsubscribe_token": unsubscribe_token,
        "site_name": getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS"),
        "base_url": getattr(settings, "WAGTAILADMIN_BASE_URL", ""),
    }
    return render_to_string("notifications/emails/digest.html", context)


def send_email_notification(notification):
    """
    Send a single email notification.

    Respects the rate limit of 5 emails per user per day.
    On success sets ``status='sent'``; on failure sets ``status='failed'``.
    """
    user = notification.recipient

    # Rate limit: max 5 emails/day
    if _email_count_today(user) >= 5:
        notification.status = "skipped"
        notification.error_message = "Rate limit: max 5 emails/day exceeded"
        notification.save(update_fields=["status", "error_message"])
        return False

    if not user.email:
        notification.status = "skipped"
        notification.error_message = "User has no email address"
        notification.save(update_fields=["status", "error_message"])
        return False

    try:
        html_body = build_email_html(notification)
        text_body = strip_tags(notification.body)

        unsubscribe_token = generate_unsubscribe_token(
            user, notification.notification_type
        )
        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")
        unsubscribe_url = f"{base_url}/notifications/unsubscribe/{unsubscribe_token}/"

        msg = EmailMultiAlternatives(
            subject=notification.title,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
            headers={
                "List-Unsubscribe": f"<{unsubscribe_url}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)

        notification.status = "sent"
        notification.sent_at = timezone.now()
        notification.save(update_fields=["status", "sent_at"])
        return True

    except Exception as exc:
        logger.exception("Failed to send email notification %s", notification.pk)
        notification.status = "failed"
        notification.error_message = str(exc)[:1000]
        notification.save(update_fields=["status", "error_message"])
        return False


# ---------------------------------------------------------------------------
# Push delivery
# ---------------------------------------------------------------------------


def send_push_notification(notification):
    """
    Send a Web Push notification via pywebpush.

    Respects the rate limit of 3 pushes per user per hour.
    """
    user = notification.recipient

    # Rate limit: max 3 push/hour
    if _push_count_last_hour(user) >= 3:
        notification.status = "skipped"
        notification.error_message = "Rate limit: max 3 push/hour exceeded"
        notification.save(update_fields=["status", "error_message"])
        return False

    subscriptions = PushSubscription.objects.filter(user=user, is_active=True)
    if not subscriptions.exists():
        notification.status = "skipped"
        notification.error_message = "No active push subscriptions"
        notification.save(update_fields=["status", "error_message"])
        return False

    vapid_settings = getattr(settings, "WEBPUSH_SETTINGS", {})
    vapid_private_key = vapid_settings.get("VAPID_PRIVATE_KEY", "")
    vapid_admin_email = vapid_settings.get("VAPID_ADMIN_EMAIL", "")

    if not vapid_private_key:
        notification.status = "failed"
        notification.error_message = "VAPID private key not configured"
        notification.save(update_fields=["status", "error_message"])
        return False

    payload = json.dumps(
        {
            "title": notification.title,
            "body": strip_tags(notification.body),
            "url": notification.url,
            "type": notification.notification_type,
        }
    )

    vapid_claims = {
        "sub": f"mailto:{vapid_admin_email}",
    }

    sent_any = False
    errors = []

    for sub in subscriptions:
        try:
            from pywebpush import webpush, WebPushException  # noqa: F811

            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh_key,
                        "auth": sub.auth_key,
                    },
                },
                data=payload,
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims,
            )
            sub.last_used = timezone.now()
            sub.save(update_fields=["last_used"])
            sent_any = True

        except Exception as exc:
            error_msg = str(exc)
            errors.append(error_msg)
            logger.warning(
                "Push failed for subscription %s: %s", sub.pk, error_msg
            )
            # Deactivate subscription on 410 Gone (unsubscribed)
            if "410" in error_msg or "Gone" in error_msg:
                sub.is_active = False
                sub.save(update_fields=["is_active"])

    if sent_any:
        notification.status = "sent"
        notification.sent_at = timezone.now()
        notification.save(update_fields=["status", "sent_at"])
        return True
    else:
        notification.status = "failed"
        notification.error_message = "; ".join(errors)[:1000]
        notification.save(update_fields=["status", "error_message"])
        return False


# ---------------------------------------------------------------------------
# Unsubscribe tokens (HMAC-SHA256)
# ---------------------------------------------------------------------------


def generate_unsubscribe_token(user, notification_type):
    """
    Generate or retrieve a deterministic HMAC-SHA256 token for one-click
    unsubscribe.  Tokens are persisted in ``UnsubscribeToken`` for
    reverse lookup.

    Returns
    -------
    str
        64-character hex token.
    """
    secret = settings.SECRET_KEY
    message = f"{user.pk}:{notification_type}"
    token = hmac.new(
        secret.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    UnsubscribeToken.objects.update_or_create(
        user=user,
        notification_type=notification_type,
        defaults={"token": token},
    )
    return token


def verify_unsubscribe_token(token):
    """
    Look up *token* and return ``(user, notification_type)`` or ``None``.
    """
    try:
        unsub = UnsubscribeToken.objects.select_related("user").get(token=token)
        return unsub.user, unsub.notification_type
    except UnsubscribeToken.DoesNotExist:
        return None


def mask_email(email):
    """
    Mask an email address for display.

    ``john@example.com`` -> ``j***@example.com``
    """
    if not email or "@" not in email:
        return "***@***"
    local, domain = email.rsplit("@", 1)
    if len(local) <= 1:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***"
    return f"{masked_local}@{domain}"

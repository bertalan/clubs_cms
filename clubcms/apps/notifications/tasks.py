"""
Django-Q2 background tasks for the notification system.

Each function is a standalone importable callable suitable for
``django_q.tasks.async_task`` or ``django_q.tasks.schedule``.
"""

import logging
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from .models import NotificationQueue, PushSubscription
from .services import (
    build_digest_html,
    create_notification,
    send_email_notification,
    send_push_notification,
)

logger = logging.getLogger(__name__)

User = get_user_model()


# ---------------------------------------------------------------------------
# Queue processing (runs every 5 minutes)
# ---------------------------------------------------------------------------


def process_notification_queue():
    """
    Process pending immediate notifications.

    Picks up ``NotificationQueue`` entries with ``status='pending'`` that
    either have no ``scheduled_for`` or whose ``scheduled_for`` is in the
    past.  Dispatches each to the appropriate channel handler.

    Designed to run every 5 minutes via Django-Q2 schedule.
    """
    now = timezone.now()
    pending = NotificationQueue.objects.filter(
        status="pending",
    ).filter(
        Q(scheduled_for__isnull=True) | Q(scheduled_for__lte=now),
    ).select_related("recipient").order_by("created_at")[:200]

    sent_count = 0
    fail_count = 0

    for notification in pending:
        try:
            if notification.channel == "email":
                ok = send_email_notification(notification)
            elif notification.channel == "push":
                ok = send_push_notification(notification)
            elif notification.channel == "in_app":
                # In-app notifications are marked sent immediately
                notification.status = "sent"
                notification.sent_at = now
                notification.save(update_fields=["status", "sent_at"])
                ok = True
            else:
                notification.status = "skipped"
                notification.error_message = f"Unknown channel: {notification.channel}"
                notification.save(update_fields=["status", "error_message"])
                ok = False

            if ok:
                sent_count += 1
            else:
                fail_count += 1

        except Exception as exc:
            logger.exception(
                "Error processing notification %s: %s", notification.pk, exc
            )
            notification.status = "failed"
            notification.error_message = str(exc)[:1000]
            notification.save(update_fields=["status", "error_message"])
            fail_count += 1

    logger.info(
        "Notification queue processed: %d sent, %d failed/skipped",
        sent_count,
        fail_count,
    )
    return {"sent": sent_count, "failed": fail_count}


# ---------------------------------------------------------------------------
# Daily digest (runs daily at 07:00)
# ---------------------------------------------------------------------------


def send_daily_digest():
    """
    Compile and send daily digest emails for users with
    ``digest_frequency='daily'``.

    Gathers all pending email notifications for these users and sends
    them as a single digest email.
    """
    from django.core.mail import EmailMultiAlternatives
    from django.utils.html import strip_tags

    from django.conf import settings as django_settings

    now = timezone.now()

    # Find users with daily digest preference and pending notifications
    users_with_pending = (
        NotificationQueue.objects.filter(
            status="pending",
            channel="email",
            recipient__digest_frequency="daily",
        )
        .values_list("recipient", flat=True)
        .distinct()
    )

    sent_count = 0
    for user_id in users_with_pending:
        try:
            user = User.objects.get(pk=user_id, is_active=True)
            if not user.email:
                continue

            notifications = list(
                NotificationQueue.objects.filter(
                    recipient=user,
                    channel="email",
                    status="pending",
                ).order_by("-created_at")[:50]
            )

            if not notifications:
                continue

            html_body = build_digest_html(user, notifications)
            text_lines = [f"- {n.title}: {n.body}" for n in notifications]
            text_body = "\n".join(text_lines)

            site_name = getattr(
                django_settings, "WAGTAIL_SITE_NAME", "Club CMS"
            )
            msg = EmailMultiAlternatives(
                subject=f"[{site_name}] Daily digest - {now.strftime('%d/%m/%Y')}",
                body=text_body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            # Mark all as sent
            NotificationQueue.objects.filter(
                pk__in=[n.pk for n in notifications]
            ).update(status="sent", sent_at=now)

            sent_count += 1

        except Exception as exc:
            logger.exception("Failed to send daily digest for user %s: %s", user_id, exc)

    logger.info("Daily digests sent: %d", sent_count)
    return {"digests_sent": sent_count}


# ---------------------------------------------------------------------------
# Weekly digest (runs Monday at 07:00)
# ---------------------------------------------------------------------------


def send_weekly_digest():
    """
    Compile and send weekly digest emails for users with
    ``digest_frequency='weekly'``.
    """
    from django.core.mail import EmailMultiAlternatives

    from django.conf import settings as django_settings

    now = timezone.now()

    users_with_pending = (
        NotificationQueue.objects.filter(
            status="pending",
            channel="email",
            recipient__digest_frequency="weekly",
        )
        .values_list("recipient", flat=True)
        .distinct()
    )

    sent_count = 0
    for user_id in users_with_pending:
        try:
            user = User.objects.get(pk=user_id, is_active=True)
            if not user.email:
                continue

            notifications = list(
                NotificationQueue.objects.filter(
                    recipient=user,
                    channel="email",
                    status="pending",
                ).order_by("-created_at")[:100]
            )

            if not notifications:
                continue

            html_body = build_digest_html(user, notifications)
            text_lines = [f"- {n.title}: {n.body}" for n in notifications]
            text_body = "\n".join(text_lines)

            site_name = getattr(
                django_settings, "WAGTAIL_SITE_NAME", "Club CMS"
            )
            msg = EmailMultiAlternatives(
                subject=f"[{site_name}] Weekly digest - {now.strftime('%d/%m/%Y')}",
                body=text_body,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                to=[user.email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.send(fail_silently=False)

            NotificationQueue.objects.filter(
                pk__in=[n.pk for n in notifications]
            ).update(status="sent", sent_at=now)

            sent_count += 1

        except Exception as exc:
            logger.exception(
                "Failed to send weekly digest for user %s: %s", user_id, exc
            )

    logger.info("Weekly digests sent: %d", sent_count)
    return {"digests_sent": sent_count}


# ---------------------------------------------------------------------------
# Membership expiry check (runs daily)
# ---------------------------------------------------------------------------


def check_expiring_memberships():
    """
    Queue membership expiry reminders at 30 and 7 days before expiry.

    Expects ``ClubUser.membership_expiry`` (DateField) on the user model.
    If the field does not exist this task is a no-op.
    """
    now = timezone.now().date()
    thresholds = [
        (30, "30 days"),
        (7, "7 days"),
    ]

    total_queued = 0
    for days, label in thresholds:
        target_date = now + timedelta(days=days)
        expiring_users = User.objects.filter(
            is_active=True,
            membership_expiry=target_date,
        )

        if not expiring_users.exists():
            continue

        for user in expiring_users:
            create_notification(
                notification_type="membership_expiring",
                title=f"Membership expiring in {label}",
                body=(
                    f"Your membership expires on "
                    f"{target_date.strftime('%d/%m/%Y')}. "
                    f"Please renew to maintain your benefits."
                ),
                url="/account/membership/",
                recipients=[user],
                channels=["email", "push"],
            )
            total_queued += 1

    logger.info("Membership expiry reminders queued: %d", total_queued)
    return {"reminders_queued": total_queued}


# ---------------------------------------------------------------------------
# Cleanup tasks
# ---------------------------------------------------------------------------


def cleanup_old_notifications():
    """
    Delete notifications older than 90 days.  Runs daily.
    """
    cutoff = timezone.now() - timedelta(days=90)
    deleted_count, _ = NotificationQueue.objects.filter(
        created_at__lt=cutoff,
    ).delete()

    logger.info("Cleaned up %d old notifications", deleted_count)
    return {"deleted": deleted_count}


def cleanup_inactive_subscriptions():
    """
    Remove push subscriptions that have been inactive (not used) for
    more than 90 days or that are marked inactive.  Runs weekly.
    """
    cutoff = timezone.now() - timedelta(days=90)

    deleted_count, _ = PushSubscription.objects.filter(
        Q(is_active=False)
        | Q(last_used__lt=cutoff)
        | Q(last_used__isnull=True, created_at__lt=cutoff)
    ).delete()

    logger.info("Cleaned up %d inactive push subscriptions", deleted_count)
    return {"deleted": deleted_count}

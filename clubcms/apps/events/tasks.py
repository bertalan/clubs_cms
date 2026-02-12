"""
Periodic tasks for the events app.

Provides management of expired bank transfer payments
and waitlist promotion.
"""

import logging

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.events.models import EventRegistration
from apps.events.utils import promote_from_waitlist

logger = logging.getLogger(__name__)


def expire_pending_bank_transfers():
    """
    Mark expired bank transfer registrations and promote from waitlist.

    Should be called periodically (e.g. every hour via cron or Celery beat).
    """
    now = timezone.now()
    expired_qs = EventRegistration.objects.filter(
        payment_provider="bank_transfer",
        payment_status="pending",
        payment_expires_at__lt=now,
    ).select_related("event", "user")

    count = 0
    for reg in expired_qs:
        reg.payment_status = "expired"
        reg.status = "cancelled"
        reg.save(update_fields=["payment_status", "status"])

        promote_from_waitlist(reg.event)

        # Send expiration notification
        if reg.user:
            try:
                from apps.notifications.services import create_notification

                create_notification(
                    notification_type="payment_expired",
                    title=str(_("Payment expired: {event}")).format(
                        event=reg.event.title,
                    ),
                    body=str(
                        _("Your bank transfer for {event} was not received in time. "
                          "Your registration has been cancelled.")
                    ).format(event=reg.event.title),
                    recipients=[reg.user],
                    channels=["email"],
                    content_object=reg,
                )
            except Exception:
                logger.exception(
                    "Failed to send expiry notification for registration %s",
                    reg.pk,
                )

        count += 1

    if count:
        logger.info("Expired %d pending bank transfer registration(s).", count)

    return count

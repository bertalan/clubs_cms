"""
Signals for the events app.

Sends notifications when event registrations are created.
Uses the notification queue for authenticated users and direct
email for guest registrations.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

from apps.events.models import EventRegistration

logger = logging.getLogger(__name__)


@receiver(post_save, sender=EventRegistration)
def on_registration_created(sender, instance, created, **kwargs):
    """Send a confirmation notification when a new registration is created."""
    if not created:
        return

    user = instance.user
    if not user:
        _send_guest_confirmation_email(instance)
        return

    from apps.notifications.services import create_notification

    create_notification(
        notification_type="event_registered",
        title=str(_("Registration confirmed: {event}")).format(
            event=instance.event.title,
        ),
        body=str(_("You are registered for {event} on {date}.")).format(
            event=instance.event.title,
            date=instance.event.start_date.strftime("%d/%m/%Y %H:%M"),
        ),
        url=instance.event.url,
        recipients=[user],
        channels=["email"],
        content_object=instance,
        scheduled_for=None,
    )


def _send_guest_confirmation_email(registration):
    """Send confirmation email to guest registrations (no user account)."""
    if not registration.email:
        return

    try:
        html = render_to_string(
            "events/emails/registration_confirmation.html",
            {
                "registration": registration,
                "event": registration.event,
            },
        )
        text_body = strip_tags(html)

        msg = EmailMultiAlternatives(
            subject=str(_("Registration confirmed: {event}")).format(
                event=registration.event.title,
            ),
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[registration.email],
        )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        logger.exception(
            "Failed to send guest confirmation email for registration %s",
            registration.pk,
        )

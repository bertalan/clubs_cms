"""
Newsletter sending service.

Handles bulk-sending newsletter campaigns to active subscribers,
filtered by category when applicable.
Uses Django's email infrastructure and integrates with Django-Q2
for asynchronous dispatch and scheduled sending.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from apps.website.models.newsletter import NewsletterSubscription, SentNewsletter

logger = logging.getLogger(__name__)

# Max emails per batch to avoid memory/timeout issues.
BATCH_SIZE = 50


def send_newsletter(newsletter_id, sent_by_id=None):
    """
    Send a newsletter campaign to matching active subscribers.

    If the newsletter has a category, only subscribers who opted into
    that category will receive it.  Otherwise all active subscribers.

    Designed to be called via ``django_q.tasks.async_task``:

        from django_q.tasks import async_task
        async_task("apps.website.services_newsletter.send_newsletter", pk, user.pk)

    Parameters
    ----------
    newsletter_id : int
        PK of the ``SentNewsletter`` to send.
    sent_by_id : int, optional
        PK of the admin user who triggered the send.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        newsletter = SentNewsletter.objects.get(pk=newsletter_id)
    except SentNewsletter.DoesNotExist:
        logger.error("Newsletter %s not found", newsletter_id)
        return {"sent": 0, "failed": 0, "error": "not_found"}

    if newsletter.status == "sent":
        logger.warning("Newsletter %s already sent, skipping", newsletter_id)
        return {"sent": 0, "failed": 0, "error": "already_sent"}

    # Filter by category if the newsletter is category-specific
    qs = NewsletterSubscription.objects.filter(is_active=True)
    if newsletter.category:
        qs = qs.filter(categories=newsletter.category)

    subscriber_list = list(qs.values_list("email", flat=True))
    total = len(subscriber_list)

    if total == 0:
        logger.info("No active subscribers for newsletter %s", newsletter_id)
        newsletter.status = "sent"
        newsletter.sent_at = timezone.now()
        newsletter.recipient_count = 0
        if sent_by_id:
            newsletter.sent_by_id = sent_by_id
        newsletter.save(update_fields=["status", "sent_at", "recipient_count", "sent_by_id"])
        return {"sent": 0, "failed": 0}

    site_name = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
    base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")

    sent_count = 0
    fail_count = 0

    for i in range(0, total, BATCH_SIZE):
        batch = subscriber_list[i : i + BATCH_SIZE]
        for email in batch:
            try:
                _send_single(newsletter, email, site_name, base_url)
                sent_count += 1
            except Exception:
                logger.exception(
                    "Failed to send newsletter %s to %s", newsletter_id, email
                )
                fail_count += 1

    # Mark as sent
    newsletter.status = "sent"
    newsletter.sent_at = timezone.now()
    newsletter.recipient_count = sent_count
    if sent_by_id:
        newsletter.sent_by_id = sent_by_id
    newsletter.save(
        update_fields=["status", "sent_at", "recipient_count", "sent_by_id"]
    )

    logger.info(
        "Newsletter %s sent: %d ok, %d failed (of %d subscribers)",
        newsletter_id,
        sent_count,
        fail_count,
        total,
    )
    return {"sent": sent_count, "failed": fail_count}


def _send_single(newsletter, email, site_name, base_url):
    """Send a single newsletter email to one subscriber address."""
    from apps.website.render_email import (
        render_newsletter_body_html,
        render_newsletter_body_text,
    )

    unsubscribe_url = f"{base_url}/newsletter/unsubscribe/"
    try:
        from apps.website.models.newsletter import NewsletterPage

        nl_page = NewsletterPage.objects.live().first()
        if nl_page:
            unsubscribe_url = f"{base_url}{nl_page.url}{nl_page.reverse_subpage('unsubscribe')}"
    except Exception:
        pass

    body_html = render_newsletter_body_html(newsletter, base_url=base_url)

    context = {
        "subject": newsletter.subject,
        "body_html": body_html,
        "site_name": site_name,
        "base_url": base_url,
        "unsubscribe_url": unsubscribe_url,
        "email": email,
    }

    html_body = render_to_string("website/emails/newsletter.html", context)
    text_body = render_newsletter_body_text(newsletter)

    msg = EmailMultiAlternatives(
        subject=newsletter.subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        headers={
            "List-Unsubscribe": f"<{unsubscribe_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        },
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)


# ── Scheduled sending ──────────────────────────────────────────────────────


def send_scheduled_newsletters():
    """
    Check for newsletters with status="scheduled" and scheduled_at <= now,
    and dispatch each one.

    Designed to run as a periodic Django-Q2 task (every 5 minutes).
    Register via::

        from django_q.models import Schedule
        Schedule.objects.get_or_create(
            name="send-scheduled-newsletters",
            defaults={
                "func": "apps.website.services_newsletter.send_scheduled_newsletters",
                "schedule_type": Schedule.MINUTES,
                "minutes": 5,
            },
        )
    """
    now = timezone.now()
    due = SentNewsletter.objects.filter(
        status="scheduled",
        scheduled_at__lte=now,
    )
    count = 0
    for newsletter in due:
        logger.info("Sending scheduled newsletter %s (due %s)", newsletter.pk, newsletter.scheduled_at)
        send_newsletter(newsletter.pk, sent_by_id=newsletter.sent_by_id)
        count += 1

    if count:
        logger.info("Dispatched %d scheduled newsletter(s)", count)
    return {"dispatched": count}

"""
Signal handlers for the website app.

Auto-newsletter: when a NewsPage is published, create a SentNewsletter
with StreamField body and queue it for async sending to all subscribers.
Also triggers the notification system for registered users.
"""

import json
import logging

from django.conf import settings
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


def on_news_page_published(sender, instance, **kwargs):
    """
    Wagtail ``page_published`` signal handler.

    Only acts on NewsPage instances. Creates a SentNewsletter campaign
    with a StreamField body and dispatches it asynchronously via Django-Q2.
    """
    from apps.website.models.pages import NewsPage

    if not isinstance(instance, NewsPage):
        return

    from apps.website.models.newsletter import NewsletterCategory, SentNewsletter

    # Avoid duplicate: check if a newsletter for this page already exists
    subject = instance.title
    if SentNewsletter.objects.filter(subject=subject).exists():
        return

    # Build intro text for plain-text fallback and notification
    intro = ""
    if hasattr(instance, "intro") and instance.intro:
        intro = strip_tags(str(instance.intro))
    if not intro:
        intro = _("A new article has been published: %(title)s") % {
            "title": instance.title,
        }

    # Build StreamField body as JSON
    base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
    page_url = f"{base_url}{instance.url}" if instance.url else ""

    body_data = []
    body_data.append({"type": "text", "value": f"<p>{intro}</p>"})
    if page_url:
        body_data.append({
            "type": "button",
            "value": {
                "text": str(_("Read the full article")),
                "url": page_url,
                "style": "primary",
            },
        })

    # Pick the first default category (or None)
    default_category = NewsletterCategory.objects.filter(is_default=True).first()

    newsletter = SentNewsletter.objects.create(
        subject=subject,
        body=json.dumps(body_data),
        category=default_category,
        is_public=True,
        status="draft",
    )

    # Queue async send via Django-Q2
    try:
        from django_q.tasks import async_task

        async_task(
            "apps.website.services_newsletter.send_newsletter",
            newsletter.pk,
            task_name=f"auto-newsletter-{newsletter.pk}",
        )
    except Exception:
        logger.exception(
            "Failed to queue auto-newsletter for page %s", instance.pk,
        )

    # Also notify registered users via notification system
    try:
        from apps.notifications.services import create_notification

        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
        create_notification(
            notification_type="news_published",
            title=instance.title,
            body=intro,
            url=f"{base_url}{instance.url}" if instance.url else "",
            channels=["email", "push"],
            content_object=instance,
        )
    except Exception:
        logger.exception(
            "Failed to create news notification for page %s", instance.pk,
        )

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.website"
    verbose_name = _("Website")

    def ready(self):
        from django.db.models.signals import post_migrate
        from wagtail.signals import page_published

        from . import signals  # noqa: F401

        page_published.connect(signals.on_news_page_published)

        # Register scheduled newsletter dispatch after migration
        post_migrate.connect(_ensure_scheduled_newsletter_task, sender=self)


def _ensure_scheduled_newsletter_task(sender, **kwargs):
    """Create the Django-Q2 schedule for sending scheduled newsletters."""
    try:
        from django_q.models import Schedule

        Schedule.objects.get_or_create(
            name="send-scheduled-newsletters",
            defaults={
                "func": "apps.website.services_newsletter.send_scheduled_newsletters",
                "schedule_type": Schedule.MINUTES,
                "minutes": 5,
            },
        )
    except Exception:
        pass  # DB not ready or django_q table not created yet

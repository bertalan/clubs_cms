from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _

# Django-Q2 schedules for the federation (minutes between runs).
FEDERATION_SCHEDULES = {
    "federation-sync-events": ("apps.federation.sync.tasks.sync_all_clubs", 60),
    "federation-sync-interests": ("apps.federation.sync.tasks.sync_interest_counts", 60),
}


def ensure_federation_schedules(**kwargs):
    """Create the hourly sync schedules, or remove them if federation is off."""
    try:
        from django_q.models import Schedule

        if not getattr(settings, "FEDERATION_ENABLED", False):
            Schedule.objects.filter(name__in=FEDERATION_SCHEDULES).delete()
            return
        for name, (func, minutes) in FEDERATION_SCHEDULES.items():
            Schedule.objects.get_or_create(
                name=name,
                defaults={
                    "func": func,
                    "schedule_type": Schedule.MINUTES,
                    "minutes": minutes,
                },
            )
    except Exception:
        pass  # DB not ready or django_q table not created yet


class FederationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.federation"
    verbose_name = _("Federation")

    def ready(self):
        try:
            import apps.federation.wagtail_hooks  # noqa: F401
        except ImportError:
            pass
        post_migrate.connect(ensure_federation_schedules, sender=self)

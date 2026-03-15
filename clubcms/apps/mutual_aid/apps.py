from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MutualAidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mutual_aid"
    verbose_name = _("Mutual Aid")

    def ready(self):
        try:
            import apps.mutual_aid.wagtail_hooks  # noqa: F401
        except ImportError:
            pass

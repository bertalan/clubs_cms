from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FederationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.federation"
    verbose_name = _("Federation")

    def ready(self):
        try:
            import apps.federation.wagtail_hooks  # noqa: F401
        except ImportError:
            pass

from django.apps import AppConfig


class MutualAidConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.mutual_aid"
    verbose_name = "Mutual Aid"

    def ready(self):
        try:
            import apps.mutual_aid.wagtail_hooks  # noqa: F401
        except ImportError:
            pass

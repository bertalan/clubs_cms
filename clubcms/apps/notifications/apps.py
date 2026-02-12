from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = "Notifications"

    def ready(self):
        # Import wagtail_hooks so they are registered on startup
        try:
            from . import wagtail_hooks  # noqa: F401
        except ImportError:
            pass

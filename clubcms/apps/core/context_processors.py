"""
Context processor to inject theme settings into all templates.
"""


def theme_context(request):
    """
    Add theme and color scheme data to the template context.

    Returns the current theme name and color settings from SiteSettings.
    Falls back to sensible defaults if SiteSettings is not configured.
    """
    try:
        from apps.website.models import SiteSettings

        settings = SiteSettings.for_request(request)
        return {
            "theme": getattr(settings, "theme", "velocity"),
            "colors": getattr(settings, "get_colors", lambda: {})(),
        }
    except Exception:
        return {
            "theme": "velocity",
            "colors": {},
        }

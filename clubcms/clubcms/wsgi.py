"""
WSGI config for ClubCMS project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubcms.settings.prod")

application = get_wsgi_application()

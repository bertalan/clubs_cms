"""
Management command to load ClubCMS demo content from a SQLite fixture.

Each language has its own .sqlite3 file with all data needed for a
complete standalone site.  Load one language as primary, then
optionally add more.

Usage:
    # Fresh English site:
    python manage.py load_demo --lang en --primary --flush

    # Add Italian pages to existing site:
    python manage.py load_demo --lang it

    # Fresh Italian-primary site, then add English:
    python manage.py load_demo --lang it --primary --flush
    python manage.py load_demo --lang en
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.demo.loader import DemoLoader


class Command(BaseCommand):
    help = "Load demo content from a per-language SQLite fixture"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            required=True,
            choices=["en", "it", "de", "fr", "es"],
            help="Language code of the fixture to load.",
        )
        parser.add_argument(
            "--primary",
            action="store_true",
            help=(
                "Set this language as the site's primary language "
                "(creates Site, sets root page)."
            ),
        )
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing demo content before loading.",
        )

    def handle(self, *args, **options):
        lang = options["lang"]
        db_path = (
            Path(settings.BASE_DIR) / "fixtures" / "demo" / f"demo_{lang}.sqlite3"
        )

        loader = DemoLoader(db_path, self.stdout, self.style)
        loader.load(primary=options["primary"], flush=options["flush"])

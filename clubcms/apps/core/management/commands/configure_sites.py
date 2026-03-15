"""
Management command to configure Django Site and Wagtail Site with the correct domain.

Reads the domain from ALLOWED_HOSTS or accepts it as argument.
Run after every deploy or first setup.

Usage:
    python manage.py configure_sites
    python manage.py configure_sites --domain=clubs.betabi.it
"""

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from wagtail.models import Site as WagtailSite


class Command(BaseCommand):
    help = "Configure Django Site and Wagtail Site with the correct domain"

    def add_arguments(self, parser):
        parser.add_argument(
            "--domain",
            type=str,
            help="Domain to set (default: first entry in ALLOWED_HOSTS)",
        )

    def handle(self, *args, **options):
        domain = options["domain"]
        if not domain:
            hosts = getattr(settings, "ALLOWED_HOSTS", [])
            # Skip wildcards and localhost
            domain = next(
                (h for h in hosts if h not in ("*", "localhost", "127.0.0.1")),
                None,
            )
        if not domain:
            self.stderr.write(self.style.ERROR(
                "No domain found. Set ALLOWED_HOSTS or pass --domain=..."
            ))
            return

        # Django Sites framework
        site, _ = Site.objects.get_or_create(pk=1)
        site.domain = domain
        site.name = "Club CMS"
        site.save()
        self.stdout.write(f"  Django Site: domain={site.domain}")

        # Wagtail Site
        ws = WagtailSite.objects.filter(is_default_site=True).first()
        if not ws:
            ws = WagtailSite.objects.first()
        if ws:
            ws.hostname = domain
            ws.port = 443
            ws.save()
            self.stdout.write(f"  Wagtail Site: hostname={ws.hostname} port={ws.port}")
        else:
            self.stderr.write(self.style.WARNING("  No Wagtail Site found to update"))

        self.stdout.write(self.style.SUCCESS(f"  Sites configured for: {domain}"))

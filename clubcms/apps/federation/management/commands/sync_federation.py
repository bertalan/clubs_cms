"""
Management command to sync events from federated partner clubs.

Usage:
    python manage.py sync_federation
    python manage.py sync_federation --club=partnercode
    python manage.py sync_federation --dry-run
    python manage.py sync_federation --cleanup
    python manage.py sync_federation --interests
"""

from django.core.management.base import BaseCommand

from apps.federation.models import FederatedClub
from apps.federation.sync.tasks import (
    cleanup_past_events,
    sync_all_clubs,
    sync_club_events,
    sync_interest_counts,
)


class Command(BaseCommand):
    help = "Sync events from federated partner clubs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--club",
            type=str,
            help="Sync only a specific partner club by short_code",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be synced without making changes",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Clean up external events older than 90 days",
        )
        parser.add_argument(
            "--interests",
            action="store_true",
            help="Sync interest counts to partner clubs",
        )
        parser.add_argument(
            "--cleanup-days",
            type=int,
            default=90,
            help="Number of days for cleanup cutoff (default: 90)",
        )

    def handle(self, *args, **options):
        club_code = options.get("club")
        dry_run = options.get("dry_run", False)
        do_cleanup = options.get("cleanup", False)
        do_interests = options.get("interests", False)
        cleanup_days = options.get("cleanup_days", 90)

        # Cleanup mode
        if do_cleanup:
            if dry_run:
                from datetime import timedelta

                from django.utils import timezone

                from apps.federation.models import ExternalEvent

                cutoff = timezone.now() - timedelta(days=cleanup_days)
                count = ExternalEvent.objects.filter(start_date__lt=cutoff).count()
                self.stdout.write(
                    f"[DRY RUN] Would delete {count} events older than {cleanup_days} days"
                )
            else:
                deleted = cleanup_past_events(days=cleanup_days)
                self.stdout.write(
                    self.style.SUCCESS(f"Cleaned up {deleted} past external events")
                )
            return

        # Interest sync mode
        if do_interests:
            if dry_run:
                self.stdout.write("[DRY RUN] Would sync interest counts to partners")
            else:
                sync_interest_counts()
                self.stdout.write(
                    self.style.SUCCESS("Interest counts synced to partners")
                )
            return

        # Event sync mode
        if club_code:
            # Sync a single club
            try:
                club = FederatedClub.objects.get(
                    short_code=club_code,
                    is_active=True,
                    is_approved=True,
                )
            except FederatedClub.DoesNotExist:
                self.stderr.write(
                    self.style.ERROR(
                        f"Club '{club_code}' not found or not active/approved"
                    )
                )
                return

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would sync events from: {club.name} ({club.short_code})\n"
                    f"  Base URL: {club.base_url}\n"
                    f"  Auto-import: {club.auto_import}\n"
                    f"  Last sync: {club.last_sync or 'never'}"
                )
            else:
                self.stdout.write(f"Syncing events from: {club.name} ({club.short_code})")
                try:
                    sync_club_events(str(club.pk))
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully synced {club.short_code}")
                    )
                except Exception as exc:
                    self.stderr.write(
                        self.style.ERROR(f"Failed to sync {club.short_code}: {exc}")
                    )
        else:
            # Sync all clubs
            clubs = FederatedClub.objects.filter(is_active=True, is_approved=True)
            if not clubs.exists():
                self.stdout.write(
                    self.style.WARNING("No active, approved partner clubs found")
                )
                return

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would sync events from {clubs.count()} partner club(s):"
                )
                for club in clubs:
                    self.stdout.write(
                        f"  - {club.name} ({club.short_code}): "
                        f"last sync {club.last_sync or 'never'}"
                    )
            else:
                self.stdout.write(
                    f"Syncing events from {clubs.count()} active partner club(s)..."
                )
                results = sync_all_clubs()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Federation sync complete: "
                        f"{results['success']} succeeded, {results['failed']} failed"
                    )
                )

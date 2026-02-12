"""
Management command to populate BoardPage members with portrait photos.

Downloads demo portraits, imports them as Wagtail images, and attaches them
to each member in the team_grid block of the BoardPage.
"""

import json
import os
import tempfile
import urllib.request

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand

from wagtail.images.models import Image

from apps.website.models import BoardPage


# Portrait URLs from randomuser.me — royalty-free demo portraits
PORTRAITS = [
    {
        "name": "Roberto Colombo",
        "url": "https://randomuser.me/api/portraits/men/32.jpg",
        "filename": "roberto_colombo.jpg",
    },
    {
        "name": "Francesca Moretti",
        "url": "https://randomuser.me/api/portraits/women/44.jpg",
        "filename": "francesca_moretti.jpg",
    },
    {
        "name": "Luca Bernardi",
        "url": "https://randomuser.me/api/portraits/men/52.jpg",
        "filename": "luca_bernardi.jpg",
    },
    {
        "name": "Chiara Fontana",
        "url": "https://randomuser.me/api/portraits/women/65.jpg",
        "filename": "chiara_fontana.jpg",
    },
    {
        "name": "Davide Marchetti",
        "url": "https://randomuser.me/api/portraits/men/75.jpg",
        "filename": "davide_marchetti.jpg",
    },
    {
        "name": "Elena Rizzo",
        "url": "https://randomuser.me/api/portraits/women/68.jpg",
        "filename": "elena_rizzo.jpg",
    },
]


class Command(BaseCommand):
    help = "Download portrait photos and attach them to BoardPage team members."

    def handle(self, *args, **options):
        board = BoardPage.objects.live().first()
        if not board:
            self.stderr.write(self.style.ERROR("No published BoardPage found."))
            return

        # Build a lookup: member name → Wagtail Image pk
        photo_map = {}
        for entry in PORTRAITS:
            name = entry["name"]
            filename = entry["filename"]

            # Skip if image already imported
            existing = Image.objects.filter(title=name).first()
            if existing:
                self.stdout.write(f"  Image for {name} already exists (pk={existing.pk}).")
                photo_map[name] = existing.pk
                continue

            # Download portrait to a temp file
            self.stdout.write(f"  Downloading portrait for {name}…")
            try:
                tmp_path = os.path.join(tempfile.gettempdir(), filename)
                urllib.request.urlretrieve(entry["url"], tmp_path)
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"  ⚠ Download failed for {name}: {exc}"))
                continue

            # Create Wagtail Image
            with open(tmp_path, "rb") as f:
                image = Image(title=name)
                image.file.save(filename, ImageFile(f), save=True)
                photo_map[name] = image.pk
                self.stdout.write(self.style.SUCCESS(f"  ✓ Imported image for {name} (pk={image.pk})"))

            # Cleanup temp file
            os.remove(tmp_path)

        if not photo_map:
            self.stderr.write(self.style.ERROR("No images were imported. Aborting."))
            return

        # ----------------------------------------------------------------
        # Rebuild the body StreamField data with photo references
        # ----------------------------------------------------------------
        # Convert to a plain Python list to allow JSON serialisation
        raw_data = json.loads(json.dumps(
            list(board.body.raw_data) if hasattr(board.body, "raw_data") else list(board.body.stream_data),
            default=str,
        ))
        updated = False

        for block in raw_data:
            if block["type"] != "team_grid":
                continue
            for member in block["value"]["members"]:
                member_name = member.get("name", "")
                if member_name in photo_map and not member.get("photo"):
                    member["photo"] = photo_map[member_name]
                    updated = True
                    self.stdout.write(f"  Attached photo to {member_name}")

        if not updated:
            self.stdout.write("  All members already have photos. Nothing to update.")
            return

        # Save the updated body
        board.body = json.dumps(raw_data)
        board.save()
        board.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("✓ BoardPage updated and published with member photos."))

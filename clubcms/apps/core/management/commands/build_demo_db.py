"""
Management command to (re-)build a demo fixture SQLite database
from the Python data definitions.

Usage:
    python manage.py build_demo_db --lang en
    python manage.py build_demo_db --lang it
    python manage.py build_demo_db          # builds both
"""

import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.core.demo.schema import SCHEMA_SQL


class Command(BaseCommand):
    help = "Build demo SQLite fixture(s) from Python data definitions"

    def add_arguments(self, parser):
        parser.add_argument(
            "--lang",
            choices=["en", "it"],
            default=None,
            help="Build only this language (default: both).",
        )

    def handle(self, *args, **options):
        langs = [options["lang"]] if options["lang"] else ["en", "it"]

        for lang in langs:
            self._build(lang)

    def _build(self, lang: str):
        # Import the data module dynamically
        if lang == "en":
            from apps.core.demo.data_en import DATA
        elif lang == "it":
            from apps.core.demo.data_it import DATA
        else:
            self.stdout.write(self.style.ERROR(f"No data module for '{lang}'"))
            return

        out_dir = Path(settings.BASE_DIR) / "fixtures" / "demo"
        out_dir.mkdir(parents=True, exist_ok=True)
        db_path = out_dir / f"demo_{lang}.sqlite3"

        # Remove existing file
        if db_path.exists():
            db_path.unlink()

        conn = sqlite3.connect(str(db_path))
        try:
            conn.executescript(SCHEMA_SQL)
            self._insert_all(conn, DATA)
            conn.commit()
            self.stdout.write(self.style.SUCCESS(
                f"Built {db_path} ({db_path.stat().st_size:,} bytes)"
            ))
        finally:
            conn.close()

    def _insert_all(self, conn: sqlite3.Connection, data: dict):
        """Insert all data from the DATA dictionary into the SQLite database."""

        # meta
        for key, value in data.get("meta", {}).items():
            conn.execute(
                "INSERT INTO meta (key, value) VALUES (?, ?)",
                (key, value),
            )

        # color_scheme
        for row in data.get("color_scheme", []):
            conn.execute(
                "INSERT INTO color_scheme VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    row["name"], row["primary_color"],
                    row["secondary_color"], row["accent"],
                    row["surface"], row["surface_alt"],
                    row["text_primary"], row["text_muted"],
                    int(row.get("is_dark_mode", False)),
                ),
            )

        # categories
        for row in data.get("categories", []):
            conn.execute(
                "INSERT INTO categories VALUES (?,?,?,?,?,?,?)",
                (
                    row["cat_type"], row["name"], row["slug"],
                    row.get("color", ""), row.get("description", ""),
                    row.get("icon", ""), row.get("sort_order", 0),
                ),
            )

        # products
        for row in data.get("products", []):
            conn.execute(
                "INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row["name"], row["slug"],
                    row.get("translation_key", ""),
                    row.get("description", ""),
                    float(row["price"]),
                    int(row.get("grants_vote", False)),
                    int(row.get("grants_events", False)),
                    int(row.get("grants_upload", False)),
                    int(row.get("grants_discount", False)),
                    row.get("discount_percent", 0),
                    row.get("sort_order", 0),
                ),
            )

        # Simple tables with consistent patterns
        for row in data.get("testimonials", []):
            conn.execute(
                "INSERT INTO testimonials VALUES (?,?,?,?)",
                (row["quote"], row["author_name"],
                 row.get("author_role", ""), int(row.get("featured", False))),
            )

        for row in data.get("faqs", []):
            conn.execute(
                "INSERT INTO faqs VALUES (?,?,?,?)",
                (row["question"], row["answer"],
                 row.get("category", ""), row.get("sort_order", 0)),
            )

        for row in data.get("photo_tags", []):
            conn.execute(
                "INSERT INTO photo_tags VALUES (?,?)",
                (row["name"], row["slug"]),
            )

        for row in data.get("press_releases", []):
            conn.execute(
                "INSERT INTO press_releases VALUES (?,?,?,?)",
                (row["title"], row["pub_date"], row["body"],
                 int(row.get("is_archived", False))),
            )

        for row in data.get("brand_assets", []):
            conn.execute(
                "INSERT INTO brand_assets VALUES (?,?,?,?)",
                (row["name"], row["category"],
                 row.get("description", ""), row.get("sort_order", 0)),
            )

        for row in data.get("aid_skills", []):
            conn.execute(
                "INSERT INTO aid_skills VALUES (?,?,?,?,?)",
                (row["name"], row["slug"], row.get("description", ""),
                 row.get("category", ""), row.get("sort_order", 0)),
            )

        for row in data.get("images", []):
            conn.execute(
                "INSERT INTO images VALUES (?,?,?,?,?)",
                (row["key"], row["width"], row["height"],
                 row["keywords"], row.get("description", "")),
            )

        # pages
        for row in data.get("pages", []):
            import json
            fields = row.get("fields", {})
            conn.execute(
                "INSERT INTO pages VALUES (?,?,?,?,?,?)",
                (
                    row["slug"], row["page_type"],
                    row.get("parent_slug"), row["translation_key"],
                    row["title"],
                    json.dumps(fields, ensure_ascii=False),
                ),
            )

        for row in data.get("place_tags", []):
            conn.execute(
                "INSERT INTO place_tags VALUES (?,?)",
                (row["name"], row["slug"]),
            )

        for row in data.get("route_stops", []):
            conn.execute(
                "INSERT INTO route_stops VALUES (?,?,?,?)",
                (row["route_slug"], row["place_slug"],
                 row.get("sort_order", 0), row.get("note", "")),
            )

        # navbar_items
        for row in data.get("navbar_items", []):
            conn.execute(
                "INSERT INTO navbar_items VALUES (?,?,?,?,?,?,?)",
                (
                    row["label"], row.get("link_url", ""),
                    row.get("link_page_slug", ""),
                    int(row.get("open_new_tab", False)),
                    int(row.get("is_cta", False)),
                    row.get("sort_order", 0),
                    row.get("parent_label", ""),
                ),
            )

        # footer_items
        for row in data.get("footer_items", []):
            conn.execute(
                "INSERT INTO footer_items VALUES (?,?,?,?)",
                (row["label"], row.get("link_url", ""),
                 row.get("link_page_slug", ""),
                 row.get("sort_order", 0)),
            )

        for row in data.get("footer_social_links", []):
            conn.execute(
                "INSERT INTO footer_social_links VALUES (?,?,?)",
                (row["platform"], row["url"], row.get("sort_order", 0)),
            )

        # site_settings
        for key, value in data.get("site_settings", {}).items():
            conn.execute(
                "INSERT INTO site_settings VALUES (?,?)",
                (key, str(value)),
            )

        # members
        for row in data.get("members", []):
            conn.execute(
                "INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row["username"], row["first_name"], row["last_name"],
                    row["email"], row.get("display_name", ""),
                    row.get("phone", ""), row.get("mobile", ""),
                    row.get("birth_date"), row.get("birth_place", ""),
                    row.get("fiscal_code", ""), row.get("city", ""),
                    row.get("province", ""), row.get("postal_code", ""),
                    row.get("address", ""), row.get("card_number", ""),
                    row.get("membership_date"), row.get("membership_expiry"),
                    row.get("bio", ""),
                    int(row.get("aid_available", False)),
                    row.get("aid_radius_km", 0),
                    row.get("aid_location_city", ""),
                    row.get("aid_coordinates", ""),
                    row.get("aid_notes", ""),
                    int(row.get("show_in_directory", False)),
                    int(row.get("public_profile", False)),
                    int(row.get("newsletter", False)),
                    row.get("image_key", ""),
                ),
            )

        # aid_requests
        for row in data.get("aid_requests", []):
            conn.execute(
                "INSERT INTO aid_requests VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    row["helper_username"], row["requester_name"],
                    row.get("requester_phone", ""),
                    row.get("requester_email", ""),
                    row.get("requester_username", ""),
                    row["issue_type"], row["description"],
                    row.get("location", ""), row.get("urgency", "medium"),
                    row.get("status", "open"),
                ),
            )

        # federated_clubs
        for row in data.get("federated_clubs", []):
            conn.execute(
                "INSERT INTO federated_clubs VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    row["short_code"], row["name"], row.get("city", ""),
                    row.get("base_url", ""), row.get("logo_url", ""),
                    row.get("description", ""), row.get("api_key", ""),
                    int(row.get("is_active", True)),
                    int(row.get("is_approved", False)),
                    int(row.get("share_our_events", False)),
                ),
            )

        # external_events
        for row in data.get("external_events", []):
            conn.execute(
                "INSERT INTO external_events VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    row["club_short_code"], row["external_id"],
                    row["event_name"],
                    row["start_days_offset"], row["end_days_offset"],
                    row.get("location_name", ""),
                    row.get("location_address", ""),
                    row.get("location_lat"), row.get("location_lon"),
                    row.get("description", ""),
                    row.get("detail_url", ""),
                    int(row.get("is_approved", False)),
                ),
            )

        for row in data.get("event_interests", []):
            conn.execute(
                "INSERT INTO event_interests VALUES (?,?,?)",
                (row["username"], row["event_external_id"],
                 row["interest_level"]),
            )

        for row in data.get("event_comments", []):
            conn.execute(
                "INSERT INTO event_comments VALUES (?,?,?)",
                (row["username"], row["event_external_id"], row["content"]),
            )

        for row in data.get("federated_helpers", []):
            conn.execute(
                "INSERT INTO federated_helpers VALUES (?,?,?,?,?,?,?,?)",
                (
                    row["club_short_code"], row["external_id"],
                    row["display_name"], row.get("city", ""),
                    row.get("latitude"), row.get("longitude"),
                    row.get("radius_km", 0), row.get("notes", ""),
                ),
            )

        for row in data.get("notifications", []):
            conn.execute(
                "INSERT INTO notifications VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    row["notification_type"], row["recipient_username"],
                    row.get("channel", "in_app"), row["title"],
                    row.get("body", ""), row.get("url_type", ""),
                    row.get("url_ref", ""), row.get("status", "pending"),
                    row.get("sent_hours_ago", 0),
                ),
            )

        for row in data.get("event_registrations", []):
            conn.execute(
                "INSERT INTO event_registrations VALUES (?,?,?,?,?,?,?)",
                (
                    row["username"], row["event_slug"],
                    row.get("status", "confirmed"),
                    row.get("ticket_type", "standard"),
                    row.get("notes", ""), row.get("guests", 0),
                    row.get("days_ago", 0),
                ),
            )

        for row in data.get("event_favorites", []):
            conn.execute(
                "INSERT INTO event_favorites VALUES (?,?)",
                (row["username"], row["event_slug"]),
            )

        for row in data.get("contributions", []):
            conn.execute(
                "INSERT INTO contributions VALUES (?,?,?,?,?)",
                (
                    row["username"], row["contribution_type"],
                    row["title"], row["body"],
                    row.get("status", "approved"),
                ),
            )

        for row in data.get("comments", []):
            conn.execute(
                "INSERT INTO comments VALUES (?,?,?,?,?)",
                (
                    row["username"], row["target_type"],
                    row["target_index"], row["content"],
                    row.get("moderation_status", "approved"),
                ),
            )

        for row in data.get("reactions", []):
            conn.execute(
                "INSERT INTO reactions VALUES (?,?,?,?)",
                (
                    row["username"], row["target_type"],
                    row["target_index"], row["reaction_type"],
                ),
            )

        for row in data.get("activity_log", []):
            conn.execute(
                "INSERT INTO activity_log VALUES (?,?,?,?)",
                (
                    row["username"], row["activity_type"],
                    row["description"], row.get("days_ago", 0),
                ),
            )

        for row in data.get("membership_requests", []):
            conn.execute(
                "INSERT INTO membership_requests VALUES (?,?,?,?,?,?,?)",
                (
                    row["first_name"], row["last_name"],
                    row["email"], row.get("phone", ""),
                    row.get("motivation", ""),
                    row.get("status", "pending"),
                    row.get("days_ago", 0),
                ),
            )

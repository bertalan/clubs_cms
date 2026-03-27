"""
DemoLoader — reads a per-language SQLite fixture and populates ClubCMS.

Usage (via management command):
    python manage.py load_demo --lang en --primary --flush
    python manage.py load_demo --lang it
"""
from __future__ import annotations

import io
import json
import sqlite3
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import requests as http_requests
from django.contrib.contenttypes.models import ContentType
from django.core.files.images import ImageFile
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override

from wagtail.images.models import Image
from wagtail.models import Locale, Page, Site

from apps.core.models import Activity, Comment, Contribution, Reaction
from apps.events.models import EventFavorite, EventRegistration
from apps.core.models import ContributionsPage, SearchPage
from apps.notifications.models import NotificationsPage
from apps.federation.models import (
    ExternalEvent,
    ExternalEventComment,
    ExternalEventInterest,
    FederatedClub,
    FederationInfoPage,
)
from apps.members.models import ClubUser, MembershipRequest, MembersAreaPage
from apps.mutual_aid.models import AidRequest, FederatedHelper, MutualAidPage
from apps.notifications.models import NotificationQueue
from apps.website.models.pages import EventsAreaPage
from apps.places.models import (
    PlaceGalleryImage,
    PlaceIndexPage,
    PlacePage,
    PlaceTag,
    PlaceType,
    RoutePage,
    RouteStop,
)
from apps.core.demo.schema import PRODUCT_TRANSLATION_KEYS
from apps.website.models import (
    AboutPage,
    AidSkill,
    BoardPage,
    BrandAsset,
    ColorScheme,
    ContactPage,
    EventCategory,
    EventDetailPage,
    EventsPage,
    FAQ,
    Footer,
    FooterMenuItem,
    FooterSocialLink,
    GalleryPage,
    HomePage,
    MembershipPlansPage,
    Navbar,
    NavbarItem,
    NewsCategory,
    NewsIndexPage,
    NewsPage,
    PartnerCategory,
    PartnerIndexPage,
    PartnerPage,
    PhotoTag,
    PressPage,
    PressRelease,
    PrivacyPage,
    Product,
    SiteSettings,
    Testimonial,
    TransparencyPage,
)

# ---- constants -----------------------------------------------------------

LOREMFLICKR = "https://loremflickr.com/{w}/{h}/{keywords}"

PAGE_TYPE_MAP: dict[str, type] = {
    "home": HomePage,
    "about": AboutPage,
    "board": BoardPage,
    "news_index": NewsIndexPage,
    "news": NewsPage,
    "events_page": EventsPage,
    "event": EventDetailPage,
    "events_area": EventsAreaPage,
    "gallery": GalleryPage,
    "contact": ContactPage,
    "privacy": PrivacyPage,
    "transparency": TransparencyPage,
    "press": PressPage,
    "membership_plans": MembershipPlansPage,
    "federation": FederationInfoPage,
    "mutual_aid": MutualAidPage,
    "search": SearchPage,
    "contributions": ContributionsPage,
    "notifications": NotificationsPage,
    "members_area": MembersAreaPage,
    "partner_index": PartnerIndexPage,
    "partner": PartnerPage,
    "place_index": PlaceIndexPage,
    "place": PlacePage,
    "route": RoutePage,
}

# Fields that need special type handling per page model
DATE_FIELDS = {
    "display_date", "pub_date", "last_updated", "partnership_start",
}
DATETIME_FIELDS = {
    "start_date", "end_date", "registration_deadline", "early_bird_deadline",
}
DECIMAL_FIELDS = {
    "base_fee", "registration_fee", "latitude", "longitude", "distance_km",
    "price",
}
CATEGORY_FIELDS = {
    "category",  # FK resolved by slug
}
TIMEDELTA_FIELDS = {
    "estimated_duration",  # stored as minutes integer
}


class DemoLoader:
    """Reads a per-language SQLite fixture and populates the CMS."""

    def __init__(self, db_path: str | Path, stdout, style):
        self.db_path = Path(db_path)
        self.stdout = stdout
        self.style = style
        self.conn: sqlite3.Connection | None = None
        self.locale: Locale | None = None
        self.lang: str = ""
        self.images: dict[str, Image] = {}
        self.created_pages: dict[str, Page] = {}
        # Category caches
        self.news_categories: dict[str, NewsCategory] = {}
        self.event_categories: dict[str, EventCategory] = {}
        self.partner_categories: dict[str, PartnerCategory] = {}

    # ---- public API -------------------------------------------------------

    def load(self, *, primary: bool = False, flush: bool = False):
        """Run the full import pipeline."""
        if not self.db_path.exists():
            self.stdout.write(self.style.ERROR(
                f"Fixture not found: {self.db_path}"
            ))
            return

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.primary = primary

        try:
            self.lang = self._meta("language")
            self.stdout.write(f"\nLoading demo data for '{self.lang}'...")

            if flush:
                self._flush()

            self.locale, _ = Locale.objects.get_or_create(
                language_code=self.lang
            )

            # 1. Snippets & categories (idempotent)
            self._load_color_scheme()
            self._load_categories()
            self._load_products()
            self._load_testimonials()
            self._load_faqs()
            self._load_photo_tags()
            self._load_press_releases()
            self._load_brand_assets()
            self._load_aid_skills()
            self._load_place_tags()

            # 2. Pages
            home = self._create_pages(primary=primary)
            if not home:
                return

            # 3. Navigation
            navbar = self._load_navbar(home)
            footer = self._load_footer(home)

            # 4. Site settings
            self._load_site_settings(home, navbar, footer, primary=primary)

            # 5. Images
            self.images = self._download_images()
            self._assign_page_images()

            # 6. Members
            members = self._load_members()

            # 7. Mutual-aid requests
            self._load_aid_requests(members)

            # 8. Event registrations & favorites
            self._load_event_registrations(members)
            self._load_event_favorites(members)

            # 9. Social interactions
            self._load_contributions(members)
            self._load_comments_and_reactions(members)
            self._load_activity_log(members)

            # 10. Membership requests
            self._load_membership_requests()

            # 11. Federation
            self._load_federated_clubs(members)

            # 12. Notifications
            self._load_notifications(members)

            # 13. Route stops (need pages to exist)
            self._load_route_stops()

            self.stdout.write(self.style.SUCCESS(
                f"\nDemo content loaded successfully for '{self.lang}'! "
                f"Visit http://localhost:8888/ to see the site."
            ))

        finally:
            self.conn.close()

    # ---- helpers ----------------------------------------------------------

    def _meta(self, key: str) -> str:
        row = self.conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else ""

    def _rows(self, table: str) -> list[sqlite3.Row]:
        return self.conn.execute(f"SELECT * FROM [{table}]").fetchall()

    def _flush(self):
        """Remove all demo-created content."""
        self.stdout.write("Flushing existing content...")
        NotificationQueue.objects.all().delete()
        FederatedClub.objects.all().delete()
        MembershipRequest.objects.all().delete()
        Activity.objects.all().delete()
        Reaction.objects.all().delete()
        Comment.objects.all().delete()
        Contribution.objects.all().delete()
        EventRegistration.objects.all().delete()
        EventFavorite.objects.all().delete()
        Image.objects.filter(file__startswith="original_images/demo_").delete()
        ClubUser.objects.filter(username__startswith="demo_").delete()
        AidRequest.objects.filter(requester_name__startswith="Demo:").delete()
        RouteStop.objects.all().delete()
        PlaceGalleryImage.objects.all().delete()
        PlaceTag.objects.all().delete()
        for model in [
            HomePage, PlaceIndexPage, SiteSettings, ColorScheme,
            Navbar, Footer, NewsCategory, EventCategory, PartnerCategory,
            Product, Testimonial, FAQ, PhotoTag, PressRelease,
            BrandAsset, AidSkill,
        ]:
            model.objects.all().delete()

    # ---- snippets & categories -------------------------------------------

    def _load_color_scheme(self):
        if ColorScheme.objects.exists():
            return
        for row in self._rows("color_scheme"):
            ColorScheme.objects.create(
                name=row["name"],
                primary=row["primary_color"],
                secondary=row["secondary_color"],
                accent=row["accent"],
                surface=row["surface"],
                surface_alt=row["surface_alt"],
                text_primary=row["text_primary"],
                text_muted=row["text_muted"],
                is_dark_mode=bool(row["is_dark_mode"]),
            )
            self.stdout.write(f"  Created ColorScheme: {row['name']}")

    def _load_categories(self):
        for row in self._rows("categories"):
            cat_type = row["cat_type"]
            if cat_type == "news":
                cat, created = NewsCategory.objects.get_or_create(
                    slug=row["slug"],
                    defaults={
                        "name": row["name"],
                        "color": row["color"],
                        "description": row["description"],
                    },
                )
                self.news_categories[row["slug"]] = cat
            elif cat_type == "event":
                cat, created = EventCategory.objects.get_or_create(
                    slug=row["slug"],
                    defaults={"name": row["name"], "icon": row["icon"]},
                )
                self.event_categories[row["slug"]] = cat
            elif cat_type == "partner":
                cat, created = PartnerCategory.objects.get_or_create(
                    slug=row["slug"],
                    defaults={
                        "name": row["name"],
                        "icon": row["icon"],
                        "order": row["sort_order"],
                    },
                )
                self.partner_categories[row["slug"]] = cat
            if created:
                self.stdout.write(f"  Created {cat_type} category: {row['name']}")

    def _load_products(self):
        for row in self._rows("products"):
            tk_key = row["translation_key"]
            tk_uuid = uuid.UUID(PRODUCT_TRANSLATION_KEYS[tk_key])

            # Already exists in this locale?
            existing = Product.objects.filter(
                locale=self.locale, translation_key=tk_uuid
            ).first()
            if existing:
                continue

            if self.primary:
                Product.objects.create(
                    slug=row["slug"],
                    name=row["name"],
                    description=row["description"],
                    price=Decimal(str(row["price"])),
                    grants_vote=bool(row["grants_vote"]),
                    grants_events=bool(row["grants_events"]),
                    grants_upload=bool(row["grants_upload"]),
                    grants_discount=bool(row["grants_discount"]),
                    discount_percent=row["discount_percent"],
                    order=row["sort_order"],
                    translation_key=tk_uuid,
                    locale=self.locale,
                )
                self.stdout.write(f"  Created Product: {row['name']}")
            else:
                # Secondary locale: copy from source
                source = Product.objects.filter(
                    translation_key=tk_uuid
                ).exclude(locale=self.locale).first()
                if source:
                    translated = source.copy_for_translation(self.locale)
                    translated.name = row["name"]
                    translated.slug = row["slug"]
                    translated.description = row["description"]
                    translated.save()
                    self.stdout.write(
                        f"  Translated Product: {row['name']}"
                    )

    def _load_testimonials(self):
        if not self.primary:
            return
        for row in self._rows("testimonials"):
            _, created = Testimonial.objects.get_or_create(
                author_name=row["author_name"],
                defaults={
                    "quote": row["quote"],
                    "author_role": row["author_role"],
                    "featured": bool(row["featured"]),
                },
            )
            if created:
                self.stdout.write(f"  Created Testimonial: {row['author_name']}")

    def _load_faqs(self):
        if not self.primary:
            return
        for row in self._rows("faqs"):
            _, created = FAQ.objects.get_or_create(
                question=row["question"],
                defaults={
                    "answer": row["answer"],
                    "category": row["category"],
                    "order": row["sort_order"],
                },
            )
            if created:
                self.stdout.write(f"  Created FAQ: {row['question'][:50]}")

    def _load_photo_tags(self):
        if not self.primary:
            return
        for row in self._rows("photo_tags"):
            _, created = PhotoTag.objects.get_or_create(
                slug=row["slug"], defaults={"name": row["name"]}
            )
            if created:
                self.stdout.write(f"  Created PhotoTag: {row['name']}")

    def _load_press_releases(self):
        if not self.primary:
            return
        for row in self._rows("press_releases"):
            _, created = PressRelease.objects.get_or_create(
                title=row["title"],
                defaults={
                    "date": date.fromisoformat(row["pub_date"]),
                    "body": row["body"],
                    "is_archived": bool(row["is_archived"]),
                },
            )
            if created:
                self.stdout.write(f"  Created PressRelease: {row['title'][:50]}")

    def _load_brand_assets(self):
        if not self.primary:
            return
        for row in self._rows("brand_assets"):
            _, created = BrandAsset.objects.get_or_create(
                name=row["name"],
                defaults={
                    "category": row["category"],
                    "description": row["description"],
                    "order": row["sort_order"],
                },
            )
            if created:
                self.stdout.write(f"  Created BrandAsset: {row['name'][:50]}")

    def _load_aid_skills(self):
        if not self.primary:
            return
        for row in self._rows("aid_skills"):
            _, created = AidSkill.objects.get_or_create(
                slug=row["slug"],
                defaults={
                    "name": row["name"],
                    "description": row["description"],
                    "category": row["category"],
                    "order": row["sort_order"],
                },
            )
            if created:
                self.stdout.write(f"  Created AidSkill: {row['name']}")

    def _load_place_tags(self):
        if not self.primary:
            return
        for row in self._rows("place_tags"):
            PlaceTag.objects.get_or_create(
                name=row["name"],
                defaults={"slug": row["slug"]},
            )

    # ---- pages -----------------------------------------------------------

    def _create_pages(self, *, primary: bool) -> HomePage | None:
        """Create all pages from the fixture in this locale's tree."""
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found!"))
            return None

        pages_data = self._rows("pages")
        # Topological sort: parents before children
        by_slug = {r["slug"]: r for r in pages_data}
        ordered: list = []
        visited: set = set()

        def _visit(row):
            slug = row["slug"]
            if slug in visited:
                return
            visited.add(slug)
            parent = row["parent_slug"]
            if parent and parent in by_slug:
                _visit(by_slug[parent])
            ordered.append(row)

        for row in pages_data:
            _visit(row)
        pages_data = ordered

        if primary:
            # Remove Wagtail default welcome page
            Page.objects.filter(depth=2, slug="home").exclude(
                content_type__model="homepage"
            ).delete()
            Page.fix_tree()
            root = Page.objects.filter(depth=1).first()

        for row in pages_data:
            self._create_single_page(row, root, primary=primary)

        home = self.created_pages.get("home")
        if not home:
            # Try to look it up from the fixture's home slug
            home_row = next(
                (r for r in pages_data if r["page_type"] == "home"), None
            )
            if home_row:
                home = HomePage.objects.filter(
                    locale=self.locale, slug=home_row["slug"]
                ).first()

        if home:
            self.stdout.write(
                f"  Created {len(self.created_pages)} pages "
                f"for locale '{self.lang}'"
            )
        return home

    def _create_single_page(
        self, row: sqlite3.Row, root: Page, *, primary: bool
    ):
        """Create one page and register it in self.created_pages."""
        page_type = row["page_type"]
        model = PAGE_TYPE_MAP.get(page_type)
        if not model:
            self.stdout.write(f"  Unknown page type: {page_type}")
            return

        slug = row["slug"]
        tk = row["translation_key"]

        # Skip if this exact page already exists in this locale
        existing = model.objects.filter(locale=self.locale, slug=slug).first()
        if not existing:
            # For secondary locales, also check by translation_key
            existing = model.objects.filter(
                locale=self.locale, translation_key=uuid.UUID(tk)
            ).first()
        if existing:
            self.created_pages[slug] = existing
            return

        fields = json.loads(row["fields"]) if row["fields"] else {}
        resolved = self._resolve_fields(model, fields)

        # --- Secondary locale: use copy_for_translation if source exists ---
        if not primary:
            source = (
                Page.objects.filter(translation_key=uuid.UUID(tk))
                .exclude(locale=self.locale)
                .first()
            )
            if source:
                source = source.specific
                translated = source.copy_for_translation(self.locale)
                # Update title and content fields from fixture
                translated.title = row["title"]
                # Only override slug if it won't conflict with siblings
                parent = translated.get_parent()
                if Page._slug_is_available(slug, parent, page=translated):
                    translated.slug = slug
                for key, value in resolved.items():
                    setattr(translated, key, value)
                translated.save_revision().publish()
                # Register under fixture slug for parent lookups by children
                self.created_pages[slug] = translated
                return

        # --- Primary locale or no source page: create from scratch ---
        page = model(
            title=row["title"],
            slug=slug,
            locale=self.locale,
            translation_key=uuid.UUID(tk),
            **resolved,
        )

        # Determine parent
        parent_slug = row["parent_slug"]
        if parent_slug is None:
            # Top-level page (HomePage) → child of root
            parent = root
        else:
            parent = self.created_pages.get(parent_slug)
            if not parent:
                self.stdout.write(
                    f"  Parent '{parent_slug}' not found for '{slug}', skipping."
                )
                return

        parent.add_child(instance=page)
        page.save_revision().publish()
        self.created_pages[slug] = page

        # Handle place tags
        if page_type == "place" and "_tags" in fields:
            for tag_name in fields["_tags"]:
                tag = PlaceTag.objects.filter(name=tag_name).first()
                if tag:
                    page.tags.add(tag)

    def _resolve_fields(
        self, model: type, fields: dict
    ) -> dict:
        """Convert JSON field values to proper Python types."""
        resolved = {}
        skip_keys = {"_tags"}  # handled separately

        for key, value in fields.items():
            if key in skip_keys:
                continue

            if value is None:
                resolved[key] = value
                continue

            if key in DATE_FIELDS:
                resolved[key] = self._parse_date(value) if value else None
            elif key in DATETIME_FIELDS:
                resolved[key] = self._parse_datetime(value) if value else None
            elif key in DECIMAL_FIELDS:
                resolved[key] = Decimal(str(value))
            elif key in TIMEDELTA_FIELDS:
                resolved[key] = timedelta(minutes=int(value))
            elif key in CATEGORY_FIELDS:
                resolved[key] = self._resolve_category(model, value)
            else:
                resolved[key] = value

        return resolved

    def _resolve_category(self, model, slug: str):
        """Resolve a category slug to a category object based on page model."""
        if model in (NewsPage,):
            return self.news_categories.get(slug)
        elif model in (EventDetailPage,):
            return self.event_categories.get(slug)
        elif model in (PartnerPage,):
            return self.partner_categories.get(slug)
        return None

    @staticmethod
    def _parse_date(value: str) -> date:
        """Parse a date string: ISO format or relative '+N' / '-N' / 'N' days."""
        stripped = value.lstrip("+-")
        if stripped.isdigit():
            return date.today() + timedelta(days=int(value))
        return date.fromisoformat(value)

    @staticmethod
    def _parse_datetime(value: str):
        """Parse to a timezone-aware datetime: ISO or relative '+N' days."""
        stripped = value.lstrip("+-")
        if stripped.isdigit():
            d = date.today() + timedelta(days=int(value))
            return timezone.make_aware(datetime(d.year, d.month, d.day, 10, 0))
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            return timezone.make_aware(dt)
        return dt

    # ---- navigation ------------------------------------------------------

    def _load_navbar(self, home: HomePage) -> Navbar:
        if Navbar.objects.exists():
            return Navbar.objects.first()

        navbar = Navbar.objects.create(name="Main Navigation", show_search=True)
        rows = self._rows("navbar_items")

        # Group: top-level first, then sub-items
        top_items = {}
        sub_items = []
        for row in sorted(rows, key=lambda r: r["sort_order"]):
            if row["parent_label"]:
                sub_items.append(row)
            else:
                page = self._resolve_page_by_slug(row["link_page_slug"])
                item = NavbarItem.objects.create(
                    navbar=navbar,
                    sort_order=row["sort_order"],
                    label=row["label"],
                    link_page=page,
                    link_url=row["link_url"] or "",
                    is_cta=bool(row["is_cta"]),
                    open_new_tab=bool(row["open_new_tab"]),
                )
                top_items[row["label"]] = item

        # Sub-items
        for row in sorted(sub_items, key=lambda r: r["sort_order"]):
            parent = top_items.get(row["parent_label"])
            if not parent:
                continue
            page = self._resolve_page_by_slug(row["link_page_slug"])
            url = row["link_url"] or ""
            # Resolve reverse URL patterns stored as "reverse:name"
            if url.startswith("reverse:"):
                url_name = url[len("reverse:"):]
                with override(self.lang):
                    try:
                        url = reverse(url_name)
                    except Exception:
                        url = ""
            NavbarItem.objects.create(
                navbar=navbar,
                parent=parent,
                sort_order=row["sort_order"],
                label=row["label"],
                link_page=page,
                link_url=url,
                is_cta=bool(row["is_cta"]),
                open_new_tab=bool(row["open_new_tab"]),
            )

        self.stdout.write("  Created Navbar with menu items")
        return navbar

    def _load_footer(self, home: HomePage) -> Footer:
        if Footer.objects.exists():
            return Footer.objects.first()

        # Read footer settings from site_settings table
        s = {r["key"]: r["value"] for r in self._rows("site_settings")}
        footer = Footer.objects.create(
            name="Main Footer",
            description=s.get(
                "footer_description",
                "<p>Moto Club Aquile Rosse ASD</p>",
            ),
            copyright_text=s.get("copyright_text", ""),
            phone=s.get("phone", ""),
            email=s.get("email", ""),
            address=s.get("address", ""),
        )

        for row in self._rows("footer_items"):
            page = self._resolve_page_by_slug(row["link_page_slug"])
            FooterMenuItem.objects.create(
                footer=footer,
                sort_order=row["sort_order"],
                label=row["label"],
                link_page=page,
                link_url=row["link_url"] or "",
            )

        for row in self._rows("footer_social_links"):
            FooterSocialLink.objects.create(
                footer=footer,
                sort_order=row["sort_order"],
                platform=row["platform"],
                url=row["url"],
            )

        self.stdout.write("  Created Footer with menu items and social links")
        return footer

    def _resolve_page_by_slug(self, slug: str):
        """Find a page by slug in created_pages or DB."""
        if not slug:
            return None
        page = self.created_pages.get(slug)
        if page:
            return page
        return Page.objects.filter(
            locale=self.locale, slug=slug
        ).first()

    # ---- site settings ---------------------------------------------------

    def _load_site_settings(
        self, home: HomePage, navbar: Navbar, footer: Footer,
        *, primary: bool,
    ):
        site = Site.objects.filter(is_default_site=True).first()
        s = {r["key"]: r["value"] for r in self._rows("site_settings")}

        if primary:
            if site:
                site.root_page = home
                site.site_name = s.get("site_name", "")
                site.save()
            else:
                site = Site.objects.create(
                    hostname="localhost",
                    port=8888,
                    root_page=home,
                    is_default_site=True,
                    site_name=s.get("site_name", ""),
                )

        if not site:
            return

        settings, _ = SiteSettings.objects.get_or_create(site=site)
        settings.site_name = s.get("site_name", settings.site_name)
        settings.tagline = s.get("tagline", "")
        settings.description = s.get("description", "")
        settings.theme = s.get("theme", "velocity")
        settings.color_scheme = None
        settings.navbar = navbar
        settings.footer = footer
        settings.phone = s.get("phone", "")
        settings.email = s.get("email", "")
        settings.address = s.get("address", "")
        settings.hours = s.get("hours", "")
        settings.facebook_url = s.get("facebook_url", "")
        settings.instagram_url = s.get("instagram_url", "")
        settings.youtube_url = s.get("youtube_url", "")
        settings.map_default_center = s.get("map_default_center", "")
        settings.map_default_zoom = int(s.get("map_default_zoom", "12"))
        settings.save()
        self.stdout.write("  Updated SiteSettings")

    # ---- images ----------------------------------------------------------

    def _download_images(self) -> dict[str, Image]:
        """Download demo images from LoremFlickr."""
        self.stdout.write("\nDownloading demo images...")
        images = {}
        for row in self._rows("images"):
            key = row["key"]
            # Skip if already downloaded
            existing = Image.objects.filter(
                title__startswith=f"Demo: {key}"
            ).first()
            if existing:
                images[key] = existing
                continue
            try:
                url = LOREMFLICKR.format(
                    w=row["width"],
                    h=row["height"],
                    keywords=row["keywords"],
                )
                resp = http_requests.get(url, timeout=30, allow_redirects=True)
                resp.raise_for_status()
                fname = f"demo_{uuid.uuid4().hex[:8]}.jpg"
                image_file = ImageFile(io.BytesIO(resp.content), name=fname)
                img = Image(
                    title=f"Demo: {key}",
                    file=image_file,
                    width=row["width"],
                    height=row["height"],
                )
                img.save()
                images[key] = img
                self.stdout.write(f"  Downloaded: {key}")
            except Exception as e:
                self.stdout.write(f"  Failed to download {key}: {e}")
        return images

    def _assign_page_images(self):
        """Assign downloaded images to pages (hero, cover, etc.)."""
        # Map image keys to page slugs for hero_image
        HERO_MAP = {
            "hero_homepage": "home",
            "hero_contact": self._meta("slug_contact"),
        }
        for img_key, page_slug in HERO_MAP.items():
            if img_key in self.images and page_slug in self.created_pages:
                page = self.created_pages[page_slug]
                if hasattr(page, "hero_image") and not page.hero_image:
                    page.hero_image = self.images[img_key]
                    page.save()

        # About page: hero_image + cover_image
        about_slug = self._meta("slug_about")
        if "hero_about" in self.images and about_slug in self.created_pages:
            page = self.created_pages[about_slug]
            if hasattr(page, "hero_image") and not page.hero_image:
                page.hero_image = self.images["hero_about"]
            if hasattr(page, "cover_image") and not page.cover_image:
                page.cover_image = self.images["hero_about"]
            page.save()

        # Event images → cover_image
        event_map = {
            "event_mandello": self._meta("slug_event_mandello"),
            "event_pisa": self._meta("slug_event_pisa"),
            "event_orobie": self._meta("slug_event_orobie"),
            "event_franciacorta": self._meta("slug_event_franciacorta"),
            "event_children": self._meta("slug_event_children"),
            "event_garda": self._meta("slug_event_garda"),
        }
        for img_key, slug in event_map.items():
            if img_key in self.images and slug in self.created_pages:
                page = self.created_pages[slug]
                if hasattr(page, "cover_image") and not page.cover_image:
                    page.cover_image = self.images[img_key]
                    page.save()

        # News images → cover_image
        news_map = {
            "news_mandello": self._meta("slug_news_kickoff"),
            "news_pisa": self._meta("slug_news_pisa"),
            "news_bayern": self._meta("slug_news_bayern"),
            "news_officina": self._meta("slug_news_workshop"),
            "news_manutenzione": self._meta("slug_news_seasonal"),
            "news_assemblea": self._meta("slug_news_assembly"),
        }
        for img_key, slug in news_map.items():
            if img_key in self.images and slug in self.created_pages:
                page = self.created_pages[slug]
                if hasattr(page, "cover_image") and not page.cover_image:
                    page.cover_image = self.images[img_key]
                    page.save()

        # Partner pages → cover_image (reuse partner_bgmoto for all)
        if "partner_bgmoto" in self.images:
            for slug, page in self.created_pages.items():
                if isinstance(page, PartnerPage):
                    if hasattr(page, "cover_image") and not page.cover_image:
                        page.cover_image = self.images["partner_bgmoto"]
                        page.save()

        # Route pages → cover_image (reuse an event image)
        fallback_img = self.images.get("event_garda")
        if fallback_img:
            for slug, page in self.created_pages.items():
                if isinstance(page, RoutePage):
                    if hasattr(page, "cover_image") and not page.cover_image:
                        page.cover_image = fallback_img
                        page.save()

        self.stdout.write("  Assigned images to pages")

    # ---- members ---------------------------------------------------------

    def _load_members(self) -> list[ClubUser]:
        self.stdout.write("\nCreating demo members...")
        members = []
        for row in self._rows("members"):
            username = row["username"]
            if ClubUser.objects.filter(username=username).exists():
                members.append(ClubUser.objects.get(username=username))
                continue

            data = dict(row)
            image_key = data.pop("image_key", "")
            # Convert dates
            for df in ("birth_date", "membership_date", "membership_expiry"):
                if data[df]:
                    data[df] = date.fromisoformat(data[df])
            # Convert booleans
            for bf in (
                "aid_available", "show_in_directory",
                "public_profile", "newsletter",
            ):
                data[bf] = bool(data[bf])

            member = ClubUser(**data)
            member.set_password("demo2026!")
            if image_key and image_key in self.images:
                member.photo = self.images[image_key]
            member.save()
            members.append(member)
            self.stdout.write(
                f"  Created member: {data['first_name']} {data['last_name']}"
            )
        return members

    # ---- aid requests ----------------------------------------------------

    def _load_aid_requests(self, members: list[ClubUser]):
        self.stdout.write("\nCreating aid requests...")
        if AidRequest.objects.filter(
            requester_name__startswith="Demo:"
        ).exists():
            return

        member_map = {m.username: m for m in members}
        for row in self._rows("aid_requests"):
            helper = member_map.get(row["helper_username"])
            requester = member_map.get(row["requester_username"])
            if not helper:
                continue
            AidRequest.objects.create(
                helper=helper,
                requester_name=row["requester_name"],
                requester_phone=row["requester_phone"],
                requester_email=row["requester_email"],
                requester_user=requester,
                issue_type=row["issue_type"],
                description=row["description"],
                location=row["location"],
                urgency=row["urgency"],
                status=row["status"],
            )
        self.stdout.write(f"  Created aid requests")

    # ---- event registrations & favorites ---------------------------------

    def _load_event_registrations(self, members: list[ClubUser]):
        self.stdout.write("\nCreating event registrations...")
        if EventRegistration.objects.filter(
            user__username__startswith="demo_"
        ).exists():
            return

        member_map = {m.username: m for m in members}
        now = timezone.now()
        for row in self._rows("event_registrations"):
            user = member_map.get(row["username"])
            event = EventDetailPage.objects.filter(
                locale=self.locale, slug=row["event_slug"]
            ).first()
            if not user or not event:
                continue
            EventRegistration.objects.create(
                user=user,
                event=event,
                status=row["status"],
                notes=row["notes"],
                guests=row["guests"],
                registered_at=now - timedelta(days=row["days_ago"]),
            )
        self.stdout.write("  Created event registrations")

    def _load_event_favorites(self, members: list[ClubUser]):
        if EventFavorite.objects.filter(
            user__username__startswith="demo_"
        ).exists():
            return

        member_map = {m.username: m for m in members}
        for row in self._rows("event_favorites"):
            user = member_map.get(row["username"])
            event = EventDetailPage.objects.filter(
                locale=self.locale, slug=row["event_slug"]
            ).first()
            if user and event:
                EventFavorite.objects.get_or_create(user=user, event=event)
        self.stdout.write("  Created event favorites")

    # ---- contributions, comments, reactions ------------------------------

    def _load_contributions(self, members: list[ClubUser]):
        self.stdout.write("\nCreating contributions...")
        if Contribution.objects.exists():
            return

        member_map = {m.username: m for m in members}
        for row in self._rows("contributions"):
            user = member_map.get(row["username"])
            if not user:
                continue
            Contribution.objects.create(
                user=user,
                contribution_type=row["contribution_type"],
                title=row["title"],
                body=row["body"],
                status=row["status"],
            )
        self.stdout.write("  Created contributions")

    def _load_comments_and_reactions(self, members: list[ClubUser]):
        self.stdout.write("\nCreating comments and reactions...")
        if Comment.objects.exists() or Reaction.objects.exists():
            return

        member_map = {m.username: m for m in members}
        news_ct = ContentType.objects.get_for_model(NewsPage)
        event_ct = ContentType.objects.get_for_model(EventDetailPage)

        news_pages = list(
            NewsPage.objects.filter(locale=self.locale).live()[:6]
        )
        event_pages = list(
            EventDetailPage.objects.filter(locale=self.locale).live()[:6]
        )

        ct_map = {"news": news_ct, "event": event_ct}
        pages_map = {"news": news_pages, "event": event_pages}

        for row in self._rows("comments"):
            user = member_map.get(row["username"])
            ct = ct_map.get(row["target_type"])
            pages = pages_map.get(row["target_type"], [])
            idx = row["target_index"]
            if user and ct and idx < len(pages):
                Comment.objects.create(
                    user=user,
                    content=row["content"],
                    content_type=ct,
                    object_id=pages[idx].pk,
                    moderation_status=row["moderation_status"],
                )

        for row in self._rows("reactions"):
            user = member_map.get(row["username"])
            ct = ct_map.get(row["target_type"])
            pages = pages_map.get(row["target_type"], [])
            idx = row["target_index"]
            if user and ct and idx < len(pages):
                Reaction.objects.create(
                    user=user,
                    content_type=ct,
                    object_id=pages[idx].pk,
                    reaction_type=row["reaction_type"],
                )

        self.stdout.write("  Created comments and reactions")

    # ---- activity log ----------------------------------------------------

    def _load_activity_log(self, members: list[ClubUser]):
        if Activity.objects.filter(
            user__username__startswith="demo_"
        ).exists():
            return

        member_map = {m.username: m for m in members}
        now = timezone.now()
        for row in self._rows("activity_log"):
            user = member_map.get(row["username"])
            if user:
                Activity.objects.create(
                    user=user,
                    action=row["activity_type"],
                    target_title=row["description"],
                    created_at=now - timedelta(days=row["days_ago"]),
                )
        self.stdout.write("  Created activity log")

    # ---- membership requests ---------------------------------------------

    def _load_membership_requests(self):
        if MembershipRequest.objects.exists():
            return

        product = Product.objects.first()
        if not product:
            return

        now = timezone.now()
        for row in self._rows("membership_requests"):
            username = f"demo_req_{row['first_name'].lower()}"
            user, _ = ClubUser.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "email": row["email"],
                },
            )
            MembershipRequest.objects.create(
                user=user,
                product=product,
                status=row["status"],
                notes=row["motivation"],
            )
        self.stdout.write("  Created membership requests")

    # ---- federation ------------------------------------------------------

    def _load_federated_clubs(self, members: list[ClubUser]):
        self.stdout.write("\nCreating federated clubs...")
        if FederatedClub.objects.exists():
            return

        admin = ClubUser.objects.filter(is_superuser=True).first()
        now = timezone.now()
        member_map = {m.username: m for m in members}

        clubs = {}
        for row in self._rows("federated_clubs"):
            club = FederatedClub.objects.create(
                name=row["name"],
                short_code=row["short_code"],
                city=row["city"],
                base_url=row["base_url"],
                logo_url=row["logo_url"],
                description=row["description"],
                api_key=row["api_key"],
                is_active=bool(row["is_active"]),
                is_approved=bool(row["is_approved"]),
                share_our_events=bool(row["share_our_events"]),
                last_sync=now - timedelta(hours=6),
                created_by=admin,
            )
            clubs[row["short_code"]] = club
        self.stdout.write(f"  Created {len(clubs)} federated clubs")

        # External events
        ext_events = {}
        for row in self._rows("external_events"):
            club = clubs.get(row["club_short_code"])
            if not club:
                continue
            evt = ExternalEvent.objects.create(
                source_club=club,
                external_id=row["external_id"],
                event_name=row["event_name"],
                start_date=now + timedelta(days=row["start_days_offset"]),
                end_date=now + timedelta(days=row["end_days_offset"]),
                location_name=row["location_name"],
                location_address=row["location_address"],
                location_lat=row["location_lat"],
                location_lon=row["location_lon"],
                description=row["description"],
                detail_url=row["detail_url"],
                is_approved=bool(row["is_approved"]),
            )
            ext_events[row["external_id"]] = evt
        self.stdout.write(f"  Created {len(ext_events)} external events")

        # Interests
        for row in self._rows("event_interests"):
            user = member_map.get(row["username"])
            evt = ext_events.get(row["event_external_id"])
            if user and evt:
                ExternalEventInterest.objects.create(
                    user=user,
                    external_event=evt,
                    interest_level=row["interest_level"],
                )

        # Comments
        for row in self._rows("event_comments"):
            user = member_map.get(row["username"])
            evt = ext_events.get(row["event_external_id"])
            if user and evt:
                ExternalEventComment.objects.create(
                    user=user,
                    external_event=evt,
                    content=row["content"],
                )

        # Federated helpers
        helpers = []
        for row in self._rows("federated_helpers"):
            club = clubs.get(row["club_short_code"])
            if club:
                helpers.append(FederatedHelper(
                    source_club=club,
                    external_id=row["external_id"],
                    display_name=row["display_name"],
                    city=row["city"],
                    latitude=row["latitude"],
                    longitude=row["longitude"],
                    radius_km=row["radius_km"],
                    notes=row["notes"],
                ))
        if helpers:
            FederatedHelper.objects.bulk_create(helpers)
        self.stdout.write(f"  Created {len(helpers)} federated helpers")

        # Enable federation on MutualAidPage
        aid_page = MutualAidPage.objects.live().first()
        if aid_page and not aid_page.enable_federation:
            aid_page.enable_federation = True
            aid_page.save()

    # ---- notifications ---------------------------------------------------

    def _load_notifications(self, members: list[ClubUser]):
        self.stdout.write("\nCreating notifications...")
        demo_types = {
            "event_reminder", "comment_reply", "membership_approved",
            "aid_request", "new_event", "contribution_approved",
        }
        if NotificationQueue.objects.filter(
            notification_type__in=demo_types
        ).exists():
            return

        member_map = {m.username: m for m in members}
        now = timezone.now()

        for row in self._rows("notifications"):
            user = member_map.get(row["recipient_username"])
            if not user:
                continue

            # Resolve URL
            url = ""
            url_type = row["url_type"]
            url_ref = row["url_ref"]
            if url_type == "reverse":
                with override(self.lang):
                    try:
                        url = reverse(url_ref)
                    except Exception:
                        pass
            elif url_type == "page":
                page = self.created_pages.get(url_ref)
                if page:
                    url = page.url

            data = {
                "notification_type": row["notification_type"],
                "recipient": user,
                "channel": row["channel"],
                "title": row["title"],
                "body": row["body"],
                "url": url,
                "status": row["status"],
            }
            if row["sent_hours_ago"] and row["status"] == "sent":
                data["sent_at"] = now - timedelta(hours=row["sent_hours_ago"])

            NotificationQueue.objects.create(**data)

        self.stdout.write("  Created notifications")

    # ---- route stops (post-page-creation) --------------------------------

    def _load_route_stops(self):
        for row in self._rows("route_stops"):
            route = RoutePage.objects.filter(
                locale=self.locale, slug=row["route_slug"]
            ).first()
            place = PlacePage.objects.filter(
                locale=self.locale, slug=row["place_slug"]
            ).first()
            if route and place:
                RouteStop.objects.get_or_create(
                    route=route,
                    place=place,
                    defaults={
                        "sort_order": row["sort_order"],
                        "note": row["note"],
                    },
                )
        self.stdout.write("  Created route stops")

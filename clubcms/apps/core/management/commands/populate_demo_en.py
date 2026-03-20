"""
Management command to populate ClubCMS with realistic demo content in English (EN).

Inherits structure from populate_demo_it and overrides all content methods
with English text. The site default locale is English.

Usage:
    python manage.py populate_demo_en
    docker compose exec web python manage.py populate_demo_en
    docker compose exec web python manage.py populate_demo_en --flush
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import override

from wagtail.models import Locale, Page, Site

from apps.core.management.commands.populate_demo_it import Command as ITCommand
from apps.core.models import Comment, Reaction, Contribution
from apps.federation.models import FederationInfoPage
from apps.members.models import ClubUser
from apps.mutual_aid.models import AidRequest
from apps.notifications.models import NotificationQueue
from apps.website.models import (
    AboutPage,
    BoardPage,
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
    PressPage,
    PressRelease,
    PrivacyPage,
    Product,
    SiteSettings,
    Testimonial,
    TransparencyPage,
)


class Command(ITCommand):
    help = "Populate ClubCMS with realistic demo content in English"

    # ------------------------------------------------------------------
    # Override: EN translations step → create IT copies instead
    # ------------------------------------------------------------------

    def _create_en_translations(self, home_page):
        """Create Italian copies of EN pages, then fill them with Italian content."""
        it_locale, _ = Locale.objects.get_or_create(language_code="it")
        self.stdout.write("Creating Italian page translations...")

        pages = [home_page] + list(
            home_page.get_descendants().specific().order_by("path")
        )

        count = 0
        skipped = 0
        for page in pages:
            try:
                page.copy_for_translation(it_locale, copy_parents=True)
                count += 1
            except Exception:
                skipped += 1

        self.stdout.write(
            f"  Created {count} Italian pages"
            + (f" ({skipped} skipped / already exist)" if skipped else "")
        )

        # Publish all IT pages and update content with Italian text
        from apps.core.management.commands.update_it_content import (
            Command as UpdateITCommand,
        )

        self.stdout.write("Publishing Italian pages...")
        from django.utils import timezone as tz

        now = tz.now()
        it_pages = Page.objects.filter(locale=it_locale, depth__gte=2)
        published = 0
        for p in it_pages:
            if not p.live:
                p.live = True
                p.has_unpublished_changes = False
                if not p.first_published_at:
                    p.first_published_at = now
                p.last_published_at = now
                p.save()
                published += 1
        self.stdout.write(f"  Published {published} Italian pages")

        self.stdout.write("Updating Italian page content...")
        updater = UpdateITCommand()
        updater.stdout = self.stdout
        updater.style = self.style
        updater.handle()

    # ------------------------------------------------------------------
    # Override: Categories (English names)
    # ------------------------------------------------------------------

    def _create_categories(self):
        # News categories
        news_cats = [
            ("Club News", "club-news", "#B91C1C",
             "News about club activities and communications"),
            ("Event Recaps", "events-recap", "#059669",
             "Reports and photos from past events"),
            ("Motorcycle World", "motorcycle-world", "#7C3AED",
             "News from the world of motorcycling and the industry"),
            ("Technical", "technical", "#2563EB",
             "Technical articles, reviews and maintenance tips"),
        ]
        self.news_categories = {}
        for name, slug, color, desc in news_cats:
            cat, created = NewsCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "color": color, "description": desc},
            )
            self.news_categories[slug] = cat
            if created:
                self.stdout.write(f"  Created NewsCategory: {name}")

        # Event categories
        event_cats = [
            ("Rally & Gathering", "rally", "rally"),
            ("Touring Ride", "touring", "motorcycle"),
            ("Social Meeting", "social-meeting", "meeting"),
            ("Track Day", "track-day", "race"),
            ("Charity Ride", "charity-ride", "charity"),
        ]
        self.event_categories = {}
        for name, slug, icon in event_cats:
            cat, created = EventCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon},
            )
            self.event_categories[slug] = cat
            if created:
                self.stdout.write(f"  Created EventCategory: {name}")

        # Partner categories
        partner_cats = [
            ("Main Sponsor", "main-sponsor", "", 1),
            ("Technical Partner", "technical-partner", "", 2),
            ("Media Partner", "media-partner", "", 3),
        ]
        self.partner_categories = {}
        for name, slug, icon, order in partner_cats:
            cat, created = PartnerCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "icon": icon, "order": order},
            )
            self.partner_categories[slug] = cat
            if created:
                self.stdout.write(f"  Created PartnerCategory: {name}")

    # ------------------------------------------------------------------
    # Override: Products (English)
    # ------------------------------------------------------------------

    def _create_products(self):
        products = [
            {
                "name": "Standard Membership",
                "slug": "socio-ordinario",
                "description": "Annual membership with voting rights and event participation.",
                "price": Decimal("50.00"),
                "grants_vote": True,
                "grants_events": True,
                "grants_upload": True,
                "order": 1,
            },
            {
                "name": "Supporter Membership",
                "slug": "socio-sostenitore",
                "description": "Supporter membership with event discounts and gallery access.",
                "price": Decimal("30.00"),
                "grants_events": True,
                "grants_discount": True,
                "discount_percent": 10,
                "order": 2,
            },
            {
                "name": "Premium Membership",
                "slug": "socio-premium",
                "description": "Premium membership with all privileges and 20% event discount.",
                "price": Decimal("100.00"),
                "grants_vote": True,
                "grants_events": True,
                "grants_upload": True,
                "grants_discount": True,
                "discount_percent": 20,
                "order": 3,
            },
        ]
        for p in products:
            _, created = Product.objects.get_or_create(
                slug=p["slug"], defaults=p,
            )
            if created:
                self.stdout.write(f"  Created Product: {p['name']}")

    # ------------------------------------------------------------------
    # Override: Testimonials (English)
    # ------------------------------------------------------------------

    def _create_testimonials(self):
        testimonials = [
            {
                "quote": "Joining this club completely changed the way I experience riding. "
                         "The Sunday rides and rallies are truly unforgettable moments.",
                "author_name": "Marco Bianchi",
                "author_role": "Member since 2019",
                "featured": True,
            },
            {
                "quote": "The mutual support among members is extraordinary. "
                         "Once I broke down on the Stelvio pass, and within 30 minutes "
                         "help was already on its way.",
                "author_name": "Giulia Ferrara",
                "author_role": "Member since 2021",
                "featured": True,
            },
            {
                "quote": "The club-organised tours are always flawless: "
                         "breathtaking routes, great food stops and wonderful company.",
                "author_name": "Alessandro Rossi",
                "author_role": "Founding member",
                "featured": False,
            },
        ]
        for t in testimonials:
            _, created = Testimonial.objects.get_or_create(
                author_name=t["author_name"], defaults=t,
            )
            if created:
                self.stdout.write(f"  Created Testimonial: {t['author_name']}")

    # ------------------------------------------------------------------
    # Override: FAQs (English)
    # ------------------------------------------------------------------

    def _create_faqs(self):
        faqs = [
            {
                "question": "How can I join the Moto Club?",
                "answer": (
                    "<p>You can join by completing the online registration form "
                    "on our website, or by visiting the club premises during opening "
                    "hours (Wednesday and Friday 20:30–23:00, Saturday 15:00–18:00). "
                    "A valid photo ID and payment of the membership fee are required.</p>"
                ),
                "category": "Membership",
                "order": 1,
            },
            {
                "question": "How much does a membership card cost?",
                "answer": (
                    "<p>We offer three membership tiers:</p><ul>"
                    "<li><strong>Standard Membership</strong>: €50/year – voting rights, "
                    "events, gallery uploads</li>"
                    "<li><strong>Supporter Membership</strong>: €30/year – events, 10% discount</li>"
                    "<li><strong>Premium Membership</strong>: €100/year – all privileges, "
                    "20% event discount</li></ul>"
                ),
                "category": "Membership",
                "order": 2,
            },
            {
                "question": "Can I participate in events without being a member?",
                "answer": (
                    "<p>Some events are also open to non-members (such as the Ride for "
                    "Children). For most club-organised events a valid membership card is "
                    "required. Non-members may attend as guests for a maximum of 2 outings "
                    "before being required to register.</p>"
                ),
                "category": "Events",
                "order": 3,
            },
            {
                "question": "How does mutual aid work?",
                "answer": (
                    "<p>The mutual aid system allows members to request and offer "
                    "assistance in case of a breakdown or roadside emergency. Each member "
                    "can indicate their skills (mechanics, transport, logistics) and their "
                    "availability radius on their profile. When help is needed the system "
                    "notifies available members in the area.</p>"
                ),
                "category": "Services",
                "order": 4,
            },
        ]
        for f in faqs:
            _, created = FAQ.objects.get_or_create(
                question=f["question"], defaults=f,
            )
            if created:
                self.stdout.write(f"  Created FAQ: {f['question'][:50]}")

    # ------------------------------------------------------------------
    # Override: Press Releases (English)
    # ------------------------------------------------------------------

    def _create_press_releases(self):
        releases = [
            {
                "title": "Moto Club Aquile Rosse announces the 2026 events calendar",
                "date": date(2026, 1, 28),
                "body": (
                    "<p>Moto Club Aquile Rosse ASD of Bergamo has presented the "
                    "official events calendar for the 2026 season, featuring over "
                    "50 appointments including rallies, tours, track days and "
                    "charitable initiatives.</p>"
                    "<p>Highlights include: the Season Opener at Mandello del Lario, "
                    "the Orobie Mountain Tour, the Track Day at Franciacorta Circuit "
                    "and the 12th edition of the Ride for Children in aid of "
                    "Papa Giovanni XXIII Hospital.</p>"
                    "<p>Press contact: press@aquilerosse.it</p>"
                ),
                "is_archived": False,
            },
            {
                "title": "Ride for Children 2025: €8,500 raised for Paediatrics",
                "date": date(2025, 10, 15),
                "body": (
                    "<p>The 11th edition of the Ride for Children — the annual charity "
                    "ride of Moto Club Aquile Rosse — concluded with great success. "
                    "The event drew more than 200 riders and raised €8,500, donated "
                    "entirely to the Paediatrics ward of Papa Giovanni XXIII Hospital "
                    "in Bergamo.</p>"
                    "<p>Since 2014 the Ride for Children has raised a cumulative total "
                    "of over €43,000.</p>"
                ),
                "is_archived": False,
            },
        ]
        for r in releases:
            _, created = PressRelease.objects.get_or_create(
                title=r["title"], defaults=r,
            )
            if created:
                self.stdout.write(f"  Created PressRelease: {r['title'][:50]}")

    # ------------------------------------------------------------------
    # Override: Home Page (English)
    # ------------------------------------------------------------------

    def _create_home_page(self):
        if HomePage.objects.exists():
            self.stdout.write("  HomePage already exists, reusing.")
            return HomePage.objects.first()

        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found!"))
            return None

        default_pages = Page.objects.filter(depth=2, slug="home").exclude(
            content_type__model="homepage"
        )
        if default_pages.exists():
            default_pages.delete()
            Page.fix_tree()
            root = Page.objects.filter(depth=1).first()

        home = HomePage(
            title="Moto Club Aquile Rosse",
            slug="home",
            hero_title="Moto Club Aquile Rosse",
            hero_subtitle="Passion, adventure and brotherhood on two wheels since 1987",
            primary_cta_text="Upcoming Events",
            secondary_cta_text="Become a Member",
            body=json.dumps([
                {
                    "type": "rich_text",
                    "value": "<h2>Welcome to Moto Club Aquile Rosse</h2>"
                             "<p>Since 1987, we have turned a passion for two wheels "
                             "into memorable rides, lasting friendships and initiatives "
                             "that connect the road with a true club spirit.</p>"
                             "<p>With more than 250 active members across Lombardy, we "
                             "organise rallies, scenic tours, track days and charity "
                             "events for riders who want every season to feel alive.</p>",
                },
                {
                    "type": "stats",
                    "value": {
                        "items": [
                            {"number": "250+", "label": "Active Members"},
                            {"number": "37", "label": "Years of History"},
                            {"number": "50+", "label": "Events / Year"},
                            {"number": "12", "label": "National Tours"},
                        ],
                    },
                },
                {
                    "type": "cta",
                    "value": {
                        "title": "Join Us",
                        "text": "Join the club, unlock members-only activities and "
                                "share tours, events and new roads with a community "
                                "that rides all year long.",
                        "button_text": "Explore Memberships",
                        "button_url": "/membership/",
                        "style": "primary",
                    },
                },
            ]),
        )
        root.add_child(instance=home)
        home.save_revision().publish()

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = home
            site.site_name = "Moto Club Aquile Rosse"
            site.save()
        else:
            Site.objects.create(
                hostname="localhost",
                port=8888,
                root_page=home,
                is_default_site=True,
                site_name="Moto Club Aquile Rosse",
            )

        self.stdout.write("  Created HomePage: Moto Club Aquile Rosse")
        return home

    # ------------------------------------------------------------------
    # Override: About Page + Board Page (English)
    # ------------------------------------------------------------------

    def _create_about_page(self, parent):
        if AboutPage.objects.exists():
            self.stdout.write("  AboutPage already exists, reusing.")
            return AboutPage.objects.first()

        about = AboutPage(
            title="About Us",
            slug="chi-siamo",
            intro=(
                "<p>Moto Club Aquile Rosse was founded in 1987 in Bergamo by a group "
                "of passionate motorcyclists who wanted to share their love of two wheels "
                "in a spirit of friendship and solidarity.</p>"
                "<p>Today the club has over 250 registered members, with headquarters "
                "at Via Borgo Palazzo 22, Bergamo. We are affiliated with the FMI "
                "(Italian Motorcycling Federation) and organise more than 50 events each "
                "year including rallies, tours, track days and charity initiatives.</p>"
            ),
            body=json.dumps([
                {
                    "type": "rich_text",
                    "value": "<h2>Our History</h2>"
                             "<p>Founded as a small group of friends meeting every Sunday "
                             "for a ride on the roads around Bergamo, the club has grown "
                             "into one of the most active in Lombardy.</p>"
                             "<h3>Our Values</h3>"
                             "<ul>"
                             "<li><strong>Passion</strong>: Motorcycling is our way of life</li>"
                             "<li><strong>Safety</strong>: Responsible riding and continuous training</li>"
                             "<li><strong>Solidarity</strong>: Mutual aid among members</li>"
                             "<li><strong>Inclusivity</strong>: All makes and models are welcome</li>"
                             "</ul>",
                },
                {
                    "type": "timeline",
                    "value": {
                        "title": "Key Milestones",
                        "items": [
                            {"year": "1987", "title": "Foundation",
                             "description": "12 friends found Moto Club Aquile Rosse in Bergamo."},
                            {"year": "1995", "title": "FMI Affiliation",
                             "description": "The club affiliates with the Italian Motorcycling Federation."},
                            {"year": "2005", "title": "New Headquarters",
                             "description": "The new club premises at Via Borgo Palazzo are inaugurated."},
                            {"year": "2015", "title": "250 Members",
                             "description": "The club reaches the milestone of 250 active members."},
                            {"year": "2024", "title": "Federation",
                             "description": "Launch of the federation programme with partner clubs across Italy."},
                        ],
                    },
                },
            ]),
        )
        parent.add_child(instance=about)
        about.save_revision().publish()
        self.stdout.write("  Created AboutPage: About Us")
        return about

    def _create_board_page(self, parent):
        if BoardPage.objects.exists():
            self.stdout.write("  BoardPage already exists, skipping.")
            return

        board = BoardPage(
            title="Board of Directors",
            slug="consiglio-direttivo",
            intro="<p>The Board of Directors leads the club with passion and dedication.</p>",
            body=json.dumps([
                {
                    "type": "team_grid",
                    "value": {
                        "columns": 3,
                        "members": [
                            {"name": "Roberto Colombo", "role": "President",
                             "bio": "Motorcyclist for 40 years, leading the club since 2015. "
                                    "Passionate about motorcycles and long-distance touring."},
                            {"name": "Francesca Moretti", "role": "Vice President",
                             "bio": "Mechanical engineer and safe-riding instructor. "
                                    "Organises the club's training courses."},
                            {"name": "Luca Bernardi", "role": "Secretary",
                             "bio": "Manages memberships, communications and "
                                    "the club website."},
                            {"name": "Chiara Fontana", "role": "Treasurer",
                             "bio": "Accountant by profession, has kept the club's "
                                    "finances in order since 2020."},
                            {"name": "Davide Marchetti", "role": "Events Manager",
                             "bio": "Plans and organises all club events. "
                                    "Specialist in logistics and route planning."},
                            {"name": "Elena Rizzo", "role": "Communications Manager",
                             "bio": "Journalist and social media manager. Handles the "
                                    "newsletter and social media channels."},
                        ],
                    },
                },
            ]),
        )
        parent.add_child(instance=board)
        board.save_revision().publish()
        self.stdout.write("  Created BoardPage: Board of Directors")

    # ------------------------------------------------------------------
    # Override: News Index + Articles (English)
    # ------------------------------------------------------------------

    def _create_news_index(self, parent):
        if NewsIndexPage.objects.exists():
            self.stdout.write("  NewsIndexPage already exists, reusing.")
            return NewsIndexPage.objects.first()

        news_index = NewsIndexPage(
            title="News",
            slug="news",
            intro="<p>All the latest from Moto Club Aquile Rosse.</p>",
        )
        parent.add_child(instance=news_index)
        news_index.save_revision().publish()
        self.stdout.write("  Created NewsIndexPage")
        return news_index

    def _create_news_articles(self, parent):
        if NewsPage.objects.exists():
            self.stdout.write("  NewsPages already exist, skipping.")
            return

        today = date.today()
        articles = [
            {
                "title": "Season Opener 2026: Back to Mandello!",
                "slug": "avviamento-motori-2026",
                "intro": "The traditional season-opening rally returns to Mandello del Lario "
                         "with surprises in store for all motorcycle enthusiasts.",
                "display_date": today - timedelta(days=3),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>As every year, the riding season kicks off with the "
                                 "traditional <strong>Season Opener</strong> at Mandello del "
                                 "Lario, the birthplace of Moto moto.</p>"
                                 "<p>The event, organised by Moto Club Le Aquile di Mandello "
                                 "in collaboration with moto Days, features a packed programme: "
                                 "from the lakeside parade to guided tours of the Moto moto "
                                 "Museum, culminating in a club dinner at Ristorante Il Griso.</p>"
                                 "<h3>Programme</h3>"
                                 "<ul>"
                                 "<li>09:00 – Meet at Piazza Garibaldi</li>"
                                 "<li>10:30 – Parade along Lake Como</li>"
                                 "<li>12:30 – Club lunch</li>"
                                 "<li>15:00 – Motorcycle museum visit</li>"
                                 "<li>18:00 – Aperitif and prize-giving</li>"
                                 "</ul>"
                                 "<p>Moto Club Aquile Rosse will attend with a delegation of "
                                 "30 members. Registrations are open until 15 March.</p>",
                    },
                ]),
            },
            {
                "title": "1st Moto Lands of Pisa: New Event in Tuscany",
                "slug": "moto-lands-pisa",
                "intro": "A new motorcycle rally is born at Pontedera, in the land of Piaggio "
                         "and just a stone's throw from the Leaning Tower.",
                "display_date": today - timedelta(days=7),
                "category": "motorcycle-world",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Exciting news from the Italian rally scene: the "
                                 "<strong>1st Moto moto Lands of Pisa</strong> has been "
                                 "announced, an event to be held at Pontedera (PI) in spring "
                                 "2026.</p>"
                                 "<p>Organised by Moto Club Terre di Pisa in collaboration "
                                 "it promises a weekend steeped "
                                 "in Tuscan motorcycling culture: guided rides through the "
                                 "Pisan hills, tastings of local produce and a static display "
                                 "in the historic town centre.</p>"
                                 "<p>Our club is already planning a group trip. Interested "
                                 "members should contact events manager Davide Marchetti.</p>",
                    },
                ]),
            },
            {
                "title": "Recap: Spring Franken Bayern Treffen 2026",
                "slug": "spring-franken-bayern-treffen",
                "intro": "Eight club members took part in the spring rally in Bavaria. "
                         "Here is the story of their adventure.",
                "display_date": today - timedelta(days=14),
                "category": "events-recap",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Last weekend a group of 8 members from Moto Club "
                                 "Aquile Rosse crossed the Alps to attend the "
                                 "<strong>Spring Franken Bayern Treffen</strong>, the spring "
                                 "rally that marks the start of the season in the German "
                                 "region of Franconia.</p>"
                                 "<p>The outbound route passed through the Brenner Pass, "
                                 "Innsbruck and Munich before reaching the Nuremberg area. "
                                 "The rally, attended by over 500 riders from across Europe, "
                                 "offered days of riding on the magnificent roads of Franconia, "
                                 "Bavarian beer and a wonderful spirit of camaraderie.</p>"
                                 "<p>Next international trip: moto Days 2026 in South Africa!</p>",
                    },
                ]),
            },
            {
                "title": "New Agreement with Officina Moto Bergamo",
                "slug": "convenzione-officina-moto-bergamo",
                "intro": "A new partnership agreement with Officina Moto Bergamo provides "
                         "discounts on servicing and repairs for all members.",
                "display_date": today - timedelta(days=20),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>We are pleased to announce a new partnership with "
                                 "<strong>Officina Moto Bergamo</strong>, a multi-brand "
                                 "service centre located at Via Seriate 42.</p>"
                                 "<p>All Moto Club Aquile Rosse members will be entitled "
                                 "to the following discounts:</p>"
                                 "<ul>"
                                 "<li>15% off routine servicing and maintenance</li>"
                                 "<li>10% off genuine and aftermarket spare parts</li>"
                                 "<li>Free electronic diagnostics</li>"
                                 "<li>Priority booking during peak season</li>"
                                 "</ul>"
                                 "<p>Simply present a valid membership card to access "
                                 "the benefits.</p>",
                    },
                ]),
            },
            {
                "title": "Getting Your Bike Ready for the Season",
                "slug": "preparazione-moto-stagione",
                "intro": "Our trusted mechanic's tips for bringing your motorcycle back "
                         "to peak condition after the winter break.",
                "display_date": today - timedelta(days=30),
                "category": "technical",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>With the warmer months approaching it's time to "
                                 "prepare your bike for the first rides. Here is an "
                                 "essential checklist prepared with our technical partner "
                                 "Officina Moto Bergamo.</p>"
                                 "<h3>Essential Checks</h3>"
                                 "<ol>"
                                 "<li><strong>Battery</strong>: Check the charge and "
                                 "electrolyte levels. If the bike has been stored for "
                                 "more than 3 months, consider replacement.</li>"
                                 "<li><strong>Tyres</strong>: Check pressure, tread depth "
                                 "and the DOT date. Tyres older than 5 years should be "
                                 "replaced.</li>"
                                 "<li><strong>Brakes</strong>: Check pad thickness and "
                                 "brake fluid level.</li>"
                                 "<li><strong>Engine oil</strong>: Change oil and filter "
                                 "if not done before winter storage.</li>"
                                 "<li><strong>Chain</strong>: Clean, lubricate and check "
                                 "tension.</li>"
                                 "<li><strong>Lights</strong>: Test all lights including "
                                 "indicators and number-plate light.</li>"
                                 "</ol>",
                    },
                ]),
            },
            {
                "title": "2026 Annual General Meeting: Accounts Approved",
                "slug": "assemblea-soci-2026",
                "intro": "The annual general meeting unanimously approved the financial "
                         "statements and the events programme for the coming year.",
                "display_date": today - timedelta(days=45),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Last Saturday the annual general meeting of Moto Club "
                                 "Aquile Rosse was held at the club premises.</p>"
                                 "<p>With 142 of the 258 eligible members present, the AGM "
                                 "unanimously approved the 2025 financial statements and the "
                                 "2026 budget.</p>"
                                 "<h3>Key Points</h3>"
                                 "<ul>"
                                 "<li>Existing board confirmed for the 2026–2027 term</li>"
                                 "<li>Events calendar approved with 52 scheduled outings</li>"
                                 "<li>New partnerships agreed with 3 affiliated workshops</li>"
                                 "<li>Launch of the federation programme with other clubs</li>"
                                 "<li>Purchase of a defibrillator for the clubhouse</li>"
                                 "</ul>",
                    },
                ]),
            },
        ]

        for article in articles:
            cat_slug = article.pop("category")
            news = NewsPage(
                category=self.news_categories.get(cat_slug),
                **article,
            )
            parent.add_child(instance=news)
            news.save_revision().publish()
            self.stdout.write(f"  Created NewsPage: {article['title']}")

    # ------------------------------------------------------------------
    # Override: Events Page + Event Detail Pages (English)
    # ------------------------------------------------------------------

    def _create_events_page(self, parent):
        if EventsPage.objects.exists():
            self.stdout.write("  EventsPage already exists, reusing.")
            return EventsPage.objects.first()

        events = EventsPage(
            title="Events",
            slug="eventi",
            intro="<p>All events organised and supported by Moto Club Aquile Rosse.</p>",
        )
        parent.add_child(instance=events)
        events.save_revision().publish()
        self.stdout.write("  Created EventsPage")
        return events

    def _create_events(self, parent):
        if EventDetailPage.objects.exists():
            self.stdout.write("  EventDetailPages already exist, skipping.")
            return

        now = timezone.now()
        events = [
            {
                "title": "Season Opener 2026 - Mandello del Lario",
                "slug": "avviamento-motori-mandello-2026",
                "intro": "The traditional season-opening rally in Mandello del Lario.",
                "start_date": now + timedelta(days=30),
                "end_date": now + timedelta(days=31),
                "location_name": "Piazza Garibaldi, Mandello del Lario",
                "location_address": "Piazza Garibaldi, 23826 Mandello del Lario LC",
                "location_coordinates": "45.9167,9.3167",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 200,
                "base_fee": Decimal("25.00"),
                "early_bird_discount": 20,
                "early_bird_deadline": now + timedelta(days=15),
                "member_discount_percent": 10,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Join us for the <strong>Season Opener 2026</strong>, "
                             "the rally that officially marks the start of the riding season "
                             "on the shores of Lake Como.</p>"
                             "<p>Organised by Moto Club Le Aquile di Mandello in collaboration "
                             "the event is open to all makes "
                             "and models.</p>"
                             "<h3>What's Included</h3>"
                             "<ul>"
                             "<li>Scenic parade along Lake Como</li>"
                             "<li>Club lunch (included in the fee)</li>"
                             "<li>Moto moto Museum visit</li>"
                             "<li>Commemorative gift</li>"
                             "</ul>",
                }]),
            },
            {
                "title": "1st Moto moto Lands of Pisa",
                "slug": "moto-lands-pisa-2026",
                "intro": "First moto rally in the land of Pontedera, among the Tuscan hills.",
                "start_date": now + timedelta(days=60),
                "end_date": now + timedelta(days=62),
                "location_name": "Historic Centre, Pontedera",
                "location_address": "Piazza Martiri della Libertà, 56025 Pontedera PI",
                "location_coordinates": "43.6631,10.6322",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 300,
                "base_fee": Decimal("40.00"),
                "early_bird_discount": 15,
                "early_bird_deadline": now + timedelta(days=45),
                "member_discount_percent": 10,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>A weekend in beautiful Tuscany for the first "
                             "<strong>Moto moto Lands of Pisa</strong>.</p>"
                             "<p>The programme includes guided tours through the Pisan hills, "
                             "a visit to the Piaggio Museum in Pontedera, tastings of local "
                             "produce and a static display in the town square featuring "
                             "both vintage and modern motorcycles.</p>",
                }]),
            },
            {
                "title": "Orobie Mountain Tour - Club Day Out",
                "slug": "tour-orobie-2026",
                "intro": "A day ride through the Bergamo valleys with a mountain-hut lunch stop.",
                "start_date": now + timedelta(days=14),
                "end_date": now + timedelta(days=14, hours=10),
                "location_name": "Club Headquarters, Bergamo",
                "location_address": "Via Borgo Palazzo 22, 24121 Bergamo",
                "location_coordinates": "45.6983,9.6773",
                "category": "touring",
                "registration_open": True,
                "max_attendees": 40,
                "base_fee": Decimal("15.00"),
                "member_discount_percent": 100,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>A club day out in the magnificent <strong>Orobie Alps</strong>, "
                             "covering approximately 180 km through the Bergamo valleys.</p>"
                             "<p>Departure from the clubhouse at 08:30. Route: Bergamo → Val Seriana "
                             "→ Passo della Presolana → Val di Scalve → Lake Iseo → Bergamo. "
                             "Lunch stop at Rifugio Albani.</p>"
                             "<p><em>Free for members with a valid membership card.</em></p>",
                }]),
            },
            {
                "title": "Track Day - Franciacorta Circuit",
                "slug": "track-day-franciacorta-2026",
                "intro": "A full day on track at Franciacorta Circuit with professional instructors.",
                "start_date": now + timedelta(days=45),
                "end_date": now + timedelta(days=45, hours=10),
                "location_name": "Autodromo di Franciacorta",
                "location_address": "Via Trento 9, 25040 Castrezzato BS",
                "location_coordinates": "45.4683,9.9900",
                "category": "track-day",
                "registration_open": True,
                "max_attendees": 30,
                "base_fee": Decimal("120.00"),
                "early_bird_discount": 10,
                "early_bird_deadline": now + timedelta(days=30),
                "member_discount_percent": 15,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>A day dedicated to safe sporting riding at "
                             "<strong>Franciacorta Circuit</strong>.</p>"
                             "<p>The programme includes:</p>"
                             "<ul>"
                             "<li>Technical and safety briefing</li>"
                             "<li>3 track sessions of 20 minutes each</li>"
                             "<li>Personalised coaching from former CIV instructors</li>"
                             "<li>Lunch at the circuit</li>"
                             "<li>Telemetry analysis (optional)</li>"
                             "</ul>"
                             "<p>Mandatory equipment: full leather suit, gloves, "
                             "technical boots, full-face helmet.</p>",
                }]),
            },
            {
                "title": "Charity: Ride for Children",
                "slug": "ride-for-children-2026",
                "intro": "Charity motorcycle ride in aid of Bergamo Children's Hospital.",
                "start_date": now + timedelta(days=75),
                "end_date": now + timedelta(days=75, hours=9),
                "location_name": "Piazza Vecchia, Bergamo Alta",
                "location_address": "Piazza Vecchia, 24129 Bergamo",
                "location_coordinates": "45.7037,9.6623",
                "category": "charity-ride",
                "registration_open": True,
                "max_attendees": 0,  # unlimited
                "base_fee": Decimal("20.00"),
                "member_discount_percent": 0,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>The <strong>Ride for Children</strong> is the annual charity "
                             "event of Moto Club Aquile Rosse, now in its 12th edition.</p>"
                             "<p>All registration proceeds will be donated to the Paediatrics "
                             "ward of Papa Giovanni XXIII Hospital in Bergamo for the purchase "
                             "of medical equipment.</p>"
                             "<p>In previous editions we have raised over €35,000 thanks to "
                             "the generosity of hundreds of riders.</p>"
                             "<p><strong>Open to everyone — members and non-members alike!</strong></p>",
                }]),
            },
            {
                "title": "Moto Rally Garda 2026",
                "slug": "moto-rally-garda-2026",
                "intro": "Motorcycle rally on Lake Garda with parade and live music.",
                "start_date": now + timedelta(days=90),
                "end_date": now + timedelta(days=93),
                "location_name": "Lungolago di Desenzano del Garda",
                "location_address": "Lungolago Cesare Battisti, 25015 Desenzano del Garda BS",
                "location_coordinates": "45.4710,10.5379",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 500,
                "base_fee": Decimal("60.00"),
                "early_bird_discount": 15,
                "early_bird_deadline": now + timedelta(days=60),
                "member_discount_percent": 5,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>The <strong>Moto Rally Garda</strong> is one of the largest "
                             "motorcycle gatherings in northern Italy, organised by "
                             "Moto Club Lago di Garda in collaboration with the local dealership.</p>"
                             "<p>Four days of bikes, music, food trucks and the famous "
                             "Thunder Parade along the lakeshore. Our club participates "
                             "as a guest with an information stand.</p>",
                }]),
            },
        ]

        for event in events:
            cat_slug = event.pop("category")
            ev = EventDetailPage(
                category=self.event_categories.get(cat_slug),
                registration_deadline=event.get("early_bird_deadline"),
                **event,
            )
            parent.add_child(instance=ev)
            ev.save_revision().publish()
            self.stdout.write(f"  Created EventDetailPage: {event['title']}")

    # ------------------------------------------------------------------
    # Override: Gallery Page (English)
    # ------------------------------------------------------------------

    def _create_gallery_page(self, parent):
        if GalleryPage.objects.exists():
            self.stdout.write("  GalleryPage already exists, skipping.")
            return

        gallery = GalleryPage(
            title="Gallery",
            slug="galleria",
            intro="<p>The best photos from our events, tours and rallies.</p>",
        )
        parent.add_child(instance=gallery)
        gallery.save_revision().publish()
        self.stdout.write("  Created GalleryPage")

    # ------------------------------------------------------------------
    # Override: Contact Page (English)
    # ------------------------------------------------------------------

    def _create_contact_page(self, parent):
        if ContactPage.objects.exists():
            self.stdout.write("  ContactPage already exists, skipping.")
            return

        contact = ContactPage(
            title="Contact",
            slug="contatti",
            # Hero section
            hero_badge="We're here for you",
            # Content
            intro="<p>Have questions? Want to know more about the club? Get in touch!</p>",
            form_title="Send Us a Message",
            success_message="<p>Thank you for your message! We will reply within 48 hours.</p>",
            captcha_enabled=True,
            captcha_provider="honeypot",
            # Membership CTA
            membership_title="Become a Member",
            membership_description=(
                "Join our community of over 250 motorcyclists. "
                "Access to all events, partner discounts, "
                "insurance and roadside assistance included."
            ),
            membership_price="Annual fee €80",
            membership_cta_text="Join Now",
            # membership_cta_url left blank - set via admin with actual page URL
        )
        parent.add_child(instance=contact)
        contact.save_revision().publish()
        self.stdout.write("  Created ContactPage")

    # ------------------------------------------------------------------
    # Override: Privacy, Transparency, Press Pages (English)
    # ------------------------------------------------------------------

    def _create_privacy_page(self, parent):
        if PrivacyPage.objects.exists():
            self.stdout.write("  PrivacyPage already exists, skipping.")
            return

        privacy = PrivacyPage(
            title="Privacy Policy",
            slug="privacy",
            last_updated=date.today(),
            body=json.dumps([{
                "type": "rich_text",
                "value": "<h2>Privacy Notice</h2>"
                         "<p>Pursuant to Regulation (EU) 2016/679 (GDPR), "
                         "Moto Club Aquile Rosse ASD, acting as Data Controller, "
                         "informs you that personal data collected through this website "
                         "will be processed in accordance with applicable legislation.</p>"
                         "<h3>Data Collected</h3>"
                         "<p>Data collected includes: first name, last name, email address, "
                         "telephone number (optional) and browsing data.</p>"
                         "<h3>Purposes of Processing</h3>"
                         "<ul>"
                         "<li>Managing club memberships</li>"
                         "<li>Organising events and communications</li>"
                         "<li>Legal compliance</li>"
                         "</ul>"
                         "<h3>Your Rights</h3>"
                         "<p>You may exercise your rights of access, rectification, "
                         "erasure and portability by writing to "
                         "privacy@aquilerosse.it.</p>",
            }]),
        )
        parent.add_child(instance=privacy)
        privacy.save_revision().publish()
        self.stdout.write("  Created PrivacyPage")

    def _create_transparency_page(self, parent):
        if TransparencyPage.objects.exists():
            self.stdout.write("  TransparencyPage already exists, skipping.")
            return

        transparency = TransparencyPage(
            title="Transparency",
            slug="trasparenza",
            intro="<p>In compliance with regulations governing amateur sports associations, "
                  "we publish the club's official documents.</p>",
            body=json.dumps([{
                "type": "rich_text",
                "value": "<h2>Club Documents</h2>"
                         "<p>The articles of association, financial statements and AGM "
                         "minutes are available for inspection by members and "
                         "supervisory bodies.</p>"
                         "<h3>Articles of Association</h3>"
                         "<p>The Articles of Association of Moto Club Aquile Rosse ASD "
                         "were approved at the founding meeting on 15 March 1987 "
                         "and last updated on 20 January 2024.</p>"
                         "<h3>Financial Statements</h3>"
                         "<ul>"
                         "<li>2025 Annual Accounts – Approved 25/01/2026</li>"
                         "<li>2024 Annual Accounts – Approved 28/01/2025</li>"
                         "</ul>",
            }]),
        )
        parent.add_child(instance=transparency)
        transparency.save_revision().publish()
        self.stdout.write("  Created TransparencyPage")

    def _create_press_page(self, parent):
        if PressPage.objects.exists():
            self.stdout.write("  PressPage already exists, skipping.")
            return

        press = PressPage(
            title="Press Room",
            slug="stampa",
            intro="<p>Press materials and media contacts.</p>",
            press_email="press@aquilerosse.it",
            press_phone="+39 035 123 4568",
            press_contact="Elena Rizzo - Communications Manager",
            body=json.dumps([{
                "type": "rich_text",
                "value": "<p>For press enquiries, interviews or photographic material "
                         "please contact the club communications office.</p>",
            }]),
        )
        parent.add_child(instance=press)
        press.save_revision().publish()
        self.stdout.write("  Created PressPage")

    def _create_membership_plans_page(self, parent):
        if MembershipPlansPage.objects.exists():
            self.stdout.write("  MembershipPlansPage already exists, skipping.")
            return
        page = MembershipPlansPage(
            title="Become a Member",
            slug="diventa-socio",
            intro="<p>Choose the membership plan that best suits your needs. "
                  "Combine multiple products to tailor your experience.</p>",
        )
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write("  Created MembershipPlansPage")

    # ------------------------------------------------------------------
    # Override: Federation Info Page (English)
    # ------------------------------------------------------------------

    def _create_federation_info_page(self, parent):
        if FederationInfoPage.objects.exists():
            self.stdout.write("  FederationInfoPage already exists, skipping.")
            return FederationInfoPage.objects.first()

        how_it_works = json.dumps([{
            "type": "step",
            "value": {
                "title": "How the Federation Works",
                "items": [
                    {"year": "1", "title": "Discover partner clubs",
                     "description": "<p>Browse the list of federated clubs and find out "
                                    "about their activities, history and the services "
                                    "they offer their members.</p>"},
                    {"year": "2", "title": "Explore shared events",
                     "description": "<p>Browse events published by partner clubs. "
                                    "You can filter by club, search by name and see "
                                    "all the details.</p>"},
                    {"year": "3", "title": "Express your interest",
                     "description": "<p>Indicate whether you are interested, undecided "
                                    "or definitely attending. The organising club only "
                                    "receives anonymous aggregate counts.</p>"},
                    {"year": "4", "title": "Discuss with fellow members",
                     "description": "<p>Talk about events with other members of your "
                                    "club. Comments are private and are never shared "
                                    "with the partner club.</p>"},
                ],
            },
        }])

        faq = json.dumps([{
            "type": "faq",
            "value": {
                "title": "Frequently Asked Questions about the Federation",
                "items": [
                    {"question": "What is the club federation?",
                     "answer": "<p>It is a voluntary network of clubs that share events "
                               "and initiatives through a secure protocol. "
                               "Every club retains full autonomy.</p>"},
                    {"question": "Do I need to pay to access federated events?",
                     "answer": "<p>No. Access to the partner events list is included "
                               "in your membership. Registering for a partner event "
                               "follows the rules of the organising club.</p>"},
                    {"question": "Is my personal data shared?",
                     "answer": "<p>No. The federation exchanges only event data "
                               "and anonymous aggregate counts. No personal data "
                               "is ever transmitted to partner clubs.</p>"},
                    {"question": "How is security guaranteed?",
                     "answer": "<p>Each partner club has unique API keys. "
                               "All communications use HTTPS with HMAC authentication. "
                               "Data is validated and sanitised before import.</p>"},
                    {"question": "Can I attend events at a partner club?",
                     "answer": "<p>You can express interest from our platform. "
                               "For actual registration, follow the instructions "
                               "on the organising club's website via the link on "
                               "the event page.</p>"},
                    {"question": "Are comments visible to partner clubs?",
                     "answer": "<p>No. Comments on partner events are visible only "
                               "to members of our own club. They are a tool for "
                               "internal discussion.</p>"},
                ],
            },
        }])

        body = json.dumps([{
            "type": "rich_text",
            "value": (
                "<h2>Benefits of the Federation</h2>"
                "<p>Being part of a federated network of clubs means more "
                "opportunities for members without losing autonomy:</p>"
                "<ul>"
                "<li><strong>More events</strong> — Access a shared calendar "
                "with dozens of appointments from partner clubs.</li>"
                "<li><strong>New friendships</strong> — Meet enthusiasts from "
                "other clubs who share your interests.</li>"
                "<li><strong>Privacy guaranteed</strong> — Your personal data "
                "stays within our club.</li>"
                "<li><strong>Private discussion</strong> — Comment and organise "
                "with your club's members in complete privacy.</li>"
                "</ul>"
                "<p>The federation is an open project: any club can join by "
                "following the technical protocol and the principles of "
                "transparency and privacy.</p>"
            ),
        }])

        with override("en"):
            federation_events_url = reverse("federation_frontend:list")

        page = FederationInfoPage(
            title="Federation",
            slug="federazione",
            intro=(
                "<p>Our network of partner clubs shares events, initiatives "
                "and opportunities for all members. Through the federation you can "
                "discover what is happening in friendly clubs, explore their events "
                "and take part in network initiatives — all from your club's "
                "platform, in complete security.</p>"
            ),
            how_it_works=how_it_works,
            faq=faq,
            body=body,
            cta_text="Explore partner events",
            cta_url=federation_events_url,
        )
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write("  Created FederationInfoPage")
        return page

    # ------------------------------------------------------------------
    # Override: Partner Index + Partners (English)
    # ------------------------------------------------------------------

    def _create_partner_index(self, parent):
        if PartnerIndexPage.objects.exists():
            self.stdout.write("  PartnerIndexPage already exists, reusing.")
            return PartnerIndexPage.objects.first()

        partners = PartnerIndexPage(
            title="Partners",
            slug="partner",
            intro="<p>The partners and sponsors who support the activities of our club.</p>",
        )
        parent.add_child(instance=partners)
        partners.save_revision().publish()
        self.stdout.write("  Created PartnerIndexPage")
        return partners

    def _create_partners(self, parent):
        if PartnerPage.objects.exists():
            self.stdout.write("  PartnerPages already exist, skipping.")
            return

        partners = [
            {
                "title": "Officina Moto Bergamo",
                "slug": "officina-moto-bergamo",
                "intro": "Multi-brand service centre and official technical partner of the club.",
                "category": "technical-partner",
                "website": "https://www.example.com/officina-moto-bg",
                "email": "info@officinamotobg.it",
                "phone": "+39 035 987 6543",
                "address": "Via Seriate 42\n24124 Bergamo",
                "contact_city": "Bergamo",
                "latitude": 45.6950,
                "longitude": 9.6700,
                "is_featured": True,
                "show_on_homepage": True,
                "partnership_start": date(2023, 1, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Officina Moto Bergamo is the official technical partner "
                             "of Moto Club Aquile Rosse. It offers full-service support "
                             "on all makes with certified staff.</p>"
                             "<p>Exclusive discounts for club members on servicing, "
                             "repairs and spare parts.</p>",
                }]),
            },
            {
                "title": "Concessionaria Moto Lecco",
                "slug": "concessionaria-lecco",
                "intro": "Official motorcycle dealership and main sponsor of the club.",
                "category": "main-sponsor",
                "website": "https://www.example.com/concessionaria-lecco",
                "email": "info@motorlecco.it",
                "phone": "+39 0341 123 456",
                "address": "Corso Matteotti 15\n23900 Lecco",
                "contact_city": "Lecco",
                "latitude": 45.8566,
                "longitude": 9.3977,
                "is_featured": True,
                "show_on_homepage": True,
                "partnership_start": date(2020, 6, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Official Moto moto dealership for the province of Lecco. "
                             "Main club sponsor since 2020, supporting our events with "
                             "demo rides and technical assistance.</p>",
                }]),
            },
            {
                "title": "Bergamo Moto Magazine",
                "slug": "bergamo-moto-magazine",
                "intro": "Online magazine dedicated to motorcycling in Bergamo and Lombardy.",
                "category": "media-partner",
                "website": "https://www.example.com/bg-moto-mag",
                "email": "editorial@bgmotomag.it",
                "contact_city": "Bergamo",
                "is_featured": False,
                "show_on_homepage": True,
                "partnership_start": date(2022, 3, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Bergamo Moto Magazine is our media partner: it covers all "
                             "club events with articles, photos and videos across "
                             "its channels.</p>",
                }]),
            },
        ]

        for p in partners:
            cat_slug = p.pop("category")
            partner = PartnerPage(
                category=self.partner_categories.get(cat_slug),
                **p,
            )
            parent.add_child(instance=partner)
            partner.save_revision().publish()
            self.stdout.write(f"  Created PartnerPage: {p['title']}")

    # ------------------------------------------------------------------
    # Override: Navbar (English labels)
    # ------------------------------------------------------------------

    def _create_navbar(self, home, about, news, events):
        if Navbar.objects.exists():
            self.stdout.write("  Navbar already exists, skipping.")
            return Navbar.objects.first()

        navbar = Navbar.objects.create(
            name="Main Navigation",
            show_search=True,
        )

        with override("en"):
            member_card_url = reverse("account:card")
            aid_map_url = reverse("mutual_aid:map")
            contributions_url = reverse("account:my_contributions")
            notifications_url = reverse("account:notifications")

        # NOTE: no "Home" item — the logo/brand already links to home
        top_items = [
            ("About Us", about),
            ("News", news),
            ("Events", events),
        ]

        gallery = GalleryPage.objects.first()
        if gallery:
            top_items.append(("Gallery", gallery))

        # "Services" is a top-level dropdown without its own page
        top_items.append(("Services", None))

        # Create top-level items
        nav_items = {}
        for i, (label, page) in enumerate(top_items):
            item = NavbarItem.objects.create(
                navbar=navbar,
                sort_order=i,
                label=label,
                link_page=page,
                is_cta=False,
            )
            nav_items[label] = item

        # Sub-items under "About Us" — institutional pages for members
        if "About Us" in nav_items:
            about_us = nav_items["About Us"]
            sub_items = [
                ("History", about, ""),
                ("Contact", ContactPage.objects.first(), ""),
                ("Become a Member", MembershipPlansPage.objects.first(), ""),
                ("Board of Directors", BoardPage.objects.first(), ""),
                ("Transparency", TransparencyPage.objects.first(), ""),
                ("Member Card", None, member_card_url),
                ("Partners", PartnerIndexPage.objects.first(), ""),
            ]
            for i, (label, page, url) in enumerate(sub_items):
                if page or url:
                    NavbarItem.objects.create(
                        navbar=navbar,
                        parent=about_us,
                        sort_order=i,
                        label=label,
                        link_page=page,
                        link_url=url,
                        is_cta=False,
                    )

        # Sub-items under "Services" — club services
        if "Services" in nav_items:
            services = nav_items["Services"]
            federation_page = FederationInfoPage.objects.first()
            service_items = [
                ("Roadside Assistance", None, aid_map_url),
                ("Federation Events", federation_page, ""),
                ("Contributions", None, contributions_url),
                ("Notifications", None, notifications_url),
                ("Press Room", PressPage.objects.first(), ""),
            ]
            for i, (label, page, url) in enumerate(service_items):
                if page or url:
                    NavbarItem.objects.create(
                        navbar=navbar,
                        parent=services,
                        sort_order=i,
                        label=label,
                        link_page=page,
                        link_url=url,
                        is_cta=False,
                    )

        self.stdout.write("  Created Navbar with menu items")
        return navbar

    # ------------------------------------------------------------------
    # Override: Footer (English)
    # ------------------------------------------------------------------

    def _create_footer(self, home, about, news, events):
        if Footer.objects.exists():
            self.stdout.write("  Footer already exists, skipping.")
            return Footer.objects.first()

        footer = Footer.objects.create(
            name="Main Footer",
            description="<p>Moto Club Aquile Rosse ASD - "
                        "Passion, adventure and brotherhood on two wheels since 1987.</p>",
            copyright_text="© 2026 Moto Club Aquile Rosse ASD. All rights reserved.",
            phone="+39 035 123 4567",
            email="info@aquilerosse.it",
            address="Via Borgo Palazzo 22\n24121 Bergamo (BG)\nItaly",
        )

        # Menu items
        pages = [
            ("About Us", about),
            ("News", news),
            ("Events", events),
        ]
        privacy = PrivacyPage.objects.first()
        if privacy:
            pages.append(("Privacy", privacy))
        transparency = TransparencyPage.objects.first()
        if transparency:
            pages.append(("Transparency", transparency))

        for i, (label, page) in enumerate(pages):
            FooterMenuItem.objects.create(
                footer=footer,
                sort_order=i,
                label=label,
                link_page=page,
            )

        # Social links
        social = [
            ("facebook", "https://www.facebook.com/motoclubaquilerosse"),
            ("instagram", "https://www.instagram.com/aquilerosse_mc"),
            ("youtube", "https://www.youtube.com/@aquilerossemc"),
        ]
        for i, (platform, url) in enumerate(social):
            FooterSocialLink.objects.create(
                footer=footer,
                sort_order=i,
                platform=platform,
                url=url,
            )

        self.stdout.write("  Created Footer with menu items and social links")
        return footer

    # ------------------------------------------------------------------
    # Override: Aid Requests (English descriptions)
    # ------------------------------------------------------------------

    def _create_aid_requests(self, members):
        """Create sample mutual aid requests."""
        self.stdout.write("\nCreating aid requests...")

        if AidRequest.objects.filter(requester_name__startswith="Demo:").exists():
            self.stdout.write("  Aid requests already exist, skipping.")
            return

        if len(members) < 5:
            self.stdout.write(
                self.style.WARNING("  Not enough members to create aid requests.")
            )
            return

        marco, giulia, alessandro, chiara, roberto = members[:5]
        now = timezone.now()

        requests_data = [
            {
                "helper": alessandro,
                "requester_name": "Demo: Marco Bianchi",
                "requester_phone": "+39 333 111 2222",
                "requester_email": "marco.bianchi@example.com",
                "requester_user": marco,
                "issue_type": "breakdown",
                "description": (
                    "Motorcycle broken down on the SS38 between Lecco and Colico, km 42. "
                    "The bike won't start — looks like an electrical fault. "
                    "I'm in the car park of Ristorante La Pergola."
                ),
                "location": "SS38, Km 42 - Dervio (LC)",
                "urgency": "high",
                "status": "resolved",
            },
            {
                "helper": giulia,
                "requester_name": "Demo: Chiara Fontana",
                "requester_phone": "+39 333 444 5555",
                "requester_email": "chiara.fontana@example.com",
                "requester_user": chiara,
                "issue_type": "flat_tire",
                "description": (
                    "Rear tyre puncture on my motorcycle on the Passo della Presolana road. "
                    "I don't have a tubeless repair kit. "
                    "I'm at Rifugio Magnolini."
                ),
                "location": "Passo della Presolana - Rifugio Magnolini (BG)",
                "urgency": "medium",
                "status": "resolved",
            },
            {
                "helper": roberto,
                "requester_name": "Demo: Giulia Ferrara",
                "requester_phone": "+39 333 222 3333",
                "requester_email": "giulia.ferrara@example.com",
                "requester_user": giulia,
                "issue_type": "fuel",
                "description": (
                    "Run out of fuel on the SP671 between Clusone and Bergamo. "
                    "The nearest petrol station was closed (Sunday evening). "
                    "I'm at Bar Sport in Gazzaniga."
                ),
                "location": "SP671, Gazzaniga (BG)",
                "urgency": "low",
                "status": "resolved",
            },
            {
                "helper": alessandro,
                "requester_name": "Demo: Roberto Colombo",
                "requester_phone": "+39 333 555 6666",
                "requester_email": "roberto.colombo@example.com",
                "requester_user": roberto,
                "issue_type": "tow",
                "description": (
                    "Vintage motorcycle with a broken gearbox on the way back from "
                    "the Mandello rally. Need a van to transport the bike to the club "
                    "premises in Bergamo (~60 km)."
                ),
                "location": "Mandello del Lario, Piazza Garibaldi (LC)",
                "urgency": "medium",
                "status": "in_progress",
            },
            {
                "helper": chiara,
                "requester_name": "Demo: Alessandro Rossi",
                "requester_phone": "+39 333 333 4444",
                "requester_email": "alessandro.rossi@example.com",
                "requester_user": alessandro,
                "issue_type": "accommodation",
                "description": (
                    "Returning from the Dolomites tour with a chain problem on my V85 TT "
                    "near Treviglio. The bike moves slowly but I can't make another 80 km "
                    "to Lecco tonight. Looking for a garage and a place to sleep."
                ),
                "location": "Treviglio centre (BG)",
                "urgency": "medium",
                "status": "open",
            },
        ]

        for data in requests_data:
            AidRequest.objects.create(**data)
            self.stdout.write(
                f"  Created AidRequest: {data['issue_type']} - "
                f"{data['requester_name']} -> {data['helper'].display_name}"
            )

    def _create_contributions(self, members):
        """User-submitted stories, proposals, announcements (English)."""
        self.stdout.write("\nCreating contributions...")
        if Contribution.objects.exists():
            self.stdout.write("  Contributions already exist, skipping.")
            return

        if len(members) < 5:
            return

        marco, giulia, alessandro, chiara, roberto = members[:5]

        contributions = [
            {
                "user": marco,
                "contribution_type": "story",
                "title": "My first ride with the club",
                "body": (
                    "It was a Saturday in April 2019 when I went on my first ride "
                    "with Moto Club Red Eagles. I didn't know anyone, I was nervous. "
                    "But all it took was stopping at the first café to realise these "
                    "were my people. Since that day I have never missed a ride."
                ),
                "status": "approved",
            },
            {
                "user": giulia,
                "contribution_type": "story",
                "title": "The Stelvio solo: fear and wonder",
                "body": (
                    "Last year I decided to tackle the Stelvio on my own. "
                    "48 hairpins, sudden fog, and halfway up a pressure drop in the "
                    "rear tyre. I called mutual aid and in 30 minutes Alessandro was "
                    "there with the van. That is what this club is about."
                ),
                "status": "approved",
            },
            {
                "user": roberto,
                "contribution_type": "proposal",
                "title": "Proposal: 5-day Sardinia Tour",
                "body": (
                    "I propose a 5-day tour in Sardinia for September 2026. "
                    "Route: Olbia → Costa Smeralda → Barbagia → Cagliari → "
                    "Oristano → Alghero → Porto Torres. I have already contacted "
                    "3 biker-friendly B&Bs along the route. Estimated budget: €600 "
                    "per person all inclusive (ferry, accommodation, breakfasts)."
                ),
                "status": "approved",
            },
            {
                "user": chiara,
                "contribution_type": "announcement",
                "title": "Membership renewal: deadline 31 March",
                "body": (
                    "Reminder to all members that the deadline for renewing your "
                    "2026 membership card is 31 March. Members who renew before "
                    "15 March will receive a 10% discount. You can renew online "
                    "from your personal profile or in person at the clubhouse "
                    "during opening hours."
                ),
                "status": "approved",
            },
            {
                "user": alessandro,
                "contribution_type": "story",
                "title": "40 years in the saddle: my collection",
                "body": (
                    "I started collecting motorcycles in 1987, the year the club "
                    "was founded. Today my garage holds 7 bikes: a Le Mans III from "
                    "'81, a Stornello Sport from '68, a V7 Classic, a California "
                    "1400, a V85 TT, a V100 Mandello and a Griso 1200. "
                    "Each one has a story, each one has taken me to incredible places."
                ),
                "status": "pending",
            },
        ]

        for c in contributions:
            Contribution.objects.create(**c)
            self.stdout.write(f"  Created Contribution: {c['title'][:50]}")

    def _create_comments_and_reactions(self, members):
        """Comments and reactions on news and events (English)."""
        self.stdout.write("\nCreating comments and reactions...")
        if Comment.objects.exists() or Reaction.objects.exists():
            self.stdout.write("  Comments/Reactions already exist, skipping.")
            return

        if len(members) < 5:
            return

        marco, giulia, alessandro, chiara, roberto = members[:5]

        from django.contrib.contenttypes.models import ContentType
        from apps.website.models.pages import NewsPage, EventDetailPage

        news_ct = ContentType.objects.get_for_model(NewsPage)
        event_ct = ContentType.objects.get_for_model(EventDetailPage)

        news_pages = list(NewsPage.objects.live()[:3])
        event_pages = list(EventDetailPage.objects.live()[:3])

        if not news_pages or not event_pages:
            return

        comments_data = [
            (marco, news_ct, news_pages[0].pk,
             "Great news! Mandello is always a must-attend event. "
             "Who's coming with the group from Bergamo?", "approved"),
            (giulia, news_ct, news_pages[0].pk,
             "I'll be there! Who wants to join me for the lake loop in the afternoon?",
             "approved"),
            (alessandro, news_ct, news_pages[0].pk,
             "Present as every year. I'm bringing the Le Mans III too — "
             "should make an impression in the vintage bike area.", "approved"),
            (chiara, news_ct, news_pages[1].pk,
             "Tuscany on a motorbike is a dream. I'm already planning "
             "the trip with Giulia.", "approved"),
            (roberto, news_ct, news_pages[2].pk,
             "The Bayern Treffen was fantastic. The roads of Franconia "
             "are among the best in Europe.", "approved"),
            (marco, event_ct, event_pages[0].pk,
             "Registered! Does anyone know a good hotel in Mandello?",
             "approved"),
            (giulia, event_ct, event_pages[1].pk,
             "Tuscany in spring… can't wait!", "approved"),
            (roberto, event_ct, event_pages[2].pk,
             "The Orobie mountains on a bike are spectacular. Beautiful route.",
             "pending"),
        ]

        for user, ct, obj_id, text, status in comments_data:
            Comment.objects.create(
                user=user, content=text,
                content_type=ct, object_id=obj_id,
                moderation_status=status,
            )
        self.stdout.write(f"  Created {len(comments_data)} comments")

        reactions_data = [
            (marco, news_ct, news_pages[0].pk, "like"),
            (giulia, news_ct, news_pages[0].pk, "love"),
            (alessandro, news_ct, news_pages[0].pk, "like"),
            (chiara, news_ct, news_pages[0].pk, "like"),
            (roberto, news_ct, news_pages[0].pk, "love"),
            (marco, news_ct, news_pages[1].pk, "like"),
            (giulia, news_ct, news_pages[1].pk, "love"),
            (chiara, news_ct, news_pages[2].pk, "like"),
            (marco, event_ct, event_pages[0].pk, "love"),
            (giulia, event_ct, event_pages[0].pk, "love"),
            (alessandro, event_ct, event_pages[0].pk, "like"),
            (roberto, event_ct, event_pages[1].pk, "love"),
            (chiara, event_ct, event_pages[2].pk, "like"),
        ]

        for user, ct, obj_id, rtype in reactions_data:
            Reaction.objects.create(
                user=user, content_type=ct,
                object_id=obj_id, reaction_type=rtype,
            )
        self.stdout.write(f"  Created {len(reactions_data)} reactions")

    def _create_notifications(self, members):
        """Sample notifications for demo members (English)."""
        self.stdout.write("\nCreating notifications...")
        # Skip only if demo notification types already exist (event_registered
        # entries are created automatically by signals and can be safely ignored)
        demo_types = {
            "event_reminder", "comment_reply", "membership_approved",
            "aid_request", "new_event", "contribution_approved",
        }
        if NotificationQueue.objects.filter(notification_type__in=demo_types).exists():
            self.stdout.write("  Notifications already exist, skipping.")
            return

        if len(members) < 5:
            return

        marco, giulia, alessandro, chiara, roberto = members[:5]
        now = timezone.now()

        with override("en"):
            member_card_url = reverse("account:card")
            aid_url = reverse("account:aid")
            contributions_url = reverse("account:my_contributions")

        with override("en"):
            member_card_url = reverse("account:card")
            aid_url = reverse("account:aid")
            contributions_url = reverse("account:my_contributions")
            orobie_event = EventDetailPage.objects.live().filter(slug="orobie-tour-2026").first()
            franciacorta_event = EventDetailPage.objects.live().filter(slug="franciacorta-track-day-2026").first()
            kickoff_news = NewsPage.objects.live().filter(slug="2026-season-kickoff").first()
            orobie_event_url = orobie_event.localized.url if orobie_event else ""
            franciacorta_event_url = franciacorta_event.localized.url if franciacorta_event else ""
            kickoff_news_url = kickoff_news.localized.url if kickoff_news else ""

        notifications = [
            {
                "notification_type": "event_reminder",
                "recipient": marco,
                "channel": "in_app",
                "title": "Reminder: Orobie Tour in 3 days",
                "body": "The Orobie Tour is scheduled for Saturday. "
                        "Meeting point at 8:30 at the clubhouse.",
                "url": orobie_event_url,
                "status": "sent",
                "sent_at": now - timedelta(hours=2),
            },
            {
                "notification_type": "event_reminder",
                "recipient": giulia,
                "channel": "in_app",
                "title": "Reminder: Orobie Tour in 3 days",
                "body": "The Orobie Tour is scheduled for Saturday. "
                        "Meeting point at 8:30 at the clubhouse.",
                "url": orobie_event_url,
                "status": "sent",
                "sent_at": now - timedelta(hours=2),
            },
            {
                "notification_type": "comment_reply",
                "recipient": marco,
                "channel": "in_app",
                "title": "Giulia replied to your comment",
                "body": "Giulia F. replied to your comment on "
                        "'2026 Season Kick-off'.",
                "url": kickoff_news_url,
                "status": "sent",
                "sent_at": now - timedelta(hours=12),
            },
            {
                "notification_type": "membership_approved",
                "recipient": giulia,
                "channel": "email",
                "title": "Your membership request has been approved!",
                "body": "Your request for the Standard Membership Card has been "
                        "approved. Your digital card is available in your profile.",
                "url": member_card_url,
                "status": "sent",
                "sent_at": now - timedelta(days=5),
            },
            {
                "notification_type": "aid_request",
                "recipient": alessandro,
                "channel": "in_app",
                "title": "New roadside assistance request near you",
                "body": "Roberto C. needs a motorcycle transport from Mandello del "
                        "Lario. Distance: ~25 km from your location.",
                "url": aid_url,
                "status": "sent",
                "sent_at": now - timedelta(hours=36),
            },
            {
                "notification_type": "new_event",
                "recipient": chiara,
                "channel": "in_app",
                "title": "New event: Franciacorta Track Day",
                "body": "A new event has been published: Track Day at Franciacorta "
                        "Circuit. Registrations are open!",
                "url": franciacorta_event_url,
                "status": "pending",
            },
            {
                "notification_type": "contribution_approved",
                "recipient": roberto,
                "channel": "in_app",
                "title": "Your proposal has been approved",
                "body": "Your proposal '5-day Sardinia Tour' has been approved "
                        "and published on the club noticeboard.",
                "url": contributions_url,
                "status": "sent",
                "sent_at": now - timedelta(days=1),
            },
        ]

        for n in notifications:
            NotificationQueue.objects.create(**n)
        self.stdout.write(f"  Created {len(notifications)} notifications")

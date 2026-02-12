"""
Management command to populate the ClubCMS with realistic demo content.

Uses real motorcycle event data from Guzzi Days, Ducati, and HOG clubs.
Creates categories, snippets, pages, news, events, members, images
and mutual-aid requests so the site is immediately visitable after running.

Usage:
    python manage.py populate_demo
    docker compose exec web python manage.py populate_demo
    docker compose exec web python manage.py populate_demo --flush
"""

import io
import json
import uuid
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import requests as http_requests
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from wagtail.images.models import Image
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

from apps.members.models import ClubUser
from apps.mutual_aid.models import AidRequest
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


# ---------------------------------------------------------------------------
# Image download helpers
# ---------------------------------------------------------------------------

LOREMFLICKR = "https://loremflickr.com/{w}/{h}/{keywords}"

IMAGE_SPECS = [
    # (filename, width, height, keywords, description)
    ("hero_homepage.jpg", 1920, 1080, "motorcycle,road", "Hero homepage - motorcycle on open road"),
    ("hero_about.jpg", 1920, 800, "motorcycle,group,riders", "About page cover - group of riders"),
    ("event_mandello.jpg", 800, 600, "motorcycle,lake", "Event Mandello - motorcycle at lake"),
    ("event_pisa.jpg", 800, 600, "motorcycle,tuscany", "Event Pisa - motorcycle in Tuscany"),
    ("event_orobie.jpg", 800, 600, "motorcycle,mountains", "Event Orobie - mountain ride"),
    ("event_franciacorta.jpg", 800, 600, "motorcycle,racetrack", "Event Track Day"),
    ("event_children.jpg", 800, 600, "motorcycle,charity", "Event Ride for Children"),
    ("event_garda.jpg", 800, 600, "motorcycle,lake,garda", "Event HOG Rally Garda"),
    ("news_mandello.jpg", 800, 600, "moto,guzzi", "News Avviamento Motori"),
    ("news_pisa.jpg", 800, 600, "motorcycle,italy", "News Moto Guzzi Lands Pisa"),
    ("news_bayern.jpg", 800, 600, "motorcycle,germany", "News Bayern Treffen"),
    ("news_officina.jpg", 800, 600, "motorcycle,workshop", "News Officina Bergamo"),
    ("news_manutenzione.jpg", 800, 600, "motorcycle,engine,repair", "News Preparazione Stagione"),
    ("news_assemblea.jpg", 800, 600, "meeting,people", "News Assemblea Soci"),
    ("member_marco.jpg", 400, 400, "biker,man,portrait", "Member Marco Bianchi"),
    ("member_giulia.jpg", 400, 400, "biker,woman,portrait", "Member Giulia Ferrara"),
    ("member_alessandro.jpg", 400, 400, "motorcyclist,man", "Member Alessandro Rossi"),
    ("member_chiara.jpg", 400, 400, "motorcyclist,woman", "Member Chiara Fontana"),
    ("member_roberto.jpg", 400, 400, "biker,man,helmet", "Member Roberto Colombo"),
]


def _download_image(w, h, keywords, title):
    """Download an image from LoremFlickr and return a Wagtail Image."""
    url = LOREMFLICKR.format(w=w, h=h, keywords=keywords)
    resp = http_requests.get(url, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    fname = f"demo_{uuid.uuid4().hex[:8]}.jpg"
    image_file = ImageFile(io.BytesIO(resp.content), name=fname)
    img = Image(title=title, file=image_file, width=w, height=h)
    img.save()
    return img


class Command(BaseCommand):
    help = "Populate ClubCMS with realistic demo content"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing demo content before populating",
        )

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing content...")
            self._flush()

        self.stdout.write("Creating demo content...")

        # Step 1: Snippets and categories
        self._create_color_scheme()
        self._create_categories()
        self._create_products()
        self._create_testimonials()
        self._create_faqs()
        self._create_photo_tags()
        self._create_press_releases()
        self._create_brand_assets()
        self._create_aid_skills()

        # Step 2: Page hierarchy
        home_page = self._create_home_page()

        # Step 3: Sub-pages
        about = self._create_about_page(home_page)
        self._create_board_page(about)
        news_index = self._create_news_index(home_page)
        events_page = self._create_events_page(home_page)
        self._create_gallery_page(home_page)
        self._create_contact_page(home_page)
        self._create_privacy_page(home_page)
        self._create_transparency_page(home_page)
        self._create_press_page(home_page)
        partner_index = self._create_partner_index(home_page)

        # Step 4: Content pages
        self._create_news_articles(news_index)
        self._create_events(events_page)
        self._create_partners(partner_index)

        # Step 5: Navigation (needs pages to exist first)
        navbar = self._create_navbar(home_page, about, news_index, events_page)
        footer = self._create_footer(home_page, about, news_index, events_page)

        # Step 6: Site settings
        self._create_site_settings(home_page, navbar, footer)

        # Step 7: Download images and assign to pages
        images = self._download_images()
        self._assign_page_images(images)

        # Step 8: Members
        members = self._create_members(images)

        # Step 9: Mutual-aid requests
        self._create_aid_requests(members)

        self.stdout.write(self.style.SUCCESS(
            "\nDemo content created successfully! "
            "Visit http://localhost:8888/ to see the site."
        ))

    def _flush(self):
        """Remove all demo-created content."""
        # Remove demo images
        Image.objects.filter(file__startswith="original_images/demo_").delete()
        # Remove demo members (cascade-deletes their aid requests)
        ClubUser.objects.filter(username__startswith="demo_").delete()
        # Remove remaining aid requests with demo prefix
        AidRequest.objects.filter(requester_name__startswith="Demo:").delete()
        # Remove pages and snippets
        for model in [HomePage, SiteSettings, ColorScheme, Navbar, Footer,
                      NewsCategory, EventCategory, PartnerCategory,
                      Product, Testimonial, FAQ, PhotoTag,
                      PressRelease, BrandAsset, AidSkill]:
            model.objects.all().delete()

    # ------------------------------------------------------------------
    # Color Scheme
    # ------------------------------------------------------------------

    def _create_color_scheme(self):
        if ColorScheme.objects.exists():
            self.stdout.write("  ColorScheme already exists, skipping.")
            self.color_scheme = ColorScheme.objects.first()
            return

        self.color_scheme = ColorScheme.objects.create(
            name="Rosso Corsa",
            primary="#B91C1C",      # Deep red
            secondary="#F59E0B",    # Amber/gold
            accent="#1E40AF",       # Deep blue
            surface="#F9FAFB",      # Light gray
            surface_alt="#FFFFFF",  # White
            text_primary="#111827", # Near black
            text_muted="#6B7280",   # Gray
            is_dark_mode=False,
        )
        self.stdout.write("  Created ColorScheme: Rosso Corsa")

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def _create_categories(self):
        # News categories
        news_cats = [
            ("Club News", "club-news", "#B91C1C",
             "News about our club activities and announcements"),
            ("Events Recap", "events-recap", "#059669",
             "Reports and photos from past events"),
            ("Motorcycle World", "motorcycle-world", "#7C3AED",
             "News from the motorcycle industry and community"),
            ("Technical", "technical", "#2563EB",
             "Technical articles, reviews, and maintenance tips"),
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
            ("Rally & Raduno", "rally", "rally"),
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
    # Products
    # ------------------------------------------------------------------

    def _create_products(self):
        products = [
            {
                "name": "Tessera Socio Ordinario",
                "slug": "socio-ordinario",
                "description": "Tessera associativa annuale con diritto di voto e partecipazione eventi.",
                "price": Decimal("50.00"),
                "grants_vote": True,
                "grants_events": True,
                "grants_upload": True,
                "order": 1,
            },
            {
                "name": "Tessera Socio Sostenitore",
                "slug": "socio-sostenitore",
                "description": "Tessera sostenitore con sconto eventi e accesso gallery.",
                "price": Decimal("30.00"),
                "grants_events": True,
                "grants_discount": True,
                "discount_percent": 10,
                "order": 2,
            },
            {
                "name": "Tessera Socio Premium",
                "slug": "socio-premium",
                "description": "Tessera premium con tutti i privilegi e 20% sconto eventi.",
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
    # Testimonials
    # ------------------------------------------------------------------

    def _create_testimonials(self):
        testimonials = [
            {
                "quote": "Far parte di questo club ha cambiato il mio modo di vivere la moto. "
                         "Le uscite domenicali e i raduni sono momenti indimenticabili.",
                "author_name": "Marco Bianchi",
                "author_role": "Socio dal 2019",
                "featured": True,
            },
            {
                "quote": "L'assistenza reciproca tra soci è straordinaria. "
                         "Una volta rimasto in panne sullo Stelvio, in 30 minuti avevo già aiuto.",
                "author_name": "Giulia Ferrara",
                "author_role": "Socia dal 2021",
                "featured": True,
            },
            {
                "quote": "I tour organizzati dal club sono sempre perfetti: "
                         "percorsi mozzafiato, soste gastronomiche e ottima compagnia.",
                "author_name": "Alessandro Rossi",
                "author_role": "Socio fondatore",
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
    # FAQs
    # ------------------------------------------------------------------

    def _create_faqs(self):
        faqs = [
            {
                "question": "Come posso iscrivermi al Moto Club?",
                "answer": (
                    "<p>Puoi iscriverti compilando il modulo di registrazione online "
                    "sul nostro sito, oppure presentandoti presso la sede sociale durante "
                    "gli orari di apertura (Mercoledì e Venerdì 20:30-23:00, Sabato "
                    "15:00-18:00). È necessario un documento di identità valido e il "
                    "pagamento della quota associativa.</p>"
                ),
                "category": "Iscrizione",
                "order": 1,
            },
            {
                "question": "Quali sono i costi della tessera socio?",
                "answer": (
                    "<p>Offriamo tre tipologie di tessera:</p><ul>"
                    "<li><strong>Socio Ordinario</strong>: €50/anno – diritto di voto, "
                    "eventi, upload gallery</li>"
                    "<li><strong>Socio Sostenitore</strong>: €30/anno – eventi, 10% sconto</li>"
                    "<li><strong>Socio Premium</strong>: €100/anno – tutti i privilegi, "
                    "20% sconto eventi</li></ul>"
                ),
                "category": "Iscrizione",
                "order": 2,
            },
            {
                "question": "Posso partecipare agli eventi senza essere socio?",
                "answer": (
                    "<p>Alcuni eventi sono aperti anche ai non soci (come il Ride for "
                    "Children). Per la maggior parte degli eventi organizzati dal club è "
                    "necessaria la tessera socio in corso di validità. I non soci possono "
                    "partecipare come ospiti per un massimo di 2 uscite prima di dover "
                    "effettuare l'iscrizione.</p>"
                ),
                "category": "Eventi",
                "order": 3,
            },
            {
                "question": "Come funziona il mutuo soccorso?",
                "answer": (
                    "<p>Il sistema di mutuo soccorso permette ai soci di richiedere e "
                    "offrire assistenza in caso di guasto o emergenza stradale. Ogni "
                    "socio può indicare nel proprio profilo le competenze (meccanica, "
                    "trasporto, logistica) e il raggio di disponibilità. In caso di "
                    "necessità, il sistema notifica i soci disponibili nella zona.</p>"
                ),
                "category": "Servizi",
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
    # Photo Tags
    # ------------------------------------------------------------------

    def _create_photo_tags(self):
        tags = [
            ("Raduno", "raduno"),
            ("Tour", "tour"),
            ("Track Day", "track-day"),
            ("Sociale", "sociale"),
            ("Beneficenza", "beneficenza"),
            ("Panorama", "panorama"),
            ("Moto", "moto"),
        ]
        for name, slug in tags:
            _, created = PhotoTag.objects.get_or_create(
                slug=slug, defaults={"name": name},
            )
            if created:
                self.stdout.write(f"  Created PhotoTag: {name}")

    # ------------------------------------------------------------------
    # Press Releases
    # ------------------------------------------------------------------

    def _create_press_releases(self):
        releases = [
            {
                "title": "Moto Club Aquile Rosse annuncia il calendario eventi 2026",
                "date": date(2026, 1, 28),
                "body": (
                    "<p>Il Moto Club Aquile Rosse ASD di Bergamo ha presentato il "
                    "calendario ufficiale degli eventi per la stagione 2026, che prevede "
                    "oltre 50 appuntamenti tra raduni, tour, track day e iniziative "
                    "benefiche.</p>"
                    "<p>Tra gli eventi di punta: l'Avviamento Motori a Mandello del "
                    "Lario, il Tour delle Orobie, il Track Day all'Autodromo di "
                    "Franciacorta e la 12ª edizione del Ride for Children a favore "
                    "dell'Ospedale Papa Giovanni XXIII.</p>"
                    "<p>Per informazioni: stampa@aquilerosse.it</p>"
                ),
                "is_archived": False,
            },
            {
                "title": "Ride for Children 2025: raccolti €8.500 per la Pediatria",
                "date": date(2025, 10, 15),
                "body": (
                    "<p>Si è conclusa con grande successo la 11ª edizione del Ride "
                    "for Children, il motogiro benefico annuale del Moto Club Aquile "
                    "Rosse. L'evento ha visto la partecipazione di oltre 200 "
                    "motociclisti e ha permesso di raccogliere €8.500, interamente "
                    "devoluti al reparto di Pediatria dell'Ospedale Papa Giovanni "
                    "XXIII di Bergamo.</p>"
                    "<p>Dal 2014 ad oggi, il Ride for Children ha raccolto "
                    "complessivamente oltre €43.000.</p>"
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
    # Brand Assets
    # ------------------------------------------------------------------

    def _create_brand_assets(self):
        assets = [
            {
                "name": "Logo Moto Club Aquile Rosse - Colore",
                "category": "logo",
                "description": (
                    "Logo ufficiale del club in versione a colori. Formato "
                    "vettoriale SVG e PNG ad alta risoluzione. Da utilizzare "
                    "su sfondo chiaro."
                ),
                "order": 1,
            },
            {
                "name": "Logo Moto Club Aquile Rosse - Bianco",
                "category": "logo",
                "description": (
                    "Logo ufficiale del club in versione bianca monocromatica. "
                    "Per utilizzo su sfondi scuri."
                ),
                "order": 2,
            },
            {
                "name": "Linee guida brand",
                "category": "template",
                "description": (
                    "Documento con le linee guida per l'utilizzo corretto del "
                    "marchio, colori ufficiali e font del club."
                ),
                "order": 3,
            },
        ]
        for a in assets:
            _, created = BrandAsset.objects.get_or_create(
                name=a["name"], defaults=a,
            )
            if created:
                self.stdout.write(f"  Created BrandAsset: {a['name'][:50]}")

    # ------------------------------------------------------------------
    # Aid Skills (Mutual Aid)
    # ------------------------------------------------------------------

    def _create_aid_skills(self):
        skills = [
            ("Meccanica base", "meccanica-base",
             "Riparazioni di base: catena, candele, fusibili, regolazioni.",
             "mechanics", 1),
            ("Meccanica avanzata", "meccanica-avanzata",
             "Interventi complessi: carburatori, impianto elettrico, freni.",
             "mechanics", 2),
            ("Trasporto moto", "trasporto-moto",
             "Disponibilità di furgone/carrello per trasporto moto in panne.",
             "transport", 3),
            ("Primo soccorso", "primo-soccorso",
             "Competenze di primo soccorso e dotazione kit emergenza.",
             "emergency", 4),
            ("Ospitalità", "ospitalita",
             "Disponibilità per ospitare soci in transito (pernottamento, garage).",
             "logistics", 5),
            ("Recupero stradale", "recupero-stradale",
             "Assistenza per recupero moto e motociclista da zone impervie.",
             "transport", 6),
        ]
        for name, slug, desc, cat, order in skills:
            _, created = AidSkill.objects.get_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description": desc,
                    "category": cat,
                    "order": order,
                },
            )
            if created:
                self.stdout.write(f"  Created AidSkill: {name}")

    # ------------------------------------------------------------------
    # Home Page
    # ------------------------------------------------------------------

    def _create_home_page(self):
        # Check if a HomePage already exists
        if HomePage.objects.exists():
            self.stdout.write("  HomePage already exists, reusing.")
            return HomePage.objects.first()

        # Get the root page
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stdout.write(self.style.ERROR("No root page found!"))
            return None

        # Delete Wagtail's default welcome page if it exists
        Page.objects.filter(depth=2, slug="home").exclude(
            content_type__model="homepage"
        ).delete()

        home = HomePage(
            title="Moto Club Aquile Rosse",
            slug="home",
            hero_title="Moto Club Aquile Rosse",
            hero_subtitle="Passione, avventura e fratellanza su due ruote dal 1987",
            primary_cta_text="Prossimi Eventi",
            secondary_cta_text="Diventa Socio",
            body=json.dumps([
                {
                    "type": "rich_text",
                    "value": "<h2>Benvenuti nel Moto Club Aquile Rosse</h2>"
                             "<p>Siamo un club motociclistico fondato nel 1987 a Bergamo, "
                             "con oltre 250 soci attivi in tutta la Lombardia. "
                             "Organizziamo raduni, tour, track day e eventi benefici "
                             "per condividere la nostra passione per le due ruote.</p>",
                },
                {
                    "type": "stats",
                    "value": {
                        "items": [
                            {"number": "250+", "label": "Soci Attivi"},
                            {"number": "37", "label": "Anni di Storia"},
                            {"number": "50+", "label": "Eventi / Anno"},
                            {"number": "12", "label": "Tour Nazionali"},
                        ],
                    },
                },
                {
                    "type": "cta",
                    "value": {
                        "title": "Unisciti a Noi",
                        "text": "Diventa socio del Moto Club Aquile Rosse e "
                                "partecipa alle nostre avventure su strada.",
                        "button_text": "Scopri le Tessere",
                        "button_url": "/about/",
                        "style": "primary",
                    },
                },
            ]),
        )
        root.add_child(instance=home)
        home.save_revision().publish()

        # Update the default site to point to our home page
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
    # About Page + Board Page
    # ------------------------------------------------------------------

    def _create_about_page(self, parent):
        if AboutPage.objects.exists():
            self.stdout.write("  AboutPage already exists, reusing.")
            return AboutPage.objects.first()

        about = AboutPage(
            title="Chi Siamo",
            slug="chi-siamo",
            intro=(
                "<p>Il Moto Club Aquile Rosse nasce nel 1987 a Bergamo dall'idea di "
                "un gruppo di appassionati motociclisti che volevano condividere la "
                "passione per le due ruote in un contesto di amicizia e solidarietà.</p>"
                "<p>Oggi il club conta oltre 250 soci iscritti, con una sede sociale "
                "in Via Borgo Palazzo 22, Bergamo. Siamo affiliati alla FMI (Federazione "
                "Motociclistica Italiana) e organizziamo ogni anno più di 50 eventi "
                "tra raduni, tour, giornate in pista e iniziative benefiche.</p>"
            ),
            body=json.dumps([
                {
                    "type": "rich_text",
                    "value": "<h2>La Nostra Storia</h2>"
                             "<p>Fondato come piccolo gruppo di amici che si ritrovavano "
                             "ogni domenica per una passeggiata sulle strade bergamasche, "
                             "il club è cresciuto fino a diventare uno dei più attivi "
                             "della Lombardia.</p>"
                             "<h3>I Nostri Valori</h3>"
                             "<ul>"
                             "<li><strong>Passione</strong>: La moto è il nostro modo di vivere</li>"
                             "<li><strong>Sicurezza</strong>: Guida responsabile e formazione continua</li>"
                             "<li><strong>Solidarietà</strong>: Mutuo soccorso tra soci</li>"
                             "<li><strong>Inclusività</strong>: Tutti i marchi e modelli sono benvenuti</li>"
                             "</ul>",
                },
                {
                    "type": "timeline",
                    "value": {
                        "items": [
                            {"year": "1987", "title": "Fondazione",
                             "description": "12 amici fondano il Moto Club Aquile Rosse a Bergamo."},
                            {"year": "1995", "title": "Affiliazione FMI",
                             "description": "Il club si affilia alla Federazione Motociclistica Italiana."},
                            {"year": "2005", "title": "Nuova Sede",
                             "description": "Inaugurata la nuova sede sociale in Via Borgo Palazzo."},
                            {"year": "2015", "title": "250 Soci",
                             "description": "Il club raggiunge il traguardo di 250 soci attivi."},
                            {"year": "2024", "title": "Federazione",
                             "description": "Avvio del programma di federazione con club partner in Italia."},
                        ],
                    },
                },
            ]),
        )
        parent.add_child(instance=about)
        about.save_revision().publish()
        self.stdout.write("  Created AboutPage: Chi Siamo")
        return about

    def _create_board_page(self, parent):
        if BoardPage.objects.exists():
            self.stdout.write("  BoardPage already exists, skipping.")
            return

        board = BoardPage(
            title="Consiglio Direttivo",
            slug="consiglio-direttivo",
            intro="<p>Il Consiglio Direttivo guida il club con passione e dedizione.</p>",
            body=json.dumps([
                {
                    "type": "team_grid",
                    "value": {
                        "columns": 3,
                        "members": [
                            {"name": "Roberto Colombo", "role": "Presidente",
                             "bio": "Motociclista da 40 anni, guida il club dal 2015. "
                                    "Appassionato di Moto Guzzi e viaggi lungo raggio."},
                            {"name": "Francesca Moretti", "role": "Vicepresidente",
                             "bio": "Ingegnere meccanico e istruttrice di guida sicura. "
                                    "Organizza i corsi di formazione del club."},
                            {"name": "Luca Bernardi", "role": "Segretario",
                             "bio": "Gestisce le iscrizioni, la comunicazione e "
                                    "il sito web del club."},
                            {"name": "Chiara Fontana", "role": "Tesoriere",
                             "bio": "Commercialista di professione, tiene i conti "
                                    "del club in ordine dal 2020."},
                            {"name": "Davide Marchetti", "role": "Resp. Eventi",
                             "bio": "Pianifica e organizza tutti gli eventi del club. "
                                    "Specialista in logistica e percorsi."},
                            {"name": "Elena Rizzo", "role": "Resp. Comunicazione",
                             "bio": "Giornalista e social media manager. Cura la "
                                    "newsletter e i canali social del club."},
                        ],
                    },
                },
            ]),
        )
        parent.add_child(instance=board)
        board.save_revision().publish()
        self.stdout.write("  Created BoardPage: Consiglio Direttivo")

    # ------------------------------------------------------------------
    # News Index + Articles
    # ------------------------------------------------------------------

    def _create_news_index(self, parent):
        if NewsIndexPage.objects.exists():
            self.stdout.write("  NewsIndexPage already exists, reusing.")
            return NewsIndexPage.objects.first()

        news_index = NewsIndexPage(
            title="News",
            slug="news",
            intro="<p>Tutte le novità dal mondo del Moto Club Aquile Rosse.</p>",
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
                "title": "Avviamento Motori 2026: Si Riparte da Mandello!",
                "slug": "avviamento-motori-2026",
                "intro": "Il tradizionale raduno di apertura stagione torna a Mandello del Lario "
                         "con novità e sorprese per tutti gli appassionati Guzzi.",
                "display_date": today - timedelta(days=3),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Come ogni anno, la stagione motociclistica si apre "
                                 "con il tradizionale <strong>Avviamento Motori</strong> "
                                 "a Mandello del Lario, la patria della Moto Guzzi.</p>"
                                 "<p>L'evento, organizzato dal Moto Club Le Aquile di Mandello "
                                 "in collaborazione con Guzzi Days, prevede un programma ricco "
                                 "di attività: dalla sfilata lungo il lago alle visite guidate "
                                 "al Museo Moto Guzzi, fino alla cena sociale presso il "
                                 "Ristorante Il Griso.</p>"
                                 "<h3>Programma</h3>"
                                 "<ul>"
                                 "<li>Ore 9:00 - Ritrovo presso Piazza Garibaldi</li>"
                                 "<li>Ore 10:30 - Sfilata lungo il Lago di Como</li>"
                                 "<li>Ore 12:30 - Pranzo sociale</li>"
                                 "<li>Ore 15:00 - Visita Museo Moto Guzzi</li>"
                                 "<li>Ore 18:00 - Aperitivo e premiazioni</li>"
                                 "</ul>"
                                 "<p>Il Moto Club Aquile Rosse parteciperà con una "
                                 "delegazione di 30 soci. Le iscrizioni sono aperte "
                                 "fino al 15 marzo.</p>",
                    },
                ]),
            },
            {
                "title": "1° Moto Guzzi Lands of Pisa: Nuovo Evento in Toscana",
                "slug": "moto-guzzi-lands-pisa",
                "intro": "Nasce un nuovo raduno guzzista a Pontedera, nella terra dove "
                         "nacque la Piaggio e a due passi dalla torre pendente.",
                "display_date": today - timedelta(days=7),
                "category": "motorcycle-world",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Grandi novità dal panorama dei raduni motociclistici "
                                 "italiani: è stato annunciato il <strong>1° Moto Guzzi "
                                 "Lands of Pisa</strong>, un evento che si terrà a Pontedera "
                                 "(PI) nella primavera 2026.</p>"
                                 "<p>L'evento è organizzato dal Moto Club Terre di Pisa "
                                 "in collaborazione con la rete Guzzi Days e promette "
                                 "un weekend all'insegna della cultura motociclistica "
                                 "toscana, con percorsi tra le colline pisane, degustazioni "
                                 "di prodotti locali e un raduno statico nel centro storico.</p>"
                                 "<p>Il nostro club sta già organizzando una trasferta di "
                                 "gruppo. Chi è interessato può contattare il responsabile "
                                 "eventi Davide Marchetti.</p>",
                    },
                ]),
            },
            {
                "title": "Resoconto: Spring Franken Bayern Treffen 2026",
                "slug": "spring-franken-bayern-treffen",
                "intro": "Otto soci del club hanno partecipato al raduno primaverile "
                         "in Baviera. Ecco il racconto dell'esperienza.",
                "display_date": today - timedelta(days=14),
                "category": "events-recap",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Lo scorso weekend un gruppo di 8 soci del Moto Club "
                                 "Aquile Rosse ha attraversato le Alpi per partecipare al "
                                 "<strong>Spring Franken Bayern Treffen</strong>, il raduno "
                                 "primaverile che segna l'inizio della stagione nella "
                                 "regione tedesca della Franconia.</p>"
                                 "<p>Il percorso di andata ha toccato il Passo del Brennero, "
                                 "Innsbruck e Monaco prima di arrivare nella zona di "
                                 "Norimberga. Il raduno, frequentato da oltre 500 motociclisti "
                                 "provenienti da tutta Europa, ha offerto giornate di "
                                 "cavalcate nelle splendide strade della Franconia, "
                                 "birra bavarese e un'atmosfera di grande cameratismo.</p>"
                                 "<p>Prossima trasferta internazionale: il Guzzi Days 2026 "
                                 "in Sudafrica!</p>",
                    },
                ]),
            },
            {
                "title": "Nuova Convenzione con Officina Moto Bergamo",
                "slug": "convenzione-officina-moto-bergamo",
                "intro": "Siglata una convenzione con l'Officina Moto Bergamo per "
                         "sconti su tagliandi e riparazioni per tutti i soci.",
                "display_date": today - timedelta(days=20),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Siamo lieti di annunciare una nuova convenzione con "
                                 "<strong>Officina Moto Bergamo</strong>, centro assistenza "
                                 "multimarca situato in Via Seriate 42.</p>"
                                 "<p>Tutti i soci del Moto Club Aquile Rosse potranno "
                                 "usufruire dei seguenti sconti:</p>"
                                 "<ul>"
                                 "<li>15% su tagliandi e manutenzione ordinaria</li>"
                                 "<li>10% su ricambi originali e aftermarket</li>"
                                 "<li>Diagnosi elettronica gratuita</li>"
                                 "<li>Priorità nelle prenotazioni durante l'alta stagione</li>"
                                 "</ul>"
                                 "<p>Per accedere alle agevolazioni è sufficiente presentare "
                                 "la tessera socio in corso di validità.</p>",
                    },
                ]),
            },
            {
                "title": "Guida alla Preparazione della Moto per la Stagione",
                "slug": "preparazione-moto-stagione",
                "intro": "I consigli del nostro meccanico di fiducia per rimettere "
                         "la moto in forma dopo la pausa invernale.",
                "display_date": today - timedelta(days=30),
                "category": "technical",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Con l'arrivo della bella stagione è tempo di "
                                 "preparare la moto per i primi giri. Ecco una checklist "
                                 "essenziale preparata con il nostro partner tecnico "
                                 "Officina Moto Bergamo.</p>"
                                 "<h3>Controlli Essenziali</h3>"
                                 "<ol>"
                                 "<li><strong>Batteria</strong>: Verificare la carica e "
                                 "i livelli dell'elettrolito. Se la moto è stata ferma "
                                 "più di 3 mesi, considerare la sostituzione.</li>"
                                 "<li><strong>Pneumatici</strong>: Controllare pressione, "
                                 "usura e data di fabbricazione (DOT). Pneumatici più "
                                 "vecchi di 5 anni vanno sostituiti.</li>"
                                 "<li><strong>Freni</strong>: Verificare lo spessore "
                                 "delle pastiglie e il livello del liquido freni.</li>"
                                 "<li><strong>Olio motore</strong>: Cambiare olio e "
                                 "filtro se non fatto prima del rimessaggio.</li>"
                                 "<li><strong>Catena</strong>: Pulire, lubrificare e "
                                 "verificare la tensione.</li>"
                                 "<li><strong>Luci</strong>: Controllare tutte le luci, "
                                 "incluse frecce e luce targa.</li>"
                                 "</ol>",
                    },
                ]),
            },
            {
                "title": "Assemblea Soci 2026: Approvato il Bilancio",
                "slug": "assemblea-soci-2026",
                "intro": "L'assemblea annuale ha approvato all'unanimità il bilancio "
                         "e il programma eventi per il nuovo anno.",
                "display_date": today - timedelta(days=45),
                "category": "club-news",
                "body": json.dumps([
                    {
                        "type": "rich_text",
                        "value": "<p>Si è tenuta sabato scorso l'assemblea annuale dei soci "
                                 "del Moto Club Aquile Rosse presso la sede sociale.</p>"
                                 "<p>Con la partecipazione di 142 soci su 258 aventi diritto, "
                                 "l'assemblea ha approvato all'unanimità il bilancio consuntivo "
                                 "2025 e il bilancio preventivo 2026.</p>"
                                 "<h3>Punti Principali</h3>"
                                 "<ul>"
                                 "<li>Confermato il direttivo in carica per il biennio 2026-2027</li>"
                                 "<li>Approvato il calendario eventi con 52 uscite programmate</li>"
                                 "<li>Nuova partnership con 3 officine convenzionate</li>"
                                 "<li>Lancio del sistema di federazione con altri club</li>"
                                 "<li>Acquisto di un defibrillatore per la sede</li>"
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
    # Events Page + Event Detail Pages
    # ------------------------------------------------------------------

    def _create_events_page(self, parent):
        if EventsPage.objects.exists():
            self.stdout.write("  EventsPage already exists, reusing.")
            return EventsPage.objects.first()

        events = EventsPage(
            title="Eventi",
            slug="eventi",
            intro="<p>Tutti gli eventi organizzati e supportati dal Moto Club Aquile Rosse.</p>",
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
                "title": "Avviamento Motori 2026 - Mandello del Lario",
                "slug": "avviamento-motori-mandello-2026",
                "intro": "Il tradizionale raduno di apertura stagione nella patria della Moto Guzzi.",
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
                    "value": "<p>Partecipa all'<strong>Avviamento Motori 2026</strong>, "
                             "il raduno che apre ufficialmente la stagione motociclistica "
                             "sulle sponde del Lago di Como.</p>"
                             "<p>Organizzato dal Moto Club Le Aquile di Mandello in "
                             "collaborazione con la rete Guzzi Days, l'evento è aperto "
                             "a tutte le marche e modelli.</p>"
                             "<h3>Cosa Include</h3>"
                             "<ul>"
                             "<li>Sfilata panoramica lungo il Lago di Como</li>"
                             "<li>Pranzo sociale (incluso nella quota)</li>"
                             "<li>Visita al Museo Moto Guzzi</li>"
                             "<li>Gadget commemorativo</li>"
                             "</ul>",
                }]),
            },
            {
                "title": "1° Moto Guzzi Lands of Pisa",
                "slug": "moto-guzzi-lands-pisa-2026",
                "intro": "Primo raduno guzzista nella terra di Pontedera, tra le colline toscane.",
                "start_date": now + timedelta(days=60),
                "end_date": now + timedelta(days=62),
                "location_name": "Centro Storico, Pontedera",
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
                    "value": "<p>Un weekend nella splendida Toscana per il primo "
                             "<strong>Moto Guzzi Lands of Pisa</strong>.</p>"
                             "<p>Il programma prevede tour guidati nelle colline "
                             "pisane, visita al Museo Piaggio di Pontedera, "
                             "degustazione di prodotti tipici e raduno statico "
                             "in piazza con esposizione di Guzzi d'epoca e moderne.</p>",
                }]),
            },
            {
                "title": "Tour delle Orobie - Giornata Sociale",
                "slug": "tour-orobie-2026",
                "intro": "Uscita giornaliera tra le valli bergamasche con sosta pranzo in rifugio.",
                "start_date": now + timedelta(days=14),
                "end_date": now + timedelta(days=14, hours=10),
                "location_name": "Sede Club, Bergamo",
                "location_address": "Via Borgo Palazzo 22, 24121 Bergamo",
                "location_coordinates": "45.6983,9.6773",
                "category": "touring",
                "registration_open": True,
                "max_attendees": 40,
                "base_fee": Decimal("15.00"),
                "member_discount_percent": 100,
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Uscita sociale nelle magnifiche <strong>Valli Orobie</strong>, "
                             "con un percorso di circa 180 km tra le valli bergamasche.</p>"
                             "<p>Partenza dalla sede alle 8:30. Percorso: Bergamo → Val Seriana "
                             "→ Passo della Presolana → Val di Scalve → Lago d'Iseo → Bergamo. "
                             "Sosta pranzo presso il Rifugio Albani.</p>"
                             "<p><em>Gratuito per i soci con tessera in regola.</em></p>",
                }]),
            },
            {
                "title": "Track Day - Autodromo di Franciacorta",
                "slug": "track-day-franciacorta-2026",
                "intro": "Giornata in pista all'Autodromo di Franciacorta con istruttori professionisti.",
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
                    "value": "<p>Una giornata dedicata alla guida sportiva sicura "
                             "all'<strong>Autodromo di Franciacorta</strong>.</p>"
                             "<p>Il programma include:</p>"
                             "<ul>"
                             "<li>Briefing tecnico e di sicurezza</li>"
                             "<li>3 turni in pista da 20 minuti ciascuno</li>"
                             "<li>Coaching personalizzato con istruttori ex-CIV</li>"
                             "<li>Pranzo in circuito</li>"
                             "<li>Analisi telemetrica (facoltativa)</li>"
                             "</ul>"
                             "<p>Obbligatori: tuta in pelle integrale, guanti, "
                             "stivali tecnici, casco integrale.</p>",
                }]),
            },
            {
                "title": "Beneficenza: Ride for Children",
                "slug": "ride-for-children-2026",
                "intro": "Motogiro benefico a favore dell'Ospedale dei Bambini di Bergamo.",
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
                    "value": "<p>Il <strong>Ride for Children</strong> è l'evento "
                             "benefico annuale del Moto Club Aquile Rosse, giunto "
                             "alla sua 12ª edizione.</p>"
                             "<p>L'intero ricavato delle iscrizioni sarà devoluto "
                             "al reparto di Pediatria dell'Ospedale Papa Giovanni XXIII "
                             "di Bergamo per l'acquisto di attrezzature mediche.</p>"
                             "<p>Nelle edizioni precedenti abbiamo raccolto oltre "
                             "€35.000 grazie alla generosità di centinaia di motociclisti.</p>"
                             "<p><strong>Aperto a tutti, soci e non soci!</strong></p>",
                }]),
            },
            {
                "title": "HOG Rally Garda 2026",
                "slug": "hog-rally-garda-2026",
                "intro": "Raduno HOG (Harley Owners Group) sul Lago di Garda con parata e concerti.",
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
                    "value": "<p>Il <strong>HOG Rally Garda</strong> è uno dei più grandi "
                             "raduni Harley-Davidson del Nord Italia, organizzato dal "
                             "Chapter HOG Lake Garda in collaborazione con il concessionario "
                             "Harley-Davidson Brescia.</p>"
                             "<p>Quattro giorni di moto, musica, food truck e la celebre "
                             "Thunder Parade lungo le sponde del lago. Il nostro club "
                             "partecipa come ospite con uno stand informativo.</p>",
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
    # Gallery Page
    # ------------------------------------------------------------------

    def _create_gallery_page(self, parent):
        if GalleryPage.objects.exists():
            self.stdout.write("  GalleryPage already exists, skipping.")
            return

        gallery = GalleryPage(
            title="Galleria",
            slug="galleria",
            intro="<p>Le foto più belle dai nostri eventi, tour e raduni.</p>",
        )
        parent.add_child(instance=gallery)
        gallery.save_revision().publish()
        self.stdout.write("  Created GalleryPage")

    # ------------------------------------------------------------------
    # Contact Page
    # ------------------------------------------------------------------

    def _create_contact_page(self, parent):
        if ContactPage.objects.exists():
            self.stdout.write("  ContactPage already exists, skipping.")
            return

        contact = ContactPage(
            title="Contatti",
            slug="contatti",
            intro="<p>Hai domande? Vuoi sapere di più sul club? Scrivici!</p>",
            form_title="Inviaci un Messaggio",
            success_message="<p>Grazie per il tuo messaggio! Ti risponderemo entro 48 ore.</p>",
            captcha_enabled=True,
            captcha_provider="honeypot",
        )
        parent.add_child(instance=contact)
        contact.save_revision().publish()
        self.stdout.write("  Created ContactPage")

    # ------------------------------------------------------------------
    # Privacy, Transparency, Press Pages
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
                "value": "<h2>Informativa sulla Privacy</h2>"
                         "<p>Ai sensi del Regolamento (UE) 2016/679 (GDPR), "
                         "il Moto Club Aquile Rosse ASD, in qualità di Titolare "
                         "del trattamento, informa che i dati personali raccolti "
                         "attraverso questo sito web saranno trattati nel rispetto "
                         "della normativa vigente.</p>"
                         "<h3>Dati Raccolti</h3>"
                         "<p>I dati raccolti comprendono: nome, cognome, indirizzo email, "
                         "numero di telefono (facoltativi) e dati di navigazione.</p>"
                         "<h3>Finalità del Trattamento</h3>"
                         "<ul>"
                         "<li>Gestione delle iscrizioni al club</li>"
                         "<li>Organizzazione di eventi e comunicazioni</li>"
                         "<li>Adempimenti di legge</li>"
                         "</ul>"
                         "<h3>Diritti dell'Interessato</h3>"
                         "<p>L'utente può esercitare i diritti di accesso, rettifica, "
                         "cancellazione e portabilità dei dati scrivendo a "
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
            title="Trasparenza",
            slug="trasparenza",
            intro="<p>In ottemperanza alla normativa sulle associazioni sportive "
                  "dilettantistiche, pubblichiamo i documenti del club.</p>",
            body=json.dumps([{
                "type": "rich_text",
                "value": "<h2>Documenti del Club</h2>"
                         "<p>Statuto, bilanci e verbali assembleari sono disponibili "
                         "per la consultazione da parte dei soci e degli enti "
                         "di controllo.</p>"
                         "<h3>Statuto</h3>"
                         "<p>Lo Statuto del Moto Club Aquile Rosse ASD è stato "
                         "approvato nell'assemblea costitutiva del 15 marzo 1987 "
                         "e aggiornato l'ultima volta il 20 gennaio 2024.</p>"
                         "<h3>Bilanci</h3>"
                         "<ul>"
                         "<li>Bilancio Consuntivo 2025 - Approvato il 25/01/2026</li>"
                         "<li>Bilancio Consuntivo 2024 - Approvato il 28/01/2025</li>"
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
            title="Area Stampa",
            slug="stampa",
            intro="<p>Materiale per la stampa e contatti per i media.</p>",
            press_email="stampa@aquilerosse.it",
            press_phone="+39 035 123 4568",
            press_contact="Elena Rizzo - Resp. Comunicazione",
            body=json.dumps([{
                "type": "rich_text",
                "value": "<p>Per richieste stampa, interviste o materiale fotografico "
                         "contattare l'ufficio comunicazione del club.</p>",
            }]),
        )
        parent.add_child(instance=press)
        press.save_revision().publish()
        self.stdout.write("  Created PressPage")

    # ------------------------------------------------------------------
    # Partner Index + Partners
    # ------------------------------------------------------------------

    def _create_partner_index(self, parent):
        if PartnerIndexPage.objects.exists():
            self.stdout.write("  PartnerIndexPage already exists, reusing.")
            return PartnerIndexPage.objects.first()

        partners = PartnerIndexPage(
            title="Partner",
            slug="partner",
            intro="<p>I partner e sponsor che supportano le attività del nostro club.</p>",
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
                "intro": "Centro assistenza multimarca e partner tecnico ufficiale del club.",
                "category": "technical-partner",
                "website": "https://www.example.com/officina-moto-bg",
                "email": "info@officinamotobg.it",
                "phone": "+39 035 987 6543",
                "address": "Via Seriate 42\n24124 Bergamo",
                "contact_city": "Bergamo",
                "is_featured": True,
                "show_on_homepage": True,
                "partnership_start": date(2023, 1, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Officina Moto Bergamo è il partner tecnico ufficiale "
                             "del Moto Club Aquile Rosse. Offre assistenza completa "
                             "su tutte le marche con personale certificato.</p>"
                             "<p>Sconti esclusivi per i soci del club su tagliandi, "
                             "riparazioni e acquisto ricambi.</p>",
                }]),
            },
            {
                "title": "Moto Guzzi Concessionaria Lecco",
                "slug": "moto-guzzi-lecco",
                "intro": "Concessionaria ufficiale Moto Guzzi e main sponsor del club.",
                "category": "main-sponsor",
                "website": "https://www.example.com/guzzi-lecco",
                "email": "info@guzzilecco.it",
                "phone": "+39 0341 123 456",
                "address": "Corso Matteotti 15\n23900 Lecco",
                "contact_city": "Lecco",
                "is_featured": True,
                "show_on_homepage": True,
                "partnership_start": date(2020, 6, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Concessionaria ufficiale Moto Guzzi per la provincia "
                             "di Lecco. Main sponsor del club dal 2020, supporta i "
                             "nostri eventi con demo ride e assistenza tecnica.</p>",
                }]),
            },
            {
                "title": "Bergamo Moto Magazine",
                "slug": "bergamo-moto-magazine",
                "intro": "Rivista online dedicata al motociclismo bergamasco e lombardo.",
                "category": "media-partner",
                "website": "https://www.example.com/bg-moto-mag",
                "email": "redazione@bgmotomag.it",
                "contact_city": "Bergamo",
                "is_featured": False,
                "show_on_homepage": True,
                "partnership_start": date(2022, 3, 1),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Bergamo Moto Magazine è il nostro media partner: "
                             "copre tutti gli eventi del club con articoli, foto "
                             "e video sui propri canali.</p>",
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
    # Navbar
    # ------------------------------------------------------------------

    def _create_navbar(self, home, about, news, events):
        if Navbar.objects.exists():
            self.stdout.write("  Navbar already exists, skipping.")
            return Navbar.objects.first()

        navbar = Navbar.objects.create(
            name="Main Navigation",
            show_search=True,
        )

        items = [
            ("Home", home, False),
            ("Chi Siamo", about, False),
            ("News", news, False),
            ("Eventi", events, False),
        ]

        # Add gallery, contact, partner pages if they exist
        gallery = GalleryPage.objects.first()
        if gallery:
            items.append(("Galleria", gallery, False))
        contact = ContactPage.objects.first()
        if contact:
            items.append(("Contatti", contact, True))

        for i, (label, page, is_cta) in enumerate(items):
            NavbarItem.objects.create(
                navbar=navbar,
                sort_order=i,
                label=label,
                link_page=page,
                is_cta=is_cta,
            )

        self.stdout.write("  Created Navbar with menu items")
        return navbar

    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------

    def _create_footer(self, home, about, news, events):
        if Footer.objects.exists():
            self.stdout.write("  Footer already exists, skipping.")
            return Footer.objects.first()

        footer = Footer.objects.create(
            name="Main Footer",
            description="<p>Moto Club Aquile Rosse ASD - "
                        "Passione, avventura e fratellanza su due ruote dal 1987.</p>",
            copyright_text="© 2026 Moto Club Aquile Rosse ASD. Tutti i diritti riservati.",
            phone="+39 035 123 4567",
            email="info@aquilerosse.it",
            address="Via Borgo Palazzo 22\n24121 Bergamo (BG)\nItalia",
        )

        # Menu items
        pages = [
            ("Chi Siamo", about),
            ("News", news),
            ("Eventi", events),
        ]
        privacy = PrivacyPage.objects.first()
        if privacy:
            pages.append(("Privacy", privacy))
        transparency = TransparencyPage.objects.first()
        if transparency:
            pages.append(("Trasparenza", transparency))

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
    # Site Settings
    # ------------------------------------------------------------------

    def _create_site_settings(self, home_page, navbar, footer):
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(self.style.WARNING("  No default site found!"))
            return

        settings, created = SiteSettings.objects.get_or_create(site=site)
        settings.site_name = "Moto Club Aquile Rosse"
        settings.tagline = "Passione, avventura e fratellanza su due ruote dal 1987"
        settings.description = (
            "Sito ufficiale del Moto Club Aquile Rosse ASD di Bergamo. "
            "Organizzazione di raduni, tour, track day ed eventi benefici "
            "per motociclisti di tutte le marche."
        )
        settings.theme = "velocity"
        settings.color_scheme = self.color_scheme
        settings.navbar = navbar
        settings.footer = footer
        settings.phone = "+39 035 123 4567"
        settings.email = "info@aquilerosse.it"
        settings.address = "Via Borgo Palazzo 22\n24121 Bergamo (BG)\nItalia"
        settings.hours = "Mer/Ven 20:30-23:00, Sab 15:00-18:00"
        settings.facebook_url = "https://www.facebook.com/motoclubaquilerosse"
        settings.instagram_url = "https://www.instagram.com/aquilerosse_mc"
        settings.youtube_url = "https://www.youtube.com/@aquilerossemc"
        settings.map_default_center = "45.6983,9.6773"
        settings.map_default_zoom = 12
        settings.save()

        action = "Created" if created else "Updated"
        self.stdout.write(f"  {action} SiteSettings")

    # ------------------------------------------------------------------
    # Images
    # ------------------------------------------------------------------

    def _download_images(self):
        """Download all images and return a dict keyed by filename stem."""
        self.stdout.write("\nDownloading images from LoremFlickr (Flickr CC)...")
        if Image.objects.filter(file__startswith="original_images/demo_").exists():
            self.stdout.write("  Demo images already exist, skipping downloads.")
            return {}

        images = {}
        for fname, w, h, keywords, title in IMAGE_SPECS:
            stem = Path(fname).stem
            self.stdout.write(f"  Downloading {fname} ({keywords})...")
            try:
                img = _download_image(w, h, keywords, title)
                images[stem] = img
                self.stdout.write(f"    -> Wagtail Image #{img.pk}: {title}")
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"    -> FAILED: {exc}"))
        return images

    def _assign_page_images(self, images):
        """Assign downloaded images to existing CMS pages."""
        if not images:
            return

        self.stdout.write("\nAssigning images to pages...")

        # Homepage hero
        home = HomePage.objects.first()
        if home and "hero_homepage" in images:
            home.hero_image = images["hero_homepage"]
            home.save_revision().publish()
            self.stdout.write("  HomePage hero_image set")

        # About cover
        about = AboutPage.objects.first()
        if about and "hero_about" in images:
            about.cover_image = images["hero_about"]
            about.save_revision().publish()
            self.stdout.write("  AboutPage cover_image set")

        # Events cover images
        event_map = {
            "avviamento-motori-mandello-2026": "event_mandello",
            "moto-guzzi-lands-pisa-2026": "event_pisa",
            "tour-orobie-2026": "event_orobie",
            "track-day-franciacorta-2026": "event_franciacorta",
            "ride-for-children-2026": "event_children",
            "hog-rally-garda-2026": "event_garda",
        }
        for slug, img_key in event_map.items():
            event = EventDetailPage.objects.filter(slug=slug).first()
            if event and img_key in images:
                event.cover_image = images[img_key]
                event.save_revision().publish()
                self.stdout.write(f"  EventDetailPage '{slug}' cover_image set")

        # News cover images
        news_map = {
            "avviamento-motori-2026": "news_mandello",
            "moto-guzzi-lands-pisa": "news_pisa",
            "spring-franken-bayern-treffen": "news_bayern",
            "convenzione-officina-moto-bergamo": "news_officina",
            "preparazione-moto-stagione": "news_manutenzione",
            "assemblea-soci-2026": "news_assemblea",
        }
        for slug, img_key in news_map.items():
            news = NewsPage.objects.filter(slug=slug).first()
            if news and img_key in images:
                news.cover_image = images[img_key]
                news.save_revision().publish()
                self.stdout.write(f"  NewsPage '{slug}' cover_image set")

    # ------------------------------------------------------------------
    # Members
    # ------------------------------------------------------------------

    def _create_members(self, images):
        """Create 5 demo club members with profile photos."""
        self.stdout.write("\nCreating demo members...")

        members_data = [
            {
                "username": "demo_marco",
                "first_name": "Marco",
                "last_name": "Bianchi",
                "email": "marco.bianchi@example.com",
                "display_name": "Marco B.",
                "phone": "+39 333 111 2222",
                "mobile": "+39 333 111 2222",
                "birth_date": date(1985, 3, 15),
                "birth_place": "Bergamo",
                "fiscal_code": "BNCMRC85C15A794X",
                "city": "Bergamo",
                "province": "BG",
                "postal_code": "24121",
                "address": "Via Roma 10",
                "card_number": "AQR-2024-001",
                "membership_date": date(2019, 1, 15),
                "membership_expiry": date(2026, 12, 31),
                "bio": "Motociclista dal 1998. Appassionato di Moto Guzzi V7 e strade di montagna. "
                       "Meccanico hobbista, sempre pronto a dare una mano ai compagni di viaggio.",
                "aid_available": True,
                "aid_radius_km": 30,
                "aid_location_city": "Bergamo",
                "aid_coordinates": "45.6983,9.6773",
                "aid_notes": "Ho attrezzi base e cavi per batteria. Disponibile weekend.",
                "show_in_directory": True,
                "public_profile": True,
                "newsletter": True,
                "image_key": "member_marco",
            },
            {
                "username": "demo_giulia",
                "first_name": "Giulia",
                "last_name": "Ferrara",
                "email": "giulia.ferrara@example.com",
                "display_name": "Giulia F.",
                "phone": "+39 333 222 3333",
                "mobile": "+39 333 222 3333",
                "birth_date": date(1990, 7, 22),
                "birth_place": "Milano",
                "fiscal_code": "FRRGLI90L62F205Y",
                "city": "Seriate",
                "province": "BG",
                "postal_code": "24068",
                "address": "Via Nazionale 45",
                "card_number": "AQR-2024-002",
                "membership_date": date(2021, 3, 1),
                "membership_expiry": date(2026, 12, 31),
                "bio": "Infermiera e motociclista. Guido una Ducati Monster 821. "
                       "Certificata primo soccorso, porto sempre il kit emergenza in moto.",
                "aid_available": True,
                "aid_radius_km": 50,
                "aid_location_city": "Seriate",
                "aid_coordinates": "45.6847,9.7267",
                "aid_notes": "Competenze primo soccorso. Disponibile anche in settimana dopo le 18.",
                "show_in_directory": True,
                "public_profile": True,
                "newsletter": True,
                "image_key": "member_giulia",
            },
            {
                "username": "demo_alessandro",
                "first_name": "Alessandro",
                "last_name": "Rossi",
                "email": "alessandro.rossi@example.com",
                "display_name": "Alex R.",
                "phone": "+39 333 333 4444",
                "mobile": "+39 333 333 4444",
                "birth_date": date(1975, 11, 8),
                "birth_place": "Lecco",
                "fiscal_code": "RSSLSN75S08E507Z",
                "city": "Lecco",
                "province": "LC",
                "postal_code": "23900",
                "address": "Corso Matteotti 88",
                "card_number": "AQR-2024-003",
                "membership_date": date(1987, 3, 15),
                "membership_expiry": date(2026, 12, 31),
                "bio": "Socio fondatore del club. Ex meccanico Moto Guzzi a Mandello. "
                       "Ho un furgone attrezzato per trasporto moto. Guido una V85 TT.",
                "aid_available": True,
                "aid_radius_km": 100,
                "aid_location_city": "Lecco",
                "aid_coordinates": "45.8566,9.3977",
                "aid_notes": "Furgone con rampa per trasporto moto. Meccanica avanzata Guzzi. "
                             "Disponibile quasi sempre, chiamare al cellulare.",
                "show_in_directory": True,
                "public_profile": True,
                "newsletter": True,
                "image_key": "member_alessandro",
            },
            {
                "username": "demo_chiara",
                "first_name": "Chiara",
                "last_name": "Fontana",
                "email": "chiara.fontana@example.com",
                "display_name": "Chiara F.",
                "phone": "+39 333 444 5555",
                "mobile": "+39 333 444 5555",
                "birth_date": date(1988, 5, 30),
                "birth_place": "Brescia",
                "fiscal_code": "FNTCHR88E70B157W",
                "city": "Treviglio",
                "province": "BG",
                "postal_code": "24047",
                "address": "Via Cavour 12",
                "card_number": "AQR-2024-004",
                "membership_date": date(2020, 6, 1),
                "membership_expiry": date(2026, 12, 31),
                "bio": "Commercialista e tesoriere del club. Guido una BMW R 1250 GS. "
                       "Viaggio spesso in solitaria verso i passi alpini.",
                "aid_available": True,
                "aid_radius_km": 25,
                "aid_location_city": "Treviglio",
                "aid_coordinates": "45.5200,9.5900",
                "aid_notes": "Posso ospitare motociclisti di passaggio (garage e camera ospiti).",
                "show_in_directory": True,
                "public_profile": True,
                "newsletter": True,
                "image_key": "member_chiara",
            },
            {
                "username": "demo_roberto",
                "first_name": "Roberto",
                "last_name": "Colombo",
                "email": "roberto.colombo@example.com",
                "display_name": "Roberto C.",
                "phone": "+39 333 555 6666",
                "mobile": "+39 333 555 6666",
                "birth_date": date(1970, 9, 3),
                "birth_place": "Bergamo",
                "fiscal_code": "CLMRRT70P03A794V",
                "city": "Bergamo",
                "province": "BG",
                "postal_code": "24122",
                "address": "Via Borgo Palazzo 22",
                "card_number": "AQR-2024-005",
                "membership_date": date(2015, 1, 1),
                "membership_expiry": date(2026, 12, 31),
                "bio": "Presidente del moto club. 40 anni in sella, collezionista Guzzi d'epoca. "
                       "Organizzo i tour annuali del club su percorsi selezionati.",
                "aid_available": True,
                "aid_radius_km": 40,
                "aid_location_city": "Bergamo",
                "aid_coordinates": "45.6983,9.6773",
                "aid_notes": "Ampia esperienza meccanica su Guzzi classiche e moderne. "
                             "Attrezzi professionali in sede club.",
                "show_in_directory": True,
                "public_profile": True,
                "newsletter": True,
                "image_key": "member_roberto",
            },
        ]

        members = []
        for data in members_data:
            image_key = data.pop("image_key")

            if ClubUser.objects.filter(username=data["username"]).exists():
                member = ClubUser.objects.get(username=data["username"])
                self.stdout.write(f"  Member '{data['username']}' already exists, reusing.")
                members.append(member)
                continue

            member = ClubUser(**data)
            member.set_password("demo2026!")

            if image_key in images:
                member.photo = images[image_key]

            member.save()
            members.append(member)
            self.stdout.write(
                f"  Created member: {data['first_name']} {data['last_name']} "
                f"({data['username']})"
            )

        return members

    # ------------------------------------------------------------------
    # Mutual-Aid Requests
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
                    "Moto Guzzi V7 in panne sulla SS38 tra Lecco e Colico, km 42. "
                    "La moto non parte, sembra un problema elettrico. "
                    "Sono al parcheggio del ristorante La Pergola."
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
                    "Foratura pneumatico posteriore BMW R 1250 GS sulla strada "
                    "del Passo della Presolana. Non ho kit riparazione tubeless. "
                    "Sono al Rifugio Magnolini."
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
                    "Rimasta senza benzina sulla SP671 tra Clusone e Bergamo. "
                    "Il distributore piu vicino era chiuso (domenica sera). "
                    "Sono al bar Sport di Gazzaniga."
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
                    "Guzzi California d'epoca con rottura cambio al ritorno dal "
                    "raduno di Mandello. Serve trasporto moto con furgone fino "
                    "alla sede club a Bergamo (~60km)."
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
                    "Di ritorno dal tour delle Dolomiti, problema alla catena "
                    "della V85 TT vicino a Treviglio. La moto si muove piano "
                    "ma non posso fare altri 80km fino a Lecco stasera. "
                    "Cercasi garage e un divano per la notte."
                ),
                "location": "Treviglio centro (BG)",
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

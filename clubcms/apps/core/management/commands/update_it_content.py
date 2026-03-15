"""
Management command to update Italian (IT) translated pages with proper
Italian content.

When the site is populated with populate_demo_en, the IT pages are created
as copies of the English pages (via copy_for_translation) and retain English
text in all content fields. This command overwrites those fields with the
correct Italian translations.

Usage:
    python manage.py update_it_content
    docker compose exec web python manage.py update_it_content
"""

import json
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from wagtail.models import Locale, Page

from apps.federation.models import FederationInfoPage
from apps.website.models import (
    AboutPage,
    BoardPage,
    ContactPage,
    EventDetailPage,
    EventsPage,
    GalleryPage,
    HomePage,
    MembershipPlansPage,
    NewsIndexPage,
    NewsPage,
    PartnerIndexPage,
    PartnerPage,
    PressPage,
    PrivacyPage,
    TransparencyPage,
)


class Command(BaseCommand):
    help = "Update Italian translated pages with proper Italian content"

    def handle(self, *args, **options):
        try:
            it = Locale.objects.get(language_code="it")
        except Locale.DoesNotExist:
            self.stdout.write(self.style.ERROR("Italian locale not found!"))
            return

        self.stdout.write("Updating Italian page content...\n")

        self._update_home_page(it)
        self._update_about_page(it)
        self._update_board_page(it)
        self._update_news_index(it)
        self._update_events_page(it)
        self._update_gallery_page(it)
        self._update_contact_page(it)
        self._update_privacy_page(it)
        self._update_transparency_page(it)
        self._update_press_page(it)
        self._update_membership_plans_page(it)
        self._update_federation_info_page(it)
        self._update_partner_index(it)
        self._update_partner_pages(it)
        self._update_news_articles(it)
        self._update_event_detail_pages(it)

        self.stdout.write(self.style.SUCCESS(
            "\nItalian content updated successfully!"
        ))

    def _save_and_publish(self, page, label):
        page.save_revision().publish()
        self.stdout.write(f"  Updated: {label}")

    # ------------------------------------------------------------------
    # Home Page
    # ------------------------------------------------------------------

    def _update_home_page(self, locale):
        page = HomePage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  HomePage (IT) not found"))
            return

        page.title = "Moto Club Aquile Rosse"
        page.hero_title = "Moto Club Aquile Rosse"
        page.hero_subtitle = "Passione, avventura e fratellanza su due ruote dal 1987"
        page.primary_cta_text = "Prossimi Eventi"
        page.secondary_cta_text = "Diventa Socio"
        page.body = json.dumps([
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
                    "button_url": "/diventa-socio/",
                    "style": "primary",
                },
            },
        ])
        self._save_and_publish(page, "HomePage")

    # ------------------------------------------------------------------
    # About Page
    # ------------------------------------------------------------------

    def _update_about_page(self, locale):
        page = AboutPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  AboutPage (IT) not found"))
            return

        page.title = "Chi Siamo"
        page.intro = (
            "<p>Il Moto Club Aquile Rosse nasce nel 1987 a Bergamo dall'idea di "
            "un gruppo di appassionati motociclisti che volevano condividere la "
            "passione per le due ruote in un contesto di amicizia e solidarietà.</p>"
            "<p>Oggi il club conta oltre 250 soci iscritti, con una sede sociale "
            "in Via Borgo Palazzo 22, Bergamo. Siamo affiliati alla FMI (Federazione "
            "Motociclistica Italiana) e organizziamo ogni anno più di 50 eventi "
            "tra raduni, tour, giornate in pista e iniziative benefiche.</p>"
        )
        page.body = json.dumps([
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
                    "title": "Momenti Chiave",
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
        ])
        self._save_and_publish(page, "AboutPage")

    # ------------------------------------------------------------------
    # Board Page
    # ------------------------------------------------------------------

    def _update_board_page(self, locale):
        page = BoardPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  BoardPage (IT) not found"))
            return

        page.title = "Consiglio Direttivo"
        page.intro = "<p>Il Consiglio Direttivo guida il club con passione e dedizione.</p>"
        page.body = json.dumps([
            {
                "type": "team_grid",
                "value": {
                    "columns": 3,
                    "members": [
                        {"name": "Roberto Colombo", "role": "Presidente",
                         "bio": "Motociclista da 40 anni, guida il club dal 2015. "
                                "Appassionato di Moto moto e viaggi lungo raggio."},
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
        ])
        self._save_and_publish(page, "BoardPage")

    # ------------------------------------------------------------------
    # News Index
    # ------------------------------------------------------------------

    def _update_news_index(self, locale):
        page = NewsIndexPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  NewsIndexPage (IT) not found"))
            return

        page.title = "Notizie"
        page.intro = "<p>Tutte le novità dal mondo del Moto Club Aquile Rosse.</p>"
        self._save_and_publish(page, "NewsIndexPage")

    # ------------------------------------------------------------------
    # Events Page
    # ------------------------------------------------------------------

    def _update_events_page(self, locale):
        page = EventsPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  EventsPage (IT) not found"))
            return

        page.title = "Eventi"
        page.intro = "<p>Tutti gli eventi organizzati e supportati dal Moto Club Aquile Rosse.</p>"
        self._save_and_publish(page, "EventsPage")

    # ------------------------------------------------------------------
    # Gallery Page
    # ------------------------------------------------------------------

    def _update_gallery_page(self, locale):
        page = GalleryPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  GalleryPage (IT) not found"))
            return

        page.title = "Galleria"
        page.intro = "<p>Le foto più belle dai nostri eventi, tour e raduni.</p>"
        self._save_and_publish(page, "GalleryPage")

    # ------------------------------------------------------------------
    # Contact Page
    # ------------------------------------------------------------------

    def _update_contact_page(self, locale):
        page = ContactPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  ContactPage (IT) not found"))
            return

        page.title = "Contatti"
        page.hero_badge = "Siamo qui per te"
        page.intro = "<p>Hai domande? Vuoi sapere di più sul club? Scrivici!</p>"
        page.form_title = "Inviaci un Messaggio"
        page.success_message = "<p>Grazie per il tuo messaggio! Ti risponderemo entro 48 ore.</p>"
        page.membership_title = "Diventa Socio"
        page.membership_description = (
            "Unisciti alla nostra comunità di oltre 250 motociclisti. "
            "Accesso a tutti gli eventi, sconti presso i partner, "
            "assicurazione e assistenza stradale inclusi."
        )
        page.membership_price = "Quota annuale €80"
        page.membership_cta_text = "Iscriviti Ora"
        self._save_and_publish(page, "ContactPage")

    # ------------------------------------------------------------------
    # Privacy Page
    # ------------------------------------------------------------------

    def _update_privacy_page(self, locale):
        page = PrivacyPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  PrivacyPage (IT) not found"))
            return

        page.title = "Privacy Policy"
        page.body = json.dumps([{
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
        }])
        self._save_and_publish(page, "PrivacyPage")

    # ------------------------------------------------------------------
    # Transparency Page
    # ------------------------------------------------------------------

    def _update_transparency_page(self, locale):
        page = TransparencyPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  TransparencyPage (IT) not found"))
            return

        page.title = "Trasparenza"
        page.intro = (
            "<p>In ottemperanza alla normativa sulle associazioni sportive "
            "dilettantistiche, pubblichiamo i documenti del club.</p>"
        )
        page.body = json.dumps([{
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
        }])
        self._save_and_publish(page, "TransparencyPage")

    # ------------------------------------------------------------------
    # Press Page
    # ------------------------------------------------------------------

    def _update_press_page(self, locale):
        page = PressPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  PressPage (IT) not found"))
            return

        page.title = "Area Stampa"
        page.intro = "<p>Materiale per la stampa e contatti per i media.</p>"
        page.press_contact = "Elena Rizzo - Resp. Comunicazione"
        page.body = json.dumps([{
            "type": "rich_text",
            "value": "<p>Per richieste stampa, interviste o materiale fotografico "
                     "contattare l'ufficio comunicazione del club.</p>",
        }])
        self._save_and_publish(page, "PressPage")

    # ------------------------------------------------------------------
    # Membership Plans Page
    # ------------------------------------------------------------------

    def _update_membership_plans_page(self, locale):
        page = MembershipPlansPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  MembershipPlansPage (IT) not found"))
            return

        page.title = "Diventa Socio"
        page.intro = (
            "<p>Scegli il piano di tesseramento più adatto alle tue esigenze. "
            "Combina più prodotti per personalizzare la tua esperienza.</p>"
        )
        self._save_and_publish(page, "MembershipPlansPage")

    # ------------------------------------------------------------------
    # Federation Info Page
    # ------------------------------------------------------------------

    def _update_federation_info_page(self, locale):
        page = FederationInfoPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  FederationInfoPage (IT) not found"))
            return

        page.title = "Federazione"
        page.intro = (
            "<p>La nostra rete di club partner condivide eventi, iniziative "
            "e opportunità per tutti i soci. Grazie alla federazione puoi "
            "scoprire cosa succede nei club amici, esplorare i loro eventi "
            "e partecipare alle iniziative della rete — tutto dalla "
            "piattaforma del tuo club, in totale sicurezza.</p>"
        )
        page.how_it_works = json.dumps([{
            "type": "step",
            "value": {
                "title": "Come funziona la Federazione",
                "items": [
                    {"year": "1", "title": "Scopri i club partner",
                     "description": "<p>Naviga la lista dei club federati e scopri "
                                    "le loro attività, la loro storia e i servizi "
                                    "che offrono ai soci.</p>"},
                    {"year": "2", "title": "Esplora gli eventi condivisi",
                     "description": "<p>Consulta gli eventi pubblicati dai club "
                                    "partner. Puoi filtrarli per club, cercarli "
                                    "per nome e vedere tutti i dettagli.</p>"},
                    {"year": "3", "title": "Esprimi il tuo interesse",
                     "description": "<p>Segna se sei interessato, indeciso o se "
                                    "partecipi sicuramente. Il club organizzatore "
                                    "riceve solo conteggi anonimi.</p>"},
                    {"year": "4", "title": "Commenta con i soci",
                     "description": "<p>Discuti gli eventi con gli altri soci del "
                                    "tuo club. I commenti sono privati e non vengono "
                                    "mai condivisi con il club partner.</p>"},
                ],
            },
        }])
        page.faq = json.dumps([{
            "type": "faq",
            "value": {
                "title": "Domande frequenti sulla Federazione",
                "items": [
                    {"question": "Cos\u0027è la federazione dei club?",
                     "answer": "<p>È una rete volontaria di club che condividono "
                               "eventi e iniziative attraverso un protocollo sicuro. "
                               "Ogni club mantiene la propria completa autonomia.</p>"},
                    {"question": "Devo pagare per accedere agli eventi federati?",
                     "answer": "<p>No. L\u0027accesso alla lista degli eventi partner "
                               "è incluso nella tessera associativa. L\u0027iscrizione "
                               "a un evento partner segue le regole del club "
                               "organizzatore.</p>"},
                    {"question": "I miei dati personali vengono condivisi?",
                     "answer": "<p>No. La federazione scambia solo dati sugli eventi "
                               "e conteggi aggregati anonimi. Nessun dato personale "
                               "viene mai trasmesso ai club partner.</p>"},
                    {"question": "Come viene garantita la sicurezza?",
                     "answer": "<p>Ogni club partner dispone di chiavi API univoche. "
                               "Le comunicazioni avvengono tramite HTTPS con "
                               "autenticazione HMAC. I dati vengono validati e "
                               "sanificati prima dell\u0027importazione.</p>"},
                    {"question": "Posso partecipare agli eventi di un club partner?",
                     "answer": "<p>Puoi esprimere interesse dalla nostra piattaforma. "
                               "Per l\u0027iscrizione effettiva, segui le indicazioni "
                               "sul sito del club organizzatore tramite il link nella "
                               "pagina dell\u0027evento.</p>"},
                    {"question": "I commenti sono visibili ai club partner?",
                     "answer": "<p>No. I commenti sugli eventi partner sono visibili "
                               "solo ai soci del nostro club. Sono uno strumento di "
                               "discussione interna.</p>"},
                ],
            },
        }])
        page.body = json.dumps([{
            "type": "rich_text",
            "value": (
                "<h2>Vantaggi della federazione</h2>"
                "<p>Far parte di una rete federata di club significa ampliare "
                "le opportunità per i soci senza rinunciare all\u0027autonomia:</p>"
                "<ul>"
                "<li><strong>Più eventi</strong> — Accedi a un calendario "
                "condiviso con decine di appuntamenti dai club partner.</li>"
                "<li><strong>Nuove amicizie</strong> — Conosci appassionati "
                "di altri club con interessi simili ai tuoi.</li>"
                "<li><strong>Privacy garantita</strong> — I tuoi dati personali "
                "restano nel nostro club.</li>"
                "<li><strong>Discussione riservata</strong> — Commenta e "
                "organizzati con i soci del tuo club in modo privato.</li>"
                "</ul>"
                "<p>La federazione è un progetto aperto: qualsiasi club può "
                "aderire rispettando il protocollo tecnico e i principi di "
                "trasparenza e privacy.</p>"
            ),
        }])
        page.cta_text = "Scopri gli eventi partner"
        page.cta_url = "/eventi/partner/"
        self._save_and_publish(page, "FederationInfoPage")

    # ------------------------------------------------------------------
    # Partner Index
    # ------------------------------------------------------------------

    def _update_partner_index(self, locale):
        page = PartnerIndexPage.objects.filter(locale=locale).first()
        if not page:
            self.stdout.write(self.style.WARNING("  PartnerIndexPage (IT) not found"))
            return

        page.title = "Partner"
        page.intro = "<p>I partner e sponsor che supportano le attività del nostro club.</p>"
        self._save_and_publish(page, "PartnerIndexPage")

    # ------------------------------------------------------------------
    # Partner Pages
    # ------------------------------------------------------------------

    def _update_partner_pages(self, locale):
        partners_it = {
            "officina-moto-bergamo": {
                "intro": "Centro assistenza multimarca e partner tecnico ufficiale del club.",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Officina Moto Bergamo è il partner tecnico ufficiale "
                             "del Moto Club Aquile Rosse. Offre assistenza completa "
                             "su tutte le marche con personale certificato.</p>"
                             "<p>Sconti esclusivi per i soci del club su tagliandi, "
                             "riparazioni e acquisto ricambi.</p>",
                }]),
            },
            "concessionaria-lecco": {
                "intro": "Concessionaria di moto e main sponsor del club.",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Concessionaria ufficiale Moto moto per la provincia "
                             "di Lecco. Main sponsor del club dal 2020, supporta i "
                             "nostri eventi con demo ride e assistenza tecnica.</p>",
                }]),
            },
            "bergamo-moto-magazine": {
                "intro": "Rivista online dedicata al motociclismo bergamasco e lombardo.",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Bergamo Moto Magazine è il nostro media partner: "
                             "copre tutti gli eventi del club con articoli, foto "
                             "e video sui propri canali.</p>",
                }]),
            },
        }

        for slug, data in partners_it.items():
            page = PartnerPage.objects.filter(locale=locale, slug=slug).first()
            if not page:
                self.stdout.write(self.style.WARNING(
                    f"  PartnerPage '{slug}' (IT) not found"
                ))
                continue
            for field, value in data.items():
                setattr(page, field, value)
            self._save_and_publish(page, f"PartnerPage: {slug}")

    # ------------------------------------------------------------------
    # News Articles
    # ------------------------------------------------------------------

    def _update_news_articles(self, locale):
        articles_it = {
            "avviamento-motori-2026": {
                "title": "Avviamento Motori 2026: Si Riparte da Mandello!",
                "intro": (
                    "Il tradizionale raduno di apertura stagione torna a Mandello del Lario "
                    "con novità e sorprese per tutti gli appassionati di moto."
                ),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Come ogni anno, la stagione motociclistica si apre "
                             "con il tradizionale <strong>Avviamento Motori</strong> "
                             "a Mandello del Lario, la patria della Moto moto.</p>"
                             "<p>L'evento, organizzato dal Moto Club Le Aquile di Mandello "
                             "prevede un programma ricco "
                             "di attività: dalla sfilata lungo il lago alle visite guidate "
                             "al Museo Moto moto, fino alla cena sociale presso il "
                             "Ristorante Il Griso.</p>"
                             "<h3>Programma</h3>"
                             "<ul>"
                             "<li>Ore 9:00 - Ritrovo presso Piazza Garibaldi</li>"
                             "<li>Ore 10:30 - Sfilata lungo il Lago di Como</li>"
                             "<li>Ore 12:30 - Pranzo sociale</li>"
                             "<li>Ore 15:00 - Visita al museo della moto</li>"
                             "<li>Ore 18:00 - Aperitivo e premiazioni</li>"
                             "</ul>"
                             "<p>Il Moto Club Aquile Rosse parteciperà con una "
                             "delegazione di 30 soci. Le iscrizioni sono aperte "
                             "fino al 15 marzo.</p>",
                }]),
            },
            "moto-lands-pisa": {
                "title": "1° Moto Lands of Pisa: Nuovo Evento in Toscana",
                "intro": (
                    "Nasce un nuovo raduno motociclistico a Pontedera, nella terra dove "
                    "nacque la Piaggio e a due passi dalla torre pendente."
                ),
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Grandi novità dal panorama dei raduni motociclistici "
                             "italiani: è stato annunciato il <strong>1° Moto moto "
                             "Lands of Pisa</strong>, un evento che si terrà a Pontedera "
                             "(PI) nella primavera 2026.</p>"
                             "<p>L'evento è organizzato dal Moto Club Terre di Pisa "
                             "in collaborazione con la rete moto Days e promette "
                             "un weekend all'insegna della cultura motociclistica "
                             "toscana, con percorsi tra le colline pisane, degustazioni "
                             "di prodotti locali e un raduno statico nel centro storico.</p>"
                             "<p>Il nostro club sta già organizzando una trasferta di "
                             "gruppo. Chi è interessato può contattare il responsabile "
                             "eventi Davide Marchetti.</p>",
                }]),
            },
            "spring-franken-bayern-treffen": {
                "title": "Resoconto: Spring Franken Bayern Treffen 2026",
                "intro": (
                    "Otto soci del club hanno partecipato al raduno primaverile "
                    "in Baviera. Ecco il racconto dell'esperienza."
                ),
                "body": json.dumps([{
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
                             "<p>Prossima trasferta internazionale: il moto Days 2026 "
                             "in Sudafrica!</p>",
                }]),
            },
            "convenzione-officina-moto-bergamo": {
                "title": "Nuova Convenzione con Officina Moto Bergamo",
                "intro": (
                    "Siglata una convenzione con l'Officina Moto Bergamo per "
                    "sconti su tagliandi e riparazioni per tutti i soci."
                ),
                "body": json.dumps([{
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
                }]),
            },
            "preparazione-moto-stagione": {
                "title": "Guida alla Preparazione della Moto per la Stagione",
                "intro": (
                    "I consigli del nostro meccanico di fiducia per rimettere "
                    "la moto in forma dopo la pausa invernale."
                ),
                "body": json.dumps([{
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
                }]),
            },
            "assemblea-soci-2026": {
                "title": "Assemblea Soci 2026: Approvato il Bilancio",
                "intro": (
                    "L'assemblea annuale ha approvato all'unanimità il bilancio "
                    "e il programma eventi per il nuovo anno."
                ),
                "body": json.dumps([{
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
                }]),
            },
        }

        for slug, data in articles_it.items():
            page = NewsPage.objects.filter(locale=locale, slug=slug).first()
            if not page:
                self.stdout.write(self.style.WARNING(
                    f"  NewsPage '{slug}' (IT) not found"
                ))
                continue
            for field, value in data.items():
                setattr(page, field, value)
            self._save_and_publish(page, f"NewsPage: {slug}")

    # ------------------------------------------------------------------
    # Event Detail Pages
    # ------------------------------------------------------------------

    def _update_event_detail_pages(self, locale):
        events_it = {
            "avviamento-motori-mandello-2026": {
                "title": "Avviamento Motori 2026 - Mandello del Lario",
                "intro": "Il tradizionale raduno di apertura stagione a Mandello del Lario.",
                "location_name": "Piazza Garibaldi, Mandello del Lario",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Partecipa all'<strong>Avviamento Motori 2026</strong>, "
                             "il raduno che apre ufficialmente la stagione motociclistica "
                             "sulle sponde del Lago di Como.</p>"
                             "<p>Organizzato dal Moto Club Le Aquile di Mandello in "
                             "collaborazione con la rete moto Days, l'evento è aperto "
                             "a tutte le marche e modelli.</p>"
                             "<h3>Cosa Include</h3>"
                             "<ul>"
                             "<li>Sfilata panoramica lungo il Lago di Como</li>"
                             "<li>Pranzo sociale (incluso nella quota)</li>"
                             "<li>Visita al Museo Moto moto</li>"
                             "<li>Gadget commemorativo</li>"
                             "</ul>",
                }]),
            },
            "moto-lands-pisa-2026": {
                "title": "1° Moto Lands of Pisa",
                "intro": "Primo raduno guzzista nella terra di Pontedera, tra le colline toscane.",
                "location_name": "Centro Storico, Pontedera",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Un weekend nella splendida Toscana per il primo "
                             "<strong>Moto moto Lands of Pisa</strong>.</p>"
                             "<p>Il programma prevede tour guidati nelle colline "
                             "pisane, visita al Museo Piaggio di Pontedera, "
                             "degustazione di prodotti tipici e raduno statico "
                             "in piazza con esposizione di moto d'epoca e moderne.</p>",
                }]),
            },
            "tour-orobie-2026": {
                "title": "Tour delle Orobie - Giornata Sociale",
                "intro": "Uscita giornaliera tra le valli bergamasche con sosta pranzo in rifugio.",
                "location_name": "Sede Club, Bergamo",
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
            "track-day-franciacorta-2026": {
                "title": "Track Day - Autodromo di Franciacorta",
                "intro": "Giornata in pista all'Autodromo di Franciacorta con istruttori professionisti.",
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
            "ride-for-children-2026": {
                "title": "Beneficenza: Ride for Children",
                "intro": "Motogiro benefico a favore dell'Ospedale dei Bambini di Bergamo.",
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
            "moto-rally-garda-2026": {
                "title": "Moto Rally Garda 2026",
                "intro": "Raduno moto sul Lago di Garda con parata e concerti.",
                "body": json.dumps([{
                    "type": "rich_text",
                    "value": "<p>Il <strong>Moto Rally Garda</strong> è uno dei più grandi "
                             "raduni moto del Nord Italia, organizzato dal "
                             "Moto Club Lago di Garda in collaborazione con il concessionario locale."
                             "</p>"
                             "<p>Quattro giorni di moto, musica, food truck e la celebre "
                             "Thunder Parade lungo le sponde del lago. Il nostro club "
                             "partecipa come ospite con uno stand informativo.</p>",
                }]),
            },
        }

        for slug, data in events_it.items():
            page = EventDetailPage.objects.filter(locale=locale, slug=slug).first()
            if not page:
                self.stdout.write(self.style.WARNING(
                    f"  EventDetailPage '{slug}' (IT) not found"
                ))
                continue
            for field, value in data.items():
                setattr(page, field, value)
            self._save_and_publish(page, f"EventDetailPage: {slug}")

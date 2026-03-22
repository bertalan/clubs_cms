"""
Italian demo data for ClubCMS.

This dictionary contains ALL data needed to populate a complete
standalone Italian-language site.  It is consumed by build_demo_db
to produce ``fixtures/demo/demo_it.sqlite3``, which in turn is
read by ``load_demo --lang it``.
"""
import json

from apps.core.demo.schema import TRANSLATION_KEYS as TK

# ---------------------------------------------------------------------------
# Helper — compact StreamField serialiser
# ---------------------------------------------------------------------------

def _sf(*blocks):
    """Return a JSON string for StreamField blocks."""
    return json.dumps(list(blocks), ensure_ascii=False)


def _rt(html):
    """Rich-text block."""
    return {"type": "rich_text", "value": html}


def _stats(items):
    return {"type": "stats", "value": {"items": items}}


def _cta(title, text, button_text, button_url, style="primary"):
    return {
        "type": "cta",
        "value": {
            "title": title,
            "text": text,
            "button_text": button_text,
            "button_url": button_url,
            "style": style,
        },
    }


def _timeline(title, items):
    return {"type": "timeline", "value": {"title": title, "items": items}}


def _team_grid(columns, members):
    return {"type": "team_grid", "value": {"columns": columns, "members": members}}


def _step(title, items):
    return {"type": "step", "value": {"title": title, "items": items}}


def _faq_block(title, items):
    return {"type": "faq", "value": {"title": title, "items": items}}


# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------

DATA = {
    # ==================================================================
    # META
    # ==================================================================
    "meta": {
        "language": "it",
        "site_name": "Moto Club Aquile Rosse",
        # Slug references used by the loader for image assignment
        "slug_about": "chi-siamo",
        "slug_contact": "contatti",
        "slug_event_mandello": "avviamento-motori-mandello-2026",
        "slug_event_pisa": "moto-lands-pisa-2026",
        "slug_event_orobie": "tour-orobie-2026",
        "slug_event_franciacorta": "track-day-franciacorta-2026",
        "slug_event_children": "ride-for-children-2026",
        "slug_event_garda": "moto-rally-garda-2026",
        "slug_news_kickoff": "avviamento-motori-2026",
        "slug_news_pisa": "moto-lands-pisa",
        "slug_news_bayern": "spring-franken-bayern-treffen",
        "slug_news_workshop": "convenzione-officina-moto-bergamo",
        "slug_news_seasonal": "preparazione-moto-stagione",
        "slug_news_assembly": "assemblea-soci-2026",
    },

    # ==================================================================
    # COLOR SCHEME
    # ==================================================================
    "color_scheme": [
        {
            "name": "Rosso Corsa",
            "primary_color": "#B91C1C",
            "secondary_color": "#F59E0B",
            "accent": "#1E40AF",
            "surface": "#F9FAFB",
            "surface_alt": "#FFFFFF",
            "text_primary": "#111827",
            "text_muted": "#6B7280",
            "is_dark_mode": False,
        },
    ],

    # ==================================================================
    # CATEGORIES
    # ==================================================================
    "categories": [
        # News
        {"cat_type": "news", "name": "Notizie Club",       "slug": "club-news",        "color": "#B91C1C", "description": "Notizie sulle attività e comunicazioni del club", "icon": "", "sort_order": 0},
        {"cat_type": "news", "name": "Resoconti eventi",   "slug": "events-recap",     "color": "#059669", "description": "Cronache e foto dagli eventi passati",            "icon": "", "sort_order": 1},
        {"cat_type": "news", "name": "Mondo moto",         "slug": "motorcycle-world", "color": "#7C3AED", "description": "Notizie dal mondo del motociclismo e dell\u2019industria", "icon": "", "sort_order": 2},
        {"cat_type": "news", "name": "Tecnica",            "slug": "technical",        "color": "#2563EB", "description": "Articoli tecnici, recensioni e consigli di manutenzione", "icon": "", "sort_order": 3},
        # Events
        {"cat_type": "event", "name": "Rally & Raduno",    "slug": "rally",          "color": "", "description": "", "icon": "rally",      "sort_order": 0},
        {"cat_type": "event", "name": "Gita in moto",      "slug": "touring",        "color": "", "description": "", "icon": "motorcycle",  "sort_order": 1},
        {"cat_type": "event", "name": "Incontro sociale",  "slug": "social-meeting", "color": "", "description": "", "icon": "meeting",     "sort_order": 2},
        {"cat_type": "event", "name": "Track Day",         "slug": "track-day",      "color": "", "description": "", "icon": "race",        "sort_order": 3},
        {"cat_type": "event", "name": "Gita benefica",     "slug": "charity-ride",   "color": "", "description": "", "icon": "charity",     "sort_order": 4},
        # Partners
        {"cat_type": "partner", "name": "Sponsor principale",  "slug": "main-sponsor",      "color": "", "description": "", "icon": "", "sort_order": 1},
        {"cat_type": "partner", "name": "Partner tecnico",     "slug": "technical-partner",  "color": "", "description": "", "icon": "", "sort_order": 2},
        {"cat_type": "partner", "name": "Partner media",       "slug": "media-partner",      "color": "", "description": "", "icon": "", "sort_order": 3},
    ],

    # ==================================================================
    # PRODUCTS
    # ==================================================================
    "products": [
        {"name": "Tessera Socio Ordinario",    "slug": "socio-ordinario",    "translation_key": "standard",  "description": "Tessera associativa annuale con diritto di voto e partecipazione eventi.",          "price": "50.00",  "grants_vote": True,  "grants_events": True,  "grants_upload": True,  "grants_discount": False, "discount_percent": 0,  "sort_order": 1},
        {"name": "Tessera Socio Sostenitore",  "slug": "socio-sostenitore",  "translation_key": "supporter", "description": "Tessera sostenitore con sconto eventi e accesso gallery.",                         "price": "30.00",  "grants_vote": False, "grants_events": True,  "grants_upload": False, "grants_discount": True,  "discount_percent": 10, "sort_order": 2},
        {"name": "Tessera Socio Premium",      "slug": "socio-premium",      "translation_key": "premium",   "description": "Tessera premium con tutti i privilegi e 20% sconto eventi.",                       "price": "100.00", "grants_vote": True,  "grants_events": True,  "grants_upload": True,  "grants_discount": True,  "discount_percent": 20, "sort_order": 3},
    ],

    # ==================================================================
    # TESTIMONIALS
    # ==================================================================
    "testimonials": [
        {"quote": "Far parte di questo club ha cambiato il mio modo di vivere la moto. Le uscite domenicali e i raduni sono momenti indimenticabili.", "author_name": "Marco Bianchi", "author_role": "Socio dal 2019", "featured": True},
        {"quote": "L\u2019assistenza reciproca tra soci è straordinaria. Una volta rimasto in panne sullo Stelvio, in 30 minuti avevo già aiuto.", "author_name": "Giulia Ferrara", "author_role": "Socia dal 2021", "featured": True},
        {"quote": "I tour organizzati dal club sono sempre perfetti: percorsi mozzafiato, soste gastronomiche e ottima compagnia.", "author_name": "Alessandro Rossi", "author_role": "Socio fondatore", "featured": False},
    ],

    # ==================================================================
    # FAQs
    # ==================================================================
    "faqs": [
        {"question": "Come posso iscrivermi al Moto Club?", "answer": "<p>Puoi iscriverti compilando il modulo di registrazione online sul nostro sito, oppure presentandoti presso la sede sociale durante gli orari di apertura (Mercoledì e Venerdì 20:30\u201323:00, Sabato 15:00\u201318:00). È necessario un documento di identità valido e il pagamento della quota associativa.</p>", "category": "Iscrizione", "sort_order": 1},
        {"question": "Quali sono i costi della tessera socio?", "answer": "<p>Offriamo tre tipologie di tessera:</p><ul><li><strong>Socio Ordinario</strong>: \u20ac50/anno \u2013 diritto di voto, eventi, upload gallery</li><li><strong>Socio Sostenitore</strong>: \u20ac30/anno \u2013 eventi, 10% sconto</li><li><strong>Socio Premium</strong>: \u20ac100/anno \u2013 tutti i privilegi, 20% sconto eventi</li></ul>", "category": "Iscrizione", "sort_order": 2},
        {"question": "Posso partecipare agli eventi senza essere socio?", "answer": "<p>Alcuni eventi sono aperti anche ai non soci (come il Ride for Children). Per la maggior parte degli eventi organizzati dal club è necessaria la tessera socio in corso di validità. I non soci possono partecipare come ospiti per un massimo di 2 uscite prima di dover effettuare l\u2019iscrizione.</p>", "category": "Eventi", "sort_order": 3},
        {"question": "Come funziona il mutuo soccorso?", "answer": "<p>Il sistema di mutuo soccorso permette ai soci di richiedere e offrire assistenza in caso di guasto o emergenza stradale. Ogni socio può indicare nel proprio profilo le competenze (meccanica, trasporto, logistica) e il raggio di disponibilità. In caso di necessità, il sistema notifica i soci disponibili nella zona.</p>", "category": "Servizi", "sort_order": 4},
    ],

    # ==================================================================
    # PHOTO TAGS
    # ==================================================================
    "photo_tags": [
        {"name": "Raduno",      "slug": "raduno"},
        {"name": "Tour",        "slug": "tour"},
        {"name": "Track Day",   "slug": "track-day"},
        {"name": "Sociale",     "slug": "sociale"},
        {"name": "Beneficenza", "slug": "beneficenza"},
        {"name": "Panorama",    "slug": "panorama"},
        {"name": "Moto",        "slug": "moto"},
    ],

    # ==================================================================
    # PRESS RELEASES
    # ==================================================================
    "press_releases": [
        {
            "title": "Moto Club Aquile Rosse annuncia il calendario eventi 2026",
            "pub_date": "2026-01-28",
            "body": (
                "<p>Il Moto Club Aquile Rosse ASD di Bergamo ha presentato il "
                "calendario ufficiale degli eventi per la stagione 2026, che prevede "
                "oltre 50 appuntamenti tra raduni, tour, track day e iniziative "
                "benefiche.</p>"
                "<p>Tra gli eventi di punta: l\u2019Avviamento Motori a Mandello del "
                "Lario, il Tour delle Orobie, il Track Day all\u2019Autodromo di "
                "Franciacorta e la 12ª edizione del Ride for Children a favore "
                "dell\u2019Ospedale Papa Giovanni XXIII.</p>"
                "<p>Per informazioni: stampa@aquilerosse.it</p>"
            ),
            "is_archived": False,
        },
        {
            "title": "Ride for Children 2025: raccolti \u20ac8.500 per la Pediatria",
            "pub_date": "2025-10-15",
            "body": (
                "<p>Si è conclusa con grande successo la 11ª edizione del Ride "
                "for Children, il motogiro benefico annuale del Moto Club Aquile "
                "Rosse. L\u2019evento ha visto la partecipazione di oltre 200 "
                "motociclisti e ha permesso di raccogliere \u20ac8.500, interamente "
                "devoluti al reparto di Pediatria dell\u2019Ospedale Papa Giovanni "
                "XXIII di Bergamo.</p>"
                "<p>Dal 2014 ad oggi, il Ride for Children ha raccolto "
                "complessivamente oltre \u20ac43.000.</p>"
            ),
            "is_archived": False,
        },
    ],

    # ==================================================================
    # BRAND ASSETS
    # ==================================================================
    "brand_assets": [
        {"name": "Logo Moto Club Aquile Rosse \u2013 Colore",   "category": "logo",     "description": "Logo ufficiale del club in versione a colori. Formato vettoriale SVG e PNG ad alta risoluzione. Da utilizzare su sfondo chiaro.", "sort_order": 1},
        {"name": "Logo Moto Club Aquile Rosse \u2013 Bianco",   "category": "logo",     "description": "Logo ufficiale del club in versione bianca monocromatica. Per utilizzo su sfondi scuri.", "sort_order": 2},
        {"name": "Linee guida brand",                            "category": "template", "description": "Documento con le linee guida per l\u2019utilizzo corretto del marchio, colori ufficiali e font del club.", "sort_order": 3},
    ],

    # ==================================================================
    # AID SKILLS
    # ==================================================================
    "aid_skills": [
        {"name": "Meccanica base",      "slug": "meccanica-base",      "description": "Riparazioni di base: catena, candele, fusibili, regolazioni.",              "category": "mechanics",  "sort_order": 1},
        {"name": "Meccanica avanzata",   "slug": "meccanica-avanzata",  "description": "Interventi complessi: carburatori, impianto elettrico, freni.",             "category": "mechanics",  "sort_order": 2},
        {"name": "Trasporto moto",       "slug": "trasporto-moto",      "description": "Disponibilità di furgone/carrello per trasporto moto in panne.",            "category": "transport",  "sort_order": 3},
        {"name": "Primo soccorso",       "slug": "primo-soccorso",      "description": "Competenze di primo soccorso e dotazione kit emergenza.",                   "category": "emergency",  "sort_order": 4},
        {"name": "Ospitalità",           "slug": "ospitalita",          "description": "Disponibilità per ospitare soci in transito (pernottamento, garage).",      "category": "logistics",  "sort_order": 5},
        {"name": "Recupero stradale",    "slug": "recupero-stradale",   "description": "Assistenza per recupero moto e motociclista da zone impervie.",             "category": "transport",  "sort_order": 6},
    ],

    # ==================================================================
    # IMAGES
    # ==================================================================
    "images": [
        {"key": "hero_homepage",      "width": 1920, "height": 1080, "keywords": "motorcycle,road",            "description": "Hero homepage"},
        {"key": "hero_about",         "width": 1920, "height": 800,  "keywords": "motorcycle,group,riders",    "description": "About page cover"},
        {"key": "hero_contact",       "width": 1920, "height": 600,  "keywords": "motorcycle,garage,workshop", "description": "Contact page hero"},
        {"key": "event_mandello",     "width": 800,  "height": 600,  "keywords": "motorcycle,lake",            "description": "Event Mandello"},
        {"key": "event_pisa",         "width": 800,  "height": 600,  "keywords": "motorcycle,tuscany",         "description": "Event Pisa"},
        {"key": "event_orobie",       "width": 800,  "height": 600,  "keywords": "motorcycle,mountains",       "description": "Event Orobie"},
        {"key": "event_franciacorta", "width": 800,  "height": 600,  "keywords": "motorcycle,racetrack",       "description": "Event Franciacorta"},
        {"key": "event_children",     "width": 800,  "height": 600,  "keywords": "motorcycle,charity",         "description": "Event Ride for Children"},
        {"key": "event_garda",        "width": 800,  "height": 600,  "keywords": "motorcycle,lake,garda",      "description": "Event Moto Rally Garda"},
        {"key": "news_mandello",      "width": 800,  "height": 600,  "keywords": "motorcycle,rally",           "description": "News Avviamento Motori"},
        {"key": "news_pisa",          "width": 800,  "height": 600,  "keywords": "motorcycle,italy",           "description": "News MotoLands Pisa"},
        {"key": "news_bayern",        "width": 800,  "height": 600,  "keywords": "motorcycle,germany",         "description": "News Bayern Treffen"},
        {"key": "news_officina",      "width": 800,  "height": 600,  "keywords": "motorcycle,workshop",        "description": "News Officina"},
        {"key": "news_manutenzione",  "width": 800,  "height": 600,  "keywords": "motorcycle,engine,repair",   "description": "News Manutenzione"},
        {"key": "news_assemblea",     "width": 800,  "height": 600,  "keywords": "meeting,people",             "description": "News Assemblea"},
        {"key": "partner_bgmoto",     "width": 1200, "height": 500,  "keywords": "motorcycle,magazine",        "description": "Bergamo Moto Magazine"},
        {"key": "member_marco",       "width": 400,  "height": 400,  "keywords": "biker,man,portrait",         "description": "Marco Bianchi"},
        {"key": "member_giulia",      "width": 400,  "height": 400,  "keywords": "biker,woman,portrait",       "description": "Giulia Ferrara"},
        {"key": "member_alessandro",  "width": 400,  "height": 400,  "keywords": "motorcyclist,man",           "description": "Alessandro Rossi"},
        {"key": "member_chiara",      "width": 400,  "height": 400,  "keywords": "motorcyclist,woman",         "description": "Chiara Fontana"},
        {"key": "member_roberto",     "width": 400,  "height": 400,  "keywords": "biker,man,helmet",           "description": "Roberto Colombo"},
    ],

    # ==================================================================
    # PLACE TAGS
    # ==================================================================
    "place_tags": [
        {"name": "Storico",          "slug": "storico"},
        {"name": "Panoramico",       "slug": "panoramico"},
        {"name": "Punto di ritrovo", "slug": "punto-di-ritrovo"},
        {"name": "Gastronomia",      "slug": "gastronomia"},
        {"name": "Paesaggistico",    "slug": "paesaggistico"},
    ],

    # ==================================================================
    # PAGES
    # ==================================================================
    "pages": [
        # ---- Home ----
        {
            "slug": "home",
            "page_type": "home",
            "parent_slug": None,
            "translation_key": TK["home"],
            "title": "Moto Club Aquile Rosse",
            "fields": {
                "hero_title": "Moto Club Aquile Rosse",
                "hero_subtitle": "Passione, avventura e fratellanza su due ruote dal 1987",
                "primary_cta_text": "Prossimi Eventi",
                "secondary_cta_text": "Diventa Socio",
                "body": [
                    _rt(
                        "<h2>Benvenuti nel Moto Club Aquile Rosse</h2>"
                        "<p>Dal 1987 trasformiamo la passione per le due ruote in "
                        "viaggi memorabili, amicizie vere e iniziative che tengono "
                        "insieme strada, territorio e spirito di club.</p>"
                        "<p>Con oltre 250 soci attivi in tutta la Lombardia, "
                        "organizziamo raduni, tour panoramici, track day ed eventi "
                        "benefici per vivere la moto con intensità, stile e senso "
                        "di appartenenza.</p>"
                    ),
                    _stats([
                        {"number": "250+", "label": "Soci Attivi"},
                        {"number": "37", "label": "Anni di Storia"},
                        {"number": "50+", "label": "Eventi / Anno"},
                        {"number": "12", "label": "Tour Nazionali"},
                    ]),
                    _cta(
                        "Unisciti a Noi",
                        "Entra nel club, accedi alle attività riservate e "
                        "condividi tour, eventi e nuove strade con una comunità "
                        "che vive la moto tutto l\u2019anno.",
                        "Scopri le Tessere",
                        "/diventa-socio/",
                    ),
                ],
            },
        },

        # ---- About ----
        {
            "slug": "chi-siamo",
            "page_type": "about",
            "parent_slug": "home",
            "translation_key": TK["about"],
            "title": "Chi Siamo",
            "fields": {
                "intro": (
                    "<p>Il Moto Club Aquile Rosse nasce nel 1987 a Bergamo dall\u2019idea di "
                    "un gruppo di appassionati motociclisti che volevano condividere la "
                    "passione per le due ruote in un contesto di amicizia e solidarietà.</p>"
                    "<p>Oggi il club conta oltre 250 soci iscritti, con una sede sociale "
                    "in Via Borgo Palazzo 22, Bergamo. Siamo affiliati alla FMI (Federazione "
                    "Motociclistica Italiana) e organizziamo ogni anno più di 50 eventi "
                    "tra raduni, tour, giornate in pista e iniziative benefiche.</p>"
                ),
                "body": [
                    _rt(
                        "<h2>La Nostra Storia</h2>"
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
                        "</ul>"
                    ),
                    _timeline("Momenti Chiave", [
                        {"year": "1987", "title": "Fondazione", "description": "12 amici fondano il Moto Club Aquile Rosse a Bergamo."},
                        {"year": "1995", "title": "Affiliazione FMI", "description": "Il club si affilia alla Federazione Motociclistica Italiana."},
                        {"year": "2005", "title": "Nuova Sede", "description": "Inaugurata la nuova sede sociale in Via Borgo Palazzo."},
                        {"year": "2015", "title": "250 Soci", "description": "Il club raggiunge il traguardo di 250 soci attivi."},
                        {"year": "2024", "title": "Federazione", "description": "Avvio del programma di federazione con club partner in Italia."},
                    ]),
                ],
            },
        },

        # ---- Board ----
        {
            "slug": "consiglio-direttivo",
            "page_type": "board",
            "parent_slug": "chi-siamo",
            "translation_key": TK["board"],
            "title": "Consiglio Direttivo",
            "fields": {
                "intro": "<p>Il Consiglio Direttivo guida il club con passione e dedizione.</p>",
                "body": [
                    _team_grid(3, [
                        {"name": "Roberto Colombo", "role": "Presidente", "bio": "Motociclista da 40 anni, guida il club dal 2015. Appassionato di viaggi lungo raggio."},
                        {"name": "Francesca Moretti", "role": "Vicepresidente", "bio": "Ingegnere meccanico e istruttrice di guida sicura. Organizza i corsi di formazione del club."},
                        {"name": "Luca Bernardi", "role": "Segretario", "bio": "Gestisce le iscrizioni, la comunicazione e il sito web del club."},
                        {"name": "Chiara Fontana", "role": "Tesoriere", "bio": "Commercialista di professione, tiene i conti del club in ordine dal 2020."},
                        {"name": "Davide Marchetti", "role": "Resp. Eventi", "bio": "Pianifica e organizza tutti gli eventi del club. Specialista in logistica e percorsi."},
                        {"name": "Elena Rizzo", "role": "Resp. Comunicazione", "bio": "Giornalista e social media manager. Cura la newsletter e i canali social del club."},
                    ]),
                ],
            },
        },

        # ---- News Index ----
        {
            "slug": "news",
            "page_type": "news_index",
            "parent_slug": "home",
            "translation_key": TK["news_index"],
            "title": "News",
            "fields": {
                "intro": "<p>Tutte le novità dal mondo del Moto Club Aquile Rosse.</p>",
            },
        },

        # ---- News Articles ----
        {
            "slug": "avviamento-motori-2026",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_kickoff"],
            "title": "Avviamento Motori 2026: Si Riparte da Mandello!",
            "fields": {
                "intro": "Il tradizionale raduno di apertura stagione torna a Mandello del Lario con novità e sorprese per tutti gli appassionati di moto.",
                "display_date": "-3",
                "category": "club-news",
                "body": [_rt(
                    "<p>Come ogni anno, la stagione motociclistica si apre "
                    "con il tradizionale <strong>Avviamento Motori</strong> "
                    "a Mandello del Lario.</p>"
                    "<p>L\u2019evento prevede un programma ricco "
                    "di attività: dalla sfilata lungo il lago alle visite guidate "
                    "al Museo, fino alla cena sociale presso il "
                    "Ristorante Il Griso.</p>"
                    "<h3>Programma</h3>"
                    "<ul>"
                    "<li>Ore 9:00 \u2013 Ritrovo presso Piazza Garibaldi</li>"
                    "<li>Ore 10:30 \u2013 Sfilata lungo il Lago di Como</li>"
                    "<li>Ore 12:30 \u2013 Pranzo sociale</li>"
                    "<li>Ore 15:00 \u2013 Visita al museo della moto</li>"
                    "<li>Ore 18:00 \u2013 Aperitivo e premiazioni</li>"
                    "</ul>"
                    "<p>Il Moto Club Aquile Rosse parteciperà con una "
                    "delegazione di 30 soci. Le iscrizioni sono aperte "
                    "fino al 15 marzo.</p>"
                )],
            },
        },
        {
            "slug": "moto-lands-pisa",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_pisa"],
            "title": "1° Moto Lands of Pisa: Nuovo Evento in Toscana",
            "fields": {
                "intro": "Nasce un nuovo raduno motociclistico a Pontedera, nella terra dove nacque la Piaggio e a due passi dalla torre pendente.",
                "display_date": "-7",
                "category": "motorcycle-world",
                "body": [_rt(
                    "<p>Grandi novità dal panorama dei raduni motociclistici "
                    "italiani: è stato annunciato il <strong>1° Moto "
                    "Lands of Pisa</strong>, un evento che si terrà a Pontedera "
                    "(PI) nella primavera 2026.</p>"
                    "<p>L\u2019evento è organizzato dal Moto Club Terre di Pisa "
                    "e promette un weekend all\u2019insegna della cultura motociclistica "
                    "toscana, con percorsi tra le colline pisane, degustazioni "
                    "di prodotti locali e un raduno statico nel centro storico.</p>"
                    "<p>Il nostro club sta già organizzando una trasferta di "
                    "gruppo. Chi è interessato può contattare il responsabile "
                    "eventi Davide Marchetti.</p>"
                )],
            },
        },
        {
            "slug": "spring-franken-bayern-treffen",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_bayern"],
            "title": "Resoconto: Spring Franken Bayern Treffen 2026",
            "fields": {
                "intro": "Otto soci del club hanno partecipato al raduno primaverile in Baviera. Ecco il racconto dell\u2019esperienza.",
                "display_date": "-14",
                "category": "events-recap",
                "body": [_rt(
                    "<p>Lo scorso weekend un gruppo di 8 soci del Moto Club "
                    "Aquile Rosse ha attraversato le Alpi per partecipare al "
                    "<strong>Spring Franken Bayern Treffen</strong>, il raduno "
                    "primaverile che segna l\u2019inizio della stagione nella "
                    "regione tedesca della Franconia.</p>"
                    "<p>Il percorso di andata ha toccato il Passo del Brennero, "
                    "Innsbruck e Monaco prima di arrivare nella zona di "
                    "Norimberga. Il raduno, frequentato da oltre 500 motociclisti "
                    "provenienti da tutta Europa, ha offerto giornate di "
                    "cavalcate nelle splendide strade della Franconia, "
                    "birra bavarese e un\u2019atmosfera di grande cameratismo.</p>"
                )],
            },
        },
        {
            "slug": "convenzione-officina-moto-bergamo",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_workshop"],
            "title": "Nuova Convenzione con Officina Moto Bergamo",
            "fields": {
                "intro": "Siglata una convenzione con l\u2019Officina Moto Bergamo per sconti su tagliandi e riparazioni per tutti i soci.",
                "display_date": "-20",
                "category": "club-news",
                "body": [_rt(
                    "<p>Siamo lieti di annunciare una nuova convenzione con "
                    "<strong>Officina Moto Bergamo</strong>, centro assistenza "
                    "multimarca situato in Via Seriate 42.</p>"
                    "<p>Tutti i soci del Moto Club Aquile Rosse potranno "
                    "usufruire dei seguenti sconti:</p>"
                    "<ul>"
                    "<li>15% su tagliandi e manutenzione ordinaria</li>"
                    "<li>10% su ricambi originali e aftermarket</li>"
                    "<li>Diagnosi elettronica gratuita</li>"
                    "<li>Priorità nelle prenotazioni durante l\u2019alta stagione</li>"
                    "</ul>"
                    "<p>Per accedere alle agevolazioni è sufficiente presentare "
                    "la tessera socio in corso di validità.</p>"
                )],
            },
        },
        {
            "slug": "preparazione-moto-stagione",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_seasonal"],
            "title": "Guida alla Preparazione della Moto per la Stagione",
            "fields": {
                "intro": "I consigli del nostro meccanico di fiducia per rimettere la moto in forma dopo la pausa invernale.",
                "display_date": "-30",
                "category": "technical",
                "body": [_rt(
                    "<p>Con l\u2019arrivo della bella stagione è tempo di "
                    "preparare la moto per i primi giri. Ecco una checklist "
                    "essenziale preparata con il nostro partner tecnico "
                    "Officina Moto Bergamo.</p>"
                    "<h3>Controlli Essenziali</h3>"
                    "<ol>"
                    "<li><strong>Batteria</strong>: Verificare la carica e "
                    "i livelli dell\u2019elettrolito. Se la moto è stata ferma "
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
                    "</ol>"
                )],
            },
        },
        {
            "slug": "assemblea-soci-2026",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_assembly"],
            "title": "Assemblea Soci 2026: Approvato il Bilancio",
            "fields": {
                "intro": "L\u2019assemblea annuale ha approvato all\u2019unanimità il bilancio e il programma eventi per il nuovo anno.",
                "display_date": "-45",
                "category": "club-news",
                "body": [_rt(
                    "<p>Si è tenuta sabato scorso l\u2019assemblea annuale dei soci "
                    "del Moto Club Aquile Rosse presso la sede sociale.</p>"
                    "<p>Con la partecipazione di 142 soci su 258 aventi diritto, "
                    "l\u2019assemblea ha approvato all\u2019unanimità il bilancio consuntivo "
                    "2025 e il bilancio preventivo 2026.</p>"
                    "<h3>Punti Principali</h3>"
                    "<ul>"
                    "<li>Confermato il direttivo in carica per il biennio 2026\u20132027</li>"
                    "<li>Approvato il calendario eventi con 52 uscite programmate</li>"
                    "<li>Nuova partnership con 3 officine convenzionate</li>"
                    "<li>Lancio del sistema di federazione con altri club</li>"
                    "<li>Acquisto di un defibrillatore per la sede</li>"
                    "</ul>"
                )],
            },
        },

        # ---- Events Page ----
        {
            "slug": "eventi",
            "page_type": "events_page",
            "parent_slug": "home",
            "translation_key": TK["events_page"],
            "title": "Eventi",
            "fields": {
                "intro": "<p>Tutti gli eventi organizzati e supportati dal Moto Club Aquile Rosse.</p>",
            },
        },

        # ---- Event Details ----
        {
            "slug": "avviamento-motori-mandello-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_mandello"],
            "title": "Avviamento Motori 2026 \u2013 Mandello del Lario",
            "fields": {
                "intro": "Il tradizionale raduno di apertura stagione a Mandello del Lario.",
                "start_date": "+30",
                "end_date": "+31",
                "location_name": "Piazza Garibaldi, Mandello del Lario",
                "location_address": "Piazza Garibaldi, 23826 Mandello del Lario LC",
                "location_coordinates": "45.9167,9.3167",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 200,
                "base_fee": "25.00",
                "early_bird_discount": 20,
                "early_bird_deadline": "+15",
                "member_discount_percent": 10,
                "body": [_rt(
                    "<p>Partecipa all\u2019<strong>Avviamento Motori 2026</strong>, "
                    "il raduno che apre ufficialmente la stagione motociclistica "
                    "sulle sponde del Lago di Como.</p>"
                    "<h3>Cosa Include</h3>"
                    "<ul>"
                    "<li>Sfilata panoramica lungo il Lago di Como</li>"
                    "<li>Pranzo sociale (incluso nella quota)</li>"
                    "<li>Visita al Museo della moto</li>"
                    "<li>Gadget commemorativo</li>"
                    "</ul>"
                )],
            },
        },
        {
            "slug": "moto-lands-pisa-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_pisa"],
            "title": "1° Moto Lands of Pisa",
            "fields": {
                "intro": "Primo raduno motociclistico nella terra di Pontedera, tra le colline toscane.",
                "start_date": "+60",
                "end_date": "+62",
                "location_name": "Centro Storico, Pontedera",
                "location_address": "Piazza Martiri della Libertà, 56025 Pontedera PI",
                "location_coordinates": "43.6631,10.6322",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 300,
                "base_fee": "40.00",
                "early_bird_discount": 15,
                "early_bird_deadline": "+45",
                "member_discount_percent": 10,
                "body": [_rt(
                    "<p>Un weekend nella splendida Toscana per il primo "
                    "<strong>Moto Lands of Pisa</strong>.</p>"
                    "<p>Il programma prevede tour guidati nelle colline "
                    "pisane, visita al Museo Piaggio di Pontedera, "
                    "degustazione di prodotti tipici e raduno statico "
                    "in piazza con esposizione di moto d\u2019epoca e moderne.</p>"
                )],
            },
        },
        {
            "slug": "tour-orobie-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_orobie"],
            "title": "Tour delle Orobie \u2013 Giornata Sociale",
            "fields": {
                "intro": "Uscita giornaliera tra le valli bergamasche con sosta pranzo in rifugio.",
                "start_date": "+14",
                "end_date": "+14",
                "location_name": "Sede Club, Bergamo",
                "location_address": "Via Borgo Palazzo 22, 24121 Bergamo",
                "location_coordinates": "45.6983,9.6773",
                "category": "touring",
                "registration_open": True,
                "max_attendees": 40,
                "base_fee": "15.00",
                "early_bird_discount": 0,
                "member_discount_percent": 100,
                "body": [_rt(
                    "<p>Uscita sociale nelle magnifiche <strong>Valli Orobie</strong>, "
                    "con un percorso di circa 180 km tra le valli bergamasche.</p>"
                    "<p>Partenza dalla sede alle 8:30. Percorso: Bergamo \u2192 Val Seriana "
                    "\u2192 Passo della Presolana \u2192 Val di Scalve \u2192 Lago d\u2019Iseo \u2192 Bergamo. "
                    "Sosta pranzo presso il Rifugio Albani.</p>"
                    "<p><em>Gratuito per i soci con tessera in regola.</em></p>"
                )],
            },
        },
        {
            "slug": "track-day-franciacorta-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_franciacorta"],
            "title": "Track Day \u2013 Autodromo di Franciacorta",
            "fields": {
                "intro": "Giornata in pista all\u2019Autodromo di Franciacorta con istruttori professionisti.",
                "start_date": "+45",
                "end_date": "+45",
                "location_name": "Autodromo di Franciacorta",
                "location_address": "Via Trento 9, 25040 Castrezzato BS",
                "location_coordinates": "45.4683,9.9900",
                "category": "track-day",
                "registration_open": True,
                "max_attendees": 30,
                "base_fee": "120.00",
                "early_bird_discount": 10,
                "early_bird_deadline": "+30",
                "member_discount_percent": 15,
                "body": [_rt(
                    "<p>Una giornata dedicata alla guida sportiva sicura "
                    "all\u2019<strong>Autodromo di Franciacorta</strong>.</p>"
                    "<p>Il programma include:</p>"
                    "<ul>"
                    "<li>Briefing tecnico e di sicurezza</li>"
                    "<li>3 turni in pista da 20 minuti ciascuno</li>"
                    "<li>Coaching personalizzato con istruttori ex-CIV</li>"
                    "<li>Pranzo in circuito</li>"
                    "</ul>"
                    "<p>Obbligatori: tuta in pelle integrale, guanti, "
                    "stivali tecnici, casco integrale.</p>"
                )],
            },
        },
        {
            "slug": "ride-for-children-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_children"],
            "title": "Beneficenza: Ride for Children",
            "fields": {
                "intro": "Motogiro benefico a favore dell\u2019Ospedale dei Bambini di Bergamo.",
                "start_date": "+75",
                "end_date": "+75",
                "location_name": "Piazza Vecchia, Bergamo Alta",
                "location_address": "Piazza Vecchia, 24129 Bergamo",
                "location_coordinates": "45.7037,9.6623",
                "category": "charity-ride",
                "registration_open": True,
                "max_attendees": 0,
                "base_fee": "20.00",
                "early_bird_discount": 0,
                "member_discount_percent": 0,
                "body": [_rt(
                    "<p>Il <strong>Ride for Children</strong> è l\u2019evento "
                    "benefico annuale del Moto Club Aquile Rosse, giunto "
                    "alla sua 12ª edizione.</p>"
                    "<p>L\u2019intero ricavato delle iscrizioni sarà devoluto "
                    "al reparto di Pediatria dell\u2019Ospedale Papa Giovanni XXIII "
                    "di Bergamo per l\u2019acquisto di attrezzature mediche.</p>"
                    "<p><strong>Aperto a tutti, soci e non soci!</strong></p>"
                )],
            },
        },
        {
            "slug": "moto-rally-garda-2026",
            "page_type": "event",
            "parent_slug": "eventi",
            "translation_key": TK["event_garda"],
            "title": "Moto Rally Garda 2026",
            "fields": {
                "intro": "Raduno moto sul Lago di Garda con parata e concerti.",
                "start_date": "+90",
                "end_date": "+93",
                "location_name": "Lungolago di Desenzano del Garda",
                "location_address": "Lungolago Cesare Battisti, 25015 Desenzano del Garda BS",
                "location_coordinates": "45.4710,10.5379",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 500,
                "base_fee": "60.00",
                "early_bird_discount": 15,
                "early_bird_deadline": "+60",
                "member_discount_percent": 5,
                "body": [_rt(
                    "<p>Il <strong>Moto Rally Garda</strong> è uno dei più grandi "
                    "raduni moto del Nord Italia.</p>"
                    "<p>Quattro giorni di moto, musica, food truck e la celebre "
                    "Thunder Parade lungo le sponde del lago. Il nostro club "
                    "partecipa come ospite con uno stand informativo.</p>"
                )],
            },
        },

        # ---- Gallery ----
        {
            "slug": "galleria",
            "page_type": "gallery",
            "parent_slug": "home",
            "translation_key": TK["gallery"],
            "title": "Galleria",
            "fields": {
                "intro": "<p>Le foto più belle dai nostri eventi, tour e raduni.</p>",
            },
        },

        # ---- Contact ----
        {
            "slug": "contatti",
            "page_type": "contact",
            "parent_slug": "home",
            "translation_key": TK["contact"],
            "title": "Contatti",
            "fields": {
                "hero_badge": "Siamo qui per te",
                "intro": "<p>Hai domande? Vuoi sapere di più sul club? Scrivici!</p>",
                "form_title": "Inviaci un Messaggio",
                "success_message": "<p>Grazie per il tuo messaggio! Ti risponderemo entro 48 ore.</p>",
                "captcha_enabled": True,
                "captcha_provider": "honeypot",
                "membership_title": "Diventa Socio",
                "membership_description": (
                    "Unisciti alla nostra comunità di oltre 250 motociclisti. "
                    "Accesso a tutti gli eventi, sconti presso i partner, "
                    "assicurazione e assistenza stradale inclusi."
                ),
                "membership_price": "Quota annuale \u20ac80",
                "membership_cta_text": "Iscriviti Ora",
            },
        },

        # ---- Privacy ----
        {
            "slug": "privacy",
            "page_type": "privacy",
            "parent_slug": "home",
            "translation_key": TK["privacy"],
            "title": "Privacy Policy",
            "fields": {
                "last_updated": "0",
                "body": [_rt(
                    "<h2>Informativa sulla Privacy</h2>"
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
                    "<h3>Diritti dell\u2019Interessato</h3>"
                    "<p>L\u2019utente può esercitare i diritti di accesso, rettifica, "
                    "cancellazione e portabilità dei dati scrivendo a "
                    "privacy@aquilerosse.it.</p>"
                )],
            },
        },

        # ---- Transparency ----
        {
            "slug": "trasparenza",
            "page_type": "transparency",
            "parent_slug": "home",
            "translation_key": TK["transparency"],
            "title": "Trasparenza",
            "fields": {
                "intro": (
                    "<p>In ottemperanza alla normativa sulle associazioni sportive "
                    "dilettantistiche, pubblichiamo i documenti del club.</p>"
                ),
                "body": [_rt(
                    "<h2>Documenti del Club</h2>"
                    "<p>Statuto, bilanci e verbali assembleari sono disponibili "
                    "per la consultazione da parte dei soci e degli enti "
                    "di controllo.</p>"
                    "<h3>Statuto</h3>"
                    "<p>Lo Statuto del Moto Club Aquile Rosse ASD è stato "
                    "approvato nell\u2019assemblea costitutiva del 15 marzo 1987 "
                    "e aggiornato l\u2019ultima volta il 20 gennaio 2024.</p>"
                    "<h3>Bilanci</h3>"
                    "<ul>"
                    "<li>Bilancio Consuntivo 2025 \u2013 Approvato il 25/01/2026</li>"
                    "<li>Bilancio Consuntivo 2024 \u2013 Approvato il 28/01/2025</li>"
                    "</ul>"
                )],
            },
        },

        # ---- Press ----
        {
            "slug": "stampa",
            "page_type": "press",
            "parent_slug": "home",
            "translation_key": TK["press"],
            "title": "Area Stampa",
            "fields": {
                "intro": "<p>Materiale per la stampa e contatti per i media.</p>",
                "press_email": "stampa@aquilerosse.it",
                "press_phone": "+39 035 123 4568",
                "press_contact": "Elena Rizzo \u2013 Resp. Comunicazione",
                "body": [_rt("<p>Per richieste stampa, interviste o materiale fotografico contattare l\u2019ufficio comunicazione del club.</p>")],
            },
        },

        # ---- Membership Plans ----
        {
            "slug": "diventa-socio",
            "page_type": "membership_plans",
            "parent_slug": "home",
            "translation_key": TK["membership_plans"],
            "title": "Diventa Socio",
            "fields": {
                "intro": "<p>Scegli il piano di tesseramento più adatto alle tue esigenze. Combina più prodotti per personalizzare la tua esperienza.</p>",
            },
        },

        # ---- Federation ----
        {
            "slug": "federazione",
            "page_type": "federation",
            "parent_slug": "home",
            "translation_key": TK["federation"],
            "title": "Federazione",
            "fields": {
                "intro": (
                    "<p>La nostra rete di club partner condivide eventi, iniziative "
                    "e opportunità per tutti i soci. Grazie alla federazione puoi "
                    "scoprire cosa succede nei club amici, esplorare i loro eventi "
                    "e partecipare alle iniziative della rete \u2014 tutto dalla "
                    "piattaforma del tuo club, in totale sicurezza.</p>"
                ),
                "how_it_works": [
                    _step("Come funziona la Federazione", [
                        {"year": "1", "title": "Scopri i club partner", "description": "<p>Naviga la lista dei club federati e scopri le loro attività, la loro storia e i servizi che offrono ai soci.</p>"},
                        {"year": "2", "title": "Esplora gli eventi condivisi", "description": "<p>Consulta gli eventi pubblicati dai club partner. Puoi filtrarli per club, cercarli per nome e vedere tutti i dettagli.</p>"},
                        {"year": "3", "title": "Esprimi il tuo interesse", "description": "<p>Segna se sei interessato, indeciso o se partecipi sicuramente. Il club organizzatore riceve solo conteggi anonimi.</p>"},
                        {"year": "4", "title": "Commenta con i soci", "description": "<p>Discuti gli eventi con gli altri soci del tuo club. I commenti sono privati e non vengono mai condivisi con il club partner.</p>"},
                    ]),
                ],
                "faq": [
                    _faq_block("Domande frequenti sulla Federazione", [
                        {"question": "Cos\u2019è la federazione dei club?", "answer": "<p>È una rete volontaria di club che condividono eventi e iniziative attraverso un protocollo sicuro. Ogni club mantiene la propria completa autonomia.</p>"},
                        {"question": "I miei dati personali vengono condivisi?", "answer": "<p>No. La federazione scambia solo dati sugli eventi e conteggi aggregati anonimi. Nessun dato personale viene mai trasmesso ai club partner.</p>"},
                        {"question": "Come viene garantita la sicurezza?", "answer": "<p>Ogni club partner dispone di chiavi API univoche. Le comunicazioni avvengono tramite HTTPS con autenticazione HMAC. I dati vengono validati e sanificati prima dell\u2019importazione.</p>"},
                    ]),
                ],
                "body": [_rt(
                    "<h2>Vantaggi della federazione</h2>"
                    "<p>Far parte di una rete federata di club significa ampliare "
                    "le opportunità per i soci senza rinunciare all\u2019autonomia:</p>"
                    "<ul>"
                    "<li><strong>Più eventi</strong> \u2014 Accedi a un calendario "
                    "condiviso con decine di appuntamenti dai club partner.</li>"
                    "<li><strong>Nuove amicizie</strong> \u2014 Conosci appassionati "
                    "di altri club con interessi simili ai tuoi.</li>"
                    "<li><strong>Privacy garantita</strong> \u2014 I tuoi dati personali "
                    "restano nel nostro club.</li>"
                    "<li><strong>Discussione riservata</strong> \u2014 Commenta e "
                    "organizzati con i soci del tuo club in modo privato.</li>"
                    "</ul>"
                    "<p>La federazione è un progetto aperto: qualsiasi club può "
                    "aderire rispettando il protocollo tecnico e i principi di "
                    "trasparenza e privacy.</p>"
                )],
                "cta_text": "Scopri gli eventi partner",
                "cta_url": "/federazione/",
            },
        },

        # ---- Partner Index ----
        {
            "slug": "partner",
            "page_type": "partner_index",
            "parent_slug": "home",
            "translation_key": TK["partner_index"],
            "title": "Partner",
            "fields": {
                "intro": "<p>I partner e sponsor che supportano le attività del nostro club.</p>",
            },
        },

        # ---- Partner Pages ----
        {
            "slug": "officina-moto-bergamo",
            "page_type": "partner",
            "parent_slug": "partner",
            "translation_key": TK["partner_officina"],
            "title": "Officina Moto Bergamo",
            "fields": {
                "intro": "Centro assistenza multimarca e partner tecnico ufficiale del club.",
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
                "partnership_start": "2023-01-01",
                "body": [_rt(
                    "<p>Officina Moto Bergamo è il partner tecnico ufficiale "
                    "del Moto Club Aquile Rosse. Offre assistenza completa "
                    "su tutte le marche con personale certificato.</p>"
                    "<p>Sconti esclusivi per i soci del club su tagliandi, "
                    "riparazioni e acquisto ricambi.</p>"
                )],
            },
        },
        {
            "slug": "concessionaria-lecco",
            "page_type": "partner",
            "parent_slug": "partner",
            "translation_key": TK["partner_concessionaria"],
            "title": "Concessionaria Moto Lecco",
            "fields": {
                "intro": "Concessionaria di moto e main sponsor del club.",
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
                "partnership_start": "2020-06-01",
                "body": [_rt(
                    "<p>Concessionaria ufficiale per la provincia "
                    "di Lecco. Main sponsor del club dal 2020, supporta i "
                    "nostri eventi con demo ride e assistenza tecnica.</p>"
                )],
            },
        },
        {
            "slug": "bergamo-moto-magazine",
            "page_type": "partner",
            "parent_slug": "partner",
            "translation_key": TK["partner_magazine"],
            "title": "Bergamo Moto Magazine",
            "fields": {
                "intro": "Rivista online dedicata al motociclismo bergamasco e lombardo.",
                "category": "media-partner",
                "website": "https://www.example.com/bg-moto-mag",
                "email": "redazione@bgmotomag.it",
                "contact_city": "Bergamo",
                "is_featured": False,
                "show_on_homepage": True,
                "partnership_start": "2022-03-01",
                "body": [_rt(
                    "<p>Bergamo Moto Magazine è il nostro media partner: "
                    "copre tutti gli eventi del club con articoli, foto "
                    "e video sui propri canali.</p>"
                )],
            },
        },

        # ---- Place Index ----
        {
            "slug": "luoghi",
            "page_type": "place_index",
            "parent_slug": "home",
            "translation_key": TK["place_index"],
            "title": "Luoghi",
            "fields": {
                "intro": "<p>Scopri i luoghi legati alla nostra comunità: sedi club, monumenti, piazze e percorsi turistici in tutta Italia.</p>",
            },
        },

        # ---- Places ----
        {
            "slug": "sede-moto-club",
            "page_type": "place",
            "parent_slug": "luoghi",
            "translation_key": TK["place_hq"],
            "title": "Sede Moto Club Aquile Rosse",
            "fields": {
                "place_type": "clubhouse",
                "latitude": "45.694200",
                "longitude": "9.670000",
                "address": "Via Borgo Palazzo 42",
                "city": "Bergamo",
                "province": "BG",
                "postal_code": "24125",
                "short_description": "La sede ufficiale del Moto Club Aquile Rosse, punto di ritrovo per ogni uscita.",
                "description": "<p>Situata nel cuore di Bergamo, la nostra sede è il punto di ritrovo per gli appassionati di moto dal 2005. Aperta a tutti i soci con tessera valida.</p>",
                "opening_hours": "Sa-Do 09:00-18:00",
                "phone": "+39 035 123 4567",
                "website_url": "https://example.com/aquile-rosse",
                "_tags": ["Punto di ritrovo"],
            },
        },
        {
            "slug": "colosseo",
            "page_type": "place",
            "parent_slug": "luoghi",
            "translation_key": TK["place_colosseum"],
            "title": "Colosseo",
            "fields": {
                "place_type": "monument",
                "latitude": "41.890210",
                "longitude": "12.492231",
                "address": "Piazza del Colosseo 1",
                "city": "Roma",
                "province": "RM",
                "postal_code": "00184",
                "short_description": "L\u2019iconico anfiteatro romano, punto di partenza per la cavalcata annuale.",
                "description": "<p>Il Colosseo è il più grande anfiteatro antico mai costruito. È il nostro punto di partenza tradizionale per la cavalcata annuale \u2018Roma Caput Mundi\u2019.</p>",
                "_tags": ["Storico", "Paesaggistico"],
            },
        },
        {
            "slug": "piazza-del-campo",
            "page_type": "place",
            "parent_slug": "luoghi",
            "translation_key": TK["place_campo"],
            "title": "Piazza del Campo",
            "fields": {
                "place_type": "square",
                "latitude": "43.318340",
                "longitude": "11.331650",
                "address": "Piazza del Campo",
                "city": "Siena",
                "province": "SI",
                "postal_code": "53100",
                "short_description": "La piazza principale di Siena a forma di conchiglia, tappa obbligata del tour toscano.",
                "description": "<p>La splendida Piazza del Campo è famosa per il Palio. Ci fermiamo qui per il pranzo durante la nostra uscita annuale in Toscana.</p>",
                "_tags": ["Storico", "Paesaggistico", "Panoramico"],
            },
        },
        {
            "slug": "trattoria-da-mario",
            "page_type": "place",
            "parent_slug": "luoghi",
            "translation_key": TK["place_trattoria"],
            "title": "Trattoria da Mario",
            "fields": {
                "place_type": "restaurant",
                "latitude": "43.771389",
                "longitude": "11.253611",
                "address": "Via Rosina 2",
                "city": "Firenze",
                "province": "FI",
                "postal_code": "50123",
                "short_description": "Un\u2019autentica trattoria fiorentina, ristorante convenzionato per i soci.",
                "description": "<p>Trattoria a gestione familiare dal 1953. I soci del club hanno il 10% di sconto presentando la tessera valida.</p>",
                "opening_hours": "Lu-Sa 12:00-15:00",
                "phone": "+39 055 218550",
                "_tags": ["Gastronomia"],
            },
        },
        {
            "slug": "passo-dello-stelvio",
            "page_type": "place",
            "parent_slug": "luoghi",
            "translation_key": TK["place_stelvio"],
            "title": "Passo dello Stelvio",
            "fields": {
                "place_type": "poi",
                "latitude": "46.528611",
                "longitude": "10.453333",
                "address": "SS38",
                "city": "Bormio",
                "province": "SO",
                "postal_code": "23032",
                "short_description": "Il valico stradale più alto delle Alpi Orientali \u2014 una strada leggendaria.",
                "description": "<p>A 2.757 metri, il Passo dello Stelvio offre 48 tornanti sul solo versante nord. Aperto da giugno a novembre, tempo permettendo.</p>",
                "_tags": ["Paesaggistico", "Panoramico"],
            },
        },

        # ---- Route ----
        {
            "slug": "cavalcata-romana",
            "page_type": "route",
            "parent_slug": "luoghi",
            "translation_key": TK["route_roman"],
            "title": "La Cavalcata Romana",
            "fields": {
                "short_description": "Un panoramico giro di mezza giornata dal Colosseo attraverso le colline a sud di Roma.",
                "description": "<p>Partendo dal Colosseo, questo percorso vi porta attraverso Via Appia Antica e nella campagna dei Castelli Romani. Perfetto per un\u2019uscita domenicale.</p>",
                "distance_km": "85.5",
                "estimated_duration": 150,  # minutes → timedelta
                "difficulty": "medium",
            },
        },
    ],

    # ==================================================================
    # ROUTE STOPS
    # ==================================================================
    "route_stops": [
        {"route_slug": "cavalcata-romana", "place_slug": "sede-moto-club", "sort_order": 1, "note": "Ritrovo alle ore 8:00"},
        {"route_slug": "cavalcata-romana", "place_slug": "colosseo",       "sort_order": 2, "note": "Sosta foto all\u2019anfiteatro"},
    ],

    # ==================================================================
    # NAVBAR
    # ==================================================================
    "navbar_items": [
        # Top-level
        {"label": "Chi Siamo",  "link_page_slug": "chi-siamo",  "link_url": "", "sort_order": 0, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "News",       "link_page_slug": "news",       "link_url": "", "sort_order": 1, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Eventi",     "link_page_slug": "eventi",     "link_url": "", "sort_order": 2, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Galleria",   "link_page_slug": "galleria",   "link_url": "", "sort_order": 3, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Servizi",    "link_page_slug": "",            "link_url": "", "sort_order": 4, "parent_label": "", "is_cta": False, "open_new_tab": False},
        # Sub: Chi Siamo
        {"label": "Storia",               "link_page_slug": "chi-siamo",          "link_url": "", "sort_order": 0, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Contatti",             "link_page_slug": "contatti",            "link_url": "", "sort_order": 1, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Diventa Socio",        "link_page_slug": "diventa-socio",       "link_url": "", "sort_order": 2, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Consiglio Direttivo",  "link_page_slug": "consiglio-direttivo", "link_url": "", "sort_order": 3, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Trasparenza",          "link_page_slug": "trasparenza",         "link_url": "", "sort_order": 4, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Tessera Socio",        "link_page_slug": "",                    "link_url": "reverse:account:card", "sort_order": 5, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        {"label": "Partner",              "link_page_slug": "partner",             "link_url": "", "sort_order": 6, "parent_label": "Chi Siamo", "is_cta": False, "open_new_tab": False},
        # Sub: Servizi
        {"label": "Soccorso Stradale",    "link_page_slug": "",            "link_url": "reverse:mutual_aid:map",          "sort_order": 0, "parent_label": "Servizi", "is_cta": False, "open_new_tab": False},
        {"label": "Federazione Eventi",   "link_page_slug": "federazione", "link_url": "",                                "sort_order": 1, "parent_label": "Servizi", "is_cta": False, "open_new_tab": False},
        {"label": "Contributi",           "link_page_slug": "",            "link_url": "reverse:account:my_contributions", "sort_order": 2, "parent_label": "Servizi", "is_cta": False, "open_new_tab": False},
        {"label": "Notifiche",            "link_page_slug": "",            "link_url": "reverse:account:notifications",    "sort_order": 3, "parent_label": "Servizi", "is_cta": False, "open_new_tab": False},
        {"label": "Area Stampa",          "link_page_slug": "stampa",      "link_url": "",                                "sort_order": 4, "parent_label": "Servizi", "is_cta": False, "open_new_tab": False},
    ],

    # ==================================================================
    # FOOTER
    # ==================================================================
    "footer_items": [
        {"label": "Chi Siamo",    "link_page_slug": "chi-siamo",    "link_url": "", "sort_order": 0},
        {"label": "News",         "link_page_slug": "news",         "link_url": "", "sort_order": 1},
        {"label": "Eventi",       "link_page_slug": "eventi",       "link_url": "", "sort_order": 2},
        {"label": "Privacy",      "link_page_slug": "privacy",      "link_url": "", "sort_order": 3},
        {"label": "Trasparenza",  "link_page_slug": "trasparenza",  "link_url": "", "sort_order": 4},
    ],

    "footer_social_links": [
        {"platform": "facebook",  "url": "https://www.facebook.com/motoclubaquilerosse",  "sort_order": 0},
        {"platform": "instagram", "url": "https://www.instagram.com/aquilerosse_mc",       "sort_order": 1},
        {"platform": "youtube",   "url": "https://www.youtube.com/@aquilerossemc",         "sort_order": 2},
    ],

    # ==================================================================
    # SITE SETTINGS
    # ==================================================================
    "site_settings": {
        "site_name": "Moto Club Aquile Rosse",
        "tagline": "Passione, avventura e fratellanza su due ruote dal 1987",
        "description": "Sito ufficiale del Moto Club Aquile Rosse ASD di Bergamo. Organizzazione di raduni, tour, track day ed eventi benefici per motociclisti di tutte le marche.",
        "theme": "velocity",
        "phone": "+39 035 123 4567",
        "email": "info@aquilerosse.it",
        "address": "Via Borgo Palazzo 22\n24121 Bergamo (BG)\nItalia",
        "hours": "Mer/Ven 20:30-23:00, Sab 15:00-18:00",
        "facebook_url": "https://www.facebook.com/motoclubaquilerosse",
        "instagram_url": "https://www.instagram.com/aquilerosse_mc",
        "youtube_url": "https://www.youtube.com/@aquilerossemc",
        "map_default_center": "45.6983,9.6773",
        "map_default_zoom": "12",
        "footer_description": "<p>Moto Club Aquile Rosse ASD \u2013 Passione, avventura e fratellanza su due ruote dal 1987.</p>",
        "copyright_text": "\u00a9 2026 Moto Club Aquile Rosse ASD. Tutti i diritti riservati.",
    },

    # ==================================================================
    # MEMBERS
    # ==================================================================
    "members": [
        {
            "username": "demo_marco", "first_name": "Marco", "last_name": "Bianchi",
            "email": "marco.bianchi@example.com", "display_name": "Marco B.",
            "phone": "+39 333 111 2222", "mobile": "+39 333 111 2222",
            "birth_date": "1985-03-15", "birth_place": "Bergamo",
            "fiscal_code": "BNCMRC85C15A794X",
            "city": "Bergamo", "province": "BG", "postal_code": "24121",
            "address": "Via Roma 10", "card_number": "AQR-2024-001",
            "membership_date": "2019-01-15", "membership_expiry": "2026-12-31",
            "bio": "Motociclista dal 1998. Appassionato di V7 e strade di montagna. Meccanico hobbista, sempre pronto a dare una mano ai compagni di viaggio.",
            "aid_available": True, "aid_radius_km": 30,
            "aid_location_city": "Bergamo", "aid_coordinates": "45.6983,9.6773",
            "aid_notes": "Ho attrezzi base e cavi per batteria. Disponibile weekend.",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_marco",
        },
        {
            "username": "demo_giulia", "first_name": "Giulia", "last_name": "Ferrara",
            "email": "giulia.ferrara@example.com", "display_name": "Giulia F.",
            "phone": "+39 333 222 3333", "mobile": "+39 333 222 3333",
            "birth_date": "1990-07-22", "birth_place": "Milano",
            "fiscal_code": "FRRGLI90L62F205Y",
            "city": "Seriate", "province": "BG", "postal_code": "24068",
            "address": "Via Nazionale 45", "card_number": "AQR-2024-002",
            "membership_date": "2021-03-01", "membership_expiry": "2026-12-31",
            "bio": "Infermiera e motociclista. Certificata primo soccorso, porto sempre il kit emergenza in moto.",
            "aid_available": True, "aid_radius_km": 50,
            "aid_location_city": "Seriate", "aid_coordinates": "45.6847,9.7267",
            "aid_notes": "Competenze primo soccorso. Disponibile anche in settimana dopo le 18.",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_giulia",
        },
        {
            "username": "demo_alessandro", "first_name": "Alessandro", "last_name": "Rossi",
            "email": "alessandro.rossi@example.com", "display_name": "Alex R.",
            "phone": "+39 333 333 4444", "mobile": "+39 333 333 4444",
            "birth_date": "1975-11-08", "birth_place": "Lecco",
            "fiscal_code": "RSSLSN75S08E507Z",
            "city": "Lecco", "province": "LC", "postal_code": "23900",
            "address": "Corso Matteotti 88", "card_number": "AQR-2024-003",
            "membership_date": "1987-03-15", "membership_expiry": "2026-12-31",
            "bio": "Socio fondatore del club. Ex meccanico a Mandello. Ho un furgone attrezzato per trasporto moto. Guido una V85 TT.",
            "aid_available": True, "aid_radius_km": 100,
            "aid_location_city": "Lecco", "aid_coordinates": "45.8566,9.3977",
            "aid_notes": "Furgone con rampa per trasporto moto. Meccanica avanzata. Disponibile quasi sempre, chiamare al cellulare.",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_alessandro",
        },
        {
            "username": "demo_chiara", "first_name": "Chiara", "last_name": "Fontana",
            "email": "chiara.fontana@example.com", "display_name": "Chiara F.",
            "phone": "+39 333 444 5555", "mobile": "+39 333 444 5555",
            "birth_date": "1988-05-30", "birth_place": "Brescia",
            "fiscal_code": "FNTCHR88E70B157W",
            "city": "Treviglio", "province": "BG", "postal_code": "24047",
            "address": "Via Cavour 12", "card_number": "AQR-2024-004",
            "membership_date": "2020-06-01", "membership_expiry": "2026-12-31",
            "bio": "Commercialista e tesoriere del club. Appassionata di grandi viaggi su due ruote. Viaggio spesso in solitaria verso i passi alpini.",
            "aid_available": True, "aid_radius_km": 25,
            "aid_location_city": "Treviglio", "aid_coordinates": "45.5200,9.5900",
            "aid_notes": "Posso ospitare motociclisti di passaggio (garage e camera ospiti).",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_chiara",
        },
        {
            "username": "demo_roberto", "first_name": "Roberto", "last_name": "Colombo",
            "email": "roberto.colombo@example.com", "display_name": "Roberto C.",
            "phone": "+39 333 555 6666", "mobile": "+39 333 555 6666",
            "birth_date": "1970-09-03", "birth_place": "Bergamo",
            "fiscal_code": "CLMRRT70P03A794V",
            "city": "Bergamo", "province": "BG", "postal_code": "24122",
            "address": "Via Borgo Palazzo 22", "card_number": "AQR-2024-005",
            "membership_date": "2015-01-01", "membership_expiry": "2026-12-31",
            "bio": "Presidente del moto club. 40 anni in sella, collezionista di moto d\u2019epoca. Organizzo i tour annuali del club su percorsi selezionati.",
            "aid_available": True, "aid_radius_km": 40,
            "aid_location_city": "Bergamo", "aid_coordinates": "45.6983,9.6773",
            "aid_notes": "Ampia esperienza meccanica su moto classiche e moderne. Attrezzi professionali in sede club.",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_roberto",
        },
    ],

    # ==================================================================
    # AID REQUESTS
    # ==================================================================
    "aid_requests": [
        {"helper_username": "demo_alessandro", "requester_name": "Demo: Marco Bianchi", "requester_phone": "+39 333 111 2222", "requester_email": "marco.bianchi@example.com", "requester_username": "demo_marco", "issue_type": "breakdown", "description": "Moto in panne sulla SS38 tra Lecco e Colico, km 42. La moto non parte, sembra un problema elettrico. Sono al parcheggio del ristorante La Pergola.", "location": "SS38, Km 42 \u2013 Dervio (LC)", "urgency": "high", "status": "resolved"},
        {"helper_username": "demo_giulia", "requester_name": "Demo: Chiara Fontana", "requester_phone": "+39 333 444 5555", "requester_email": "chiara.fontana@example.com", "requester_username": "demo_chiara", "issue_type": "flat_tire", "description": "Foratura pneumatico posteriore sulla strada del Passo della Presolana. Non ho kit riparazione tubeless. Sono al Rifugio Magnolini.", "location": "Passo della Presolana \u2013 Rifugio Magnolini (BG)", "urgency": "medium", "status": "resolved"},
        {"helper_username": "demo_roberto", "requester_name": "Demo: Giulia Ferrara", "requester_phone": "+39 333 222 3333", "requester_email": "giulia.ferrara@example.com", "requester_username": "demo_giulia", "issue_type": "fuel", "description": "Rimasta senza benzina sulla SP671 tra Clusone e Bergamo. Il distributore più vicino era chiuso (domenica sera). Sono al bar Sport di Gazzaniga.", "location": "SP671, Gazzaniga (BG)", "urgency": "low", "status": "resolved"},
        {"helper_username": "demo_alessandro", "requester_name": "Demo: Roberto Colombo", "requester_phone": "+39 333 555 6666", "requester_email": "roberto.colombo@example.com", "requester_username": "demo_roberto", "issue_type": "tow", "description": "Moto d\u2019epoca con rottura cambio al ritorno dal raduno di Mandello. Serve trasporto moto con furgone fino alla sede club a Bergamo (~60km).", "location": "Mandello del Lario, Piazza Garibaldi (LC)", "urgency": "medium", "status": "in_progress"},
        {"helper_username": "demo_chiara", "requester_name": "Demo: Alessandro Rossi", "requester_phone": "+39 333 333 4444", "requester_email": "alessandro.rossi@example.com", "requester_username": "demo_alessandro", "issue_type": "accommodation", "description": "Di ritorno dal tour delle Dolomiti, problema alla catena della V85 TT vicino a Treviglio. La moto si muove piano ma non posso fare altri 80km fino a Lecco stasera. Cercasi garage e un divano per la notte.", "location": "Treviglio centro (BG)", "urgency": "medium", "status": "open"},
    ],

    # ==================================================================
    # FEDERATED CLUBS
    # ==================================================================
    "federated_clubs": [
        {"short_code": "MANDELLO", "name": "Moto Club Le Aquile \u2013 Mandello del Lario", "city": "Mandello del Lario", "base_url": "https://api.motoclubmandello.it", "logo_url": "/static/img/federation/mandello.svg", "description": "Storico club sulle sponde del Lago di Como, punto di riferimento per gli appassionati di moto nel lecchese. Organizzano raduni panoramici, giri del lago e incontri tecnici.", "api_key": "demo_key_mandello_2026_abcdef1234567890", "is_active": True, "is_approved": True, "share_our_events": True},
        {"short_code": "PISA", "name": "Moto Club Terre di Pisa", "city": "Pisa", "base_url": "https://api.mcterre-pisa.it", "logo_url": "/static/img/federation/pisa.svg", "description": "Club attivo nella provincia di Pisa, focalizzato su touring e cultura locale. Tour tra le colline toscane, eventi enogastronomici e gite sulla costa tirrenica.", "api_key": "demo_key_pisa_2026_abcdef1234567890", "is_active": True, "is_approved": True, "share_our_events": True},
        {"short_code": "MOTOGARDA", "name": "Moto Club Lago di Garda", "city": "Desenzano del Garda", "base_url": "https://api.motoclub-garda.it", "logo_url": "/static/img/federation/garda.svg", "description": "Club motociclistico del Lago di Garda. Raduni, gite benefiche e touring del weekend sulle strade del Trentino e del Veneto.", "api_key": "demo_key_garda_2026_abcdef1234567890", "is_active": True, "is_approved": False, "share_our_events": False},
    ],

    # ==================================================================
    # EXTERNAL EVENTS
    # ==================================================================
    "external_events": [
        {"club_short_code": "MANDELLO", "external_id": "mandello-apertura-2026", "event_name": "Avviamento Motori 2026 \u2013 Mandello", "start_days_offset": 28, "end_days_offset": 29, "location_name": "Piazza Garibaldi, Mandello del Lario", "location_address": "23826 Mandello del Lario LC", "location_lat": 45.9167, "location_lon": 9.3167, "description": "Tradizionale apertura di stagione a Mandello del Lario. Sfilata sul lago, visita al museo e cena sociale.", "detail_url": "https://motoclubmandello.it/eventi/avviamento-2026", "is_approved": True},
        {"club_short_code": "MANDELLO", "external_id": "mandello-open-day", "event_name": "Open Day Mandello", "start_days_offset": 50, "end_days_offset": 50, "location_name": "Centro storico Mandello", "location_address": "Via Parodi 57, 23826 Mandello del Lario LC", "location_lat": 45.9200, "location_lon": 9.3200, "description": "Porte aperte allo storico stabilimento di Mandello. Visite guidate alla linea di produzione e al museo.", "detail_url": "https://motoclubmandello.it/eventi/open-day-2026", "is_approved": True},
        {"club_short_code": "PISA", "external_id": "pisa-lands-2026", "event_name": "1° Moto Lands of Pisa", "start_days_offset": 58, "end_days_offset": 60, "location_name": "Pontedera, Centro Storico", "location_address": "56025 Pontedera PI", "location_lat": 43.6631, "location_lon": 10.6322, "description": "Primo raduno motociclistico nella terra di Pontedera. Tour collinari, visita al Museo Piaggio, degustazioni.", "detail_url": "https://mcterre-pisa.it/eventi/lands-of-pisa-2026", "is_approved": True},
    ],

    "event_interests": [
        {"username": "demo_marco",      "event_external_id": "mandello-apertura-2026", "interest_level": "going"},
        {"username": "demo_giulia",     "event_external_id": "mandello-apertura-2026", "interest_level": "going"},
        {"username": "demo_alessandro", "event_external_id": "mandello-apertura-2026", "interest_level": "going"},
        {"username": "demo_roberto",    "event_external_id": "mandello-open-day",      "interest_level": "interested"},
        {"username": "demo_marco",      "event_external_id": "pisa-lands-2026",        "interest_level": "maybe"},
        {"username": "demo_chiara",     "event_external_id": "pisa-lands-2026",        "interest_level": "interested"},
    ],

    "event_comments": [
        {"username": "demo_marco",      "event_external_id": "mandello-apertura-2026", "content": "Saremo lì con 4 moto da Bergamo! Chi si unisce al gruppo?"},
        {"username": "demo_giulia",     "event_external_id": "mandello-apertura-2026", "content": "Ci sarò! Partiamo insieme sabato mattina?"},
        {"username": "demo_alessandro", "event_external_id": "mandello-open-day",      "content": "L\u2019Open Day è sempre un\u2019esperienza unica. Consigliatissimo."},
    ],

    "federated_helpers": [
        {"club_short_code": "MANDELLO", "external_id": "mandello-helper-01", "display_name": "Luca M.",    "city": "Mandello del Lario", "latitude": 45.9170, "longitude": 9.3170, "radius_km": 30, "notes": "Meccanico esperto, disponibile con furgone attrezzato."},
        {"club_short_code": "MANDELLO", "external_id": "mandello-helper-02", "display_name": "Stefano B.", "city": "Lecco",              "latitude": 45.8530, "longitude": 9.3900, "radius_km": 40, "notes": "Carro attrezzi per moto. Disponibile weekend."},
        {"club_short_code": "PISA",     "external_id": "pisa-helper-01",     "display_name": "Andrea P.",  "city": "Pontedera",           "latitude": 43.6631, "longitude": 10.6322, "radius_km": 35, "notes": "Officina mobile, riparazioni su strada."},
        {"club_short_code": "PISA",     "external_id": "pisa-helper-02",     "display_name": "Marco T.",   "city": "Pisa",                "latitude": 43.7228, "longitude": 10.4017, "radius_km": 25, "notes": "Trasporto moto con carrello. Disponibile 24/7."},
    ],

    # ==================================================================
    # NOTIFICATIONS
    # ==================================================================
    "notifications": [
        {"notification_type": "event_reminder", "recipient_username": "demo_marco",  "channel": "in_app", "title": "Promemoria: Tour delle Orobie tra 3 giorni", "body": "Il Tour delle Orobie è previsto per sabato. Ritrovo alle 8:30 in sede.", "url_type": "page", "url_ref": "tour-orobie-2026", "status": "sent", "sent_hours_ago": 2},
        {"notification_type": "event_reminder", "recipient_username": "demo_giulia", "channel": "in_app", "title": "Promemoria: Tour delle Orobie tra 3 giorni", "body": "Il Tour delle Orobie è previsto per sabato. Ritrovo alle 8:30 in sede.", "url_type": "page", "url_ref": "tour-orobie-2026", "status": "sent", "sent_hours_ago": 2},
        {"notification_type": "event_reminder", "recipient_username": "demo_marco",  "channel": "in_app", "title": "Giulia ha risposto al tuo commento", "body": "Giulia F. ha risposto al tuo commento su \u2018Avviamento Motori 2026\u2019.", "url_type": "page", "url_ref": "avviamento-motori-2026", "status": "sent", "sent_hours_ago": 12},
        {"notification_type": "membership_expiring", "recipient_username": "demo_giulia", "channel": "email", "title": "La tua richiesta di tessera è stata approvata!", "body": "La tua richiesta per la Tessera Socio Ordinario è stata approvata. La tessera digitale è disponibile nel tuo profilo.", "url_type": "reverse", "url_ref": "account:card", "status": "sent", "sent_hours_ago": 120},
        {"notification_type": "aid_request", "recipient_username": "demo_alessandro", "channel": "in_app", "title": "Nuova richiesta di soccorso vicino a te", "body": "Roberto C. ha bisogno di trasporto moto da Mandello del Lario. Distanza: ~25 km.", "url_type": "reverse", "url_ref": "mutual_aid:map", "status": "sent", "sent_hours_ago": 36},
        {"notification_type": "event_published", "recipient_username": "demo_chiara", "channel": "in_app", "title": "Nuovo evento: Track Day Franciacorta", "body": "È stato pubblicato un nuovo evento: Track Day all\u2019Autodromo di Franciacorta. Le iscrizioni sono aperte!", "url_type": "page", "url_ref": "track-day-franciacorta-2026", "status": "pending", "sent_hours_ago": 0},
        {"notification_type": "event_published", "recipient_username": "demo_roberto", "channel": "in_app", "title": "La tua proposta è stata approvata", "body": "La tua proposta \u2018Tour Sardegna 5 giorni\u2019 è stata approvata e pubblicata.", "url_type": "reverse", "url_ref": "account:my_contributions", "status": "sent", "sent_hours_ago": 24},
    ],

    # ==================================================================
    # EVENT REGISTRATIONS
    # ==================================================================
    "event_registrations": [
        {"username": "demo_marco",      "event_slug": "avviamento-motori-mandello-2026", "status": "confirmed", "guests": 0, "notes": "", "days_ago": 10},
        {"username": "demo_giulia",     "event_slug": "avviamento-motori-mandello-2026", "status": "confirmed", "guests": 0, "notes": "", "days_ago": 8},
        {"username": "demo_alessandro", "event_slug": "avviamento-motori-mandello-2026", "status": "registered","guests": 0, "notes": "", "days_ago": 5},
        {"username": "demo_roberto",    "event_slug": "avviamento-motori-mandello-2026", "status": "confirmed", "guests": 1, "notes": "", "days_ago": 12},
        {"username": "demo_marco",      "event_slug": "moto-lands-pisa-2026",            "status": "registered","guests": 0, "notes": "", "days_ago": 3},
        {"username": "demo_alessandro", "event_slug": "moto-lands-pisa-2026",            "status": "confirmed", "guests": 0, "notes": "", "days_ago": 7},
        {"username": "demo_giulia",     "event_slug": "tour-orobie-2026",                "status": "confirmed", "guests": 0, "notes": "", "days_ago": 2},
        {"username": "demo_chiara",     "event_slug": "tour-orobie-2026",                "status": "confirmed", "guests": 0, "notes": "", "days_ago": 4},
        {"username": "demo_roberto",    "event_slug": "tour-orobie-2026",                "status": "confirmed", "guests": 0, "notes": "", "days_ago": 6},
        {"username": "demo_marco",      "event_slug": "track-day-franciacorta-2026",     "status": "confirmed", "guests": 0, "notes": "", "days_ago": 1},
        {"username": "demo_chiara",     "event_slug": "track-day-franciacorta-2026",     "status": "waitlist",  "guests": 0, "notes": "", "days_ago": 1},
    ],

    # ==================================================================
    # EVENT FAVORITES
    # ==================================================================
    "event_favorites": [
        {"username": "demo_marco",      "event_slug": "avviamento-motori-mandello-2026"},
        {"username": "demo_marco",      "event_slug": "tour-orobie-2026"},
        {"username": "demo_marco",      "event_slug": "ride-for-children-2026"},
        {"username": "demo_giulia",     "event_slug": "avviamento-motori-mandello-2026"},
        {"username": "demo_giulia",     "event_slug": "moto-lands-pisa-2026"},
        {"username": "demo_giulia",     "event_slug": "ride-for-children-2026"},
        {"username": "demo_alessandro", "event_slug": "avviamento-motori-mandello-2026"},
        {"username": "demo_alessandro", "event_slug": "track-day-franciacorta-2026"},
        {"username": "demo_chiara",     "event_slug": "tour-orobie-2026"},
        {"username": "demo_chiara",     "event_slug": "moto-rally-garda-2026"},
        {"username": "demo_roberto",    "event_slug": "avviamento-motori-mandello-2026"},
        {"username": "demo_roberto",    "event_slug": "ride-for-children-2026"},
        {"username": "demo_roberto",    "event_slug": "moto-rally-garda-2026"},
    ],

    # ==================================================================
    # CONTRIBUTIONS
    # ==================================================================
    "contributions": [
        {"username": "demo_marco", "contribution_type": "story", "title": "La mia prima uscita con il club", "body": "Era un sabato di aprile 2019 quando ho fatto la prima uscita con il Moto Club Aquile Rosse. Non conoscevo nessuno, ero nervoso. Ma bastò fermarsi al primo bar per capire che questa era la mia gente. Da quel giorno non ho mai perso un\u2019uscita.", "status": "approved"},
        {"username": "demo_giulia", "contribution_type": "story", "title": "Lo Stelvio in solitaria: paura e meraviglia", "body": "L\u2019anno scorso ho deciso di affrontare lo Stelvio da sola. 48 tornanti, nebbia improvvisa, e a metà salita un calo di pressione al posteriore. Ho chiamato il mutuo soccorso e in 30 minuti Alessandro era lì col furgone. Questo è il club.", "status": "approved"},
        {"username": "demo_roberto", "contribution_type": "proposal", "title": "Proposta: Tour Sardegna 5 giorni", "body": "Propongo un tour di 5 giorni in Sardegna per settembre 2026. Percorso: Olbia \u2192 Costa Smeralda \u2192 Barbagia \u2192 Cagliari \u2192 Oristano \u2192 Alghero \u2192 Porto Torres. Ho già contattato 3 B&B biker-friendly lungo il percorso. Budget stimato: \u20ac600 a persona tutto incluso (traghetto, pernottamenti, colazioni).", "status": "approved"},
        {"username": "demo_chiara", "contribution_type": "announcement", "title": "Rinnovo tessere: scadenza 31 marzo", "body": "Ricordo a tutti i soci che il termine per il rinnovo della tessera 2026 è il 31 marzo. Chi rinnova entro il 15 marzo avrà uno sconto del 10% sulla quota. Potete rinnovare online dal profilo personale o in sede durante gli orari di apertura.", "status": "approved"},
        {"username": "demo_alessandro", "contribution_type": "story", "title": "40 anni in sella: la mia collezione", "body": "Ho iniziato a collezionare moto nel 1987, anno di fondazione del club. Oggi nel mio garage ci sono 7 moto: una Le Mans III del \u201981, una Stornello Sport del \u201968, una V7 Classic, una California 1400, una V85 TT, una V100 Mandello e una Griso 1200. Ognuna ha una storia, ognuna mi ha portato in posti incredibili.", "status": "pending"},
    ],

    # ==================================================================
    # COMMENTS
    # ==================================================================
    "comments": [
        {"username": "demo_marco",      "target_type": "news",  "target_index": 0, "content": "Grande notizia! Mandello è sempre un appuntamento imperdibile. Chi viene col gruppo da Bergamo?", "moderation_status": "approved"},
        {"username": "demo_giulia",     "target_type": "news",  "target_index": 0, "content": "Io ci sarò! Chi mi fa compagnia per il giro del lago nel pomeriggio?", "moderation_status": "approved"},
        {"username": "demo_alessandro", "target_type": "news",  "target_index": 0, "content": "Presente come ogni anno. Porto anche la Le Mans III, così facciamo colpo al parcheggio d\u2019epoca.", "moderation_status": "approved"},
        {"username": "demo_chiara",     "target_type": "news",  "target_index": 1, "content": "La Toscana in moto è un sogno. Sto già organizzando il viaggio con Giulia.", "moderation_status": "approved"},
        {"username": "demo_roberto",    "target_type": "news",  "target_index": 2, "content": "Il Bayern Treffen è stato fantastico. Le strade della Franconia sono tra le migliori d\u2019Europa.", "moderation_status": "approved"},
        {"username": "demo_marco",      "target_type": "event", "target_index": 0, "content": "Iscritto! Qualcuno conosce un buon hotel a Mandello?", "moderation_status": "approved"},
        {"username": "demo_giulia",     "target_type": "event", "target_index": 1, "content": "La Toscana in primavera\u2026 non vedo l\u2019ora!", "moderation_status": "approved"},
        {"username": "demo_roberto",    "target_type": "event", "target_index": 2, "content": "Le Orobie in moto sono spettacolari. Percorso bellissimo.", "moderation_status": "pending"},
    ],

    # ==================================================================
    # REACTIONS
    # ==================================================================
    "reactions": [
        {"username": "demo_marco",      "target_type": "news",  "target_index": 0, "reaction_type": "like"},
        {"username": "demo_giulia",     "target_type": "news",  "target_index": 0, "reaction_type": "love"},
        {"username": "demo_alessandro", "target_type": "news",  "target_index": 0, "reaction_type": "like"},
        {"username": "demo_chiara",     "target_type": "news",  "target_index": 0, "reaction_type": "like"},
        {"username": "demo_roberto",    "target_type": "news",  "target_index": 0, "reaction_type": "love"},
        {"username": "demo_marco",      "target_type": "news",  "target_index": 1, "reaction_type": "like"},
        {"username": "demo_giulia",     "target_type": "news",  "target_index": 1, "reaction_type": "love"},
        {"username": "demo_chiara",     "target_type": "news",  "target_index": 2, "reaction_type": "like"},
        {"username": "demo_marco",      "target_type": "event", "target_index": 0, "reaction_type": "love"},
        {"username": "demo_giulia",     "target_type": "event", "target_index": 0, "reaction_type": "love"},
        {"username": "demo_alessandro", "target_type": "event", "target_index": 0, "reaction_type": "like"},
        {"username": "demo_roberto",    "target_type": "event", "target_index": 1, "reaction_type": "love"},
        {"username": "demo_chiara",     "target_type": "event", "target_index": 2, "reaction_type": "like"},
    ],

    # ==================================================================
    # ACTIVITY LOG
    # ==================================================================
    "activity_log": [
        {"username": "demo_marco",      "activity_type": "login",          "description": "",                                                "days_ago": 0},
        {"username": "demo_marco",      "activity_type": "register",       "description": "Iscritto all\u2019Avviamento Motori 2026",         "days_ago": 1},
        {"username": "demo_giulia",     "activity_type": "login",          "description": "",                                                "days_ago": 0},
        {"username": "demo_giulia",     "activity_type": "profile_update", "description": "Aggiornamento profilo",                            "days_ago": 2},
        {"username": "demo_alessandro", "activity_type": "comment",        "description": "Commentato su Avviamento Motori 2026",             "days_ago": 3},
        {"username": "demo_chiara",     "activity_type": "login",          "description": "",                                                "days_ago": 1},
        {"username": "demo_roberto",    "activity_type": "login",          "description": "",                                                "days_ago": 0},
        {"username": "demo_roberto",    "activity_type": "reaction",       "description": "Reazione a 1° Moto Lands of Pisa",                "days_ago": 4},
    ],

    # ==================================================================
    # MEMBERSHIP REQUESTS
    # ==================================================================
    "membership_requests": [
        {"first_name": "Luca",    "last_name": "Moretti",   "email": "luca.moretti@example.com",   "phone": "+39 333 777 8888", "motivation": "Guido da 5 anni e mi piacerebbe entrare in un club che organizza tour ed eventi.",                   "status": "pending",   "days_ago": 3},
        {"first_name": "Sara",    "last_name": "De Luca",   "email": "sara.deluca@example.com",    "phone": "+39 333 888 9999", "motivation": "Un amico mi ha consigliato il vostro club. Vorrei conoscere altri motociclisti della zona di Bergamo.", "status": "pending",   "days_ago": 7},
        {"first_name": "Andrea",  "last_name": "Mazzini",   "email": "andrea.mazzini@example.com", "phone": "",                 "motivation": "Cerco un club ben organizzato, attento alla sicurezza e al touring.",                                  "status": "approved",  "days_ago": 14},
        {"first_name": "Elena",   "last_name": "Colombo",   "email": "elena.colombo@example.com",  "phone": "+39 333 000 1111", "motivation": "",                                                                                                    "status": "rejected",  "days_ago": 30},
        {"first_name": "Davide",  "last_name": "Russo",     "email": "davide.russo@example.com",   "phone": "+39 333 111 0000", "motivation": "Ho partecipato al Ride for Children l\u2019anno scorso e sono rimasto colpito dall\u2019organizzazione del club.", "status": "approved",  "days_ago": 45},
    ],
}

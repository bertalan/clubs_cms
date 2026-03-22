"""
English demo data for ClubCMS.

This dictionary contains ALL data needed to populate a complete
standalone English-language site.  It is consumed by build_demo_db
to produce ``fixtures/demo/demo_en.sqlite3``, which in turn is
read by ``load_demo --lang en``.
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
        "language": "en",
        "site_name": "Moto Club Aquile Rosse",
        # Slug references used by the loader for image assignment
        "slug_about": "about-us",
        "slug_contact": "contact",
        "slug_event_mandello": "season-opener-mandello-2026",
        "slug_event_pisa": "moto-lands-pisa-2026",
        "slug_event_orobie": "orobie-tour-2026",
        "slug_event_franciacorta": "franciacorta-track-day-2026",
        "slug_event_children": "ride-for-children-2026",
        "slug_event_garda": "moto-rally-garda-2026",
        "slug_news_kickoff": "2026-season-kickoff",
        "slug_news_pisa": "moto-lands-pisa",
        "slug_news_bayern": "spring-franken-bayern-treffen",
        "slug_news_workshop": "workshop-bergamo-partnership",
        "slug_news_seasonal": "seasonal-motorcycle-prep",
        "slug_news_assembly": "2026-annual-assembly",
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
        {"cat_type": "news", "name": "Club News",        "slug": "club-news",        "color": "#B91C1C", "description": "News about club activities and communications", "icon": "", "sort_order": 0},
        {"cat_type": "news", "name": "Event Recaps",     "slug": "events-recap",     "color": "#059669", "description": "Reports and photos from past events",          "icon": "", "sort_order": 1},
        {"cat_type": "news", "name": "Motorcycle World", "slug": "motorcycle-world", "color": "#7C3AED", "description": "News from the world of motorcycling",          "icon": "", "sort_order": 2},
        {"cat_type": "news", "name": "Technical",        "slug": "technical",        "color": "#2563EB", "description": "Technical articles, reviews and maintenance",   "icon": "", "sort_order": 3},
        # Events
        {"cat_type": "event", "name": "Rally & Gathering", "slug": "rally",          "color": "", "description": "", "icon": "rally",      "sort_order": 0},
        {"cat_type": "event", "name": "Touring Ride",      "slug": "touring",        "color": "", "description": "", "icon": "motorcycle",  "sort_order": 1},
        {"cat_type": "event", "name": "Social Meeting",    "slug": "social-meeting", "color": "", "description": "", "icon": "meeting",     "sort_order": 2},
        {"cat_type": "event", "name": "Track Day",         "slug": "track-day",      "color": "", "description": "", "icon": "race",        "sort_order": 3},
        {"cat_type": "event", "name": "Charity Ride",      "slug": "charity-ride",   "color": "", "description": "", "icon": "charity",     "sort_order": 4},
        # Partners
        {"cat_type": "partner", "name": "Main Sponsor",       "slug": "main-sponsor",      "color": "", "description": "", "icon": "", "sort_order": 1},
        {"cat_type": "partner", "name": "Technical Partner",  "slug": "technical-partner",  "color": "", "description": "", "icon": "", "sort_order": 2},
        {"cat_type": "partner", "name": "Media Partner",      "slug": "media-partner",      "color": "", "description": "", "icon": "", "sort_order": 3},
    ],

    # ==================================================================
    # PRODUCTS
    # ==================================================================
    "products": [
        {"name": "Standard Membership", "slug": "standard-membership", "translation_key": "standard", "description": "Annual membership with voting rights and event participation.", "price": "50.00", "grants_vote": True, "grants_events": True, "grants_upload": True, "grants_discount": False, "discount_percent": 0, "sort_order": 1},
        {"name": "Supporter Membership", "slug": "supporter-membership", "translation_key": "supporter", "description": "Supporter membership with event discounts and gallery access.", "price": "30.00", "grants_vote": False, "grants_events": True, "grants_upload": False, "grants_discount": True, "discount_percent": 10, "sort_order": 2},
        {"name": "Premium Membership", "slug": "premium-membership", "translation_key": "premium", "description": "Premium membership with all privileges and 20% event discount.", "price": "100.00", "grants_vote": True, "grants_events": True, "grants_upload": True, "grants_discount": True, "discount_percent": 20, "sort_order": 3},
    ],

    # ==================================================================
    # TESTIMONIALS
    # ==================================================================
    "testimonials": [
        {"quote": "Joining this club completely changed the way I experience riding. The Sunday rides and rallies are truly unforgettable moments.", "author_name": "Marco Bianchi", "author_role": "Member since 2019", "featured": True},
        {"quote": "The mutual support among members is extraordinary. Once I broke down on Stelvio Pass, and within 30 minutes help was already on its way.", "author_name": "Giulia Ferrara", "author_role": "Member since 2021", "featured": True},
        {"quote": "The club-organised tours are always flawless: breathtaking routes, great food stops and wonderful company.", "author_name": "Alessandro Rossi", "author_role": "Founding member", "featured": False},
    ],

    # ==================================================================
    # FAQs
    # ==================================================================
    "faqs": [
        {"question": "How can I join the Moto Club?", "answer": "<p>You can join by completing the online registration form on our website, or by visiting the club premises during opening hours (Wednesday and Friday 20:30\u201323:00, Saturday 15:00\u201318:00). A valid photo ID and payment of the membership fee are required.</p>", "category": "Membership", "sort_order": 1},
        {"question": "How much does a membership card cost?", "answer": "<p>We offer three membership tiers:</p><ul><li><strong>Standard</strong>: \u20ac50/year \u2013 voting rights, events, gallery</li><li><strong>Supporter</strong>: \u20ac30/year \u2013 events, 10% discount</li><li><strong>Premium</strong>: \u20ac100/year \u2013 all privileges, 20% discount</li></ul>", "category": "Membership", "sort_order": 2},
        {"question": "Can I participate in events without being a member?", "answer": "<p>Some events are open to non-members (e.g. Ride for Children). For most club events a valid membership card is required. Non-members may attend as guests for a maximum of 2 outings before registering.</p>", "category": "Events", "sort_order": 3},
        {"question": "How does mutual aid work?", "answer": "<p>The mutual aid system lets members request and offer assistance for breakdowns or roadside emergencies. Each member indicates their skills (mechanics, transport, logistics) and availability radius on their profile. When help is needed the system notifies available members nearby.</p>", "category": "Services", "sort_order": 4},
    ],

    # ==================================================================
    # PHOTO TAGS
    # ==================================================================
    "photo_tags": [
        {"name": "Rally",    "slug": "rally"},
        {"name": "Tour",     "slug": "tour"},
        {"name": "Track Day","slug": "track-day"},
        {"name": "Social",   "slug": "social"},
        {"name": "Charity",  "slug": "charity"},
        {"name": "Panorama", "slug": "panorama"},
        {"name": "Bikes",    "slug": "bikes"},
    ],

    # ==================================================================
    # PRESS RELEASES
    # ==================================================================
    "press_releases": [
        {
            "title": "Moto Club Aquile Rosse announces the 2026 events calendar",
            "pub_date": "2026-01-28",
            "body": "<p>Moto Club Aquile Rosse ASD of Bergamo has presented the official events calendar for the 2026 season, featuring over 50 appointments including rallies, tours, track days and charitable initiatives.</p><p>Press contact: press@aquilerosse.it</p>",
            "is_archived": False,
        },
        {
            "title": "Ride for Children 2025: \u20ac8,500 raised for Paediatrics",
            "pub_date": "2025-10-15",
            "body": "<p>The 11th edition of the Ride for Children concluded with great success. The event drew more than 200 riders and raised \u20ac8,500, donated entirely to the Paediatrics ward of Papa Giovanni XXIII Hospital in Bergamo.</p>",
            "is_archived": False,
        },
    ],

    # ==================================================================
    # BRAND ASSETS
    # ==================================================================
    "brand_assets": [
        {"name": "Logo \u2013 Colour",        "category": "logo",     "description": "Official club logo in full colour. Vector SVG and high-resolution PNG. Use on light backgrounds.", "sort_order": 1},
        {"name": "Logo \u2013 White",         "category": "logo",     "description": "Official club logo in white monochrome for use on dark backgrounds.", "sort_order": 2},
        {"name": "Brand Guidelines",    "category": "template", "description": "Document with brand usage guidelines, official colours and club fonts.", "sort_order": 3},
    ],

    # ==================================================================
    # AID SKILLS
    # ==================================================================
    "aid_skills": [
        {"name": "Basic Mechanics",    "slug": "basic-mechanics",    "description": "Basic repairs: chain, spark plugs, fuses, adjustments.",                   "category": "mechanics",  "sort_order": 1},
        {"name": "Advanced Mechanics", "slug": "advanced-mechanics", "description": "Complex work: carburettors, electrical systems, brakes.",                  "category": "mechanics",  "sort_order": 2},
        {"name": "Motorcycle Transport","slug": "motorcycle-transport","description": "Van or trailer available for transporting a broken-down bike.",           "category": "transport",  "sort_order": 3},
        {"name": "First Aid",          "slug": "first-aid",          "description": "First-aid skills and emergency kit on board.",                             "category": "emergency",  "sort_order": 4},
        {"name": "Hospitality",        "slug": "hospitality",        "description": "Able to host passing members (overnight stay, garage).",                   "category": "logistics",  "sort_order": 5},
        {"name": "Roadside Recovery",  "slug": "roadside-recovery",  "description": "Assistance recovering bike and rider from difficult terrain.",             "category": "transport",  "sort_order": 6},
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
        {"key": "news_mandello",      "width": 800,  "height": 600,  "keywords": "motorcycle,rally",           "description": "News Season Opener"},
        {"key": "news_pisa",          "width": 800,  "height": 600,  "keywords": "motorcycle,italy",           "description": "News MotoLands Pisa"},
        {"key": "news_bayern",        "width": 800,  "height": 600,  "keywords": "motorcycle,germany",         "description": "News Bayern Treffen"},
        {"key": "news_officina",      "width": 800,  "height": 600,  "keywords": "motorcycle,workshop",        "description": "News Workshop"},
        {"key": "news_manutenzione",  "width": 800,  "height": 600,  "keywords": "motorcycle,engine,repair",   "description": "News Seasonal Prep"},
        {"key": "news_assemblea",     "width": 800,  "height": 600,  "keywords": "meeting,people",             "description": "News Assembly"},
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
        {"name": "Historical",    "slug": "historical"},
        {"name": "Panoramic",     "slug": "panoramic"},
        {"name": "Meeting Point", "slug": "meeting-point"},
        {"name": "Food & Drink",  "slug": "food-drink"},
        {"name": "Scenic",        "slug": "scenic"},
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
                "hero_subtitle": "Passion, adventure and brotherhood on two wheels since 1987",
                "primary_cta_text": "Upcoming Events",
                "secondary_cta_text": "Become a Member",
                "body": [
                    _rt("<h2>Welcome to Moto Club Aquile Rosse</h2><p>Since 1987, we have turned a passion for two wheels into memorable rides, lasting friendships and initiatives that connect the road with a true club spirit.</p><p>With more than 250 active members across Lombardy, we organise rallies, scenic tours, track days and charity events for riders who want every season to feel alive.</p>"),
                    _stats([
                        {"number": "250+", "label": "Active Members"},
                        {"number": "37", "label": "Years of History"},
                        {"number": "50+", "label": "Events / Year"},
                        {"number": "12", "label": "National Tours"},
                    ]),
                    _cta("Join Us", "Join the club, unlock members-only activities and share tours, events and new roads with a community that rides all year long.", "Explore Memberships", "/en/membership/"),
                ],
            },
        },

        # ---- About ----
        {
            "slug": "about-us",
            "page_type": "about",
            "parent_slug": "home",
            "translation_key": TK["about"],
            "title": "About Us",
            "fields": {
                "intro": "<p>Moto Club Aquile Rosse was founded in 1987 in Bergamo by a group of passionate motorcyclists who wanted to share their love of two wheels in a spirit of friendship and solidarity.</p><p>Today the club has over 250 registered members, with headquarters at Via Borgo Palazzo 22, Bergamo. We are affiliated with the FMI (Italian Motorcycling Federation) and organise more than 50 events each year.</p>",
                "body": [
                    _rt("<h2>Our History</h2><p>Founded as a small group of friends meeting every Sunday for a ride on the roads around Bergamo, the club has grown into one of the most active in Lombardy.</p><h3>Our Values</h3><ul><li><strong>Passion</strong>: Motorcycling is our way of life</li><li><strong>Safety</strong>: Responsible riding and continuous training</li><li><strong>Solidarity</strong>: Mutual aid among members</li><li><strong>Inclusivity</strong>: All makes and models welcome</li></ul>"),
                    _timeline("Key Milestones", [
                        {"year": "1987", "title": "Foundation", "description": "12 friends found Moto Club Aquile Rosse in Bergamo."},
                        {"year": "1995", "title": "FMI Affiliation", "description": "The club affiliates with the Italian Motorcycling Federation."},
                        {"year": "2005", "title": "New Headquarters", "description": "The new club premises at Via Borgo Palazzo are inaugurated."},
                        {"year": "2015", "title": "250 Members", "description": "The club reaches the milestone of 250 active members."},
                        {"year": "2024", "title": "Federation", "description": "Launch of the federation programme with partner clubs across Italy."},
                    ]),
                ],
            },
        },

        # ---- Board ----
        {
            "slug": "board-of-directors",
            "page_type": "board",
            "parent_slug": "about-us",
            "translation_key": TK["board"],
            "title": "Board of Directors",
            "fields": {
                "intro": "<p>The Board of Directors leads the club with passion and dedication.</p>",
                "body": [
                    _team_grid(3, [
                        {"name": "Roberto Colombo", "role": "President", "bio": "Motorcyclist for 40 years, leading the club since 2015. Passionate about long-distance touring."},
                        {"name": "Francesca Moretti", "role": "Vice President", "bio": "Mechanical engineer and safe-riding instructor. Organises the club\u2019s training courses."},
                        {"name": "Luca Bernardi", "role": "Secretary", "bio": "Manages memberships, communications and the club website."},
                        {"name": "Chiara Fontana", "role": "Treasurer", "bio": "Accountant by profession, has kept the club\u2019s finances in order since 2020."},
                        {"name": "Davide Marchetti", "role": "Events Manager", "bio": "Plans and organises all club events. Specialist in logistics and route planning."},
                        {"name": "Elena Rizzo", "role": "Communications Manager", "bio": "Journalist and social media manager. Handles newsletter and social channels."},
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
                "intro": "<p>All the latest from Moto Club Aquile Rosse.</p>",
            },
        },

        # ---- News Articles ----
        {
            "slug": "2026-season-kickoff",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_kickoff"],
            "title": "Season Opener 2026: Back to Mandello!",
            "fields": {
                "intro": "The traditional season-opening rally returns to Mandello del Lario with surprises in store for all motorcycle enthusiasts.",
                "display_date": "-3",
                "category": "club-news",
                "body": [_rt("<p>As every year, the riding season kicks off with the traditional <strong>Season Opener</strong> at Mandello del Lario.</p><p>The event features a packed programme: from the lakeside parade to guided tours of the motorcycle museum, culminating in a club dinner at Ristorante Il Griso.</p><h3>Programme</h3><ul><li>09:00 \u2013 Meet at Piazza Garibaldi</li><li>10:30 \u2013 Parade along Lake Como</li><li>12:30 \u2013 Club lunch</li><li>15:00 \u2013 Motorcycle museum visit</li><li>18:00 \u2013 Aperitif and prize-giving</li></ul><p>Moto Club Aquile Rosse will attend with a delegation of 30 members. Registrations are open until 15 March.</p>")],
            },
        },
        {
            "slug": "moto-lands-pisa",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_pisa"],
            "title": "1st Moto Lands of Pisa: New Event in Tuscany",
            "fields": {
                "intro": "A new motorcycle rally is born at Pontedera, in the land of Piaggio and just a stone\u2019s throw from the Leaning Tower.",
                "display_date": "-7",
                "category": "motorcycle-world",
                "body": [_rt("<p>Exciting news from the Italian rally scene: the <strong>1st Moto Lands of Pisa</strong> has been announced, to be held at Pontedera (PI) in spring 2026.</p><p>Organised by Moto Club Terre di Pisa, it promises a weekend steeped in Tuscan motorcycling culture: guided rides through the Pisan hills, tastings of local produce and a static display in the historic town centre.</p><p>Our club is already planning a group trip. Interested members should contact events manager Davide Marchetti.</p>")],
            },
        },
        {
            "slug": "spring-franken-bayern-treffen",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_bayern"],
            "title": "Recap: Spring Franken Bayern Treffen 2026",
            "fields": {
                "intro": "Eight club members took part in the spring rally in Bavaria. Here is the story of their adventure.",
                "display_date": "-14",
                "category": "events-recap",
                "body": [_rt("<p>Last weekend a group of 8 members crossed the Alps to attend the <strong>Spring Franken Bayern Treffen</strong>, the spring rally in the German region of Franconia.</p><p>The outbound route passed through the Brenner Pass, Innsbruck and Munich before reaching the Nuremberg area. The rally, attended by over 500 riders from across Europe, offered days of riding on the magnificent roads of Franconia, Bavarian beer and a wonderful spirit of camaraderie.</p>")],
            },
        },
        {
            "slug": "workshop-bergamo-partnership",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_workshop"],
            "title": "New Agreement with Officina Moto Bergamo",
            "fields": {
                "intro": "A new partnership agreement with Officina Moto Bergamo provides discounts on servicing and repairs for all members.",
                "display_date": "-20",
                "category": "club-news",
                "body": [_rt("<p>We are pleased to announce a new partnership with <strong>Officina Moto Bergamo</strong>, a multi-brand service centre located at Via Seriate 42.</p><p>All members will be entitled to:</p><ul><li>15% off routine servicing</li><li>10% off spare parts</li><li>Free electronic diagnostics</li><li>Priority booking during peak season</li></ul><p>Simply present a valid membership card to access the benefits.</p>")],
            },
        },
        {
            "slug": "seasonal-motorcycle-prep",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_seasonal"],
            "title": "Getting Your Bike Ready for the Season",
            "fields": {
                "intro": "Our trusted mechanic\u2019s tips for bringing your motorcycle back to peak condition after the winter break.",
                "display_date": "-30",
                "category": "technical",
                "body": [_rt("<p>With the warmer months approaching it\u2019s time to prepare your bike for the first rides.</p><h3>Essential Checks</h3><ol><li><strong>Battery</strong>: Check charge and electrolyte levels.</li><li><strong>Tyres</strong>: Check pressure, tread depth and DOT date.</li><li><strong>Brakes</strong>: Check pad thickness and brake fluid.</li><li><strong>Engine oil</strong>: Change oil and filter.</li><li><strong>Chain</strong>: Clean, lubricate and check tension.</li><li><strong>Lights</strong>: Test all lights including indicators.</li></ol>")],
            },
        },
        {
            "slug": "2026-annual-assembly",
            "page_type": "news",
            "parent_slug": "news",
            "translation_key": TK["news_assembly"],
            "title": "2026 Annual General Meeting: Accounts Approved",
            "fields": {
                "intro": "The annual general meeting unanimously approved the financial statements and the events programme for the coming year.",
                "display_date": "-45",
                "category": "club-news",
                "body": [_rt("<p>Last Saturday the annual general meeting was held at the club premises.</p><p>With 142 of the 258 eligible members present, the AGM unanimously approved the 2025 financial statements and the 2026 budget.</p><h3>Key Points</h3><ul><li>Existing board confirmed for the 2026\u20132027 term</li><li>Events calendar approved with 52 scheduled outings</li><li>New partnerships agreed with 3 affiliated workshops</li><li>Launch of the federation programme</li><li>Purchase of a defibrillator for the clubhouse</li></ul>")],
            },
        },

        # ---- Events Page ----
        {
            "slug": "events",
            "page_type": "events_page",
            "parent_slug": "home",
            "translation_key": TK["events_page"],
            "title": "Events",
            "fields": {
                "intro": "<p>All events organised and supported by Moto Club Aquile Rosse.</p>",
            },
        },

        # ---- Event Details ----
        {
            "slug": "season-opener-mandello-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_mandello"],
            "title": "Season Opener 2026 \u2013 Mandello del Lario",
            "fields": {
                "intro": "The traditional season-opening rally in Mandello del Lario.",
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
                "body": [_rt("<p>Join us for the <strong>Season Opener 2026</strong>, the rally that officially marks the start of the riding season on the shores of Lake Como.</p><h3>What\u2019s Included</h3><ul><li>Scenic parade along Lake Como</li><li>Club lunch (included in the fee)</li><li>Motorcycle museum visit</li><li>Commemorative gift</li></ul>")],
            },
        },
        {
            "slug": "moto-lands-pisa-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_pisa"],
            "title": "1st Moto Lands of Pisa",
            "fields": {
                "intro": "First motorcycle rally in the land of Pontedera, among the Tuscan hills.",
                "start_date": "+60",
                "end_date": "+62",
                "location_name": "Historic Centre, Pontedera",
                "location_address": "Piazza Martiri della Libert\u00e0, 56025 Pontedera PI",
                "location_coordinates": "43.6631,10.6322",
                "category": "rally",
                "registration_open": True,
                "max_attendees": 300,
                "base_fee": "40.00",
                "early_bird_discount": 15,
                "early_bird_deadline": "+45",
                "member_discount_percent": 10,
                "body": [_rt("<p>A weekend in beautiful Tuscany for the first <strong>Moto Lands of Pisa</strong>.</p><p>The programme includes guided tours through the Pisan hills, a visit to the Piaggio Museum in Pontedera, tastings of local produce and a static display in the town square.</p>")],
            },
        },
        {
            "slug": "orobie-tour-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_orobie"],
            "title": "Orobie Mountain Tour \u2013 Club Day Out",
            "fields": {
                "intro": "A day ride through the Bergamo valleys with a mountain-hut lunch stop.",
                "start_date": "+14",
                "end_date": "+14",
                "location_name": "Club Headquarters, Bergamo",
                "location_address": "Via Borgo Palazzo 22, 24121 Bergamo",
                "location_coordinates": "45.6983,9.6773",
                "category": "touring",
                "registration_open": True,
                "max_attendees": 40,
                "base_fee": "15.00",
                "early_bird_discount": 0,
                "member_discount_percent": 100,
                "body": [_rt("<p>A club day out in the magnificent <strong>Orobie Alps</strong>, covering approximately 180 km through the Bergamo valleys.</p><p>Departure from the clubhouse at 08:30. Route: Bergamo \u2192 Val Seriana \u2192 Passo della Presolana \u2192 Val di Scalve \u2192 Lake Iseo \u2192 Bergamo. Lunch stop at Rifugio Albani.</p><p><em>Free for members with a valid membership card.</em></p>")],
            },
        },
        {
            "slug": "franciacorta-track-day-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_franciacorta"],
            "title": "Track Day \u2013 Franciacorta Circuit",
            "fields": {
                "intro": "A full day on track at Franciacorta Circuit with professional instructors.",
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
                "body": [_rt("<p>A day dedicated to safe sporting riding at <strong>Franciacorta Circuit</strong>.</p><ul><li>Technical and safety briefing</li><li>3 track sessions of 20 minutes each</li><li>Personalised coaching</li><li>Lunch at the circuit</li></ul><p>Mandatory: full leather suit, gloves, technical boots, full-face helmet.</p>")],
            },
        },
        {
            "slug": "ride-for-children-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_children"],
            "title": "Charity: Ride for Children",
            "fields": {
                "intro": "Charity motorcycle ride in aid of Bergamo Children\u2019s Hospital.",
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
                "body": [_rt("<p>The <strong>Ride for Children</strong> is the annual charity event of Moto Club Aquile Rosse, now in its 12th edition.</p><p>All registration proceeds will be donated to the Paediatrics ward of Papa Giovanni XXIII Hospital in Bergamo.</p><p><strong>Open to everyone \u2014 members and non-members alike!</strong></p>")],
            },
        },
        {
            "slug": "moto-rally-garda-2026",
            "page_type": "event",
            "parent_slug": "events",
            "translation_key": TK["event_garda"],
            "title": "Moto Rally Garda 2026",
            "fields": {
                "intro": "Motorcycle rally on Lake Garda with parade and live music.",
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
                "body": [_rt("<p>The <strong>Moto Rally Garda</strong> is one of the largest motorcycle gatherings in northern Italy.</p><p>Four days of bikes, music, food trucks and the famous Thunder Parade along the lakeshore.</p>")],
            },
        },

        # ---- Gallery ----
        {
            "slug": "gallery",
            "page_type": "gallery",
            "parent_slug": "home",
            "translation_key": TK["gallery"],
            "title": "Gallery",
            "fields": {
                "intro": "<p>The best photos from our events, tours and rallies.</p>",
            },
        },

        # ---- Contact ----
        {
            "slug": "contact",
            "page_type": "contact",
            "parent_slug": "home",
            "translation_key": TK["contact"],
            "title": "Contact",
            "fields": {
                "hero_badge": "We\u2019re here for you",
                "intro": "<p>Have questions? Want to know more about the club? Get in touch!</p>",
                "form_title": "Send Us a Message",
                "success_message": "<p>Thank you for your message! We will reply within 48 hours.</p>",
                "captcha_enabled": True,
                "captcha_provider": "honeypot",
                "membership_title": "Become a Member",
                "membership_description": "Join our community of over 250 motorcyclists. Access to all events, partner discounts, insurance and roadside assistance included.",
                "membership_price": "Annual fee \u20ac80",
                "membership_cta_text": "Join Now",
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
                "body": [_rt("<h2>Privacy Notice</h2><p>Pursuant to Regulation (EU) 2016/679 (GDPR), Moto Club Aquile Rosse ASD, acting as Data Controller, informs you that personal data collected through this website will be processed in accordance with applicable legislation.</p><h3>Data Collected</h3><p>First name, last name, email address, telephone number (optional) and browsing data.</p><h3>Purposes</h3><ul><li>Managing club memberships</li><li>Organising events and communications</li><li>Legal compliance</li></ul><h3>Your Rights</h3><p>Access, rectification, erasure and portability: privacy@aquilerosse.it</p>")],
            },
        },

        # ---- Transparency ----
        {
            "slug": "transparency",
            "page_type": "transparency",
            "parent_slug": "home",
            "translation_key": TK["transparency"],
            "title": "Transparency",
            "fields": {
                "intro": "<p>In compliance with regulations governing amateur sports associations, we publish the club\u2019s official documents.</p>",
                "body": [_rt("<h2>Club Documents</h2><p>The articles of association, financial statements and AGM minutes are available for inspection by members and supervisory bodies.</p><h3>Articles of Association</h3><p>Approved at the founding meeting on 15 March 1987, last updated 20 January 2024.</p><h3>Financial Statements</h3><ul><li>2025 Annual Accounts \u2013 Approved 25/01/2026</li><li>2024 Annual Accounts \u2013 Approved 28/01/2025</li></ul>")],
            },
        },

        # ---- Press ----
        {
            "slug": "press",
            "page_type": "press",
            "parent_slug": "home",
            "translation_key": TK["press"],
            "title": "Press Room",
            "fields": {
                "intro": "<p>Press materials and media contacts.</p>",
                "press_email": "press@aquilerosse.it",
                "press_phone": "+39 035 123 4568",
                "press_contact": "Elena Rizzo \u2013 Communications Manager",
                "body": [_rt("<p>For press enquiries, interviews or photographic material please contact the club communications office.</p>")],
            },
        },

        # ---- Membership Plans ----
        {
            "slug": "membership",
            "page_type": "membership_plans",
            "parent_slug": "home",
            "translation_key": TK["membership_plans"],
            "title": "Become a Member",
            "fields": {
                "intro": "<p>Choose the membership plan that best suits your needs.</p>",
            },
        },

        # ---- Federation ----
        {
            "slug": "federation",
            "page_type": "federation",
            "parent_slug": "home",
            "translation_key": TK["federation"],
            "title": "Federation",
            "fields": {
                "intro": "<p>Our network of partner clubs shares events, initiatives and opportunities for all members.</p>",
                "how_it_works": [
                    _step("How the Federation Works", [
                        {"year": "1", "title": "Discover partner clubs", "description": "<p>Browse the list of federated clubs and find out about their activities.</p>"},
                        {"year": "2", "title": "Explore shared events", "description": "<p>Browse events published by partner clubs. Filter by club, search by name.</p>"},
                        {"year": "3", "title": "Express your interest", "description": "<p>Indicate whether you are interested, undecided or definitely attending. The organising club only receives anonymous aggregate counts.</p>"},
                        {"year": "4", "title": "Discuss with fellow members", "description": "<p>Talk about events with other members of your club. Comments are private.</p>"},
                    ]),
                ],
                "faq": [
                    _faq_block("Frequently Asked Questions", [
                        {"question": "What is the club federation?", "answer": "<p>A voluntary network of clubs sharing events through a secure protocol. Every club retains full autonomy.</p>"},
                        {"question": "Is my personal data shared?", "answer": "<p>No. Only event data and anonymous aggregate counts are exchanged.</p>"},
                        {"question": "How is security guaranteed?", "answer": "<p>Unique API keys per club. HTTPS with HMAC authentication. Validated data.</p>"},
                    ]),
                ],
                "body": [_rt("<h2>Benefits</h2><ul><li><strong>More events</strong> \u2014 Shared calendar with dozens of appointments.</li><li><strong>New friendships</strong> \u2014 Meet enthusiasts from partner clubs.</li><li><strong>Privacy guaranteed</strong> \u2014 Your data stays within our club.</li></ul>")],
                "cta_text": "Explore partner events",
                "cta_url": "/en/federation/",
            },
        },

        # ---- Partner Index ----
        {
            "slug": "partners",
            "page_type": "partner_index",
            "parent_slug": "home",
            "translation_key": TK["partner_index"],
            "title": "Partners",
            "fields": {
                "intro": "<p>The partners and sponsors who support the activities of our club.</p>",
            },
        },

        # ---- Partner Pages ----
        {
            "slug": "officina-moto-bergamo",
            "page_type": "partner",
            "parent_slug": "partners",
            "translation_key": TK["partner_officina"],
            "title": "Officina Moto Bergamo",
            "fields": {
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
                "partnership_start": "2023-01-01",
                "body": [_rt("<p>Officina Moto Bergamo is the official technical partner. Full-service support on all makes with certified staff.</p><p>Exclusive discounts for members on servicing, repairs and spare parts.</p>")],
            },
        },
        {
            "slug": "lecco-motorcycle-dealership",
            "page_type": "partner",
            "parent_slug": "partners",
            "translation_key": TK["partner_concessionaria"],
            "title": "Concessionaria Moto Lecco",
            "fields": {
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
                "partnership_start": "2020-06-01",
                "body": [_rt("<p>Official dealership for the province of Lecco. Main club sponsor since 2020, supporting events with demo rides and technical assistance.</p>")],
            },
        },
        {
            "slug": "bergamo-moto-magazine",
            "page_type": "partner",
            "parent_slug": "partners",
            "translation_key": TK["partner_magazine"],
            "title": "Bergamo Moto Magazine",
            "fields": {
                "intro": "Online magazine dedicated to motorcycling in Bergamo and Lombardy.",
                "category": "media-partner",
                "website": "https://www.example.com/bg-moto-mag",
                "email": "editorial@bgmotomag.it",
                "contact_city": "Bergamo",
                "is_featured": False,
                "show_on_homepage": True,
                "partnership_start": "2022-03-01",
                "body": [_rt("<p>Bergamo Moto Magazine is our media partner: it covers all club events with articles, photos and videos.</p>")],
            },
        },

        # ---- Place Index ----
        {
            "slug": "places",
            "page_type": "place_index",
            "parent_slug": "home",
            "translation_key": TK["place_index"],
            "title": "Places",
            "fields": {
                "intro": "<p>Discover the places connected to our community: club headquarters, monuments, squares and tourist routes across Italy.</p>",
            },
        },

        # ---- Places ----
        {
            "slug": "club-headquarters",
            "page_type": "place",
            "parent_slug": "places",
            "translation_key": TK["place_hq"],
            "title": "Moto Club Aquile Rosse HQ",
            "fields": {
                "place_type": "clubhouse",
                "latitude": "45.694200",
                "longitude": "9.670000",
                "address": "Via Borgo Palazzo 42",
                "city": "Bergamo",
                "province": "BG",
                "postal_code": "24125",
                "short_description": "The official headquarters of Moto Club Aquile Rosse, where riders meet every weekend.",
                "description": "<p>Located in the heart of Bergamo, our clubhouse has been the gathering point for motorcycle enthusiasts since 2005. Open to all members with a valid card.</p>",
                "opening_hours": "Sa-Su 09:00-18:00",
                "phone": "+39 035 123 4567",
                "website_url": "https://example.com/aquile-rosse",
                "_tags": ["Meeting Point"],
            },
        },
        {
            "slug": "colosseum",
            "page_type": "place",
            "parent_slug": "places",
            "translation_key": TK["place_colosseum"],
            "title": "Colosseum",
            "fields": {
                "place_type": "monument",
                "latitude": "41.890210",
                "longitude": "12.492231",
                "address": "Piazza del Colosseo 1",
                "city": "Roma",
                "province": "RM",
                "postal_code": "00184",
                "short_description": "The iconic Roman amphitheatre, starting point for the annual ride.",
                "description": "<p>The Colosseum is the largest ancient amphitheatre ever built. It\u2019s our traditional starting point for the annual \u2018Roma Caput Mundi\u2019 ride.</p>",
                "_tags": ["Historical", "Scenic"],
            },
        },
        {
            "slug": "piazza-del-campo",
            "page_type": "place",
            "parent_slug": "places",
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
                "short_description": "Siena\u2019s shell-shaped main square, a mandatory stop on our Tuscany tour.",
                "description": "<p>The stunning Piazza del Campo is famous for the Palio horse race. We stop here for lunch during our annual Tuscan ride.</p>",
                "_tags": ["Historical", "Scenic", "Panoramic"],
            },
        },
        {
            "slug": "trattoria-da-mario",
            "page_type": "place",
            "parent_slug": "places",
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
                "short_description": "An authentic Florentine trattoria, partner restaurant for club members.",
                "description": "<p>Family-run trattoria since 1953. Club members get 10% discount showing a valid membership card.</p>",
                "opening_hours": "Mo-Sa 12:00-15:00",
                "phone": "+39 055 218550",
                "_tags": ["Food & Drink"],
            },
        },
        {
            "slug": "stelvio-pass",
            "page_type": "place",
            "parent_slug": "places",
            "translation_key": TK["place_stelvio"],
            "title": "Stelvio Pass",
            "fields": {
                "place_type": "poi",
                "latitude": "46.528611",
                "longitude": "10.453333",
                "address": "SS38",
                "city": "Bormio",
                "province": "SO",
                "postal_code": "23032",
                "short_description": "The highest paved mountain pass in the Eastern Alps \u2014 a legendary motorcycle road.",
                "description": "<p>At 2,757 metres, Stelvio Pass offers 48 hairpin bends on the north side alone. Open June to November, weather permitting.</p>",
                "_tags": ["Scenic", "Panoramic"],
            },
        },

        # ---- Route ----
        {
            "slug": "roman-ride",
            "page_type": "route",
            "parent_slug": "places",
            "translation_key": TK["route_roman"],
            "title": "The Roman Ride",
            "fields": {
                "short_description": "A scenic half-day ride from the Colosseum through the hills south of Rome.",
                "description": "<p>Starting at the Colosseum, this route takes you through Via Appia Antica and into the Castelli Romani countryside. Perfect for a Sunday morning ride.</p>",
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
        {"route_slug": "roman-ride", "place_slug": "club-headquarters", "sort_order": 1, "note": "Meeting point at 8:00 AM"},
        {"route_slug": "roman-ride", "place_slug": "colosseum",         "sort_order": 2, "note": "Photo stop at the amphitheatre"},
    ],

    # ==================================================================
    # NAVBAR
    # ==================================================================
    "navbar_items": [
        # Top-level
        {"label": "About Us", "link_page_slug": "about-us", "link_url": "", "sort_order": 0, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "News",     "link_page_slug": "news",     "link_url": "", "sort_order": 1, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Events",   "link_page_slug": "events",   "link_url": "", "sort_order": 2, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Gallery",  "link_page_slug": "gallery",  "link_url": "", "sort_order": 3, "parent_label": "", "is_cta": False, "open_new_tab": False},
        {"label": "Services", "link_page_slug": "",          "link_url": "", "sort_order": 4, "parent_label": "", "is_cta": False, "open_new_tab": False},
        # Sub: About Us
        {"label": "History",            "link_page_slug": "about-us",           "link_url": "", "sort_order": 0, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Contact",            "link_page_slug": "contact",            "link_url": "", "sort_order": 1, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Become a Member",    "link_page_slug": "membership",         "link_url": "", "sort_order": 2, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Board of Directors", "link_page_slug": "board-of-directors", "link_url": "", "sort_order": 3, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Transparency",       "link_page_slug": "transparency",       "link_url": "", "sort_order": 4, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Member Card",        "link_page_slug": "",                   "link_url": "reverse:account:card", "sort_order": 5, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        {"label": "Partners",           "link_page_slug": "partners",           "link_url": "", "sort_order": 6, "parent_label": "About Us", "is_cta": False, "open_new_tab": False},
        # Sub: Services
        {"label": "Roadside Assistance", "link_page_slug": "",          "link_url": "reverse:mutual_aid:map",          "sort_order": 0, "parent_label": "Services", "is_cta": False, "open_new_tab": False},
        {"label": "Federation Events",   "link_page_slug": "federation","link_url": "",                                 "sort_order": 1, "parent_label": "Services", "is_cta": False, "open_new_tab": False},
        {"label": "Contributions",       "link_page_slug": "",          "link_url": "reverse:account:my_contributions", "sort_order": 2, "parent_label": "Services", "is_cta": False, "open_new_tab": False},
        {"label": "Notifications",       "link_page_slug": "",          "link_url": "reverse:account:notifications",    "sort_order": 3, "parent_label": "Services", "is_cta": False, "open_new_tab": False},
        {"label": "Press Room",          "link_page_slug": "press",     "link_url": "",                                 "sort_order": 4, "parent_label": "Services", "is_cta": False, "open_new_tab": False},
    ],

    # ==================================================================
    # FOOTER
    # ==================================================================
    "footer_items": [
        {"label": "About Us",     "link_page_slug": "about-us",     "link_url": "", "sort_order": 0},
        {"label": "News",         "link_page_slug": "news",         "link_url": "", "sort_order": 1},
        {"label": "Events",       "link_page_slug": "events",       "link_url": "", "sort_order": 2},
        {"label": "Privacy",      "link_page_slug": "privacy",      "link_url": "", "sort_order": 3},
        {"label": "Transparency", "link_page_slug": "transparency", "link_url": "", "sort_order": 4},
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
        "tagline": "Passion, adventure and brotherhood on two wheels since 1987",
        "description": "Official website of Moto Club Aquile Rosse ASD of Bergamo. Rallies, tours, track days and charity events for motorcyclists of all makes.",
        "theme": "velocity",
        "phone": "+39 035 123 4567",
        "email": "info@aquilerosse.it",
        "address": "Via Borgo Palazzo 22\n24121 Bergamo (BG)\nItaly",
        "hours": "Wed/Fri 20:30-23:00, Sat 15:00-18:00",
        "facebook_url": "https://www.facebook.com/motoclubaquilerosse",
        "instagram_url": "https://www.instagram.com/aquilerosse_mc",
        "youtube_url": "https://www.youtube.com/@aquilerossemc",
        "map_default_center": "45.6983,9.6773",
        "map_default_zoom": "12",
        "footer_description": "<p>Moto Club Aquile Rosse ASD \u2013 Passion, adventure and brotherhood on two wheels since 1987.</p>",
        "copyright_text": "\u00a9 2026 Moto Club Aquile Rosse ASD. All rights reserved.",
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
            "bio": "Motorcycle rider since 1998. Passionate about V7s and mountain roads. Hobby mechanic, always ready to lend a hand.",
            "aid_available": True, "aid_radius_km": 30,
            "aid_location_city": "Bergamo", "aid_coordinates": "45.6983,9.6773",
            "aid_notes": "Basic tools and battery cables. Available weekends.",
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
            "bio": "Nurse and rider. First-aid certified, always carry an emergency kit on the bike.",
            "aid_available": True, "aid_radius_km": 50,
            "aid_location_city": "Seriate", "aid_coordinates": "45.6847,9.7267",
            "aid_notes": "First-aid skills. Also available weekdays after 18:00.",
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
            "bio": "Founding member. Former motorcycle mechanic at Mandello. Have an equipped van for bike transport. Ride a V85 TT.",
            "aid_available": True, "aid_radius_km": 100,
            "aid_location_city": "Lecco", "aid_coordinates": "45.8566,9.3977",
            "aid_notes": "Van with ramp for motorcycle transport. Advanced mechanics. Almost always available, call mobile.",
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
            "bio": "Accountant and club treasurer. Passionate about long-distance two-wheel touring. Often ride solo to Alpine passes.",
            "aid_available": True, "aid_radius_km": 25,
            "aid_location_city": "Treviglio", "aid_coordinates": "45.5200,9.5900",
            "aid_notes": "Can host passing riders (garage and guest room).",
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
            "bio": "Club president. 40 years in the saddle, vintage motorcycle collector. Organise the annual club tours on hand-picked routes.",
            "aid_available": True, "aid_radius_km": 40,
            "aid_location_city": "Bergamo", "aid_coordinates": "45.6983,9.6773",
            "aid_notes": "Broad mechanical experience on classic and modern bikes. Professional tools at the clubhouse.",
            "show_in_directory": True, "public_profile": True, "newsletter": True,
            "image_key": "member_roberto",
        },
    ],

    # ==================================================================
    # AID REQUESTS
    # ==================================================================
    "aid_requests": [
        {"helper_username": "demo_alessandro", "requester_name": "Demo: Marco Bianchi", "requester_phone": "+39 333 111 2222", "requester_email": "marco.bianchi@example.com", "requester_username": "demo_marco", "issue_type": "breakdown", "description": "Motorcycle broken down on the SS38 between Lecco and Colico, km 42. Won\u2019t start \u2014 electrical fault. I\u2019m in the car park of Ristorante La Pergola.", "location": "SS38, Km 42 \u2013 Dervio (LC)", "urgency": "high", "status": "resolved"},
        {"helper_username": "demo_giulia", "requester_name": "Demo: Chiara Fontana", "requester_phone": "+39 333 444 5555", "requester_email": "chiara.fontana@example.com", "requester_username": "demo_chiara", "issue_type": "flat_tire", "description": "Rear tyre puncture on the Passo della Presolana road. No tubeless repair kit. I\u2019m at Rifugio Magnolini.", "location": "Passo della Presolana \u2013 Rifugio Magnolini (BG)", "urgency": "medium", "status": "resolved"},
        {"helper_username": "demo_roberto", "requester_name": "Demo: Giulia Ferrara", "requester_phone": "+39 333 222 3333", "requester_email": "giulia.ferrara@example.com", "requester_username": "demo_giulia", "issue_type": "fuel", "description": "Run out of fuel on the SP671 between Clusone and Bergamo. Nearest station was closed (Sunday evening). I\u2019m at Bar Sport in Gazzaniga.", "location": "SP671, Gazzaniga (BG)", "urgency": "low", "status": "resolved"},
        {"helper_username": "demo_alessandro", "requester_name": "Demo: Roberto Colombo", "requester_phone": "+39 333 555 6666", "requester_email": "roberto.colombo@example.com", "requester_username": "demo_roberto", "issue_type": "tow", "description": "Vintage bike with a broken gearbox on the way back from the Mandello rally. Need a van to transport the bike to the club premises (~60 km).", "location": "Mandello del Lario, Piazza Garibaldi (LC)", "urgency": "medium", "status": "in_progress"},
        {"helper_username": "demo_chiara", "requester_name": "Demo: Alessandro Rossi", "requester_phone": "+39 333 333 4444", "requester_email": "alessandro.rossi@example.com", "requester_username": "demo_alessandro", "issue_type": "accommodation", "description": "Returning from the Dolomites tour with a chain problem near Treviglio. Can\u2019t make another 80 km to Lecco tonight. Need a garage and a place to sleep.", "location": "Treviglio centre (BG)", "urgency": "medium", "status": "open"},
    ],

    # ==================================================================
    # FEDERATED CLUBS
    # ==================================================================
    "federated_clubs": [
        {"short_code": "MANDELLO", "name": "Moto Club Le Aquile \u2013 Mandello del Lario", "city": "Mandello del Lario", "base_url": "https://api.motoclubmandello.it", "logo_url": "/static/img/federation/mandello.svg", "description": "Historic club on the shores of Lake Como, a landmark for motorcycle enthusiasts in the Lecco area. They organise scenic rallies, lake tours and technical meetings.", "api_key": "demo_key_mandello_2026_abcdef1234567890", "is_active": True, "is_approved": True, "share_our_events": True},
        {"short_code": "PISA", "name": "Moto Club Terre di Pisa", "city": "Pisa", "base_url": "https://api.mcterre-pisa.it", "logo_url": "/static/img/federation/pisa.svg", "description": "Active club in the province of Pisa focused on touring and local culture. Tours through the Tuscan hills, food-and-wine events and rides to the Tyrrhenian coast.", "api_key": "demo_key_pisa_2026_abcdef1234567890", "is_active": True, "is_approved": True, "share_our_events": True},
        {"short_code": "MOTOGARDA", "name": "Moto Club Lago di Garda", "city": "Desenzano del Garda", "base_url": "https://api.motoclub-garda.it", "logo_url": "/static/img/federation/garda.svg", "description": "Lake Garda motorcycle club. Rallies, charity rides and weekend touring on the roads of Trentino and Veneto.", "api_key": "demo_key_garda_2026_abcdef1234567890", "is_active": True, "is_approved": False, "share_our_events": False},
    ],

    # ==================================================================
    # EXTERNAL EVENTS
    # ==================================================================
    "external_events": [
        {"club_short_code": "MANDELLO", "external_id": "mandello-apertura-2026", "event_name": "Season Opener 2026 \u2013 Mandello", "start_days_offset": 28, "end_days_offset": 29, "location_name": "Piazza Garibaldi, Mandello del Lario", "location_address": "23826 Mandello del Lario LC", "location_lat": 45.9167, "location_lon": 9.3167, "description": "Traditional season opener at Mandello del Lario. Lakeside parade, museum visit and club dinner.", "detail_url": "https://motoclubmandello.it/eventi/avviamento-2026", "is_approved": True},
        {"club_short_code": "MANDELLO", "external_id": "mandello-open-day", "event_name": "Open Day Mandello", "start_days_offset": 50, "end_days_offset": 50, "location_name": "Centro storico Mandello", "location_address": "Via Parodi 57, 23826 Mandello del Lario LC", "location_lat": 45.9200, "location_lon": 9.3200, "description": "Open doors at the historic Mandello factory. Guided tours of the production line and museum.", "detail_url": "https://motoclubmandello.it/eventi/open-day-2026", "is_approved": True},
        {"club_short_code": "PISA", "external_id": "pisa-lands-2026", "event_name": "1st Moto Lands of Pisa", "start_days_offset": 58, "end_days_offset": 60, "location_name": "Pontedera, Centro Storico", "location_address": "56025 Pontedera PI", "location_lat": 43.6631, "location_lon": 10.6322, "description": "First motorcycle rally in the land of Pontedera. Pisan hill tours, Piaggio Museum visit, tastings.", "detail_url": "https://mcterre-pisa.it/eventi/lands-of-pisa-2026", "is_approved": True},
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
        {"username": "demo_marco",      "event_external_id": "mandello-apertura-2026", "content": "We\u2019ll be there with 4 bikes from Bergamo! Who\u2019s joining the group?"},
        {"username": "demo_giulia",     "event_external_id": "mandello-apertura-2026", "content": "Count me in! Shall we ride together Saturday morning?"},
        {"username": "demo_alessandro", "event_external_id": "mandello-open-day",      "content": "The Open Day is always a unique experience. Highly recommended."},
    ],

    "federated_helpers": [
        {"club_short_code": "MANDELLO", "external_id": "mandello-helper-01", "display_name": "Luca M.",    "city": "Mandello del Lario", "latitude": 45.9170, "longitude": 9.3170, "radius_km": 30, "notes": "Expert mechanic, available with equipped van."},
        {"club_short_code": "MANDELLO", "external_id": "mandello-helper-02", "display_name": "Stefano B.", "city": "Lecco",              "latitude": 45.8530, "longitude": 9.3900, "radius_km": 40, "notes": "Motorcycle tow truck. Available weekends."},
        {"club_short_code": "PISA",     "external_id": "pisa-helper-01",     "display_name": "Andrea P.",  "city": "Pontedera",           "latitude": 43.6631, "longitude": 10.6322, "radius_km": 35, "notes": "Mobile workshop, roadside repairs."},
        {"club_short_code": "PISA",     "external_id": "pisa-helper-02",     "display_name": "Marco T.",   "city": "Pisa",                "latitude": 43.7228, "longitude": 10.4017, "radius_km": 25, "notes": "Motorcycle trailer transport. Available 24/7."},
    ],

    # ==================================================================
    # NOTIFICATIONS
    # ==================================================================
    "notifications": [
        {"notification_type": "event_reminder", "recipient_username": "demo_marco",  "channel": "in_app", "title": "Reminder: Orobie Tour in 3 days", "body": "The Orobie Tour is scheduled for Saturday. Meeting at 8:30 at the clubhouse.", "url_type": "page", "url_ref": "orobie-tour-2026", "status": "sent", "sent_hours_ago": 2},
        {"notification_type": "event_reminder", "recipient_username": "demo_giulia", "channel": "in_app", "title": "Reminder: Orobie Tour in 3 days", "body": "The Orobie Tour is scheduled for Saturday. Meeting at 8:30 at the clubhouse.", "url_type": "page", "url_ref": "orobie-tour-2026", "status": "sent", "sent_hours_ago": 2},
        {"notification_type": "event_reminder", "recipient_username": "demo_marco",  "channel": "in_app", "title": "Giulia replied to your comment", "body": "Giulia F. replied to your comment on \u20182026 Season Kick-off\u2019.", "url_type": "page", "url_ref": "2026-season-kickoff", "status": "sent", "sent_hours_ago": 12},
        {"notification_type": "membership_expiring", "recipient_username": "demo_giulia", "channel": "email", "title": "Your membership request has been approved!", "body": "Your Standard Membership Card request has been approved. The digital card is available in your profile.", "url_type": "reverse", "url_ref": "account:card", "status": "sent", "sent_hours_ago": 120},
        {"notification_type": "aid_request", "recipient_username": "demo_alessandro", "channel": "in_app", "title": "New roadside assistance request near you", "body": "Roberto C. needs motorcycle transport from Mandello del Lario. Distance: ~25 km.", "url_type": "reverse", "url_ref": "mutual_aid:map", "status": "sent", "sent_hours_ago": 36},
        {"notification_type": "event_published", "recipient_username": "demo_chiara", "channel": "in_app", "title": "New event: Franciacorta Track Day", "body": "A new event has been published: Track Day at Franciacorta Circuit. Registrations are open!", "url_type": "page", "url_ref": "franciacorta-track-day-2026", "status": "pending", "sent_hours_ago": 0},
        {"notification_type": "event_published", "recipient_username": "demo_roberto", "channel": "in_app", "title": "Your proposal has been approved", "body": "Your proposal \u20185-day Sardinia Tour\u2019 has been approved and published.", "url_type": "reverse", "url_ref": "account:my_contributions", "status": "sent", "sent_hours_ago": 24},
    ],

    # ==================================================================
    # EVENT REGISTRATIONS
    # ==================================================================
    "event_registrations": [
        {"username": "demo_marco",      "event_slug": "season-opener-mandello-2026", "status": "confirmed", "guests": 0, "notes": "", "days_ago": 10},
        {"username": "demo_giulia",     "event_slug": "season-opener-mandello-2026", "status": "confirmed", "guests": 0, "notes": "", "days_ago": 8},
        {"username": "demo_alessandro", "event_slug": "season-opener-mandello-2026", "status": "registered","guests": 0, "notes": "", "days_ago": 5},
        {"username": "demo_roberto",    "event_slug": "season-opener-mandello-2026", "status": "confirmed", "guests": 1, "notes": "", "days_ago": 12},
        {"username": "demo_marco",      "event_slug": "moto-lands-pisa-2026",        "status": "registered","guests": 0, "notes": "", "days_ago": 3},
        {"username": "demo_alessandro", "event_slug": "moto-lands-pisa-2026",        "status": "confirmed", "guests": 0, "notes": "", "days_ago": 7},
        {"username": "demo_giulia",     "event_slug": "orobie-tour-2026",            "status": "confirmed", "guests": 0, "notes": "", "days_ago": 2},
        {"username": "demo_chiara",     "event_slug": "orobie-tour-2026",            "status": "confirmed", "guests": 0, "notes": "", "days_ago": 4},
        {"username": "demo_roberto",    "event_slug": "orobie-tour-2026",            "status": "confirmed", "guests": 0, "notes": "", "days_ago": 6},
        {"username": "demo_marco",      "event_slug": "franciacorta-track-day-2026", "status": "confirmed", "guests": 0, "notes": "", "days_ago": 1},
        {"username": "demo_chiara",     "event_slug": "franciacorta-track-day-2026", "status": "waitlist",  "guests": 0, "notes": "", "days_ago": 1},
    ],

    # ==================================================================
    # EVENT FAVORITES
    # ==================================================================
    "event_favorites": [
        {"username": "demo_marco",      "event_slug": "season-opener-mandello-2026"},
        {"username": "demo_marco",      "event_slug": "orobie-tour-2026"},
        {"username": "demo_marco",      "event_slug": "ride-for-children-2026"},
        {"username": "demo_giulia",     "event_slug": "season-opener-mandello-2026"},
        {"username": "demo_giulia",     "event_slug": "moto-lands-pisa-2026"},
        {"username": "demo_giulia",     "event_slug": "ride-for-children-2026"},
        {"username": "demo_alessandro", "event_slug": "season-opener-mandello-2026"},
        {"username": "demo_alessandro", "event_slug": "franciacorta-track-day-2026"},
        {"username": "demo_chiara",     "event_slug": "orobie-tour-2026"},
        {"username": "demo_chiara",     "event_slug": "moto-rally-garda-2026"},
        {"username": "demo_roberto",    "event_slug": "season-opener-mandello-2026"},
        {"username": "demo_roberto",    "event_slug": "ride-for-children-2026"},
        {"username": "demo_roberto",    "event_slug": "moto-rally-garda-2026"},
    ],

    # ==================================================================
    # CONTRIBUTIONS
    # ==================================================================
    "contributions": [
        {"username": "demo_marco", "contribution_type": "story", "title": "My first ride with the club", "body": "It was a Saturday in April 2019 when I went on my first ride with the club. I didn\u2019t know anyone, I was nervous. But all it took was stopping at the first caf\u00e9 to realise these were my people. Since that day I have never missed a ride.", "status": "approved"},
        {"username": "demo_giulia", "contribution_type": "story", "title": "The Stelvio solo: fear and wonder", "body": "Last year I decided to tackle the Stelvio on my own. 48 hairpins, sudden fog, and halfway up a rear tyre pressure drop. I called mutual aid and in 30 minutes Alessandro was there with the van. That is what this club is about.", "status": "approved"},
        {"username": "demo_roberto", "contribution_type": "proposal", "title": "Proposal: 5-day Sardinia Tour", "body": "I propose a 5-day tour in Sardinia for September 2026. Route: Olbia \u2192 Costa Smeralda \u2192 Barbagia \u2192 Cagliari \u2192 Oristano \u2192 Alghero \u2192 Porto Torres. I have already contacted 3 biker-friendly B&Bs. Estimated budget: \u20ac600 per person (ferry, accommodation, breakfasts).", "status": "approved"},
        {"username": "demo_chiara", "contribution_type": "announcement", "title": "Membership renewal: deadline 31 March", "body": "Reminder: the deadline for renewing your 2026 membership card is 31 March. Members who renew before 15 March get a 10% discount. Renew online from your profile or in person at the clubhouse during opening hours.", "status": "approved"},
        {"username": "demo_alessandro", "contribution_type": "story", "title": "40 years in the saddle: my collection", "body": "I started collecting motorcycles in 1987, the year the club was founded. Today my garage holds 7 bikes: a Le Mans III from \u201981, a Stornello Sport from \u201968, a V7 Classic, a California 1400, a V85 TT, a V100 Mandello and a Griso 1200. Each one has a story.", "status": "pending"},
    ],

    # ==================================================================
    # COMMENTS
    # ==================================================================
    "comments": [
        {"username": "demo_marco",      "target_type": "news",  "target_index": 0, "content": "Great news! Mandello is always a must-attend. Who\u2019s coming with the Bergamo group?",  "moderation_status": "approved"},
        {"username": "demo_giulia",     "target_type": "news",  "target_index": 0, "content": "I\u2019ll be there! Who wants to join me for the lake loop in the afternoon?",             "moderation_status": "approved"},
        {"username": "demo_alessandro", "target_type": "news",  "target_index": 0, "content": "Present as every year. Bringing the Le Mans III too \u2014 should make an impression in the vintage area.", "moderation_status": "approved"},
        {"username": "demo_chiara",     "target_type": "news",  "target_index": 1, "content": "Tuscany on a motorbike is a dream. Already planning the trip with Giulia.",                "moderation_status": "approved"},
        {"username": "demo_roberto",    "target_type": "news",  "target_index": 2, "content": "The Bayern Treffen was fantastic. The roads of Franconia are among the best in Europe.",    "moderation_status": "approved"},
        {"username": "demo_marco",      "target_type": "event", "target_index": 0, "content": "Registered! Does anyone know a good hotel in Mandello?",                                  "moderation_status": "approved"},
        {"username": "demo_giulia",     "target_type": "event", "target_index": 1, "content": "Tuscany in spring\u2026 can\u2019t wait!",                                                "moderation_status": "approved"},
        {"username": "demo_roberto",    "target_type": "event", "target_index": 2, "content": "The Orobie mountains on a bike are spectacular. Beautiful route.",                          "moderation_status": "pending"},
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
        {"username": "demo_marco",      "activity_type": "login",          "description": "",                                           "days_ago": 0},
        {"username": "demo_marco",      "activity_type": "register",       "description": "Registered for Season Opener 2026",           "days_ago": 1},
        {"username": "demo_giulia",     "activity_type": "login",          "description": "",                                           "days_ago": 0},
        {"username": "demo_giulia",     "activity_type": "profile_update", "description": "Profile updated",                             "days_ago": 2},
        {"username": "demo_alessandro", "activity_type": "comment",        "description": "Commented on Season Opener 2026",              "days_ago": 3},
        {"username": "demo_chiara",     "activity_type": "login",          "description": "",                                           "days_ago": 1},
        {"username": "demo_roberto",    "activity_type": "login",          "description": "",                                           "days_ago": 0},
        {"username": "demo_roberto",    "activity_type": "reaction",       "description": "Reacted to 1st Moto Lands of Pisa",           "days_ago": 4},
    ],

    # ==================================================================
    # MEMBERSHIP REQUESTS
    # ==================================================================
    "membership_requests": [
        {"first_name": "Luca",    "last_name": "Moretti",   "email": "luca.moretti@example.com",   "phone": "+39 333 777 8888", "motivation": "I\u2019ve been riding for 5 years and would love to join a club that organises tours and events.", "status": "pending",   "days_ago": 3},
        {"first_name": "Sara",    "last_name": "De Luca",   "email": "sara.deluca@example.com",    "phone": "+39 333 888 9999", "motivation": "A friend recommended your club. I\u2019d like to meet other riders in the Bergamo area.",     "status": "pending",   "days_ago": 7},
        {"first_name": "Andrea",  "last_name": "Mazzini",   "email": "andrea.mazzini@example.com", "phone": "",                 "motivation": "Looking for a well-organised club focused on safety and touring.",                           "status": "approved",  "days_ago": 14},
        {"first_name": "Elena",   "last_name": "Colombo",   "email": "elena.colombo@example.com",  "phone": "+39 333 000 1111", "motivation": "",                                                                                           "status": "rejected",  "days_ago": 30},
        {"first_name": "Davide",  "last_name": "Russo",     "email": "davide.russo@example.com",   "phone": "+39 333 111 0000", "motivation": "I attended the Ride for Children last year and was impressed by the club\u2019s organisation.",  "status": "approved",  "days_ago": 45},
    ],
}

"""
SQLite schema for ClubCMS demo data fixtures.

Each language has its own .sqlite3 file containing ALL data needed
to populate a complete standalone site in that language.
"""
import uuid

# ---------------------------------------------------------------------------
# Shared translation keys — same UUID used across all locale fixtures
# so Wagtail can link pages as translations of each other.
# ---------------------------------------------------------------------------

_NS = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def _tk(name: str) -> str:
    """Deterministic UUID from a page identifier."""
    return str(uuid.uuid5(_NS, name))


PRODUCT_TRANSLATION_KEYS = {
    "standard": _tk("product_standard"),
    "supporter": _tk("product_supporter"),
    "premium": _tk("product_premium"),
}

TRANSLATION_KEYS = {
    # Top-level pages
    "home": _tk("home"),
    "about": _tk("about"),
    "board": _tk("board"),
    "news_index": _tk("news_index"),
    "events_page": _tk("events_page"),
    "gallery": _tk("gallery"),
    "contact": _tk("contact"),
    "privacy": _tk("privacy"),
    "transparency": _tk("transparency"),
    "press": _tk("press"),
    "membership_plans": _tk("membership_plans"),
    "federation": _tk("federation"),
    "mutual_aid": _tk("mutual_aid"),
    "search": _tk("search"),
    "contributions": _tk("contributions"),
    "notifications": _tk("notifications"),
    "partner_index": _tk("partner_index"),
    "place_index": _tk("place_index"),
    # Partners
    "partner_officina": _tk("partner_officina"),
    "partner_concessionaria": _tk("partner_concessionaria"),
    "partner_magazine": _tk("partner_magazine"),
    # News articles
    "news_kickoff": _tk("news_kickoff"),
    "news_pisa": _tk("news_pisa"),
    "news_bayern": _tk("news_bayern"),
    "news_workshop": _tk("news_workshop"),
    "news_seasonal": _tk("news_seasonal"),
    "news_assembly": _tk("news_assembly"),
    # Events
    "event_mandello": _tk("event_mandello"),
    "event_pisa": _tk("event_pisa"),
    "event_orobie": _tk("event_orobie"),
    "event_franciacorta": _tk("event_franciacorta"),
    "event_children": _tk("event_children"),
    "event_garda": _tk("event_garda"),
    # Places
    "place_hq": _tk("place_hq"),
    "place_colosseum": _tk("place_colosseum"),
    "place_campo": _tk("place_campo"),
    "place_trattoria": _tk("place_trattoria"),
    "place_stelvio": _tk("place_stelvio"),
    "route_roman": _tk("route_roman"),
}

# ---------------------------------------------------------------------------
# SQL schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS color_scheme (
    name           TEXT NOT NULL,
    primary_color  TEXT NOT NULL,
    secondary_color TEXT NOT NULL,
    accent         TEXT NOT NULL,
    surface        TEXT NOT NULL,
    surface_alt    TEXT NOT NULL,
    text_primary   TEXT NOT NULL,
    text_muted     TEXT NOT NULL,
    is_dark_mode   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    cat_type    TEXT NOT NULL,
    name        TEXT NOT NULL,
    slug        TEXT NOT NULL,
    color       TEXT DEFAULT '',
    description TEXT DEFAULT '',
    icon        TEXT DEFAULT '',
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    name             TEXT NOT NULL,
    slug             TEXT NOT NULL,
    translation_key  TEXT NOT NULL,
    description      TEXT DEFAULT '',
    price            REAL NOT NULL,
    grants_vote      INTEGER DEFAULT 0,
    grants_events    INTEGER DEFAULT 0,
    grants_upload    INTEGER DEFAULT 0,
    grants_discount  INTEGER DEFAULT 0,
    discount_percent INTEGER DEFAULT 0,
    sort_order       INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS testimonials (
    quote       TEXT NOT NULL,
    author_name TEXT NOT NULL,
    author_role TEXT DEFAULT '',
    featured    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS faqs (
    question   TEXT NOT NULL,
    answer     TEXT NOT NULL,
    category   TEXT DEFAULT '',
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS photo_tags (
    name TEXT NOT NULL,
    slug TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS press_releases (
    title       TEXT NOT NULL,
    pub_date    TEXT NOT NULL,
    body        TEXT NOT NULL,
    is_archived INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS brand_assets (
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    description TEXT DEFAULT '',
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS aid_skills (
    name        TEXT NOT NULL,
    slug        TEXT NOT NULL,
    description TEXT DEFAULT '',
    category    TEXT DEFAULT '',
    sort_order  INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS images (
    key         TEXT PRIMARY KEY,
    width       INTEGER NOT NULL,
    height      INTEGER NOT NULL,
    keywords    TEXT NOT NULL,
    description TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS pages (
    slug            TEXT NOT NULL,
    page_type       TEXT NOT NULL,
    parent_slug     TEXT,
    translation_key TEXT NOT NULL,
    title           TEXT NOT NULL,
    fields          TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS place_tags (
    name TEXT NOT NULL,
    slug TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS route_stops (
    route_slug TEXT NOT NULL,
    place_slug TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    note       TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS navbar_items (
    label          TEXT NOT NULL,
    link_url       TEXT DEFAULT '',
    link_page_slug TEXT DEFAULT '',
    open_new_tab   INTEGER DEFAULT 0,
    is_cta         INTEGER DEFAULT 0,
    sort_order     INTEGER DEFAULT 0,
    parent_label   TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS footer_items (
    label          TEXT NOT NULL,
    link_url       TEXT DEFAULT '',
    link_page_slug TEXT DEFAULT '',
    sort_order     INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS footer_social_links (
    platform   TEXT NOT NULL,
    url        TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS site_settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS members (
    username          TEXT PRIMARY KEY,
    first_name        TEXT NOT NULL,
    last_name         TEXT NOT NULL,
    email             TEXT NOT NULL,
    display_name      TEXT DEFAULT '',
    phone             TEXT DEFAULT '',
    mobile            TEXT DEFAULT '',
    birth_date        TEXT,
    birth_place       TEXT DEFAULT '',
    fiscal_code       TEXT DEFAULT '',
    city              TEXT DEFAULT '',
    province          TEXT DEFAULT '',
    postal_code       TEXT DEFAULT '',
    address           TEXT DEFAULT '',
    card_number       TEXT DEFAULT '',
    membership_date   TEXT,
    membership_expiry TEXT,
    bio               TEXT DEFAULT '',
    aid_available     INTEGER DEFAULT 0,
    aid_radius_km     INTEGER DEFAULT 0,
    aid_location_city TEXT DEFAULT '',
    aid_coordinates   TEXT DEFAULT '',
    aid_notes         TEXT DEFAULT '',
    show_in_directory INTEGER DEFAULT 0,
    public_profile    INTEGER DEFAULT 0,
    newsletter        INTEGER DEFAULT 0,
    image_key         TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS aid_requests (
    helper_username    TEXT NOT NULL,
    requester_name     TEXT NOT NULL,
    requester_phone    TEXT DEFAULT '',
    requester_email    TEXT DEFAULT '',
    requester_username TEXT DEFAULT '',
    issue_type         TEXT NOT NULL,
    description        TEXT NOT NULL,
    location           TEXT DEFAULT '',
    urgency            TEXT DEFAULT 'medium',
    status             TEXT DEFAULT 'open'
);

CREATE TABLE IF NOT EXISTS federated_clubs (
    short_code       TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    city             TEXT DEFAULT '',
    base_url         TEXT DEFAULT '',
    logo_url         TEXT DEFAULT '',
    description      TEXT DEFAULT '',
    api_key          TEXT DEFAULT '',
    is_active        INTEGER DEFAULT 1,
    is_approved      INTEGER DEFAULT 0,
    share_our_events INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS external_events (
    club_short_code  TEXT NOT NULL,
    external_id      TEXT NOT NULL,
    event_name       TEXT NOT NULL,
    start_days_offset INTEGER NOT NULL,
    end_days_offset  INTEGER NOT NULL,
    location_name    TEXT DEFAULT '',
    location_address TEXT DEFAULT '',
    location_lat     REAL,
    location_lon     REAL,
    description      TEXT DEFAULT '',
    detail_url       TEXT DEFAULT '',
    is_approved      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS event_interests (
    username          TEXT NOT NULL,
    event_external_id TEXT NOT NULL,
    interest_level    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_comments (
    username          TEXT NOT NULL,
    event_external_id TEXT NOT NULL,
    content           TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS federated_helpers (
    club_short_code TEXT NOT NULL,
    external_id     TEXT NOT NULL,
    display_name    TEXT NOT NULL,
    city            TEXT DEFAULT '',
    latitude        REAL,
    longitude       REAL,
    radius_km       INTEGER DEFAULT 0,
    notes           TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_type  TEXT NOT NULL,
    recipient_username TEXT NOT NULL,
    channel            TEXT DEFAULT 'in_app',
    title              TEXT NOT NULL,
    body               TEXT DEFAULT '',
    url_type           TEXT DEFAULT '',
    url_ref            TEXT DEFAULT '',
    status             TEXT DEFAULT 'pending',
    sent_hours_ago     REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS event_registrations (
    username    TEXT NOT NULL,
    event_slug  TEXT NOT NULL,
    status      TEXT DEFAULT 'confirmed',
    ticket_type TEXT DEFAULT 'standard',
    notes       TEXT DEFAULT '',
    guests      INTEGER DEFAULT 0,
    days_ago    INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS event_favorites (
    username   TEXT NOT NULL,
    event_slug TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contributions (
    username          TEXT NOT NULL,
    contribution_type TEXT NOT NULL,
    title             TEXT NOT NULL,
    body              TEXT NOT NULL,
    status            TEXT DEFAULT 'approved'
);

CREATE TABLE IF NOT EXISTS comments (
    username          TEXT NOT NULL,
    target_type       TEXT NOT NULL,
    target_index      INTEGER NOT NULL,
    content           TEXT NOT NULL,
    moderation_status TEXT DEFAULT 'approved'
);

CREATE TABLE IF NOT EXISTS reactions (
    username      TEXT NOT NULL,
    target_type   TEXT NOT NULL,
    target_index  INTEGER NOT NULL,
    reaction_type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activity_log (
    username      TEXT NOT NULL,
    activity_type TEXT NOT NULL,
    description   TEXT NOT NULL,
    days_ago      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS membership_requests (
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT NOT NULL,
    phone      TEXT DEFAULT '',
    motivation TEXT DEFAULT '',
    status     TEXT DEFAULT 'pending',
    days_ago   INTEGER DEFAULT 0
);
"""

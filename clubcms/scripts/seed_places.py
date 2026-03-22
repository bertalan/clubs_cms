#!/usr/bin/env python
"""
Seed script: create missing locales + demo Places pages (EN + IT).

Usage:
    docker compose exec web python manage.py shell < scripts/seed_places.py
"""

from decimal import Decimal
from wagtail.models import Locale, Page
from apps.places.models import (
    PlaceIndexPage,
    PlacePage,
    PlaceGalleryImage,
    PlaceTag,
    PlaceType,
    RoutePage,
    RouteStop,
)
from apps.website.models import HomePage


# ── 1. Create missing locales ─────────────────────────────────────
REQUIRED_LOCALES = ["en", "it", "de", "fr", "es"]
created_locales = []
for code in REQUIRED_LOCALES:
    loc, created = Locale.objects.get_or_create(language_code=code)
    if created:
        created_locales.append(code)
        print(f"  ✓ Locale '{code}' created")
    else:
        print(f"  · Locale '{code}' already exists")

if created_locales:
    print(f"\n  Created {len(created_locales)} new locale(s): {', '.join(created_locales)}")
else:
    print("\n  All locales already present.")

# ── 2. Get or create PlaceIndexPage under HomePage (EN) ──────────
en_locale = Locale.objects.get(language_code="en")
it_locale = Locale.objects.get(language_code="it")

home = HomePage.objects.filter(locale=en_locale).first()
if not home:
    home = HomePage.objects.first()
if not home:
    print("\n  ✗ No HomePage found. Cannot create places.")
    sys.exit(1)

print(f"\n  Using HomePage: '{home.title}' (id={home.id}, locale={home.locale})")

# Check if PlaceIndexPage already exists
index = PlaceIndexPage.objects.filter(locale=en_locale).first()
if index:
    print(f"  · PlaceIndexPage already exists: '{index.title}' (id={index.id})")
else:
    index = home.add_child(instance=PlaceIndexPage(
        title="Places",
        slug="places",
        locale=en_locale,
        intro="<p>Discover the places connected to our community: club headquarters, monuments, squares, and tourist routes across Italy.</p>",
        live=True,
    ))
    print(f"  ✓ PlaceIndexPage created: '{index.title}' (id={index.id})")

# ── 3. Create tags ────────────────────────────────────────────────
tag_names = ["Historical", "Scenic", "Meeting Point", "Food & Drink", "Panoramic"]
tags = {}
for name in tag_names:
    slug = name.lower().replace(" & ", "-").replace(" ", "-")
    tag, created = PlaceTag.objects.get_or_create(name=name, defaults={"slug": slug})
    tags[name] = tag
    if created:
        print(f"  ✓ Tag '{name}' created")

# ── 4. Create demo PlacePages (EN) ───────────────────────────────
DEMO_PLACES = [
    {
        "title": "Moto Club Aquile Rosse HQ",
        "slug": "moto-club-aquile-rosse-hq",
        "place_type": PlaceType.CLUBHOUSE,
        "latitude": Decimal("41.902782"),
        "longitude": Decimal("12.496366"),
        "address": "Via dei Fori Imperiali 1",
        "city": "Roma",
        "province": "RM",
        "postal_code": "00186",
        "short_description": "The official headquarters of Moto Club Aquile Rosse, where riders meet every weekend.",
        "description": "<p>Located in the heart of Rome, our clubhouse has been the gathering point for motorcycle enthusiasts since 2005. Open to all members with a valid membership card.</p>",
        "opening_hours": "Sa-Su 09:00-18:00",
        "phone": "+39 06 1234567",
        "website_url": "https://example.com/aquile-rosse",
        "tags": ["Meeting Point"],
    },
    {
        "title": "Colosseum",
        "slug": "colosseum",
        "place_type": PlaceType.MONUMENT,
        "latitude": Decimal("41.890210"),
        "longitude": Decimal("12.492231"),
        "address": "Piazza del Colosseo 1",
        "city": "Roma",
        "province": "RM",
        "postal_code": "00184",
        "short_description": "The iconic Roman amphitheatre, a frequent meeting point for club rides departing from Rome.",
        "description": "<p>The Colosseum is the largest ancient amphitheatre ever built. It's our traditional starting point for the annual 'Roma Caput Mundi' ride.</p>",
        "tags": ["Historical", "Scenic"],
    },
    {
        "title": "Piazza del Campo",
        "slug": "piazza-del-campo",
        "place_type": PlaceType.SQUARE,
        "latitude": Decimal("43.318340"),
        "longitude": Decimal("11.331650"),
        "address": "Piazza del Campo",
        "city": "Siena",
        "province": "SI",
        "postal_code": "53100",
        "short_description": "Siena's shell-shaped main square, a mandatory stop on our Tuscany tour.",
        "description": "<p>The stunning Piazza del Campo is famous for the Palio horse race. We stop here for lunch during our annual Tuscan ride.</p>",
        "tags": ["Historical", "Scenic", "Panoramic"],
    },
    {
        "title": "Trattoria da Mario",
        "slug": "trattoria-da-mario",
        "place_type": PlaceType.RESTAURANT,
        "latitude": Decimal("43.771389"),
        "longitude": Decimal("11.253611"),
        "address": "Via Rosina 2",
        "city": "Firenze",
        "province": "FI",
        "postal_code": "50123",
        "short_description": "An authentic Florentine trattoria, partner restaurant for club members.",
        "description": "<p>Family-run trattoria since 1953. Club members get 10% discount showing a valid membership card.</p>",
        "opening_hours": "Mo-Sa 12:00-15:00",
        "phone": "+39 055 218550",
        "tags": ["Food & Drink"],
    },
    {
        "title": "Passo dello Stelvio",
        "slug": "passo-dello-stelvio",
        "place_type": PlaceType.POI,
        "latitude": Decimal("46.528611"),
        "longitude": Decimal("10.453333"),
        "address": "SS38",
        "city": "Bormio",
        "province": "SO",
        "postal_code": "23032",
        "short_description": "The highest paved mountain pass in the Eastern Alps — a legendary motorcycle road.",
        "description": "<p>At 2,757 metres, Passo dello Stelvio offers 48 hairpin bends on the north side alone. Open June to November, weather permitting.</p>",
        "tags": ["Scenic", "Panoramic"],
    },
]

created_places = []
for data in DEMO_PLACES:
    tag_names_for_place = data.pop("tags", [])
    
    existing = PlacePage.objects.filter(slug=data["slug"], locale=en_locale).first()
    if existing:
        print(f"  · PlacePage '{data['title']}' already exists (id={existing.id})")
        created_places.append(existing)
        continue

    place = index.add_child(instance=PlacePage(
        locale=en_locale,
        live=True,
        **data,
    ))
    
    # Add tags
    for tag_name in tag_names_for_place:
        if tag_name in tags:
            place.tags.add(tags[tag_name])

    created_places.append(place)
    print(f"  ✓ PlacePage '{data['title']}' created (id={place.id}, type={place.place_type})")


# ── 5. Create a demo RoutePage (EN) ──────────────────────────────
route_slug = "roman-ride"
existing_route = RoutePage.objects.filter(slug=route_slug, locale=en_locale).first()
if existing_route:
    print(f"  · RoutePage '{existing_route.title}' already exists (id={existing_route.id})")
else:
    from datetime import timedelta

    route = index.add_child(instance=RoutePage(
        title="The Roman Ride",
        slug=route_slug,
        locale=en_locale,
        live=True,
        short_description="A scenic half-day ride from the Colosseum through the hills south of Rome.",
        description="<p>Starting at the Colosseum, this route takes you through Via Appia Antica and into the Castelli Romani countryside. Perfect for a Sunday morning ride.</p>",
        distance_km=Decimal("85.5"),
        estimated_duration=timedelta(hours=2, minutes=30),
        difficulty="medium",
    ))

    # Add stops (must reference existing PlacePage objects)
    hq = PlacePage.objects.filter(slug="moto-club-aquile-rosse-hq", locale=en_locale).first()
    colosseum = PlacePage.objects.filter(slug="colosseum", locale=en_locale).first()
    
    stops_data = []
    if hq:
        stops_data.append({"place": hq, "sort_order": 1, "note": "Meeting point at 8:00 AM"})
    if colosseum:
        stops_data.append({"place": colosseum, "sort_order": 2, "note": "Photo stop at the amphitheatre"})

    for stop_data in stops_data:
        RouteStop.objects.create(route=route, **stop_data)

    print(f"  ✓ RoutePage 'The Roman Ride' created (id={route.id}) with {len(stops_data)} stops")


# ── 6. Copy pages to IT locale ───────────────────────────────────
print("\n  Copying pages to IT locale...")

# Copy index
it_index = PlaceIndexPage.objects.filter(locale=it_locale).first()
if it_index:
    print(f"  · IT PlaceIndexPage already exists: '{it_index.title}'")
else:
    try:
        it_index = index.copy_for_translation(it_locale, copy_parents=True)
        it_index.title = "Luoghi"
        it_index.slug = "luoghi"
        it_index.intro = "<p>Scopri i luoghi legati alla nostra comunità: sedi club, monumenti, piazze e percorsi turistici in tutta Italia.</p>"
        it_index.save_revision().publish()
        print(f"  ✓ IT PlaceIndexPage created: 'Luoghi' (id={it_index.id})")
    except Exception as e:
        print(f"  ✗ Failed to copy PlaceIndexPage to IT: {e}")
        it_index = None

# Copy child pages
IT_TRANSLATIONS = {
    "moto-club-aquile-rosse-hq": {
        "title": "Sede Moto Club Aquile Rosse",
        "slug": "sede-moto-club-aquile-rosse",
        "short_description": "La sede ufficiale del Moto Club Aquile Rosse, dove i motociclisti si ritrovano ogni fine settimana.",
        "description": "<p>Situata nel cuore di Roma, la nostra sede è il punto di ritrovo per gli appassionati di moto dal 2005. Aperta a tutti i soci con tessera valida.</p>",
    },
    "colosseum": {
        "title": "Colosseo",
        "slug": "colosseo",
        "short_description": "L'iconico anfiteatro romano, punto di ritrovo abituale per le uscite del club da Roma.",
        "description": "<p>Il Colosseo è il più grande anfiteatro antico mai costruito. È il nostro punto di partenza tradizionale per la cavalcata annuale 'Roma Caput Mundi'.</p>",
    },
    "piazza-del-campo": {
        "title": "Piazza del Campo",
        "slug": "piazza-del-campo-it",
        "short_description": "La piazza principale di Siena a forma di conchiglia, tappa obbligata del nostro tour toscano.",
        "description": "<p>La splendida Piazza del Campo è famosa per il Palio. Ci fermiamo qui per il pranzo durante la nostra uscita annuale in Toscana.</p>",
    },
    "trattoria-da-mario": {
        "title": "Trattoria da Mario",
        "slug": "trattoria-da-mario-it",
        "short_description": "Un'autentica trattoria fiorentina, ristorante convenzionato per i soci del club.",
        "description": "<p>Trattoria a gestione familiare dal 1953. I soci del club hanno il 10% di sconto presentando la tessera valida.</p>",
    },
    "passo-dello-stelvio": {
        "title": "Passo dello Stelvio",
        "slug": "passo-dello-stelvio-it",
        "short_description": "Il valico stradale più alto delle Alpi Orientali — una strada leggendaria per motociclisti.",
        "description": "<p>A 2.757 metri, il Passo dello Stelvio offre 48 tornanti sul solo versante nord. Aperto da giugno a novembre, tempo permettendo.</p>",
    },
}

for en_slug, it_data in IT_TRANSLATIONS.items():
    en_page = PlacePage.objects.filter(slug=en_slug, locale=en_locale).first()
    if not en_page:
        print(f"  ✗ EN page '{en_slug}' not found, skipping IT copy")
        continue
    
    it_page = PlacePage.objects.filter(translation_key=en_page.translation_key, locale=it_locale).first()
    if it_page:
        print(f"  · IT PlacePage '{it_data['title']}' already exists (id={it_page.id})")
        continue

    try:
        it_page = en_page.copy_for_translation(it_locale)
        it_page.title = it_data["title"]
        it_page.slug = it_data["slug"]
        it_page.short_description = it_data["short_description"]
        it_page.description = it_data["description"]
        it_page.save_revision().publish()
        print(f"  ✓ IT PlacePage '{it_data['title']}' created (id={it_page.id})")
    except Exception as e:
        print(f"  ✗ Failed to copy '{en_slug}' to IT: {e}")

# Copy route
en_route = RoutePage.objects.filter(slug=route_slug, locale=en_locale).first()
if en_route:
    it_route = RoutePage.objects.filter(translation_key=en_route.translation_key, locale=it_locale).first()
    if it_route:
        print(f"  · IT RoutePage already exists: '{it_route.title}'")
    else:
        try:
            it_route = en_route.copy_for_translation(it_locale)
            it_route.title = "La Cavalcata Romana"
            it_route.slug = "cavalcata-romana"
            it_route.short_description = "Un panoramico giro di mezza giornata dal Colosseo attraverso le colline a sud di Roma."
            it_route.description = "<p>Partendo dal Colosseo, questo percorso vi porta attraverso Via Appia Antica e nella campagna dei Castelli Romani. Perfetto per un'uscita domenicale.</p>"
            it_route.save_revision().publish()
            print(f"  ✓ IT RoutePage 'La Cavalcata Romana' created (id={it_route.id})")
        except Exception as e:
            print(f"  ✗ Failed to copy RoutePage to IT: {e}")


# ── Summary ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  SUMMARY")
print("=" * 60)
print(f"  Locales:          {Locale.objects.count()} ({', '.join(l.language_code for l in Locale.objects.all())})")
print(f"  PlaceIndexPage:   {PlaceIndexPage.objects.count()} (EN: {PlaceIndexPage.objects.filter(locale=en_locale).count()}, IT: {PlaceIndexPage.objects.filter(locale=it_locale).count()})")
print(f"  PlacePage:        {PlacePage.objects.count()} (EN: {PlacePage.objects.filter(locale=en_locale).count()}, IT: {PlacePage.objects.filter(locale=it_locale).count()})")
print(f"  RoutePage:        {RoutePage.objects.count()} (EN: {RoutePage.objects.filter(locale=en_locale).count()}, IT: {RoutePage.objects.filter(locale=it_locale).count()})")
print(f"  PlaceTag:         {PlaceTag.objects.count()}")
print(f"\n  Browse EN: http://localhost:8000/en/places/")
print(f"  Browse IT: http://localhost:8000/it/luoghi/")
print("=" * 60)

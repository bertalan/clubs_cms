"""
One-time fix: assign cover_image to pages that were missed due to
_assign_page_images using 'highlight_image' instead of 'cover_image'.

Run on server: python manage.py shell < scripts/fix_cover_images.py
"""
from wagtail.images.models import Image
from wagtail.models import Page

# ── helpers ──────────────────────────────────────────────────────────
def get_demo_image(key):
    """Fetch a demo image by its key prefix."""
    return Image.objects.filter(title=f"Demo: {key}").first()


def assign_cover(slug, img):
    """Set cover_image on every locale variant of `slug`."""
    if not img:
        return
    pages = Page.objects.filter(slug=slug).specific()
    for p in pages:
        if hasattr(p, "cover_image") and not p.cover_image_id:
            p.cover_image = img
            p.save_revision().publish()
            print(f"  ✓ {p.slug} (pk={p.pk}) ← {img.title}")


# ── image key → page slug mapping ───────────────────────────────────
EVENT_MAP = {
    "event_mandello": ["season-opener-mandello-2026", "avviamento-motori-mandello-2026"],
    "event_pisa": ["moto-lands-pisa-2026"],
    "event_orobie": ["orobie-tour-2026", "tour-orobie-2026"],
    "event_franciacorta": ["franciacorta-track-day-2026", "track-day-franciacorta-2026"],
    "event_children": ["ride-for-children-2026"],
    "event_garda": ["moto-rally-garda-2026"],
}

NEWS_MAP = {
    "news_mandello": ["2026-season-kickoff", "avviamento-motori-2026"],
    "news_pisa": ["moto-lands-pisa"],
    "news_bayern": ["spring-franken-bayern-treffen"],
    "news_officina": ["workshop-bergamo-partnership", "convenzione-officina-moto-bergamo"],
    "news_manutenzione": ["seasonal-motorcycle-prep", "preparazione-moto-stagione"],
    "news_assemblea": ["2026-annual-assembly", "assemblea-soci-2026"],
}

ABOUT_SLUGS = ["about-us", "chi-siamo"]

PARTNER_SLUGS = [
    "bergamo-moto-magazine",
    "lecco-motorcycle-dealership",
    "officina-moto-bergamo",
]

ROUTE_SLUGS = ["roman-ride"]

# ── apply ────────────────────────────────────────────────────────────
print("=== Fixing cover_image assignments ===\n")

print("Events:")
for img_key, slugs in EVENT_MAP.items():
    img = get_demo_image(img_key)
    for slug in slugs:
        assign_cover(slug, img)

print("\nNews:")
for img_key, slugs in NEWS_MAP.items():
    img = get_demo_image(img_key)
    for slug in slugs:
        assign_cover(slug, img)

print("\nAbout:")
about_img = get_demo_image("hero_about")
for slug in ABOUT_SLUGS:
    assign_cover(slug, about_img)

print("\nPartners:")
partner_img = get_demo_image("partner_bgmoto")
for slug in PARTNER_SLUGS:
    assign_cover(slug, partner_img)

print("\nRoutes:")
route_img = get_demo_image("event_garda")  # reuse event image
for slug in ROUTE_SLUGS:
    assign_cover(slug, route_img)

print("\n=== Done ===")

# Implementation Checklist

## Overview

Complete checklist for building the CMS using native Wagtail features. No custom code required - all configuration via admin panels.

---

## PHASE 1: Project Setup (1-2 days)

### Environment

| Task | Status |
|------|--------|
| Python 3.11+ virtual environment | ☐ |
| Install Wagtail + dependencies | ☐ |
| PostgreSQL database created | ☐ |
| Docker Compose for development | ☐ |

### Django Configuration

| Task | Status |
|------|--------|
| Settings split (base, dev, prod) | ☐ |
| Apps created: core, website, custom_user | ☐ |
| First migration run | ☐ |
| Superuser created | ☐ |

### References
- [50-DOCKER.md](50-DOCKER.md)

---

## PHASE 2: Site Settings (1 day)

### Admin Configuration

| Task | Status |
|------|--------|
| Site Settings model registered | ☐ |
| Site name configured | ☐ |
| Logo uploaded | ☐ |
| Contact info entered | ☐ |
| Social links configured | ☐ |

### Theme Configuration

| Task | Status |
|------|--------|
| ColorScheme snippet created | ☐ |
| Default theme selected | ☐ |
| Theme CSS files in static | ☐ |

### References
- [36-WAGTAIL-ADMIN.md](36-WAGTAIL-ADMIN.md)
- [37-COLOR-SCHEME.md](37-COLOR-SCHEME.md)

---

## PHASE 3: Snippets (2 days)

### Navigation

| Task | Status |
|------|--------|
| Navbar snippet created | ☐ |
| Menu items added | ☐ |
| Footer snippet created | ☐ |
| Footer content configured | ☐ |

### Content Snippets

| Task | Status |
|------|--------|
| FAQ items created | ☐ |
| Partner logos added | ☐ |
| Testimonials added | ☐ |

### Taxonomy

| Task | Status |
|------|--------|
| News categories created | ☐ |
| Event categories created | ☐ |
| Photo tags created | ☐ |

### References
- [42-SNIPPETS.md](42-SNIPPETS.md)

---

## PHASE 4: StreamField Blocks (2-3 days)

### Hero Blocks

| Block | Status |
|-------|--------|
| HeroSliderBlock | ☐ |
| HeroBannerBlock | ☐ |
| HeroCountdownBlock | ☐ |

### Content Blocks

| Block | Status |
|-------|--------|
| CardsGridBlock | ☐ |
| CTABlock | ☐ |
| StatsBlock | ☐ |
| QuoteBlock | ☐ |
| TimelineBlock | ☐ |

### Media Blocks

| Block | Status |
|-------|--------|
| GalleryBlock | ☐ |
| VideoEmbedBlock | ☐ |
| ImageBlock | ☐ |
| DocumentListBlock | ☐ |
| MapBlock | ☐ |

### Layout Blocks

| Block | Status |
|-------|--------|
| GridBlock | ☐ |
| TwoColumnBlock | ☐ |
| AccordionBlock | ☐ |
| TabsBlock | ☐ |

### Route Block

| Block | Status |
|-------|--------|
| RouteBlock (OSM + OSRM) | ☐ |

### References
- [20-STREAMFIELD-BLOCKS.md](20-STREAMFIELD-BLOCKS.md)
- [21-HERO-BLOCKS.md](21-HERO-BLOCKS.md)
- [22-CONTENT-BLOCKS.md](22-CONTENT-BLOCKS.md)
- [23-MEDIA-BLOCKS.md](23-MEDIA-BLOCKS.md)
- [24-LAYOUT-BLOCKS.md](24-LAYOUT-BLOCKS.md)
- [87-ROUTE-MAPS.md](87-ROUTE-MAPS.md)

---

## PHASE 5: Page Models (2-3 days)

### Core Pages

| Page | Status |
|------|--------|
| HomePage (max 1) | ☐ |
| ContentPage (generic) | ☐ |

### Static Pages

| Page | Status |
|------|--------|
| AboutPage | ☐ |
| BoardPage | ☐ |
| ContactPage (with form + captcha) | ☐ |
| PrivacyPage | ☐ |
| TransparencyPage | ☐ |
| PressPage (Ufficio Stampa) | ☐ |

### News

| Page | Status |
|------|--------|
| NewsIndexPage (max 1) | ☐ |
| NewsPage | ☐ |

### Events

| Page | Status |
|------|--------|
| EventsPage (max 1) | ☐ |
| EventDetailPage | ☐ |

### Gallery

| Page | Status |
|------|--------|
| GalleryPage (max 1) | ☐ |
| Collections configured | ☐ |

### References
- [10-PAGE-MODELS.md](10-PAGE-MODELS.md)
- [11-HOME-PAGE.md](11-HOME-PAGE.md)
- [12-CONTENT-PAGES.md](12-CONTENT-PAGES.md)
- [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md)
- [14-GALLERY.md](14-GALLERY.md)

---

## PHASE 6: Templates (3-4 days)

### Base Templates

| Template | Status |
|----------|--------|
| base.html | ☐ |
| navbar include | ☐ |
| footer include | ☐ |

### Theme Templates

| Theme | Status |
|-------|--------|
| Velocity | ☐ |
| Heritage | ☐ |
| Terra | ☐ |
| Zen | ☐ |
| Clubs | ☐ |
| Tricolore | ☐ |

### Block Templates

| Task | Status |
|------|--------|
| All hero block templates | ☐ |
| All content block templates | ☐ |
| All media block templates | ☐ |
| All layout block templates | ☐ |

### References
- [30-TEMPLATE-SYSTEM.md](30-TEMPLATE-SYSTEM.md)
- [31-38: Theme files](31-THEME-VELOCITY.md)

---

## PHASE 7: Multilingual (2 days)

### Setup

| Task | Status |
|------|--------|
| wagtail-localize installed | ☐ |
| Locales created (IT, EN, DE, FR, ES) | ☐ |
| Default locale set (EN) | ☐ |

### Content Translation

| Task | Status |
|------|--------|
| Navbar translated | ☐ |
| Footer translated | ☐ |
| Core pages translated | ☐ |
| Template strings translated | ☐ |

### Language Switcher

| Task | Status |
|------|--------|
| Switcher in navbar | ☐ |
| hreflang tags in head | ☐ |

### References
- [41-MULTILANG.md](41-MULTILANG.md)

---

## PHASE 8: SEO (1-2 days)

### Schema.org

| Task | Status |
|------|--------|
| Organization schema (HomePage) | ☐ |
| Article schema (NewsPage) | ☐ |
| Event schema (EventDetailPage) | ☐ |
| ItemList for index pages | ☐ |

### Meta Tags

| Task | Status |
|------|--------|
| Open Graph tags | ☐ |
| Twitter cards | ☐ |
| Canonical URLs | ☐ |

### Discovery

| Task | Status |
|------|--------|
| sitemap.xml configured | ☐ |
| robots.txt configured | ☐ |
| Atom/RSS feeds | ☐ |

### References
- [40-SEO-JSONLD.md](40-SEO-JSONLD.md)

---

## PHASE 9: Member Features (3-4 days)

### User System

| Task | Status |
|------|--------|
| Custom User model | ☐ |
| Product snippet (package system) | ☐ |
| Member profile with products | ☐ |
| QR code + Barcode generation | ☐ |
| Public profile page | ☐ |
| Member admin viewset | ☐ |

### Press Office

| Task | Status |
|------|--------|
| PressPage created | ☐ |
| BrandAsset snippet | ☐ |
| PressRelease snippet | ☐ |
| Download tracking (optional) | ☐ |

### Event Registration

| Task | Status |
|------|--------|
| EventAttendance model | ☐ |
| Registration form | ☐ |
| Captcha protection | ☐ |
| Early booking tiers | ☐ |
| Passenger/companion fields | ☐ |
| Waitlist management | ☐ |

### Member Uploads

| Task | Status |
|------|--------|
| Photo upload form | ☐ |
| Batch upload with shared metadata | ☐ |
| PhotoTag snippet | ☐ |
| Moderation queue | ☐ |
| Collection assignment | ☐ |

### Event Favorites

| Task | Status |
|------|--------|
| Favorite model | ☐ |
| My Events page | ☐ |
| Map view (Leaflet) | ☐ |
| ICS export | ☐ |
| Public profile link | ☐ |
| Auto-archive past events | ☐ |

### Partners & Sponsors

| Task | Status |
|------|--------|
| PartnerCategory snippet | ☐ |
| Partner model with owner | ☐ |
| Partner logo + description | ☐ |
| Member discount field | ☐ |
| Partner verification page | ☐ |
| Two-factor verification (card + secondary) | ☐ |
| Homepage partner logo grid | ☐ |
| Dedicated partners page | ☐ |

### Mutual Aid Network

| Task | Status |
|------|--------|
| AidSkill snippet | ☐ |
| Member aid preferences | ☐ |
| Per-field privacy controls | ☐ |
| Aid map (Leaflet + clustering) | ☐ |
| Helper cards with contact | ☐ |
| Contact form (privacy fallback) | ☐ |
| Notification system | ☐ |
| Admin dashboard | ☐ |

### Notifications & Newsletter

| Task | Status |
|------|--------|
| User notification preferences | ☐ |
| User delivery schedule (day/time) | ☐ |
| Timezone support | ☐ |
| NotificationTemplate snippet | ☐ |
| Notification queue model | ☐ |
| Email delivery (SMTP) | ☐ |
| PWA push delivery (Web Push) | ☐ |
| Daily/weekly digest processing | ☐ |
| Weekend favorites reminder | ☐ |
| One-click unsubscribe flow | ☐ |
| Unsubscribe confirmation page | ☐ |
| Wagtail page_published hook | ☐ |
| Admin notifications dashboard | ☐ |
| API endpoints | ☐ |
| Background task runner (Django-Q) | ☐ |

### References
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md)
- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md)
- [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md)
- [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md)
- [89-PARTNERS.md](89-PARTNERS.md)
- [90-MUTUAL-AID.md](90-MUTUAL-AID.md)
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md)

---

## PHASE 10: Testing (2 days)

### Unit Tests

| Task | Status |
|------|--------|
| Page model tests | ☐ |
| Block tests | ☐ |
| Snippet tests | ☐ |

### Integration Tests

| Task | Status |
|------|--------|
| Navigation tests | ☐ |
| Form submission tests | ☐ |
| Multilingual tests | ☐ |

### Manual Testing

| Task | Status |
|------|--------|
| All pages render correctly | ☐ |
| All blocks display properly | ☐ |
| Mobile responsive | ☐ |
| All languages work | ☐ |

---

## PHASE 11: Deployment (1-2 days)

### Server Setup

| Task | Status |
|------|--------|
| Server provisioned | ☐ |
| PostgreSQL installed | ☐ |
| Nginx configured | ☐ |
| Gunicorn service created | ☐ |
| SSL certificate (Let's Encrypt) | ☐ |

### Deploy Script

| Task | Status |
|------|--------|
| Variables configured | ☐ |
| Backup system working | ☐ |
| Rotation (keep 10) working | ☐ |
| First deploy successful | ☐ |

### Monitoring

| Task | Status |
|------|--------|
| Health check endpoint | ☐ |
| Error logging configured | ☐ |
| Backup cron jobs | ☐ |

### References
- [51-PRODUCTION.md](51-PRODUCTION.md)

---

## Timeline Summary

| Phase | Days | Priority |
|-------|------|----------|
| 1. Setup | 1-2 | High |
| 2. Site Settings | 1 | High |
| 3. Snippets | 2 | High |
| 4. StreamField Blocks | 2-3 | High |
| 5. Page Models | 2-3 | High |
| 6. Templates | 3-4 | High |
| 7. Multilingual | 2 | Medium |
| 8. SEO | 1-2 | Medium |
| 9. Member Features | 3-4 | Medium |
| 10. Testing | 2 | Medium |
| 11. Deployment | 1-2 | High |

**Total: 20-27 days**

---

## MVP vs Full

### MVP (First Release)

| Component | Included |
|-----------|----------|
| Setup + Site Settings | ✅ |
| Snippets (Navbar, Footer) | ✅ |
| Core Blocks (Hero, Cards, CTA) | ✅ |
| Core Pages (Home, About, Contact) | ✅ |
| 1 Theme (Velocity or Tricolore) | ✅ |
| Italian only | ✅ |
| Basic SEO | ✅ |
| Production deploy | ✅ |

### Full Release

| Component | Included |
|-----------|----------|
| All StreamField Blocks | ✅ |
| All Page Types | ✅ |
| All 6 Themes | ✅ |
| 5 Languages | ✅ |
| Member Features | ✅ |
| Event Favorites + Map | ✅ |
| Route Maps | ✅ |
| Partners & Sponsors | ✅ |
| Mutual Aid Network | ✅ |
| Notifications & Newsletter | ✅ |
| Full SEO + Feeds | ✅ |

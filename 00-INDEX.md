# Rebuild Documentation - Pure Wagtail 7.x

## Validated Wagtail 7.x Patterns

| Type | Correct Usage | Example |
|------|---------------|---------|
| **Snippet** | Reusable editorial content | Navbar, Footer, ColorScheme, MembershipType |
| **Django Model + ModelViewSet** | Transactional/application data | User, EventAttendance, Activity, Comment |
| **Page** | CMS page content | HomePage, NewsPage, EventDetailPage |

## Documents by Category

### Setup (01-03)
- [01-PROJECT-STRUCTURE.md](01-PROJECT-STRUCTURE.md) - Folder structure
- [02-DEPENDENCIES.md](02-DEPENDENCIES.md) - Python dependencies
- [03-SETTINGS.md](03-SETTINGS.md) - Django/Wagtail configuration

### Page Models (10-14)
- [10-PAGE-MODELS.md](10-PAGE-MODELS.md) - BasePage, JsonLdMixin
- [11-HOME-PAGE.md](11-HOME-PAGE.md) - HomePage
- [12-CONTENT-PAGES.md](12-CONTENT-PAGES.md) - Contact, Privacy, Board
- [13-NEWS-EVENTS.md](13-NEWS-EVENTS.md) - News, Events
- [14-GALLERY.md](14-GALLERY.md) - Gallery with Wagtail Collections

### Blocks (20-24)
- [20-STREAMFIELD-BLOCKS.md](20-STREAMFIELD-BLOCKS.md) - Blocks architecture
- [21-HERO-BLOCKS.md](21-HERO-BLOCKS.md) - Hero slider/banner
- [22-CONTENT-BLOCKS.md](22-CONTENT-BLOCKS.md) - Cards, CTA, Stats
- [23-MEDIA-BLOCKS.md](23-MEDIA-BLOCKS.md) - Gallery, Video, Map
- [24-LAYOUT-BLOCKS.md](24-LAYOUT-BLOCKS.md) - Grid, Accordion, Tabs

### Template System (30-39)
- [30-TEMPLATE-SYSTEM.md](30-TEMPLATE-SYSTEM.md) - Django templates
- [31-THEME-VELOCITY.md](31-THEME-VELOCITY.md) - Modern/Tailwind
- [32-THEME-HERITAGE.md](32-THEME-HERITAGE.md) - Classic/Bootstrap
- [33-THEME-ECO.md](33-THEME-ECO.md) - Sustainability/Eco-friendly
- [34-THEME-ZEN.md](34-THEME-ZEN.md) - Minimalism with Purpose
- [35-THEMES-PROPOSAL.md](35-THEMES-PROPOSAL.md) - Theme switching system
- [36-WAGTAIL-ADMIN.md](36-WAGTAIL-ADMIN.md) - Admin customization + Captcha
- [37-COLOR-SCHEME.md](37-COLOR-SCHEME.md) - Dynamic CSS variables
- [38-THEME-CLUBS.md](38-THEME-CLUBS.md) - Premium Italian style
- [39-THEME-TRICOLORE.md](39-THEME-TRICOLORE.md) - Italian flag theme

### SEO & i18n (40-42)
- [40-SEO-JSONLD.md](40-SEO-JSONLD.md) - Schema.org
- [41-MULTILANG.md](41-MULTILANG.md) - wagtail-localize
- [42-SNIPPETS.md](42-SNIPPETS.md) - Navbar, Footer, SiteSettings

### Deploy (50-51, 60, 70)
- [50-DOCKER.md](50-DOCKER.md) - Docker setup
- [51-PRODUCTION.md](51-PRODUCTION.md) - Nginx, SSL
- [60-CHECKLIST.md](60-CHECKLIST.md) - Implementation phases
- [70-MIGRATION-SCRIPT.md](70-MIGRATION-SCRIPT.md) - Export/Import

### Member Features (80-91)
- [80-MEMBERSHIP-SYSTEM.md](80-MEMBERSHIP-SYSTEM.md) - User + Products + QR/Barcode + Public Profile
- [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) - Member photo upload + Batch upload
- [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) - EventAttendance + Early Booking + Passenger
- [83-TRANSACTIONAL-MODELS.md](83-TRANSACTIONAL-MODELS.md) - Activity, Reaction, Comment
- [84-PWA-BASE.md](84-PWA-BASE.md) + [84-PWA-PUSH.md](84-PWA-PUSH.md) - PWA
- [85-CONTRIBUTION-BASE.md](85-CONTRIBUTION-BASE.md) + [85-MODERATION.md](85-MODERATION.md)
- [86-FAVORITE-EVENTS.md](86-FAVORITE-EVENTS.md) - Event Favorites + Map + ICS
- [87-ROUTE-MAPS.md](87-ROUTE-MAPS.md) - RouteBlock for StreamField
- [88-PRESS-OFFICE.md](88-PRESS-OFFICE.md) - Press Office + Brand Kit
- [89-PARTNERS.md](89-PARTNERS.md) - Partners, Sponsors, Affiliates + Owner system
- [90-MUTUAL-AID.md](90-MUTUAL-AID.md) - Mutual Aid Network + Map + Privacy controls
- [91-NOTIFICATIONS.md](91-NOTIFICATIONS.md) - Notification & Newsletter System + API + PWA Push

### Examples
- [EXAMPLE-THEME-VELOCITY.html](examples/EXAMPLE-THEME-VELOCITY.html) - Modern demo
- [EXAMPLE-THEME-HERITAGE.html](examples/EXAMPLE-THEME-HERITAGE.html) - Classic demo
- [EXAMPLE-THEME-TERRA.html](examples/EXAMPLE-THEME-TERRA.html) - Eco-friendly demo
- [EXAMPLE-THEME-ZEN.html](examples/EXAMPLE-THEME-ZEN.html) - Minimal demo
- EXAMPLE-VELOCITY-BASE.md, EXAMPLE-VELOCITY-PARTS.md, EXAMPLE-ABOUT-PAGE.md

## Six Themes Summary

| Theme | Style | Framework | Bundle |
|-------|-------|-----------|--------|
| **Velocity** | Modern, dynamic | Tailwind CSS | <50KB |
| **Heritage** | Classic, elegant | Bootstrap 5 | <80KB |
| **Terra** | Eco-friendly | Pure CSS | <15KB |
| **Zen** | Minimal, focused | Pure CSS | <10KB |
| **Clubs** | Premium Italian | Tailwind CSS | <60KB |
| **Tricolore** | Italian pride | Pure CSS | <30KB |

All themes: WCAG 2.2 AA compliant ✓

## Total: ~40 documents, ~3000 lines

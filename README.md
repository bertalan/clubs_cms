# Club Website - Documentation Repository

> **Documentation for a complete Wagtail 7.x CMS for clubs and associations**

This repository contains comprehensive documentation for building a feature-rich motorcycle club website using **Wagtail 7.x** and **Django 5.x**.

## 📂 Repository Structure

```
docs/rebuild/
├── README.md              ← You are here
└── idea/                  ← Complete documentation
    ├── 00-INDEX.md        ← Start here: Master index
    ├── README.md          ← Full multilingual guide
    ├── 01-03/             ← Setup: Structure, Dependencies, Settings
    ├── 10-14/             ← Page Models: Home, Content, News, Events, Gallery
    ├── 20-24/             ← StreamField Blocks: Hero, Content, Media, Layout
    ├── 30-39/             ← Themes: 6 complete themes with live previews
    ├── 40-42/             ← SEO, Multilingual, Snippets
    ├── 50-70/             ← Deployment: Docker, Production, Migration
    ├── 80-92/             ← Member Features: Membership, Events, Federation
    └── theme_examples/    ← Live HTML previews of all 6 themes
```

## 🚀 Quick Start

### For Developers

1. **Read the index:** [`idea/00-INDEX.md`](idea/00-INDEX.md) - Complete documentation catalog
2. **Explore the architecture:** [`idea/01-PROJECT-STRUCTURE.md`](idea/01-PROJECT-STRUCTURE.md)
3. **Check dependencies:** [`idea/02-DEPENDENCIES.md`](idea/02-DEPENDENCIES.md)
4. **Review the checklist:** [`idea/60-CHECKLIST.md`](idea/60-CHECKLIST.md)

### For Club Members

Read the **User Guide** section in [`idea/README.md`](idea/README.md) for:
- How to use the website
- Member features
- Event registration
- Photo gallery
- Digital membership card

## 🎨 6 Premium Themes

| Theme | Style | Preview |
|-------|-------|---------|
| **Velocity** | Modern/Tailwind | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/velocity/) |
| **Heritage** | Classic/Bootstrap | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/heritage/) |
| **Terra** | Eco-friendly | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/terra/) |
| **Zen** | Minimalist | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/zen/) |
| **Clubs** | Premium Italian | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/clubs/) |
| **Tricolore** | Italian Pride 🇮🇹 | [View](https://bertalan.github.io/motoclubsite_prj/theme_examples/tricolore/) |

All themes are fully responsive and include complete implementations for all pages (Home, Events, Gallery, About, Contact).

## 📚 Documentation Categories

### Core System (01-42)
- **Setup & Configuration** (01-03): Project structure, dependencies, Django/Wagtail settings
- **Page Models** (10-14): Home, content pages, news, events, gallery with Wagtail collections
- **StreamField Blocks** (20-24): Reusable content blocks for dynamic page building
- **Template System** (30-39): Theme architecture with 6 complete themes
- **SEO & Internationalization** (40-42): Schema.org JSON-LD, wagtail-localize, snippets

### Deployment (50-70)
- **Docker Setup** (50): Multi-stage Dockerfile, docker-compose, production config
- **Production Deploy** (51): Nginx, SSL, static files, media handling
- **Implementation Checklist** (60): Phase-by-phase development roadmap
- **Data Migration** (70): Export/import scripts for legacy content

### Member Features (80-92)
- **Membership System** (80): User profiles, QR codes, products, display names
- **Gallery Upload** (81): Member photo uploads, batch processing, moderation
- **Event Registration** (82): Open events, tiered pricing, passenger support
- **Transactional Models** (83): Activities, reactions, comments
- **PWA** (84): Progressive Web App with offline support, push notifications
- **Contribution System** (85): User-generated content with moderation
- **Favorites & Maps** (86): Event favorites, interactive maps, ICS export
- **Route Planning** (87): OSM + OSRM integration for route visualization
- **Press Office** (88): Media assets, brand kit, press releases
- **Partners** (89): Sponsors, affiliates, member verification for discounts
- **Mutual Aid** (90): Member assistance network with privacy controls, federated access
- **Notifications** (91): Email, PWA push, SMS with weekend reminders
- **Event Federation** (92): Share events with partner clubs via API

## 🔑 Key Features

### For Club Administrators
- **Wagtail CMS**: Easy content management without coding
- **6 Themes**: Switch themes instantly via admin panel
- **Multilingual**: Support for 5 languages (IT, EN, DE, FR, ES)
- **Member Management**: Products, QR codes, tiered pricing
- **Event Management**: Registration, attendance tracking, federation with partners
- **Moderation**: Review user-generated content before publishing
- **Analytics**: Track member activity, event popularity

### For Club Members
- **Digital Membership Card**: QR/barcode for quick check-in
- **Event Registration**: Book events online with passenger support
- **Photo Uploads**: Share ride photos with moderation
- **Mutual Aid Network**: Find help from nearby members
- **PWA Support**: Install as mobile app, offline access, push notifications
- **Newsletter**: Weekly digest, event reminders
- **Partner Events**: See events from federated clubs

### Technical Excellence
- **Wagtail 7.x**: Latest CMS with StreamField blocks
- **Django 5.x**: Modern Python web framework
- **Docker Ready**: Production-ready containers
- **SEO Optimized**: Schema.org JSON-LD, meta tags
- **Secure**: Captcha, rate limiting, HTTPS/SSL
- **Scalable**: PostgreSQL, Redis, static/media CDN support

## 📖 Multilingual Support

The main user guide is available in 5 languages:

- 🇬🇧 [English](idea/README.md)
- 🇮🇹 [Italiano](idea/README-it.md)
- 🇩🇪 [Deutsch](idea/README-de.md)
- 🇫🇷 [Français](idea/README-fr.md)
- 🇪🇸 [Español](idea/README-es.md)

## 🤝 Federation Network

The system supports **Event Federation** with partner motorcycle clubs:

- **Share Events**: Publish your events to partner clubs automatically
- **Discover Events**: Members see events from the entire network
- **Anonymous Interest**: Track interest without exposing member data
- **Secure API**: HMAC-SHA256 signed requests with rate limiting
- **Mutual Aid**: Extended network for roadside assistance

See [`idea/92-EVENT-FEDERATION.md`](idea/92-EVENT-FEDERATION.md) for complete specifications.

## 📋 Implementation Phases

The project is organized in **10 phases** from basic CMS to advanced member features:

1. **Phase 1**: Core Wagtail setup, first theme
2. **Phase 2**: Multilingual content
3. **Phase 3**: News & Events
4. **Phase 4**: Gallery with Wagtail Collections
5. **Phase 5**: Member system & QR codes
6. **Phase 6**: Event registration & attendance
7. **Phase 7**: PWA & Push notifications
8. **Phase 8**: Advanced features (Routes, Press, Partners)
9. **Phase 9**: Mutual Aid network
10. **Phase 10**: Event Federation

See [`idea/60-CHECKLIST.md`](idea/60-CHECKLIST.md) for the complete implementation checklist.

## 📝 License

This documentation is available under the terms specified in [`idea/LICENSE`](idea/LICENSE).

## 🏍️ Built With Love for Motorcycle Communities

This project is designed specifically for motorcycle clubs, with features that address the unique needs of rider communities: event coordination, group rides, member networking, roadside assistance, and inter-club collaboration.

---

**Need help?** Start with [`idea/00-INDEX.md`](idea/00-INDEX.md) for the complete documentation index.

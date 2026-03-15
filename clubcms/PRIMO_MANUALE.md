# ClubCMS - User Manual

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Docker Setup](#2-docker-setup)
3. [Admin Panel Overview](#3-admin-panel-overview)
4. [Site Settings](#4-site-settings)
5. [Managing Pages](#5-managing-pages)
6. [News & Articles](#6-news--articles)
7. [Events](#7-events)
8. [Gallery](#8-gallery)
9. [Partners](#9-partners)
10. [Snippets (Navbar, Footer, Categories)](#10-snippets)
11. [Members & Membership](#11-members--membership)
12. [Notifications](#12-notifications)
13. [Federation](#13-federation)
14. [Demo Data](#14-demo-data)
15. [Troubleshooting](#15-troubleshooting)

---

## 1. Getting Started

ClubCMS is a content management system built on Wagtail 7.x and Django 5.x, designed specifically for motorcycle clubs. It provides:

- **Page management**: Homepage, About, News, Events, Gallery, Contact, Privacy, Transparency, Press, Partners
- **Member management**: Registration, membership cards with QR/barcode, profiles
- **Event system**: Registration, pricing tiers, early bird discounts, waitlists, ICS export
- **Notification system**: Email, push notifications, digest
- **Federation**: Inter-club event sharing with HMAC-signed API
- **Mutual aid**: Member-to-member roadside assistance network
- **6 themes**: Velocity, Heritage, Terra, Zen, Clubs, Tricolore
- **5 languages**: Italian, English, German, French, Spanish
- **SEO**: JSON-LD structured data, sitemaps, RSS feeds

### Prerequisites

- Docker and Docker Compose
- A modern web browser

### Quick Start

```bash
cd clubcms/
docker compose up -d
docker compose exec web python manage.py populate_demo_it
```

Then visit:
- **Site**: http://localhost:8888/
- **Admin**: http://localhost:8888/admin/
- **Login**: `admin` / `admin1234`

---

## 2. Docker Setup

### Starting the Application

```bash
# Build and start containers
docker compose up -d

# View logs
docker compose logs -f web

# Stop containers
docker compose down

# Rebuild after code changes
docker compose up -d --build
```

### Environment Variables

The `docker-compose.yml` defines these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `clubcms.settings.dev` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://postgres:postgres@db:5432/clubcms` |
| `SECRET_KEY` | Django secret key | Dev-only key (change in production!) |

### Database Operations

```bash
# Run migrations
docker compose exec web python manage.py migrate

# Create a superuser
docker compose exec web python manage.py createsuperuser

# Access the database shell
docker compose exec db psql -U postgres clubcms

# Backup the database
docker compose exec db pg_dump -U postgres clubcms > backup.sql
```

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run with SQLite (automatic when DATABASE_URL is not set)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 3. Admin Panel Overview

Access the Wagtail admin at `/admin/`. The sidebar provides:

| Section | Description |
|---------|-------------|
| **Pages** | Content tree: all site pages |
| **Images** | Upload and manage images |
| **Documents** | Upload and manage documents |
| **Snippets** | Reusable content blocks (navbar, footer, categories, etc.) |
| **Settings** | Site-wide configuration |

### Page Tree Structure

```
Home (Moto Club Aquile Rosse)
├── Chi Siamo (About)
│   └── Consiglio Direttivo (Board)
├── News (Index)
│   ├── Article 1
│   ├── Article 2
│   └── ...
├── Eventi (Events Index)
│   ├── Event 1
│   ├── Event 2
│   └── ...
├── Galleria (Gallery)
├── Contatti (Contact)
├── Privacy Policy
├── Trasparenza (Transparency)
├── Area Stampa (Press)
└── Partner (Index)
    ├── Partner 1
    └── ...
```

---

## 4. Site Settings

Navigate to **Settings → Site Settings** in the admin. Configuration is organized in tabs:

### General Tab
- **Site name**: Displayed in header and meta tags
- **Tagline**: Short description shown in the header
- **Description**: Default SEO meta description

### Theme Tab
- **Theme**: Choose from 6 visual themes
  - `Velocity` - Modern, dynamic design
  - `Heritage` - Classic, vintage feel
  - `Terra` - Natural, earth tones
  - `Zen` - Minimal, clean layout
  - `Clubs` - Bold, club-oriented
  - `Tricolore` - Italian tricolor accent
- **Colour scheme**: Select a predefined color palette

### Branding Tab
- **Logo**: Main site logo
- **Logo (dark)**: Alternative logo for dark backgrounds
- **Favicon**: Browser tab icon

### Contact Tab
- Phone, email, address, opening hours

### Social Tab
- URLs for Facebook, Instagram, Twitter/X, YouTube, LinkedIn, TikTok

### Navigation Tab
- **Navbar**: Select which navigation menu to use
- **Footer**: Select which footer to use

### PWA Tab
- Progressive Web App configuration (name, icons, colors)

### Forms Tab
- **CAPTCHA provider**: `Honeypot` (default, no external service), `Cloudflare Turnstile`, or `hCaptcha`
- Site key and secret key for external providers

### Map Tab
- **Routing service**: OpenStreetMap (default), Google Maps, or Mapbox
- API key (for Google/Mapbox)
- Default map center coordinates and zoom level

---

## 5. Managing Pages

### Creating a New Page

1. In the admin sidebar, click **Pages**
2. Navigate to the parent page
3. Click **Add child page**
4. Select the page type
5. Fill in the fields
6. Click **Publish** (or **Save Draft** to continue later)

### Page Types

| Type | Location | Description |
|------|----------|-------------|
| `HomePage` | Root | Main landing page (max 1) |
| `AboutPage` | Under Home | About us page (max 1) |
| `BoardPage` | Under About | Board/team members |
| `NewsIndexPage` | Under Home | News listing (max 1) |
| `NewsPage` | Under News Index | Individual articles |
| `EventsPage` | Under Home | Events listing (max 1) |
| `EventDetailPage` | Under Events | Individual events |
| `GalleryPage` | Under Home | Photo gallery (max 1) |
| `ContactPage` | Under Home | Contact form (max 1) |
| `PrivacyPage` | Under Home | Privacy policy (max 1) |
| `TransparencyPage` | Under Home | Transparency docs (max 1) |
| `PressPage` | Under Home | Press office (max 1) |
| `PartnerIndexPage` | Under Home | Partners listing (max 1) |
| `PartnerPage` | Under Partners | Individual partners |

### StreamField Body Content

Most pages feature a **Body** field using Wagtail's StreamField editor. Available block types:

**Content Blocks:**
- `Rich Text` - Standard formatted text with headings, lists, links
- `Cards Grid` - Grid of cards (2-4 columns)
- `CTA` - Call-to-action section with button
- `Stats` - Statistics/numbers display
- `Quote` - Blockquote with author
- `Timeline` - Chronological timeline
- `Team Grid` - Team member profiles
- `Newsletter Signup` - Newsletter subscription form
- `Alert` - Alert/notice banner

**Media Blocks:**
- `Image` - Single image with alignment options
- `Gallery` - Image gallery grid with lightbox
- `Video Embed` - YouTube/Vimeo embed
- `Document` - Single downloadable file
- `Document List` - Multiple downloadable files
- `Map` - Interactive map (OpenStreetMap)

**Layout Blocks:**
- `Accordion` - Expandable panels (FAQ style)
- `Tabs` - Tabbed content sections
- `Two Columns` - Side-by-side layout
- `Section` - Full-width wrapper with background
- `Divider` - Visual separator
- `Spacer` - Vertical whitespace

**Event-specific Blocks:**
- `Route` - Motorcycle route with waypoints on a map
- `Event Gallery` - Photo gallery for events
- `Event Map` - Location map for events

---

## 6. News & Articles

### Creating a News Article

1. Navigate to **Pages → Home → News**
2. Click **Add child page → News Page**
3. Fill in:
   - **Title**: Article headline
   - **Cover image**: Featured image for listings
   - **Intro**: Short summary (displayed in listings)
   - **Display date**: Publication date
   - **Category**: Select from predefined categories
   - **Tags**: Add relevant tags
   - **Body**: Article content using StreamField blocks
4. Click **Publish**

### News Categories

Manage categories under **Snippets → News categories**:

| Category | Color | Use |
|----------|-------|-----|
| Club News | Red | Club announcements, internal news |
| Events Recap | Green | Reports from past events |
| Motorcycle World | Purple | Industry news, community |
| Technical | Blue | Maintenance tips, reviews |

### SEO for News

On the **Promote** tab of each article:
- **Slug**: URL path (auto-generated from title)
- **Search description**: SEO meta description
- **Show in menus**: Include in navigation if needed

---

## 7. Events

### Creating an Event

1. Navigate to **Pages → Home → Eventi**
2. Click **Add child page → Event Detail Page**
3. Fill in the **Content** tab:
   - **Title**: Event name
   - **Cover image**: Event banner
   - **Intro**: Short description for listings
   - **Start/End date**: Event schedule
   - **Location**: Name, address, coordinates (lat,lng)
   - **Category**: Rally, Touring, Social, Track Day, or Charity
   - **Body**: Full event description

4. Fill in the **Registration** tab:
   - **Registration open**: Toggle to enable/disable
   - **Registration deadline**: Cutoff date
   - **Max attendees**: 0 = unlimited
   - **Base fee**: Standard price in EUR
   - **Early bird discount**: Percentage discount
   - **Early bird deadline**: When early bird pricing ends
   - **Member discount**: Percentage discount for club members

### Event Pricing Logic

The system automatically calculates prices:

```
Standard price: base_fee
Early bird:     base_fee * (1 - early_bird_discount/100)  [before deadline]
Member price:   base_fee * (1 - member_discount_percent/100)
Both combined:  base_fee * (1 - early_bird/100) * (1 - member/100)
```

### Event Features

- **Waitlist**: When max attendees is reached, new registrations join a waitlist
- **ICS Export**: Members can download calendar files
- **Route Maps**: Add motorcycle routes with waypoints
- **Countdown**: Homepage hero block can show countdown to next event

---

## 8. Gallery

### Setting Up the Gallery

The Gallery page displays images organized by **Wagtail Collections** (albums).

1. Go to **Settings → Collections**
2. Create sub-collections under Root (e.g., "Raduno 2024", "Track Day Franciacorta")
3. Upload images to the desired collection via **Images → Add images**
4. Edit the Gallery page and optionally set a **Root collection** to limit which albums are shown

### Image Upload from Admin

1. Go to **Images** in the admin sidebar
2. Click **Add images**
3. Drag and drop or select files
4. Assign each image to a collection
5. Add tags and titles

---

## 9. Partners

### Adding a Partner

1. Navigate to **Pages → Home → Partner**
2. Click **Add child page → Partner Page**
3. Fill in:
   - **Title**: Partner/sponsor name
   - **Logo**: Partner logo image
   - **Category**: Main Sponsor, Technical, or Media Partner
   - **Intro**: Short description
   - **Body**: Full partner description
   - **Website, Email, Phone, Address**: Contact details
   - **Social URLs**: Partner's social media links
   - **Featured**: Show prominently
   - **Show on homepage**: Display on the home page
   - **Partnership dates**: Start and end dates

### Partner Categories

Manage under **Snippets → Partner categories**. Default categories:
- **Main Sponsor** - Primary sponsors
- **Technical Partner** - Service/product partners
- **Media Partner** - Press and media partners

---

## 10. Snippets

Snippets are reusable content pieces managed under **Snippets** in the admin.

### Navbar

Create and manage navigation menus:
1. Go to **Snippets → Navbars**
2. Add/edit a navbar
3. Add **Menu items** with:
   - Label (display text)
   - Link page (internal) or External URL
   - Is CTA (render as a button)
4. Assign the navbar in **Settings → Site Settings → Navigation**

### Footer

Create and manage footers:
1. Go to **Snippets → Footers**
2. Add description, copyright, contact details
3. Add **Menu items** (links to internal pages)
4. Add **Social links** (Facebook, Instagram, YouTube, etc.)
5. Assign in **Settings → Site Settings → Navigation**

### Colour Schemes

Create custom color palettes:
1. Go to **Snippets → Colour schemes**
2. Define colors: primary, secondary, accent, surface, text
3. Toggle dark mode if needed
4. Assign in **Settings → Site Settings → Theme**

### Other Snippets

| Snippet | Purpose |
|---------|---------|
| **News categories** | Organize news articles |
| **Event categories** | Organize events (Rally, Touring, etc.) |
| **Partner categories** | Organize partners/sponsors |
| **Photo tags** | Tag gallery images |
| **Products** | Membership tiers with pricing and privileges |
| **FAQs** | Frequently asked questions |
| **Testimonials** | Member quotes/reviews |
| **Press releases** | Press office content |
| **Brand assets** | Downloadable logos, fonts, templates |
| **Aid skills** | Mutual aid skill categories |

---

## 11. Members & Membership

### Member Registration

Members register through the site's registration form. After registration:
1. Email verification is sent
2. Profile can be completed (personal data, motorcycle info)
3. Membership card with QR code and barcode is generated

### Managing Members (Admin)

Go to **Snippets → Club users** (or the Members section):
- View all registered members
- Edit profiles, membership dates, card numbers
- Manage membership products
- Export member data

### Membership Products

Products define membership tiers. Manage under **Snippets → Products**:

| Product | Price | Privileges |
|---------|-------|-----------|
| Socio Ordinario | €50 | Vote, events, gallery upload |
| Socio Sostenitore | €30 | Events, 10% discount |
| Socio Premium | €100 | All privileges, 20% discount |

Each product has privilege flags:
- `grants_vote` - Assembly voting rights
- `grants_events` - Event registration access
- `grants_upload` - Gallery upload permission
- `grants_discount` - Event fee discounts
- `discount_percent` - Discount percentage

### Member Card

Each member gets a card with:
- Club name and logo
- Member name and photo
- Card number and membership dates
- **QR code**: Contains vCard data for contact sharing
- **Barcode**: Code128 format for scanning at events

---

## 12. Notifications

### Notification Types

The system supports:
- **Email**: Direct email notifications
- **Push**: Browser push notifications (PWA)
- **Digest**: Bundled notifications (daily/weekly)

### Notification Events

| Event | Trigger |
|-------|---------|
| New event published | When an event page goes live |
| Event reminder | Before event start date |
| Membership expiry | Before membership expires |
| News update | When a news article is published |

### Managing Notifications

Admin panel shows the notification queue with status, recipient, and delivery info.

Members control their preferences in their profile:
- Email notifications on/off
- Push notifications on/off
- Digest frequency: Immediate, Daily, Weekly
- Per-category toggles (news, events, membership, partners)

---

## 13. Federation

### What is Federation?

Federation allows multiple clubs to share events and coordinate activities through a secure API. Each club maintains its own independent CMS but can:
- Share events with partner clubs
- Display partner events to members
- Enable cross-club event interest/comments
- Coordinate mutual aid networks

### Setting Up Federation

1. Go to the federation admin section
2. Register partner clubs with their API endpoint URLs
3. Exchange API keys (public key `pk_` and secret key `sk_`)
4. API calls are signed with HMAC-SHA256 for security

### Security

- All API requests are HMAC-SHA256 signed
- Timestamp validation (5-minute window) prevents replay attacks
- Rate limiting: 60 requests/hour per partner
- HTML content is sanitized before storage

---

## 14. Demo Data

### Populating Demo Content

Two demo commands are available — choose the language for your default site:

```bash
# Italian demo (default locale: IT, IT+EN pages)
docker compose exec web python manage.py populate_demo_it

# English demo (default locale: EN)
docker compose exec web python manage.py populate_demo_en

# Reset and repopulate (add --flush to either command)
docker compose exec web python manage.py populate_demo_it --flush
docker compose exec web python manage.py populate_demo_en --flush
```

Both commands create:
- 4 News categories, 5 Event categories, 3 Partner categories
- 3 Membership products
- 3 Testimonials
- Full page hierarchy (Home, About, Board, News, Events, Gallery, Contact, Privacy, Transparency, Press, Partners)
- 6 news articles with realistic content
- 6 events (rallies, touring, track day, charity ride)
- 3 partners (sponsor, technical, media)
- Navbar and Footer with menu items and social links
- Complete Site Settings

`populate_demo_it` additionally creates English copies of all pages as a starting point for translation.
Other locales (DE, FR, ES) are activated later from the Wagtail admin.

### Demo Content Sources

Event data is inspired by real motorcycle club events from Northern Italy:
- **Avviamento Motori, Lands of Pisa, Spring Bayern Treffen**: annual rallies
- **Rally Lago di Garda**: lake touring event
- **Club-organized**: Tour delle Orobie, Track Day Franciacorta, Ride for Children

---

## 15. Troubleshooting

### Common Issues

**Site shows "Welcome to Wagtail" instead of demo content:**
```bash
docker compose exec web python manage.py populate_demo_it
```

**Database migrations out of sync:**
```bash
docker compose exec web python manage.py migrate
```

**Static files not loading:**
```bash
docker compose exec web python manage.py collectstatic --noinput
```

**Page tree corruption:**
```bash
docker compose exec web python manage.py fixtree
```

**Reset everything:**
```bash
docker compose down -v  # WARNING: deletes all data
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py populate_demo_it
```

### Checking System Health

```bash
# Django system check
docker compose exec web python manage.py check

# Check with deployment warnings
docker compose exec web python manage.py check --deploy

# View container logs
docker compose logs -f web
docker compose logs -f db
```

### Production Deployment

For production, update `docker-compose.yml`:

1. Use `clubcms.settings.prod` instead of `dev`
2. Set a strong `SECRET_KEY` (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
3. Set `ALLOWED_HOSTS` to your domain
4. Use `gunicorn` instead of `runserver`
5. Enable HTTPS with a reverse proxy (nginx, Caddy, Traefik)
6. Set up email backend for notifications (SMTP, SES, etc.)

---

## Appendix: Management Commands

| Command | Description |
|---------|-------------|
| `populate_demo_it` | Create Italian demo content |
| `populate_demo_it --flush` | Reset and recreate Italian demo content |
| `populate_demo_en` | Create English demo content |
| `populate_demo_en --flush` | Reset and recreate English demo content |
| `createsuperuser` | Create admin user |
| `migrate` | Apply database migrations |
| `collectstatic` | Collect static files for production |
| `fixtree` | Fix Wagtail page tree inconsistencies |
| `sync_federation` | Sync events with federated partner clubs |

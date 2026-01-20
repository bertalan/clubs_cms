# Content Pages

## Overview

Content pages provide static information about the organization. They share a common structure with customizable StreamField content.

### Multilingual

All content pages are translatable via Wagtail Localize:
- Translate action available on each page
- All text fields and StreamField blocks are translatable
- Images: only title/alt text translated, not image file

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## AboutPage

### Purpose
Main "About Us" page describing the organization's history, mission, and values.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Page title |
| Intro | Text | Brief introduction (displayed below title) |
| Body | StreamField | Main content area |

### Recommended Body Blocks

| Block | Usage |
|-------|-------|
| Rich Text | History, mission statement |
| Image + Text | Photo with description |
| Timeline | Organization history |
| Stats | Key achievements |
| Team Preview | Link to BoardPage |
| CTA | Join us invitation |

### Settings

| Setting | Value |
|---------|-------|
| Subpage Types | BoardPage |
| Max Count | 1 |

---

## BoardPage (Board of Directors)

### Purpose
Displays organization leadership, board members, and staff.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Our Team" |
| Intro | Text | Introduction text |
| Body | StreamField | Team members and content |

### Team Member Block

Each team member card includes:

| Field | Type | Required |
|-------|------|----------|
| Name | Text | Yes |
| Role/Title | Text | Yes |
| Photo | Image | No |
| Bio | Text | No |
| Email | Email | No |
| Phone | Text | No |
| Social Links | Repeater | No |

### Display Options

| Option | Description |
|--------|-------------|
| Layout | Grid (3-4 columns) or List |
| Photo Style | Circle, square, or none |
| Show Contact | Yes/No |
| Order | Manual drag-drop |

### Settings

| Setting | Value |
|---------|-------|
| Parent Page Types | AboutPage |

---

## ContactPage

### Purpose
Contact information and contact form.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Page title |
| Intro | Text | Introduction text |
| Form Title | Text | Form heading |
| Success Message | Text | Confirmation after submit |
| Body | StreamField | Additional content |

### Contact Information Section

| Field | Source |
|-------|--------|
| Address | Site Settings |
| Phone | Site Settings |
| Email | Site Settings |
| Hours | Site Settings |
| Map | Embed code or coordinates |

### Contact Form Fields

| Field | Type | Required |
|-------|------|----------|
| Name | Text | Yes |
| Email | Email | Yes |
| Subject | Dropdown | No |
| Message | Textarea | Yes |
| Privacy Consent | Checkbox | Yes |

### Form Protection (Captcha)

Choose one method in Site Settings:

| Method | Description |
|--------|-------------|
| Honeypot + Time | Hidden field + minimum submit time |
| Cloudflare Turnstile | Privacy-friendly, invisible |
| hCaptcha | Privacy-focused alternative |

See [36-WAGTAIL-ADMIN.md](36-WAGTAIL-ADMIN.md) for captcha configuration.

### Map Options

| Option | Description |
|--------|-------------|
| Show Map | Yes/No toggle |
| Map Provider | OpenStreetMap (Leaflet) |
| Geocoding | Nominatim (OSM) |
| Routing | OSRM or OpenRouteService |
| Coordinates | Latitude, Longitude |
| Zoom Level | 1-20 |

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Schema Type | ContactPage |

### Links to Press Office

ContactPage and TransparencyPage should include a link to Press Office:
- "Media & Press" → `/press/`

See [88-PRESS-OFFICE.md](88-PRESS-OFFICE.md) for Press Office page.

---

## PrivacyPage

### Purpose
Privacy policy and legal information.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Privacy Policy" |
| Last Updated | Date | Auto or manual |
| Body | StreamField | Policy content |

### Recommended Body Blocks

| Block | Usage |
|-------|-------|
| Rich Text | Policy sections |
| Accordion | Expandable sections |
| Table of Contents | Jump links |

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Show in Menus | Usually footer only |

---

## TransparencyPage

### Purpose
Legal documents, statutes, annual reports for nonprofit transparency.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Transparency" |
| Intro | Text | Introduction |
| Body | StreamField | Document groups |

### Document Group Block

| Field | Type | Description |
|-------|------|-------------|
| Group Title | Text | e.g., "Annual Reports" |
| Documents | Repeater | List of documents |

### Document Item Fields

| Field | Type |
|-------|------|
| Document Title | Text |
| Document File | Document Chooser |
| Year | Number |
| Description | Text |

### Display

Documents organized by category with:
- Download links
- File type icons
- File size display
- Year labels

---

## Content Page Summary

| Page | Max Count | Parent | Purpose |
|------|-----------|--------|---------|
| AboutPage | 1 | Root | Organization info |
| BoardPage | - | AboutPage | Team members |
| ContactPage | 1 | Root | Contact form |
| PrivacyPage | 1 | Root | Legal/privacy |
| TransparencyPage | - | Root | Documents |

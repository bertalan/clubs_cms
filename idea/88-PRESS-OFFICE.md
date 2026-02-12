# Press Office

## Overview

Dedicated section for journalists, partners and sponsors to download official club materials.

### Multilingual

| Element | Translatable |
|---------|-------------|
| PressPage | Yes (all fields) |
| PressRelease snippet | Yes (title, body) |
| Brand Kit files | No (universal) |
| Document titles | Yes (alt descriptions) |

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## URL

```
/press/
```

## Access

| Type | Visibility |
|------|------------|
| Page | Public |
| Download | Public (no login) |

---

## Sections

### 1. Brand Kit

| Content | Formats |
|---------|---------|
| Main logo | SVG, PNG, PDF |
| Monochrome logo | SVG, PNG |
| Negative logo (white) | SVG, PNG |
| Favicon | ICO, PNG 512x512 |
| Color palette | PDF with HEX/RGB codes |
| Fonts | Font link or OTF/TTF files |

### 2. Institutional Photos

| Content | Notes |
|---------|-------|
| Headquarters | HD exterior/interior photos |
| Board Members | Official member photos |
| Vintage motorcycles | Representative selection |
| Main events | 5-10 photos per event |

### 3. Press Releases

| Field | Description |
|-------|-------------|
| Title | Release title |
| Date | Publication date |
| Body | Release text |
| Attachment | Downloadable PDF |
| Archive | Grouped by year |

### 4. Press Contact

| Field | Value |
|-------|-------|
| Email | press@motoclub.it |
| Phone | Optional |
| Contact Person | Press officer name |
| Notes | Response times, hours |

---

## Page Model

### PressPage

| Field | Type | Description |
|-------|------|-------------|
| title | Text | "Press Office" |
| intro | RichText | Introduction |
| press_email | Email | Press contact email |
| press_phone | Text | Phone (optional) |
| press_contact | Text | Contact person name |
| body | StreamField | Main content |

### StreamField Blocks

| Block | Usage |
|-------|-------|
| DocumentListBlock | For Brand Kit files |
| GalleryBlock | For institutional photos |
| AccordionBlock | For releases by year |

---

## Press Releases (Snippet)

### Fields

| Field | Type | Description |
|-------|------|-------------|
| title | Text | Release title |
| date | Date | Publication date |
| body | RichText | Release text |
| attachment | Document | PDF attachment |
| is_archived | Boolean | Archived |

### Admin Path

```
Snippets → Press Releases
```

### Admin Filters

| Filter | Options |
|--------|---------|
| Year | Year selection |
| Archived | Yes / No |

---

## Brand Assets (Snippet)

### Fields

| Field | Type | Description |
|-------|------|-------------|
| name | Text | Asset name (e.g., "Main logo") |
| category | Choice | Logo / Photo / Document |
| file | Document | Downloadable file |
| preview | Image | Preview (for photos) |
| description | Text | Usage notes |
| order | Integer | Display order |

### Categories

| Category | Content |
|----------|---------|
| logo | Logos in various formats |
| colors | Palette, guidelines |
| photos | Institutional HD photos |
| templates | Social templates, presentations |

### Admin Path

```
Snippets → Brand Assets
```

---

## Auto-Archive

### Logic

| Condition | Action |
|-----------|--------|
| Release > 1 year | Suggests archiving |
| `is_archived = True` | Moved to "Archive" accordion |

### Display

| Status | Position |
|--------|----------|
| Active | Main list |
| Archived | Accordion by year |

---

## Links from Other Pages

### From Transparency

Add link in documents section:
- "Press materials" → `/press/`

### From Footer

Optional link in footer:
- "Resources" or "Documents" section

### From About

Link in text or sidebar:
- "Download our brand kit"

---

## Template

### Structure

```
templates/website/press_page.html
```

### Layout

| Section | Content |
|---------|---------|
| Header | Title + intro |
| Brand Kit | Grid with preview + download |
| Photos | Gallery with HD download |
| Releases | List with year filter |
| Archive | Accordion by year |
| Contact | Card with email/phone |

---

## Download Tracking (Optional)

### Log Fields

| Field | Description |
|-------|-------------|
| asset | Downloaded asset |
| timestamp | Download date/time |
| ip | IP (anonymized) |
| user_agent | Browser |

### Admin Report

| Metric | Description |
|--------|-------------|
| Total downloads | Per asset |
| Monthly downloads | Monthly trend |
| Most downloaded | Top 10 |

---

## SEO

### Meta

| Field | Value |
|-------|-------|
| Title | "Press Office - {Club Name}" |
| Description | "Download official logos, photos and press releases" |

### Schema.org

No specific schema required.

---

## Permissions

| Action | Who |
|--------|-----|
| View page | Everyone |
| Download assets | Everyone |
| Manage assets | Staff |
| Create releases | Staff |
| Archive releases | Staff |

---

## References

- [12-CONTENT-PAGES.md](12-CONTENT-PAGES.md) - TransparencyPage (cross-link)
- [23-MEDIA-BLOCKS.md](23-MEDIA-BLOCKS.md) - DocumentListBlock, GalleryBlock

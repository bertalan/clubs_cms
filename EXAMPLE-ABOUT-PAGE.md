# Example: About Page

## Overview

How to structure an About page using Wagtail page model and StreamField blocks.

---

## Page Type

| Setting | Value |
|---------|-------|
| Model | AboutPage |
| Template | Theme-specific (e.g., `themes/velocity/about_page.html`) |
| Parent | HomePage |
| Max Instances | 1 per language |

---

## Page Fields

### Header Section

| Field | Type | Description |
|-------|------|-------------|
| title | Text | Page title (inherited) |
| intro | Text (255 chars) | Subtitle/tagline |
| cover_image | Image | Header background |

### Body Content

| Field | Type | Description |
|-------|------|-------------|
| body | StreamField | Main content blocks |

---

## Recommended Blocks

| Block | Use Case |
|-------|----------|
| RichTextBlock | Introduction paragraph |
| TimelineBlock | Club history milestones |
| TeamBlock | Board members / staff |
| StatsBlock | Key numbers (members, events, years) |
| GalleryBlock | Historical photos |
| CTABlock | Join us call-to-action |

### Example Block Order

1. RichTextBlock - Who we are
2. StatsBlock - Numbers at a glance
3. TimelineBlock - Our history
4. TeamBlock - Meet the board
5. GalleryBlock - Photo gallery
6. CTABlock - Become a member

---

## Schema.org

### Type

| Property | Value |
|----------|-------|
| @type | Organization |
| name | Page title |
| url | Page URL |
| description | Intro text |

### Additional Properties

| Property | Source |
|----------|--------|
| logo | Site Settings logo |
| foundingDate | From timeline or settings |
| address | From Site Settings |
| email | From Site Settings |
| telephone | From Site Settings |

---

## Template Structure

### Layout

| Section | Content |
|---------|---------|
| Hero | Cover image with title overlay |
| Content | StreamField blocks rendered |

### Hero Style

| Element | Style |
|---------|-------|
| Height | Medium (60vh) |
| Overlay | Primary color at 70% |
| Title | Large, centered, white |
| Subtitle | Medium, white at 80% |

---

## SEO Panel

| Field | Description |
|-------|-------------|
| Meta Title | Override page title |
| Meta Description | For search results |
| Social Image | Open Graph image |

---

## Translation

| Translatable | Fields |
|--------------|--------|
| Yes | title, intro, body |
| Yes (Wagtail Images) | cover_image alt text |
| Auto | URL slug per language |

---

## Admin Panels

| Panel | Fields |
|-------|--------|
| Content | title, intro, cover_image, body |
| SEO | meta title, description, social image |
| Settings | slug, publish date |

---

## Advantages

| Aspect | Benefit |
|--------|---------|
| StreamField | Editor chooses block order |
| JSON-LD | Automatic SEO schema |
| Multilingual | Wagtail Localize ready |
| Flexible | Any combination of blocks |

---

## References

- [12-CONTENT-PAGES.md](12-CONTENT-PAGES.md) - Content page types
- [20-STREAMFIELD-BLOCKS.md](20-STREAMFIELD-BLOCKS.md) - Available blocks
- [40-SEO-JSONLD.md](40-SEO-JSONLD.md) - Schema.org implementation

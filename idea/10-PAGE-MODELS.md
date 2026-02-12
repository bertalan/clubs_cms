# Page Models Base

## Overview

Page models define the content structure in Wagtail. All pages inherit from Wagtail's native `Page` class and use built-in features for content management.

## Page Hierarchy

The site uses the following page structure:

```
Root (Site)
├── HomePage (max 1)
├── AboutPage
│   └── BoardPage
├── NewsIndexPage (max 1)
│   └── NewsPage (multiple)
├── EventsPage (max 1)
│   └── EventDetailPage (multiple)
├── GalleryPage (max 1)
├── ContactPage (max 1)
├── PrivacyPage (max 1)
├── TransparencyPage
├── PressPage (max 1)
├── PartnersPage (max 1)
└── MutualAidPage (max 1)
```

### Member-Only Pages (authenticated)

```
/my-events/     → MyEventsPage (favorites, registrations)
/my-profile/    → ProfilePage (member profile)
/my-card/       → MemberCardPage (digital card)
/my-photos/     → MyPhotosPage (upload history)
```

These are not Wagtail pages but Django views with authentication required.

## Base Page Structure

All content pages share common characteristics:

### Content Tab Fields

| Field | Type | Purpose |
|-------|------|---------|
| Title | Text (required) | Page title, auto-generates slug |
| Body | StreamField | Flexible content area |

### Promote Tab Fields (SEO)

| Field | Type | Purpose |
|-------|------|---------|
| Slug | Auto-generated | URL path segment |
| Title Tag | Text | Custom browser title |
| Meta Description | Text | Search result description |
| Social Image | Image | Open Graph/Twitter image |

### Settings Tab

| Field | Type | Purpose |
|-------|------|---------|
| Go Live Date | DateTime | Scheduled publishing |
| Expiry Date | DateTime | Auto-unpublish |
| Show in Menus | Boolean | Navigation visibility |

## StreamField Content Blocks

Pages use StreamField for flexible content. Available blocks:

| Block Type | Purpose |
|------------|---------|
| Hero Slider | Full-width image carousel |
| Hero Banner | Single image with text overlay |
| Rich Text | Formatted text content |
| Cards Grid | Feature cards in grid layout |
| CTA Section | Call-to-action with button |
| Stats | Statistics counters |
| Gallery | Image gallery from collection |
| Video Embed | YouTube/Vimeo embed |
| Accordion | Expandable FAQ sections |
| Tabs | Tabbed content sections |

See [20-STREAMFIELD-BLOCKS.md](20-STREAMFIELD-BLOCKS.md) for block details.

## Page Type Constraints

Configure in admin which child pages each type allows:

| Parent Page | Allowed Children |
|-------------|------------------|
| HomePage | None (landing only) |
| AboutPage | BoardPage |
| NewsIndexPage | NewsPage |
| EventsPage | EventDetailPage |
| GalleryPage | None |
| ContactPage | None |

## Page Settings

### Maximum Instances

| Page Type | Max Count | Reason |
|-----------|-----------|--------|
| HomePage | 1 | Single homepage |
| NewsIndexPage | 1 | Single news section |
| EventsPage | 1 | Single events section |
| GalleryPage | 1 | Single gallery hub |
| ContactPage | 1 | Single contact page |
| PrivacyPage | 1 | Single privacy policy |
| PressPage | 1 | Single press office |
| PartnersPage | 1 | Single partners hub |
| MutualAidPage | 1 | Single aid network page |

### Template Assignment

Templates are located in `templates/website/pages/`:

| Page Type | Template File |
|-----------|---------------|
| HomePage | `home_page.html` |
| ContentPage | `content_page.html` |
| NewsIndexPage | `news_index_page.html` |
| NewsPage | `news_page.html` |
| EventsPage | `events_page.html` |
| EventDetailPage | `event_detail_page.html` |
| GalleryPage | `gallery_page.html` |
| ContactPage | `contact_page.html` |
| PressPage | `press_page.html` |
| PartnersPage | `partners_page.html` |
| MutualAidPage | `mutual_aid_page.html` |

All templates extend `templates/base.html` which loads the active theme.

### Theme Loading

The base template:
1. Reads theme selection from Site Settings
2. Loads CSS from `static/css/themes/{theme}/`
3. Injects CSS variables from admin color configuration

Available themes: velocity, heritage, terra, zen, clubs, tricolore

See [30-TEMPLATE-SYSTEM.md](30-TEMPLATE-SYSTEM.md) for details.

## JSON-LD Schema

Schema.org structured data is generated automatically:

| Page Type | Schema Type |
|-----------|-------------|
| HomePage | Organization |
| NewsPage | Article |
| EventDetailPage | Event |
| ContactPage | ContactPage |
| PressPage | WebPage + Organization |
| PartnersPage | ItemList (LocalBusiness) |
| MutualAidPage | WebPage |
| Other pages | WebPage |

See [40-SEO-JSONLD.md](40-SEO-JSONLD.md) for schema details.

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| `Page` model | Base content type |
| `StreamField` | Flexible content |
| `FieldPanel` | Admin form fields |
| `MultiFieldPanel` | Grouped fields |
| `InlinePanel` | Related items |
| `parent_page_types` | Hierarchy control |
| `subpage_types` | Child page control |
| `max_count` | Instance limits |

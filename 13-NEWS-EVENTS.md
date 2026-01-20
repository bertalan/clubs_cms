# News & Events

## Overview

News and Events use a parent-child page structure for organization and filtering.

### Multilingual

News and Events pages are fully translatable:
- Index pages: title, intro, body
- NewsPage: title, intro, body, categories
- EventDetailPage: all text fields, location description

**Note:** Dates, times, prices remain synced (same across languages).

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## Page Structure

```
NewsIndexPage (listing)
└── NewsPage (articles)

EventsPage (listing)
└── EventDetailPage (individual events)
```

---

## NewsIndexPage

### Purpose
Lists all news articles with filtering and pagination.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "News" or "Latest Updates" |
| Intro | Text | Section introduction |
| Body | StreamField | Optional content above listing |

### Listing Configuration

| Option | Description |
|--------|-------------|
| Items per Page | Number (default: 12) |
| Default Sort | Date descending |
| Show Filters | Categories, tags, date |
| Layout | Grid or list view |

### Filtering Options

| Filter | Type |
|--------|------|
| Category | Dropdown |
| Tag | Tag cloud or dropdown |
| Date Range | Date picker |
| Search | Text search |

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Subpage Types | NewsPage only |
| Schema Type | CollectionPage with ItemList |

---

## NewsPage (Article)

### Purpose
Individual news article or blog post.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Article headline |
| Display Date | Date | Publication date |
| Author | User Chooser | Article author |
| Cover Image | Image Chooser | Featured image |
| Intro | Text | Article summary/excerpt |
| Body | StreamField | Article content |
| Gallery | StreamField | Photo gallery (GalleryImageBlock) |
| Tags | Tag Chooser | Article tags |
| Category | Snippet Chooser | Article category |

### Body StreamField Blocks

| Block | Purpose |
|-------|---------|
| RichTextBlock | Formatted text |
| ImageBlock | Single image with caption |
| GalleryBlock | Image gallery from Collection |
| VideoEmbedBlock | YouTube, Vimeo embeds |
| DocumentBlock | Single file attachment (PDF, DOC, etc.) |
| DocumentListBlock | Multiple file attachments |
| QuoteBlock | Blockquote with author |
| MapBlock | Location map |

### Gallery Features

The gallery field supports browsable lightbox display:

| Feature | Description |
|---------|-------------|
| Lightbox Navigation | Previous/Next with keyboard arrows |
| Image Title | Inherited from Wagtail image title |
| Image Caption | Inherited from image alt text or custom caption |
| Thumbnails | Grid display with click to enlarge |
| Swipe Support | Touch gestures on mobile |
| Download | Optional download button |

### Promote Tab (Additional)

| Field | Type | Description |
|-------|------|-------------|
| Social Image | Image | Open Graph image |
| Featured | Checkbox | Show on homepage |

### Body Blocks

| Block | Usage |
|-------|-------|
| Rich Text | Main article content |
| Image | Inline images |
| Image Gallery | Photo galleries |
| Video Embed | YouTube/Vimeo |
| Quote | Pull quotes |
| Related Articles | Links to other news |

### Display Elements

| Element | Source |
|---------|--------|
| Title | Title field |
| Date | Display Date |
| Author | Author field + avatar |
| Reading Time | Calculated from content |
| Share Buttons | Social sharing |
| Tags | Tags field |
| Related | Automatic or manual |

### Settings

| Setting | Value |
|---------|-------|
| Parent Page Types | NewsIndexPage only |
| Schema Type | Article |

### Schema.org (Article)

| Property | Source |
|----------|--------|
| @type | "Article" |
| headline | Title |
| datePublished | Display Date |
| dateModified | Last published |
| author | Author name |
| image | Cover Image |
| publisher | Organization data |

---

## EventsPage

### Purpose
Lists upcoming and past events.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Events" |
| Intro | Text | Section introduction |
| Body | StreamField | Optional content |

### Listing Configuration

| Option | Description |
|--------|-------------|
| Default View | Upcoming events first |
| Show Past Events | Yes, in separate section |
| Calendar View | Optional calendar display |
| Items per Page | Number (default: 12) |

### Filtering Options

| Filter | Type |
|--------|------|
| Date Range | Date picker |
| Category | Dropdown |
| Location | Text or dropdown |
| Registration Status | Open/Closed |

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Subpage Types | EventDetailPage only |
| Schema Type | CollectionPage with ItemList |

---

## EventDetailPage

### Purpose
Individual event with details and registration.

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | Event name |
| Start Date | DateTime | Event start |
| End Date | DateTime | Event end (optional) |
| Location Name | Text | Venue name |
| Location Address | Text | Full address |
| Location Coordinates | Text | Lat/Long for map |
| Image | Image Chooser | Event image |
| Intro | Text | Short description |
| Body | StreamField | Full event details |
| Gallery | StreamField | Photo gallery (GalleryImageBlock) |
| Tags | Tag Chooser | Event tags (shared with News) |

### Body StreamField Blocks

| Block | Purpose |
|-------|---------|
| RichTextBlock | Formatted text (program, details) |
| ImageBlock | Single image with caption |
| GalleryBlock | Image gallery from Collection |
| VideoEmbedBlock | YouTube, Vimeo embeds |
| DocumentBlock | Single file attachment (regulations, forms) |
| DocumentListBlock | Multiple attachments (maps, info sheets) |
| MapBlock | Location map |
| RouteBlock | Event route with GPX |

### Gallery Features

Same lightbox gallery as NewsPage:
- Browsable with keyboard/swipe navigation
- Title and caption from Wagtail image metadata
- Responsive thumbnail grid
- Fullscreen viewing mode

### Registration Section

| Field | Type | Description |
|-------|------|-------------|
| Registration Open | Boolean | Enable/disable signup |
| Registration Deadline | DateTime | Cutoff date |
| Max Participants | Number | Capacity limit |
| Price | Decimal | Event cost (0 = free) |
| Members Only | Boolean | Restrict to members |
| External Registration | URL | External signup link |

### Early Booking

Configurable discount tiers based on registration date.

See [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) for:
- Early booking tier configuration
- Discount percentage per tier
- Price display with savings

### Passenger/Companion

Riders can register with a passenger (pillion).

See [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) for:
- Passenger as member or non-member
- Optional passenger details
- Passenger pricing options

### Display Elements

| Element | Source |
|---------|--------|
| Event Header | Title, image, date |
| Date/Time | Start/End formatted |
| Location | Name + address + map |
| Registration Status | Open/Closed/Full |
| Spots Remaining | Calculated |
| Register Button | If open |
| Add to Calendar | ICS download |
| Share | Social buttons |

### Settings

| Setting | Value |
|---------|-------|
| Parent Page Types | EventsPage only |
| Schema Type | Event |

### Schema.org (Event)

| Property | Source |
|----------|--------|
| @type | "Event" |
| name | Title |
| description | Intro |
| startDate | Start Date (ISO 8601) |
| endDate | End Date (ISO 8601) |
| location.name | Location Name |
| location.address | Location Address |
| image | Event Image |
| offers | Price + availability |
| organizer | Organization data |

See [82-EVENT-REGISTRATIONS.md](82-EVENT-REGISTRATIONS.md) for registration handling.

---

## News Categories (Snippet)

Manage via **Snippets → News Categories**:

| Field | Type |
|-------|------|
| Name | Text |
| Slug | Auto-generated |
| Description | Text |
| Color | Color picker (optional) |

## Tags

Tags are managed automatically:
- Created on first use
- Shared across all news
- Displayed as clickable filters
- Used for related articles

# Content Blocks

## Overview

Content blocks display text, data, and interactive elements within page content.

---

## CardBlock

Single content card with image, title, and text.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Image | Image Chooser | No | Card image |
| Title | Text | Yes | Card heading |
| Text | Text | No | Card description |
| Link | URL/Page | No | Card click destination |
| Link Text | Text | No | Button text |

---

## CardsGridBlock

Grid of multiple cards.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Cards | Repeater | Yes | 1-12 cards |
| Columns | Dropdown | No | 2, 3, or 4 columns |
| Card Style | Dropdown | No | Default, Bordered, Shadow |

### Card Grid Styles

| Style | Description |
|-------|-------------|
| Default | Clean minimal cards |
| Bordered | Subtle border |
| Shadow | Elevated with shadow |
| Overlay | Text over image |

---

## CTABlock

Call-to-action section with prominent button.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | Yes | Main heading |
| Text | Text | No | Supporting text |
| Button Text | Text | Yes | Button label |
| Button Link | URL/Page | Yes | Button destination |
| Background | Dropdown | No | Primary, Secondary, Dark |
| Alignment | Dropdown | No | Left, Center, Right |

### Background Options

| Option | Description |
|--------|-------------|
| Primary | Brand primary color |
| Secondary | Brand secondary color |
| Dark | Dark background, light text |
| Image | Custom background image |

---

## StatsBlock

Display key statistics/numbers.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Stats | Repeater | Yes | 2-6 stat items |
| Animate | Boolean | No | Count-up animation |
| Layout | Dropdown | No | Row, Grid |

### Stat Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Icon | Icon Chooser | No | FontAwesome or similar |
| Value | Text | Yes | Number or text |
| Label | Text | Yes | What the stat represents |
| Suffix | Text | No | %, +, etc. |

### Example Stats

| Icon | Value | Label |
|------|-------|-------|
| 👥 | 150+ | Members |
| 📅 | 25 | Events per year |
| 🏍️ | 50,000 | Km traveled |

---

## QuoteBlock

Pull quote or testimonial.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Quote | Text | Yes | Quote text |
| Author | Text | No | Person quoted |
| Role | Text | No | Author's title/role |
| Photo | Image Chooser | No | Author photo |
| Style | Dropdown | No | Simple, Card, Large |

---

## TestimonialsBlock

Multiple testimonials in carousel or grid.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Testimonials | Repeater | Yes | Quote items |
| Layout | Dropdown | No | Carousel, Grid |
| Autoplay | Boolean | No | For carousel |

---

## TimelineBlock

Chronological sequence of events.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Items | Repeater | Yes | Timeline entries |
| Style | Dropdown | No | Vertical, Horizontal |

### Timeline Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Year/Date | Text | Yes | Time marker |
| Title | Text | Yes | Event title |
| Description | Text | Yes | Event details |
| Image | Image Chooser | No | Optional image |

---

## RichTextBlock

Formatted text content with WYSIWYG editor.

### Features

| Feature | Description |
|---------|-------------|
| Headings | H2, H3, H4 |
| Formatting | Bold, italic, underline |
| Lists | Bullet and numbered |
| Links | Internal pages, external URLs |
| Images | Inline images |
| Embeds | Videos, social media |

---

## TableBlock

Data table with rows and columns.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Table Data | Table | Yes | Rows and columns |
| Has Header | Boolean | No | First row as header |
| Striped | Boolean | No | Alternating row colors |
| Responsive | Boolean | No | Horizontal scroll on mobile |

---

## FeaturedPagesBlock

Highlight selected pages.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Pages | Page Chooser (multi) | Yes | Selected pages |
| Layout | Dropdown | No | Cards, List |
| Show Image | Boolean | No | Display page image |
| Show Excerpt | Boolean | No | Display page intro |

---

## AlertBlock

Notification or announcement banner.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Message | Text | Yes | Alert text |
| Type | Dropdown | No | Info, Success, Warning, Error |
| Dismissible | Boolean | No | Can be closed |
| Link | URL/Page | No | Optional action link |

### Alert Types

| Type | Color | Icon |
|------|-------|------|
| Info | Blue | ℹ️ |
| Success | Green | ✓ |
| Warning | Yellow | ⚠️ |
| Error | Red | ✕ |

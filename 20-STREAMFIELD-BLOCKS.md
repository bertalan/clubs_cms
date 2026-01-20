# StreamField Blocks

## Overview

StreamField blocks provide flexible content editing in Wagtail. All blocks use native Wagtail features with configuration via admin panels.

## Block Categories

| Category | Purpose | Blocks |
|----------|---------|--------|
| Hero | Full-width headers | Slider, Banner, Countdown |
| Content | Text/data sections | Cards, Stats, Quote, Timeline |
| Media | Images/video/docs | Gallery, Video, Documents, Map |
| Layout | Structure | Grid, Columns, Accordion, Tabs |
| Route | Maps with routes | RouteBlock |

See individual block documentation:
- [21-HERO-BLOCKS.md](21-HERO-BLOCKS.md)
- [22-CONTENT-BLOCKS.md](22-CONTENT-BLOCKS.md)
- [23-MEDIA-BLOCKS.md](23-MEDIA-BLOCKS.md)
- [24-LAYOUT-BLOCKS.md](24-LAYOUT-BLOCKS.md)
- [87-ROUTE-MAPS.md](87-ROUTE-MAPS.md)

---

## Common Block Settings

Every block includes a Settings panel with:

| Field | Type | Description |
|-------|------|-------------|
| Custom ID | Text | HTML id attribute for anchors |
| Custom Class | Text | Additional CSS classes |
| Background | Dropdown | Default, Light, Dark, Primary |
| Padding | Dropdown | Small, Medium, Large |

---

## Block Availability by Page Type

| Page Type | Available Blocks |
|-----------|------------------|
| HomePage | All blocks |
| ContentPage | All blocks |
| NewsPage | Content, Media, Layout |
| EventDetailPage | Content, Media, Layout, Route |
| GalleryPage | Media only |

---

## Native Wagtail Block Types

StreamField uses these built-in Wagtail block types:

### Chooser Blocks

| Block | Purpose | Admin UI |
|-------|---------|----------|
| ImageChooserBlock | Select image | Image picker modal |
| DocumentChooserBlock | Select document | Document picker |
| PageChooserBlock | Select page | Page tree picker |
| SnippetChooserBlock | Select snippet | Snippet picker |
| EmbedBlock | Video/embed URL | URL input with preview |

### Input Blocks

| Block | Purpose | Admin UI |
|-------|---------|----------|
| CharBlock | Short text | Text input |
| TextBlock | Long text | Textarea |
| RichTextBlock | Formatted text | WYSIWYG editor |
| URLBlock | Web address | URL input |
| EmailBlock | Email address | Email input |
| IntegerBlock | Whole number | Number input |
| DecimalBlock | Decimal number | Number input |
| BooleanBlock | Yes/No | Checkbox |
| DateBlock | Date | Date picker |
| TimeBlock | Time | Time picker |
| DateTimeBlock | Date + time | DateTime picker |

### Choice Blocks

| Block | Purpose | Admin UI |
|-------|---------|----------|
| ChoiceBlock | Single selection | Dropdown |
| MultipleChoiceBlock | Multiple selection | Checkboxes |

### Structural Blocks

| Block | Purpose | Admin UI |
|-------|---------|----------|
| StructBlock | Group of fields | Fieldset |
| ListBlock | Repeatable items | Add/remove buttons |
| StreamBlock | Mixed content | Block chooser |

---

## Template Location

Block templates are in `templates/website/blocks/`:

| Block | Template |
|-------|----------|
| HeroSliderBlock | `hero_slider_block.html` |
| HeroBannerBlock | `hero_banner_block.html` |
| CardsGridBlock | `cards_grid_block.html` |
| GalleryBlock | `gallery_block.html` |
| AccordionBlock | `accordion_block.html` |
| etc. | `{block_name}_block.html` |

---

## Rendering in Templates

StreamField content renders automatically:

| Template Tag | Usage |
|--------------|-------|
| `{% include_block page.body %}` | Render entire StreamField |
| `{% include_block block %}` | Render single block |
| `{{ block.value.field }}` | Access block field |

---

## Block Icons

Each block has an icon visible in the admin:

| Icon | Meaning |
|------|---------|
| 🖼️ image | Image-related |
| 📄 doc-full | Document/card |
| 🎬 media | Video/audio |
| 📊 order | Statistics |
| 📝 openquote | Quote |
| 🗂️ grip | Grid/cards |
| 📋 list-ul | List/accordion |
| ⏰ time | Timeline |
| 📍 site | Map/location |

---

## Admin Panel Organization

Blocks appear in the editor organized by category:

| Section | Contains |
|---------|----------|
| Hero Sections | Slider, Banner, Countdown |
| Content | Cards, Stats, Quote, CTA |
| Media | Gallery, Video, Image, Documents |
| Layout | Grid, Columns, Accordion, Tabs |
| Maps | Route, Location |

---

## Block Validation

Native Wagtail validation:

| Rule | Configuration |
|------|---------------|
| Required fields | `required=True` (default) |
| Max length | `max_length=100` |
| Min/Max items | `min_num=1, max_num=10` |
| Allowed pages | `page_type="website.EventDetailPage"` |

---

## Responsive Behavior

All blocks are mobile-responsive:

| Block | Mobile Behavior |
|-------|-----------------|
| Grid | Stacks vertically |
| Columns | Stacks vertically |
| Slider | Touch swipe enabled |
| Gallery | 2 columns on mobile |
| Tabs | Converts to accordion |

---

## Theme Support

All blocks adapt to the 6 available themes. Colors and styles come from CSS variables:

| Theme | Block Style Variations |
|-------|------------------------|
| Velocity | Modern, sharp edges, bold colors |
| Heritage | Classic, serif accents, warm tones |
| Terra | Organic, rounded, earth colors |
| Zen | Minimal, clean, neutral palette |
| Clubs | Premium, gold accents, dark backgrounds |
| Tricolore | Italian flag colors, patriotic accents |

### Theme-Specific Rendering

Blocks inherit theme variables automatically:

| CSS Variable | Block Usage |
|--------------|-------------|
| `--color-primary` | CTA buttons, links, accents |
| `--color-secondary` | Secondary buttons, highlights |
| `--color-surface` | Card backgrounds |
| `--color-text` | Body text |
| `--color-heading` | Titles, headings |
| `--border-radius` | Cards, buttons, images |
| `--font-heading` | Block titles |
| `--font-body` | Block content |

### Block Template Location by Theme

Templates can be theme-specific:

| Priority | Path |
|----------|------|
| 1 (first) | `templates/themes/{theme}/blocks/{block}.html` |
| 2 (fallback) | `templates/website/blocks/{block}.html` |

---

## Multilingual Support

Blocks support Wagtail Localize for translations.

### Translatable Fields

| Field Type | Translatable | Notes |
|------------|--------------|-------|
| CharBlock | Yes | All text content |
| TextBlock | Yes | All text content |
| RichTextBlock | Yes | Full content translation |
| ImageChooserBlock | Optional | Can use same or different image |
| PageChooserBlock | Auto | Links to translated page version |
| URLBlock | Optional | May need locale-specific URL |
| ChoiceBlock | No | Options are code values |
| BooleanBlock | No | True/false unchanged |
| NumberBlocks | No | Numbers unchanged |

### Translation Workflow

| Step | Action |
|------|--------|
| 1 | Create page in default language |
| 2 | Add StreamField content |
| 3 | Use "Translate" action in admin |
| 4 | Edit translated block content |
| 5 | Publish translated version |

### Sync vs Override

| Mode | Behavior |
|------|----------|
| Synced | Changes in source update translation |
| Overridden | Translation independent of source |

### Language-Specific Images

For blocks with images:

| Option | Usage |
|--------|-------|
| Same image | Universal visuals (logos, photos) |
| Different image | Text in image, locale-specific |

### RTL Support

Blocks automatically adapt for RTL languages:

| Block | RTL Behavior |
|-------|--------------|
| Grid | Direction reversed |
| Columns | Order swapped |
| Slider | Navigation mirrored |
| Text | Right-aligned |

---

## Related Documentation

| Doc | Topic |
|-----|-------|
| [10-PAGE-MODELS.md](10-PAGE-MODELS.md) | Page types using blocks |
| [30-TEMPLATE-SYSTEM.md](30-TEMPLATE-SYSTEM.md) | Template structure |

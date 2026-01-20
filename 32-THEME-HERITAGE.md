# Theme: Heritage (Classic)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Elegant, traditional, luxury feel |
| Framework | Bootstrap 5 (CSS only) |
| Fonts | Playfair Display (headings), Lato (body) |
| Bundle Target | <80KB CSS |

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary | `#1E3A5F` (navy) | Navbar, headings |
| Secondary | `#D4AF37` (gold) | Borders, accents |
| Accent | `#8B1538` (bordeaux) | Links, highlights |
| Surface | `#FDFCF7` (cream) | Page background |
| Surface Alt | `#FFFFFF` | Cards |
| Text Primary | `#1a1a1a` | Body text |
| Text Muted | `#555555` | Secondary text |

## Component Characteristics

### Navbar
- Dark navy background
- Logo on left, menu items right
- Gold accent on active/hover
- Collapsible on mobile

### Hero Sections
- 70vh height maximum
- Overlay badge with serif text
- Elegant serif heading
- Subtle gradient overlay
- Single or dual CTA buttons

### Cards
- 1px gold border
- Minimal rounded corners (4-8px)
- Subtle shadow on hover
- Serif headings inside

### Buttons
- Rectangular shape (4px radius)
- Outline and filled variants
- Gold or navy colors
- Uppercase text option

### Grid Layouts
- Bootstrap grid system
- `.row` and `.col-*` classes
- Consistent gutter spacing

## Typography

| Element | Style |
|---------|-------|
| H1 | Playfair Display, 2.5-4rem, weight 700 |
| H2 | Playfair Display, 2rem, weight 600 |
| H3 | Playfair Display, 1.5rem, weight 600 |
| Body | Lato, 1rem, weight 400, line-height 1.7 |
| Small | Lato, 0.875rem |

## Decorative Elements

- Gold underlines on headings
- Ornamental dividers
- Subtle texture backgrounds (optional)
- Classic iconography

## Static Files

```
static/css/themes/heritage/
├── main.css          → Bootstrap + overrides
├── components.css    → Block-specific styles
└── fonts.css         → Font loading
```

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Heritage" from Theme dropdown
2. Configure colors (navy, gold palette recommended)
3. Upload classic/elegant logo
4. Save and preview

## Use Cases

- Historical organizations
- Luxury brands
- Traditional clubs
- Cultural institutions
- Wine/gastronomy sites

## Accessibility

- High contrast text
- Clear link styling
- Readable serif fonts at proper sizes
- Alternative text for decorative elements

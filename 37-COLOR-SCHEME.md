# Dynamic Color System

## Overview

Colors are managed entirely through the Wagtail admin, eliminating hardcoded values in templates or CSS. This allows editors to customize the site appearance without developer intervention.

## Color Scheme Management

### Admin Location

**Snippets → Color Schemes**

### Creating Color Schemes

1. Go to **Snippets → Color Schemes**
2. Click "Add Color Scheme"
3. Enter scheme name (e.g., "Velocity Dark")
4. Configure colors using the color picker
5. Save

### Color Fields

| Field | CSS Variable | Purpose |
|-------|-------------|---------|
| Name | – | Identifier for the scheme |
| Primary | `--primary` | Brand color, navbar, headings |
| Secondary | `--secondary` | CTAs, highlights, accents |
| Accent | `--accent` | Links, hover states |
| Surface | `--surface` | Main background |
| Surface Alt | `--surface-alt` | Cards, alternate sections |
| Text Primary | `--text` | Main body text |
| Text Muted | `--text-muted` | Secondary text, captions |

## Predefined Schemes

The following schemes are available by default:

### Velocity Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Velocity Light | #0F172A | #F59E0B | #8B5CF6 |
| Velocity Dark | #F8FAFC | #F59E0B | #8B5CF6 |

### Heritage Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Heritage Gold | #1E3A5F | #D4AF37 | #8B1538 |
| Heritage Navy | #D4AF37 | #1E3A5F | #8B1538 |

### Terra Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Terra Earth | #2D3B2D | #4A7C59 | #F2C94C |
| Terra Dark | #E8DFD0 | #4A7C59 | #F2C94C |

### Zen Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Zen Light | #111111 | #0066FF | #0066FF |

### Clubs Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Clubs Black | #0A0A0A | #C41E3A | #E02547 |
| Clubs Red | #C41E3A | #0A0A0A | #FFFFFF |

### Tricolore Schemes

| Scheme | Primary | Secondary | Accent |
|--------|---------|-----------|--------|
| Tricolore Classic | #009246 | #CE2B37 | #C9A227 |
| Tricolore Elegant | #1a1a1a | #009246 | #CE2B37 |

## Applying Color Schemes

### Site-Wide

1. Go to **Settings → Site Settings**
2. Select color scheme from dropdown
3. Save

### Per-Page Override (Optional)

Pages can optionally override the site scheme:
1. Edit page in Wagtail
2. Go to "Promote" tab
3. Select page-specific color scheme
4. Publish

## CSS Variable Output

The selected scheme outputs CSS variables in the `<head>`:

```html
<style>
:root {
  --primary: #0F172A;
  --secondary: #F59E0B;
  --accent: #8B5CF6;
  --surface: #F8FAFC;
  --surface-alt: #FFFFFF;
  --text: #111111;
  --text-muted: #666666;
}
</style>
```

## Using Colors in CSS

All theme CSS files reference variables, not hardcoded colors:

```css
/* Buttons */
.btn-primary { 
  background: var(--primary); 
  color: var(--surface); 
}
.btn-secondary { 
  background: var(--secondary); 
  color: var(--text); 
}

/* Cards */
.card { 
  background: var(--surface-alt); 
  border-color: var(--secondary); 
}

/* Typography */
h1, h2, h3 { color: var(--text); }
p { color: var(--text-muted); }
a { color: var(--accent); }
```

## Accessibility Requirements

### Contrast Ratios

Ensure color combinations meet WCAG AA standards:

| Combination | Minimum Ratio |
|-------------|---------------|
| Text on Surface | 4.5:1 |
| Large Text on Surface | 3:1 |
| UI Components | 3:1 |

### Testing Tools

- Browser DevTools contrast checker
- WebAIM Contrast Checker
- Lighthouse accessibility audit

## Creating Custom Schemes

Editors can create custom schemes:

1. Go to **Snippets → Color Schemes**
2. Click "Add Color Scheme"
3. Use color pickers to select colors
4. Test contrast ratios
5. Preview on site
6. Adjust as needed

## Theme + Color Scheme Relationship

| Provides | Defined In |
|----------|-----------|
| Layout, components, fonts | Theme CSS files |
| Colors only | Color Scheme (admin) |

This separation allows:
- Same theme with different colors for different seasons/events
- A/B testing color schemes
- Quick color updates without CSS changes

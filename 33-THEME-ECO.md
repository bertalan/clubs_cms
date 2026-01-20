# Theme: Terra (Eco-Friendly)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Earth-conscious, sustainable, minimal |
| Framework | Pure CSS (no framework) |
| Fonts | System fonts only (zero downloads) |
| Bundle Target | <15KB CSS total |

## Sustainability Principles

| Practice | Benefit |
|----------|---------|
| System fonts | No font file downloads |
| No shadows | Reduced GPU rendering |
| Dark mode default | OLED energy savings |
| Lazy loading | Reduced bandwidth |
| Minimal images | Lower carbon footprint |
| Single CSS file | Fewer HTTP requests |

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary (Earth) | `#2D3B2D` (forest) | Headings, navbar |
| Secondary (Leaf) | `#4A7C59` (green) | Links, CTAs |
| Accent (Sun) | `#F2C94C` (yellow) | Highlights |
| Surface (Sand) | `#E8DFD0` (beige) | Background |
| Surface Alt (Bark) | `#6B4423` (brown) | Cards in dark mode |
| Text Primary | `#1a1a1a` | Body text |
| Text Muted | `#555555` | Secondary text |

## Component Characteristics

### Navbar
- Simple, text-based
- No background image
- Minimal items (3-4 max)
- No dropdowns

### Hero Sections
- Text-only by default
- No background images
- Large typography emphasis
- Single CTA preferred

### Cards
- 2px solid border (no shadow)
- Minimal padding
- No decorative images
- Text-focused content

### Buttons
- Solid color, high contrast
- No gradients
- Simple hover state (color swap)
- Clear, readable text

### Grid Layouts
- CSS Grid with `auto-fit`
- Minimal gaps
- Single column on mobile

## Typography

| Element | Style |
|---------|-------|
| H1 | System sans, 2.5-3rem, weight 700 |
| H2 | System sans, 1.75rem, weight 600 |
| H3 | System sans, 1.25rem, weight 600 |
| Body | System sans, 1rem, weight 400 |

System font stack: `system-ui, -apple-system, BlinkMacSystemFont, sans-serif`

## Dark Mode (Default)

Inverts light/dark colors for OLED energy savings:
- Background becomes dark
- Text becomes light
- Accent colors stay vibrant

## Static Files

```
static/css/themes/terra/
└── main.css          → Single file, all styles
```

## Image Guidelines

| Rule | Implementation |
|------|----------------|
| Max size | 100KB per image |
| Format | WebP preferred |
| Lazy loading | Always enabled |
| Decorative images | Avoid |

## Carbon Target

- Goal: <0.5g CO₂ per page view
- Validate: websitecarbon.com
- Monitor: regular audits

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Terra" from Theme dropdown
2. Configure earth-tone colors
3. Keep logo simple (SVG preferred)
4. Enable dark mode default

## Use Cases

- Environmental organizations
- Sustainable brands
- Eco-tourism
- Green initiatives
- Nature-focused clubs

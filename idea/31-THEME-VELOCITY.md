# Theme: Velocity (Modern)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Dynamic, tech-forward, startup feel |
| Framework | Tailwind CSS (pre-compiled) |
| Fonts | Inter (headings), Open Sans (body) |
| Bundle Target | <50KB CSS |

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary | `#0F172A` (dark navy) | Navbar, headings |
| Secondary | `#F59E0B` (amber) | CTAs, highlights |
| Accent | `#8B5CF6` (purple) | Links, hover states |
| Surface | `#F8FAFC` (light gray) | Page background |
| Surface Alt | `#FFFFFF` | Cards, sections |
| Text Primary | `#111111` | Body text |
| Text Muted | `#666666` | Secondary text |

## Component Characteristics

### Navbar
- Fixed position with backdrop blur
- Logo on left, navigation center/right
- Prominent CTA button (pill shape)
- Mobile: hamburger menu

### Hero Sections
- Full-screen or 80vh height
- Background image with gradient overlay
- Large heading (font-weight 900)
- Two CTA buttons (primary + outline)
- Badge element for emphasis

### Cards
- Large rounded corners (16-24px)
- Subtle shadow, stronger on hover
- Scale transform on hover
- Image at top, content below

### Buttons
- Pill shape (fully rounded)
- Icon + text combination
- Scale effect on hover
- Primary: filled, Secondary: outline

### Grid Layouts
- 1 column mobile, 2 tablet, 3 desktop
- Generous gap spacing (2rem)
- Auto-fit for galleries

## Typography

| Element | Style |
|---------|-------|
| H1 | 3-5rem, weight 900, tight line-height |
| H2 | 2-2.5rem, weight 800 |
| H3 | 1.25-1.5rem, weight 700 |
| Body | 1rem, weight 400, line-height 1.6 |
| Small | 0.875rem, muted color |

## Dark Mode

Optional dark mode toggle:
- Swap surface colors
- Adjust text contrast
- Toggle via CSS class on `<html>`

## Static Files

```
static/css/themes/velocity/
├── main.css          → Core styles + Tailwind
├── components.css    → Block-specific styles
└── utilities.css     → Helper classes
```

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Velocity" from Theme dropdown
2. Configure colors in Color Scheme section
3. Upload custom logo if needed
4. Save and preview

## Accessibility

- Minimum contrast ratio 4.5:1
- Focus states visible
- Skip to content link
- Semantic HTML structure

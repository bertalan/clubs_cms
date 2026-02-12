# Theme System Architecture

## Available Themes

| Theme | Style | Framework | Bundle |
|-------|-------|-----------|--------|
| Velocity | Modern, dynamic | Tailwind | <50KB |
| Heritage | Classic, elegant | Bootstrap 5 | <80KB |
| Terra | Eco-friendly | Pure CSS | <15KB |
| Zen | Minimalist | Pure CSS | <10KB |
| Clubs | Premium Italian | Tailwind | <60KB |
| Tricolore | Italian flag-inspired | Pure CSS | <30KB |

## Theme Selection in Admin

Themes are selected via **Settings → Site Settings → Theme Configuration**:

1. **Theme Dropdown**: Select from available themes
2. **Color Scheme**: Choose predefined scheme or create custom
3. **Logo Upload**: Site logo (SVG recommended)
4. **Favicon**: Site icon

## Site Settings Structure

The Site Settings panel organizes theme configuration:

| Section | Fields |
|---------|--------|
| General | Site name, tagline |
| Theme | Theme selection dropdown |
| Colors | Primary, secondary, accent, surface, text colors |
| Typography | Font family selection (if applicable) |
| Logo & Icons | Logo upload, favicon |
| Social | Social media links |

## Template Resolution

Templates are organized by theme:

```
templates/
├── base.html                    → Loads theme-specific includes
├── themes/
│   ├── velocity/
│   │   ├── base.html
│   │   └── includes/
│   ├── heritage/
│   ├── terra/
│   ├── zen/
│   ├── clubs/
│   └── tricolore/
└── website/
    └── blocks/                  → Shared block templates
```

## CSS Variable System

All themes use CSS variables for colors, injected from Site Settings:

```css
:root {
  --primary: [from settings];
  --secondary: [from settings];
  --accent: [from settings];
  --surface: [from settings];
  --surface-alt: [from settings];
  --text: [from settings];
  --text-muted: [from settings];
}
```

## Theme-Specific CSS

Each theme has its own CSS file:

```
static/css/themes/
├── velocity/main.css
├── heritage/main.css
├── terra/main.css
├── zen/main.css
├── clubs/main.css
└── tricolore/main.css
```

## Color Schemes (Predefined)

Create predefined color schemes via fixtures or admin:

| Scheme | Primary | Secondary | Best For |
|--------|---------|-----------|----------|
| Velocity Default | #0F172A | #F59E0B | Tech clubs |
| Heritage Gold | #1E3A5F | #D4AF37 | Traditional |
| Terra Earth | #2D3B2D | #4A7C59 | Eco sites |
| Zen Minimal | #111111 | #0066FF | Content sites |
| Clubs Italian | #0A0A0A | #C41E3A | Moto clubs |
| Tricolore | #009246 | #CE2B37 | Italian orgs |

## Feature Support Matrix

| Feature | Velocity | Heritage | Terra | Zen | Clubs | Tricolore |
|---------|----------|----------|-------|-----|-------|-----------|
| Dark Mode | ✓ | – | ✓ | – | ✓ | – |
| Animations | ✓ | ✓ | – | – | ✓ | ✓ |
| Hero Images | ✓ | ✓ | Optional | – | ✓ | ✓ |
| Carousels | ✓ | ✓ | – | – | ✓ | ✓ |
| Video Backgrounds | ✓ | – | – | – | ✓ | – |

## Switching Themes

To change theme:
1. Go to **Settings → Site Settings**
2. Select new theme from dropdown
3. Optionally adjust colors for new theme
4. Save changes
5. Clear cache if needed

## Creating Custom Themes

For new themes:
1. Create CSS file in `static/css/themes/{theme}/main.css`
2. Add theme choice to Site Settings model
3. Create template folder `templates/themes/{theme}/`
4. Define component styles using CSS variables
5. Test all page types

## Performance Considerations

| Theme | Recommendations |
|-------|----------------|
| Velocity | Enable Tailwind purge |
| Heritage | Use Bootstrap CSS only (no JS) |
| Terra | Single CSS file only |
| Zen | Minimal styles, no extras |
| Clubs | Precompile Tailwind |
| Tricolore | Keep CSS minimal |

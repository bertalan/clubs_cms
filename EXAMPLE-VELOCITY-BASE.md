# Velocity Theme - Base Template

## Overview

Base template for the Velocity theme. Modern, tech-forward design with smooth animations.

---

## Template Structure

```
templates/themes/velocity/
├── base.html              ← Main base template
├── includes/
│   ├── navbar.html
│   ├── footer.html
│   ├── head.html
│   └── scripts.html
└── blocks/
    ├── hero_slider.html
    ├── cards_grid.html
    └── ...
```

---

## Base Template Components

### Head Section

| Element | Description |
|---------|-------------|
| Charset | UTF-8 |
| Viewport | Responsive meta |
| Title | Page title + site name |
| Fonts | Self-hosted Inter (Fontsource) |
| Icons | FontAwesome (self-hosted) |
| Theme CSS | Velocity styles |
| CSS Variables | Dynamic from ColorScheme |

### CSS Variables

| Variable | Source |
|----------|--------|
| `--color-primary` | ColorScheme.primary |
| `--color-secondary` | ColorScheme.secondary |
| `--color-accent` | ColorScheme.accent |

### Body Structure

| Section | Content |
|---------|---------|
| Navbar | Fixed top navigation |
| Main | Page content block |
| Footer | Site footer |
| Scripts | JS at end of body |

### JavaScript

| Library | Purpose |
|---------|---------|
| AOS | Animate On Scroll |
| Alpine.js | Interactive components (optional) |

---

## Theme Characteristics

| Aspect | Velocity Style |
|--------|----------------|
| Typography | Inter font, clean sans-serif |
| Colors | Dark primary, bright secondary |
| Animations | Smooth fade-up on scroll |
| Layout | Full-width sections |
| Buttons | Rounded (pill) style |

---

## Navbar Style

| Element | Style |
|---------|-------|
| Position | Fixed top |
| Background | Transparent → solid on scroll |
| Logo | Left aligned |
| Menu | Center or right |
| CTA Button | Accent color, rounded |

## Footer Style

| Element | Style |
|---------|-------|
| Background | Primary color |
| Text | White/light |
| Layout | Multi-column grid |
| Social | Icon links |

---

## References

- [EXAMPLE-VELOCITY-PARTS.md](EXAMPLE-VELOCITY-PARTS.md) - Navbar and Footer details
- [30-TEMPLATE-SYSTEM.md](30-TEMPLATE-SYSTEM.md) - Theme system overview
- [31-THEME-VELOCITY.md](31-THEME-VELOCITY.md) - Velocity theme spec

# Velocity Theme - Components

## Overview

Key components for the Velocity theme: navbar, footer, and hero section.

---

## Navbar

### Structure

| Element | Description |
|---------|-------------|
| Container | Fixed top, max-width with padding |
| Logo | Left side, from Site Settings |
| Menu Items | Center or right, from Navbar snippet |
| CTA Button | Right side, styled button |
| Mobile Toggle | Hamburger icon (mobile only) |

### Scroll Behavior

| State | Style |
|-------|-------|
| Top of page | Transparent background |
| After scroll | Solid background with shadow |

### Logo Display

| Source | Fallback |
|--------|----------|
| Site Settings logo image | Site name as text |

### Menu Items

| Source | Display |
|--------|---------|
| Navbar snippet items | Link with title |
| Active state | Highlighted current page |

### CTA Button

| Property | Value |
|----------|-------|
| Background | Secondary color |
| Text | Primary color |
| Shape | Rounded (pill) |
| Link | Configurable (e.g., Contact) |

---

## Footer

### Structure

| Section | Content |
|---------|---------|
| Background | Primary color |
| Container | Max-width, multi-column grid |
| Column 1-2 | Site name + description |
| Column 3 | Menu links |
| Column 4 | Contact info + social |
| Bottom | Copyright |

### Contact Info

| Element | Source |
|---------|--------|
| Email | Footer snippet |
| Phone | Footer snippet |
| Address | Footer snippet (optional) |

### Social Icons

| Platform | Icon |
|----------|------|
| Facebook | FontAwesome fab fa-facebook |
| Instagram | FontAwesome fab fa-instagram |
| YouTube | FontAwesome fab fa-youtube |

### Copyright

| Element | Content |
|---------|---------|
| Year | Current year (dynamic) |
| Name | Site name |

---

## Hero Section

### Full-Screen Hero

| Element | Description |
|---------|-------------|
| Height | 100vh (full viewport) |
| Background | Image with overlay |
| Content | Centered text |
| Overlay | Primary color at 80% opacity |

### Hero Content

| Element | Style |
|---------|-------|
| Title | Large (5xl-7xl), bold, white |
| Subtitle | Medium, white at 80% opacity |
| CTA Button | Secondary color, rounded |

### Animation

| Element | Effect |
|---------|--------|
| Title | Fade up on load |
| Subtitle | Fade up (delayed) |
| Button | Fade up (more delayed) |

---

## Responsive Behavior

### Navbar

| Breakpoint | Behavior |
|------------|----------|
| Desktop (lg+) | Full menu visible |
| Mobile/Tablet | Hamburger menu |

### Footer

| Breakpoint | Layout |
|------------|--------|
| Desktop | 4 columns |
| Tablet | 2 columns |
| Mobile | 1 column stacked |

### Hero

| Breakpoint | Title Size |
|------------|------------|
| Desktop | 7xl |
| Tablet | 6xl |
| Mobile | 5xl |

---

## Color Usage

### Primary Color

| Element | Usage |
|---------|-------|
| Navbar background (scrolled) | Yes |
| Footer background | Yes |
| Hero overlay | 80% opacity |
| Text (on light) | Yes |

### Secondary Color

| Element | Usage |
|---------|-------|
| CTA buttons | Background |
| Accents | Borders, highlights |
| Hover states | Background change |

---

## References

- [EXAMPLE-VELOCITY-BASE.md](EXAMPLE-VELOCITY-BASE.md) - Base template
- [42-SNIPPETS.md](42-SNIPPETS.md) - Navbar and Footer snippets
- [21-HERO-BLOCKS.md](21-HERO-BLOCKS.md) - Hero block options

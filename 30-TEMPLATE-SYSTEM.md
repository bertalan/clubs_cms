# Template System

## Overview

The template system uses native Wagtail/Django features without custom code. Themes and colors are managed entirely from the Wagtail admin panel.

## Architecture Principles

| Principle | Implementation |
|-----------|----------------|
| No custom Python code | Use native Wagtail features only |
| Colors via admin | All colors defined in Site Settings |
| Theme selection | Dropdown in Site Settings |
| Template inheritance | Standard Django template extends |
| Components | Wagtail StreamField blocks |

## Base Template Structure

The base template:
- Loads theme CSS from static files based on Site Settings theme selection
- Injects CSS variables from Site Settings color configuration
- Includes navbar and footer via template includes
- Provides content blocks for page templates

## Template Hierarchy

```
templates/
├── base.html                    → Main layout, loads theme
├── includes/
│   ├── navbar.html             → Site navigation
│   ├── footer.html             → Site footer
│   └── head.html               → Meta tags, CSS loading
└── website/
    ├── pages/
    │   ├── home_page.html      → Homepage template
    │   ├── content_page.html   → Generic content
    │   ├── news_page.html      → News listing
    │   └── contact_page.html   → Contact form
    └── blocks/
        ├── hero_block.html     → Hero sections
        ├── card_block.html     → Card components
        └── cta_block.html      → Call to action
```

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| `BaseSiteSetting` | Store theme and color configuration |
| `StreamField` | Flexible page content |
| `FieldPanel` | Admin UI for settings |
| `SnippetChooserPanel` | Select color schemes |
| Template tags | `{% include_block %}`, `{% pageurl %}`, `{% image %}` |

## Theme Loading

Themes are loaded based on the `theme` field in Site Settings:
1. Admin selects theme from dropdown (velocity, heritage, terra, zen, clubs, tricolore)
2. Base template loads corresponding CSS file from `static/css/themes/{theme}/`
3. CSS variables are injected from color settings

## Color Injection

Colors are defined in Site Settings and output as CSS variables:
- Primary, secondary, accent colors
- Surface and background colors
- Text colors (primary, muted)

The template outputs these as inline `<style>` with `:root` CSS variables.

## Responsive Considerations

- Mobile-first approach
- Breakpoints defined in theme CSS
- Navigation collapses on mobile
- Images use `loading="lazy"`

## Performance

- Single CSS file per theme
- Minimal JavaScript
- Lazy loading for images
- Font subset loading

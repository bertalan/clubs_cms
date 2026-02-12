# Theme: Zen (Minimalist)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Focused, content-first, calm |
| Framework | Pure CSS (no framework) |
| Fonts | Inter only (2 weights) |
| Bundle Target | <10KB CSS total |

## Design Philosophy

| Rule | Rationale |
|------|-----------|
| Max 3 nav items | Reduce decision fatigue |
| 1 CTA per section | Clear action hierarchy |
| Max 720px content | Optimal reading line length |
| No carousels | Users don't engage with them |
| No decorative images | Every image must inform |
| Text links > Buttons | Minimal visual noise |

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary (Ink) | `#111111` | Text, headings |
| Secondary (Accent) | `#0066FF` (blue) | Links only |
| Surface (Paper) | `#FFFFFF` | Background |
| Surface Alt (Mist) | `#F5F5F5` | Subtle sections |
| Text Primary | `#111111` | Body text |
| Text Muted | `#666666` | Secondary text |

## Component Characteristics

### Navbar
- Text only, no icons
- 3 items maximum
- No background color
- Subtle underline on hover

### Hero Sections
- Text-only always
- Massive typography
- No background images
- Single understated CTA

### Cards
- No borders
- Spacing-defined separation
- Minimal text
- No images unless essential

### Buttons
- Underlined text links preferred
- No boxes unless primary action
- No icons
- Subtle color change on hover

### Grid Layouts
- 2 columns maximum
- Asymmetric option (2fr 1fr)
- Generous whitespace

## Typography Scale

| Element | Size | Notes |
|---------|------|-------|
| H1 | `clamp(2.5rem, 8vw, 5rem)` | Hero only |
| H2 | 1.5rem | Section headings |
| Body | 1rem | Main content |
| Small | 0.85rem | Metadata |

## Anti-Patterns (Never Use)

- ❌ Parallax effects
- ❌ Animations
- ❌ Decorative icons
- ❌ Multiple button styles
- ❌ Sidebar content
- ❌ Auto-playing media
- ❌ Pop-ups or modals
- ❌ More than 2 colors

## Footer

- Single line layout
- Essential links only
- Copyright text
- No social icons unless necessary

## Static Files

```
static/css/themes/zen/
└── main.css          → Single file, minimal styles
```

## Content Guidelines

| Element | Recommendation |
|---------|----------------|
| Paragraphs | Short, focused |
| Lists | Bulleted, not numbered |
| Images | Only if they add information |
| Videos | Avoid unless core content |

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Zen" from Theme dropdown
2. Use only black/white + one accent color
3. Simple text logo or none
4. Review content for minimalism

## Use Cases

- Personal portfolios
- Writers/authors
- Meditation/wellness
- Photography (image-focused)
- Documentation sites

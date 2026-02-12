# Theme: Clubs (Premium Italian)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Premium, Italian motorcycle brand inspired |
| Framework | Tailwind CSS (pre-compiled) |
| Fonts | System fonts (weight 900 for headings) |
| Bundle Target | <60KB CSS |

## Design Philosophy

Inspired by Italian luxury brands and motorcycle culture:
- Dark, immersive backgrounds
- Bold typography
- Red accent color (Italian red)
- Full-width sections
- Smooth transitions

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary (Black) | `#0A0A0A` | Main background |
| Secondary (Dark) | `#1A1A1A` | Navbar, cards |
| Accent (Red) | `#C41E3A` | CTAs, highlights |
| Accent Hover | `#E02547` | Hover states |
| Surface | `#0A0A0A` | Page background |
| Text Primary | `#FFFFFF` | Body text |
| Text Muted | `#A0A0A0` | Secondary text (7:1 contrast) |

## Component Characteristics

### Navbar
- Fixed top, black background with blur
- White logo on left
- Uppercase menu items, letter-spacing
- Animated underline on hover
- Red CTA button on right

### Hero Sections
- Full viewport height (100vh)
- Background image/video with gradient overlay
- Centered content
- Font-weight 900 heading (uppercase)
- Subtitle with reduced opacity
- Two CTA buttons (primary red + outline white)

### Content Sections
- Alternating black/dark gray backgrounds
- Generous padding (6rem vertical)
- Uppercase section titles
- Decorative line under headings
- Cards with hover effect (scale + shadow)

### Cards
- Dark background (#1A1A1A)
- White border on hover
- Scale transform on hover
- Red accent elements

### Buttons
- Primary: Red background, white text
- Secondary: White outline, white text
- Uppercase, letter-spacing
- Scale on hover

### Footer
- Black background
- Large centered logo
- Links in columns
- Prominent social icons
- Red accent on hover

## Typography

| Element | Style |
|---------|-------|
| H1 | 3-5rem, weight 900, uppercase, tight tracking |
| H2 | 2-2.5rem, weight 800, uppercase |
| H3 | 1.25-1.5rem, weight 700 |
| Body | 1rem, weight 400, line-height 1.7 |
| CTA | Bold, uppercase, wide letter-spacing |

## Distinctive Features

### History/Timeline Sections
- Vertical timeline layout
- Prominent dates in red
- Alternating left/right content

### Gallery
- Grid with hover zoom
- Info overlay on hover
- Red accent borders

### News/Events
- Horizontal card layout
- Highlighted dates in red
- Scale on hover

### Services/Features
- 3-column grid
- Icons or numbers in red
- Clean descriptions

### CTA Sections
- Red background
- White text
- Immersive full-width effect

## Anti-Patterns (Avoid)

- ❌ Pastel colors
- ❌ Serif fonts
- ❌ Excessive rounded corners (max 4px)
- ❌ Childish or casual elements
- ❌ Light/white backgrounds
- ❌ Too much whitespace

## Static Files

```
static/css/themes/clubs/
├── main.css          → Core styles + Tailwind
├── components.css    → Block-specific styles
└── animations.css    → Hover effects, transitions
```

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Clubs" from Theme dropdown
2. Configure dark color palette
3. Upload bold/strong logo
4. Save and preview

## Use Cases

- Motorcycle clubs
- Automotive associations
- Premium car clubs
- Racing teams
- Luxury communities
- Italian-themed organizations

## Accessibility

- Ensure 7:1 contrast for muted text on dark backgrounds
- Red (#C41E3A) passes contrast on black
- Focus states with visible outlines
- Alt text for all hero images

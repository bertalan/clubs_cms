# Theme: Tricolore (Italian Pride)

## Profile

| Attribute | Value |
|-----------|-------|
| Style | Italian flag-inspired, patriotic, vibrant |
| Framework | Pure CSS (no framework) |
| Fonts | Montserrat (all weights) |
| Bundle Target | <30KB CSS |

## Design Philosophy

Celebrates Italian heritage and national pride:
- Green, white, and red color scheme (Italian flag)
- Gold accents for elegance
- Tricolore ribbon elements throughout
- Light, elegant backgrounds
- Balanced use of all three flag colors

## Color Palette

Configure these colors in **Settings → Site Settings → Theme Configuration**:

| Variable | Default Value | Usage |
|----------|---------------|-------|
| Primary (Verde) | `#009246` (green) | Headers, CTAs, links |
| Secondary (Rosso) | `#CE2B37` (red) | Accents, hover states |
| Accent (Oro) | `#C9A227` (gold) | Highlights, badges |
| Surface (Bianco) | `#F4F5F0` (off-white) | Page background |
| Surface Alt | `#FFFFFF` | Cards, sections |
| Text Primary (Ink) | `#1a1a1a` | Body text |
| Text Muted (Gray) | `#666666` | Secondary text |

## Distinctive Elements

### Tricolore Ribbon
A signature element appearing throughout the theme:
- 6px height bar at top of page
- Three equal sections: green, white, red
- Also used as decorative borders on cards
- Appears in footer

### Logo Badge
Circular badge with tricolore gradient:
- Circular shape with border
- Vertical stripes: green, white, red
- Used alongside text logo

### Cockade Decoration
Circular tricolore element for special features:
- Conic gradient with three colors
- Used on featured gallery items
- Positioned in corners

## Component Characteristics

### Navbar
- White background with subtle shadow
- Sticky position
- Logo with tricolore badge on left
- Navigation links turn red on hover
- Clean, elegant appearance

### Hero Sections
- Green gradient background
- Red gradient overlay on right side
- White text with strong typography
- Badge element with gold dot
- Two CTA buttons (white + outline)

### Stats Section
- White background
- Cards with tricolore top border (gradient)
- Alternating green/red numbers
- Centered text
- Grid layout (4 columns)

### Cards
- White background with rounded corners
- Box shadow, stronger on hover
- Transform on hover (translateY)
- Tricolore accents (tags, borders)
- Image areas with gradient backgrounds

### Buttons
- Primary: White background, green text
- On hover: Gold background, white text
- Secondary: Outline style
- Subtle border-radius (4px)
- Scale/shadow on hover

### CTA Sections
- Red background
- White text
- Decorative circles (semi-transparent)
- Prominent button

### Footer
- Dark ink background (#1a1a1a)
- White/gold text and links
- Tricolore decorative element
- Multi-column layout
- Gold hover color on links

## Typography

| Element | Style |
|---------|-------|
| H1 | Montserrat, clamp(2.5rem, 5vw, 3.5rem), weight 900 |
| H2 | Montserrat, 2-2.2rem, weight 900 |
| H3 | Montserrat, 1.2-1.5rem, weight 800 |
| Body | Montserrat, 1rem, weight 400, line-height 1.6 |
| Small | 0.85-0.9rem, uppercase, letter-spacing |

## Color Usage Pattern

Alternate colors to maintain visual balance:

| Section | Primary Color | Accent |
|---------|--------------|--------|
| Hero | Verde (green) | Red overlay |
| Stats | Alternating green/red | Tricolore border |
| Cards | Verde tags | Red on hover |
| CTA | Rosso (red) | White/gold |
| Footer | Dark (ink) | Gold links |

## Grid Layouts

- Stats: 4 columns (2 on mobile)
- Cards: 3 columns (1 on mobile)
- Footer: 4 columns (2 on mobile)
- Generous gap spacing (2rem)

## Special Features

### Route/Itinerary Cards
- Gradient image backgrounds
- Ribbon badge (positioned with rotation)
- Tag with region/category
- Meta information with icons

### Gallery Grid
- Masonry-style layout
- Tricolore border at bottom of items
- Hover overlay with info
- Cockade decoration on featured items

### Timeline Elements
- Vertical layout for history
- Color-coded dates
- Alternating content positioning

## Static Files

```
static/css/themes/tricolore/
├── main.css          → Core styles
├── components.css    → Block-specific styles
└── utilities.css     → Helper classes
```

## Wagtail Admin Configuration

In **Settings → Site Settings**:
1. Select "Tricolore" from Theme dropdown
2. Configure Italian flag colors (or use defaults)
3. Upload logo with tricolore element
4. Save and preview

## Use Cases

- Italian cultural organizations
- Italian motorcycle/car clubs
- Tourism (Italian routes/destinations)
- Italian heritage associations
- Regional Italian clubs abroad
- Sports teams with Italian theme

## Accessibility

- Verde (#009246) passes contrast on white
- Rosso (#CE2B37) passes contrast on white
- Text maintains 4.5:1 ratio
- Clear focus states
- Semantic heading structure

## Anti-Patterns (Avoid)

- ❌ Using only one flag color
- ❌ Dark backgrounds (except footer)
- ❌ Heavy shadows
- ❌ Sans-serif fonts other than Montserrat
- ❌ Ignoring the tricolore balance

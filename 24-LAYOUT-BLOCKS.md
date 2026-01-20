# Layout Blocks

## Overview

Layout blocks control page structure and organize content into columns, grids, and interactive sections.

---

## GridBlock

Flexible grid layout for mixed content.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Items | Repeater | Yes | Grid items |
| Columns | Dropdown | No | 2, 3, 4 columns |
| Gap | Dropdown | No | Small, Medium, Large |
| Equal Height | Boolean | No | Force equal item heights |

### Grid Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Content | StreamBlock | Yes | Nested content blocks |
| Column Span | Dropdown | No | 1 or 2 columns |
| Background | Dropdown | No | None, Light, Dark |

### Gap Sizes

| Option | Spacing |
|--------|---------|
| Small | 8px / 0.5rem |
| Medium | 16px / 1rem |
| Large | 24px / 1.5rem |

---

## TwoColumnBlock

Simple two-column layout.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Left Column | StreamBlock | Yes | Left content |
| Right Column | StreamBlock | Yes | Right content |
| Ratio | Dropdown | No | 50/50, 60/40, 40/60, 70/30 |
| Vertical Align | Dropdown | No | Top, Center, Bottom |
| Reverse on Mobile | Boolean | No | Swap order on small screens |

### Column Ratios

| Option | Left | Right |
|--------|------|-------|
| 50/50 | 50% | 50% |
| 60/40 | 60% | 40% |
| 40/60 | 40% | 60% |
| 70/30 | 70% | 30% |
| 30/70 | 30% | 70% |

---

## ThreeColumnBlock

Three-column layout.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Left Column | StreamBlock | Yes | Left content |
| Center Column | StreamBlock | Yes | Center content |
| Right Column | StreamBlock | Yes | Right content |
| Equal Width | Boolean | No | Force equal widths |

---

## AccordionBlock

Expandable/collapsible sections.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Items | Repeater | Yes | Accordion panels |
| Allow Multiple | Boolean | No | Multiple open at once |
| First Open | Boolean | No | First item expanded |
| Style | Dropdown | No | Default, Bordered, Separated |

### Accordion Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | Yes | Panel header |
| Content | RichText | Yes | Panel content |
| Icon | Icon Chooser | No | Custom icon |

### Behavior

| Option | Description |
|--------|-------------|
| Single | Only one panel open |
| Multiple | Any panels can be open |
| All Closed | Start with all closed |
| First Open | First panel expanded |

---

## TabsBlock

Tabbed content sections.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Tabs | Repeater | Yes | Tab panels |
| Style | Dropdown | No | Default, Boxed, Pills |
| Position | Dropdown | No | Top, Left |

### Tab Item Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | Yes | Tab label |
| Icon | Icon Chooser | No | Tab icon |
| Content | StreamBlock | Yes | Tab content |

### Tab Styles

| Style | Description |
|-------|-------------|
| Default | Underlined active tab |
| Boxed | Bordered tab panels |
| Pills | Rounded tab buttons |

### Mobile Behavior

On mobile screens, tabs convert to accordion for better usability.

---

## ContainerBlock

Wrapper with width constraints.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Content | StreamBlock | Yes | Inner content |
| Width | Dropdown | No | Narrow, Default, Wide, Full |
| Background | Dropdown | No | None, Light, Dark, Primary |
| Padding | Dropdown | No | None, Small, Medium, Large |

### Width Options

| Option | Max Width |
|--------|-----------|
| Narrow | 720px |
| Default | 1140px |
| Wide | 1400px |
| Full | 100% |

---

## SectionBlock

Full-width section with background.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Content | StreamBlock | Yes | Section content |
| Background Color | Color/Dropdown | No | Background style |
| Background Image | Image Chooser | No | Background image |
| Overlay | Dropdown | No | None, Light, Dark |
| Padding | Dropdown | No | Small, Medium, Large, XL |
| ID | Text | No | Anchor link target |

---

## DividerBlock

Visual separator between sections.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Style | Dropdown | No | Line, Dots, Icon, Space |
| Width | Dropdown | No | Short, Medium, Full |
| Spacing | Dropdown | No | Small, Medium, Large |
| Color | Dropdown | No | Default, Light, Dark, Primary |

### Divider Styles

| Style | Description |
|-------|-------------|
| Line | Simple horizontal line |
| Dots | Three centered dots |
| Icon | Custom icon centered |
| Space | Invisible spacing only |

---

## SpacerBlock

Vertical spacing adjustment.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Height | Dropdown | Yes | XS, S, M, L, XL |

### Height Values

| Option | Desktop | Mobile |
|--------|---------|--------|
| XS | 16px | 8px |
| S | 32px | 16px |
| M | 48px | 24px |
| L | 64px | 32px |
| XL | 96px | 48px |

---

## Responsive Behavior

| Block | Mobile Adaptation |
|-------|-------------------|
| Grid | Stacks to single column |
| TwoColumn | Stacks vertically |
| ThreeColumn | Stacks vertically |
| Tabs | Converts to accordion |
| Accordion | Full width panels |

---

## Nesting

Layout blocks support nesting:

| Parent | Can Contain |
|--------|-------------|
| Grid | Any content block |
| Columns | Any content block |
| Container | Any block including layout |
| Section | Any block including layout |
| Accordion | Content blocks only |
| Tabs | Content blocks only |

---

## Accessibility

| Feature | Implementation |
|---------|----------------|
| Accordion | ARIA expanded states |
| Tabs | ARIA tab roles |
| Focus | Visible focus indicators |
| Keyboard | Tab, Enter, Arrow keys |
| Screen readers | Proper announcements |

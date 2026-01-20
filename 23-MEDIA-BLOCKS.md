# Media Blocks

## Overview

Media blocks display images, videos, documents, and interactive maps.

---

## GalleryBlock

Image gallery from Wagtail Collection.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Collection | Collection Chooser | Yes | Source image collection |
| Columns | Dropdown | No | 2, 3, or 4 columns |
| Max Images | Number | No | Limit displayed (default: 12) |
| Show Lightbox | Boolean | No | Enable fullscreen view |
| Show Captions | Boolean | No | Display image titles |
| Aspect Ratio | Dropdown | No | Square, 4:3, 16:9, Original |

### Lightbox Features

| Feature | Description |
|---------|-------------|
| Navigation | Previous/Next arrows |
| Keyboard | Arrow keys, Escape |
| Swipe | Touch gestures on mobile |
| Caption | Image title and alt text |
| Counter | "3 of 12" indicator |
| Zoom | Optional pinch zoom |

### Display Options

| Option | Description |
|--------|-------------|
| Grid | Regular grid layout |
| Masonry | Pinterest-style layout |
| Carousel | Horizontal scrolling |

---

## GalleryImageBlock

Individual image selection for inline galleries.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Image | Image Chooser | Yes | Selected image |
| Caption | Text | No | Override image title |

Used in StreamField repeaters for custom galleries not tied to Collections.

---

## ImageBlock

Single image with options.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Image | Image Chooser | Yes | Selected image |
| Caption | Text | No | Image caption |
| Alignment | Dropdown | No | Left, Center, Right |
| Size | Dropdown | No | Small, Medium, Large, Full |
| Link | URL/Page | No | Click destination |

### Size Options

| Size | Width |
|------|-------|
| Small | 33% container |
| Medium | 50% container |
| Large | 75% container |
| Full | 100% container |

---

## VideoEmbedBlock

Embedded video from YouTube, Vimeo, etc.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Video URL | Embed | Yes | Video URL |
| Caption | Text | No | Video description |
| Aspect Ratio | Dropdown | No | 16:9, 4:3, 1:1 |
| Autoplay | Boolean | No | Auto-start (muted) |

### Supported Providers

| Provider | URL Format |
|----------|------------|
| YouTube | youtube.com/watch?v=... |
| Vimeo | vimeo.com/... |
| Dailymotion | dailymotion.com/video/... |

### Privacy Considerations

| Option | Description |
|--------|-------------|
| No-cookie | Use youtube-nocookie.com |
| Thumbnail | Show preview, load on click |
| Consent | Require cookie consent first |

---

## DocumentBlock

Single document download.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Document | Document Chooser | Yes | PDF, DOC, etc. |
| Title | Text | No | Override document title |
| Description | Text | No | Brief description |
| Show Icon | Boolean | No | File type icon |
| Show Size | Boolean | No | Display file size |

---

## DocumentListBlock

Group of documents.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Title | Text | No | Section heading |
| Documents | Repeater | Yes | Document items |
| Style | Dropdown | No | List, Cards, Table |

### Display Info

| Element | Description |
|---------|-------------|
| Icon | Auto-detected from file type |
| Title | Document title |
| Size | File size in KB/MB |
| Download | Click to download |

---

## MapBlock

Interactive map display.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Address | Text | No | Location (geocoded) |
| Latitude | Decimal | No | Manual coordinates |
| Longitude | Decimal | No | Manual coordinates |
| Zoom | Number | No | 1-20 (default: 15) |
| Height | Dropdown | No | Small, Medium, Large |
| Show Marker | Boolean | No | Pin on location |
| Marker Label | Text | No | Popup text |

### Map Provider

| Component | Service |
|-----------|---------|
| Tiles | OpenStreetMap |
| Library | Leaflet.js |
| Geocoding | Nominatim |
| Directions | OSRM link |

### Height Options

| Option | Pixels |
|--------|--------|
| Small | 300px |
| Medium | 400px |
| Large | 500px |

---

## AudioBlock

Audio player for podcasts, recordings.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Audio File | Document Chooser | Yes | MP3, WAV, etc. |
| Title | Text | No | Track title |
| Show Controls | Boolean | Yes | Play/pause/seek |
| Autoplay | Boolean | No | Auto-start |

---

## EmbedBlock

Generic embed for social media, etc.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| URL | URL | Yes | Content URL |
| Caption | Text | No | Description |

### Supported Embeds

| Type | Example |
|------|---------|
| Twitter/X | Tweet embed |
| Instagram | Post embed |
| Facebook | Post embed |
| Spotify | Track/playlist |
| SoundCloud | Audio |

---

## BeforeAfterBlock

Image comparison slider.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| Before Image | Image Chooser | Yes | Left/before state |
| After Image | Image Chooser | Yes | Right/after state |
| Before Label | Text | No | "Before" text |
| After Label | Text | No | "After" text |
| Orientation | Dropdown | No | Horizontal, Vertical |

---

## Accessibility

| Block | Accessibility Features |
|-------|------------------------|
| Images | Alt text from Wagtail |
| Videos | Captions support |
| Documents | File type announced |
| Maps | Keyboard navigation |
| Audio | Controls accessible |

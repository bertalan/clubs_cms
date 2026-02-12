# Gallery System

## Overview

The gallery system uses native **Wagtail Collections** to organize images. No custom models required.

### Multilingual

Gallery content translation:
- **GalleryPage**: title, intro, body translatable
- **Images**: title and alt text translatable (not file)
- **Collections**: names are NOT translated (internal organization)

See [41-MULTILANG.md](41-MULTILANG.md) for translation workflow.

---

## Architecture

| Component | Wagtail Feature |
|-----------|-----------------|
| Image Storage | Wagtail Images |
| Organization | Wagtail Collections |
| Display | GalleryPage + GalleryBlock |
| Upload | Media Library (admin) or frontend |

## Collections

### What Are Collections?

Collections are Wagtail's native way to organize media:
- Hierarchical folder structure
- Permission-based access
- Shared across images and documents
- Managed in **Settings → Collections**

### Collection Structure Example

```
Root
├── Gallery
│   ├── Events 2024
│   │   ├── Spring Rally
│   │   └── Summer Meeting
│   ├── Events 2025
│   └── Club History
├── News
│   └── Article Images
└── Members
    └── Profile Photos
```

### Creating Collections

1. Go to **Settings → Collections**
2. Click "Add a collection"
3. Enter collection name
4. Select parent collection
5. Save

### Collection Permissions

| Permission | Description |
|------------|-------------|
| Add | Upload new images |
| Edit | Modify image details |
| Delete | Remove images |
| Choose | Select in page editors |

---

## GalleryPage

### Purpose
Main gallery hub displaying all albums (collections).

### Content Tab Fields

| Field | Type | Description |
|-------|------|-------------|
| Title | Text | e.g., "Photo Gallery" |
| Intro | Text | Introduction text |
| Body | StreamField | Optional content |

### Display Configuration

| Option | Description |
|--------|-------------|
| Root Collection | Starting collection for gallery |
| Show Empty Albums | Yes/No |
| Album Layout | Grid (3-4 columns) |
| Cover Image | First image or custom |
| Show Image Count | Yes/No |

### Album Display

Each collection/album shows:
- Cover image (first in collection)
- Album name (collection name)
- Image count
- Click to view album

### Settings

| Setting | Value |
|---------|-------|
| Max Count | 1 |
| Template | gallery_page.html |
| Schema Type | ImageGallery |

---

## GalleryBlock (StreamField)

### Purpose
Embed a gallery anywhere in page content.

### Block Fields

| Field | Type | Description |
|-------|------|-------------|
| Collection | Collection Chooser | Source album |
| Columns | Choice | 2, 3, or 4 columns |
| Max Images | Number | Limit displayed (default: 12) |
| Show Lightbox | Boolean | Enable fullscreen view |
| Show Captions | Boolean | Display image titles |

### Display Options

| Option | Values |
|--------|--------|
| Layout | Grid, Masonry |
| Aspect Ratio | Square, 4:3, 16:9, Original |
| Gap | Small, Medium, Large |
| Hover Effect | Zoom, Fade, None |

---

## Image Display

### Thumbnail Generation

Wagtail generates thumbnails automatically:

| Context | Size | Method |
|---------|------|--------|
| Album Cover | 400×300 | fill |
| Gallery Grid | 400×400 | fill (square) |
| Lightbox | 1920×1080 | max |
| Thumbnail | 150×150 | fill |

### Image Fields

Each image in Wagtail has:

| Field | Description |
|-------|-------------|
| Title | Image name/caption |
| File | Original upload |
| Collection | Assigned collection |
| Tags | Searchable tags |

### Batch Upload for Members

Members can upload multiple photos with shared metadata:
- Title prefix (auto-numbered)
- Shared description
- Shared tags (PhotoTag snippets)
- Single event/collection assignment

See [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) for batch upload details.
| Focal Point | Crop center |
| Alt Text | Accessibility text |

---

## Lightbox Viewer

When viewing full-size images:

| Feature | Description |
|---------|-------------|
| Navigation | Previous/Next arrows |
| Keyboard | Arrow keys, Escape to close |
| Caption | Image title displayed |
| Download | Optional download link |
| Share | Social share buttons |

---

## Album Detail View

Clicking an album shows:

| Element | Description |
|---------|-------------|
| Album Title | Collection name |
| Description | Collection description (if set) |
| Image Grid | All images in collection |
| Image Count | Total images |
| Back Link | Return to gallery |

---

## Member Photo Upload

Members can upload photos to designated collections:

### Upload Configuration

| Setting | Value |
|---------|-------|
| Target Collection | Member-specific or shared |
| Approval Required | Yes (moderation queue) |
| Max File Size | Configured in settings |
| Allowed Formats | JPEG, PNG, WebP |

See [81-GALLERY-UPLOAD.md](81-GALLERY-UPLOAD.md) for member uploads.

---

## Schema.org (ImageGallery)

| Property | Source |
|----------|--------|
| @type | "ImageGallery" |
| name | Page title |
| description | Intro text |
| image | Array of ImageObject |

### ImageObject Properties

| Property | Source |
|----------|--------|
| @type | "ImageObject" |
| contentUrl | Full image URL |
| thumbnailUrl | Thumbnail URL |
| name | Image title |
| description | Alt text |

---

## Native Wagtail Features Used

| Feature | Purpose |
|---------|---------|
| Wagtail Images | Image storage and processing |
| Collections | Album organization |
| Image Chooser | Admin image selection |
| Renditions | Automatic thumbnail generation |
| Focal Points | Smart cropping |

## Advantages of Collections

| Benefit | Description |
|---------|-------------|
| No Custom Models | Uses built-in Wagtail features |
| Admin Integration | Managed in Media Library |
| Permissions | Native access control |
| Reusability | Same images across pages |
| Search | Built-in image search |

"""
Audit all Wagtail pages for image field assignments.
Run on server: python manage.py shell < scripts/audit_images.py
"""
from wagtail.models import Page
from wagtail.images.models import Image

print("=== IMAGE FILES IN DB ===")
for img in Image.objects.all():
    exists = img.file.storage.exists(img.file.name)
    print(f"  [{img.pk}] {img.title} -> {img.file.name}  exists={exists}")

print("\n=== PAGES WITH IMAGE FIELDS ===")
all_pages = Page.objects.all().specific()
for p in all_pages:
    cls = p.__class__.__name__
    img_fields = [
        f.name for f in p._meta.get_fields()
        if "image" in f.name.lower()
    ]
    vals = {}
    for f in img_fields:
        val = getattr(p, f, None)
        if val is not None:
            vals[f] = str(val)

    body = getattr(p, "body", None)
    img_block_types = []
    if body and hasattr(body, "stream_data"):
        for block in body.stream_data:
            btype = block.get("type", "")
            bval = block.get("value", {})
            if "image" in btype.lower() or "hero" in btype.lower() or "gallery" in btype.lower():
                img_block_types.append(btype)
            elif isinstance(bval, dict) and "image" in bval:
                img_block_types.append(f"{btype}(img={bval['image']})")

    if vals or img_block_types:
        print(f"  [{p.pk}] {cls}: {p.title[:60]}")
        if vals:
            print(f"        fields: {vals}")
        if img_block_types:
            print(f"        blocks: {img_block_types}")
    elif img_fields:
        print(f"  [{p.pk}] {cls}: {p.title[:60]}  -> MISSING: {img_fields}")

print("\n=== MEDIA DIRECTORY ===")
import os
media_root = "/www/wwwroot/clubs.betabi.it/clubcms/clubcms/media"
for root, dirs, files in os.walk(media_root):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, media_root)
        size = os.path.getsize(full)
        print(f"  {rel}  ({size:,} bytes)")

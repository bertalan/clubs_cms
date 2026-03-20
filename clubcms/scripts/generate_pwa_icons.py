from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from PIL import Image, ImageDraw

SOURCE_URL = "https://clubs.betabi.it/media/images/logo-clubs.2e16d0ba.fill-180x180.format-png.png"
OUT_DIR = Path("/app/static/pwa")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BG = "#0F172A"
ACCENT = "#D4AF37"
HIGHLIGHT = "#1E293B"


def load_source() -> Image.Image:
    with urlopen(SOURCE_URL) as response:
        source = Image.open(BytesIO(response.read())).convert("RGBA")
    bbox = source.getbbox()
    if bbox:
        source = source.crop(bbox)
    return source


def make_icon(source: Image.Image, size: int, logo_scale: float = 0.68, add_ring: bool = True) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), BG)
    draw = ImageDraw.Draw(canvas)
    inset = int(size * 0.08)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=BG)
    if add_ring:
        draw.ellipse((inset, inset, size - inset, size - inset), fill=HIGHLIGHT)
        ring = max(2, size // 64)
        draw.ellipse((inset, inset, size - inset, size - inset), outline=ACCENT, width=ring)
    logo_size = int(size * logo_scale)
    logo = source.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.bitmap((0, 0), logo.split()[-1], fill=(0, 0, 0, 110))
    pos = ((size - logo_size) // 2, (size - logo_size) // 2)
    canvas.alpha_composite(shadow, (pos[0] + max(1, size // 128), pos[1] + max(1, size // 128)))
    canvas.alpha_composite(logo, pos)
    return canvas


def main() -> None:
    source = load_source()
    assets = {
        "icon-192.png": make_icon(source, 192, logo_scale=0.68),
        "icon-512.png": make_icon(source, 512, logo_scale=0.68),
        "apple-touch-icon.png": make_icon(source, 180, logo_scale=0.68),
        "badge-72.png": make_icon(source, 72, logo_scale=0.62, add_ring=False),
        "favicon-32.png": make_icon(source, 32, logo_scale=0.76, add_ring=False),
        "favicon-16.png": make_icon(source, 16, logo_scale=0.82, add_ring=False),
    }

    for name, image in assets.items():
        image.save(OUT_DIR / name)

    assets["icon-192.png"].save(OUT_DIR / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("generated", sorted(path.name for path in OUT_DIR.iterdir()))


if __name__ == "__main__":
    main()

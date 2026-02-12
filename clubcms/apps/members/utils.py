"""
Utility functions for the members app.

Handles card number generation, QR code creation (vCard format),
and barcode generation for membership cards.

Optional dependencies:
- qrcode: for QR code image generation
- python-barcode: for barcode image generation
"""

import os
from datetime import date

from django.conf import settings
from django.utils import timezone


def generate_card_number(user):
    """
    Generate a card number in YYYY-NNNN format.

    Uses the membership_date year (or current year if not set)
    and a zero-padded sequential number based on existing cards
    in the same year.

    Args:
        user: ClubUser instance.

    Returns:
        str: Card number in 'YYYY-NNNN' format.
    """
    from apps.members.models import ClubUser

    year = user.membership_date.year if user.membership_date else timezone.now().year
    year_str = str(year)

    # Find the highest existing card number for this year
    existing = (
        ClubUser.objects.filter(card_number__startswith=f"{year_str}-")
        .exclude(pk=user.pk)
        .values_list("card_number", flat=True)
    )

    max_seq = 0
    for cn in existing:
        try:
            seq = int(cn.split("-")[1])
            if seq > max_seq:
                max_seq = seq
        except (IndexError, ValueError):
            continue

    new_seq = max_seq + 1
    return f"{year_str}-{new_seq:04d}"


def _ensure_dir(path):
    """Create directory if it does not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def build_vcard(user):
    """
    Build a vCard 3.0 string with ONLY non-sensitive data.

    Includes: name, organisation (club name), card number, expiry date.
    Excludes: email, phone, fiscal_code, address, birth_date.

    Args:
        user: ClubUser instance.

    Returns:
        str: vCard formatted string.
    """
    club_name = getattr(settings, "WAGTAIL_SITE_NAME", "Club CMS")
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{user.get_full_name() or user.username}",
        f"N:{user.last_name};{user.first_name};;;",
        f"ORG:{club_name}",
    ]
    if user.card_number:
        lines.append(f"NOTE:Card {user.card_number}")
    if user.membership_expiry:
        exp = user.membership_expiry.strftime("%Y-%m-%d")
        lines.append(f"X-EXPIRY:{exp}")
    lines.append("END:VCARD")
    return "\n".join(lines)


def generate_qr_code(user):
    """
    Generate a QR code image from the user's vCard data.

    The QR code is saved to media/members/qr/<card_number>.png.
    Returns the relative path from MEDIA_ROOT, or None if the
    qrcode library is not installed.

    Args:
        user: ClubUser instance with card_number set.

    Returns:
        str or None: Relative media path to the QR image, or None.
    """
    try:
        import qrcode
    except ImportError:
        return None

    if not user.card_number:
        return None

    vcard = build_vcard(user)

    safe_filename = user.card_number.replace("/", "-").replace("\\", "-")
    relative_path = os.path.join("members", "qr", f"{safe_filename}.png")
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    _ensure_dir(full_path)

    img = qrcode.make(vcard, error_correction=qrcode.constants.ERROR_CORRECT_M)
    img.save(full_path)

    return relative_path


def generate_barcode(user):
    """
    Generate a Code128 barcode image from the user's card number.

    The barcode is saved to media/members/barcode/<card_number>.png.
    Returns the relative path from MEDIA_ROOT, or None if the
    python-barcode library is not installed.

    Args:
        user: ClubUser instance with card_number set.

    Returns:
        str or None: Relative media path to the barcode image, or None.
    """
    try:
        import barcode
        from barcode.writer import ImageWriter
    except ImportError:
        return None

    if not user.card_number:
        return None

    safe_filename = user.card_number.replace("/", "-").replace("\\", "-")
    relative_path = os.path.join("members", "barcode", safe_filename)
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
    _ensure_dir(full_path + ".png")  # ensure parent dir exists

    code128 = barcode.get("code128", user.card_number, writer=ImageWriter())
    # barcode library appends the extension automatically
    saved_path = code128.save(full_path)

    # Return relative path with extension
    if saved_path:
        return os.path.relpath(saved_path, settings.MEDIA_ROOT)
    return relative_path + ".png"

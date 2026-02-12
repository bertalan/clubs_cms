"""
Signals for the members app.

Post-save signal on ClubUser:
- Auto-generates card_number (YYYY-NNNN format) when membership_date
  is set and card_number is empty.
- Regenerates QR code and barcode when card_number changes.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save, sender="members.ClubUser")
def handle_clubuser_post_save(sender, instance, created, **kwargs):
    """
    Auto-generate card number and regenerate QR/barcode after save.

    This signal:
    1. Generates a card_number if membership_date is set but card_number
       is empty. Uses YYYY-NNNN format via utils.generate_card_number().
    2. Regenerates QR code and barcode images whenever the card_number
       is present (including after auto-generation).

    Uses update() to avoid triggering recursive post_save signals.
    """
    from apps.members.utils import (
        generate_barcode,
        generate_card_number,
        generate_qr_code,
    )

    update_fields = {}

    # Auto-generate card number if membership_date is set but card_number is empty
    if instance.membership_date and not instance.card_number:
        new_card_number = generate_card_number(instance)
        update_fields["card_number"] = new_card_number
        # Update instance in memory so QR/barcode generation works
        instance.card_number = new_card_number

    # Apply database update without triggering another post_save
    if update_fields:
        sender.objects.filter(pk=instance.pk).update(**update_fields)

    # Regenerate QR code and barcode if card_number exists
    if instance.card_number:
        try:
            generate_qr_code(instance)
        except Exception:
            logger.exception(
                "Failed to generate QR code for user %s", instance.pk
            )

        try:
            generate_barcode(instance)
        except Exception:
            logger.exception(
                "Failed to generate barcode for user %s", instance.pk
            )

"""
Verification models for partner member verification.

VerificationLog: audit trail for partner-initiated member card verifications.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


VERIFICATION_TYPE_CHOICES = [
    ("display_name", _("Display name")),
    ("city", _("City")),
    ("phone", _("Phone")),
]

VERIFICATION_RESULT_CHOICES = [
    ("success", _("Success")),
    ("not_found", _("Not found")),
    ("wrong_data", _("Wrong data")),
    ("expired", _("Expired membership")),
]


class VerificationLog(models.Model):
    """
    Audit trail for partner-initiated member verification.

    Records who verified, what card number was checked, what secondary
    factor was used, the result, and the IP address for security auditing.
    """

    partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_logs",
        verbose_name=_("Partner user"),
        help_text=_("The partner owner who performed this verification."),
    )
    card_number = models.CharField(
        max_length=50,
        verbose_name=_("Card number"),
    )
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPE_CHOICES,
        verbose_name=_("Verification type"),
        help_text=_("Which secondary factor was used for verification."),
    )
    result = models.CharField(
        max_length=20,
        choices=VERIFICATION_RESULT_CHOICES,
        verbose_name=_("Result"),
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP address"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("verification log")
        verbose_name_plural = _("verification logs")
        indexes = [
            models.Index(fields=["partner", "-created_at"]),
            models.Index(fields=["card_number"]),
        ]

    def __str__(self) -> str:
        return (
            f"{self.card_number} - {self.get_result_display()} "
            f"({self.created_at:%Y-%m-%d %H:%M})"
        )

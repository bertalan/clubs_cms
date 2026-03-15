"""
Anti-spam protection for public-facing forms.

Provides a honeypot field + timestamp check mixin that can be added
to any Django form.  No external service required — privacy-friendly
and effective against automated bots.

Usage
-----
::

    class MyPublicForm(AntispamMixin, forms.Form):
        ...

The mixin adds two hidden fields:

* ``website``  — a honeypot field (always empty for humans)
* ``form_ts``  — the Unix timestamp when the form was rendered

Bots that fill the honeypot or submit too quickly (< 3 s) are
rejected with a generic validation error.
"""

import time

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# Minimum seconds between form render and submit.  Humans almost
# never submit a complex registration form in under 3 seconds.
ANTISPAM_MIN_SECONDS = getattr(settings, "ANTISPAM_MIN_SECONDS", 3)


class AntispamMixin:
    """
    Mixin that adds a honeypot + timestamp check to a Django form.

    Must appear **before** the base form class in the MRO so that
    ``__init__`` and ``clean`` are wired correctly.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Honeypot — screen-reader-hidden, tab-unreachable, but bots
        # will normally fill it in.
        self.fields["website"] = forms.CharField(
            required=False,
            label="",
            widget=forms.TextInput(
                attrs={
                    "tabindex": "-1",
                    "autocomplete": "off",
                    "aria-hidden": "true",
                    "style": "position:absolute;left:-9999px;top:-9999px;",
                }
            ),
        )

        # Timestamp — the epoch-seconds when the form was rendered.
        self.fields["form_ts"] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(),
        )
        # Set initial value only when rendering a fresh (unbound) form.
        if not self.is_bound:
            self.initial["form_ts"] = str(int(time.time()))

    def clean(self):
        cleaned = super().clean()

        # 1. Honeypot check
        if cleaned.get("website"):
            raise forms.ValidationError(
                _("Form submission rejected. Please try again."),
                code="spam_honeypot",
            )

        # 2. Timing check
        form_ts = cleaned.get("form_ts", "")
        try:
            rendered_at = int(form_ts)
        except (ValueError, TypeError):
            raise forms.ValidationError(
                _("Form submission rejected. Please try again."),
                code="spam_timestamp_invalid",
            )

        elapsed = time.time() - rendered_at
        if elapsed < ANTISPAM_MIN_SECONDS:
            raise forms.ValidationError(
                _("Form submitted too quickly. Please wait a moment and try again."),
                code="spam_too_fast",
            )

        return cleaned

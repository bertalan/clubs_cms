"""
Tests for the AntispamMixin (honeypot + timestamp bot protection).
"""

import time

import pytest
from django import forms
from django.utils import translation

from apps.core.antispam import ANTISPAM_MIN_SECONDS, AntispamMixin


# ---------------------------------------------------------------------------
# Minimal test form
# ---------------------------------------------------------------------------


class _SimpleForm(AntispamMixin, forms.Form):
    name = forms.CharField(max_length=100)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAntispamMixin:
    """Verify honeypot and timing checks."""

    def _valid_ts(self, seconds_ago=10):
        """Return a form_ts value from *seconds_ago* in the past."""
        return str(int(time.time()) - seconds_ago)

    # -- Honeypot ----------------------------------------------------------

    def test_honeypot_empty_passes(self):
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "",
            "form_ts": self._valid_ts(),
        })
        assert form.is_valid(), form.errors

    def test_honeypot_filled_rejects(self):
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "http://spam.example.com",
            "form_ts": self._valid_ts(),
        })
        assert not form.is_valid()
        assert "__all__" in form.errors  # non-field error from honeypot

    # -- Timestamp ---------------------------------------------------------

    def test_valid_timestamp_passes(self):
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "",
            "form_ts": self._valid_ts(seconds_ago=30),
        })
        assert form.is_valid(), form.errors

    def test_too_fast_rejects(self):
        """Submission within ANTISPAM_MIN_SECONDS is rejected."""
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "",
            "form_ts": str(int(time.time()) + 5),  # in the future
        })
        assert not form.is_valid()
        assert "__all__" in form.errors  # non-field error from timing check

    def test_missing_timestamp_rejects(self):
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "",
            "form_ts": "",
        })
        assert not form.is_valid()
        assert "__all__" in form.errors  # non-field error from invalid ts

    def test_invalid_timestamp_rejects(self):
        form = _SimpleForm(data={
            "name": "Mario",
            "website": "",
            "form_ts": "not-a-number",
        })
        assert not form.is_valid()
        assert "__all__" in form.errors  # non-field error from invalid ts

    # -- Fresh form rendering ----------------------------------------------

    def test_unbound_form_has_initial_ts(self):
        form = _SimpleForm()
        assert "form_ts" in form.initial
        ts = int(form.initial["form_ts"])
        assert abs(ts - int(time.time())) < 5

    def test_hidden_fields_present(self):
        form = _SimpleForm()
        assert "website" in form.fields
        assert "form_ts" in form.fields
        # honeypot is visually hidden
        assert "aria-hidden" in str(form.fields["website"].widget.render("website", ""))
        # timestamp is a HiddenInput
        assert isinstance(form.fields["form_ts"].widget, forms.HiddenInput)

    # -- Integration with non-antispam fields ------------------------------

    def test_real_field_validation_still_works(self):
        """Name is still required even when antispam passes."""
        form = _SimpleForm(data={
            "name": "",
            "website": "",
            "form_ts": self._valid_ts(),
        })
        assert not form.is_valid()
        assert "name" in form.errors

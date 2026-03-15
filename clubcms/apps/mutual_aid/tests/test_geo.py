"""Tests for geo-search coordinate parsing (comma-as-decimal locale bug)."""

import pytest

from apps.mutual_aid.views import _parse_float_locale


class TestParseFloatLocale:
    """Ensure coordinates with comma decimal separators are handled."""

    def test_dot_decimal(self):
        assert _parse_float_locale("45.6395418") == pytest.approx(45.6395418)

    def test_comma_decimal(self):
        """Italian/European locale sends comma as decimal separator."""
        assert _parse_float_locale("45,6395418") == pytest.approx(45.6395418)

    def test_negative_with_comma(self):
        assert _parse_float_locale("-9,2788304") == pytest.approx(-9.2788304)

    def test_integer(self):
        assert _parse_float_locale("50") == 50.0

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            _parse_float_locale("")

    def test_none_raises(self):
        with pytest.raises((ValueError, TypeError)):
            _parse_float_locale(None)

    def test_whitespace_stripped(self):
        assert _parse_float_locale("  45.6  ") == pytest.approx(45.6)

    def test_dot_and_comma_kept_as_is(self):
        """If both dot and comma present (unlikely but defensive), don't replace."""
        # "1,234.56" → float("1,234.56") would fail, but shouldn't mangle
        with pytest.raises(ValueError):
            _parse_float_locale("1,234.56")

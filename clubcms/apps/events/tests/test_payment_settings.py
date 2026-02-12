"""
Unit tests for PaymentSettings model computed properties.

Tests test/live mode switching, available_providers, and
helper properties using the actual model with database.
"""

import pytest
from wagtail.models import Site

from apps.website.models.settings import PaymentSettings


def _get_or_create_settings(**kwargs):
    """Get or create PaymentSettings for the default site."""
    site = Site.objects.get(is_default_site=True)
    ps, _ = PaymentSettings.objects.get_or_create(site=site)
    for k, v in kwargs.items():
        setattr(ps, k, v)
    ps.save()
    return ps


@pytest.mark.django_db
class TestPaymentSettingsMode:
    """Tests for test/live mode switching."""

    def test_is_test_mode(self):
        ps = _get_or_create_settings(payment_mode="test")
        assert ps.is_test_mode is True

    def test_is_live_mode(self):
        ps = _get_or_create_settings(payment_mode="live")
        assert ps.is_test_mode is False


@pytest.mark.django_db
class TestPaymentSettingsStripe:
    """Tests for Stripe computed properties."""

    def test_stripe_enabled_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=True,
            stripe_live_enabled=False,
        )
        assert ps.stripe_enabled is True

    def test_stripe_disabled_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=False,
            stripe_live_enabled=True,
        )
        assert ps.stripe_enabled is False

    def test_stripe_enabled_live_mode(self):
        ps = _get_or_create_settings(
            payment_mode="live",
            stripe_test_enabled=True,
            stripe_live_enabled=True,
        )
        assert ps.stripe_enabled is True

    def test_stripe_keys_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_public_key="pk_test_123",
            stripe_test_secret_key="sk_test_456",
            stripe_test_webhook_secret="whsec_test_789",
            stripe_live_public_key="pk_live_xxx",
            stripe_live_secret_key="sk_live_xxx",
        )
        assert ps.stripe_public_key == "pk_test_123"
        assert ps.stripe_secret_key == "sk_test_456"
        assert ps.stripe_webhook_secret == "whsec_test_789"

    def test_stripe_keys_live_mode(self):
        ps = _get_or_create_settings(
            payment_mode="live",
            stripe_test_public_key="pk_test_123",
            stripe_live_public_key="pk_live_abc",
            stripe_live_secret_key="sk_live_def",
            stripe_live_webhook_secret="whsec_live_ghi",
        )
        assert ps.stripe_public_key == "pk_live_abc"
        assert ps.stripe_secret_key == "sk_live_def"
        assert ps.stripe_webhook_secret == "whsec_live_ghi"


@pytest.mark.django_db
class TestPaymentSettingsPayPal:
    """Tests for PayPal computed properties."""

    def test_paypal_enabled_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            paypal_test_enabled=True,
            paypal_live_enabled=False,
        )
        assert ps.paypal_enabled is True

    def test_paypal_disabled_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            paypal_test_enabled=False,
        )
        assert ps.paypal_enabled is False

    def test_paypal_base_url_test(self):
        ps = _get_or_create_settings(payment_mode="test")
        assert "sandbox" in ps.paypal_base_url

    def test_paypal_base_url_live(self):
        ps = _get_or_create_settings(payment_mode="live")
        assert "sandbox" not in ps.paypal_base_url

    def test_paypal_credentials_test_mode(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            paypal_test_client_id="cid_test",
            paypal_test_secret="sec_test",
            paypal_live_client_id="cid_live",
            paypal_live_secret="sec_live",
        )
        assert ps.paypal_client_id == "cid_test"
        assert ps.paypal_secret == "sec_test"


@pytest.mark.django_db
class TestPaymentSettingsProviders:
    """Tests for available_providers property."""

    def test_all_enabled(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=True,
            paypal_test_enabled=True,
            bank_transfer_enabled=True,
        )
        providers = ps.available_providers
        assert "stripe" in providers
        assert "paypal" in providers
        assert "bank_transfer" in providers

    def test_none_enabled(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=False,
            paypal_test_enabled=False,
            bank_transfer_enabled=False,
        )
        assert ps.available_providers == []

    def test_only_bank_transfer(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=False,
            paypal_test_enabled=False,
            bank_transfer_enabled=True,
        )
        assert ps.available_providers == ["bank_transfer"]

    def test_stripe_only(self):
        ps = _get_or_create_settings(
            payment_mode="test",
            stripe_test_enabled=True,
            paypal_test_enabled=False,
            bank_transfer_enabled=False,
        )
        assert ps.available_providers == ["stripe"]

"""
Unit tests for apps/events/payment.py

Tests payment reference generation, Stripe checkout session creation,
and PayPal order creation/capture using mock objects.
No database access required — uses SimpleNamespace for mock objects.
"""

from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from apps.events.payment import generate_payment_reference


# ---------------------------------------------------------------------------
# Mock object factories
# ---------------------------------------------------------------------------


def create_mock_registration(
    pk=1,
    event_id=42,
    payment_amount=Decimal("50.00"),
    payment_session_id="",
    payment_provider="",
    payment_status="pending",
):
    """Create a mock EventRegistration for payment tests."""
    mock = MagicMock()
    mock.pk = pk
    mock.event_id = event_id
    mock.payment_amount = payment_amount
    mock.payment_session_id = payment_session_id
    mock.payment_provider = payment_provider
    mock.payment_status = payment_status
    mock.event = SimpleNamespace(
        pk=event_id, title="Summer Ride 2025", url="/events/summer-ride/"
    )
    return mock


def create_mock_payment_settings(
    stripe_enabled=True,
    stripe_secret_key="sk_test_xxx",
    stripe_public_key="pk_test_xxx",
    stripe_webhook_secret="whsec_test_xxx",
    paypal_enabled=True,
    paypal_client_id="paypal_client_xxx",
    paypal_secret="paypal_secret_xxx",
    paypal_base_url="https://api-m.sandbox.paypal.com",
):
    """Create a mock PaymentSettings for payment tests."""
    return SimpleNamespace(
        stripe_enabled=stripe_enabled,
        stripe_secret_key=stripe_secret_key,
        stripe_public_key=stripe_public_key,
        stripe_webhook_secret=stripe_webhook_secret,
        paypal_enabled=paypal_enabled,
        paypal_client_id=paypal_client_id,
        paypal_secret=paypal_secret,
        paypal_base_url=paypal_base_url,
    )


def create_mock_request():
    """Create a mock Django HttpRequest."""
    mock = MagicMock()
    mock.build_absolute_uri = lambda path: f"https://example.com{path}"
    return mock


# ---------------------------------------------------------------------------
# Payment reference tests
# ---------------------------------------------------------------------------


class TestGeneratePaymentReference:
    """Tests for generate_payment_reference function."""

    def test_format_matches_pattern(self):
        """Reference matches EVT-XXXXX-XXXX format."""
        reg = SimpleNamespace(pk=1, event_id=42)
        ref = generate_payment_reference(reg)
        assert ref.startswith("EVT-")
        parts = ref.split("-")
        assert len(parts) == 3
        assert len(parts[1]) == 5  # zero-padded event_id
        assert len(parts[2]) == 4  # hash part

    def test_deterministic(self):
        """Same registration produces same reference."""
        reg = SimpleNamespace(pk=1, event_id=42)
        assert generate_payment_reference(reg) == generate_payment_reference(reg)

    def test_different_pks_differ(self):
        """Different PKs produce different references."""
        reg1 = SimpleNamespace(pk=1, event_id=42)
        reg2 = SimpleNamespace(pk=2, event_id=42)
        assert generate_payment_reference(reg1) != generate_payment_reference(reg2)

    def test_hash_part_is_uppercase(self):
        """Hash portion of the reference is uppercase hex."""
        reg = SimpleNamespace(pk=99, event_id=7)
        ref = generate_payment_reference(reg)
        hash_part = ref.split("-")[2]
        assert hash_part == hash_part.upper()

    def test_event_id_zero_padded(self):
        """Event ID is zero-padded to 5 digits."""
        reg = SimpleNamespace(pk=1, event_id=3)
        ref = generate_payment_reference(reg)
        assert ref.startswith("EVT-00003-")


# ---------------------------------------------------------------------------
# Stripe Checkout tests
# ---------------------------------------------------------------------------


class TestCreateStripeCheckoutSession:
    """Tests for create_stripe_checkout_session function."""

    @patch("apps.events.payment.stripe")
    def test_creates_session_with_correct_params(self, mock_stripe):
        """Verify stripe.checkout.Session.create is called with correct line items."""
        from apps.events.payment import create_stripe_checkout_session

        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
        mock_stripe.checkout.Session.create.return_value = mock_session

        reg = create_mock_registration(payment_amount=Decimal("50.00"))
        ps = create_mock_payment_settings()
        request = create_mock_request()

        url = create_stripe_checkout_session(reg, ps, request)

        assert url == "https://checkout.stripe.com/pay/cs_test_123"
        mock_stripe.checkout.Session.create.assert_called_once()
        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert call_kwargs["mode"] == "payment"
        assert call_kwargs["line_items"][0]["price_data"]["unit_amount"] == 5000
        assert call_kwargs["line_items"][0]["price_data"]["currency"] == "eur"

    @patch("apps.events.payment.stripe")
    def test_stores_session_id_on_registration(self, mock_stripe):
        """Session ID is saved to registration.payment_session_id."""
        from apps.events.payment import create_stripe_checkout_session

        mock_session = MagicMock()
        mock_session.id = "cs_test_456"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_456"
        mock_stripe.checkout.Session.create.return_value = mock_session

        reg = create_mock_registration()
        ps = create_mock_payment_settings()
        request = create_mock_request()

        create_stripe_checkout_session(reg, ps, request)

        assert reg.payment_session_id == "cs_test_456"
        assert reg.payment_provider == "stripe"
        reg.save.assert_called_once()

    @patch("apps.events.payment.stripe")
    def test_sets_stripe_api_key(self, mock_stripe):
        """Stripe API key is set from payment settings."""
        from apps.events.payment import create_stripe_checkout_session

        mock_session = MagicMock()
        mock_session.id = "cs_test_789"
        mock_session.url = "https://checkout.stripe.com/x"
        mock_stripe.checkout.Session.create.return_value = mock_session

        reg = create_mock_registration()
        ps = create_mock_payment_settings(stripe_secret_key="sk_test_my_key")
        request = create_mock_request()

        create_stripe_checkout_session(reg, ps, request)

        assert mock_stripe.api_key == "sk_test_my_key"

    @patch("apps.events.payment.stripe")
    def test_success_url_contains_session_placeholder(self, mock_stripe):
        """Success URL includes the Stripe session ID template variable."""
        from apps.events.payment import create_stripe_checkout_session

        mock_session = MagicMock()
        mock_session.id = "cs_test_url"
        mock_session.url = "https://checkout.stripe.com/x"
        mock_stripe.checkout.Session.create.return_value = mock_session

        reg = create_mock_registration()
        ps = create_mock_payment_settings()
        request = create_mock_request()

        create_stripe_checkout_session(reg, ps, request)

        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert "{CHECKOUT_SESSION_ID}" in call_kwargs["success_url"]

    @patch("apps.events.payment.stripe")
    def test_metadata_includes_registration_id(self, mock_stripe):
        """Metadata contains registration_id and event_id."""
        from apps.events.payment import create_stripe_checkout_session

        mock_session = MagicMock()
        mock_session.id = "cs_test_meta"
        mock_session.url = "https://checkout.stripe.com/x"
        mock_stripe.checkout.Session.create.return_value = mock_session

        reg = create_mock_registration(pk=42, event_id=99)
        ps = create_mock_payment_settings()
        request = create_mock_request()

        create_stripe_checkout_session(reg, ps, request)

        call_kwargs = mock_stripe.checkout.Session.create.call_args[1]
        assert call_kwargs["metadata"]["registration_id"] == "42"
        assert call_kwargs["metadata"]["event_id"] == "99"


# ---------------------------------------------------------------------------
# PayPal access token tests
# ---------------------------------------------------------------------------


class TestGetPayPalAccessToken:
    """Tests for get_paypal_access_token function."""

    @patch("apps.events.payment.httpx.Client")
    def test_returns_access_token(self, mock_client_cls):
        """Access token is extracted from PayPal response."""
        from apps.events.payment import get_paypal_access_token

        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "TOKEN_ABC"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ps = create_mock_payment_settings()
        token = get_paypal_access_token(ps)

        assert token == "TOKEN_ABC"
        mock_client.post.assert_called_once()

    @patch("apps.events.payment.httpx.Client")
    def test_uses_correct_auth(self, mock_client_cls):
        """Basic auth uses client_id and secret."""
        from apps.events.payment import get_paypal_access_token

        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "T"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ps = create_mock_payment_settings(
            paypal_client_id="my_id", paypal_secret="my_secret"
        )
        get_paypal_access_token(ps)

        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["auth"] == ("my_id", "my_secret")


# ---------------------------------------------------------------------------
# PayPal order tests
# ---------------------------------------------------------------------------


class TestCreatePayPalOrder:
    """Tests for create_paypal_order function."""

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_creates_order_and_returns_approval_url(
        self, mock_client_cls, mock_token
    ):
        """PayPal order is created and approval URL is returned."""
        from apps.events.payment import create_paypal_order

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ORDER_123",
            "links": [
                {"rel": "self", "href": "https://api.paypal.com/orders/ORDER_123"},
                {
                    "rel": "payer-action",
                    "href": "https://www.paypal.com/checkoutnow?token=ORDER_123",
                },
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        reg = create_mock_registration(payment_amount=Decimal("30.00"))
        ps = create_mock_payment_settings()
        request = create_mock_request()

        order_id, approval_url = create_paypal_order(reg, ps, request)

        assert order_id == "ORDER_123"
        assert "paypal.com" in approval_url
        assert reg.payment_session_id == "ORDER_123"
        assert reg.payment_provider == "paypal"

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_sends_correct_amount(self, mock_client_cls, mock_token):
        """Order amount matches registration payment_amount."""
        from apps.events.payment import create_paypal_order

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ORD_X",
            "links": [
                {
                    "rel": "payer-action",
                    "href": "https://paypal.com/approve",
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        reg = create_mock_registration(payment_amount=Decimal("75.50"))
        ps = create_mock_payment_settings()
        request = create_mock_request()

        create_paypal_order(reg, ps, request)

        call_kwargs = mock_client.post.call_args[1]
        json_body = call_kwargs["json"]
        amount = json_body["purchase_units"][0]["amount"]["value"]
        assert amount == "75.50"

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_raises_on_missing_approval_link(self, mock_client_cls, mock_token):
        """ValueError raised if no payer-action link in response."""
        from apps.events.payment import create_paypal_order

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ORD_NO_LINK",
            "links": [{"rel": "self", "href": "https://api.paypal.com/x"}],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        reg = create_mock_registration()
        ps = create_mock_payment_settings()
        request = create_mock_request()

        with pytest.raises(ValueError, match="No payer-action link"):
            create_paypal_order(reg, ps, request)


# ---------------------------------------------------------------------------
# PayPal capture tests
# ---------------------------------------------------------------------------


class TestCapturePayPalOrder:
    """Tests for capture_paypal_order function."""

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_returns_completed_capture(self, mock_client_cls, mock_token):
        """Successful capture returns COMPLETED status and capture ID."""
        from apps.events.payment import capture_paypal_order

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "payments": {
                        "captures": [{"id": "CAP_123", "status": "COMPLETED"}]
                    }
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ps = create_mock_payment_settings()
        result = capture_paypal_order("ORDER_123", ps)

        assert result["status"] == "COMPLETED"
        assert result["id"] == "CAP_123"

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_handles_missing_capture_id(self, mock_client_cls, mock_token):
        """Missing captures array returns empty id without raising."""
        from apps.events.payment import capture_paypal_order

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "COMPLETED",
            "purchase_units": [{"payments": {}}],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        ps = create_mock_payment_settings()
        result = capture_paypal_order("ORDER_NO_CAP", ps)

        assert result["status"] == "COMPLETED"
        assert result["id"] == ""

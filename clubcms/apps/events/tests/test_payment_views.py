"""
Integration tests for payment views.

Uses Django test client + database fixtures. All external API calls
(Stripe, PayPal/httpx) are mocked.
"""

import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.events.models import EventRegistration

User = get_user_model()

try:
    import stripe  # noqa: F401

    HAS_STRIPE = True
except ImportError:
    HAS_STRIPE = False


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _create_event_page(**kwargs):
    """Create a minimal EventDetailPage for testing."""
    from wagtail.models import Page

    from apps.website.models.pages import EventDetailPage

    defaults = {
        "title": "Paid Event",
        "start_date": timezone.now() + timedelta(days=30),
        "base_fee": Decimal("50.00"),
        "registration_open": True,
        "max_attendees": 100,
    }
    defaults.update(kwargs)

    # Ensure unique slug
    if "slug" not in defaults:
        import uuid

        defaults["slug"] = f"paid-event-{uuid.uuid4().hex[:8]}"

    root = Page.objects.first()
    event = EventDetailPage(**defaults)
    root.add_child(instance=event)
    return event


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="paytest", password="testpass123456", email="pay@test.com"
    )


@pytest.fixture
def event_page(db):
    return _create_event_page()


@pytest.fixture
def registration(db, user, event_page):
    with patch("apps.notifications.services.create_notification"):
        return EventRegistration.objects.create(
            event=event_page,
            user=user,
            payment_amount=Decimal("50.00"),
            payment_status="pending",
        )


@pytest.fixture
def payment_settings(db):
    from wagtail.models import Site

    from apps.website.models.settings import PaymentSettings

    site = Site.objects.get(is_default_site=True)
    ps, _ = PaymentSettings.objects.get_or_create(site=site)
    ps.payment_mode = "test"
    ps.stripe_test_enabled = True
    ps.stripe_test_public_key = "pk_test_xxx"
    ps.stripe_test_secret_key = "sk_test_xxx"
    ps.stripe_test_webhook_secret = "whsec_test_xxx"
    ps.paypal_test_enabled = True
    ps.paypal_test_client_id = "paypal_test_id"
    ps.paypal_test_secret = "paypal_test_secret"
    ps.bank_transfer_enabled = True
    ps.bank_iban = "IT60X0542811101000000123456"
    ps.bank_transfer_expiry_days = 5
    ps.save()
    return ps


@pytest.fixture
def auth_client(user):
    client = Client()
    client.login(username="paytest", password="testpass123456")
    return client


# ---------------------------------------------------------------------------
# PaymentChoiceView GET
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentChoiceViewGET:
    """Tests for PaymentChoiceView GET requests."""

    def test_renders_available_providers(
        self, auth_client, registration, payment_settings
    ):
        """GET renders the payment choice page with providers."""
        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_redirects_if_already_paid(
        self, auth_client, registration, payment_settings
    ):
        """GET redirects to my_registrations if already paid."""
        registration.payment_status = "paid"
        registration.save(update_fields=["payment_status"])
        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.get(url)
        assert response.status_code == 302

    def test_404_for_other_users_registration(
        self, db, registration, payment_settings
    ):
        """GET returns 404 for another user's registration."""
        other = User.objects.create_user(
            username="other", password="testpass123456"
        )
        client = Client()
        client.login(username="other", password="testpass123456")
        url = reverse("events:payment_choice", args=[registration.pk])
        response = client.get(url)
        assert response.status_code == 404

    def test_requires_login(self, db, registration, payment_settings):
        """GET redirects to login for unauthenticated users."""
        client = Client()
        url = reverse("events:payment_choice", args=[registration.pk])
        response = client.get(url)
        assert response.status_code == 302
        assert "/accounts/login/" in response.url or "/login/" in response.url


# ---------------------------------------------------------------------------
# PaymentChoiceView POST — Stripe
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentChoiceViewPOSTStripe:
    """Tests for Stripe payment flow through PaymentChoiceView."""

    @patch("apps.events.payment.stripe")
    def test_stripe_redirects_to_checkout(
        self, mock_stripe, auth_client, registration, payment_settings
    ):
        """POST with provider=stripe creates session and redirects."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_abc"
        mock_session.url = "https://checkout.stripe.com/pay/cs_test_abc"
        mock_stripe.checkout.Session.create.return_value = mock_session

        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.post(url, {"provider": "stripe"})

        assert response.status_code == 302
        assert "checkout.stripe.com" in response.url

        registration.refresh_from_db()
        assert registration.payment_session_id == "cs_test_abc"
        assert registration.payment_provider == "stripe"

    @patch(
        "apps.events.payment.create_stripe_checkout_session",
        side_effect=Exception("Stripe error"),
    )
    def test_stripe_error_rerenders_with_error(
        self, mock_create, auth_client, registration, payment_settings
    ):
        """Stripe failure re-renders the page with an error message."""
        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.post(url, {"provider": "stripe"})

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# PaymentChoiceView POST — PayPal
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentChoiceViewPOSTPayPal:
    """Tests for PayPal payment flow through PaymentChoiceView."""

    @patch("apps.events.payment.get_paypal_access_token", return_value="TOKEN")
    @patch("apps.events.payment.httpx.Client")
    def test_paypal_redirects_to_approval(
        self,
        mock_client_cls,
        mock_token,
        auth_client,
        registration,
        payment_settings,
    ):
        """POST with provider=paypal creates order and redirects."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "id": "ORDER_PP_123",
            "links": [
                {
                    "rel": "payer-action",
                    "href": "https://www.paypal.com/checkoutnow?token=ORDER_PP_123",
                }
            ],
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_cls.return_value = mock_client

        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.post(url, {"provider": "paypal"})

        assert response.status_code == 302
        assert "paypal.com" in response.url

        registration.refresh_from_db()
        assert registration.payment_session_id == "ORDER_PP_123"
        assert registration.payment_provider == "paypal"

    @patch(
        "apps.events.payment.create_paypal_order",
        side_effect=Exception("PayPal error"),
    )
    def test_paypal_error_rerenders_with_error(
        self, mock_create, auth_client, registration, payment_settings
    ):
        """PayPal failure re-renders the page with an error message."""
        url = reverse("events:payment_choice", args=[registration.pk])
        response = auth_client.post(url, {"provider": "paypal"})

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# PaymentChoiceView POST — Bank Transfer
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentChoiceViewPOSTBankTransfer:
    """Tests for bank transfer flow through PaymentChoiceView."""

    @patch("apps.events.views.PaymentChoiceView._setup_bank_transfer")
    def test_bank_transfer_calls_setup(
        self, mock_setup, auth_client, registration, payment_settings
    ):
        """POST with provider=bank_transfer calls _setup_bank_transfer."""
        from django.http import HttpResponseRedirect

        mock_setup.return_value = HttpResponseRedirect("/mocked/")
        url = reverse("events:payment_choice", args=[registration.pk])
        auth_client.post(url, {"provider": "bank_transfer"})
        mock_setup.assert_called_once()


# ---------------------------------------------------------------------------
# StripeWebhookView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.skipif(not HAS_STRIPE, reason="stripe package not installed")
class TestStripeWebhookView:
    """Tests for StripeWebhookView."""

    @patch("apps.events.views.stripe_lib.Webhook.construct_event")
    def test_valid_webhook_updates_payment(
        self, mock_construct, client, payment_settings
    ):
        """Valid webhook with checkout.session.completed marks registration paid."""
        user = User.objects.create_user(
            username="webhookuser", password="testpass123456"
        )
        event = _create_event_page(slug="webhook-event")
        with patch("apps.notifications.services.create_notification"):
            reg = EventRegistration.objects.create(
                event=event,
                user=user,
                payment_amount=Decimal("50.00"),
                payment_session_id="cs_test_webhook",
                payment_provider="stripe",
                payment_status="pending",
            )

        mock_construct.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_webhook",
                    "payment_intent": "pi_test_123",
                }
            },
        }

        url = reverse("events:stripe_webhook")
        response = client.post(
            url,
            data=json.dumps({"fake": "payload"}),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig_xxx",
        )

        assert response.status_code == 200
        reg.refresh_from_db()
        assert reg.payment_status == "paid"
        assert reg.payment_id == "pi_test_123"

    @patch("apps.events.views.stripe_lib.Webhook.construct_event")
    def test_invalid_signature_returns_400(
        self, mock_construct, client, payment_settings
    ):
        """Invalid Stripe signature returns 400."""
        mock_construct.side_effect = ValueError("Invalid payload")

        url = reverse("events:stripe_webhook")
        response = client.post(
            url,
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_sig",
        )

        assert response.status_code == 400

    def test_no_csrf_required(self, client, payment_settings):
        """Webhook endpoint does not require CSRF token."""
        url = reverse("events:stripe_webhook")
        response = client.post(
            url, data=b"{}", content_type="application/json"
        )
        # Should not get 403 Forbidden (CSRF)
        assert response.status_code != 403

    @patch("apps.events.views.stripe_lib.Webhook.construct_event")
    def test_ignores_unknown_event_types(
        self, mock_construct, client, payment_settings
    ):
        """Non-checkout.session.completed events return 200 without processing."""
        mock_construct.return_value = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test_xxx"}},
        }

        url = reverse("events:stripe_webhook")
        response = client.post(
            url,
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# PayPalReturnView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPayPalReturnView:
    """Tests for PayPalReturnView."""

    @patch("apps.events.payment.capture_paypal_order")
    def test_successful_capture_redirects_to_success(
        self, mock_capture, auth_client, registration, payment_settings
    ):
        """Successful capture marks registration paid and redirects to success."""
        registration.payment_provider = "paypal"
        registration.payment_session_id = "ORDER_RETURN_123"
        registration.save(
            update_fields=["payment_provider", "payment_session_id"]
        )

        mock_capture.return_value = {"status": "COMPLETED", "id": "CAP_456"}

        url = reverse("events:paypal_return", args=[registration.pk])
        response = auth_client.get(url)

        assert response.status_code == 302
        assert "success" in response.url

        registration.refresh_from_db()
        assert registration.payment_status == "paid"
        assert registration.payment_id == "CAP_456"

    @patch("apps.events.payment.capture_paypal_order")
    def test_failed_capture_redirects_to_cancel(
        self, mock_capture, auth_client, registration, payment_settings
    ):
        """Failed capture redirects to cancel page."""
        registration.payment_provider = "paypal"
        registration.payment_session_id = "ORDER_FAIL"
        registration.save(
            update_fields=["payment_provider", "payment_session_id"]
        )

        mock_capture.side_effect = Exception("PayPal API error")

        url = reverse("events:paypal_return", args=[registration.pk])
        response = auth_client.get(url)

        assert response.status_code == 302
        assert "cancel" in response.url

    def test_already_paid_redirects_to_success(
        self, auth_client, registration, payment_settings
    ):
        """Already-paid registration redirects to success."""
        registration.payment_provider = "paypal"
        registration.payment_session_id = "ORDER_PAID"
        registration.payment_status = "paid"
        registration.save(
            update_fields=[
                "payment_provider",
                "payment_session_id",
                "payment_status",
            ]
        )

        url = reverse("events:paypal_return", args=[registration.pk])
        response = auth_client.get(url)

        assert response.status_code == 302
        assert "success" in response.url

    def test_non_paypal_registration_redirects_to_cancel(
        self, auth_client, registration, payment_settings
    ):
        """Non-PayPal registration redirects to cancel page."""
        registration.payment_provider = "stripe"
        registration.save(update_fields=["payment_provider"])

        url = reverse("events:paypal_return", args=[registration.pk])
        response = auth_client.get(url)

        assert response.status_code == 302
        assert "cancel" in response.url


# ---------------------------------------------------------------------------
# PaymentSuccessView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentSuccessView:
    """Tests for PaymentSuccessView."""

    def test_renders_for_paid_registration(
        self, auth_client, registration, payment_settings
    ):
        """Success page renders for paid registration."""
        registration.payment_status = "paid"
        registration.save(update_fields=["payment_status"])

        url = reverse("events:payment_success", args=[registration.pk])
        response = auth_client.get(url)

        assert response.status_code == 200

    def test_renders_for_pending_registration(
        self, auth_client, registration, payment_settings
    ):
        """Success page renders even if webhook hasn't arrived yet."""
        url = reverse("events:payment_success", args=[registration.pk])
        response = auth_client.get(url)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# PaymentCancelView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPaymentCancelView:
    """Tests for PaymentCancelView."""

    def test_renders_cancel_page(
        self, auth_client, registration, payment_settings
    ):
        """Cancel page renders correctly."""
        url = reverse("events:payment_cancel", args=[registration.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_requires_login(self, db, registration, payment_settings):
        """Cancel page redirects unauthenticated users."""
        client = Client()
        url = reverse("events:payment_cancel", args=[registration.pk])
        response = client.get(url)
        assert response.status_code == 302

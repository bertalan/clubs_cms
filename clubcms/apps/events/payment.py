"""
Payment service layer for the events app.

Provides payment reference generation for bank transfers,
Stripe Checkout Session management, and PayPal Orders API
integration via httpx.
"""

import hashlib
import logging

import httpx

try:
    import stripe
except ImportError:
    stripe = None

from django.urls import reverse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Bank transfer
# ---------------------------------------------------------------------------


def generate_payment_reference(registration):
    """
    Generate a unique payment reference for bank transfers.

    Format: EVT-{event_pk:05d}-{hash:4}
    Example: EVT-00042-A7B3
    """
    hash_part = hashlib.sha256(
        str(registration.pk).encode()
    ).hexdigest()[:4].upper()
    return f"EVT-{registration.event_id:05d}-{hash_part}"


# ---------------------------------------------------------------------------
# Stripe Checkout
# ---------------------------------------------------------------------------


def create_stripe_checkout_session(registration, payment_settings, request):
    """
    Create a Stripe Checkout Session and return the session URL.

    Args:
        registration: EventRegistration instance (must have payment_amount > 0).
        payment_settings: PaymentSettings instance (must have stripe_enabled=True).
        request: Django HttpRequest (for building absolute URLs).

    Returns:
        str: The Stripe Checkout Session URL for redirect.

    Raises:
        stripe.error.StripeError: On Stripe API failure.
        RuntimeError: If stripe library is not installed.
    """
    if stripe is None:
        raise RuntimeError("stripe package is not installed")

    stripe.api_key = payment_settings.stripe_secret_key

    success_url = request.build_absolute_uri(
        reverse("events:payment_success", args=[registration.pk])
    ) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = request.build_absolute_uri(
        reverse("events:payment_cancel", args=[registration.pk])
    )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "product_data": {
                        "name": registration.event.title,
                    },
                    "unit_amount": int(registration.payment_amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(registration.pk),
        metadata={
            "registration_id": str(registration.pk),
            "event_id": str(registration.event_id),
        },
    )

    registration.payment_session_id = session.id
    registration.payment_provider = "stripe"
    registration.save(update_fields=["payment_session_id", "payment_provider"])

    return session.url


# ---------------------------------------------------------------------------
# PayPal Orders API (via httpx)
# ---------------------------------------------------------------------------


def get_paypal_access_token(payment_settings):
    """
    Obtain a PayPal OAuth2 access token using client credentials.

    Args:
        payment_settings: PaymentSettings instance.

    Returns:
        str: Bearer access token.

    Raises:
        httpx.HTTPStatusError: On PayPal API failure.
    """
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{payment_settings.paypal_base_url}/v1/oauth2/token",
            auth=(payment_settings.paypal_client_id, payment_settings.paypal_secret),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json"},
        )
        response.raise_for_status()
        return response.json()["access_token"]


def create_paypal_order(registration, payment_settings, request):
    """
    Create a PayPal order and return (order_id, approval_url).

    Args:
        registration: EventRegistration instance.
        payment_settings: PaymentSettings instance.
        request: Django HttpRequest.

    Returns:
        tuple[str, str]: (order_id, approval_url).

    Raises:
        httpx.HTTPStatusError: On PayPal API failure.
        ValueError: If no approval link found in response.
    """
    access_token = get_paypal_access_token(payment_settings)

    return_url = request.build_absolute_uri(
        reverse("events:paypal_return", args=[registration.pk])
    )
    cancel_url = request.build_absolute_uri(
        reverse("events:payment_cancel", args=[registration.pk])
    )

    order_body = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": str(registration.pk),
                "description": registration.event.title[:127],
                "amount": {
                    "currency_code": "EUR",
                    "value": f"{registration.payment_amount:.2f}",
                },
            }
        ],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                    "brand_name": "Club CMS",
                    "user_action": "PAY_NOW",
                }
            }
        },
    }

    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{payment_settings.paypal_base_url}/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=order_body,
        )
        response.raise_for_status()
        data = response.json()

    order_id = data["id"]

    # Find the approval URL from response links
    approval_url = None
    for link in data.get("links", []):
        if link.get("rel") == "payer-action":
            approval_url = link["href"]
            break

    if not approval_url:
        raise ValueError(
            f"No payer-action link found in PayPal order response: {data}"
        )

    registration.payment_session_id = order_id
    registration.payment_provider = "paypal"
    registration.save(update_fields=["payment_session_id", "payment_provider"])

    return order_id, approval_url


def capture_paypal_order(order_id, payment_settings):
    """
    Capture a previously approved PayPal order.

    Args:
        order_id: PayPal order ID string.
        payment_settings: PaymentSettings instance.

    Returns:
        dict: With 'status' and 'id' keys.

    Raises:
        httpx.HTTPStatusError: On PayPal API failure.
    """
    access_token = get_paypal_access_token(payment_settings)

    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{payment_settings.paypal_base_url}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            content=b"",
        )
        response.raise_for_status()
        data = response.json()

    capture_id = ""
    try:
        capture_id = data["purchase_units"][0]["payments"]["captures"][0]["id"]
    except (KeyError, IndexError):
        logger.warning("Could not extract capture ID from PayPal response: %s", data)

    return {
        "status": data.get("status", ""),
        "id": capture_id,
    }

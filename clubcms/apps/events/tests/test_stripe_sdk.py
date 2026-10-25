"""
Stripe SDK compatibility (stripe-python 16).

Unlike the view tests, these do not mock the SDK where it matters:
- the webhook is signed for real (HMAC-SHA256), so stripe.Webhook.construct_event
  parses it and the handler works on real StripeObject instances (no .get()
  since stripe 15);
- the Checkout Session parameters are checked against the SDK's own
  SessionCreateParams (payment_method_types was removed in stripe 16).
"""

import hashlib
import hmac
import json
import re
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import stripe
from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse
from stripe.params.checkout import SessionCreateParams

from apps.events.payment import create_stripe_checkout_session

APPS_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _events_area(events_area_page):
    """EventsAreaPage for URL resolution (fixture in conftest.py)."""
    return events_area_page


def _signed_webhook(client, payload, secret):
    body = json.dumps(payload)
    ts = int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    return client.post(
        reverse("events:stripe_webhook"),
        data=body,
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE=f"t={ts},v1={sig}",
    )


def _completed_event(session_id, payment_intent="pi_test_123"):
    return {
        "id": "evt_test_1",
        "object": "event",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": session_id,
                "object": "checkout.session",
                "payment_intent": payment_intent,
                "payment_status": "paid",
            }
        },
    }


@pytest.mark.django_db
def test_real_signed_webhook_marks_registration_paid(client, registration, payment_settings):
    registration.payment_session_id = "cs_test_real"
    registration.payment_provider = "stripe"
    registration.save()

    resp = _signed_webhook(client, _completed_event("cs_test_real"), "whsec_test_xxx")

    assert resp.status_code == 200
    registration.refresh_from_db()
    assert registration.payment_status == "paid"
    assert registration.payment_id == "pi_test_123"


@pytest.mark.django_db
def test_webhook_without_payment_intent(client, registration, payment_settings):
    registration.payment_session_id = "cs_test_nopi"
    registration.payment_provider = "stripe"
    registration.save()
    payload = _completed_event("cs_test_nopi")
    del payload["data"]["object"]["payment_intent"]

    resp = _signed_webhook(client, payload, "whsec_test_xxx")

    assert resp.status_code == 200
    registration.refresh_from_db()
    assert registration.payment_status == "paid"
    assert registration.payment_id == ""


@pytest.mark.django_db
def test_webhook_with_wrong_secret_is_rejected(client, registration, payment_settings):
    resp = _signed_webhook(client, _completed_event("cs_x"), "whsec_wrong")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_checkout_params_are_valid_for_the_sdk(registration, payment_settings):
    request = RequestFactory().get("/", HTTP_HOST="localhost")
    fake_session = MagicMock(id="cs_test_new", url="https://checkout.stripe.test/cs")
    with patch("stripe.checkout.Session.create", return_value=fake_session) as create:
        url = create_stripe_checkout_session(registration, payment_settings, request)

    assert url == "https://checkout.stripe.test/cs"
    kwargs = create.call_args.kwargs
    unknown = set(kwargs) - set(SessionCreateParams.__annotations__)
    assert not unknown, f"parameters not in stripe {stripe.VERSION}: {unknown}"
    assert kwargs["allowed_payment_method_types"] == ["card"]


def test_api_version_is_pinned_to_the_sdk_version():
    from stripe._api_version import _ApiVersion

    assert settings.STRIPE_API_VERSION == _ApiVersion.CURRENT


def test_code_does_not_use_removed_stripe_apis():
    offenders = []
    for path in APPS_DIR.rglob("*.py"):
        if "/tests/" in str(path) or "/migrations/" in str(path):
            continue
        src = path.read_text()
        for needle in (r"\bstripe\.error\.", r"\bstripe_lib\.error\.", r"\bpayment_method_types="):
            if re.search(needle, src):
                offenders.append(f"{path.relative_to(APPS_DIR)}: {needle}")
    assert not offenders, offenders

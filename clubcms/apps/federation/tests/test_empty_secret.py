"""
An empty shared secret must never authenticate anything.

Before 2026-10-25 verify_request() accepted a signature computed with an
empty key, so a partner record without `our_key_for_them` could be called by
anyone who knew its (public) api_key.
"""

from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.federation.api.security import sign_request, verify_request
from apps.federation.models import FederatedClub
from apps.federation.sync.tasks import _post_interest_to_partner, sync_club_events
from apps.federation.tests.test_api import EVENTS_URL, FederationAPIBase


def test_verify_request_rejects_empty_secret():
    ts = timezone.now().isoformat()
    assert verify_request("", ts, sign_request("", ts, "")) is False
    assert verify_request("   ", ts, sign_request("   ", ts, "")) is False


class TestApiWithoutSharedSecret(FederationAPIBase):
    def setUp(self):
        super().setUp()
        FederatedClub.objects.filter(pk=self.partner.pk).update(our_key_for_them="")

    def test_request_signed_with_empty_secret_is_rejected(self):
        ts = timezone.now().isoformat()
        resp = self.client.get(
            EVENTS_URL,
            HTTP_X_FEDERATION_KEY=self.partner.api_key,
            HTTP_X_TIMESTAMP=ts,
            HTTP_X_SIGNATURE=sign_request("", ts, ""),
        )
        self.assertEqual(resp.status_code, 401)


@pytest.mark.django_db
def test_sync_without_secret_does_not_call_partner():
    club = FederatedClub.objects.create(
        name="No Secret", short_code="NOSECRET", base_url="https://p.example",
        api_key="pk_nosecret", our_key_for_them="", is_active=True, is_approved=True,
    )
    with patch("urllib.request.urlopen") as urlopen:
        with pytest.raises(ValueError):
            sync_club_events(str(club.pk))
        urlopen.assert_not_called()
    club.refresh_from_db()
    assert club.last_error


@pytest.mark.django_db
def test_interest_push_without_secret_does_not_call_partner():
    club = FederatedClub.objects.create(
        name="No Secret 2", short_code="NOSECRET2", base_url="https://p.example",
        api_key="pk_nosecret2", our_key_for_them="", is_active=True, is_approved=True,
    )
    with patch("urllib.request.urlopen") as urlopen:
        _post_interest_to_partner(club, "evt-1", {"interested": 1}, "OURS")
        urlopen.assert_not_called()


@pytest.mark.django_db
def test_api_key_is_unique():
    field = FederatedClub._meta.get_field("api_key")
    assert field.unique

"""
An empty secret must never authenticate anything.

Before 2026-10-25 verify_request() accepted a signature computed with an
empty key, so a partner record without a secret could be called by anyone
who knew its (public) key.
"""

from unittest.mock import patch

import pytest

from apps.federation.models import FederatedClub
from apps.federation.sync.tasks import _post_interest_to_partner, sync_club_events
from apps.federation.tests.test_api import EVENTS_URL, FederationAPIBase, signed_headers


class TestApiWithoutSecret(FederationAPIBase):
    def setUp(self):
        super().setUp()
        FederatedClub.objects.filter(pk=self.partner.pk).update(inbound_secret="")

    def test_request_signed_with_empty_secret_is_rejected(self):
        resp = self.client.get(EVENTS_URL, **signed_headers(self.partner.inbound_key, ""))
        self.assertEqual(resp.status_code, 401)


def _club(code, **kwargs):
    return FederatedClub.objects.create(
        name=code, short_code=code, base_url="https://p.example",
        is_active=True, is_approved=True, **kwargs,
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "outbound", [{"outbound_key": "pk_x", "outbound_secret": ""}, {"outbound_key": "", "outbound_secret": "sk_x"}]
)
def test_sync_without_partner_credential_does_not_call_partner(outbound):
    club = _club("NOSECRET", **outbound)
    with patch("urllib.request.urlopen") as urlopen:
        with pytest.raises(ValueError):
            sync_club_events(str(club.pk))
        urlopen.assert_not_called()
    club.refresh_from_db()
    assert club.last_error


@pytest.mark.django_db
def test_interest_push_without_partner_credential_does_not_call_partner():
    club = _club("NOSECRET2")
    with patch("urllib.request.urlopen") as urlopen:
        _post_interest_to_partner(club, "evt-1", {"interested": 1}, "OURS")
        urlopen.assert_not_called()


@pytest.mark.django_db
def test_new_club_gets_its_own_inbound_credential():
    first, second = _club("ONE"), _club("TWO")
    assert first.inbound_key.startswith("pk_") and first.inbound_secret.startswith("sk_")
    assert first.inbound_key != second.inbound_key
    assert first.inbound_secret != second.inbound_secret
    assert FederatedClub._meta.get_field("inbound_key").unique


@pytest.mark.django_db
def test_sync_signs_with_the_credential_the_partner_issued_us():
    club = _club("SIGNS", outbound_key="pk_from_partner", outbound_secret="sk_from_partner")
    with patch("urllib.request.urlopen", side_effect=OSError("stop")) as urlopen:
        with pytest.raises(OSError):
            sync_club_events(str(club.pk))
    request = urlopen.call_args.args[0]
    assert request.get_header("X-federation-key") == "pk_from_partner"
    assert request.get_header("X-federation-key") != club.inbound_key

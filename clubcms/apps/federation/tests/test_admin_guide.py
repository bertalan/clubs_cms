"""
Partner club admin page: page guide, read-only system fields, the
credential we issue (shown, regenerated), the partner's credential
(pasted), connection test and scheduled sync.
"""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest
from django.test import Client, override_settings
from django.urls import reverse

from apps.federation.models import FederatedClub

ADD_URL_NAME = "wagtailsnippets_federation_federatedclub:add"
EDIT_URL_NAME = "wagtailsnippets_federation_federatedclub:edit"


@pytest.fixture
def admin_client(db, django_user_model):
    user = django_user_model.objects.create_superuser("guide_admin", "g@example.com", "x")
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def club(db):
    return FederatedClub.objects.create(
        name="Partner", short_code="PARTNER", base_url="https://partner.example",
        outbound_key="pk_partner", outbound_secret="sk_partner",
        is_active=True, is_approved=True, last_error="old error",
    )


def test_add_page_shows_guide_and_no_tooltip(admin_client):
    html = admin_client.get(reverse(ADD_URL_NAME)).content.decode()
    assert "data-admin-guide-open" in html
    assert "<dialog" in html
    assert "admin_field_help" not in html


def test_system_fields_are_read_only(admin_client, club):
    html = admin_client.get(reverse(EDIT_URL_NAME, args=[club.pk])).content.decode()
    for field in ("last_sync", "last_error", "created_at", "created_by", "inbound_key", "inbound_secret"):
        assert f'name="{field}"' not in html, field
    assert "old error" in html  # still visible, as read-only output
    for field in ("outbound_key", "outbound_secret", "short_code", "base_url"):
        assert f'name="{field}"' in html, field
    assert 'type="password" name="outbound_secret"' in html


def test_edit_page_shows_the_credential_we_issued(admin_client, club):
    html = admin_client.get(reverse(EDIT_URL_NAME, args=[club.pk])).content.decode()
    assert club.inbound_key in html
    assert club.inbound_secret in html  # masked in a password input, copyable
    assert reverse("federation_regenerate_inbound", args=[club.pk]) in html


def test_add_page_does_not_show_a_credential_that_will_change(admin_client):
    html = admin_client.get(reverse(ADD_URL_NAME)).content.decode()
    assert "federation-inbound-key" not in html
    assert "regenerate-access" not in html
    assert "test-connection" not in html


def test_add_page_saves_a_long_partner_secret(admin_client):
    from apps.federation.utils import generate_public_key, generate_secret_key

    secret = generate_secret_key()  # 67 characters: longer than the old 64 limit
    resp = admin_client.post(reverse(ADD_URL_NAME), {
        "name": "New Partner", "short_code": "NEWP", "base_url": "https://new.example",
        "outbound_key": generate_public_key(), "outbound_secret": secret,
        "auto_import": "on",
    })
    assert resp.status_code == 302, resp.context["form"].errors if resp.context else resp
    club = FederatedClub.objects.get(short_code="NEWP")
    assert club.outbound_secret == secret
    assert club.inbound_secret.startswith("sk_") and club.inbound_secret != secret


# ---------------------------------------------------------------------------
# Regenerate the credential we issued
# ---------------------------------------------------------------------------


def test_regenerate_replaces_key_and_secret(admin_client, club):
    old_key, old_secret = club.inbound_key, club.inbound_secret
    resp = admin_client.post(reverse("federation_regenerate_inbound", args=[club.pk]))
    assert resp.status_code == 302
    club.refresh_from_db()
    assert club.inbound_key != old_key
    assert club.inbound_secret != old_secret
    assert club.outbound_key == "pk_partner"  # the partner's credential is untouched


def test_regenerate_requires_post_and_permission(admin_client, club, django_user_model):
    url = reverse("federation_regenerate_inbound", args=[club.pk])
    assert admin_client.get(url).status_code == 405
    member = django_user_model.objects.create_user("member", "m@example.com", "x")
    c = Client()
    c.force_login(member)
    old_key = club.inbound_key
    assert c.post(url).status_code in (302, 403)
    club.refresh_from_db()
    assert club.inbound_key == old_key


# ---------------------------------------------------------------------------
# Connection test
# ---------------------------------------------------------------------------


class _Resp(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _test_connection(admin_client, club):
    url = reverse("federation_test_connection", args=[club.pk])
    return admin_client.post(url, follow=True)


def test_connection_ok(admin_client, club):
    body = json.dumps({"events": [], "total": 0, "club": "X"}).encode()
    with patch("urllib.request.urlopen", return_value=_Resp(body)) as urlopen:
        resp = _test_connection(admin_client, club)
    request = urlopen.call_args.args[0]
    assert request.get_header("X-federation-key") == "pk_partner"
    assert request.get_header("X-signature").startswith("sha256=")
    assert request.get_header("X-nonce")
    messages = [str(m) for m in resp.context["messages"]]
    assert any("OK" in m for m in messages), messages


@pytest.mark.parametrize("code", [401, 403, 404])
def test_connection_http_errors_are_explained(admin_client, club, code):
    err = urllib.error.HTTPError(club.base_url, code, "Error", {}, None)
    with patch("urllib.request.urlopen", side_effect=err):
        resp = _test_connection(admin_client, club)
    messages = " ".join(str(m) for m in resp.context["messages"])
    assert str(code) in messages


def test_connection_without_secret_does_not_call_partner(admin_client, club):
    FederatedClub.objects.filter(pk=club.pk).update(outbound_secret="")
    with patch("urllib.request.urlopen") as urlopen:
        _test_connection(admin_client, club)
    urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Scheduled sync
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sync_is_scheduled_only_when_federation_is_enabled():
    from django_q.models import Schedule

    from apps.federation.apps import ensure_federation_schedules

    with override_settings(FEDERATION_ENABLED=False):
        ensure_federation_schedules()
    assert not Schedule.objects.filter(name__startswith="federation-").exists()

    with override_settings(FEDERATION_ENABLED=True):
        ensure_federation_schedules()
        ensure_federation_schedules()  # idempotent
    funcs = set(Schedule.objects.filter(name__startswith="federation-").values_list("func", flat=True))
    assert funcs == {
        "apps.federation.sync.tasks.sync_all_clubs",
        "apps.federation.sync.tasks.sync_interest_counts",
    }

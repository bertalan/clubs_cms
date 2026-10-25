"""
Partner club admin page: page guide, read-only system fields, key
generation, connection test and scheduled sync.
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
        api_key="pk_partner", our_key_for_them="sk_partner",
        is_active=True, is_approved=True, last_error="old error",
    )


def test_add_page_shows_guide_and_no_tooltip(admin_client):
    html = admin_client.get(reverse(ADD_URL_NAME)).content.decode()
    assert "data-admin-guide-open" in html
    assert "<dialog" in html
    assert "admin_field_help" not in html


def test_system_fields_are_read_only(admin_client, club):
    html = admin_client.get(reverse(EDIT_URL_NAME, args=[club.pk])).content.decode()
    for field in ("last_sync", "last_error", "created_at", "created_by"):
        assert f'name="{field}"' not in html, field
    assert "old error" in html  # still visible, as read-only output
    for field in ("api_key", "our_key_for_them", "short_code", "base_url"):
        assert f'name="{field}"' in html, field


# ---------------------------------------------------------------------------
# Generate key pair
# ---------------------------------------------------------------------------


def test_generate_keys_returns_a_fresh_pair(admin_client):
    url = reverse("federation_generate_keys")
    first = admin_client.post(url).json()
    second = admin_client.post(url).json()
    assert first["api_key"].startswith("pk_")
    assert first["shared_secret"].startswith("sk_")
    assert first != second


def test_generate_keys_requires_post_and_staff(db, admin_client, django_user_model):
    url = reverse("federation_generate_keys")
    assert admin_client.get(url).status_code == 405
    member = django_user_model.objects.create_user("member", "m@example.com", "x")
    c = Client()
    c.force_login(member)
    assert c.post(url).status_code in (302, 403)


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
    messages = [str(m) for m in resp.context["messages"]]
    assert any("OK" in m for m in messages), messages


def test_connection_auth_error_explains_keys(admin_client, club):
    err = urllib.error.HTTPError(club.base_url, 401, "Unauthorized", {}, None)
    with patch("urllib.request.urlopen", side_effect=err):
        resp = _test_connection(admin_client, club)
    messages = " ".join(str(m) for m in resp.context["messages"])
    assert "401" in messages


def test_connection_without_secret_does_not_call_partner(admin_client, club):
    FederatedClub.objects.filter(pk=club.pk).update(our_key_for_them="")
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

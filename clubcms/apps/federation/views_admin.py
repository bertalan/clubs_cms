"""
Admin-only helpers for the partner club edit page.

- generate_keys: a fresh pk_/sk_ pair, to be copied to both sites.
- test_connection: signed request to the partner's events endpoint, with
  an explanation of the most common failures.
"""

import json
import urllib.error
import urllib.request

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.federation.models import FederatedClub
from apps.federation.sync.tasks import build_events_request
from apps.federation.utils import generate_api_key_pair

TEST_TIMEOUT = 10  # seconds


@require_POST
@staff_member_required
def generate_keys(request):
    if not request.user.has_perm("federation.change_federatedclub") and not request.user.has_perm(
        "federation.add_federatedclub"
    ):
        return HttpResponseForbidden()
    api_key, shared_secret = generate_api_key_pair()
    return JsonResponse({"api_key": api_key, "shared_secret": shared_secret})


def _connection_error_message(club, exc):
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code == 401:
            return _(
                "The partner answered 401 (not authenticated). Check that both "
                "sites have exactly the same link key and shared secret, and that "
                "the partner has marked this club as approved and active."
            )
        if exc.code == 404:
            return _(
                "The partner answered 404. Check the site address (root only, no "
                "path) and that federation is enabled on the partner site."
            )
        if exc.code == 429:
            return _("The partner answered 429: too many requests. Try again in an hour.")
        return _("The partner answered with HTTP error %(code)s.") % {"code": exc.code}
    if isinstance(exc, OSError):  # URLError, timeouts, TLS errors
        return _("Could not reach %(url)s: %(reason)s. Check the address.") % {
            "url": club.base_url,
            "reason": getattr(exc, "reason", exc),
        }
    return _(
        "The partner answered, but not with federation data. Check that the "
        "address points to a ClubCMS site."
    )


@require_POST
@staff_member_required
def test_connection(request, pk):
    if not request.user.has_perm("federation.change_federatedclub"):
        return HttpResponseForbidden()
    club = get_object_or_404(FederatedClub, pk=pk)
    edit_url = reverse("wagtailsnippets_federation_federatedclub:edit", args=[club.pk])

    if not club.our_key_for_them.strip() or not club.api_key.strip():
        messages.error(
            request,
            _("Link key and shared secret are both required. Save them, then test again."),
        )
        return redirect(edit_url)

    req = build_events_request(club, timezone.now().date().isoformat())
    try:
        with urllib.request.urlopen(req, timeout=TEST_TIMEOUT) as response:
            data = json.loads(response.read().decode("utf-8"))
        if "events" not in data:
            raise ValueError("no events key")
    except (OSError, ValueError) as exc:
        messages.error(request, _connection_error_message(club, exc))
        return redirect(edit_url)

    messages.success(
        request,
        _("Connection OK: %(club)s answered and shares %(count)d upcoming events.")
        % {"club": club.name, "count": len(data.get("events", []))},
    )
    return redirect(edit_url)

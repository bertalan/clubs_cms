"""
Admin-only helpers for the partner club edit page.

- regenerate_inbound: replaces the access credential we issued to the
  partner; the old one stops working at once.
- test_connection: request to the partner's events endpoint, signed with
  the credential the partner issued us, with an explanation of the most
  common failures.
"""

import json
import urllib.error
import urllib.request

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.federation.models import FederatedClub
from apps.federation.sync.tasks import build_events_request

TEST_TIMEOUT = 10  # seconds


def _edit_url(club):
    return reverse("wagtailsnippets_federation_federatedclub:edit", args=[club.pk])


@require_POST
@staff_member_required
def regenerate_inbound(request, pk):
    if not request.user.has_perm("federation.change_federatedclub"):
        return HttpResponseForbidden()
    club = get_object_or_404(FederatedClub, pk=pk)
    club.regenerate_inbound_credential()
    messages.success(
        request,
        _(
            "New access key and secret created for %(club)s. The old ones no "
            "longer work: send the new values to the partner's administrator."
        )
        % {"club": club.name},
    )
    return redirect(_edit_url(club))


def _connection_error_message(club, exc):
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code == 401:
            return _(
                "The partner answered 401 (not authenticated). Check that you "
                "pasted exactly the access key and secret the partner issued to "
                "us, and that the partner has marked our club as approved and "
                "active on its site."
            )
        if exc.code == 403:
            return _(
                "The partner answered 403: it recognised us but does not share "
                "its events with us. Ask them to tick \"Share our events\" in "
                "the record for our club."
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
    edit_url = _edit_url(club)

    if not club.has_outbound_credential:
        messages.error(
            request,
            _(
                "Paste the access key and secret the partner issued to us, "
                "save, then test again."
            ),
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

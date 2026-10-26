"""
Page guides for the federation admin pages.
"""

from django.utils.translation import gettext_lazy as _

from apps.core.admin_guides import AdminGuide, GuideSection

FEDERATED_CLUB_GUIDE = AdminGuide(
    key="federated-club",
    title=_("Partner clubs: how to set up a link"),
    summary=_(
        "A partner club is another club's ClubCMS site linked to ours: the "
        "two sites exchange events, never member data. Each club issues the "
        "access to its own site and sends it to the other, so the link needs "
        "two different credentials, one per direction."
    ),
    sections=(
        GuideSection(
            title=_("What this page is for"),
            paragraphs=(
                _(
                    "Each record is a link with one partner club. With an "
                    "active link our site reads the partner's upcoming events "
                    "and shows them among ours, and, if you allow it, the "
                    "partner reads our events. Interest counts are exchanged "
                    "as totals only."
                ),
            ),
        ),
        GuideSection(
            title=_("Two credentials, one per direction"),
            paragraphs=(
                _(
                    "\"Access we grant to this partner\" is created by our "
                    "site when you save the club. You send it to the partner, "
                    "who uses it to read our events. Only we can replace it, "
                    "and replacing it locks the partner out until it pastes "
                    "the new values."
                ),
                _(
                    "\"Access this partner grants us\" is created by the "
                    "partner on its own site, in the record for our club. "
                    "They send it to you and you paste it here. We use it to "
                    "read their events."
                ),
                _(
                    "The two credentials are different and independent: each "
                    "club decides who may enter its own site."
                ),
            ),
        ),
        GuideSection(
            title=_("Before you start"),
            paragraphs=(
                _(
                    "Agree on the link with the partner's administrator. You "
                    "need the address of their site and the club code they "
                    "use for themselves. Federation must be enabled on both "
                    "servers (FEDERATION_ENABLED setting)."
                ),
            ),
        ),
        GuideSection(
            title=_("Setting up the link"),
            steps=(
                _(
                    "Fill in the partner's name, club code and site address "
                    "(the root of their site, e.g. https://partner.example, "
                    "without any path), then save."
                ),
                _(
                    "After saving, \"Access we grant to this partner\" shows "
                    "an access key (pk_…) and an access secret (sk_…). Send "
                    "both to the partner's administrator, if you can over two "
                    "channels: the key by email, the secret by phone or "
                    "encrypted message."
                ),
                _(
                    "The partner does the same on its site and sends you its "
                    "key and secret: paste them in \"Access this partner "
                    "grants us\"."
                ),
                _(
                    "Tick \"Approved\" once you know who runs the partner "
                    "site, and \"Active\" to open the link: both are needed."
                ),
                _(
                    "Choose whether to share our events and whether imported "
                    "events are published immediately or wait for approval."
                ),
                _(
                    "Save, then press \"Test connection\": it calls the "
                    "partner with the values you pasted and explains any "
                    "error."
                ),
            ),
        ),
        GuideSection(
            title=_("Common problems"),
            paragraphs=(
                _(
                    "Error 401: the key or secret pasted in \"Access this "
                    "partner grants us\" does not match what the partner "
                    "issued, or the partner has not approved and activated "
                    "our club on its side."
                ),
                _(
                    "Error 403: the partner recognises us but has not ticked "
                    "\"Share our events\" for our club."
                ),
                _(
                    "Error 404: the address includes a path, or federation is "
                    "not enabled on the partner's server."
                ),
                _(
                    "No events arriving: check \"Last sync error\" at the "
                    "bottom of this page, and that the partner has events "
                    "published in the future."
                ),
            ),
        ),
        GuideSection(
            title=_("After saving"),
            paragraphs=(
                _(
                    "Events are fetched automatically every hour from every "
                    "partner that is approved, active and whose access you "
                    "have pasted. \"Last successful sync\" and \"Last sync error\" "
                    "are filled in by the system. To stop the exchange "
                    "without losing the settings, untick \"Active\"."
                ),
            ),
        ),
    ),
)

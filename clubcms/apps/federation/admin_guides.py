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
        "two sites exchange events, never member data. The link only works "
        "if both administrators enter the same key pair."
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
            title=_("Before you start"),
            paragraphs=(
                _(
                    "Agree on the link with the partner's administrator. You "
                    "need: the address of their site, the club code they use "
                    "for themselves, and a key pair that you will both enter "
                    "exactly the same. Federation must be enabled on both "
                    "servers (FEDERATION_ENABLED setting)."
                ),
            ),
        ),
        GuideSection(
            title=_("Setting up the link"),
            steps=(
                _(
                    "One of the two administrators presses \"Generate key "
                    "pair\": it fills in a link key (pk_…) and a shared "
                    "secret (sk_…)."
                ),
                _(
                    "Send both values to the other administrator over a "
                    "secure channel (phone, encrypted message), never by "
                    "plain email."
                ),
                _(
                    "Both sites enter the same two values: pk_… in \"Link "
                    "key\", sk_… in \"Shared secret\". They are not one key "
                    "per side: the pair is shared."
                ),
                _(
                    "Club code: the code the partner uses for itself. "
                    "Partner site address: the root of their site, e.g. "
                    "https://partner.example, without any path."
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
                    "Save, then press \"Test connection\": it checks the saved "
                    "values against the partner site and explains any error."
                ),
            ),
        ),
        GuideSection(
            title=_("Common problems"),
            paragraphs=(
                _(
                    "Error 401: the two sites do not have exactly the same "
                    "link key and shared secret, or the partner has not "
                    "approved and activated our club on its side."
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
                    "partner that is approved, active and has a shared "
                    "secret. \"Last successful sync\" and \"Last sync error\" "
                    "are filled in by the system. To stop the exchange "
                    "without losing the settings, untick \"Active\"."
                ),
            ),
        ),
    ),
)

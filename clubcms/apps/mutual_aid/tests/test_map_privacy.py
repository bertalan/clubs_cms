"""
The helpers map must respect each helper's privacy choices.

Before 2026-10-26 the map listed a helper's notes even with "Show helper
notes" off (the JSON API already hid them), and computed names without
the viewer, ignoring "show real name to members".
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site

from apps.mutual_aid.models import AidPrivacySettings, MutualAidPage
from apps.website.templatetags.website_tags import visible_name

User = get_user_model()


@pytest.fixture
def aid_page(db):
    root = Page.objects.filter(depth=1).first() or Page.add_root(title="Root")
    home = Page.objects.filter(depth=2).first()
    if not home:
        home = Page(title="Test Home", slug="test-home")
        root.add_child(instance=home)
    Site.objects.update_or_create(
        hostname="localhost", defaults={"root_page": home, "is_default_site": True}
    )
    page = MutualAidPage(title="Mutual Aid", slug="mutual-aid-privacy")
    home.add_child(instance=page)
    page.save_revision().publish()
    return page


def _member(username, **kwargs):
    return User.objects.create_user(
        username=username, password="x", membership_expiry=date.today() + timedelta(days=365), **kwargs
    )


def test_map_hides_notes_unless_the_helper_allows_them(client, aid_page):
    hidden = _member("hidden", first_name="Ada", last_name="Bianchi", aid_available=True,
                     aid_location_city="Rome", aid_notes="SECRET-NOTE-A")
    shown = _member("shown", first_name="Bea", last_name="Neri", aid_available=True,
                    aid_location_city="Milan", aid_notes="PUBLIC-NOTE-B")
    AidPrivacySettings.objects.update_or_create(user=hidden, defaults={"show_bio_on_aid": False})
    AidPrivacySettings.objects.update_or_create(user=shown, defaults={"show_bio_on_aid": True})

    client.force_login(_member("viewer"))
    html = client.get(aid_page.url).content.decode()
    assert "SECRET-NOTE-A" not in html
    assert "PUBLIC-NOTE-B" in html


def test_map_shows_real_name_only_when_the_helper_allows_it(client, aid_page):
    _member("private", first_name="Carla", last_name="Verdi", display_name="RiderC",
            aid_available=True, aid_location_city="Rome", show_real_name_to_members=False)
    client.force_login(_member("viewer2"))
    html = client.get(aid_page.url).content.decode()
    assert "RiderC" in html
    assert "Verdi" not in html


@pytest.mark.django_db
def test_visible_name_filter_respects_viewer():
    author = _member("author", first_name="Dario", last_name="Rossi", display_name="DR",
                     show_real_name_to_members=False)
    assert visible_name(author, None) == "DR"
    assert visible_name(author, _member("member")) == "DR"
    staff = User.objects.create_user(username="staff", password="x", is_staff=True)
    assert "Rossi" in visible_name(author, staff)
    assert visible_name(None, staff) == ""

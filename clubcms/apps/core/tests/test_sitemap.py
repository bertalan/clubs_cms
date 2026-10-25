"""
/sitemap.xml must render (wagtail.contrib.sitemaps uses the "sitemap.xml"
template shipped by django.contrib.sitemaps: 500 TemplateDoesNotExist on live
for at least a month before 2026-10-25) and must list every locale, with
reciprocal hreflang alternates between translations.
"""

import xml.etree.ElementTree as ET

import pytest
from django.test import Client
from wagtail.models import Locale, Page, PageViewRestriction, Site

NS = {
    "sm": "http://www.sitemaps.org/schemas/sitemap/0.9",
    "xhtml": "http://www.w3.org/1999/xhtml",
}


def _sitemap():
    response = Client().get("/sitemap.xml", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    root = ET.fromstring(response.content)
    urls = {}
    for url in root.findall("sm:url", NS):
        loc = url.find("sm:loc", NS).text
        urls[loc] = {
            link.get("hreflang"): link.get("href")
            for link in url.findall("xhtml:link", NS)
        }
    return urls


@pytest.mark.django_db
def test_sitemap_xml_renders():
    response = Client().get("/sitemap.xml", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert b"<urlset" in response.content


@pytest.fixture
def site_tree(db):
    """EN home + IT translation, a translated child, an EN-only child,
    a draft IT child and a private EN child."""
    en = Locale.objects.get_or_create(language_code="en")[0]
    it = Locale.objects.get_or_create(language_code="it")[0]
    root = Page.get_first_root_node()
    home = root.add_child(instance=Page(title="Home", slug="sm-home", locale=en))
    Site.objects.all().delete()
    Site.objects.create(hostname="localhost", root_page=home, is_default_site=True)

    home_it = home.copy_for_translation(it)
    home_it.save_revision().publish()

    about = home.add_child(instance=Page(title="About", slug="about"))
    about_it = about.copy_for_translation(it)
    about_it.save_revision().publish()

    home.add_child(instance=Page(title="Only EN", slug="only-en"))

    news = home.add_child(instance=Page(title="News", slug="news"))
    news_it = news.copy_for_translation(it)  # draft: never published
    assert not news_it.live

    private = home.add_child(instance=Page(title="Private", slug="private"))
    PageViewRestriction.objects.create(
        page=private, restriction_type=PageViewRestriction.LOGIN
    )
    return {
        "home": home, "home_it": home_it.specific,
        "about": about, "about_it": about_it.specific,
        "news": news, "private": private,
    }


def _url(page):
    return page.get_full_url()


def test_sitemap_lists_every_locale(site_tree):
    urls = _sitemap()
    for key in ("home", "home_it", "about", "about_it", "news"):
        assert _url(site_tree[key]) in urls, key
    assert any("/only-en/" in loc for loc in urls)


def test_alternates_are_reciprocal_with_x_default(site_tree):
    urls = _sitemap()
    en_url, it_url = _url(site_tree["about"]), _url(site_tree["about_it"])
    expected = {"en": en_url, "it": it_url, "x-default": en_url}
    assert urls[en_url] == expected
    assert urls[it_url] == expected


def test_untranslated_page_has_no_alternates(site_tree):
    urls = _sitemap()
    only_en = next(loc for loc in urls if "/only-en/" in loc)
    assert urls[only_en] == {}


def test_draft_translation_is_not_an_alternate(site_tree):
    urls = _sitemap()
    assert urls[_url(site_tree["news"])] == {}


def test_private_pages_are_excluded(site_tree):
    urls = _sitemap()
    assert _url(site_tree["private"]) not in urls

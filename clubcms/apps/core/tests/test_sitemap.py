"""
/sitemap.xml must render: wagtail.contrib.sitemaps uses the "sitemap.xml"
template shipped by django.contrib.sitemaps (500 TemplateDoesNotExist on
live for at least a month before 2026-10-25).
"""

import pytest
from django.test import Client


@pytest.mark.django_db
def test_sitemap_xml_renders():
    response = Client().get("/sitemap.xml", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert response["Content-Type"].startswith("application/xml")
    assert b"<urlset" in response.content

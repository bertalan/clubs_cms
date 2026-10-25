"""
Multilingual sitemap.

Wagtail's default sitemap only walks the default Site root, i.e. one locale.
This one lists the live, public pages of every translation of the root and
adds reciprocal hreflang alternates (plus x-default) between translations,
using the alternates support of Django's sitemap.xml template.
"""

from collections import defaultdict

from django.conf import settings
from django.db.models import Q
from wagtail.contrib.sitemaps import Sitemap
from wagtail.models import Page


class MultilingualSitemap(Sitemap):
    def __init__(self, request=None):
        super().__init__(request)
        self._alternates = None

    def _pages(self):
        roots = self.get_wagtail_site().root_page.get_translations(inclusive=True)
        in_any_root = Q()
        for root in roots:
            in_any_root |= Q(path__startswith=root.path)
        return Page.objects.filter(in_any_root).live().public().order_by("path")

    def items(self):
        return self._pages().defer_streamfields().specific()

    def _alternates_by_translation_key(self):
        """{translation_key: [{"lang_code", "location"}, ...]} for live pages."""
        if self._alternates is None:
            groups = defaultdict(list)
            for page in self._pages().select_related("locale"):
                groups[page.translation_key].append(
                    {
                        "lang_code": page.locale.language_code,
                        "location": page.get_full_url(self.request),
                    }
                )
            default_lang = settings.LANGUAGE_CODE.split("-")[0]
            self._alternates = {}
            for key, alternates in groups.items():
                if len(alternates) < 2:
                    continue
                alternates.sort(key=lambda a: a["lang_code"])
                default = next(
                    (a for a in alternates if a["lang_code"] == default_lang), None
                )
                if default:
                    alternates = alternates + [
                        {"lang_code": "x-default", "location": default["location"]}
                    ]
                self._alternates[key] = alternates
        return self._alternates

    def _urls(self, page, protocol, domain):
        alternates = self._alternates_by_translation_key()
        urls = []
        last_mods = set()
        for item in self.paginator.page(page).object_list.iterator():
            page_url = item.get_full_url(self.request)
            for url_info in item.get_sitemap_urls(self.request):
                if url_info.get("location") == page_url:
                    url_info = {
                        **url_info,
                        "alternates": alternates.get(item.translation_key, []),
                    }
                urls.append(url_info)
                last_mods.add(url_info.get("lastmod"))
        if last_mods and None not in last_mods:
            self.latest_lastmod = max(last_mods)
        return urls

"""
Blocks with list children must render their items.

Iterating a ListBlock value yields the item values directly; the templates
used ``item.value.title`` (the StreamBlock idiom), so cards, stats, tabs,
accordions, testimonials, pricing plans and table rows rendered empty
until 2026-10-26.
"""

import pytest

from apps.website import blocks as B

CASES = [
    (B.CardsGridBlock, {"title": "T", "cards": [{"title": "CARD-TITLE", "text": "CARD-TEXT"}]},
     ["CARD-TITLE", "CARD-TEXT"]),
    (B.StatsBlock, {"stats": [{"value": "1500+", "label": "STAT-LABEL"}]}, ["1500+", "STAT-LABEL"]),
    (B.CounterUpBlock, {"counters": [{"value": 42, "suffix": "km", "label": "COUNTER-LABEL"}]},
     ["42", "COUNTER-LABEL"]),
    (B.TabsBlock, {"tabs": [{"title": "TAB-TITLE", "content": "<p>TAB-BODY</p>"}]}, ["TAB-TITLE", "TAB-BODY"]),
    (B.AccordionBlock, {"items": [{"title": "ACC-TITLE", "content": "<p>ACC-BODY</p>"}]},
     ["ACC-TITLE", "ACC-BODY"]),
    (B.TestimonialsBlock, {"testimonials": [{"quote": "QUOTE-TEXT", "name": "QUOTE-NAME"}]},
     ["QUOTE-TEXT", "QUOTE-NAME"]),
    (B.PricingTableBlock,
     {"plans": [{"name": "PLAN-NAME", "price": "PLAN-PRICE", "features": ["FEATURE-ONE"]}]},
     ["PLAN-NAME", "PLAN-PRICE", "FEATURE-ONE"]),
    (B.TableBlock, {"headers": ["HEAD-ONE"], "rows": [{"cells": ["CELL-ONE"]}]}, ["HEAD-ONE", "CELL-ONE"]),
]


@pytest.mark.django_db
@pytest.mark.parametrize("block_class, data, expected", CASES, ids=[c[0].__name__ for c in CASES])
def test_list_items_are_rendered(block_class, data, expected):
    block = block_class()
    html = block.render(block.to_python(data))
    for text in expected:
        assert text in html, f"{block_class.__name__}: {text!r} missing"

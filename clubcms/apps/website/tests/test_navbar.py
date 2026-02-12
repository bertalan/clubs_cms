"""
Tests for navbar dropdown/submenu functionality.

Tests: model parent-child relationships, top_level_items filtering.
"""

import pytest
from django.contrib.auth import get_user_model

from apps.website.models.snippets import Navbar, NavbarItem

User = get_user_model()


@pytest.mark.django_db
class TestNavbarItemParentChild:
    """NavbarItem can have children to create dropdown menus."""

    def _create_navbar(self):
        return Navbar.objects.create(name="Test Nav", show_search=True)

    def test_top_level_items_excludes_children(self):
        """top_level_items() returns only items without a parent."""
        nav = self._create_navbar()
        parent_item = NavbarItem.objects.create(
            navbar=nav, label="Events", sort_order=0
        )
        NavbarItem.objects.create(
            navbar=nav, label="Calendar", parent=parent_item, sort_order=1
        )
        NavbarItem.objects.create(
            navbar=nav, label="My Events", parent=parent_item, sort_order=2
        )
        NavbarItem.objects.create(
            navbar=nav, label="Home", sort_order=3
        )

        top_items = nav.top_level_items()
        assert top_items.count() == 2
        labels = list(top_items.values_list("label", flat=True))
        assert "Events" in labels
        assert "Home" in labels
        assert "Calendar" not in labels
        assert "My Events" not in labels

    def test_children_accessible_from_parent(self):
        """Parent item's children are accessible via .children.all()."""
        nav = self._create_navbar()
        parent_item = NavbarItem.objects.create(
            navbar=nav, label="Club", sort_order=0
        )
        child1 = NavbarItem.objects.create(
            navbar=nav, label="Join", parent=parent_item, sort_order=1
        )
        child2 = NavbarItem.objects.create(
            navbar=nav, label="Directory", parent=parent_item, sort_order=2
        )

        children = parent_item.children.all()
        assert children.count() == 2
        assert child1 in children
        assert child2 in children

    def test_item_without_parent_is_top_level(self):
        """Item with parent=None is a top-level item."""
        nav = self._create_navbar()
        item = NavbarItem.objects.create(
            navbar=nav, label="Home", parent=None, sort_order=0
        )
        assert item.parent is None
        assert item in nav.top_level_items()

    def test_deleting_parent_cascades_to_children(self):
        """Deleting a parent item also deletes its children."""
        nav = self._create_navbar()
        parent_item = NavbarItem.objects.create(
            navbar=nav, label="Events", sort_order=0
        )
        NavbarItem.objects.create(
            navbar=nav, label="Calendar", parent=parent_item, sort_order=1
        )
        NavbarItem.objects.create(
            navbar=nav, label="Favs", parent=parent_item, sort_order=2
        )

        assert NavbarItem.objects.filter(navbar=nav).count() == 3
        parent_item.delete()
        assert NavbarItem.objects.filter(navbar=nav).count() == 0

    def test_navbar_str(self):
        """Navbar __str__ returns name."""
        nav = self._create_navbar()
        assert str(nav) == "Test Nav"

    def test_navbar_item_str(self):
        """NavbarItem __str__ returns label."""
        nav = self._create_navbar()
        item = NavbarItem.objects.create(navbar=nav, label="About", sort_order=0)
        assert str(item) == "About"


@pytest.mark.django_db
class TestNavbarDropdownCSS:
    """Verify dropdown CSS exists in theme files."""

    def test_base_css_has_dropdown_styles(self):
        """base.css contains .site-nav__dropdown styles."""
        import os
        from django.conf import settings
        css_path = os.path.join(settings.STATICFILES_DIRS[0], "css", "base.css")
        with open(css_path) as f:
            content = f.read()
        assert ".site-nav__dropdown" in content
        assert ".site-nav__dropdown-menu" in content
        assert ".site-nav__dropdown-toggle" in content

    def test_all_themes_have_dropdown_styles(self):
        """Each of the 6 themes has dropdown-related CSS."""
        import os
        from django.conf import settings
        themes = ["velocity", "heritage", "terra", "zen", "clubs", "tricolore"]
        for theme in themes:
            css_path = os.path.join(
                settings.STATICFILES_DIRS[0], "css", "themes", theme, "main.css"
            )
            with open(css_path) as f:
                content = f.read()
            assert ".site-nav__dropdown" in content, f"{theme} missing dropdown styles"

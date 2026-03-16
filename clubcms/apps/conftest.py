"""
Shared pytest fixtures for the ClubCMS project.

Place this file at ``apps/conftest.py`` so that every test module under
``apps/`` can use these fixtures without explicit imports.

All fixtures that touch the database are implicitly compatible with
``@pytest.mark.django_db`` -- callers must apply that marker on their
own tests (or use ``pytestmark = pytest.mark.django_db`` at module level).
"""

from datetime import date, timedelta

import pytest

from apps.factories import (
    ClubUserFactory,
    ColorSchemeFactory,
    FooterFactory,
    FooterMenuItemFactory,
    FooterSocialLinkFactory,
    NavbarFactory,
    NavbarItemFactory,
    ProductFactory,
)


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def user_factory(db):
    """
    Factory fixture that returns the ``ClubUserFactory`` callable.

    Usage::

        def test_something(user_factory):
            user = user_factory(username="rider1", email="rider1@example.com")
            assert user.pk is not None
    """
    return ClubUserFactory


@pytest.fixture()
def active_member(db):
    """
    A ``ClubUser`` whose membership is valid (expiry 365 days in the future)
    and who owns a full-privilege ``Product``.
    """
    product = ProductFactory(
        name="Full Membership",
        slug="full-membership",
        grants_vote=True,
        grants_upload=True,
        grants_events=True,
        grants_discount=True,
        discount_percent=15,
    )
    user = ClubUserFactory(
        username="active_member",
        first_name="Active",
        last_name="Member",
        membership_date=date.today() - timedelta(days=30),
        membership_expiry=date.today() + timedelta(days=365),
        card_number="CARD-001",
    )
    user.products.add(product)
    return user


@pytest.fixture()
def inactive_user(db):
    """
    A ``ClubUser`` with **no** membership data at all.

    ``inactive_user.is_active_member`` is ``False``.
    """
    return ClubUserFactory(
        username="inactive_user",
        first_name="Inactive",
        last_name="User",
        membership_date=None,
        membership_expiry=None,
        card_number=None,
    )


@pytest.fixture()
def staff_user(db):
    """
    A ``ClubUser`` with ``is_staff=True`` for admin/Wagtail access tests.
    """
    return ClubUserFactory(
        username="staff_user",
        first_name="Staff",
        last_name="Admin",
        is_staff=True,
    )


# ---------------------------------------------------------------------------
# Product fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def product_factory(db):
    """
    Factory fixture that returns the ``ProductFactory`` callable.

    Usage::

        def test_product(product_factory):
            prod = product_factory(name="Gold", price=Decimal("99.00"))
            assert prod.is_active is True
    """
    return ProductFactory


# ---------------------------------------------------------------------------
# Navbar fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def navbar_with_items(db):
    """
    A ``Navbar`` with three ``NavbarItem`` children already attached.

    Returns the ``Navbar`` instance.  Access items via
    ``navbar.items.all()``.
    """
    navbar = NavbarFactory(name="Main Navigation", show_search=True)

    NavbarItemFactory(navbar=navbar, label="Home", link_url="/", sort_order=0)
    NavbarItemFactory(navbar=navbar, label="About", link_url="/about/", sort_order=1)
    NavbarItemFactory(
        navbar=navbar,
        label="Join Us",
        link_url="https://example.com/join",
        open_new_tab=True,
        is_cta=True,
        sort_order=2,
    )

    return navbar

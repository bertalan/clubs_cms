"""
Shared pytest fixtures for the ClubCMS project.

Place this file at ``apps/conftest.py`` so that every test module under
``apps/`` can use these fixtures without explicit imports.

All fixtures that touch the database are implicitly compatible with
``@pytest.mark.django_db`` -- callers must apply that marker on their
own tests (or use ``pytestmark = pytest.mark.django_db`` at module level).
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from apps.website.models.snippets import Navbar, NavbarItem, Product

User = get_user_model()  # members.ClubUser


# ---------------------------------------------------------------------------
# Helpers (internal)
# ---------------------------------------------------------------------------

_user_counter = 0


def _next_username(prefix: str = "user") -> str:
    """Return a unique username for each call within a test session."""
    global _user_counter
    _user_counter += 1
    return f"{prefix}_{_user_counter}"


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def user_factory(db):
    """
    Factory fixture that returns a callable for creating ``ClubUser`` instances.

    Usage::

        def test_something(user_factory):
            user = user_factory(username="rider1", email="rider1@example.com")
            assert user.pk is not None

    Any keyword argument accepted by ``ClubUser`` can be passed; sensible
    defaults are provided for the most common fields.
    """

    def _create(**kwargs):
        defaults = {
            "username": _next_username(),
            "email": "",
            "first_name": "Test",
            "last_name": "User",
            "is_active": True,
        }
        defaults.update(kwargs)

        # Pop password so we can use set_password for proper hashing.
        password = defaults.pop("password", "testpass123")

        # Handle ``email`` default based on username when not explicitly given.
        if not defaults["email"]:
            defaults["email"] = f"{defaults['username']}@example.com"

        user = User(**defaults)
        user.set_password(password)
        user.save()
        return user

    return _create


@pytest.fixture()
def active_member(db, user_factory, product_factory):
    """
    A ``ClubUser`` whose membership is valid (expiry 365 days in the future)
    and who owns a full-privilege ``Product``.

    The user is returned with its related product already attached, so
    ``active_member.is_active_member`` is ``True`` and all ``grants_*``
    properties evaluate to ``True``.
    """
    product = product_factory(
        name="Full Membership",
        slug="full-membership",
        grants_vote=True,
        grants_upload=True,
        grants_events=True,
        grants_discount=True,
        discount_percent=15,
    )
    user = user_factory(
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
def inactive_user(db, user_factory):
    """
    A ``ClubUser`` with **no** membership data at all -- ``membership_expiry``
    is ``None`` and no products are assigned.

    ``inactive_user.is_active_member`` is ``False``.
    """
    return user_factory(
        username="inactive_user",
        first_name="Inactive",
        last_name="User",
        membership_date=None,
        membership_expiry=None,
        card_number=None,
    )


@pytest.fixture()
def staff_user(db, user_factory):
    """
    A ``ClubUser`` with ``is_staff=True`` for admin/Wagtail access tests.
    """
    return user_factory(
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
    Factory fixture that returns a callable for creating ``Product`` snippet
    instances.

    Usage::

        def test_product(product_factory):
            prod = product_factory(name="Gold", price=Decimal("99.00"))
            assert prod.is_active is True
    """

    _counter = 0

    def _create(**kwargs):
        nonlocal _counter
        _counter += 1

        defaults = {
            "name": f"Product {_counter}",
            "slug": f"product-{_counter}",
            "description": "",
            "price": Decimal("50.00"),
            "is_active": True,
            "order": 0,
            "grants_vote": False,
            "grants_upload": False,
            "grants_events": False,
            "grants_discount": False,
            "discount_percent": 0,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)

    return _create


# ---------------------------------------------------------------------------
# Navbar fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def navbar_with_items(db):
    """
    A ``Navbar`` with three ``NavbarItem`` children already attached:

    1. "Home"   -- internal link (``link_url`` as placeholder)
    2. "About"  -- internal link
    3. "Join Us" -- external CTA, opens in a new tab

    Returns the ``Navbar`` instance.  Access items via
    ``navbar.items.all()``.
    """
    navbar = Navbar.objects.create(
        name="Main Navigation",
        logo=None,
        show_search=True,
    )

    NavbarItem.objects.create(
        navbar=navbar,
        label="Home",
        link_url="/",
        open_new_tab=False,
        is_cta=False,
        sort_order=0,
    )
    NavbarItem.objects.create(
        navbar=navbar,
        label="About",
        link_url="/about/",
        open_new_tab=False,
        is_cta=False,
        sort_order=1,
    )
    NavbarItem.objects.create(
        navbar=navbar,
        label="Join Us",
        link_url="https://example.com/join",
        open_new_tab=True,
        is_cta=True,
        sort_order=2,
    )

    return navbar

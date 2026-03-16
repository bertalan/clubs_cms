"""
Factory Boy factories for ClubCMS models.

Usage in tests::

    from apps.factories import ClubUserFactory, ProductFactory

    user = ClubUserFactory(first_name="Mario")
    product = ProductFactory(grants_vote=True, price=Decimal("99.00"))
"""

from datetime import date, timedelta
from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from apps.website.models.snippets import (
    ColorScheme,
    Footer,
    FooterMenuItem,
    FooterSocialLink,
    Navbar,
    NavbarItem,
    Product,
)

User = get_user_model()


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


class ClubUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = "Test"
    last_name = "User"
    is_active = True
    password = factory.PostGeneration(
        lambda obj, create, extracted, **kw: obj.set_password(
            extracted or "testpass123"
        )
    )

    @classmethod
    def _after_postgeneration(cls, instance, create, results=None):
        if create:
            instance.save()


# ---------------------------------------------------------------------------
# Product (membership tier)
# ---------------------------------------------------------------------------


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n}")
    slug = factory.Sequence(lambda n: f"product-{n}")
    description = ""
    price = Decimal("50.00")
    is_active = True
    order = 0
    grants_vote = False
    grants_upload = False
    grants_events = False
    grants_discount = False
    discount_percent = 0


# ---------------------------------------------------------------------------
# ColorScheme
# ---------------------------------------------------------------------------


class ColorSchemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ColorScheme

    name = factory.Sequence(lambda n: f"Scheme {n}")
    primary = "#0F172A"
    secondary = "#F59E0B"
    accent = "#8B5CF6"
    surface = "#F8FAFC"
    surface_alt = "#FFFFFF"
    text_primary = "#111111"
    text_muted = "#666666"
    is_dark_mode = False


# ---------------------------------------------------------------------------
# Navbar + NavbarItem
# ---------------------------------------------------------------------------


class NavbarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Navbar

    name = factory.Sequence(lambda n: f"Navbar {n}")
    logo = None
    show_search = True


class NavbarItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NavbarItem

    navbar = factory.SubFactory(NavbarFactory)
    label = factory.Sequence(lambda n: f"Link {n}")
    link_url = "/"
    open_new_tab = False
    is_cta = False
    sort_order = factory.Sequence(lambda n: n)


# ---------------------------------------------------------------------------
# Footer + children
# ---------------------------------------------------------------------------


class FooterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Footer

    name = factory.Sequence(lambda n: f"Footer {n}")
    description = ""
    copyright_text = ""
    phone = ""
    email = ""
    address = ""


class FooterMenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FooterMenuItem

    footer = factory.SubFactory(FooterFactory)
    label = factory.Sequence(lambda n: f"Menu item {n}")
    link_url = "/"
    sort_order = factory.Sequence(lambda n: n)


class FooterSocialLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FooterSocialLink

    footer = factory.SubFactory(FooterFactory)
    platform = "facebook"
    url = "https://facebook.com/example"
    sort_order = factory.Sequence(lambda n: n)

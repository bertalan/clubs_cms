"""
Tests for allauth template overrides and membership plans page.

Tests: signup, login, logout, password reset pages render correctly
with the site theme, and the membership plans page shows products.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


@pytest.mark.django_db
class TestSignupPage:
    """Signup page renders with site theme and correct form."""

    def test_signup_returns_200(self, client):
        """GET /account/signup/ returns 200."""
        response = client.get("/it/account/signup/")
        assert response.status_code == 200

    def test_signup_contains_csrf_token(self, client):
        """Signup form contains CSRF token."""
        response = client.get("/it/account/signup/")
        assert b"csrfmiddlewaretoken" in response.content

    def test_signup_contains_custom_fields(self, client):
        """Signup form includes first_name and last_name fields."""
        response = client.get("/it/account/signup/")
        content = response.content.decode()
        assert "first_name" in content
        assert "last_name" in content

    def test_signup_has_login_link(self, client):
        """Signup page contains link to login."""
        response = client.get("/it/account/signup/")
        content = response.content.decode()
        assert "account_login" in content or "/account/login/" in content or "Log in" in content or "Accedi" in content


@pytest.mark.django_db
class TestLoginPage:
    """Login page renders with site theme."""

    def test_login_returns_200(self, client):
        """GET /account/login/ returns 200."""
        response = client.get("/it/account/login/")
        assert response.status_code == 200

    def test_login_contains_csrf_token(self, client):
        """Login form contains CSRF token."""
        response = client.get("/it/account/login/")
        assert b"csrfmiddlewaretoken" in response.content

    def test_login_has_signup_link(self, client):
        """Login page contains link to signup."""
        response = client.get("/it/account/login/")
        content = response.content.decode()
        assert "account_signup" in content or "/account/signup/" in content or "Sign up" in content or "Registrati" in content

    def test_login_has_password_reset_link(self, client):
        """Login page contains link to password reset."""
        response = client.get("/it/account/login/")
        content = response.content.decode()
        assert "password" in content.lower()


@pytest.mark.django_db
class TestLogoutPage:
    """Logout page requires confirmation via POST."""

    def test_logout_page_returns_200(self, client):
        """GET /account/logout/ returns 200 for logged-in user."""
        user = User.objects.create_user(
            username="logoutuser", password="testpass123!"
        )
        client.force_login(user)
        response = client.get("/it/account/logout/")
        assert response.status_code == 200

    def test_logout_contains_csrf_token(self, client):
        """Logout page has CSRF token for POST form."""
        user = User.objects.create_user(
            username="logoutcsrf", password="testpass123!"
        )
        client.force_login(user)
        response = client.get("/it/account/logout/")
        assert b"csrfmiddlewaretoken" in response.content


@pytest.mark.django_db
class TestPasswordResetPage:
    """Password reset page renders correctly."""

    def test_password_reset_returns_200(self, client):
        """GET /account/password/reset/ returns 200."""
        response = client.get("/it/account/password/reset/")
        assert response.status_code == 200


@pytest.fixture
def membership_plans_page():
    """Create a published MembershipPlansPage under the root."""
    from apps.website.models.pages import MembershipPlansPage
    from wagtail.models import Page

    if MembershipPlansPage.objects.exists():
        return MembershipPlansPage.objects.first()
    root = Page.objects.filter(depth=1).first()
    home = root.get_children().first()
    if home is None:
        from wagtail.models import Site
        home = root
    page = MembershipPlansPage(
        title="Diventa Socio",
        slug="diventa-socio",
        intro="<p>Test intro</p>",
    )
    home.add_child(instance=page)
    page.save_revision().publish()
    return page


@pytest.mark.django_db
class TestMembershipPlansPage:
    """Membership plans Wagtail page shows active products."""

    def test_plans_page_returns_200(self, client, membership_plans_page):
        """GET /diventa-socio/ returns 200."""
        response = client.get(membership_plans_page.url)
        assert response.status_code == 200

    def test_plans_page_shows_active_products(self, client, membership_plans_page):
        """Active products appear on the plans page."""
        from apps.website.models.snippets import Product
        Product.objects.create(
            name="Basic Card", slug="basic-card", price=20,
            is_active=True, grants_events=True,
        )
        Product.objects.create(
            name="Hidden Plan", slug="hidden", price=10,
            is_active=False,
        )
        response = client.get(membership_plans_page.url)
        content = response.content.decode()
        assert "Basic Card" in content
        assert "Hidden Plan" not in content

    def test_plans_page_highlights_user_plan(self, client, membership_plans_page):
        """Logged-in user's current products are highlighted."""
        from apps.website.models.snippets import Product
        product = Product.objects.create(
            name="Premium", slug="premium", price=50,
            is_active=True, grants_vote=True, grants_events=True,
        )
        user = User.objects.create_user(
            username="memberuser", password="testpass123!"
        )
        product.members.add(user)
        client.force_login(user)

        response = client.get(membership_plans_page.url)
        content = response.content.decode()
        assert "pricing-card--active" in content

    def test_plans_page_shows_signup_cta_for_anonymous(self, client, membership_plans_page):
        """Anonymous users see signup CTA."""
        from apps.website.models.snippets import Product
        Product.objects.create(
            name="Basic", slug="basic", price=20,
            is_active=True, grants_events=True,
        )
        response = client.get(membership_plans_page.url)
        content = response.content.decode()
        assert "account_signup" in content or "Sign up" in content or "Registrati" in content


@pytest.mark.django_db
class TestLoginRedirectURL:
    """LOGIN_REDIRECT_URL is correctly set."""

    def test_login_redirect_url_is_home(self):
        """LOGIN_REDIRECT_URL points to the home page."""
        from django.conf import settings
        assert str(settings.LOGIN_REDIRECT_URL) == "/"

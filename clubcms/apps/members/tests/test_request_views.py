"""
Tests for membership request tracking views:
- request_detail_view (stepper, ownership)
- cancel_request_view (POST-only, ownership, status change)
- card_view context (pending_requests, recent_resolved banners)
"""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

User = get_user_model()


@pytest.mark.django_db
class TestRequestDetailView:
    """Tests for MembersAreaPage.request_detail_view."""

    @pytest.fixture(autouse=True)
    def _setup(self, db):
        from wagtail.models import Page, Site

        from apps.members.models import MembersAreaPage, MembershipRequest
        from apps.website.models.snippets import Product

        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root")
        home = Page.objects.filter(depth=2).first()
        if not home:
            home = Page(title="Test Home", slug="test-home")
            root.add_child(instance=home)
        Site.objects.update_or_create(
            hostname="localhost",
            defaults={"root_page": home, "is_default_site": True},
        )
        self.page = MembersAreaPage(title="Members", slug="members")
        home.add_child(instance=self.page)
        self.page.save_revision().publish()

        self.user = User.objects.create_user(
            username="member1",
            password="testpass123!",
            membership_expiry=date.today() + timedelta(days=365),
        )
        self.other_user = User.objects.create_user(
            username="other1",
            password="testpass123!",
        )
        self.product = Product.objects.create(
            name="Gold Plan", price=100, is_active=True
        )
        self.req_pending = MembershipRequest.objects.create(
            user=self.user, product=self.product, status="pending", notes="Please"
        )
        self.req_approved = MembershipRequest.objects.create(
            user=self.user,
            product=self.product,
            status="approved",
            processed_at=timezone.now(),
        )
        self.req_rejected = MembershipRequest.objects.create(
            user=self.user,
            product=self.product,
            status="rejected",
            admin_notes="Incomplete docs",
            processed_at=timezone.now(),
        )
        self.req_cancelled = MembershipRequest.objects.create(
            user=self.user, product=self.product, status="cancelled"
        )

    def _url(self, pk):
        return self.page.url + self.page.reverse_subpage(
            "request_detail", kwargs={"pk": pk}
        )

    def test_anonymous_redirected(self, client):
        resp = client.get(self._url(self.req_pending.pk))
        assert resp.status_code == 302
        assert "login" in resp.url or "account" in resp.url

    def test_owner_gets_200(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_pending.pk))
        assert resp.status_code == 200

    def test_non_owner_gets_404(self, client):
        client.force_login(self.other_user)
        resp = client.get(self._url(self.req_pending.pk))
        assert resp.status_code == 404

    def test_nonexistent_pk_gets_404(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(99999))
        assert resp.status_code == 404

    def test_pending_stepper_has_3_steps(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_pending.pk))
        steps = resp.context["steps"]
        assert len(steps) == 3
        assert steps[0]["done"] is True  # Submitted
        assert steps[1]["done"] is False  # Under Review
        assert steps[2]["done"] is False  # Decision

    def test_approved_stepper_all_done(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_approved.pk))
        steps = resp.context["steps"]
        assert len(steps) == 3
        assert all(s["done"] for s in steps)
        assert "Approved" in steps[2]["label"] or "Approv" in str(steps[2]["label"])

    def test_rejected_stepper(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_rejected.pk))
        steps = resp.context["steps"]
        assert len(steps) == 3
        assert steps[2]["done"] is True

    def test_cancelled_stepper(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_cancelled.pk))
        steps = resp.context["steps"]
        assert len(steps) == 3
        assert steps[2]["done"] is True

    def test_context_contains_membership_req(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_pending.pk))
        assert resp.context["membership_req"].pk == self.req_pending.pk


@pytest.mark.django_db
class TestCancelRequestView:
    """Tests for MembersAreaPage.cancel_request_view."""

    @pytest.fixture(autouse=True)
    def _setup(self, db):
        from wagtail.models import Page, Site

        from apps.members.models import MembersAreaPage, MembershipRequest
        from apps.website.models.snippets import Product

        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root")
        home = Page.objects.filter(depth=2).first()
        if not home:
            home = Page(title="Test Home", slug="test-home")
            root.add_child(instance=home)
        Site.objects.update_or_create(
            hostname="localhost",
            defaults={"root_page": home, "is_default_site": True},
        )
        self.page = MembersAreaPage(title="Members", slug="members")
        home.add_child(instance=self.page)
        self.page.save_revision().publish()

        self.user = User.objects.create_user(
            username="canceller",
            password="testpass123!",
            membership_expiry=date.today() + timedelta(days=365),
        )
        self.other_user = User.objects.create_user(
            username="other_cancel",
            password="testpass123!",
        )
        self.product = Product.objects.create(
            name="Silver Plan", price=50, is_active=True
        )
        self.req_pending = MembershipRequest.objects.create(
            user=self.user, product=self.product, status="pending"
        )
        self.req_approved = MembershipRequest.objects.create(
            user=self.user, product=self.product, status="approved"
        )

    def _url(self, pk):
        return self.page.url + self.page.reverse_subpage(
            "cancel_request", kwargs={"pk": pk}
        )

    def test_anonymous_redirected(self, client):
        resp = client.post(self._url(self.req_pending.pk))
        assert resp.status_code == 302
        assert "login" in resp.url or "account" in resp.url

    def test_get_returns_404(self, client):
        client.force_login(self.user)
        resp = client.get(self._url(self.req_pending.pk))
        assert resp.status_code == 404

    def test_post_cancels_pending(self, client):
        from apps.members.models import MembershipRequest

        client.force_login(self.user)
        resp = client.post(self._url(self.req_pending.pk))
        assert resp.status_code == 302
        self.req_pending.refresh_from_db()
        assert self.req_pending.status == "cancelled"

    def test_post_non_pending_returns_404(self, client):
        client.force_login(self.user)
        resp = client.post(self._url(self.req_approved.pk))
        assert resp.status_code == 404

    def test_non_owner_returns_404(self, client):
        client.force_login(self.other_user)
        resp = client.post(self._url(self.req_pending.pk))
        assert resp.status_code == 404

    def test_nonexistent_pk_returns_404(self, client):
        client.force_login(self.user)
        resp = client.post(self._url(99999))
        assert resp.status_code == 404

    def test_redirect_to_membership_requests(self, client):
        client.force_login(self.user)
        resp = client.post(self._url(self.req_pending.pk))
        assert resp.status_code == 302
        assert "membership-requests" in resp.url


@pytest.mark.django_db
class TestCardViewRequestBanners:
    """Tests for pending/resolved request banners in card_view context."""

    @pytest.fixture(autouse=True)
    def _setup(self, db):
        from wagtail.models import Page, Site

        from apps.members.models import MembersAreaPage, MembershipRequest
        from apps.website.models.snippets import Product

        root = Page.objects.filter(depth=1).first()
        if not root:
            root = Page.add_root(title="Root")
        home = Page.objects.filter(depth=2).first()
        if not home:
            home = Page(title="Test Home", slug="test-home")
            root.add_child(instance=home)
        Site.objects.update_or_create(
            hostname="localhost",
            defaults={"root_page": home, "is_default_site": True},
        )
        self.page = MembersAreaPage(title="Members", slug="members")
        home.add_child(instance=self.page)
        self.page.save_revision().publish()

        self.user = User.objects.create_user(
            username="carduser",
            password="testpass123!",
            membership_expiry=date.today() + timedelta(days=365),
        )
        self.product = Product.objects.create(
            name="Basic Plan", price=25, is_active=True
        )

    def _url(self):
        return self.page.url + self.page.reverse_subpage("card")

    def test_pending_requests_in_context(self, client):
        from apps.members.models import MembershipRequest

        MembershipRequest.objects.create(
            user=self.user, product=self.product, status="pending"
        )
        client.force_login(self.user)
        resp = client.get(self._url())
        assert resp.status_code == 200
        assert len(resp.context["pending_requests"]) == 1

    def test_no_pending_requests(self, client):
        client.force_login(self.user)
        resp = client.get(self._url())
        assert resp.status_code == 200
        assert len(resp.context["pending_requests"]) == 0

    def test_recent_resolved_in_context(self, client):
        from apps.members.models import MembershipRequest

        MembershipRequest.objects.create(
            user=self.user,
            product=self.product,
            status="approved",
            processed_at=timezone.now(),
        )
        client.force_login(self.user)
        resp = client.get(self._url())
        assert len(resp.context["recent_resolved"]) == 1

    def test_old_resolved_not_in_context(self, client):
        from apps.members.models import MembershipRequest

        req = MembershipRequest.objects.create(
            user=self.user,
            product=self.product,
            status="approved",
            processed_at=timezone.now() - timedelta(days=60),
        )
        client.force_login(self.user)
        resp = client.get(self._url())
        assert len(resp.context["recent_resolved"]) == 0

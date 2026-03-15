"""
T14 + T15 — Test moderazione e admin ViewSets.

Verifica:
- Comment, Activity, Reaction ViewSets registrati in Wagtail admin
- Moderazione commenti: approve/reject
- ViewSets hanno configurazione corretta
"""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils import timezone

from apps.core.admin import activity_viewset, comment_viewset, reaction_viewset
from apps.core.models import Activity, Comment, Reaction
from apps.members.models import ClubUser


class TestViewSetsConfiguration(TestCase):
    """ViewSets must have correct configuration."""

    def test_comment_viewset_model(self):
        self.assertEqual(comment_viewset.model, Comment)

    def test_comment_viewset_icon(self):
        self.assertEqual(comment_viewset.icon, "comment")

    def test_activity_viewset_model(self):
        self.assertEqual(activity_viewset.model, Activity)

    def test_activity_viewset_icon(self):
        self.assertEqual(activity_viewset.icon, "history")

    def test_reaction_viewset_model(self):
        self.assertEqual(reaction_viewset.model, Reaction)

    def test_reaction_viewset_icon(self):
        self.assertEqual(reaction_viewset.icon, "heart")

    def test_all_viewsets_added_to_menu(self):
        self.assertTrue(comment_viewset.add_to_admin_menu)
        self.assertTrue(activity_viewset.add_to_admin_menu)
        self.assertTrue(reaction_viewset.add_to_admin_menu)


class TestWagtailHooksRegistered(TestCase):
    """ViewSets must be registered via hooks."""

    def test_hooks_registered(self):
        from wagtail import hooks as wagtail_hooks

        registered = wagtail_hooks.get_hooks("register_admin_viewset")
        viewsets = [fn() for fn in registered]
        viewset_classes = [
            vs.__class__.__name__ for vs in viewsets
            if hasattr(vs, "model")
        ]
        self.assertIn("CommentViewSet", viewset_classes)
        self.assertIn("ActivityViewSet", viewset_classes)
        self.assertIn("ReactionViewSet", viewset_classes)


@pytest.mark.django_db
class TestCommentModeration(TestCase):
    """Comment moderation workflow: pending → approved/rejected."""

    @classmethod
    def setUpTestData(cls):
        cls.user = ClubUser.objects.create_user(
            username="user_mod", email="umod@test.com", password="testpass123"
        )
        cls.admin = ClubUser.objects.create_user(
            username="admin_mod", email="amod@test.com", password="testpass123",
            is_staff=True, is_superuser=True,
        )
        cls.ct = ContentType.objects.get_for_model(ClubUser)

    def test_comment_starts_pending(self):
        c = Comment.objects.create(
            user=self.user, content="Test",
            content_type=self.ct, object_id=self.user.pk,
        )
        self.assertEqual(c.moderation_status, "pending")

    def test_approve_comment(self):
        c = Comment.objects.create(
            user=self.user, content="Approve me",
            content_type=self.ct, object_id=self.user.pk,
        )
        c.moderation_status = "approved"
        c.moderated_by = self.admin
        c.save()
        c.refresh_from_db()
        self.assertEqual(c.moderation_status, "approved")
        self.assertEqual(c.moderated_by, self.admin)

    def test_reject_comment(self):
        c = Comment.objects.create(
            user=self.user, content="Reject me",
            content_type=self.ct, object_id=self.user.pk,
        )
        c.moderation_status = "rejected"
        c.moderated_by = self.admin
        c.save()
        c.refresh_from_db()
        self.assertEqual(c.moderation_status, "rejected")

    def test_filter_pending_comments(self):
        Comment.objects.create(
            user=self.user, content="Pending",
            content_type=self.ct, object_id=self.user.pk,
        )
        Comment.objects.create(
            user=self.user, content="Approved",
            content_type=self.ct, object_id=self.user.pk,
            moderation_status="approved",
        )
        pending = Comment.objects.filter(moderation_status="pending")
        self.assertEqual(pending.count(), 1)
        self.assertEqual(pending.first().content, "Pending")


@pytest.mark.django_db
class TestMembersViewSetExists(TestCase):
    """Members ViewSet must be registered."""

    def _get_registered_model_names(self):
        from wagtail import hooks as wagtail_hooks

        registered = wagtail_hooks.get_hooks("register_admin_viewset")
        viewsets = [fn() for fn in registered]
        return [
            vs.model.__name__
            for vs in viewsets
            if hasattr(vs, "model") and hasattr(vs.model, "__name__")
        ]

    def test_clubuser_viewset_registered(self):
        self.assertIn("ClubUser", self._get_registered_model_names())

    def test_membership_request_viewset_registered(self):
        self.assertIn("MembershipRequest", self._get_registered_model_names())

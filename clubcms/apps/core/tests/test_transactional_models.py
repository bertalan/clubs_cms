"""
T13 — Test Activity, Reaction, Comment models.

Verifica modelli transazionali: creazione, unique constraint, threading, moderation.
"""

import pytest
from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError
from django.test import TestCase

from apps.core.models import Activity, Comment, Reaction
from apps.members.models import ClubUser


@pytest.mark.django_db
class TestActivityModel(TestCase):
    """Activity log model tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = ClubUser.objects.create_user(
            username="actor", email="actor@test.com", password="testpass123"
        )

    def test_create_activity(self):
        act = Activity.objects.create(
            user=self.user,
            action="login",
            target_title="Dashboard",
        )
        self.assertEqual(act.action, "login")
        self.assertIsNotNone(act.created_at)

    def test_activity_with_generic_target(self):
        ct = ContentType.objects.get_for_model(ClubUser)
        act = Activity.objects.create(
            user=self.user,
            action="profile_update",
            target_content_type=ct,
            target_id=self.user.pk,
            target_title=self.user.username,
        )
        self.assertEqual(act.target, self.user)

    def test_activity_ordering(self):
        Activity.objects.create(user=self.user, action="login", target_title="First")
        Activity.objects.create(user=self.user, action="upload", target_title="Second")
        activities = list(Activity.objects.filter(user=self.user))
        self.assertEqual(activities[0].target_title, "Second")

    def test_activity_str(self):
        act = Activity.objects.create(
            user=self.user, action="login", target_title="Test"
        )
        s = str(act)
        self.assertIn("Test", s)

    def test_action_choices(self):
        valid_actions = [c[0] for c in Activity.ACTION_CHOICES]
        self.assertIn("upload", valid_actions)
        self.assertIn("comment", valid_actions)
        self.assertIn("reaction", valid_actions)


@pytest.mark.django_db
class TestReactionModel(TestCase):
    """Reaction model tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = ClubUser.objects.create_user(
            username="liker", email="liker@test.com", password="testpass123"
        )
        cls.user2 = ClubUser.objects.create_user(
            username="liker2", email="liker2@test.com", password="testpass123"
        )
        cls.ct = ContentType.objects.get_for_model(ClubUser)

    def test_create_reaction(self):
        r = Reaction.objects.create(
            user=self.user,
            reaction_type="like",
            content_type=self.ct,
            object_id=self.user2.pk,
        )
        self.assertEqual(r.reaction_type, "like")
        self.assertEqual(r.content_object, self.user2)

    def test_unique_constraint(self):
        Reaction.objects.create(
            user=self.user,
            reaction_type="like",
            content_type=self.ct,
            object_id=self.user2.pk,
        )
        with self.assertRaises(IntegrityError):
            Reaction.objects.create(
                user=self.user,
                reaction_type="love",
                content_type=self.ct,
                object_id=self.user2.pk,
            )

    def test_different_users_can_react(self):
        Reaction.objects.create(
            user=self.user,
            content_type=self.ct,
            object_id=self.user2.pk,
        )
        r2 = Reaction.objects.create(
            user=self.user2,
            content_type=self.ct,
            object_id=self.user.pk,
        )
        self.assertEqual(Reaction.objects.count(), 2)


@pytest.mark.django_db
class TestCommentModel(TestCase):
    """Comment model tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = ClubUser.objects.create_user(
            username="commenter", email="comm@test.com", password="testpass123"
        )
        cls.ct = ContentType.objects.get_for_model(ClubUser)

    def test_create_comment(self):
        c = Comment.objects.create(
            user=self.user,
            content="Great event!",
            content_type=self.ct,
            object_id=self.user.pk,
        )
        self.assertEqual(c.moderation_status, "pending")
        self.assertTrue(c.is_reply is False)

    def test_reply_threading(self):
        parent = Comment.objects.create(
            user=self.user,
            content="Parent comment",
            content_type=self.ct,
            object_id=self.user.pk,
        )
        reply = Comment.objects.create(
            user=self.user,
            content="Reply comment",
            content_type=self.ct,
            object_id=self.user.pk,
            parent=parent,
        )
        self.assertTrue(reply.is_reply)
        self.assertEqual(reply.parent, parent)
        self.assertEqual(parent.replies.count(), 1)

    def test_moderation_status_choices(self):
        c = Comment.objects.create(
            user=self.user,
            content="Test",
            content_type=self.ct,
            object_id=self.user.pk,
            moderation_status="approved",
        )
        self.assertEqual(c.moderation_status, "approved")

    def test_comment_ordering_chronological(self):
        c1 = Comment.objects.create(
            user=self.user, content="First",
            content_type=self.ct, object_id=self.user.pk,
        )
        c2 = Comment.objects.create(
            user=self.user, content="Second",
            content_type=self.ct, object_id=self.user.pk,
        )
        comments = list(Comment.objects.all())
        self.assertEqual(comments[0].content, "First")

    def test_str_representation(self):
        c = Comment.objects.create(
            user=self.user, content="Test",
            content_type=self.ct, object_id=self.user.pk,
        )
        s = str(c)
        self.assertIn("Comment", s)

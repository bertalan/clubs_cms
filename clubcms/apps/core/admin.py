"""
Wagtail admin ViewSets for transactional models:
Comment moderation, Activity log, Photo moderation.
"""

from django.utils.translation import gettext_lazy as _
from wagtail.admin.viewsets.model import ModelViewSet

from apps.core.models import Activity, Comment, Reaction


# ---------------------------------------------------------------------------
# Comment Moderation ViewSet
# ---------------------------------------------------------------------------


class CommentViewSet(ModelViewSet):
    """Admin moderation queue for user comments."""

    model = Comment
    icon = "comment"
    menu_label = _("Comments")
    menu_order = 300
    add_to_admin_menu = True
    form_fields = ["user", "content", "moderation_status", "moderated_by"]
    list_display = [
        "user",
        "content",
        "moderation_status",
        "created_at",
    ]
    list_filter = ["moderation_status"]
    search_fields = ["content", "user__username"]
    ordering = ["-created_at"]


comment_viewset = CommentViewSet("comments")


# ---------------------------------------------------------------------------
# Activity Log ViewSet
# ---------------------------------------------------------------------------


class ActivityViewSet(ModelViewSet):
    """Admin view of user activity log (read-only audit trail)."""

    model = Activity
    icon = "history"
    menu_label = _("Activity log")
    menu_order = 310
    add_to_admin_menu = True
    form_fields = ["user", "action", "target_title", "target_url"]
    list_display = [
        "user",
        "action",
        "target_title",
        "created_at",
    ]
    list_filter = ["action"]
    search_fields = ["target_title", "user__username"]
    ordering = ["-created_at"]


activity_viewset = ActivityViewSet("activities")


# ---------------------------------------------------------------------------
# Reaction ViewSet
# ---------------------------------------------------------------------------


class ReactionViewSet(ModelViewSet):
    """Admin view of user reactions."""

    model = Reaction
    icon = "heart"
    menu_label = _("Reactions")
    menu_order = 320
    add_to_admin_menu = True
    form_fields = ["user", "reaction_type"]
    list_display = [
        "user",
        "reaction_type",
        "created_at",
    ]
    list_filter = ["reaction_type"]
    ordering = ["-created_at"]


reaction_viewset = ReactionViewSet("reactions")

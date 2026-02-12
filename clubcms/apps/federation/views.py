"""
Frontend views for the federation app.

All views require login. Interest and comment actions require
active membership.
"""

import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, View

from apps.federation.models import (
    ExternalEvent,
    ExternalEventComment,
    ExternalEventInterest,
)

logger = logging.getLogger(__name__)


def _is_active_member(user):
    """Check if user is an active club member."""
    return getattr(user, "is_active_member", False)


class ExternalEventsListView(LoginRequiredMixin, ListView):
    """
    List of approved, visible external events from partner clubs.

    Template: ``federation/external_events_list.html``
    URL: ``/eventi/partner/``
    """

    model = ExternalEvent
    template_name = "federation/external_events_list.html"
    context_object_name = "events"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            ExternalEvent.objects.filter(
                is_approved=True,
                is_hidden=False,
                start_date__gte=timezone.now(),
            )
            .select_related("source_club")
            .order_by("start_date")
        )

        # Optional filtering by club
        club_code = self.request.GET.get("club")
        if club_code:
            qs = qs.filter(source_club__short_code=club_code)

        # Optional search
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(event_name__icontains=search)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from apps.federation.models import FederatedClub

        context["partner_clubs"] = FederatedClub.objects.filter(
            is_active=True, is_approved=True
        ).order_by("name")
        context["selected_club"] = self.request.GET.get("club", "")
        context["search_query"] = self.request.GET.get("q", "")
        return context


class ExternalEventDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for a single external event.

    Template: ``federation/external_event_detail.html``
    URL: ``/eventi/partner/<club_code>/<event_id>/``
    """

    model = ExternalEvent
    template_name = "federation/external_event_detail.html"
    context_object_name = "event"

    def get_object(self, queryset=None):
        return get_object_or_404(
            ExternalEvent.objects.select_related("source_club"),
            source_club__short_code=self.kwargs["club_code"],
            pk=self.kwargs["event_id"],
            is_approved=True,
            is_hidden=False,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object
        user = self.request.user

        # User's current interest
        context["user_interest"] = None
        if user.is_authenticated:
            try:
                context["user_interest"] = ExternalEventInterest.objects.get(
                    user=user, external_event=event
                )
            except ExternalEventInterest.DoesNotExist:
                pass

        # Comments (non-deleted)
        context["comments"] = (
            event.comments.filter(is_deleted=False)
            .select_related("user")
            .order_by("created_at")
        )

        # Interest counts
        context["interest_counts"] = {
            "interested": event.interests.filter(interest_level="interested").count(),
            "maybe": event.interests.filter(interest_level="maybe").count(),
            "going": event.interests.filter(interest_level="going").count(),
        }

        context["is_active_member"] = _is_active_member(user)

        return context


class SetInterestView(LoginRequiredMixin, View):
    """
    POST-only view to create or update interest in an external event.

    Requires active membership.

    POST params:
        interest_level: one of 'interested', 'maybe', 'going', 'remove'
    """

    http_method_names = ["post"]

    def post(self, request, club_code, event_id):
        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        event = get_object_or_404(
            ExternalEvent,
            source_club__short_code=club_code,
            pk=event_id,
            is_approved=True,
        )

        interest_level = request.POST.get("interest_level", "")

        if interest_level == "remove":
            ExternalEventInterest.objects.filter(
                user=request.user, external_event=event
            ).delete()
        elif interest_level in ("interested", "maybe", "going"):
            ExternalEventInterest.objects.update_or_create(
                user=request.user,
                external_event=event,
                defaults={"interest_level": interest_level},
            )
        else:
            return HttpResponseForbidden("Invalid interest level")

        return HttpResponseRedirect(
            reverse(
                "federation_frontend:detail",
                kwargs={"club_code": club_code, "event_id": event_id},
            )
        )


class AddCommentView(LoginRequiredMixin, View):
    """
    POST-only view to add a comment on an external event.

    Requires active membership. Comments are local-only and never
    shared with the partner club.

    POST params:
        content: comment text
    """

    http_method_names = ["post"]

    def post(self, request, club_code, event_id):
        if not _is_active_member(request.user):
            return HttpResponseForbidden("Active membership required")

        event = get_object_or_404(
            ExternalEvent,
            source_club__short_code=club_code,
            pk=event_id,
            is_approved=True,
        )

        content = request.POST.get("content", "").strip()
        if not content:
            return HttpResponseRedirect(
                reverse(
                    "federation_frontend:detail",
                    kwargs={"club_code": club_code, "event_id": event_id},
                )
            )

        # Limit comment length
        content = content[:2000]

        ExternalEventComment.objects.create(
            user=request.user,
            external_event=event,
            content=content,
        )

        # Send notification to other commenters
        try:
            from apps.notifications.services import create_notification

            other_commenters = (
                ExternalEventComment.objects.filter(
                    external_event=event, is_deleted=False
                )
                .exclude(user=request.user)
                .values_list("user", flat=True)
                .distinct()
            )

            from django.contrib.auth import get_user_model

            User = get_user_model()
            recipients = User.objects.filter(pk__in=other_commenters)

            if recipients.exists():
                display_name = request.user.get_visible_name()
                create_notification(
                    notification_type="partner_event_comment",
                    title=f"New comment on {event.event_name}",
                    body=f"{display_name} commented on the partner event '{event.event_name}'",
                    url=reverse(
                        "federation_frontend:detail",
                        kwargs={"club_code": club_code, "event_id": str(event_id)},
                    ),
                    recipients=recipients,
                    content_object=event,
                )
        except Exception:
            logger.exception("Failed to send comment notification")

        return HttpResponseRedirect(
            reverse(
                "federation_frontend:detail",
                kwargs={"club_code": club_code, "event_id": event_id},
            )
        )


class DeleteCommentView(LoginRequiredMixin, View):
    """
    POST-only view to soft-delete a user's own comment.

    POST params:
        comment_id: UUID of the comment to delete
    """

    http_method_names = ["post"]

    def post(self, request, club_code, event_id):
        comment_id = request.POST.get("comment_id", "")

        comment = get_object_or_404(
            ExternalEventComment,
            pk=comment_id,
            user=request.user,
            external_event__source_club__short_code=club_code,
            external_event__pk=event_id,
        )

        comment.is_deleted = True
        comment.save(update_fields=["is_deleted"])

        return HttpResponseRedirect(
            reverse(
                "federation_frontend:detail",
                kwargs={"club_code": club_code, "event_id": event_id},
            )
        )

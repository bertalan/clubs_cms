"""
Wagtail hooks for the members app.

Registers the ClubUser and MembershipRequest ModelViewSets with the Wagtail admin.
"""

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from wagtail import hooks
from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin

from apps.members.admin import clubuser_viewset, membership_request_viewset
from apps.members.models import ClubUser, MembershipRequest


@hooks.register("register_admin_viewset")
def register_clubuser_viewset():
    return clubuser_viewset


@hooks.register("register_admin_viewset")
def register_membership_request_viewset():
    return membership_request_viewset


# ---------------------------------------------------------------------------
# Custom Admin Views for Card Actions
# ---------------------------------------------------------------------------


def _user_edit_redirect(user_id):
    """Helper to redirect to user edit page with membership tab."""
    return HttpResponseRedirect(
        reverse("clubusers:edit", args=[user_id]) + "#tab-iscrizione"
    )


@require_POST
def issue_card_view(request, user_id):
    """Admin action to issue a membership card."""
    user = get_object_or_404(ClubUser, pk=user_id)
    force_new = request.POST.get("force_new") == "1"
    
    if user.issue_card(force_new=force_new):
        messages.success(
            request,
            _("Card issued successfully: %(card)s") % {"card": user.card_number}
        )
    else:
        messages.warning(
            request,
            _("User already has an active card: %(card)s") % {"card": user.card_number}
        )
    
    return _user_edit_redirect(user_id)


@require_POST
def renew_card_view(request, user_id):
    """Admin action to renew a membership card."""
    user = get_object_or_404(ClubUser, pk=user_id)
    
    if user.renew_card():
        messages.success(
            request,
            _("Card renewed until %(expiry)s") % {"expiry": user.membership_expiry}
        )
    else:
        messages.error(
            request,
            _("Cannot renew: user has no card number.")
        )
    
    return _user_edit_redirect(user_id)


@require_POST
def suspend_card_view(request, user_id):
    """Admin action to suspend a membership card temporarily."""
    user = get_object_or_404(ClubUser, pk=user_id)
    reason = request.POST.get("reason", "")
    
    if not user.card_number:
        messages.warning(request, _("This user does not have a card to suspend."))
    elif user.card_status == "suspended":
        messages.warning(request, _("This card is already suspended."))
    elif user.card_status == "terminated":
        messages.warning(request, _("Cannot suspend a terminated card."))
    else:
        user.card_status = "suspended"
        user.card_status_reason = reason
        user.card_status_changed = timezone.now()
        user.save(update_fields=["card_status", "card_status_reason", "card_status_changed"])
        messages.success(
            request,
            _("Card %(card)s has been suspended.") % {"card": user.card_number}
        )
    
    return _user_edit_redirect(user_id)


@require_POST
def reactivate_card_view(request, user_id):
    """Admin action to reactivate a suspended membership card."""
    user = get_object_or_404(ClubUser, pk=user_id)
    
    if not user.card_number:
        messages.warning(request, _("This user does not have a card."))
    elif user.card_status == "active":
        messages.warning(request, _("This card is already active."))
    elif user.card_status == "terminated":
        messages.warning(request, _("Cannot reactivate a terminated card. Issue a new card instead."))
    else:
        user.card_status = "active"
        user.card_status_reason = ""
        user.card_status_changed = timezone.now()
        user.save(update_fields=["card_status", "card_status_reason", "card_status_changed"])
        messages.success(
            request,
            _("Card %(card)s has been reactivated.") % {"card": user.card_number}
        )
    
    return _user_edit_redirect(user_id)


@require_POST
def terminate_card_view(request, user_id):
    """Admin action to terminate a membership card permanently."""
    user = get_object_or_404(ClubUser, pk=user_id)
    reason = request.POST.get("reason", "")
    
    if not user.card_number:
        messages.warning(request, _("This user does not have a card to terminate."))
    elif user.card_status == "terminated":
        messages.warning(request, _("This card is already terminated."))
    else:
        user.card_status = "terminated"
        user.card_status_reason = reason
        user.card_status_changed = timezone.now()
        user.save(update_fields=["card_status", "card_status_reason", "card_status_changed"])
        messages.success(
            request,
            _("Card %(card)s has been terminated.") % {"card": user.card_number}
        )
    
    return _user_edit_redirect(user_id)


@require_POST
def approve_request_view(request, request_id):
    """Admin action to approve a membership request."""
    membership_request = get_object_or_404(MembershipRequest, pk=request_id)
    
    if membership_request.approve(admin_user=request.user):
        messages.success(
            request,
            _("Request approved. Card: %(card)s") % {"card": membership_request.user.card_number}
        )
    else:
        messages.warning(
            request,
            _("Request could not be approved (status: %(status)s)") % {
                "status": membership_request.get_status_display()
            }
        )
    
    return HttpResponseRedirect(
        reverse("membership_requests:edit", args=[request_id])
    )


@require_POST
def reject_request_view(request, request_id):
    """Admin action to reject a membership request."""
    membership_request = get_object_or_404(MembershipRequest, pk=request_id)
    reason = request.POST.get("reason", "")
    
    if membership_request.reject(admin_user=request.user, reason=reason):
        messages.success(request, _("Request rejected."))
    else:
        messages.warning(
            request,
            _("Request could not be rejected (status: %(status)s)") % {
                "status": membership_request.get_status_display()
            }
        )
    
    return HttpResponseRedirect(
        reverse("membership_requests:edit", args=[request_id])
    )


@hooks.register("register_admin_urls")
def register_card_action_urls():
    return [
        path(
            "members/issue-card/<int:user_id>/",
            issue_card_view,
            name="members_issue_card"
        ),
        path(
            "members/renew-card/<int:user_id>/",
            renew_card_view,
            name="members_renew_card"
        ),
        path(
            "members/suspend-card/<int:user_id>/",
            suspend_card_view,
            name="members_suspend_card"
        ),
        path(
            "members/reactivate-card/<int:user_id>/",
            reactivate_card_view,
            name="members_reactivate_card"
        ),
        path(
            "members/terminate-card/<int:user_id>/",
            terminate_card_view,
            name="members_terminate_card"
        ),
        path(
            "members/approve-request/<int:request_id>/",
            approve_request_view,
            name="members_approve_request"
        ),
        path(
            "members/reject-request/<int:request_id>/",
            reject_request_view,
            name="members_reject_request"
        ),
    ]

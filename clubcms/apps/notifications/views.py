"""
Notification views.

Handles unsubscribe flow (token-based, no login), push subscription
management, notification history, and mark-read AJAX.
"""

import json
import logging
from urllib.parse import urlparse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import ListView, TemplateView

from .models import NOTIFICATION_PREFERENCE_MAP, NotificationQueue, PushSubscription
from .services import mask_email, verify_unsubscribe_token

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Unsubscribe (no login required, token-based)
# ---------------------------------------------------------------------------


@method_decorator(csrf_protect, name="post")
class UnsubscribeView(TemplateView):
    """
    GET: Show confirmation page with masked email.
    POST: Process unsubscribe and redirect to success.
    """

    template_name = "notifications/unsubscribe.html"

    def _resolve_token(self):
        token = self.kwargs.get("token", "")
        result = verify_unsubscribe_token(token)
        return result

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        result = self._resolve_token()
        if result is not None:
            user, notification_type = result
            ctx["valid"] = True
            ctx["masked_email"] = mask_email(user.email)
            ctx["notification_type"] = notification_type
            ctx["notification_type_display"] = dict(
                NOTIFICATION_PREFERENCE_MAP
            ).get(notification_type, notification_type)
        else:
            ctx["valid"] = False
        return ctx

    def post(self, request, *args, **kwargs):
        result = self._resolve_token()
        if result is None:
            return self.get(request, *args, **kwargs)

        user, notification_type = result
        pref_field = NOTIFICATION_PREFERENCE_MAP.get(notification_type)
        if pref_field and hasattr(user, pref_field):
            setattr(user, pref_field, False)
            user.save(update_fields=[pref_field])
            logger.info(
                "User %s unsubscribed from %s via token",
                user.pk,
                notification_type,
            )

        return redirect("notifications:unsubscribe_success")


class UnsubscribeSuccessView(TemplateView):
    """Simple success page after unsubscribe."""

    template_name = "notifications/unsubscribe_success.html"


# ---------------------------------------------------------------------------
# Push subscription management (login required, JSON)
# ---------------------------------------------------------------------------


class PushSubscribeView(LoginRequiredMixin, View):
    """
    POST: Register a new push subscription.
    Expects JSON body with endpoint, keys.p256dh, keys.auth.
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse(
                {"error": _("Invalid JSON body")}, status=400
            )

        endpoint = data.get("endpoint", "")
        keys = data.get("keys", {})
        p256dh = keys.get("p256dh", "")
        auth = keys.get("auth", "")

        # Validate endpoint URL
        if not endpoint:
            return JsonResponse(
                {"error": _("Endpoint is required")}, status=400
            )

        parsed = urlparse(endpoint)
        if parsed.scheme not in ("https",):
            return JsonResponse(
                {"error": _("Endpoint must use HTTPS")}, status=400
            )

        if not p256dh or not auth:
            return JsonResponse(
                {"error": _("Encryption keys are required")}, status=400
            )

        sub, created = PushSubscription.objects.update_or_create(
            user=request.user,
            endpoint=endpoint,
            defaults={
                "p256dh_key": p256dh,
                "auth_key": auth,
                "is_active": True,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        )

        return JsonResponse(
            {
                "ok": True,
                "created": created,
                "subscription_id": sub.pk,
            }
        )


class PushUnsubscribeView(LoginRequiredMixin, View):
    """
    POST: Remove a push subscription.
    Expects JSON body with endpoint.
    """

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse(
                {"error": _("Invalid JSON body")}, status=400
            )

        endpoint = data.get("endpoint", "")
        if not endpoint:
            return JsonResponse(
                {"error": _("Endpoint is required")}, status=400
            )

        deleted_count, _ = PushSubscription.objects.filter(
            user=request.user,
            endpoint=endpoint,
        ).delete()

        return JsonResponse({"ok": True, "deleted": deleted_count})


# ---------------------------------------------------------------------------
# Notification history (login required)
# ---------------------------------------------------------------------------


class NotificationHistoryView(LoginRequiredMixin, ListView):
    """
    Display the authenticated user's notification history.
    """

    template_name = "notifications/history.html"
    context_object_name = "notifications"
    paginate_by = 25

    def get_queryset(self):
        return (
            NotificationQueue.objects.filter(
                recipient=self.request.user,
                status="sent",
            )
            .order_by("-sent_at")
        )


# ---------------------------------------------------------------------------
# Mark-read (login required, AJAX)
# ---------------------------------------------------------------------------


class MarkReadView(LoginRequiredMixin, View):
    """
    POST: Mark a notification as read (sets status to 'sent' if in_app).
    Returns JSON response for AJAX usage.
    """

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        notification = get_object_or_404(
            NotificationQueue,
            pk=pk,
            recipient=request.user,
        )

        # We use sent_at as an indicator of "read" for in_app
        if not notification.sent_at:
            notification.sent_at = timezone.now()
            notification.save(update_fields=["sent_at"])

        return JsonResponse({"ok": True, "pk": notification.pk})

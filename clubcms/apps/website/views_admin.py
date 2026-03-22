"""
Admin-only maintenance views for cache and task management.

Accessible from the Wagtail admin sidebar under Settings → Maintenance.
Requires superuser access.
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views import View

from wagtail.admin.views.generic.base import WagtailAdminTemplateMixin

logger = logging.getLogger(__name__)


class MaintenanceView(WagtailAdminTemplateMixin, View):
    """Dashboard showing cache stats and action buttons."""

    template_name = "website/admin/maintenance.html"
    page_title = "Maintenance"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, _("Access denied."))
            return redirect("wagtailadmin_home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        from django.contrib.sessions.models import Session
        from django.utils import timezone

        from django_q.models import Failure, OrmQ, Schedule, Success

        context = self.get_context_data()
        context.update(
            {
                "cache_backend": cache.__class__.__name__,
                "sessions_total": Session.objects.count(),
                "sessions_expired": Session.objects.filter(
                    expire_date__lt=timezone.now()
                ).count(),
                "q_queued": OrmQ.objects.count(),
                "q_success": Success.objects.count(),
                "q_failure": Failure.objects.count(),
                "q_schedules": Schedule.objects.count(),
            }
        )
        return self.render_to_response(context)

    def post(self, request):
        action = request.POST.get("action", "")

        if action == "clear_cache":
            cache.clear()
            messages.success(request, _("Cache cleared successfully."))
            logger.info("Cache cleared by %s", request.user)

        elif action == "clear_sessions":
            from django.contrib.sessions.models import Session
            from django.utils import timezone

            count = Session.objects.filter(expire_date__lt=timezone.now()).delete()[0]
            messages.success(
                request,
                _("%(count)d expired sessions removed.") % {"count": count},
            )
            logger.info("Cleared %d expired sessions (by %s)", count, request.user)

        elif action == "clear_q_success":
            from django_q.models import Success

            count = Success.objects.all().delete()[0]
            messages.success(
                request,
                _("%(count)d completed task logs removed.") % {"count": count},
            )
            logger.info("Cleared %d Q success logs (by %s)", count, request.user)

        elif action == "clear_q_failure":
            from django_q.models import Failure

            count = Failure.objects.all().delete()[0]
            messages.warning(
                request,
                _("%(count)d failed task logs removed.") % {"count": count},
            )
            logger.info("Cleared %d Q failure logs (by %s)", count, request.user)

        elif action == "clear_all":
            from django.contrib.sessions.models import Session
            from django.utils import timezone

            from django_q.models import Failure, Success

            cache.clear()
            sess = Session.objects.filter(expire_date__lt=timezone.now()).delete()[0]
            succ = Success.objects.all().delete()[0]
            fail = Failure.objects.all().delete()[0]
            messages.success(
                request,
                _(
                    "All cleared: cache, %(sess)d sessions, "
                    "%(succ)d success logs, %(fail)d failure logs."
                )
                % {"sess": sess, "succ": succ, "fail": fail},
            )
            logger.info(
                "Full maintenance clear by %s: %d sessions, %d success, %d failure",
                request.user,
                sess,
                succ,
                fail,
            )

        return redirect("maintenance_admin")


# ═══════════════════════════════════════════════════════════════════════════
# Newsletter send view
# ═══════════════════════════════════════════════════════════════════════════


class SendNewsletterView(WagtailAdminTemplateMixin, View):
    """Confirm and trigger async sending of a newsletter campaign."""

    template_name = "website/admin/send_newsletter.html"
    page_title = _("Send Newsletter")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _("Access denied."))
            return redirect("wagtailadmin_home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        from apps.website.models.newsletter import (
            NewsletterSubscription,
            SentNewsletter,
        )
        from apps.website.render_email import render_newsletter_body_html

        newsletter = SentNewsletter.objects.filter(pk=pk).first()
        if not newsletter:
            messages.error(request, _("Newsletter not found."))
            return redirect("wagtailadmin_home")

        # Count subscribers — filter by category if set
        qs = NewsletterSubscription.objects.filter(is_active=True)
        if newsletter.category:
            qs = qs.filter(categories=newsletter.category)
        subscriber_count = qs.count()

        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
        body_preview = render_newsletter_body_html(newsletter, base_url=base_url)

        context = self.get_context_data()
        context.update(
            {
                "newsletter": newsletter,
                "subscriber_count": subscriber_count,
                "already_sent": newsletter.status == "sent",
                "body_preview": body_preview,
            }
        )
        return self.render_to_response(context)

    def post(self, request, pk):
        from django_q.tasks import async_task

        from apps.website.models.newsletter import SentNewsletter

        newsletter = SentNewsletter.objects.filter(pk=pk).first()
        if not newsletter:
            messages.error(request, _("Newsletter not found."))
            return redirect("wagtailadmin_home")

        if newsletter.status == "sent":
            messages.warning(request, _("This newsletter has already been sent."))
            return redirect("sentnewsletter:edit", pk)

        async_task(
            "apps.website.services_newsletter.send_newsletter",
            newsletter.pk,
            request.user.pk,
            task_name=f"newsletter-{newsletter.pk}",
        )

        messages.success(
            request,
            _("Newsletter '%(subject)s' queued for sending.")
            % {"subject": newsletter.subject},
        )
        return redirect("sentnewsletter:index")


class PreviewNewsletterView(WagtailAdminTemplateMixin, View):
    """Render a full email preview of a newsletter campaign in admin."""

    template_name = "website/admin/preview_newsletter.html"
    page_title = _("Preview Newsletter")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, _("Access denied."))
            return redirect("wagtailadmin_home")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, pk):
        from apps.website.models.newsletter import SentNewsletter
        from apps.website.render_email import render_newsletter_body_html

        newsletter = SentNewsletter.objects.filter(pk=pk).first()
        if not newsletter:
            messages.error(request, _("Newsletter not found."))
            return redirect("wagtailadmin_home")

        base_url = getattr(settings, "WAGTAILADMIN_BASE_URL", "").rstrip("/")
        body_preview = render_newsletter_body_html(newsletter, base_url=base_url)

        context = self.get_context_data()
        context.update(
            {
                "newsletter": newsletter,
                "body_preview": body_preview,
            }
        )
        return self.render_to_response(context)

"""
Custom Wagtail admin panels for members app.
"""

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import Panel


class CardActionsPanel(Panel):
    """
    Custom panel that displays card action buttons (Issue/Renew/Suspend/Terminate).
    """

    class BoundPanel(Panel.BoundPanel):
        template_name = "admin/members/panels/card_actions.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            instance = self.instance

            if instance and instance.pk:
                context["instance"] = instance
                context["issue_url"] = reverse("members_issue_card", args=[instance.pk])
                context["renew_url"] = reverse("members_renew_card", args=[instance.pk])
                context["suspend_url"] = reverse("members_suspend_card", args=[instance.pk])
                context["reactivate_url"] = reverse("members_reactivate_card", args=[instance.pk])
                context["terminate_url"] = reverse("members_terminate_card", args=[instance.pk])
                context["has_card"] = bool(instance.card_number)
                context["is_active"] = instance.is_active_member
                context["card_number"] = instance.card_number
                context["membership_date"] = instance.membership_date
                context["membership_expiry"] = instance.membership_expiry
                context["days_to_expiry"] = instance.days_to_expiry
                context["card_status"] = instance.card_status
                context["card_status_display"] = instance.get_card_status_display()
                context["card_status_reason"] = instance.card_status_reason
                context["card_status_changed"] = instance.card_status_changed
                
                # Get user's products with locale info
                from wagtail.models import Locale
                from django.utils.translation import get_language
                
                # Get products, preferring current locale
                current_lang = get_language() or 'it'
                try:
                    current_locale = Locale.objects.get(language_code=current_lang)
                except Locale.DoesNotExist:
                    current_locale = Locale.get_default()
                
                # Get all products for this user
                user_products = instance.products.all()
                
                # Group by translation_key to show one per product
                seen_keys = set()
                products_list = []
                for product in user_products:
                    if product.translation_key not in seen_keys:
                        seen_keys.add(product.translation_key)
                        # Try to get localized version
                        localized = user_products.filter(
                            translation_key=product.translation_key,
                            locale=current_locale
                        ).first()
                        if localized:
                            products_list.append(localized)
                        else:
                            products_list.append(product)
                
                context["user_products"] = products_list
            else:
                context["instance"] = None
                context["has_card"] = False
                context["user_products"] = []

            return context


class RequestActionsPanel(Panel):
    """
    Custom panel that displays request details, user info, product info,
    and approve/reject buttons for MembershipRequest.
    """

    class BoundPanel(Panel.BoundPanel):
        template_name = "admin/members/panels/request_actions.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            instance = self.instance

            if instance and instance.pk:
                context["instance"] = instance
                context["approve_url"] = reverse("members_approve_request", args=[instance.pk])
                context["reject_url"] = reverse("members_reject_request", args=[instance.pk])
                context["is_pending"] = instance.status == "pending"
                context["status"] = instance.status
                context["status_display"] = instance.get_status_display()
                
                # User information
                user = instance.user
                context["user"] = user
                context["user_edit_url"] = reverse("clubusers:edit", args=[user.pk])
                context["user_full_name"] = user.get_full_name() or user.username
                context["user_email"] = user.email
                context["user_has_card"] = bool(user.card_number)
                context["user_card_number"] = user.card_number
                context["user_membership_expiry"] = user.membership_expiry
                context["user_is_active_member"] = user.is_active_member
                
                # Product information (with locale handling)
                product = instance.product
                context["product"] = product
                context["product_name"] = product.name
                context["product_price"] = product.price
                context["product_validity_days"] = product.validity_days
                context["product_available_from"] = product.available_from
                context["product_available_until"] = product.available_until
                context["product_is_purchasable"] = product.is_purchasable
                
                # Check if user already has this product
                user_has_product = user.products.filter(
                    translation_key=product.translation_key
                ).exists()
                context["user_has_product"] = user_has_product
                
            else:
                context["instance"] = None
                context["is_pending"] = False

            return context

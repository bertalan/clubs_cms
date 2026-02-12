"""
Access-control decorators for the members app.

Provides two decorators:
- active_member_required: requires an authenticated, active member.
- member_with_product: requires the member to own a specific product.
"""

import functools

from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def active_member_required(view_func):
    """
    Decorator that ensures the user is authenticated and is an active member.

    If the user is not authenticated, redirects to the login page.
    If the user is authenticated but not an active member, returns 403.
    """

    @functools.wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.conf import settings

            login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
            return redirect(f"{login_url}?next={request.path}")

        if not getattr(request.user, "is_active_member", False):
            return HttpResponseForbidden(
                "Access denied. Active membership is required."
            )

        return view_func(request, *args, **kwargs)

    return _wrapped


def member_with_product(product_slug):
    """
    Decorator factory that ensures the user owns a product with the given slug.

    Usage::

        @member_with_product("premium")
        def my_view(request):
            ...

    If the user is not authenticated, redirects to login.
    If the user does not own the product, returns 403.

    Args:
        product_slug (str): Slug of the required product.

    Returns:
        Decorator function.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.conf import settings

                login_url = getattr(settings, "LOGIN_URL", "/accounts/login/")
                return redirect(f"{login_url}?next={request.path}")

            has_product = request.user.products.filter(
                slug=product_slug
            ).exists()
            if not has_product:
                return HttpResponseForbidden(
                    f"Access denied. Product '{product_slug}' is required."
                )

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator

from django.contrib import admin

from apps.federation.models import (
    ExternalEvent,
    ExternalEventComment,
    ExternalEventInterest,
    FederatedClub,
)


@admin.register(FederatedClub)
class FederatedClubAdmin(admin.ModelAdmin):
    list_display = ["name", "short_code", "is_active", "is_approved", "last_sync"]
    list_filter = ["is_active", "is_approved"]
    search_fields = ["name", "short_code"]
    readonly_fields = ["id", "created_at"]


@admin.register(ExternalEvent)
class ExternalEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "source_club", "start_date", "is_approved", "is_hidden"]
    list_filter = ["source_club", "is_approved", "is_hidden"]
    search_fields = ["event_name"]
    readonly_fields = ["id", "fetched_at", "updated_at"]


@admin.register(ExternalEventInterest)
class ExternalEventInterestAdmin(admin.ModelAdmin):
    list_display = ["user", "external_event", "interest_level", "created_at"]
    list_filter = ["interest_level"]
    readonly_fields = ["id"]


@admin.register(ExternalEventComment)
class ExternalEventCommentAdmin(admin.ModelAdmin):
    list_display = ["user", "external_event", "is_deleted", "created_at"]
    list_filter = ["is_deleted"]
    readonly_fields = ["id"]

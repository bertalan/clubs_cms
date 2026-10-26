from django.contrib import admin

from apps.federation.models import (
    ExternalEvent,
    ExternalEventComment,
    ExternalEventInterest,
    FederatedClub,
)


@admin.register(FederatedClub)
class FederatedClubAdmin(admin.ModelAdmin):
    list_display = ["name", "short_code", "city", "is_active", "is_approved", "last_sync"]
    list_filter = ["is_active", "is_approved"]
    search_fields = ["name", "short_code", "city"]
    readonly_fields = ["id", "created_at"]


@admin.register(ExternalEvent)
class ExternalEventAdmin(admin.ModelAdmin):
    list_display = ["event_name", "source_club", "start_date", "is_approved", "is_hidden"]
    list_filter = ["source_club", "is_approved", "is_hidden"]
    search_fields = ["event_name"]
    # Only approval and visibility are decided locally: the rest comes from the partner sync.
    readonly_fields = [
        "id",
        "source_club",
        "external_id",
        "event_name",
        "start_date",
        "end_date",
        "location_name",
        "location_address",
        "location_lat",
        "location_lon",
        "description",
        "event_status",
        "image_url",
        "detail_url",
        "fetched_at",
        "updated_at",
    ]

    def has_add_permission(self, request):
        return False


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

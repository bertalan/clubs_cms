from django.contrib import admin

from apps.mutual_aid.models import (
    AidPrivacySettings,
    AidRequest,
    ContactUnlock,
    FederatedAidAccess,
    FederatedAidAccessRequest,
)


@admin.register(AidRequest)
class AidRequestAdmin(admin.ModelAdmin):
    list_display = ["requester_name", "helper", "issue_type", "urgency", "status", "created_at"]
    list_filter = ["status", "urgency", "issue_type", "is_from_federation"]
    search_fields = ["requester_name", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(AidPrivacySettings)
class AidPrivacySettingsAdmin(admin.ModelAdmin):
    list_display = ["user", "show_phone_on_aid", "show_email_on_aid", "show_exact_location"]
    search_fields = ["user__username", "user__email"]


@admin.register(FederatedAidAccess)
class FederatedAidAccessAdmin(admin.ModelAdmin):
    list_display = [
        "external_display_name", "source_club", "access_level",
        "contacts_unlocked", "is_active", "created_at",
    ]
    list_filter = ["source_club", "access_level", "is_active"]
    search_fields = ["external_display_name"]
    readonly_fields = ["id", "created_at"]


@admin.register(FederatedAidAccessRequest)
class FederatedAidAccessRequestAdmin(admin.ModelAdmin):
    list_display = ["federated_access", "status", "reviewed_by", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["id", "created_at"]


@admin.register(ContactUnlock)
class ContactUnlockAdmin(admin.ModelAdmin):
    list_display = ["federated_access", "helper", "unlocked_at"]
    readonly_fields = ["id", "unlocked_at"]

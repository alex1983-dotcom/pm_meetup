from django.contrib import admin
from .models import Material, Partner, TeamMember, SiteSettings, Page, PartnershipApplication


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "view_count", "created_at")
    list_filter = ("category",)
    search_fields = ("title",)
    list_editable = ("category",)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "partnership_level", "event", "display_order", "created_at")
    list_filter = ("partnership_level",)
    search_fields = ("name",)
    list_editable = ("display_order",)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "display_order", "created_at")
    search_fields = ("full_name",)
    list_editable = ("display_order",)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "email", "phone", "updated_at")

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    list_filter = ("is_published",)
    search_fields = ("title",)
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_published",)


@admin.register(PartnershipApplication)
class PartnershipApplicationAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_name", "contact_email", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("company_name", "contact_name", "contact_email")
    readonly_fields = ("created_at",)
    list_editable = ("status",)

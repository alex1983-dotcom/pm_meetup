from django.contrib import admin
from .models import ApiKey


@admin.register(ApiKey)
class ApiKey(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    readonly_fields = ("key", "created_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


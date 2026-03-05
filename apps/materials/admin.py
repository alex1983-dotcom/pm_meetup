from django.contrib import admin

from .models import Material, MaterialCategory


@admin.register(MaterialCategory)
class MaterialCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "display_order", "is_active", "created_at")
    list_editable = ("display_order", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("display_order", "title")


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "label",
        "category",
        "date",
        "place",
        "duration_minutes",
        "view_count",
        "created_at",
    )
    list_filter = ("category", "date")
    search_fields = ("title", "label", "place")

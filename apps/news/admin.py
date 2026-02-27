from django.contrib import admin
from .models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title", "author", "is_published", "publication_date",
        "views_count", "read_time_minutes", "created_at",
    )
    list_filter = ("is_published",)
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views_count", "created_at", "updated_at")
    filter_horizontal = ("tags",)
    date_hierarchy = "publication_date"
    list_editable = ("is_published",)

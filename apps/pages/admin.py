from django.contrib import admin

from apps.pages.models import BlockItem, BlockType, Page, PageBlock


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    search_fields = ("name", "slug")
    ordering = ("slug",)


@admin.register(BlockType)
class BlockTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


class BlockItemInline(admin.TabularInline):
    model = BlockItem
    extra = 1
    fields = ("title", "subtitle", "content", "icon", "order")
    ordering = ("order",)


@admin.register(PageBlock)
class PageBlockAdmin(admin.ModelAdmin):
    list_display = ("page", "block_type", "order")
    list_filter = ("page", "block_type")
    ordering = ("page", "order")
    inlines = [BlockItemInline]


@admin.register(BlockItem)
class BlockItemAdmin(admin.ModelAdmin):
    list_display = ("block", "title", "order", "created_at")
    search_fields = ("title", "subtitle", "content")
    list_filter = ("block__page", "block__block_type")
    ordering = ("block", "order")


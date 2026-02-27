from django.contrib import admin
from .models import EventCategory, Speaker, Event, EventSegment, EventRegistration, EventGallery


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("order",)


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "company", "created_at")
    search_fields = ("full_name", "company")
    list_filter = ("topics",)
    filter_horizontal = ("topics",)


class EventSegmentInline(admin.TabularInline):
    model = EventSegment
    extra = 0
    fields = ("title", "time_start", "time_end", "order", "location")
    show_change_link = True


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title", "date", "time_start", "event_type", "format", "status",
        "is_featured", "capacity", "created_at",
    )
    list_filter = ("status", "event_type", "format", "is_featured")
    search_fields = ("title", "location_city")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    filter_horizontal = ("categories", "tags", "speakers")
    inlines = [EventSegmentInline]
    date_hierarchy = "date"
    list_editable = ("status", "is_featured")


@admin.register(EventSegment)
class EventSegmentAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "time_start", "time_end", "order")
    list_filter = ("event",)
    search_fields = ("title",)
    filter_horizontal = ("speakers",)
    ordering = ("event", "order", "time_start")


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "attendance_status", "created_at")
    list_filter = ("status", "attendance_status")
    search_fields = ("user__email", "event__title")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(EventGallery)
class EventGalleryAdmin(admin.ModelAdmin):
    list_display = ("event", "title", "photo_count", "created_at")
    list_filter = ("event",)
    search_fields = ("title",)

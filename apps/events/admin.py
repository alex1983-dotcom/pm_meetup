from django.contrib import admin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.contrib import messages
from django.utils.text import slugify

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
    change_form_template = "admin/events/event/change_form.html"
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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<path:object_id>/duplicate/",
                self.admin_site.admin_view(self.duplicate_event_view),
                name="events_event_duplicate",
            ),
        ]
        return custom + urls

    def duplicate_event_view(self, request, object_id):
        if request.method != "GET":
            return HttpResponseForbidden()
        if not request.user.has_perm("events.add_event"):
            return HttpResponseForbidden()
        original = get_object_or_404(Event, pk=object_id)
        base_slug = slugify(original.title, allow_unicode=True) + "-копия"
        if len(base_slug) > 220:
            base_slug = base_slug[:217] + "-"
        slug = base_slug
        counter = 2
        while Event.objects.filter(slug=slug).exists():
            suffix = f"-{counter}"
            slug = (base_slug + suffix)[:220]
            counter += 1
        new_event = Event(
            title=original.title,
            slug=slug,
            description=original.description,
            date=original.date,
            time_start=original.time_start,
            time_end=original.time_end,
            format=original.format,
            location_address=original.location_address,
            location_city=original.location_city,
            location_venue=original.location_venue,
            online_url=original.online_url,
            online_platform=original.online_platform,
            event_type=original.event_type,
            cover_image=None,
            capacity=original.capacity,
            price=original.price,
            registration_type=original.registration_type,
            status="draft",
            cancellation_reason=original.cancellation_reason,
            meta_title=original.meta_title,
            meta_description=original.meta_description,
            is_featured=original.is_featured,
        )
        new_event.save()
        new_event.categories.set(original.categories.all())
        new_event.tags.set(original.tags.all())
        new_event.speakers.set(original.speakers.all())
        for seg in original.segments.all():
            new_seg = EventSegment(
                event=new_event,
                title=seg.title,
                description=seg.description,
                time_start=seg.time_start,
                time_end=seg.time_end,
                order=seg.order,
                location=seg.location,
            )
            new_seg.save()
            new_seg.speakers.set(seg.speakers.all())
        messages.success(
            request,
            "Событие успешно продублировано. Измените при необходимости дату и название.",
        )
        return redirect(reverse("admin:events_event_change", args=[new_event.pk]))


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

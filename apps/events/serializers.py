from decimal import Decimal

from rest_framework import serializers

from apps.core.serializers import TagSerializer
from apps.events.models import (
    Event,
    EventGallery,
    EventRegistration,
    EventSegment,
    Speaker,
)


class SpeakerListSerializer(serializers.ModelSerializer):
    topics = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Speaker
        fields = (
            "id",
            "full_name",
            "position",
            "company",
            "photo",
            "bio",
            "email",
            "social_links",
            "topics",
        )


class EventSegmentSerializer(serializers.ModelSerializer):
    speakers = SpeakerListSerializer(many=True, read_only=True)

    class Meta:
        model = EventSegment
        fields = (
            "id",
            "title",
            "description",
            "time_start",
            "time_end",
            "order",
            "location",
            "speakers",
        )


class _EventPriceRepresentationMixin:
    """Пустая цена в БД (null) в API отдаётся как 0 — бесплатно."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("price") is None:
            data["price"] = Decimal("0")
        return data


class EventListSerializer(_EventPriceRepresentationMixin, serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "date",
            "time_start",
            "time_end",
            "format",
            "cover_image",  
            "location_city",
            "price",
            "status",
            "is_featured",
        )


class EventDetailSerializer(_EventPriceRepresentationMixin, serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    speakers = SpeakerListSerializer(many=True, read_only=True)
    segments = EventSegmentSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "title",
            "slug",
            "short_description",
            "description",
            "date",
            "time_start",
            "time_end",
            "format",
            "event_type",
            "cover_image",
            "location_address",
            "location_city",
            "location_venue",
            "online_url",
            "online_platform",
            "capacity",
            "price",
            "registration_type",
            "status",
            "meta_title",
            "meta_description",
            "is_featured",
            "tags",
            "speakers",
            "segments",
        )


class EventGalleryEventSerializer(serializers.ModelSerializer):
    """Минимальные поля события для карточки галереи (дата, город)."""

    class Meta:
        model = Event
        fields = ("id", "slug", "title", "date", "location_city")


class EventGallerySerializer(serializers.ModelSerializer):
    event = EventGalleryEventSerializer(read_only=True)

    class Meta:
        model = EventGallery
        fields = (
            "id",
            "event",
            "title",
            "cover_image",
            "photo_count",
            "external_album_url",
        )


class EventRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRegistration
        fields = (
            "id",
            "event",
            "user",
            "status",
            "attendance_status",
            "extra_data",
            "created_at",
        )
        read_only_fields = ("user", "status", "attendance_status", "created_at")

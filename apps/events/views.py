from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from apps.events.models import (
    Event,
    EventCategory,
    EventGallery,
    EventRegistration,
    EventSegment,
    Speaker,
)
from apps.events.serializers import (
    EventCategorySerializer,
    EventDetailSerializer,
    EventGallerySerializer,
    EventListSerializer,
    EventRegistrationSerializer,
    EventSegmentSerializer,
    SpeakerListSerializer,
)


@extend_schema_view(tags=["events"])
class EventCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventCategory.objects.all()
    serializer_class = EventCategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


@extend_schema_view(tags=["events"])
class SpeakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerListSerializer


@extend_schema_view(tags=["events"])
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventDetailSerializer
        return EventListSerializer

    def get_queryset(self):
        qs = Event.objects.prefetch_related(
            "categories",
            "tags",
            "speakers",
            "segments__speakers",
        )
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


@extend_schema_view(tags=["events"])
class EventSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventSegment.objects.prefetch_related("speakers")
    serializer_class = EventSegmentSerializer


@extend_schema_view(tags=["events"])
class EventGalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventGallery.objects.all()
    serializer_class = EventGallerySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        event_slug = self.request.query_params.get("event")
        if event_slug:
            qs = qs.filter(event__slug=event_slug)
        return qs


@extend_schema_view(tags=["events"])
class EventRegistrationViewSet(viewsets.ModelViewSet):
    serializer_class = EventRegistrationSerializer
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = EventRegistration.objects.select_related("event", "user")
        if self.request.user.is_authenticated:
            qs = qs.filter(user=self.request.user)
        else:
            qs = qs.none()
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            raise ValidationError("Требуется авторизация для регистрации на событие.")

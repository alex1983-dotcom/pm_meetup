from django.db.models import Q, Value
from django.db.models.functions import Coalesce, Greatest
from django.contrib.postgres.search import TrigramSimilarity
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, viewsets
from rest_framework.exceptions import ValidationError

from apps.events.models import (
    Event,
    EventGallery,
    EventRegistration,
    EventSegment,
    EventTheme,
    Speaker,
)
from apps.events.serializers import (
    EventDetailSerializer,
    EventGallerySerializer,
    EventListSerializer,
    EventRegistrationSerializer,
    EventSegmentSerializer,
    EventThemeSerializer,
    SpeakerListSerializer,
)


@extend_schema(tags=["events"])
class EventThemeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventTheme.objects.all()
    serializer_class = EventThemeSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


@extend_schema(tags=["events"])
class SpeakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerListSerializer


@extend_schema(tags=["events"])
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["date", "time_start", "created_at", "title"]
    ordering = ["-date", "-time_start"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventDetailSerializer
        return EventListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Триграммный fuzzy-поиск по названию, описанию, локации, спикерам и тегам.",
            ),
            OpenApiParameter(
                name="min_rank",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Порог релевантности для триграммного поиска (по умолчанию 0.12).",
            ),
            OpenApiParameter(
                name="tag",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Слаг тега для фильтрации событий (например: sobytiya).",
            ),
            OpenApiParameter(
                name="tags",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Список слагов тегов через запятую (например: sobytiya,techconference).",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Фильтр по статусу события.",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка: date, -date, time_start, -time_start, created_at, -created_at, title, -title.",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        # При активном search сортировка задаётся в get_queryset() (-search_rank).
        # Иначе OrderingFilter перезапишет её на ordering по умолчанию (-date).
        if self.request.query_params.get("search", "").strip():
            return queryset
        return super().filter_queryset(queryset)

    def get_queryset(self):
        qs = Event.objects.prefetch_related(
            "themes",
            "tags",
            "speakers",
            "segments__speakers",
        )
        search_query = self.request.query_params.get("search", "").strip()
        min_rank_raw = self.request.query_params.get("min_rank")
        try:
            min_rank = float(min_rank_raw) if min_rank_raw is not None else 0.12
        except (TypeError, ValueError):
            min_rank = 0.12
        min_rank = max(0.0, min(1.0, min_rank))
        if search_query:
            qs = qs.annotate(
                search_rank=Greatest(
                    Coalesce(TrigramSimilarity("title", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("short_description", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("description", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("location_city", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("location_venue", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("speakers__full_name", search_query), Value(0.0)),
                )
            ).filter(
                Q(search_rank__gte=min_rank)
                | Q(tags__name__icontains=search_query)
                | Q(tags__slug__icontains=search_query)
            )
        status = self.request.query_params.get("status")
        if status:
            qs = qs.filter(status=status)
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)
        tags = self.request.query_params.get("tags")
        if tags:
            tag_slugs = [slug.strip() for slug in tags.split(",") if slug.strip()]
            if tag_slugs:
                qs = qs.filter(tags__slug__in=tag_slugs)
        if search_query:
            qs = qs.order_by("-search_rank", "-date", "-time_start")
        qs = qs.distinct()
        return qs


@extend_schema(tags=["events"])
class EventSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventSegment.objects.prefetch_related("speakers")
    serializer_class = EventSegmentSerializer


@extend_schema(tags=["events"])
class EventGalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventGallery.objects.all()
    serializer_class = EventGallerySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        event_slug = self.request.query_params.get("event")
        if event_slug:
            qs = qs.filter(event__slug=event_slug)
        return qs


@extend_schema(tags=["events"])
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

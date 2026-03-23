from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Value
from django.db.models.functions import Coalesce, Greatest
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, viewsets

from apps.materials.models import Material, MaterialCategory
from apps.materials.serializers import (
    MaterialCategorySerializer,
    MaterialDetailSerializer,
    MaterialListSerializer,
)


@extend_schema(tags=["materials"])
class MaterialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialCategory.objects.filter(is_active=True)
    serializer_class = MaterialCategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


@extend_schema(tags=["materials"])
class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.select_related("category")
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["date", "created_at", "view_count", "title"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MaterialDetailSerializer
        return MaterialListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Триграммный fuzzy-поиск по названию, типу, описанию, месту и категории.",
            ),
            OpenApiParameter(
                name="min_rank",
                type=float,
                location=OpenApiParameter.QUERY,
                description="Порог релевантности для триграммного поиска (по умолчанию 0.12).",
            ),
            OpenApiParameter(
                name="category",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Слаг категории материала.",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка: date, -date, created_at, -created_at, view_count, -view_count, title, -title.",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        if self.request.query_params.get("search", "").strip():
            return queryset
        return super().filter_queryset(queryset)

    def get_queryset(self):
        qs = super().get_queryset()
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
                    Coalesce(TrigramSimilarity("label", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("description", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("place", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("category__title", search_query), Value(0.0)),
                )
            ).filter(search_rank__gte=min_rank).order_by("-search_rank", "-created_at")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs

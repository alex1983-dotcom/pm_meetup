from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Value
from django.db.models.functions import Coalesce, Greatest
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, viewsets

from apps.news.models import NewsArticle
from apps.news.serializers import NewsArticleDetailSerializer, NewsArticleListSerializer


@extend_schema(tags=["news"])
class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.filter(is_published=True).prefetch_related("tags")
    lookup_field = "slug"
    lookup_url_kwarg = "slug"
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["publication_date", "created_at", "views_count", "title"]
    ordering = ["-publication_date", "-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Триграммный fuzzy-поиск по заголовку, описанию, контенту и тегам.",
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
                description="Слаг тега для фильтрации новостей.",
            ),
            OpenApiParameter(
                name="tags",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Список слагов тегов через запятую.",
            ),
            OpenApiParameter(
                name="ordering",
                type=str,
                location=OpenApiParameter.QUERY,
                description="Сортировка: publication_date, -publication_date, created_at, -created_at, views_count, -views_count, title, -title.",
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
                    Coalesce(TrigramSimilarity("short_description", search_query), Value(0.0)),
                    Coalesce(TrigramSimilarity("content", search_query), Value(0.0)),
                )
            ).filter(
                Q(search_rank__gte=min_rank)
                | Q(tags__name__icontains=search_query)
                | Q(tags__slug__icontains=search_query)
            )
        tag = self.request.query_params.get("tag")
        if tag:
            qs = qs.filter(tags__slug=tag)
        tags = self.request.query_params.get("tags")
        if tags:
            tag_slugs = [slug.strip() for slug in tags.split(",") if slug.strip()]
            if tag_slugs:
                qs = qs.filter(tags__slug__in=tag_slugs)
        if search_query:
            qs = qs.order_by("-search_rank", "-publication_date", "-created_at")
        return qs.distinct()

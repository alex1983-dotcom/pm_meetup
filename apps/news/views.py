from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets

from apps.news.models import NewsArticle
from apps.news.serializers import NewsArticleDetailSerializer, NewsArticleListSerializer


@extend_schema_view(tags=["news"])
class NewsArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsArticle.objects.filter(is_published=True).prefetch_related("tags")
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return NewsArticleDetailSerializer
        return NewsArticleListSerializer

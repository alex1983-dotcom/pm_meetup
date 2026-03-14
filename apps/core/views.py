from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets

from apps.core.models import Tag
from apps.core.serializers import TagSerializer


@extend_schema_view(tags=["core"])
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и детали тегов (для фильтров событий/новостей)."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"

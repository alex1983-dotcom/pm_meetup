from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets

from apps.materials.models import Material, MaterialCategory
from apps.materials.serializers import (
    MaterialCategorySerializer,
    MaterialDetailSerializer,
    MaterialListSerializer,
)


@extend_schema_view(tags=["materials"])
class MaterialCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MaterialCategory.objects.filter(is_active=True)
    serializer_class = MaterialCategorySerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


@extend_schema_view(tags=["materials"])
class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Material.objects.select_related("category")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return MaterialDetailSerializer
        return MaterialListSerializer

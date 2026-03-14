from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.materials.views import MaterialCategoryViewSet, MaterialViewSet

router = DefaultRouter()
router.register(r"categories", MaterialCategoryViewSet, basename="materialcategory")
router.register(r"materials", MaterialViewSet, basename="material")

urlpatterns = [
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.news.views import NewsArticleViewSet

router = DefaultRouter()
router.register(r"articles", NewsArticleViewSet, basename="newsarticle")

urlpatterns = [
    path("", include(router.urls)),
]

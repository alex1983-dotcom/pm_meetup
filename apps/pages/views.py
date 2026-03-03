from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import OnlyWithApiKeyOrFromFrontend
from apps.pages.models import Page
from apps.pages.serializers import PageSerializer


class PageDetailAPIView(APIView):
    """
    Возвращает структуру блоков и элементов для указанной страницы.

    GET /api/pages/<slug>/
    """

    permission_classes = [OnlyWithApiKeyOrFromFrontend]

    def get(self, request, slug: str, *args, **kwargs) -> Response:
        page = get_object_or_404(
            Page.objects.prefetch_related(
                "blocks__block_type",
                "blocks__items",
            ),
            slug=slug,
        )
        serializer = PageSerializer(page)
        return Response(serializer.data)


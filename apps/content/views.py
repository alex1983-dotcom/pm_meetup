from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.response import Response

from apps.content.models import Page, Partner, PartnershipApplication, SiteSettings, TeamMember
from apps.content.serializers import (
    ContentPageSerializer,
    PartnerSerializer,
    PartnershipApplicationSerializer,
    SiteSettingsSerializer,
    TeamMemberSerializer,
)


@extend_schema_view(tags=["content"])
class PartnerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


@extend_schema_view(tags=["content"])
class TeamMemberViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TeamMember.objects.all().order_by("display_order", "full_name")
    serializer_class = TeamMemberSerializer


@extend_schema_view(tags=["content"])
class SiteSettingsViewSet(viewsets.ReadOnlyModelViewSet):
    """Singleton: одна запись настроек сайта."""

    serializer_class = SiteSettingsSerializer

    def get_queryset(self):
        return SiteSettings.objects.filter(pk=1)

    def get_object(self):
        return SiteSettings.load()

    def list(self, request, *args, **kwargs):
        instance = SiteSettings.load()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema_view(tags=["content"])
class ContentPageViewSet(viewsets.ReadOnlyModelViewSet):
    """Статичные страницы (О нас, Контакты) — только опубликованные."""

    queryset = Page.objects.filter(is_published=True)
    serializer_class = ContentPageSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


@extend_schema_view(tags=["content"])
class PartnershipApplicationViewSet(viewsets.ModelViewSet):
    """Публичная отправка заявки на партнёрство; список только для админов через админку."""

    queryset = PartnershipApplication.objects.all()
    serializer_class = PartnershipApplicationSerializer
    http_method_names = ["post", "options", "head"]

    def get_serializer_class(self):
        return PartnershipApplicationSerializer

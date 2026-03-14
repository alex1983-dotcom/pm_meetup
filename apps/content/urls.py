from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.content.views import (
    ContentPageViewSet,
    PartnerViewSet,
    PartnershipApplicationViewSet,
    SiteSettingsViewSet,
    TeamMemberViewSet,
)

router = DefaultRouter()
router.register(r"partners", PartnerViewSet, basename="partner")
router.register(r"team", TeamMemberViewSet, basename="teammember")
router.register(r"settings", SiteSettingsViewSet, basename="sitesettings")
router.register(r"static-pages", ContentPageViewSet, basename="contentpage")
router.register(r"partnership-applications", PartnershipApplicationViewSet, basename="partnershipapplication")

urlpatterns = [
    path("", include(router.urls)),
]

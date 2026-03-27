from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.events.views import (
    EventGalleryViewSet,
    EventRegistrationViewSet,
    EventSegmentViewSet,
    EventViewSet,
    SpeakerViewSet,
)

router = DefaultRouter()
router.register(r"speakers", SpeakerViewSet, basename="speaker")
router.register(r"events", EventViewSet, basename="event")
router.register(r"segments", EventSegmentViewSet, basename="eventsegment")
router.register(r"galleries", EventGalleryViewSet, basename="eventgallery")
router.register(r"registrations", EventRegistrationViewSet, basename="eventregistration")

urlpatterns = [
    path("", include(router.urls)),
]

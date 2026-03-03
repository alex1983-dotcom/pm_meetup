from django.urls import path

from apps.pages.views import PageDetailAPIView


app_name = "pages"

urlpatterns = [
    path("api/pages/<slug:slug>/", PageDetailAPIView.as_view(), name="page-detail"),
]


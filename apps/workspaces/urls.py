from django.urls import path

from .views import LandingView, StatusView

app_name = "workspaces"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("status/", StatusView.as_view(), name="status"),
]

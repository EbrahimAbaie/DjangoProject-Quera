from django.urls import path

from .views import AboutView, DashboardPreviewView, LandingView, StatusView

app_name = "workspaces"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("about/", AboutView.as_view(), name="about"),
    path("status/", StatusView.as_view(), name="status"),
    path("dashboard/", DashboardPreviewView.as_view(), name="dashboard"),
]

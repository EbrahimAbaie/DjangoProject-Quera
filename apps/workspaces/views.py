from django.views.generic import TemplateView

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tags.models import Tag
from apps.time_entries.models import TimeEntry

from .models import Workspace


class LandingView(TemplateView):
    template_name = "pages/landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            workspace_count=Workspace.objects.count(),
            project_count=Project.objects.count(),
        )
        return context


class StatusView(TemplateView):
    template_name = "pages/status.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            workspace_count=Workspace.objects.count(),
            client_count=Client.objects.count(),
            project_count=Project.objects.count(),
            tag_count=Tag.objects.count(),
            time_entry_count=TimeEntry.objects.count(),
            running_timer_count=TimeEntry.objects.running().count(),
        )
        return context

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from apps.clients.models import Client
from apps.contact_notes.forms import ContactNoteForm
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


class AboutView(FormView):
    template_name = "pages/about.html"
    form_class = ContactNoteForm
    success_url = reverse_lazy("workspaces:about")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your note has been saved.")
        return super().form_valid(form)


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


class DashboardPreviewView(LoginRequiredMixin, TemplateView):
    template_name = "pages/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = TimeEntry.objects.visible_to(self.request.user)
        context["workspaces"] = (
            Workspace.objects.annotate(
                member_count=Count(
                    "memberships",
                    filter=Q(
                        memberships__is_active=True,
                        memberships__is_deleted=False,
                    ),
                    distinct=True,
                )
            ).visible_to(self.request.user)
        )
        context["running_timer_count"] = entries.running().count()
        context["recent_entries"] = entries.select_related(
            "project",
            "workspace",
        )[:5]
        return context

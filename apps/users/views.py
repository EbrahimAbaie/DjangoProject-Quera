from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import ProfileForm, RegisterForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "registration/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user

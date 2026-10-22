from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("mobile", "first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "birth_date",
            "description",
            "profile_picture",
        )
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }

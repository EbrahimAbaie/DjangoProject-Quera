from django import forms

from .models import ContactNote


class ContactNoteForm(forms.ModelForm):
    class Meta:
        model = ContactNote
        fields = ("name", "email", "message")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError("Message must contain at least 10 characters.")
        return message

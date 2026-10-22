from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from apps.contact_notes.admin import ContactNoteAdmin
from apps.contact_notes.forms import ContactNoteForm
from apps.contact_notes.models import ContactNote


class ContactNoteFormTests(TestCase):
    def test_message_must_have_at_least_ten_trimmed_characters(self):
        form = ContactNoteForm(
            data={
                "name": "Ali",
                "email": "ali@example.com",
                "message": "  short  ",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["message"],
            ["Message must contain at least 10 characters."],
        )

    def test_valid_form_strips_and_saves_message(self):
        form = ContactNoteForm(
            data={
                "name": "Ali",
                "email": "ali@example.com",
                "message": "  A sufficiently long message.  ",
            }
        )

        self.assertTrue(form.is_valid())
        note = form.save()
        self.assertEqual(note.message, "A sufficiently long message.")


class AboutPageTests(TestCase):
    def test_about_page_renders_form_and_navigation_link(self):
        response = self.client.get(reverse("workspaces:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about.html")
        self.assertIsInstance(response.context["form"], ContactNoteForm)
        self.assertContains(response, 'class="stack-form"')
        self.assertContains(response, reverse("workspaces:about"))

    def test_valid_submission_saves_note_and_displays_success_message(self):
        response = self.client.post(
            reverse("workspaces:about"),
            data={
                "name": "Sara",
                "email": "sara@example.com",
                "message": "Please tell me more about Quera Clock.",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("workspaces:about"))
        note = ContactNote.objects.get()
        self.assertEqual(note.name, "Sara")
        self.assertEqual(note.email, "sara@example.com")
        self.assertContains(response, "Your note has been saved.")

    def test_invalid_submission_does_not_save_note(self):
        response = self.client.post(
            reverse("workspaces:about"),
            data={
                "name": "Sara",
                "email": "sara@example.com",
                "message": "short",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ContactNote.objects.exists())
        self.assertContains(response, "Message must contain at least 10 characters.")


class ContactNoteAdminTests(TestCase):
    def test_admin_configuration(self):
        model_admin = ContactNoteAdmin(ContactNote, admin.site)

        self.assertEqual(
            model_admin.list_display,
            ("name", "email", "is_reviewed", "created_at"),
        )
        self.assertEqual(
            model_admin.search_fields,
            ("name", "email", "message"),
        )
        self.assertEqual(model_admin.list_filter, ("is_reviewed", "created_at"))
        self.assertEqual(model_admin.ordering, ("-created_at",))

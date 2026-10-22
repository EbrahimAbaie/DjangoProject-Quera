from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.users.forms import ProfileForm, RegisterForm
from apps.users.models import User


class UserFormTests(TestCase):
    def test_register_form_contains_profile_and_password_fields(self):
        form = RegisterForm()

        self.assertEqual(
            set(form.fields),
            {"mobile", "first_name", "last_name", "email", "password1", "password2"},
        )

    def test_profile_form_fields_and_birth_date_widget(self):
        form = ProfileForm()

        self.assertEqual(
            list(form.fields),
            [
                "first_name",
                "last_name",
                "email",
                "birth_date",
                "description",
                "profile_picture",
            ],
        )
        self.assertEqual(form.fields["birth_date"].widget.input_type, "date")


class AuthenticationViewTests(TestCase):
    password = "StrongPass123!"

    def setUp(self):
        self.user = User.objects.create_user(
            mobile="09120000004",
            password=self.password,
        )

    def test_login_and_register_pages_use_project_templates(self):
        login_response = self.client.get(reverse("users:login"))
        register_response = self.client.get(reverse("users:register"))

        self.assertEqual(login_response.status_code, 200)
        self.assertTemplateUsed(login_response, "registration/login.html")
        self.assertEqual(register_response.status_code, 200)
        self.assertTemplateUsed(register_response, "registration/register.html")

    def test_registration_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "mobile": "09120000005",
                "first_name": "Sara",
                "last_name": "Ahmadi",
                "email": "sara@example.com",
                "password1": self.password,
                "password2": self.password,
            },
        )

        self.assertRedirects(response, reverse("users:profile"))
        registered_user = User.objects.get(mobile="09120000005")
        self.assertEqual(int(self.client.session["_auth_user_id"]), registered_user.pk)

    def test_login_redirects_to_profile(self):
        response = self.client.post(
            reverse("users:login"),
            data={"username": self.user.mobile, "password": self.password},
        )

        self.assertRedirects(response, reverse("users:profile"))

    def test_logout_accepts_post_and_redirects_to_landing(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("users:logout"))

        self.assertRedirects(response, reverse("workspaces:landing"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_requires_login(self):
        response = self.client.get(reverse("users:profile"))

        expected_url = f'{reverse("users:login")}?next={reverse("users:profile")}'
        self.assertRedirects(response, expected_url)

    def test_profile_updates_current_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("users:profile"),
            data={
                "first_name": "Ali",
                "last_name": "Ahmadi",
                "email": "ali@example.com",
                "birth_date": "2000-01-02",
                "description": "Django developer",
            },
        )

        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ali")
        self.assertEqual(self.user.birth_date, date(2000, 1, 2))

    def test_navigation_changes_with_authentication_state(self):
        landing_url = reverse("workspaces:landing")
        guest_response = self.client.get(landing_url)

        self.assertContains(guest_response, f'href="{reverse("users:login")}"')
        self.assertContains(guest_response, f'href="{reverse("users:register")}"')

        self.client.force_login(self.user)
        user_response = self.client.get(landing_url)

        self.assertContains(user_response, f'href="{reverse("users:profile")}"')
        self.assertContains(user_response, f'action="{reverse("users:logout")}"')
        self.assertContains(user_response, 'class="nav-logout-form"')
        self.assertContains(user_response, 'class="nav-link-button"')

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from dreams_app.models import Dream, Favorite


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("register")

    def test_register_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_with_valid_data_creates_user(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_register_logs_in_user_after_success(self):
        self.client.post(self.url, {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        response = self.client.get(reverse("home"))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_register_redirects_already_logged_in_user(self):
        User.objects.create_user(username="existing", password="pass123")
        self.client.login(username="existing", password="pass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_register_with_duplicate_email_fails(self):
        User.objects.create_user(
            username="first",
            email="duplicate@example.com",
            password="pass123",
        )
        response = self.client.post(self.url, {
            "username": "second",
            "email": "duplicate@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="second").exists())

    def test_register_with_mismatched_passwords_fails(self):
        response = self.client.post(self.url, {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "StrongPass123!",
            "password2": "WrongPass456!",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="testuser").exists())


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = User.objects.create_user(
            username="alice",
            password="testpass123",
        )

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_with_correct_credentials(self):
        response = self.client.post(self.url, {
            "username": "alice",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(self.url, {
            "username": "alice",
            "password": "wrongpassword",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_nonexistent_user_fails(self):
        response = self.client.post(self.url, {
            "username": "nobody",
            "password": "testpass123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_redirects_already_logged_in_user(self):
        self.client.login(username="alice", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="bob",
            password="testpass123",
        )

    def test_logout_logs_out_user(self):
        self.client.login(username="bob", password="testpass123")
        self.client.get(reverse("logout"))
        response = self.client.get(reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirects_to_home(self):
        self.client.login(username="bob", password="testpass123")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="carol",
            password="testpass123",
        )
        self.url = reverse("profile")

    def test_profile_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_profile_loads_for_logged_in_user(self):
        self.client.login(username="carol", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_shows_correct_dream_count(self):
        Dream.objects.create(user=self.user, name="Dream 1", text="text")
        Dream.objects.create(user=self.user, name="Dream 2", text="text")
        self.client.login(username="carol", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["dream_count"], 2)

    def test_profile_shows_correct_favorites_count(self):
        dream = Dream.objects.create(user=self.user, name="Dream", text="text")
        Favorite.objects.create(user=self.user, dream=dream)
        self.client.login(username="carol", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["favorites_count"], 1)

    def test_profile_role_new_dreamer(self):
        Dream.objects.create(user=self.user, name="Dream", text="text")
        self.client.login(username="carol", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["role"], "New Dreamer")

    def test_profile_role_just_arrived_with_no_dreams(self):
        self.client.login(username="carol", password="testpass123")
        response = self.client.get(self.url)
        self.assertEqual(response.context["role"], "Just Arrived")


class CustomUserCreationFormTests(TestCase):
    def test_email_is_saved_on_user(self):
        client = Client()
        client.post(reverse("register"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

    def test_email_is_stored_lowercase(self):
        client = Client()
        client.post(reverse("register"), {
            "username": "newuser",
            "email": "NewUser@Example.COM",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        user = User.objects.get(username="newuser")
        self.assertEqual(user.email, "newuser@example.com")

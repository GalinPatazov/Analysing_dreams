from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from dreams_app.models import Dream, Favorite


class DreamViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="charlie",
            password="testpass123",
        )
        self.other_user = User.objects.create_user(
            username="dave",
            password="testpass123",
        )
        self.dream = Dream.objects.create(
            user=self.user,
            name="Ocean",
            text="A calm ocean dream.",
            analysis_text="Calm and reflective.",
        )

    def test_dream_detail_denies_other_users(self):
        self.client.login(username="dave", password="testpass123")
        response = self.client.get(reverse("dreams_app:detail", kwargs={"pk": self.dream.pk}))
        self.assertEqual(response.status_code, 404)

    def test_dream_detail_allows_owner(self):
        self.client.login(username="charlie", password="testpass123")
        response = self.client.get(reverse("dreams_app:detail", kwargs={"pk": self.dream.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ocean")

    def test_my_dreams_only_shows_current_users_dreams(self):
        Dream.objects.create(
            user=self.other_user,
            name="Other dream",
            text="Not mine.",
        )
        self.client.login(username="charlie", password="testpass123")
        response = self.client.get(reverse("dreams_app:my_dreams"))
        self.assertEqual(response.status_code, 200)
        dreams = list(response.context["dreams"])
        self.assertEqual(len(dreams), 1)
        self.assertEqual(dreams[0].user, self.user)

    def test_toggle_favorite_adds_and_removes(self):
        self.client.login(username="charlie", password="testpass123")
        url = reverse("dreams_app:toggle_favorite", kwargs={"pk": self.dream.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, dream=self.dream).exists())

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Favorite.objects.filter(user=self.user, dream=self.dream).exists())

    @patch("dreams_app.views._consume_ai_analysis", return_value=True)
    @patch("dreams_app.views.analyze_dream", return_value="Mock analysis")
    @patch("dreams_app.views.generate_dream_image", return_value=None)
    def test_create_dream_saves_user_and_redirects(
        self,
        mock_generate_image,
        mock_analyze_dream,
        mock_consume,
    ):
        self.client.login(username="charlie", password="testpass123")
        url = reverse("dreams_app:new_dream")

        response = self.client.post(url, data={"name": "New dream", "text": "I was in a forest."})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Dream.objects.count(), 2)

        dream = Dream.objects.order_by("-created_at").first()
        self.assertEqual(dream.user, self.user)
        self.assertEqual(dream.name, "New dream")
        self.assertEqual(dream.text, "I was in a forest.")
        self.assertEqual(dream.analysis_text, "Mock analysis")

        mock_consume.assert_called_once()
        mock_analyze_dream.assert_called_once_with("I was in a forest.")
        mock_generate_image.assert_called_once_with("I was in a forest.")

    def test_delete_dream_by_owner(self):
        self.client.login(username="charlie", password="testpass123")
        url = reverse("dreams_app:delete_dream", kwargs={"pk": self.dream.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Dream.objects.filter(pk=self.dream.pk).exists())

    def test_delete_dream_denied_for_other_user(self):
        self.client.login(username="dave", password="testpass123")
        url = reverse("dreams_app:delete_dream", kwargs={"pk": self.dream.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Dream.objects.filter(pk=self.dream.pk).exists())

    @patch("dreams_app.views._consume_ai_analysis", return_value=True)
    @patch("dreams_app.views.analyze_dream", return_value="Updated analysis")
    @patch("dreams_app.views.generate_dream_image", return_value=None)
    def test_update_dream_regenerates_and_redirects(
        self,
        mock_generate_image,
        mock_analyze_dream,
        mock_consume,
    ):
        self.client.login(username="charlie", password="testpass123")
        url = reverse("dreams_app:edit_dream", kwargs={"pk": self.dream.pk})

        response = self.client.post(
            url,
            data={"name": "Ocean updated", "text": "A stormy ocean dream."},
        )

        self.assertEqual(response.status_code, 302)

        self.dream.refresh_from_db()
        self.assertEqual(self.dream.name, "Ocean updated")
        self.assertEqual(self.dream.text, "A stormy ocean dream.")
        self.assertEqual(self.dream.analysis_text, "Updated analysis")

        mock_consume.assert_called_once()
        mock_analyze_dream.assert_called_once_with("A stormy ocean dream.")
        mock_generate_image.assert_called_once_with("A stormy ocean dream.")
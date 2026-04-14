from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from dreams_app.models import Dream, Favorite, AIAnalysisDailyUsage


class DreamModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            password="testpass123",
        )
        self.dream = Dream.objects.create(
            user=self.user,
            name="Flying",
            text="I was flying over the sea.",
        )

    def test_dream_str(self):
        expected_date = self.dream.created_at.strftime("%Y-%m-%d")
        self.assertEqual(str(self.dream), f"Dream by {self.user.username} on {expected_date}")

    def test_favorite_str(self):
        favorite = Favorite.objects.create(user=self.user, dream=self.dream)
        self.assertEqual(str(favorite), f"{self.user.username}'s favorite dream")

    def test_ai_usage_str(self):
        usage = AIAnalysisDailyUsage.objects.create(
            user=self.user,
            date=timezone.localdate(),
            count=2,
        )
        self.assertEqual(str(usage), f"{self.user.username} - {usage.date} (2)")
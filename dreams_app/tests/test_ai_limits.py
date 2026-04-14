from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from dreams_app.models import AIAnalysisDailyUsage
from dreams_app.views import _can_consume_ai_analysis, DAILY_AI_ANALYSIS_LIMIT


class AIUsageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="bob",
            password="testpass123",
        )
        self.today = timezone.localdate()

    def test_can_consume_when_no_usage_exists(self):
        self.assertTrue(_can_consume_ai_analysis(self.user))

    def test_can_consume_until_limit(self):
        AIAnalysisDailyUsage.objects.create(
            user=self.user,
            date=self.today,
            count=DAILY_AI_ANALYSIS_LIMIT - 1,
        )
        self.assertTrue(_can_consume_ai_analysis(self.user))

    def test_cannot_consume_when_limit_reached(self):
        AIAnalysisDailyUsage.objects.create(
            user=self.user,
            date=self.today,
            count=DAILY_AI_ANALYSIS_LIMIT,
        )
        self.assertFalse(_can_consume_ai_analysis(self.user))

    def test_staff_can_consume_unlimited(self):
        staff = User.objects.create_user(
            username="admin",
            password="testpass123",
            is_staff=True,
        )
        self.assertTrue(_can_consume_ai_analysis(staff))
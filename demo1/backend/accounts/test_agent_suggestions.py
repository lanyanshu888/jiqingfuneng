import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import (
    AgentUserBinding,
    AuthToken,
    Course,
    CourseProgress,
    GrowthPlan,
    GrowthTask,
    ProactiveSuggestion,
    YouthProfile,
)


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentSuggestionTests(TestCase):
    endpoint = "/api/agent/skills/daily-suggestion/"

    def setUp(self):
        self.user = User.objects.create_user(username="daily-user")
        self.token = AuthToken.create_for_user(self.user)
        YouthProfile.objects.create(
            user=self.user,
            nickname="小冀",
            region="河北省沧州市",
            education="本科",
            major="电子商务",
            intents=["想找工作"],
            abilities=["沟通表达"],
        )
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-daily", user=self.user,
            access_token_digest=AgentUserBinding.digest_access_token("daily-binding-token"),
        )
        self.plan = GrowthPlan.objects.create(user=self.user, goal="数字运营就业")

    def skill_post(self):
        return self.client.post(
            self.endpoint,
            data=json.dumps({
                "externalUserId": "xy-daily",
                "bindingToken": "daily-binding-token",
            }),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_overdue_task_is_first_daily_suggestion(self):
        future = GrowthTask.objects.create(
            plan=self.plan,
            stage="seven_days",
            title="查看就业政策",
            due_at=timezone.now() + timedelta(hours=12),
            status="pending",
            sequence=2,
        )
        overdue = GrowthTask.objects.create(
            plan=self.plan,
            stage="seven_days",
            title="完善简历",
            due_at=timezone.now() - timedelta(hours=1),
            status="pending",
            sequence=1,
        )

        response = self.skill_post()
        suggestions = response.json()["data"]["suggestions"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(suggestions[0]["taskId"], overdue.id)
        self.assertEqual(suggestions[0]["priority"], "urgent")
        self.assertEqual(suggestions[1]["taskId"], future.id)

    def test_same_daily_trigger_is_not_saved_twice(self):
        GrowthTask.objects.create(
            plan=self.plan,
            stage="seven_days",
            title="完善简历",
            due_at=timezone.now() - timedelta(hours=1),
        )

        self.skill_post()
        self.skill_post()

        self.assertEqual(ProactiveSuggestion.objects.filter(user=self.user).count(), 1)

    def test_logged_in_miniprogram_reads_same_dashboard(self):
        GrowthTask.objects.create(
            plan=self.plan,
            stage="seven_days",
            title="完善简历",
            due_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get(
            "/api/agent/me/dashboard/",
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["plan"]["goal"], "数字运营就业")
        self.assertEqual(response.json()["suggestions"][0]["priority"], "urgent")

    def test_completed_resource_is_not_recommended_again(self):
        course = Course.objects.create(
            title="已完成数字运营课", status="published", tags=["数字运营"]
        )
        CourseProgress.objects.create(
            user=self.user,
            course=course,
            completed=True,
            completed_at=timezone.now(),
        )

        response = self.skill_post()

        resource_suggestions = [
            item for item in response.json()["data"]["suggestions"]
            if item["suggestionType"] == "resource"
        ]
        self.assertEqual(resource_suggestions, [])

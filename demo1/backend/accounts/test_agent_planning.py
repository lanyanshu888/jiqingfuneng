import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import AgentUserBinding, GrowthEvent, GrowthPlan, YouthProfile


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentPlanningTests(TestCase):
    endpoint = "/api/agent/skills/career-plan/"

    def setUp(self):
        self.user = User.objects.create_user(username="plan-user")
        self.profile = YouthProfile.objects.create(
            user=self.user,
            nickname="小冀",
            region="河北省沧州市黄骅市",
            education="本科",
            major="电子商务",
            intents=["想找工作"],
            abilities=["沟通表达"],
            tags=["数字运营"],
        )
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-plan", user=self.user
        )

    def skill_post(self, payload):
        return self.client.post(
            self.endpoint,
            data=json.dumps({"externalUserId": "xy-plan", **payload}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_career_plan_creates_three_stages(self):
        response = self.skill_post({"goal": "在县域从事数字运营"})

        self.assertTrue(response.json()["ok"])
        plan = GrowthPlan.objects.get(user=self.user, status="active")
        self.assertEqual(
            set(plan.tasks.values_list("stage", flat=True)),
            {"seven_days", "one_month", "three_months"},
        )
        self.assertGreaterEqual(plan.tasks.count(), 6)
        self.assertTrue(GrowthEvent.objects.filter(
            user=self.user, event_type="growth_plan_created"
        ).exists())

    def test_career_plan_rejects_missing_goal(self):
        response = self.skill_post({"goal": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "PROFILE_INCOMPLETE")
        self.assertEqual(response.json()["data"]["missingFields"], ["goal"])
        self.assertFalse(GrowthPlan.objects.filter(user=self.user).exists())

    def test_new_plan_replaces_previous_active_plan(self):
        old = GrowthPlan.objects.create(user=self.user, goal="旧目标")

        response = self.skill_post({"goal": "在县域从事数字运营"})

        old.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(old.status, "replaced")
        self.assertEqual(GrowthPlan.objects.filter(user=self.user, status="active").count(), 1)

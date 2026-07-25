import json
import os
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase, override_settings

from .models import AgentToolLog, Enrollment, GrowthEvent, GrowthPlan


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentDemoFlowTests(TestCase):
    def skill_post(self, endpoint, external_user_id, payload=None):
        return self.client.post(
            endpoint,
            data=json.dumps({
                "externalUserId": external_user_id,
                **(payload or {}),
            }),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_complete_binding_to_daily_suggestion_flow(self):
        with patch.dict(os.environ, {"JIQING_DEMO_PASSWORD": "demo-pass-2026"}):
            call_command("seed_demo_data")

        login = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": "demo_youth", "password": "demo-pass-2026"}),
            content_type="application/json",
        )
        token = login.json()["token"]
        generated = self.client.post(
            "/api/agent/binding-code/",
            HTTP_AUTHORIZATION=f"Token {token}",
        )
        external_user_id = "xiaoyi-demo-user"
        bound = self.client.post(
            "/api/agent/bind/",
            data=json.dumps({
                "externalUserId": external_user_id,
                "code": generated.json()["code"],
            }),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )
        self.assertNotIn("bindingToken", bound.json().get("data", {}))
        profile = self.skill_post(
            "/api/agent/skills/profile-context/", external_user_id
        )
        plan = self.skill_post(
            "/api/agent/skills/career-plan/",
            external_user_id,
            {"goal": "在河北县域从事数字运营"},
        )
        policies = self.skill_post(
            "/api/agent/skills/policy-search/",
            external_user_id,
            {"keyword": "就业", "region": "沧州"},
        )
        resources = self.skill_post(
            "/api/agent/skills/resource-match/",
            external_user_id,
            {"resourceTypes": ["activity"]},
        )
        activity_id = resources.json()["data"]["items"][0]["resourceId"]
        preview = self.skill_post(
            "/api/agent/skills/growth-action/",
            external_user_id,
            {"action": "enroll_activity", "resourceId": activity_id},
        )
        executed = self.skill_post(
            "/api/agent/skills/growth-action/",
            external_user_id,
            {
                "action": "enroll_activity",
                "resourceId": activity_id,
                "confirmed": True,
                "confirmationToken": preview.json()["data"]["confirmationToken"],
            },
        )
        daily = self.skill_post(
            "/api/agent/skills/daily-suggestion/", external_user_id
        )

        self.assertEqual(bound.status_code, 200)
        self.assertEqual(profile.json()["data"]["missingFields"], [])
        self.assertEqual(plan.status_code, 201)
        self.assertTrue(policies.json()["sources"])
        self.assertEqual(executed.status_code, 201)
        self.assertTrue(daily.json()["data"]["suggestions"])
        self.assertTrue(Enrollment.objects.exists())
        self.assertTrue(GrowthPlan.objects.filter(status="active").exists())
        self.assertTrue(GrowthEvent.objects.filter(event_type="activity_enrolled").exists())
        self.assertGreaterEqual(AgentToolLog.objects.count(), 7)

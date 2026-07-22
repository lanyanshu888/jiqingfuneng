import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import AgentUserBinding, GrowthEvent, YouthProfile


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentProfileTests(TestCase):
    endpoint = "/api/agent/skills/profile-context/"

    def setUp(self):
        self.user = User.objects.create_user(username="profile-user")
        self.profile = YouthProfile.objects.create(
            user=self.user,
            nickname="小冀",
            education="本科",
            intents=["想找工作"],
        )
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-profile", user=self.user
        )

    def skill_post(self, payload):
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_reads_bound_users_profile_and_missing_fields(self):
        GrowthEvent.objects.create(user=self.user, event_type="course_completed")

        response = self.skill_post({"externalUserId": "xy-profile"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["profile"]["nickname"], "小冀")
        self.assertEqual(
            response.json()["data"]["missingFields"],
            ["region", "major", "abilities"],
        )
        self.assertEqual(
            response.json()["data"]["recentGrowth"][0]["eventType"],
            "course_completed",
        )

    def test_profile_update_requires_explicit_confirmation(self):
        response = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": {"region": "河北省沧州市"},
            "confirmed": False,
        })

        self.assertTrue(response.json()["requiresConfirmation"])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.region, "")

    def test_confirmed_update_saves_only_allowed_fields(self):
        response = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": {
                "region": "河北省沧州市",
                "major": "电子商务",
                "user": 999,
            },
            "confirmed": True,
        })

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.region, "河北省沧州市")
        self.assertEqual(self.profile.major, "电子商务")
        self.assertEqual(self.profile.user, self.user)
        self.assertTrue(GrowthEvent.objects.filter(
            user=self.user, event_type="profile_updated_by_agent"
        ).exists())

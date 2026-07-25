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
            platform="xiaoyi", external_user_id="xy-profile", user=self.user,
            access_token_digest=AgentUserBinding.digest_access_token("profile-binding-token"),
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

    def test_string_false_does_not_count_as_profile_confirmation(self):
        response = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": {"region": "河北省沧州市"},
            "confirmed": "false",
        })

        self.assertTrue(response.json()["requiresConfirmation"])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.region, "")

    def test_confirmed_update_saves_only_allowed_fields(self):
        changes = {
            "region": "河北省沧州市",
            "major": "电子商务",
            "user": 999,
        }
        preview = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": changes,
            "confirmed": False,
        }).json()
        response = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": changes,
            "confirmed": True,
            "confirmationToken": preview["data"]["confirmationToken"],
        })

        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.profile.region, "河北省沧州市")
        self.assertEqual(self.profile.major, "电子商务")
        self.assertEqual(self.profile.user, self.user)
        self.assertTrue(GrowthEvent.objects.filter(
            user=self.user, event_type="profile_updated_by_agent"
        ).exists())

    def test_profile_confirmation_token_rejects_changed_fields(self):
        preview = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": {"region": "河北省沧州市"},
            "confirmed": False,
        }).json()

        response = self.skill_post({
            "externalUserId": "xy-profile",
            "operation": "update",
            "changes": {"region": "河北省石家庄市"},
            "confirmed": True,
            "confirmationToken": preview["data"]["confirmationToken"],
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "CONFIRMATION_MISMATCH")
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.region, "")

    # --- operation缺失、未绑定、鉴权失败、响应结构 ---

    def test_missing_operation_defaults_to_read(self):
        """不传 operation 默认按 read 处理，正常返回画像"""
        response = self.skill_post({"externalUserId": "xy-profile"})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["data"]["profile"]["nickname"], "小冀")

    def test_unbound_user_returns_correct_error(self):
        response = self.skill_post({"externalUserId": "xy-never-bound"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()["ok"])
        self.assertEqual(response.json()["errorCode"], "AGENT_USER_NOT_BOUND")
        self.assertIn("尚未绑定", response.json()["message"])

    def test_response_contains_all_standard_fields(self):
        response = self.skill_post({"externalUserId": "xy-profile"})
        body = response.json()
        for field in ("ok", "message", "data", "sources", "requiresConfirmation", "errorCode"):
            self.assertIn(field, body, f"缺少字段: {field}")

    def test_error_response_contains_all_standard_fields(self):
        response = self.skill_post({"externalUserId": "xy-never-bound"})
        body = response.json()
        for field in ("ok", "message", "data", "sources", "requiresConfirmation", "errorCode"):
            self.assertIn(field, body, f"错误响应缺少字段: {field}")
        self.assertIsInstance(body["data"], dict)
        self.assertIsInstance(body["sources"], list)

    def test_missing_service_key_returns_401_json(self):
        response = self.client.post(
            self.endpoint,
            data=json.dumps({"externalUserId": "xy-profile"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        body = response.json()
        self.assertFalse(body["ok"])
        self.assertEqual(body["errorCode"], "INVALID_SERVICE_CREDENTIAL")

    def test_no_csrf_or_login_redirect(self):
        response = self.client.post(
            self.endpoint,
            data=json.dumps({"externalUserId": "xy-profile"}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )
        self.assertIn(response.status_code, [200, 403])
        self.assertEqual(response["Content-Type"], "application/json")

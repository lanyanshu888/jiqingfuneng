import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import AgentToolLog, AgentUserBinding


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentSecurityTests(TestCase):
    endpoint = "/api/agent/skills/profile-context/"

    def post(self, payload, key=None):
        headers = {}
        if key is not None:
            headers["HTTP_X_AGENT_SERVICE_KEY"] = key
        return self.client.post(
            self.endpoint,
            data=json.dumps(payload),
            content_type="application/json",
            **headers,
        )

    def test_skill_rejects_missing_service_key_with_common_protocol(self):
        response = self.post({"externalUserId": "xy-001"})

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {
            "ok": False,
            "message": "Agent 服务凭据无效",
            "data": {},
            "sources": [],
            "requiresConfirmation": False,
            "errorCode": "INVALID_SERVICE_CREDENTIAL",
        })

    def test_skill_rejects_wrong_service_key(self):
        response = self.post({"externalUserId": "xy-001"}, key="wrong-key")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["errorCode"], "INVALID_SERVICE_CREDENTIAL")

    def test_skill_rejects_unbound_external_user_and_logs_call(self):
        response = self.post({"externalUserId": "xy-missing"}, key="test-agent-key")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["errorCode"], "AGENT_USER_NOT_BOUND")
        log = AgentToolLog.objects.get()
        self.assertIsNone(log.user)
        self.assertEqual(log.skill_name, "profile_context")
        self.assertEqual(log.result_status, "error")
        self.assertEqual(log.request_summary["fields"], ["externalUserId"])

    def test_skill_resolves_only_active_binding(self):
        user = User.objects.create_user(username="bound")
        AgentUserBinding.objects.create(
            platform="xiaoyi",
            external_user_id="xy-disabled",
            user=user,
            is_active=False,
        )

        response = self.post({"externalUserId": "xy-disabled"}, key="test-agent-key")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["errorCode"], "AGENT_USER_NOT_BOUND")

    def test_external_user_id_cannot_be_used_without_its_binding_token(self):
        victim = User.objects.create_user(username="victim")
        AgentUserBinding.objects.create(
            platform="xiaoyi",
            external_user_id="xy-victim",
            user=victim,
            access_token_digest=AgentUserBinding.digest_access_token("victim-secret-token"),
        )

        response = self.post(
            {
                "externalUserId": "xy-victim",
                "bindingToken": "attacker-token",
            },
            key="test-agent-key",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["errorCode"], "AGENT_BINDING_TOKEN_INVALID")

import hashlib
import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import AgentBindingCode, AgentUserBinding, AuthToken


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentBindingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="bind-user")
        self.token = AuthToken.create_for_user(self.user)

    def generate_code(self):
        return self.client.post(
            "/api/agent/binding-code/",
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

    def bind(self, external_user_id, code):
        return self.client.post(
            "/api/agent/bind/",
            data=json.dumps({"externalUserId": external_user_id, "code": code}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_logged_in_user_generates_six_digit_hashed_code(self):
        response = self.generate_code()

        self.assertEqual(response.status_code, 201)
        self.assertRegex(response.json()["code"], r"^\d{6}$")
        self.assertEqual(response.json()["expiresIn"], 600)
        stored = AgentBindingCode.objects.get(user=self.user)
        self.assertNotEqual(stored.code_digest, response.json()["code"])
        self.assertEqual(
            stored.code_digest,
            hashlib.sha256(response.json()["code"].encode()).hexdigest(),
        )

    def test_code_binds_xiaoyi_identity_once(self):
        code = self.generate_code().json()["code"]

        bound = self.bind("xy-001", code)
        repeated = self.bind("xy-002", code)

        self.assertEqual(bound.status_code, 200)
        self.assertEqual(bound.json()["data"]["bound"], True)
        self.assertEqual(repeated.status_code, 400)
        self.assertEqual(repeated.json()["errorCode"], "BINDING_CODE_INVALID")
        self.assertTrue(AgentUserBinding.objects.filter(
            platform="xiaoyi", external_user_id="xy-001", user=self.user, is_active=True
        ).exists())

    def test_expired_code_is_rejected(self):
        code = self.generate_code().json()["code"]
        AgentBindingCode.objects.filter(user=self.user).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

        response = self.bind("xy-expired", code)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "BINDING_CODE_EXPIRED")

    def test_binding_requires_external_user_id(self):
        code = self.generate_code().json()["code"]

        response = self.bind("", code)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "EXTERNAL_ID_REQUIRED")

    def test_new_external_identity_replaces_users_old_binding(self):
        old = AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-old", user=self.user
        )
        code = self.generate_code().json()["code"]

        response = self.bind("xy-new", code)

        old.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(old.is_active)
        self.assertTrue(AgentUserBinding.objects.get(external_user_id="xy-new").is_active)

    def test_bind_rejects_malformed_json_with_stable_protocol(self):
        response = self.client.post(
            "/api/agent/bind/",
            data="{broken",
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "INVALID_JSON")

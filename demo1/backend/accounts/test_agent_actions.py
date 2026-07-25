import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import signing
from django.test import TestCase, override_settings

from .models import (
    Activity,
    AgentUserBinding,
    Enrollment,
    Favorite,
    GrowthEvent,
    Policy,
)


@override_settings(
    AGENT_SERVICE_KEY="test-agent-key",
    AGENT_CONFIRMATION_MAX_AGE_SECONDS=300,
)
class AgentActionTests(TestCase):
    endpoint = "/api/agent/skills/growth-action/"

    def setUp(self):
        self.user = User.objects.create_user(username="action-user")
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-action", user=self.user,
            access_token_digest=AgentUserBinding.digest_access_token("action-binding-token"),
        )
        self.activity = Activity.objects.create(title="县域成长营", status="published")

    def skill_post(self, payload):
        return self.client.post(
            self.endpoint,
            data=json.dumps({
                "externalUserId": "xy-action",
                **payload,
            }),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_activity_enrollment_only_executes_after_confirmation(self):
        preview = self.skill_post({
            "action": "enroll_activity", "resourceId": self.activity.id
        }).json()

        self.assertTrue(preview["requiresConfirmation"])
        self.assertFalse(Enrollment.objects.filter(user=self.user).exists())

        executed = self.skill_post({
            "action": "enroll_activity",
            "resourceId": self.activity.id,
            "confirmed": True,
            "confirmationToken": preview["data"]["confirmationToken"],
        })

        self.assertEqual(executed.status_code, 201)
        self.assertTrue(Enrollment.objects.filter(
            user=self.user, activity=self.activity
        ).exists())
        self.assertTrue(GrowthEvent.objects.filter(
            user=self.user, event_type="activity_enrolled"
        ).exists())

    def test_string_false_does_not_count_as_action_confirmation(self):
        response = self.skill_post({
            "action": "enroll_activity",
            "resourceId": self.activity.id,
            "confirmed": "false",
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["requiresConfirmation"])
        self.assertFalse(Enrollment.objects.filter(user=self.user).exists())

    def test_confirmation_token_rejects_changed_resource(self):
        other = Activity.objects.create(title="另一个活动", status="published")
        token = self.skill_post({
            "action": "enroll_activity", "resourceId": self.activity.id
        }).json()["data"]["confirmationToken"]

        response = self.skill_post({
            "action": "enroll_activity",
            "resourceId": other.id,
            "confirmed": True,
            "confirmationToken": token,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errorCode"], "CONFIRMATION_MISMATCH")
        self.assertFalse(Enrollment.objects.exists())

    def test_expired_confirmation_token_is_rejected(self):
        token = self.skill_post({
            "action": "enroll_activity", "resourceId": self.activity.id
        }).json()["data"]["confirmationToken"]

        with patch("accounts.agent_actions.signing.loads", side_effect=signing.SignatureExpired):
            response = self.skill_post({
                "action": "enroll_activity",
                "resourceId": self.activity.id,
                "confirmed": True,
                "confirmationToken": token,
            })

        self.assertEqual(response.json()["errorCode"], "CONFIRMATION_EXPIRED")

    def test_favorite_action_is_additive_and_idempotent(self):
        policy = Policy.objects.create(title="就业政策", status="published")
        preview = self.skill_post({
            "action": "favorite_resource",
            "resourceType": "policy",
            "resourceId": policy.id,
        }).json()
        payload = {
            "action": "favorite_resource",
            "resourceType": "policy",
            "resourceId": policy.id,
            "confirmed": True,
            "confirmationToken": preview["data"]["confirmationToken"],
        }

        first = self.skill_post(payload)
        second = self.skill_post(payload)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Favorite.objects.filter(user=self.user).count(), 1)

    def test_expired_policy_cannot_be_favorited(self):
        expired = Policy.objects.create(
            title="过期政策",
            status="published",
            source="人社部门",
            effective_until=date.today() - timedelta(days=1),
        )

        response = self.skill_post({
            "action": "favorite_resource",
            "resourceType": "policy",
            "resourceId": expired.id,
        })

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["errorCode"], "RESOURCE_UNAVAILABLE")

    def test_full_activity_cannot_accept_another_enrollment(self):
        full_activity = Activity.objects.create(
            title="满员活动", status="published", capacity=1
        )
        other = User.objects.create_user(username="already-enrolled")
        Enrollment.objects.create(user=other, activity=full_activity)

        response = self.skill_post({
            "action": "enroll_activity", "resourceId": full_activity.id
        })

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()["errorCode"], "ACTIVITY_FULL")

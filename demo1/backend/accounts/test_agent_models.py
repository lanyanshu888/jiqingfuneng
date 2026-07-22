from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import (
    AgentBindingCode,
    AgentToolLog,
    AgentUserBinding,
    GrowthPlan,
    GrowthTask,
    ProactiveSuggestion,
)


class AgentModelTests(TestCase):
    def test_external_identity_is_unique_per_platform(self):
        user = User.objects.create_user(username="agent-user")
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-001", user=user
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            AgentUserBinding.objects.create(
                platform="xiaoyi", external_user_id="xy-001", user=user
            )

    def test_binding_code_digest_is_unique(self):
        user = User.objects.create_user(username="code-user")
        AgentBindingCode.objects.create(
            user=user,
            code_digest="a" * 64,
            expires_at="2026-07-22T22:00:00+08:00",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            AgentBindingCode.objects.create(
                user=user,
                code_digest="a" * 64,
                expires_at="2026-07-22T22:10:00+08:00",
            )

    def test_growth_plan_has_three_stage_tasks(self):
        user = User.objects.create_user(username="planner")
        plan = GrowthPlan.objects.create(user=user, goal="县域数字运营就业")
        for stage in ("seven_days", "one_month", "three_months"):
            GrowthTask.objects.create(plan=plan, stage=stage, title=stage)

        self.assertEqual(
            set(plan.tasks.values_list("stage", flat=True)),
            {"seven_days", "one_month", "three_months"},
        )

    def test_logs_and_suggestions_are_linked_to_user(self):
        user = User.objects.create_user(username="tracked-user")
        log = AgentToolLog.objects.create(
            user=user,
            skill_name="profile_context",
            request_summary={"fields": ["externalUserId"]},
            result_status="success",
            duration_ms=18,
        )
        suggestion = ProactiveSuggestion.objects.create(
            user=user,
            suggestion_type="profile",
            content="完善你的专业信息",
            trigger_reason="missing:major",
            scheduled_for="2026-07-22T09:00:00+08:00",
        )

        self.assertEqual(log.user, user)
        self.assertEqual(suggestion.user, user)

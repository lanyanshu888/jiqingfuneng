import json
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .models import (
    Activity,
    AgentUserBinding,
    Course,
    Mentor,
    Opportunity,
    Policy,
    YouthProfile,
)


@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentMatchingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="match-user")
        YouthProfile.objects.create(
            user=self.user,
            region="河北省沧州市黄骅市",
            education="本科",
            major="电子商务",
            intents=["想找工作", "想提升技能"],
            tags=["数字运营", "县域就业"],
        )
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-match", user=self.user
        )

    def skill_post(self, endpoint, payload):
        return self.client.post(
            endpoint,
            data=json.dumps({"externalUserId": "xy-match", **payload}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )

    def test_policy_search_only_returns_current_sourced_results(self):
        current = Policy.objects.create(
            title="沧州青年就业补贴",
            status="published",
            region="沧州",
            source="沧州市人社局",
            target="高校毕业生就业",
            support="就业补贴",
            effective_until=date.today() + timedelta(days=30),
        )
        Policy.objects.create(
            title="过期就业补贴",
            status="published",
            region="沧州",
            source="旧文件",
            effective_until=date.today() - timedelta(days=1),
        )
        Policy.objects.create(
            title="草稿就业补贴", status="draft", region="沧州", source="草稿"
        )

        response = self.skill_post(
            "/api/agent/skills/policy-search/",
            {"keyword": "就业", "region": "沧州"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["id"] for item in response.json()["data"]["items"]],
            [current.id],
        )
        self.assertEqual(response.json()["sources"][0]["publisher"], "沧州市人社局")

    def test_policy_search_returns_honest_empty_result(self):
        response = self.skill_post(
            "/api/agent/skills/policy-search/", {"keyword": "不存在的政策"}
        )

        self.assertEqual(response.json()["data"]["items"], [])
        self.assertEqual(response.json()["sources"], [])
        self.assertIn("暂未找到", response.json()["message"])

    def test_resource_match_scores_and_explains_all_resource_types(self):
        Opportunity.objects.create(
            title="黄骅数字运营岗位",
            status="published",
            region="沧州黄骅",
            education="本科",
            major="电子商务",
            tags=["数字运营", "县域就业"],
            deadline=date.today() + timedelta(days=20),
        )
        Opportunity.objects.create(
            title="外地行政岗位", status="published", region="邯郸", tags=["行政"]
        )
        Course.objects.create(
            title="数字运营实训课", status="published", tags=["数字运营"]
        )
        Activity.objects.create(
            title="县域青年实践营", status="published", tags=["县域就业"]
        )
        Mentor.objects.create(
            title="电商导师王老师", status="published", good_at="电子商务与数字运营"
        )

        response = self.skill_post(
            "/api/agent/skills/resource-match/",
            {"resourceTypes": ["opportunity", "course", "activity", "mentor"]},
        )
        items = response.json()["data"]["items"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual({item["resourceType"] for item in items}, {
            "opportunity", "course", "activity", "mentor"
        })
        best_opportunity = next(item for item in items if item["resourceType"] == "opportunity")
        self.assertEqual(best_opportunity["title"], "黄骅数字运营岗位")
        self.assertGreaterEqual(best_opportunity["score"], 70)
        self.assertTrue(best_opportunity["reasons"])

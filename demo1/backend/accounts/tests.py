from django.contrib.auth.models import User
from django.contrib import admin
from django.db import IntegrityError
from django.core.management import call_command
from django.test import TestCase

from .models import Activity, AuthToken, Course, CourseProgress, Enrollment, Favorite, GrowthEvent, Mentor, MentorConsultation, Opportunity, Policy, YouthProfile


class ApiAuthenticationTests(TestCase):
    def test_profile_endpoint_rejects_unauthenticated_request(self):
        response = self.client.get("/api/profiles/me/")

        self.assertEqual(response.status_code, 401)


class EnrollmentModelTests(TestCase):
    def test_same_user_cannot_enroll_in_same_activity_twice(self):
        user = User.objects.create_user(username="youth", password="secret123")
        activity = Activity.objects.create(title="成长营")
        Enrollment.objects.create(user=user, activity=activity)

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(user=user, activity=activity)


class PolicyApiTests(TestCase):
    def test_policy_list_only_returns_published_and_current_policies(self):
        Policy.objects.create(title="可展示", status="published", effective_until="2026-12-31")
        Policy.objects.create(title="草稿", status="draft", effective_until="2026-12-31")
        Policy.objects.create(title="过期", status="published", effective_until="2020-01-01")

        response = self.client.get("/api/policies/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["title"] for item in response.json()["items"]], ["可展示"])

    def test_policy_detail_returns_a_published_policy(self):
        policy = Policy.objects.create(title="可展示", status="published", source="人社部门")

        response = self.client.get(f"/api/policies/{policy.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "可展示")
        self.assertEqual(response.json()["source"], "人社部门")


class ResourceApiTests(TestCase):
    def test_resource_lists_only_return_published_items(self):
        Opportunity.objects.create(title="可展示岗位", status="published")
        Opportunity.objects.create(title="草稿岗位", status="draft")
        Course.objects.create(title="可展示课程", status="published")
        Activity.objects.create(title="可展示活动", status="published")

        opportunity_response = self.client.get("/api/opportunities/")
        course_response = self.client.get("/api/courses/")
        activity_response = self.client.get("/api/activities/")

        self.assertEqual([item["title"] for item in opportunity_response.json()["items"]], ["可展示岗位"])
        self.assertEqual([item["title"] for item in course_response.json()["items"]], ["可展示课程"])
        self.assertEqual([item["title"] for item in activity_response.json()["items"]], ["可展示活动"])

    def test_resource_detail_endpoints_return_published_resources(self):
        opportunity = Opportunity.objects.create(title="实习", status="published")
        course = Course.objects.create(title="课程", status="published")
        activity = Activity.objects.create(title="活动", status="published")

        self.assertEqual(self.client.get(f"/api/opportunities/{opportunity.id}/").json()["title"], "实习")
        self.assertEqual(self.client.get(f"/api/courses/{course.id}/").json()["title"], "课程")
        self.assertEqual(self.client.get(f"/api/activities/{activity.id}/").json()["title"], "活动")


class DemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_published_resources(self):
        call_command("seed_demo_data")

        self.assertGreater(Policy.objects.filter(status="published").count(), 0)
        self.assertGreater(Opportunity.objects.filter(status="published").count(), 0)
        self.assertGreater(Course.objects.filter(status="published").count(), 0)
        self.assertGreater(Activity.objects.filter(status="published").count(), 0)


class RecommendationApiTests(TestCase):
    def test_recommendations_prioritize_matching_region_and_intent(self):
        user = User.objects.create_user(username="recommend", password="secret123")
        token = AuthToken.create_for_user(user)
        YouthProfile.objects.create(
            user=user,
            region="沧州黄骅市",
            intents=["想找实习"],
            tags=["实习优先"],
        )
        Opportunity.objects.create(title="外地岗位", status="published", region="石家庄市", tags=["岗位匹配"])
        Opportunity.objects.create(title="本地实习", status="published", region="沧州黄骅市", tags=["实习优先"])

        response = self.client.get("/api/recommendations/", HTTP_AUTHORIZATION=f"Token {token.key}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["opportunity"]["title"], "本地实习")


class MentorConsultationApiTests(TestCase):
    def test_consultation_is_saved_and_returned_in_growth_records(self):
        user = User.objects.create_user(username="consult", password="secret123")
        token = AuthToken.create_for_user(user)
        mentor = Mentor.objects.create(title="赵老师", status="published", available="周日")
        headers = {"HTTP_AUTHORIZATION": f"Token {token.key}"}

        response = self.client.post(
            f"/api/mentors/{mentor.id}/consult/",
            data='{"question":"如何准备创业计划书？"}',
            content_type="application/json",
            **headers,
        )
        records = self.client.get("/api/me/growth/", **headers)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(MentorConsultation.objects.filter(user=user, mentor=mentor).exists())
        self.assertEqual(records.json()["consultations"][0]["question"], "如何准备创业计划书？")


class AdminRegistrationTests(TestCase):
    def test_growth_resources_are_registered_in_django_admin(self):
        for model in (Policy, Opportunity, Course, Activity, Mentor, Enrollment, CourseProgress, MentorConsultation):
            self.assertTrue(admin.site.is_registered(model), model.__name__)


class FavoriteApiTests(TestCase):
    def test_favorite_endpoint_toggles_and_growth_records_include_favorite(self):
        user = User.objects.create_user(username="favorite", password="secret123")
        token = AuthToken.create_for_user(user)
        policy = Policy.objects.create(title="就业政策", status="published")
        headers = {"HTTP_AUTHORIZATION": f"Token {token.key}"}
        payload = f'{{"resourceType":"policy","resourceId":{policy.id}}}'

        added = self.client.post("/api/favorites/toggle/", data=payload, content_type="application/json", **headers)
        records = self.client.get("/api/me/growth/", **headers)
        removed = self.client.post("/api/favorites/toggle/", data=payload, content_type="application/json", **headers)

        self.assertEqual(added.json()["favorited"], True)
        self.assertEqual(records.json()["favorites"][0]["title"], "就业政策")
        self.assertEqual(removed.json()["favorited"], False)
        self.assertFalse(Favorite.objects.filter(user=user).exists())


class EnrollmentApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="applicant", password="secret123")
        self.token = AuthToken.create_for_user(self.user)
        self.activity = Activity.objects.create(title="成长营", status="published")

    def test_activity_enrollment_is_saved_and_second_request_conflicts(self):
        headers = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

        first = self.client.post(f"/api/activities/{self.activity.id}/enroll/", **headers)
        second = self.client.post(f"/api/activities/{self.activity.id}/enroll/", **headers)

        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)
        self.assertTrue(Enrollment.objects.filter(user=self.user, activity=self.activity).exists())
        self.assertTrue(GrowthEvent.objects.filter(user=self.user, event_type="activity_enrolled").exists())

    def test_course_completion_is_saved(self):
        course = Course.objects.create(title="简历课", status="published")
        headers = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

        response = self.client.post(f"/api/courses/{course.id}/complete/", **headers)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(CourseProgress.objects.filter(user=self.user, course=course, completed=True).exists())
        self.assertTrue(GrowthEvent.objects.filter(user=self.user, event_type="course_completed").exists())

    def test_opportunity_enrollment_is_saved(self):
        opportunity = Opportunity.objects.create(title="数字运营实习", status="published")
        headers = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

        response = self.client.post(f"/api/opportunities/{opportunity.id}/enroll/", **headers)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Enrollment.objects.filter(user=self.user, opportunity=opportunity).exists())
        self.assertTrue(GrowthEvent.objects.filter(user=self.user, event_type="opportunity_enrolled").exists())

    def test_growth_records_return_current_users_enrollments_and_courses(self):
        course = Course.objects.create(title="简历课", status="published")
        Enrollment.objects.create(user=self.user, activity=self.activity)
        CourseProgress.objects.create(user=self.user, course=course, completed=True)
        headers = {"HTTP_AUTHORIZATION": f"Token {self.token.key}"}

        response = self.client.get("/api/me/growth/", **headers)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["activities"][0]["title"], "成长营")
        self.assertEqual(response.json()["courses"][0]["title"], "简历课")

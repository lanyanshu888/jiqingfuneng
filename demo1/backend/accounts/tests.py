from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Activity, AuthToken, Course, CourseProgress, Enrollment, GrowthEvent, Opportunity, Policy


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

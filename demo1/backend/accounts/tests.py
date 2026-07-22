from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from .models import Activity, Enrollment


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

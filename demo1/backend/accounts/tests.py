from django.test import TestCase


class ApiAuthenticationTests(TestCase):
    def test_profile_endpoint_rejects_unauthenticated_request(self):
        response = self.client.get("/api/profiles/me/")

        self.assertEqual(response.status_code, 401)

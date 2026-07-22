from pathlib import Path

import yaml
from django.test import SimpleTestCase


OPENAPI_PATH = Path(__file__).resolve().parents[3] / "xiaoyi-agent" / "openapi.yaml"


class XiaoyiContractTests(SimpleTestCase):
    def load_document(self):
        return yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))

    def test_openapi_declares_binding_and_all_agent_skills(self):
        document = self.load_document()
        operation_ids = {
            operation["operationId"]
            for path_item in document["paths"].values()
            for method, operation in path_item.items()
            if method.lower() in {"get", "post", "put", "patch", "delete"}
        }
        self.assertEqual(operation_ids, {
            "bindAccount",
            "profileContext",
            "careerPlan",
            "policySearch",
            "resourceMatch",
            "growthAction",
            "dailySuggestion",
        })

    def test_openapi_defines_service_key_and_common_response(self):
        document = self.load_document()
        service_key = document["components"]["securitySchemes"]["AgentServiceKey"]
        response_fields = document["components"]["schemas"]["AgentResponse"]["properties"]

        self.assertEqual(service_key["name"], "X-Agent-Service-Key")
        self.assertEqual(service_key["in"], "header")
        self.assertTrue({
            "ok", "message", "data", "sources", "requiresConfirmation", "errorCode"
        }.issubset(response_fields))

    def test_growth_action_requires_confirmation_fields(self):
        document = self.load_document()
        schema = document["paths"]["/agent/skills/growth-action/"]["post"][
            "requestBody"
        ]["content"]["application/json"]["schema"]
        properties = schema["properties"]

        self.assertIn("confirmed", properties)
        self.assertIn("confirmationToken", properties)

    def test_every_skill_requires_binding_token(self):
        document = self.load_document()
        skill_paths = [
            path for path in document["paths"]
            if path.startswith("/agent/skills/")
        ]
        for path in skill_paths:
            schema = document["paths"][path]["post"]["requestBody"][
                "content"
            ]["application/json"]["schema"]
            self.assertIn("bindingToken", schema["required"], path)
            self.assertIn("bindingToken", schema["properties"], path)

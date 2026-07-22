import os
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase


BACKEND_DIR = Path(__file__).resolve().parents[1]


class DeploymentSettingsTests(SimpleTestCase):
    def run_manage(self, *args, **overrides):
        env = os.environ.copy()
        env.update(overrides)
        return subprocess.run(
            [sys.executable, "manage.py", *args],
            cwd=BACKEND_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_production_rejects_default_secret_key(self):
        result = self.run_manage(
            "check",
            JIQING_DEBUG="false",
            JIQING_SECRET_KEY="dev-only-change-before-deploy",
            JIQING_AGENT_SERVICE_KEY="a" * 32,
            JIQING_ALLOWED_HOSTS="agent.example.com",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JIQING_SECRET_KEY", result.stderr)

    def test_production_rejects_short_agent_service_key(self):
        result = self.run_manage(
            "check",
            JIQING_DEBUG="false",
            JIQING_SECRET_KEY="s" * 50,
            JIQING_AGENT_SERVICE_KEY="short",
            JIQING_ALLOWED_HOSTS="agent.example.com",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JIQING_AGENT_SERVICE_KEY", result.stderr)

    def test_production_requires_explicit_allowed_hosts(self):
        result = self.run_manage(
            "check",
            JIQING_DEBUG="false",
            JIQING_SECRET_KEY="s" * 50,
            JIQING_AGENT_SERVICE_KEY="a" * 32,
            JIQING_ALLOWED_HOSTS="",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JIQING_ALLOWED_HOSTS", result.stderr)

    def test_production_accepts_explicit_secure_environment(self):
        result = self.run_manage(
            "check",
            JIQING_DEBUG="false",
            JIQING_SECRET_KEY="s" * 50,
            JIQING_AGENT_SERVICE_KEY="a" * 32,
            JIQING_ALLOWED_HOSTS="agent.example.com",
            JIQING_SQLITE_PATH="/tmp/jiqing-settings-test.sqlite3",
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_sqlite_path_comes_from_environment(self):
        expected = "/tmp/jiqing-settings-test.sqlite3"
        result = self.run_manage(
            "shell",
            "-c",
            "from django.conf import settings; print(settings.DATABASES['default']['NAME'])",
            JIQING_SQLITE_PATH=expected,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), expected)

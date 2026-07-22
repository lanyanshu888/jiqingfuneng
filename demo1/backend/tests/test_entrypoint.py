import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENTRYPOINT = BACKEND_DIR / "docker-entrypoint.sh"


class EntrypointTests(unittest.TestCase):
    def make_command(self, directory, name):
        path = Path(directory) / name
        path.write_text(
            '#!/bin/sh\nprintf "%s %s\\n" "$0" "$*" >> "$TRACE_FILE"\n',
            encoding="utf-8",
        )
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_entrypoint(self, **overrides):
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_file = Path(temp_dir) / "trace.log"
            self.make_command(temp_dir, "python")
            self.make_command(temp_dir, "gunicorn")
            env = os.environ.copy()
            env.update({"PATH": f"{temp_dir}:{env['PATH']}", "TRACE_FILE": str(trace_file)})
            env.update(overrides)
            result = subprocess.run(
                ["sh", str(ENTRYPOINT)],
                cwd=BACKEND_DIR,
                env=env,
                capture_output=True,
                text=True,
            )
            trace = trace_file.read_text(encoding="utf-8") if trace_file.exists() else ""
            return result, trace

    def test_default_start_migrates_without_seeding_then_runs_gunicorn(self):
        result, trace = self.run_entrypoint(PORT="8080")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("manage.py migrate --noinput", trace)
        self.assertNotIn("seed_demo_data", trace)
        self.assertIn("jiqing_backend.wsgi:application --bind 0.0.0.0:8080", trace)

    def test_seed_requires_explicit_demo_password(self):
        result, trace = self.run_entrypoint(
            JIQING_SEED_DEMO="true",
            JIQING_DEMO_PASSWORD="",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JIQING_DEMO_PASSWORD", result.stderr)
        self.assertNotIn("seed_demo_data", trace)

# Generic HTTPS Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a portable, secure Docker production runtime for the Django Agent API so it can be exposed through a platform-managed HTTPS endpoint.

**Architecture:** Django remains the business and identity service. A small environment parser in settings validates production secrets and chooses a persistent SQLite path; a POSIX entrypoint performs migrations and optional explicit demo seeding before Gunicorn starts. The container runs as a non-root user, while TLS termination remains the responsibility of the selected cloud platform or reverse proxy.

**Tech Stack:** Python 3.12, Django 4.2, Gunicorn, POSIX shell, Docker, Python `unittest`

---

## File map

- Modify `demo1/backend/jiqing_backend/settings.py`: production validation and configurable SQLite path.
- Create `demo1/backend/accounts/test_deployment_settings.py`: subprocess tests for production settings behavior.
- Create `demo1/backend/docker-entrypoint.sh`: migrations, optional demo seed, Gunicorn handoff.
- Create `demo1/backend/tests/__init__.py`: standalone deployment-test package.
- Create `demo1/backend/tests/test_entrypoint.py`: entrypoint behavior tests with fake commands.
- Create `demo1/backend/Dockerfile`: non-root production image and HTTP health check.
- Create `demo1/backend/.dockerignore`: exclude local state and sensitive artifacts.
- Modify `demo1/backend/requirements.txt`: add pinned Gunicorn runtime.
- Modify `demo1/backend/README.md`: exact local Docker and HTTPS platform deployment procedure.
- Modify `xiaoyi-agent/README.md`: connect a deployed URL to the Xiaoyi test Agent.

### Task 1: Production settings contract

**Files:**
- Create: `demo1/backend/accounts/test_deployment_settings.py`
- Modify: `demo1/backend/jiqing_backend/settings.py`

- [ ] **Step 1: Write failing subprocess tests**

Create tests that invoke `manage.py check` with controlled environments:

```python
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
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_deployment_settings -v 2`

Expected: the first two tests fail because settings currently accept insecure production defaults.

- [ ] **Step 3: Add minimal settings validation and database path support**

In `settings.py`, import `ImproperlyConfigured`, define the development default once, read `JIQING_SQLITE_PATH`, and reject insecure production values:

```python
from django.core.exceptions import ImproperlyConfigured

DEV_SECRET_KEY = "dev-only-change-before-deploy"
SECRET_KEY = os.environ.get("JIQING_SECRET_KEY", DEV_SECRET_KEY)
DEBUG = os.environ.get("JIQING_DEBUG", "true").lower() == "true"
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("JIQING_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]
AGENT_SERVICE_KEY = os.environ.get("JIQING_AGENT_SERVICE_KEY", "")

if not DEBUG and SECRET_KEY == DEV_SECRET_KEY:
    raise ImproperlyConfigured("生产环境必须设置独立的 JIQING_SECRET_KEY")
if not DEBUG and len(AGENT_SERVICE_KEY) < 32:
    raise ImproperlyConfigured("生产环境的 JIQING_AGENT_SERVICE_KEY 不少于32个字符")
if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured("生产环境必须设置 JIQING_ALLOWED_HOSTS")

SQLITE_PATH = os.environ.get("JIQING_SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": SQLITE_PATH,
    }
}
```

Place the validation after the existing `ALLOWED_HOSTS` parsing, remove the later duplicate
`AGENT_SERVICE_KEY` assignment, and keep `SECURE_PROXY_SSL_HEADER` plus secure cookies unchanged.

- [ ] **Step 4: Run focused and configuration tests and verify GREEN**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_deployment_settings -v 2 && .venv/bin/python manage.py check`

Expected: 5 tests pass and Django reports no issues.

- [ ] **Step 5: Commit settings contract**

```bash
git add demo1/backend/accounts/test_deployment_settings.py demo1/backend/jiqing_backend/settings.py
git commit -m "feat: validate production deployment settings"
```

### Task 2: Entrypoint behavior

**Files:**
- Create: `demo1/backend/docker-entrypoint.sh`
- Create: `demo1/backend/tests/__init__.py`
- Create: `demo1/backend/tests/test_entrypoint.py`

- [ ] **Step 1: Write failing entrypoint behavior tests**

Use temporary fake `python` and `gunicorn` commands that append their arguments to a trace file. Assert the default path migrates and starts Gunicorn without seeding, and that explicit seeding without a password fails:

```python
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
        path.write_text('#!/bin/sh\nprintf "%s %s\\n" "$0" "$*" >> "$TRACE_FILE"\n', encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def run_entrypoint(self, **overrides):
        with tempfile.TemporaryDirectory() as temp_dir:
            trace_file = Path(temp_dir) / "trace.log"
            self.make_command(temp_dir, "python")
            self.make_command(temp_dir, "gunicorn")
            env = os.environ.copy()
            env.update({"PATH": f"{temp_dir}:{env['PATH']}", "TRACE_FILE": str(trace_file)})
            env.update(overrides)
            result = subprocess.run(["sh", str(ENTRYPOINT)], cwd=BACKEND_DIR, env=env, capture_output=True, text=True)
            trace = trace_file.read_text(encoding="utf-8") if trace_file.exists() else ""
            return result, trace

    def test_default_start_migrates_without_seeding_then_runs_gunicorn(self):
        result, trace = self.run_entrypoint(PORT="8080")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("manage.py migrate --noinput", trace)
        self.assertNotIn("seed_demo_data", trace)
        self.assertIn("jiqing_backend.wsgi:application --bind 0.0.0.0:8080", trace)

    def test_seed_requires_explicit_demo_password(self):
        result, trace = self.run_entrypoint(JIQING_SEED_DEMO="true", JIQING_DEMO_PASSWORD="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JIQING_DEMO_PASSWORD", result.stderr)
        self.assertNotIn("seed_demo_data", trace)
```

- [ ] **Step 2: Run the standalone tests and verify RED**

Run: `cd demo1/backend && .venv/bin/python -m unittest tests.test_entrypoint -v`

Expected: ERROR because `docker-entrypoint.sh` does not exist.

- [ ] **Step 3: Implement the minimal POSIX entrypoint**

```sh
#!/bin/sh
set -eu

python manage.py migrate --noinput

if [ "${JIQING_SEED_DEMO:-false}" = "true" ]; then
  if [ -z "${JIQING_DEMO_PASSWORD:-}" ]; then
    echo "JIQING_SEED_DEMO=true 时必须设置 JIQING_DEMO_PASSWORD" >&2
    exit 1
  fi
  python manage.py seed_demo_data
fi

exec gunicorn jiqing_backend.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile - \
  --error-logfile -
```

- [ ] **Step 4: Run standalone tests and verify GREEN**

Run: `cd demo1/backend && chmod +x docker-entrypoint.sh && .venv/bin/python -m unittest tests.test_entrypoint -v`

Expected: 2 tests pass.

- [ ] **Step 5: Commit the entrypoint**

```bash
git add demo1/backend/docker-entrypoint.sh demo1/backend/tests
git commit -m "feat: add safe production entrypoint"
```

### Task 3: Container image and operator documentation

**Files:**
- Create: `demo1/backend/Dockerfile`
- Create: `demo1/backend/.dockerignore`
- Modify: `demo1/backend/requirements.txt`
- Modify: `demo1/backend/README.md`
- Modify: `xiaoyi-agent/README.md`

- [ ] **Step 1: Add a failing packaging contract test**

Extend `tests/test_entrypoint.py` with a test that reads the deployment artifacts and asserts non-root execution, health check, pinned Gunicorn, and local-state exclusions:

```python
    def test_container_contract_is_secure_and_reproducible(self):
        dockerfile = (BACKEND_DIR / "Dockerfile").read_text(encoding="utf-8")
        dockerignore = (BACKEND_DIR / ".dockerignore").read_text(encoding="utf-8")
        requirements = (BACKEND_DIR / "requirements.txt").read_text(encoding="utf-8")
        self.assertIn("USER app", dockerfile)
        self.assertIn("/api/health/", dockerfile)
        self.assertIn("gunicorn==23.0.0", requirements)
        self.assertIn("db.sqlite3", dockerignore)
        self.assertIn(".venv", dockerignore)
```

- [ ] **Step 2: Run the packaging test and verify RED**

Run: `cd demo1/backend && .venv/bin/python -m unittest tests.test_entrypoint.EntrypointTests.test_container_contract_is_secure_and_reproducible -v`

Expected: ERROR because `Dockerfile` and `.dockerignore` do not exist.

- [ ] **Step 3: Add the minimal production image**

Add `gunicorn==23.0.0` to `requirements.txt` and create this image definition:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JIQING_SQLITE_PATH=/data/db.sqlite3

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN useradd --create-home --uid 10001 app \
    && mkdir -p /data \
    && chown -R app:app /app /data \
    && chmod +x /app/docker-entrypoint.sh

USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl --fail --silent http://127.0.0.1:${PORT:-8000}/api/health/ || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
```

Create `.dockerignore` with these exact classes of exclusions:

```text
.venv
.idea
__pycache__
*.py[cod]
*.log
db.sqlite3
.env
.git
```

- [ ] **Step 4: Document exact build, run, HTTPS, persistence and Xiaoyi steps**

Append a `Docker 部署` section to the backend README with the following operator contract, adapting only surrounding headings to avoid duplication:

````markdown
## Docker 部署

```bash
cd demo1/backend
docker build -t jiqing-agent:latest .
docker volume create jiqing-agent-data
docker run --rm -p 8000:8000 \
  -v jiqing-agent-data:/data \
  -e JIQING_DEBUG=false \
  -e JIQING_SECRET_KEY='<至少50位随机值>' \
  -e JIQING_AGENT_SERVICE_KEY='<至少32位随机值>' \
  -e JIQING_ALLOWED_HOSTS='agent.example.com' \
  jiqing-agent:latest
curl --fail http://127.0.0.1:8000/api/health/
```

首次需要演示数据时，额外设置 `JIQING_SEED_DEMO=true` 与强随机
`JIQING_DEMO_PASSWORD`；后续启动应移除 `JIQING_SEED_DEMO`。云平台必须挂载
持久磁盘到 `/data`，通过 Secret 管理功能注入密钥，并在容器前提供 HTTPS。
````

Append to `xiaoyi-agent/README.md`:

```markdown
## 公网联调

部署完成后先访问 `https://<实际域名>/api/health/`。确认返回 200，再把
`openapi.yaml` 中唯一的 `servers[0].url` 改为
`https://<实际域名>/api`。服务密钥只配置在平台私密参数中。测试态联调通过后
仍需团队成员在小艺开放平台手动确认发布，不由部署脚本自动提交。
```

- [ ] **Step 5: Run packaging tests and optional image verification**

Run: `cd demo1/backend && .venv/bin/python -m unittest tests.test_entrypoint -v`

Expected: 3 tests pass.

If `docker version` succeeds, additionally run:

```bash
docker build -t jiqing-agent:test .
docker run --rm -d --name jiqing-agent-test -p 18000:8000 \
  -e JIQING_DEBUG=false \
  -e JIQING_SECRET_KEY=ssssssssssssssssssssssssssssssssssssssssssssssssss \
  -e JIQING_AGENT_SERVICE_KEY=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  -e JIQING_ALLOWED_HOSTS=127.0.0.1,localhost \
  jiqing-agent:test
curl --fail http://127.0.0.1:18000/api/health/
docker stop jiqing-agent-test
```

Expected: image builds, health endpoint returns `{"status":"ok","service":"jiqing-backend"}`, and container stops cleanly. If Docker is unavailable, record that image runtime verification is pending rather than claiming it passed.

- [ ] **Step 6: Commit the container package**

```bash
git add demo1/backend/Dockerfile demo1/backend/.dockerignore demo1/backend/requirements.txt demo1/backend/README.md xiaoyi-agent/README.md demo1/backend/tests/test_entrypoint.py
git commit -m "feat: package agent backend for https deployment"
```

### Task 4: Regression verification and PR update

**Files:**
- Modify: `docs/superpowers/plans/2026-07-22-generic-https-deployment.md` (check completed boxes only)

- [ ] **Step 1: Run all backend checks**

Run: `cd demo1/backend && .venv/bin/python manage.py makemigrations --check && .venv/bin/python manage.py check && .venv/bin/python manage.py test -v 2`

Expected: no model changes, no Django issues, and all backend tests pass.

- [ ] **Step 2: Run deployment and mini-program tests**

Run: `cd demo1/backend && .venv/bin/python -m unittest tests.test_entrypoint -v && cd .. && node --test tests/*.test.js`

Expected: all deployment tests and all mini-program tests pass.

- [ ] **Step 3: Inspect the final diff and worktree**

Run: `git diff --check && git status --short && git log --oneline -6`

Expected: no whitespace errors; only the pre-existing untracked `.superpowers/` directory may remain.

- [ ] **Step 4: Push the existing PR branch**

Run: `git push origin feat/xiaoyi-agent-mvp`

Expected: GitHub PR #2 updates with the deployment commits. Do not merge or publish the Xiaoyi Agent without separate user authorization.

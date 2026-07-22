# 冀青智引小艺 Agent MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在小艺开放平台与现有 Django 数据服务之间建立可验证的 Agent 闭环，实现账号绑定、青年画像、三阶段职业规划、政策解释、资源匹配、确认后行动和今日建议。

**Architecture:** 小艺 Agent 负责自然语言理解、追问和 Skills 编排；Django 新增独立的 Agent API 层，负责服务鉴权、用户绑定、结构化检索、业务写入和审计。小程序新增“连接小艺”页，用一次性绑定码连接已有青年档案，并展示今日建议和成长计划。MVP 不调用第三方付费模型，规划和推荐由可测试的确定性规则生成，小艺负责把结构化结果转成自然表达。

**Tech Stack:** Python 3、Django 4.2、SQLite（开发/演示）、微信小程序原生 JavaScript/WXML/WXSS、小艺开放平台 Skills、OpenAPI 3.0、Django signing、Node.js 内置测试运行器。

---

## 执行前准备

- 本计划依赖第一阶段分支 `feat/growth-data-closure` 和 PR #1。
- 执行时使用 `using-git-worktrees`，从包含本设计与计划的提交创建分支 `feat/xiaoyi-agent-mvp`，工作树目录为 `.worktrees/xiaoyi-agent-mvp`。
- 每个任务严格遵循 `test-driven-development`：先添加单个失败测试，确认失败原因正确，再写最小实现并运行相关测试。
- 不提交仓库根目录下的 `.superpowers/` 运行时目录。

## Task 1: Agent 数据模型与后台管理

**Files:**
- Create: `demo1/backend/accounts/test_agent_models.py`
- Modify: `demo1/backend/accounts/models.py`
- Create: `demo1/backend/accounts/migrations/0003_agent_mvp.py`
- Modify: `demo1/backend/accounts/admin.py`

**Step 1: 写失败的模型测试**

在 `test_agent_models.py` 创建用户后验证：绑定码摘要唯一、外部用户标识唯一、成长计划可包含三个阶段任务、工具日志与建议可关联用户。核心断言如下：

```python
class AgentModelTests(TestCase):
    def test_external_identity_is_unique_per_platform(self):
        user = User.objects.create_user(username="agent-user")
        AgentUserBinding.objects.create(
            platform="xiaoyi", external_user_id="xy-001", user=user
        )
        with self.assertRaises(IntegrityError):
            AgentUserBinding.objects.create(
                platform="xiaoyi", external_user_id="xy-001", user=user
            )

    def test_growth_plan_has_three_stage_tasks(self):
        user = User.objects.create_user(username="planner")
        plan = GrowthPlan.objects.create(user=user, goal="县域数字运营就业")
        for stage in ("seven_days", "one_month", "three_months"):
            GrowthTask.objects.create(plan=plan, stage=stage, title=stage)
        self.assertEqual(set(plan.tasks.values_list("stage", flat=True)), {
            "seven_days", "one_month", "three_months"
        })
```

**Step 2: 运行测试并确认因模型不存在而失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_models -v 2`

Expected: `ImportError`，指出 Agent 模型尚未定义。

**Step 3: 添加模型**

在 `models.py` 添加设计中八个模型：

- `AgentBindingCode(user, code_digest, expires_at, used_at, created_at)`；`code_digest` 唯一且建立索引。
- `AgentUserBinding(platform, external_user_id, user, is_active, bound_at)`；平台与外部 ID 联合唯一，同一平台下一名用户只保留一个有效绑定。
- `AgentConversation(user, platform, external_conversation_id, summary, last_interacted_at)`。
- `AgentMessage(conversation, role, content_summary, created_at)`。
- `GrowthPlan(user, goal, starts_on, ends_on, status, rationale, created_at, updated_at)`。
- `GrowthTask(plan, stage, title, action_type, resource_type, resource_id, due_at, completed_at, status, sequence)`。
- `AgentToolLog(user, skill_name, request_summary, result_status, duration_ms, created_at)`。
- `ProactiveSuggestion(user, suggestion_type, content, trigger_reason, scheduled_for, viewed_at, completed_at, created_at)`。

为阶段、状态和角色字段定义显式 choices；为绑定查询、用户计划和待办建议增加复合索引。

**Step 4: 生成并检查迁移**

Run: `cd demo1/backend && .venv/bin/python manage.py makemigrations accounts --name agent_mvp`

Expected: 生成 `0003_agent_mvp.py`，只包含上述模型、约束和索引。

Run: `cd demo1/backend && .venv/bin/python manage.py migrate --plan`

Expected: `accounts.0003_agent_mvp` 可执行，无依赖冲突。

**Step 5: 注册后台并运行测试**

在 `admin.py` 注册八个模型，为绑定、计划、任务、日志和建议配置 `list_display`、`list_filter`、`search_fields`，不在列表中显示绑定码摘要全文。

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_models -v 2`

Expected: PASS。

**Step 6: 提交**

```bash
git add demo1/backend/accounts/models.py demo1/backend/accounts/admin.py demo1/backend/accounts/migrations/0003_agent_mvp.py demo1/backend/accounts/test_agent_models.py
git commit -m "feat: add agent growth data models"
```

## Task 2: 统一协议、服务鉴权与调用审计

**Files:**
- Create: `demo1/backend/accounts/test_agent_security.py`
- Create: `demo1/backend/accounts/agent_protocol.py`
- Create: `demo1/backend/accounts/agent_auth.py`
- Modify: `demo1/backend/jiqing_backend/settings.py`
- Modify: `demo1/backend/README.md`

**Step 1: 写鉴权失败测试**

测试无 `X-Agent-Service-Key`、错误密钥和未绑定外部用户均被拒绝，且响应始终符合统一协议：

```python
@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentSecurityTests(TestCase):
    def test_skill_rejects_missing_service_key(self):
        response = self.client.post(
            "/api/agent/skills/profile-context/",
            data=json.dumps({"externalUserId": "xy-001"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["errorCode"], "INVALID_SERVICE_CREDENTIAL")
        self.assertFalse(response.json()["ok"])
```

**Step 2: 运行测试并确认 404/协议缺失**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_security -v 2`

Expected: FAIL，接口不存在或返回结构不匹配。

**Step 3: 实现统一响应与装饰器**

`agent_protocol.py` 暴露：

```python
def agent_response(*, ok, message, data=None, sources=None,
                   requires_confirmation=False, error_code=None, status=200):
    return JsonResponse({
        "ok": ok,
        "message": message,
        "data": data or {},
        "sources": sources or [],
        "requiresConfirmation": requires_confirmation,
        "errorCode": error_code,
    }, status=status)
```

`agent_auth.py` 使用 `secrets.compare_digest` 校验 `settings.AGENT_SERVICE_KEY`；Skill 装饰器从请求体读取 `externalUserId`，只解析启用的 `AgentUserBinding`，把用户设为 `request.agent_user`。每次调用在 `finally` 中写入 `AgentToolLog`，请求摘要只保留字段名和资源 ID，不记录绑定码、密钥或完整对话。

**Step 4: 配置环境变量并记录部署说明**

在 `settings.py` 添加：

```python
AGENT_SERVICE_KEY = os.environ.get("JIQING_AGENT_SERVICE_KEY", "")
AGENT_CONFIRMATION_MAX_AGE_SECONDS = int(
    os.environ.get("JIQING_AGENT_CONFIRMATION_MAX_AGE_SECONDS", "300")
)
```

在后端 README 说明生产环境必须设置不少于 32 个随机字符的 `JIQING_AGENT_SERVICE_KEY`，只能由小艺 Skill 服务端携带，不得写入小程序。

**Step 5: 运行测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_security -v 2`

Expected: PASS。

**Step 6: 提交**

```bash
git add demo1/backend/accounts/agent_protocol.py demo1/backend/accounts/agent_auth.py demo1/backend/accounts/test_agent_security.py demo1/backend/jiqing_backend/settings.py demo1/backend/README.md
git commit -m "feat: secure agent skill requests"
```

## Task 3: 一次性绑定码和小艺身份绑定

**Files:**
- Create: `demo1/backend/accounts/test_agent_binding.py`
- Create: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写绑定闭环测试**

覆盖：登录用户生成六位绑定码；十分钟内可使用；只保存 SHA-256 摘要；一次使用后失效；过期码拒绝；同一小艺账号重新绑定时安全更新关系。

```python
@override_settings(AGENT_SERVICE_KEY="test-agent-key")
class AgentBindingTests(TestCase):
    def test_code_binds_xiaoyi_identity_once(self):
        user = User.objects.create_user(username="bind-user")
        token = AuthToken.create_for_user(user)
        generated = self.client.post(
            "/api/agent/binding-code/",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )
        code = generated.json()["code"]
        bound = self.client.post(
            "/api/agent/bind/",
            data=json.dumps({"externalUserId": "xy-001", "code": code}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )
        repeated = self.client.post(
            "/api/agent/bind/",
            data=json.dumps({"externalUserId": "xy-002", "code": code}),
            content_type="application/json",
            HTTP_X_AGENT_SERVICE_KEY="test-agent-key",
        )
        self.assertEqual(bound.status_code, 200)
        self.assertEqual(repeated.json()["errorCode"], "BINDING_CODE_INVALID")
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_binding -v 2`

Expected: FAIL，绑定接口尚未注册。

**Step 3: 实现生成和绑定接口**

- `POST /api/agent/binding-code/` 使用现有 `auth_required`；先使该用户未使用的旧码过期，再以 `secrets.randbelow(900000) + 100000` 生成六位码，保存 `sha256(code.encode()).hexdigest()`，返回明文码和 `expiresAt`。
- `POST /api/agent/bind/` 只使用服务密钥鉴权；在 `transaction.atomic()` 和 `select_for_update()` 中校验摘要、到期时间与 `used_at`，成功后设置 `used_at` 并 `update_or_create` 外部身份绑定。
- 所有失败使用稳定错误码：`BINDING_CODE_INVALID`、`BINDING_CODE_EXPIRED`、`EXTERNAL_ID_REQUIRED`。

**Step 4: 运行绑定和安全测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_binding accounts.test_agent_security -v 2`

Expected: PASS。

**Step 5: 提交**

```bash
git add demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_binding.py
git commit -m "feat: bind xiaoyi identities with one-time codes"
```

## Task 4: 青年画像 Skill

**Files:**
- Create: `demo1/backend/accounts/test_agent_profile.py`
- Create: `demo1/backend/accounts/agent_services.py`
- Modify: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写画像读取、缺失字段和确认更新测试**

测试读取只能返回绑定用户；缺失字段固定为 `region`、`education`、`major`、`intents`、`abilities`；更新未携带 `confirmed: true` 时只返回确认请求，不写数据库。

```python
def test_profile_update_requires_explicit_confirmation(self):
    response = self.skill_post("/api/agent/skills/profile-context/", {
        "externalUserId": "xy-profile",
        "operation": "update",
        "changes": {"region": "河北省沧州市"},
        "confirmed": False,
    })
    self.assertTrue(response.json()["requiresConfirmation"])
    self.profile.refresh_from_db()
    self.assertEqual(self.profile.region, "")
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_profile -v 2`

Expected: FAIL，Skill 接口不存在。

**Step 3: 实现画像服务与接口**

`agent_services.py` 添加 `profile_context(user)`，返回：

```json
{
  "profile": {"region": "", "education": "", "major": "", "intents": [], "abilities": []},
  "missingFields": ["region", "education", "major", "intents", "abilities"],
  "recentGrowth": []
}
```

最近成长行为最多 10 条，按时间倒序；画像更新仅允许白名单字段，显式 `confirmed: true` 后保存，并写 `GrowthEvent(event_type="profile_updated_by_agent")`。

注册 `POST /api/agent/skills/profile-context/` 并套用服务鉴权、外部身份解析和审计装饰器。

**Step 4: 运行测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_profile -v 2`

Expected: PASS。

**Step 5: 提交**

```bash
git add demo1/backend/accounts/agent_services.py demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_profile.py
git commit -m "feat: expose youth profile agent skill"
```

## Task 5: 政策可信检索和资源匹配 Skills

**Files:**
- Create: `demo1/backend/accounts/test_agent_matching.py`
- Modify: `demo1/backend/accounts/agent_services.py`
- Modify: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写政策时效、来源和用户画像匹配测试**

覆盖草稿和过期政策不可见、地区与关键词过滤、每条政策必须返回来源；资源结果覆盖岗位、课程、活动、导师，包含 0–100 分和可读的匹配原因。

```python
def test_policy_search_only_returns_current_sourced_results(self):
    current = Policy.objects.create(
        title="沧州青年就业补贴", status="published", region="沧州",
        source="沧州市人社局", effective_until=date.today() + timedelta(days=30),
    )
    Policy.objects.create(
        title="过期补贴", status="published", region="沧州",
        source="旧文件", effective_until=date.today() - timedelta(days=1),
    )
    response = self.skill_post("/api/agent/skills/policy-search/", {
        "externalUserId": "xy-match", "keyword": "就业", "region": "沧州"
    })
    self.assertEqual([item["id"] for item in response.json()["data"]["items"]], [current.id])
    self.assertEqual(response.json()["sources"][0]["publisher"], "沧州市人社局")
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_matching -v 2`

Expected: FAIL，两个 Skill 尚不存在。

**Step 3: 实现结构化政策检索**

实现 `search_policies(user, keyword, region, category, limit=5)`：

- 只查询 `status="published"` 且未过期政策。
- 地区参数为空时使用用户画像地区；允许“河北省”和画像所在县域的宽松包含匹配。
- 关键词仅检索 `title/target/support/conditions/materials`，限制长度 50，结果上限 5。
- `data.items` 返回适用理由、条件、材料、流程、办理地点、电话和不确定条件。
- `sources` 返回 `title`、`publisher`（现有 `source` 字段）、`publishedAt`、`effectiveUntil`，无结果时返回空数组并明确“暂未找到”。

**Step 4: 实现资源匹配**

实现 `match_resources(user, resource_types, goal, limit=3)`，复用现有画像字段并使用固定可解释评分：地区 +30、意图 +25、标签交集每项 +10、专业/学历文本匹配 +15、有效期 +10；总分封顶 100。每项返回 `resourceType`、`resourceId`、`title`、`score`、`reasons` 和关键字段。只返回已发布且未截止资源。

注册：

- `POST /api/agent/skills/policy-search/`
- `POST /api/agent/skills/resource-match/`

**Step 5: 运行相关和回归测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_matching accounts.tests.PolicyApiTests accounts.tests.RecommendationApiTests -v 2`

Expected: PASS。

**Step 6: 提交**

```bash
git add demo1/backend/accounts/agent_services.py demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_matching.py
git commit -m "feat: add trusted policy and resource skills"
```

## Task 6: 三阶段职业规划 Skill

**Files:**
- Create: `demo1/backend/accounts/test_agent_planning.py`
- Modify: `demo1/backend/accounts/agent_services.py`
- Modify: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写确定性规划测试**

测试画像完整时生成一个有效计划及至少六个任务，三个阶段均存在；画像缺失发展目标时返回 `PROFILE_INCOMPLETE` 和待补字段；重复生成会将旧计划设为 `replaced`。

```python
def test_career_plan_creates_three_stages(self):
    response = self.skill_post("/api/agent/skills/career-plan/", {
        "externalUserId": "xy-plan", "goal": "在县域从事数字运营"
    })
    self.assertTrue(response.json()["ok"])
    plan = GrowthPlan.objects.get(user=self.user, status="active")
    self.assertEqual(set(plan.tasks.values_list("stage", flat=True)), {
        "seven_days", "one_month", "three_months"
    })
    self.assertGreaterEqual(plan.tasks.count(), 6)
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_planning -v 2`

Expected: FAIL，规划 Skill 尚不存在。

**Step 3: 实现规则规划器**

实现 `create_career_plan(user, goal)`：

- 7 天：补全画像、查看一项匹配政策、收藏一项目标资源。
- 1 个月：完成一门匹配课程、报名一次活动或投递一个岗位。
- 3 个月：完成阶段复盘、更新画像、执行下一轮资源匹配。
- 根据 `intents` 将“就业/创业/学习/社会实践”模板中的标题与关联资源替换为画像最相关的内容。
- 使用数据库事务将旧 active 计划改为 replaced，创建新计划、任务和 `GrowthEvent(event_type="growth_plan_created")`。
- 返回阶段、任务 ID、标题、截止时间、匹配依据，不宣称任务已经完成。

注册 `POST /api/agent/skills/career-plan/`。

**Step 4: 运行测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_planning -v 2`

Expected: PASS。

**Step 5: 提交**

```bash
git add demo1/backend/accounts/agent_services.py demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_planning.py
git commit -m "feat: generate staged youth growth plans"
```

## Task 7: 显式确认后的成长行动 Skill

**Files:**
- Create: `demo1/backend/accounts/test_agent_actions.py`
- Create: `demo1/backend/accounts/agent_actions.py`
- Modify: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写预览、篡改、过期和执行测试**

首次调用报名、申请、收藏或完成任务必须返回 `requiresConfirmation: true` 和 `confirmationToken`，且数据库不变；第二次携带有效 token 才写入；token 绑定用户、动作和资源，修改参数或超时均拒绝；重复执行返回幂等结果。

```python
def test_activity_enrollment_only_executes_after_confirmation(self):
    preview = self.skill_post("/api/agent/skills/growth-action/", {
        "externalUserId": "xy-action", "action": "enroll_activity",
        "resourceId": self.activity.id
    }).json()
    self.assertTrue(preview["requiresConfirmation"])
    self.assertFalse(Enrollment.objects.filter(user=self.user).exists())

    executed = self.skill_post("/api/agent/skills/growth-action/", {
        "externalUserId": "xy-action", "action": "enroll_activity",
        "resourceId": self.activity.id, "confirmed": True,
        "confirmationToken": preview["data"]["confirmationToken"]
    })
    self.assertEqual(executed.status_code, 201)
    self.assertTrue(Enrollment.objects.filter(user=self.user).exists())
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_actions -v 2`

Expected: FAIL，行动 Skill 尚不存在。

**Step 3: 实现签名确认令牌和动作分发**

`agent_actions.py` 使用 `django.core.signing.dumps/loads`，salt 固定为 `jiqing-agent-action`，payload 只含绑定用户 ID、动作、资源类型和资源 ID；`loads` 使用 `AGENT_CONFIRMATION_MAX_AGE_SECONDS`。

允许动作白名单：

- `enroll_activity` → `Enrollment(activity=...)`
- `apply_opportunity` → `Enrollment(opportunity=...)`
- `favorite_resource` → `Favorite(...)`，仅添加不做 toggle
- `complete_course` → `CourseProgress(completed=True)`
- `complete_task` → `GrowthTask(status="completed", completed_at=now())`

执行前重新校验资源仍已发布且未截止；使用 `get_or_create/update_or_create` 保证幂等；成功写入对应 `GrowthEvent`。签名错误返回 `CONFIRMATION_INVALID`，过期返回 `CONFIRMATION_EXPIRED`，参数变化返回 `CONFIRMATION_MISMATCH`。

注册 `POST /api/agent/skills/growth-action/`。

**Step 4: 运行行动测试与原有写接口回归**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_actions accounts.tests.EnrollmentApiTests accounts.tests.FavoriteApiTests -v 2`

Expected: PASS。

**Step 5: 提交**

```bash
git add demo1/backend/accounts/agent_actions.py demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_actions.py
git commit -m "feat: require confirmation for agent actions"
```

## Task 8: 今日建议与计划查询

**Files:**
- Create: `demo1/backend/accounts/test_agent_suggestions.py`
- Modify: `demo1/backend/accounts/agent_services.py`
- Modify: `demo1/backend/accounts/agent_views.py`
- Modify: `demo1/backend/accounts/urls.py`

**Step 1: 写主动建议优先级测试**

测试优先级为：逾期任务、24 小时内到期任务、画像缺失、新发布匹配资源；每日同一触发依据不重复创建；返回当前有效计划摘要。

```python
def test_overdue_task_is_first_daily_suggestion(self):
    task = GrowthTask.objects.create(
        plan=self.plan, stage="seven_days", title="完善简历",
        due_at=timezone.now() - timedelta(hours=1), status="pending"
    )
    response = self.skill_post("/api/agent/skills/daily-suggestion/", {
        "externalUserId": "xy-daily"
    })
    first = response.json()["data"]["suggestions"][0]
    self.assertEqual(first["taskId"], task.id)
    self.assertEqual(first["priority"], "urgent")
```

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_suggestions -v 2`

Expected: FAIL，今日建议 Skill 尚不存在。

**Step 3: 实现建议服务**

实现 `build_daily_suggestions(user, now)`，最多返回三条，并用 `suggestion_type + trigger_reason + scheduled_for日期` 去重保存。建议包含 `priority`、`title`、`content`、`reason`、可选 `taskId/resourceType/resourceId`。接口同时返回 active 计划和三阶段完成数。

注册两个复用同一服务的入口：

- `POST /api/agent/skills/daily-suggestion/`：供小艺以服务密钥和外部用户 ID 调用。
- `GET /api/agent/me/dashboard/`：供已登录小程序以现有 Token 调用，返回相同建议和 active 计划摘要。

不在本任务实现未经确认的小艺系统推送。

**Step 4: 运行测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_suggestions -v 2`

Expected: PASS。

**Step 5: 提交**

```bash
git add demo1/backend/accounts/agent_services.py demo1/backend/accounts/agent_views.py demo1/backend/accounts/urls.py demo1/backend/accounts/test_agent_suggestions.py
git commit -m "feat: generate proactive daily suggestions"
```

## Task 9: 小程序“连接小艺”页面

**Files:**
- Modify: `demo1/app.json`
- Modify: `demo1/utils/api.js`
- Modify: `demo1/pages/mine/mine.js`
- Create: `demo1/pages/agent/agent.js`
- Create: `demo1/pages/agent/agent.json`
- Create: `demo1/pages/agent/agent.wxml`
- Create: `demo1/pages/agent/agent.wxss`
- Create: `demo1/tests/agent-page.test.js`

**Step 1: 写前端失败测试**

使用现有 Node 测试方式验证 API 封装、页面注册、登录拦截、绑定码倒计时和今日建议渲染：

```javascript
test("agent page requests a one-time binding code", async () => {
  global.wx = createWxMock({ code: "482731", expiresIn: 600 });
  const page = loadPage("pages/agent/agent.js");
  await page.generateBindingCode();
  assert.equal(page.data.bindingCode, "482731");
  assert.equal(global.wx.lastRequest.url.endsWith("/agent/binding-code/"), true);
});
```

**Step 2: 运行并确认失败**

Run: `cd demo1 && node --test tests/agent-page.test.js`

Expected: FAIL，页面和 API 方法不存在。

**Step 3: 添加 API 与页面**

- `utils/api.js` 添加 `generateAgentBindingCode()` 和 `getAgentDashboard()`；后者使用现有用户 Token 调用 `/agent/me/dashboard/`，小程序永远不持有 Agent 服务密钥。
- `app.json` 注册 `pages/agent/agent`。
- “我的”菜单首项新增“连接小艺 Agent”。
- 页面未登录时提供登录按钮；已登录时加载今日建议和三阶段计划摘要，并可生成绑定码、显示十分钟倒计时、复制绑定码和三步使用说明。
- 页面不得打印 Token、服务密钥或绑定码摘要；倒计时结束后清空明文码。

**Step 4: 运行前端测试**

Run: `cd demo1 && node --test tests/*.test.js`

Expected: 全部 PASS。

**Step 5: 提交**

```bash
git add demo1/app.json demo1/utils/api.js demo1/pages/mine/mine.js demo1/pages/agent demo1/tests/agent-page.test.js
git commit -m "feat: add xiaoyi connection page"
```

## Task 10: 小艺 Agent 配置包与双语体验

**Files:**
- Create: `xiaoyi-agent/README.md`
- Create: `xiaoyi-agent/openapi.yaml`
- Create: `xiaoyi-agent/system-prompt.md`
- Create: `xiaoyi-agent/conversation-examples.md`
- Create: `xiaoyi-agent/test-cases.md`
- Create: `demo1/backend/accounts/test_xiaoyi_contract.py`
- Modify: `demo1/backend/requirements.txt`

**Step 1: 写 OpenAPI 合约失败测试**

测试配置文件包含绑定接口和六个 Skills 共七个唯一 `operationId`、统一服务密钥头、外部用户 ID、统一响应字段，并保证写操作文档要求确认：

```python
class XiaoyiContractTests(SimpleTestCase):
    def test_openapi_declares_all_agent_skills(self):
        document = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
        operation_ids = {
            operation["operationId"]
            for path in document["paths"].values()
            for operation in path.values()
        }
        self.assertEqual(operation_ids, {
            "bindAccount", "profileContext", "careerPlan", "policySearch",
            "resourceMatch", "growthAction", "dailySuggestion"
        })
```

在 `requirements.txt` 加入受 Django 4.2 支持的 `PyYAML` 固定版本，供合约测试解析 YAML。

**Step 2: 运行并确认失败**

Run: `cd demo1/backend && .venv/bin/pip install -r requirements.txt && .venv/bin/python manage.py test accounts.test_xiaoyi_contract -v 2`

Expected: FAIL，`xiaoyi-agent/openapi.yaml` 尚不存在。

**Step 3: 编写平台配置包**

- `openapi.yaml` 以 OpenAPI 3.0.3 完整描述绑定和六个 Skills，服务 URL 通过平台环境替换为实际 HTTPS 地址；定义 `X-Agent-Service-Key` security scheme 和统一 `AgentResponse` schema。
- `system-prompt.md` 明确角色、能力边界、隐私规则、政策来源要求、确认规则和错误话术；默认中文，检测到英文提问时提供简洁中英双语关键步骤。
- `conversation-examples.md` 提供首次绑定、画像补全、就业规划、政策咨询、资源推荐、报名确认、今日建议七组可直接配置/测试的对话。
- `test-cases.md` 记录正常、未绑定、政策无结果、服务异常、取消操作和 token 过期等验收用例。
- `README.md` 记录在小艺开放平台创建 Agent、粘贴提示词、导入接口、配置服务地址/密钥、逐项联调和发布测试态的顺序；对平台尚未验证的入口名称明确标注“以当前控制台显示为准”，不虚构已发布状态。

**Step 4: 运行合约和全量后端测试**

Run: `cd demo1/backend && .venv/bin/python manage.py test -v 2`

Expected: 全部 PASS。

**Step 5: 提交**

```bash
git add xiaoyi-agent demo1/backend/requirements.txt demo1/backend/accounts/test_xiaoyi_contract.py
git commit -m "docs: add deployable xiaoyi agent package"
```

## Task 11: 演示数据、端到端验收和交付文档

**Files:**
- Modify: `demo1/backend/accounts/management/commands/seed_demo_data.py`
- Create: `demo1/backend/accounts/test_agent_demo.py`
- Create: `docs/agent-api.md`
- Create: `docs/demo-script-5min.md`
- Modify: `README.md`

**Step 1: 写完整主链路测试**

单个测试按真实顺序执行：登录用户生成绑定码 → 小艺绑定 → 读取画像 → 创建计划 → 查询带来源政策 → 匹配资源 → 获取行动确认 → 确认报名 → 查询今日建议；验证 `AgentToolLog`、`GrowthEvent`、`Enrollment` 和计划数据均已落库。

**Step 2: 运行并确认演示数据不足或链路失败**

Run: `cd demo1/backend && .venv/bin/python manage.py test accounts.test_agent_demo -v 2`

Expected: 首次运行因 Agent 演示用户或匹配数据缺失而 FAIL。

**Step 3: 扩充幂等演示种子**

更新 `seed_demo_data`，增加固定账号 `demo_youth` 的完整画像，以及可命中的河北县域就业政策、数字运营岗位、技能课程、实践活动和导师。命令可重复执行，不产生重复资源，不在仓库中保存生产密码；演示密码通过 `JIQING_DEMO_PASSWORD` 获取，开发默认值仅在 README 标明不可用于生产。

**Step 4: 编写交付说明**

- `docs/agent-api.md`：逐个接口列出认证、请求、成功响应、错误码和 curl 示例；示例使用虚构密钥。
- `docs/demo-script-5min.md`：按分钟写出演示台词与屏幕动作，覆盖“绑定—画像—规划—政策—资源—确认报名—今日建议”，并准备网络异常时的本地录屏兜底说明。
- 根 README 增加项目升级后的架构、快速启动、Agent 配置包入口和测试命令。

**Step 5: 执行全量验证**

Run: `cd demo1/backend && .venv/bin/python manage.py makemigrations --check`

Expected: `No changes detected`。

Run: `cd demo1/backend && .venv/bin/python manage.py check --deploy`

Expected: 仅出现已在部署说明中解释的本地 DEBUG/HTTPS 警告，不能有模型、URL 或安全配置错误。

Run: `cd demo1/backend && .venv/bin/python manage.py test -v 2`

Expected: 全部 PASS。

Run: `cd demo1 && node --test tests/*.test.js`

Expected: 全部 PASS。

Run: `git status --short`

Expected: 仅允许根目录 `.superpowers/` 为未跟踪运行时目录；实现文件均已提交。

**Step 6: 人工验收**

- 启动 Django：`cd demo1/backend && JIQING_AGENT_SERVICE_KEY=local-demo-agent-key .venv/bin/python manage.py runserver`。
- 执行 `docs/agent-api.md` 的绑定与六个 Skill 请求。
- 用微信开发者工具验证绑定码页面；用小艺开放平台测试态验证七段对话。
- 截图保存绑定成功、政策来源、行动确认和成长记录四个关键证据，加入比赛材料目录但不提交含用户敏感信息的图片。

**Step 7: 提交**

```bash
git add demo1/backend/accounts/management/commands/seed_demo_data.py demo1/backend/accounts/test_agent_demo.py docs/agent-api.md docs/demo-script-5min.md README.md
git commit -m "test: verify complete agent growth loop"
```

## 最终完成标准

- 七个小艺操作（绑定加六项 Skills）均由 OpenAPI 描述并通过合约测试。
- 未绑定、越权、过期资源和错误服务密钥均不能读取或写入个人数据。
- 画像更新和所有业务写操作均要求用户显式确认。
- 政策结果仅来自已发布、未过期数据，且每条都带来源。
- 三阶段计划、行动结果、成长记录和今日建议形成可重复演示的数据闭环。
- 后端全量测试、前端全量测试、迁移检查通过。
- 小艺平台测试态配置完成后，可在五分钟内演示完整主链路。

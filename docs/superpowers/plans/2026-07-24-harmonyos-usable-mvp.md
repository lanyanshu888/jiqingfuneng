# 冀青智引鸿蒙应用可真实使用精简版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `harmony-app/` 中开发可真实注册、建立画像、执行成长计划、查看与使用资源、离线只读、发送本地提醒并提供桌面成长卡片的鸿蒙手机应用。

**Architecture:** 鸿蒙应用使用 ArkTS/ArkUI Stage 模型，通过单一 API 适配层访问现有 Django 用户接口；登录令牌保存在 Asset Store Kit，本地非敏感缓存由 ArkData 管理。小艺服务密钥永不进入客户端，智能助手通过新增的登录用户接口或同结构开发样例运行。

**Tech Stack:** HarmonyOS 7 / API 26、ArkTS、ArkUI、Ability Kit、Network Kit、ArkData、Asset Store Kit、Notification Kit、Form Kit、Django REST-style JSON API、Hvigor、DevEco Testing。

---

## 0. 执行边界

本计划分为9个可独立验收的阶段：

1. 工程与接口基线；
2. 主题、导航和通用组件；
3. 网络、认证和安全存储；
4. 首次画像；
5. 首页与成长规划；
6. 资源与成长行动；
7. 智能助手与个人中心；
8. 离线缓存、通知和桌面卡片；
9. 真机联调、验收和交付。

### 当前代码状态警告

正确仓库工作目录：

```text
/Users/shuaishuai/Documents/Codex/2026-07-22/ai-agent-agent-3-1-2/work/jiqingfuneng/.worktrees/growth-data-closure
```

当前分支：

```text
feat/xiaoyi-agent-mvp
```

计划编写时，后台认证与小艺相关文件存在其他开发者的未提交修改。执行者不得删除、覆盖或顺手提交这些修改。鸿蒙开发建议从当前功能分支新建独立分支：

```bash
git switch -c feat/harmonyos-usable-mvp
```

如果 Git 因未提交修改阻止切换，停止操作并由原修改者先提交或另建 worktree。禁止使用 `git reset --hard`、`git checkout -- .` 或删除 worktree。

## 1. 文件结构

创建以下结构：

```text
harmony-app/
├── AppScope/
│   ├── app.json5
│   └── resources/base/element/string.json
├── build-profile.json5
├── hvigorfile.ts
├── oh-package.json5
├── README.md
├── docs/
│   ├── api-contract.md
│   ├── test-record.md
│   └── known-issues.md
├── entry/
│   ├── build-profile.json5
│   ├── hvigorfile.ts
│   ├── oh-package.json5
│   └── src/
│       ├── main/
│       │   ├── module.json5
│       │   ├── ets/
│       │   │   ├── entryability/EntryAbility.ets
│       │   │   ├── pages/Index.ets
│       │   │   ├── pages/auth/LoginPage.ets
│       │   │   ├── pages/auth/RegisterPage.ets
│       │   │   ├── pages/onboarding/ProfileWizardPage.ets
│       │   │   ├── pages/onboarding/ProfileResultPage.ets
│       │   │   ├── pages/home/HomePage.ets
│       │   │   ├── pages/plan/PlanPage.ets
│       │   │   ├── pages/plan/TaskDetailPage.ets
│       │   │   ├── pages/resource/ResourceCenterPage.ets
│       │   │   ├── pages/resource/ResourceDetailPage.ets
│       │   │   ├── pages/assistant/AssistantPage.ets
│       │   │   ├── pages/assistant/AssistantResultPage.ets
│       │   │   ├── pages/mine/MinePage.ets
│       │   │   ├── pages/mine/ProfilePage.ets
│       │   │   ├── pages/mine/RecordsPage.ets
│       │   │   ├── pages/mine/SettingsPage.ets
│       │   │   ├── components/AsyncStateView.ets
│       │   │   ├── components/ConfirmActionDialog.ets
│       │   │   ├── components/GrowthProgressCard.ets
│       │   │   ├── components/ResourceCard.ets
│       │   │   ├── components/SectionHeader.ets
│       │   │   ├── core/config/Environment.ets
│       │   │   ├── core/http/ApiClient.ets
│       │   │   ├── core/http/ApiError.ets
│       │   │   ├── core/auth/AuthStore.ets
│       │   │   ├── core/cache/CacheStore.ets
│       │   │   ├── core/network/NetworkState.ets
│       │   │   ├── core/notification/ReminderService.ets
│       │   │   ├── core/form/GrowthFormService.ets
│       │   │   ├── models/AuthModels.ets
│       │   │   ├── models/ProfileModels.ets
│       │   │   ├── models/PlanModels.ets
│       │   │   ├── models/ResourceModels.ets
│       │   │   ├── models/AssistantModels.ets
│       │   │   ├── repositories/AuthRepository.ets
│       │   │   ├── repositories/ProfileRepository.ets
│       │   │   ├── repositories/PlanRepository.ets
│       │   │   ├── repositories/ResourceRepository.ets
│       │   │   ├── repositories/AssistantRepository.ets
│       │   │   ├── repositories/RecordsRepository.ets
│       │   │   ├── mock/MockFixtures.ets
│       │   │   ├── state/AppState.ets
│       │   │   └── theme/AppTheme.ets
│       │   └── resources/
│       │       ├── base/element/color.json
│       │       ├── base/element/string.json
│       │       ├── base/profile/main_pages.json
│       │       └── base/profile/form_config.json
│       ├── mock/ets/test/
│       │   ├── ApiClient.test.ets
│       │   ├── AuthStore.test.ets
│       │   ├── CacheStore.test.ets
│       │   ├── Repository.test.ets
│       │   └── ReminderService.test.ets
│       └── ohosTest/ets/test/
│           ├── Ability.test.ets
│           └── UserJourney.test.ets
└── growthform/
    ├── build-profile.json5
    ├── hvigorfile.ts
    ├── oh-package.json5
    └── src/main/
        ├── module.json5
        ├── ets/widget/pages/GrowthCard.ets
        ├── ets/widget/GrowthFormExtensionAbility.ets
        └── resources/base/profile/form_config.json
```

每个文件只承担一个责任。不得把网络请求、缓存、页面布局和业务判断全部写进单个页面文件。

## Task 1：建立工程和接口基线

**Files:**

- Create: `harmony-app/`
- Create: `harmony-app/docs/api-contract.md`
- Create: `harmony-app/README.md`
- Read: `docs/superpowers/specs/2026-07-24-harmonyos-usable-mvp-design.md`
- Read: `demo1/backend/accounts/urls.py`
- Read: `demo1/utils/api.js`

- [ ] **Step 1：保护现有修改**

Run:

```bash
cd "/Users/shuaishuai/Documents/Codex/2026-07-22/ai-agent-agent-3-1-2/work/jiqingfuneng/.worktrees/growth-data-closure"
git status --short --branch
git diff --name-only
```

Expected:

- 当前分支和未提交文件清晰可见；
- 不删除现有修改；
- 如果无法安全建分支，先让原修改者处理。

- [ ] **Step 2：创建HarmonyOS工程**

在 DevEco Studio 中选择：

```text
File → New → Create Project → Application → Empty Ability
```

使用固定参数：

```text
Project name: JiqingZhiyin
Bundle name: com.jiqing.zhiyin
Project directory: 仓库根目录/harmony-app
Language: ArkTS
Device type: Phone
Compile SDK: API 26
Compatible SDK: API 12
Model: Stage
```

Expected:

- DevEco Studio 完成 Sync；
- 默认应用可在API 26手机模拟器启动；
- `harmony-app/entry/src/main/ets/pages/Index.ets` 存在。

- [ ] **Step 3：固定构建命令**

Run from `harmony-app/`:

```bash
./hvigorw clean --no-daemon
./hvigorw assembleHap --mode module -p product=default -p module=entry@default --no-daemon
```

Expected:

- 两条命令退出码为0；
- 生成 `entry-default-signed.hap` 或当前DevEco版本对应的未签名调试HAP。

- [ ] **Step 4：写接口契约文档**

Create `harmony-app/docs/api-contract.md` with this exact contract:

```markdown
# 鸿蒙端 API 契约

所有地址以 `/api` 为基础路径。除注册和登录外，请求头必须带：

`Authorization: Token <当前用户令牌>`

## 已有接口

- POST `/auth/register/`
- POST `/auth/login/`
- GET `/auth/me/`
- GET/POST `/profiles/me/`
- GET `/recommendations/`
- GET `/policies/` 和 GET `/policies/{id}/`
- GET `/opportunities/` 和 GET `/opportunities/{id}/`
- POST `/opportunities/{id}/enroll/`
- GET `/courses/` 和 GET `/courses/{id}/`
- POST `/courses/{id}/complete/`
- GET `/activities/` 和 GET `/activities/{id}/`
- POST `/activities/{id}/enroll/`
- GET `/mentors/`
- POST `/mentors/{id}/consult/`
- POST `/favorites/toggle/`
- GET `/me/growth/`
- GET `/agent/me/dashboard/`

## 鸿蒙智能助手需要的登录用户接口

- GET `/assistant/profile-analysis/`
- POST `/assistant/career-plan/`，请求 `{ "goal": "县域数字运营" }`
- GET `/assistant/policy-search/?keyword=高校毕业生&region=沧州&limit=5`
- POST `/assistant/resource-match/`，请求 `{ "resourceTypes": ["opportunity","course","activity","mentor"], "goal": "数字运营", "limit": 3 }`
- GET `/agent/me/dashboard/`

这些接口使用用户 Token，不使用 `X-Agent-Service-Key`，并复用后台已有画像、规划、政策和资源服务逻辑。

## 错误

- 400：输入不完整；
- 401：未登录或登录过期；
- 404：资源不存在；
- 409：重复报名、重复申请或重复完成；
- 503：服务暂时不可用。

客户端只展示响应中的 `message`，不展示内部堆栈。
```

- [ ] **Step 5：建立接口冻结门**

在 `harmony-app/README.md` 写明：

```markdown
真实联调前必须确认 `docs/api-contract.md` 的全部接口可用。智能助手四个新增登录用户接口未完成时，应用只允许使用 MockFixtures 开发页面，不得把小艺服务密钥写入客户端。
```

- [ ] **Step 6：提交工程基线**

```bash
git add harmony-app
git commit -m "chore: scaffold HarmonyOS phone app"
```

## Task 2：建立主题、导航和通用页面状态

**Files:**

- Create: `harmony-app/entry/src/main/ets/theme/AppTheme.ets`
- Create: `harmony-app/entry/src/main/ets/components/AsyncStateView.ets`
- Create: `harmony-app/entry/src/main/ets/components/SectionHeader.ets`
- Create: `harmony-app/entry/src/main/ets/pages/Index.ets`
- Modify: `harmony-app/entry/src/main/resources/base/element/color.json`
- Modify: `harmony-app/entry/src/main/resources/base/element/string.json`
- Modify: `harmony-app/entry/src/main/resources/base/profile/main_pages.json`
- Test: `harmony-app/entry/src/ohosTest/ets/test/Ability.test.ets`

- [ ] **Step 1：先写导航验收测试**

Create `Ability.test.ets`:

```ts
import { describe, it, expect } from '@ohos/hypium';

export default function abilityTest(): void {
  describe('MainNavigation', () => {
    it('declaresFiveMainTabs', 0, () => {
      const tabs: string[] = ['首页', '规划', '资源', '助手', '我的'];
      expect(tabs.length).assertEqual(5);
      expect(tabs[0]).assertEqual('首页');
      expect(tabs[4]).assertEqual('我的');
    });
  });
}
```

- [ ] **Step 2：运行测试并确认工程可测**

Run:

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
```

Expected: test task completes and reports `MainNavigation` pass. If current Hvigor exposes the test task under a different generated name, use DevEco Studio `Run → Test` once, record the exact generated task in `README.md`, then use that exact task for all later commits.

- [ ] **Step 3：实现颜色常量**

Add to `color.json`:

```json
{
  "color": [
    { "name": "app_background", "value": "#F7FAF8" },
    { "name": "surface", "value": "#FFFFFF" },
    { "name": "primary", "value": "#167D74" },
    { "name": "primary_light", "value": "#DDF3EF" },
    { "name": "accent", "value": "#F29B52" },
    { "name": "text_primary", "value": "#17312F" },
    { "name": "text_secondary", "value": "#607572" },
    { "name": "divider", "value": "#E2EBE8" },
    { "name": "danger", "value": "#C94B45" }
  ]
}
```

- [ ] **Step 4：实现统一布局常量**

Create `AppTheme.ets`:

```ts
export class AppTheme {
  static readonly PAGE_PADDING: number = 16;
  static readonly CARD_RADIUS: number = 16;
  static readonly CARD_GAP: number = 12;
  static readonly TITLE_SIZE: number = 24;
  static readonly SECTION_SIZE: number = 18;
  static readonly BODY_SIZE: number = 15;
  static readonly CAPTION_SIZE: number = 12;
}
```

- [ ] **Step 5：实现五栏入口**

`Index.ets` 使用 ArkUI `Tabs`，固定顺序：

```ts
@Entry
@Component
struct Index {
  @State currentIndex: number = 0;

  build() {
    Tabs({ index: this.currentIndex, barPosition: BarPosition.End }) {
      TabContent() { HomePage() }.tabBar('首页')
      TabContent() { PlanPage() }.tabBar('规划')
      TabContent() { ResourceCenterPage() }.tabBar('资源')
      TabContent() { AssistantPage() }.tabBar('助手')
      TabContent() { MinePage() }.tabBar('我的')
    }
    .barMode(BarMode.Fixed)
    .onChange((index: number) => this.currentIndex = index)
    .backgroundColor($r('app.color.app_background'))
  }
}
```

Import the five page components explicitly at the top of the file.

- [ ] **Step 6：实现统一异步状态**

`AsyncStateView.ets` receives:

```ts
export type AsyncStatus = 'idle' | 'loading' | 'content' | 'empty' | 'error' | 'offline';
```

Component behavior:

- `loading`: display `LoadingProgress` and “正在加载”；
- `empty`: display title, description and optional action；
- `error`: display readable message and retry button；
- `offline`: display “当前离线，正在显示最近保存的内容”；
- `content`: render child content through a builder parameter.

- [ ] **Step 7：构建并提交**

```bash
./hvigorw assembleHap --mode module -p product=default -p module=entry@default --no-daemon
git add harmony-app/entry
git commit -m "feat: add HarmonyOS app shell and theme"
```

Expected: build passes and simulator shows five bottom tabs.

## Task 3：建立数据模型、网络层和安全登录

**Files:**

- Create: `harmony-app/entry/src/main/ets/core/config/Environment.ets`
- Create: `harmony-app/entry/src/main/ets/core/http/ApiError.ets`
- Create: `harmony-app/entry/src/main/ets/core/http/ApiClient.ets`
- Create: `harmony-app/entry/src/main/ets/core/auth/AuthStore.ets`
- Create: `harmony-app/entry/src/main/ets/models/AuthModels.ets`
- Create: `harmony-app/entry/src/main/ets/repositories/AuthRepository.ets`
- Create: `harmony-app/entry/src/mock/ets/test/ApiClient.test.ets`
- Create: `harmony-app/entry/src/mock/ets/test/AuthStore.test.ets`
- Modify: `harmony-app/entry/src/main/module.json5`

- [ ] **Step 1：声明网络权限**

Add to `module.json5`:

```json
"requestPermissions": [
  {
    "name": "ohos.permission.INTERNET"
  },
  {
    "name": "ohos.permission.GET_NETWORK_INFO"
  },
  {
    "name": "ohos.permission.NOTIFICATION",
    "reason": "$string:notification_permission_reason",
    "usedScene": {
      "abilities": ["EntryAbility"],
      "when": "inuse"
    }
  }
]
```

- [ ] **Step 2：定义认证模型**

Create `AuthModels.ets`:

```ts
export interface UserSummary {
  id: number;
  username: string;
  nickname: string;
}

export interface AuthResponse {
  token: string;
  user: UserSummary;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest extends LoginRequest {
  nickname: string;
}
```

- [ ] **Step 3：实现配置哨兵**

Create `Environment.ets`:

```ts
export class Environment {
  static readonly API_BASE_URL: string = 'https://api.jiqing.invalid/api';
  static readonly MOCK_MODE: boolean = true;

  static assertReadyForRealApi(): void {
    if (!this.MOCK_MODE && this.API_BASE_URL.includes('.invalid')) {
      throw new Error('真实构建未配置 API_BASE_URL');
    }
  }
}
```

The committed default must never point to an expired Quick Tunnel. Real integration uses an ignored local configuration or a product-specific build config.

- [ ] **Step 4：实现统一错误**

Create `ApiError.ets`:

```ts
export class ApiError extends Error {
  readonly statusCode: number;
  readonly userMessage: string;

  constructor(statusCode: number, userMessage: string) {
    super(userMessage);
    this.statusCode = statusCode;
    this.userMessage = userMessage;
  }

  isUnauthorized(): boolean {
    return this.statusCode === 401;
  }
}
```

- [ ] **Step 5：实现统一HTTP客户端**

`ApiClient.ets` must:

- import `http` from `@kit.NetworkKit`;
- accept base URL and a token provider;
- set JSON content type;
- add `Authorization: Token <token>` only when a token exists;
- enforce a 15-second connection and read timeout;
- parse JSON responses;
- map 400/401/404/409/503 to `ApiError`;
- destroy each HTTP request after completion;
- never log password, token or response bodies containing private data.

Public interface:

```ts
export interface TokenProvider {
  getToken(): Promise<string>;
}

export class ApiClient {
  constructor(baseUrl: string, tokenProvider: TokenProvider);
  get<T>(path: string): Promise<T>;
  post<T>(path: string, body: object): Promise<T>;
}
```

- [ ] **Step 6：先测试401转换**

In `ApiClient.test.ets`, inject a fake transport returning:

```json
{"statusCode":401,"body":"{\"message\":\"登录已失效，请重新登录\"}"}
```

Assert:

```ts
expect(error.statusCode).assertEqual(401);
expect(error.userMessage).assertEqual('登录已失效，请重新登录');
```

- [ ] **Step 7：实现安全令牌存储**

`AuthStore.ets` uses Asset Store Kit for token storage and Preferences only for non-sensitive user summary.

Public interface:

```ts
export class AuthStore implements TokenProvider {
  saveSession(response: AuthResponse): Promise<void>;
  getToken(): Promise<string>;
  getUser(): Promise<UserSummary | null>;
  hasSession(): Promise<boolean>;
  clearSession(): Promise<void>;
}
```

Asset alias is fixed:

```text
jiqing.auth.token.v1
```

`clearSession()` removes the asset and the cached user summary.

- [ ] **Step 8：实现认证仓库**

`AuthRepository.ets` methods:

```ts
login(request: LoginRequest): Promise<AuthResponse>
register(request: RegisterRequest): Promise<AuthResponse>
getMe(): Promise<UserSummary>
logout(): Promise<void>
```

Paths:

```text
POST /auth/login/
POST /auth/register/
GET /auth/me/
```

Validate before request:

- username is non-empty;
- password length is at least 6;
- nickname is non-empty for registration.

- [ ] **Step 9：验证令牌清理**

Test:

1. Save `test-token`;
2. Assert `hasSession()` is true;
3. Call `clearSession()`;
4. Assert token is empty and cached user is null.

- [ ] **Step 10：构建和提交**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
./hvigorw assembleHap --mode module -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add secure auth and API client"
```

## Task 4：实现登录、注册和首次画像

**Files:**

- Create: `harmony-app/entry/src/main/ets/pages/auth/LoginPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/auth/RegisterPage.ets`
- Create: `harmony-app/entry/src/main/ets/models/ProfileModels.ets`
- Create: `harmony-app/entry/src/main/ets/repositories/ProfileRepository.ets`
- Create: `harmony-app/entry/src/main/ets/pages/onboarding/ProfileWizardPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/onboarding/ProfileResultPage.ets`
- Test: `harmony-app/entry/src/ohosTest/ets/test/UserJourney.test.ets`

- [ ] **Step 1：定义画像模型**

Create `ProfileModels.ets`:

```ts
export interface YouthProfile {
  nickname: string;
  age?: string;
  major: string;
  region: string;
  education: string;
  status: string;
  intents: string[];
  abilities: string[];
  type: string;
  tags: string[];
  summary: string;
}

export interface ProfileResponse {
  profile: YouthProfile;
}
```

Do not add identity-card number, precise address or gender as required fields.

- [ ] **Step 2：实现登录页面**

Requirements:

- username and password fields;
- password masked;
- “登录” button disabled while submitting;
- readable validation;
- successful login saves session, calls `/auth/me/`, and routes according to profile presence;
- 401 or bad credentials do not save any token;
- link to registration.

- [ ] **Step 3：实现注册页面**

Fields:

- username;
- nickname;
- password;
- confirm password.

Rules:

- password at least 6 characters;
- passwords must match;
- submitting twice while loading is blocked;
- successful registration saves session and enters profile wizard.

- [ ] **Step 4：实现4步画像问卷**

Steps:

1. 地区、学历、专业；
2. 当前状态；
3. 发展方向；
4. 兴趣能力和当前困难。

Use fixed initial option arrays matching the current backend:

```ts
export const REGION_OPTIONS: string[] = [
  '沧州市 黄骅市',
  '石家庄市 正定县',
  '秦皇岛市 海港区',
  '承德市 围场县',
  '邯郸市 丛台区',
  '雄安新区'
];

export const EDUCATION_OPTIONS: string[] = ['高中/中职', '大专', '本科', '硕士及以上'];
export const STATUS_OPTIONS: string[] = ['在校', '待就业', '已就业', '创业中', '返乡发展'];
export const INTENT_OPTIONS: string[] = [
  '想找工作',
  '想找实习',
  '想考公考编',
  '想创业',
  '想参加社会实践',
  '想提升技能',
  '想了解政策'
];
```

Back navigation preserves entered values. Final submission is a single POST.

- [ ] **Step 5：实现画像仓库**

```ts
export class ProfileRepository {
  constructor(api: ApiClient);
  getMine(): Promise<ProfileResponse>;
  saveMine(profile: YouthProfile): Promise<ProfileResponse>;
}
```

Paths:

```text
GET /profiles/me/
POST /profiles/me/
```

- [ ] **Step 6：实现画像结果**

Display:

- type;
- summary;
- tags;
- current goal;
- “进入成长首页”.

If profile save fails, remain on the form with entered values and a retry button. Do not route to the home screen as if save succeeded.

- [ ] **Step 7：测试主流程**

`UserJourney.test.ets` must assert:

- registration success opens wizard;
- incomplete current step cannot advance;
- successful profile save opens result;
- result can enter main tabs.

- [ ] **Step 8：构建和提交**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add login and youth profile onboarding"
```

## Task 5：实现首页、规划和智能结果模型

**Files:**

- Create: `harmony-app/entry/src/main/ets/models/PlanModels.ets`
- Create: `harmony-app/entry/src/main/ets/models/AssistantModels.ets`
- Create: `harmony-app/entry/src/main/ets/repositories/PlanRepository.ets`
- Create: `harmony-app/entry/src/main/ets/pages/home/HomePage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/plan/PlanPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/plan/TaskDetailPage.ets`
- Create: `harmony-app/entry/src/main/ets/components/GrowthProgressCard.ets`
- Test: `harmony-app/entry/src/mock/ets/test/Repository.test.ets`

- [ ] **Step 1：定义计划模型**

```ts
export type PlanStage = 'seven_days' | 'one_month' | 'three_months';
export type TaskStatus = 'pending' | 'completed' | 'overdue';

export interface GrowthTask {
  id: number;
  stage: PlanStage;
  title: string;
  reason: string;
  dueAt: string;
  status: TaskStatus;
  resourceType?: string;
  resourceId?: number;
}

export interface GrowthPlan {
  id: number;
  goal: string;
  progress: number;
  tasks: GrowthTask[];
}

export interface DailySuggestion {
  type: string;
  title: string;
  reason: string;
  actionLabel: string;
  resourceType?: string;
  resourceId?: number;
  taskId?: number;
}

export interface DashboardResponse {
  suggestions: DailySuggestion[];
  plan: GrowthPlan | null;
}
```

- [ ] **Step 2：实现首页仓库**

Use:

```text
GET /agent/me/dashboard/
GET /recommendations/
GET /me/growth/
```

The repository combines responses into a `HomeViewData` object. It does not expose raw JSON to `HomePage`.

- [ ] **Step 3：实现首页**

Render in order:

- greeting;
- first daily suggestion;
- plan progress;
- recommendation reason;
- one policy/opportunity/course/activity;
- deadlines.

State behavior:

- no profile: button to complete profile;
- no plan: button to assistant plan generator;
- empty resources: honest empty state;
- offline with cache: offline banner and cached content;
- error without cache: retry state.

- [ ] **Step 4：实现规划页面**

Use three tabs or segmented controls for the three stages.

Each task shows:

- title;
- reason;
- due date;
- status;
- linked resource;
- action button.

Completed tasks remain visible.

- [ ] **Step 5：实现任务详情**

Actions:

- open linked resource;
- mark complete through the authenticated user endpoint;
- show confirmation dialog before completion;
- refresh dashboard and plan after success.

If the existing backend exposes task completion only through small-Yi service authentication, stop real integration and request the backend owner to add:

```text
POST /api/plans/tasks/{id}/complete/
```

The client must not call `/agent/skills/growth-action/` with a bundled service key.

- [ ] **Step 6：test repository mapping**

Fixture:

```json
{
  "suggestions": [
    {
      "type": "task_due",
      "title": "完成数字运营基础课程",
      "reason": "任务将在24小时内到期",
      "actionLabel": "去完成",
      "taskId": 1
    }
  ],
  "plan": {
    "id": 1,
    "goal": "县域数字运营",
    "progress": 33,
    "tasks": []
  }
}
```

Assert first suggestion title and progress equal fixture values.

- [ ] **Step 7：构建和提交**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add growth dashboard and plan pages"
```

## Task 6：实现资源中心和真实行动闭环

**Files:**

- Create: `harmony-app/entry/src/main/ets/models/ResourceModels.ets`
- Create: `harmony-app/entry/src/main/ets/repositories/ResourceRepository.ets`
- Create: `harmony-app/entry/src/main/ets/pages/resource/ResourceCenterPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/resource/ResourceDetailPage.ets`
- Create: `harmony-app/entry/src/main/ets/components/ResourceCard.ets`
- Create: `harmony-app/entry/src/main/ets/components/ConfirmActionDialog.ets`
- Modify: `harmony-app/entry/src/main/ets/pages/mine/RecordsPage.ets`
- Test: `harmony-app/entry/src/mock/ets/test/Repository.test.ets`

- [ ] **Step 1：定义统一资源模型**

```ts
export type ResourceType = 'policy' | 'opportunity' | 'course' | 'activity' | 'mentor';

export interface GrowthResource {
  id: number;
  resourceType: ResourceType;
  title: string;
  region?: string;
  category?: string;
  description?: string;
  deadline?: string;
  startsAt?: string;
  tags: string[];
  reasons: string[];
  sourceUrl?: string;
  favorited: boolean;
  actionState?: string;
}

export interface ResourceListResponse {
  items: GrowthResource[];
}
```

- [ ] **Step 2：实现资源仓库**

Methods:

```ts
list(type: ResourceType): Promise<GrowthResource[]>
detail(type: ResourceType, id: number): Promise<GrowthResource>
toggleFavorite(type: ResourceType, id: number): Promise<boolean>
applyOpportunity(id: number): Promise<void>
enrollActivity(id: number): Promise<void>
completeCourse(id: number): Promise<void>
consultMentor(id: number, scheduledAt: string, question: string): Promise<void>
growthRecords(): Promise<GrowthRecords>
```

Use exact existing paths from `docs/api-contract.md`.

- [ ] **Step 3：实现资源列表**

Tabs:

- 政策；
- 岗位；
- 课程；
- 活动；
- 导师。

Filters:

- keyword;
- region;
- type;
- “适合我的”;
- “即将截止”.

Filtering may initially be local over the fetched list, but repository method signatures must allow later server-side query parameters.

- [ ] **Step 4：实现统一详情页**

The page switches content by `resourceType`. It must not show absent fields as blank rows.

Actions:

- policy: favorite and open official source;
- opportunity: favorite and apply;
- course: favorite and complete;
- activity: favorite and enroll;
- mentor: consult.

- [ ] **Step 5：实现确认弹窗**

Before apply, enroll, complete or consult, show:

- resource title;
- action text;
- consequence;
- cancel;
- confirm.

Disable confirm while request is running.

- [ ] **Step 6：verify real success**

For each action:

1. Call real endpoint;
2. Wait for 2xx response;
3. Show success;
4. Refresh resource state;
5. Refresh growth records.

For 409:

- display backend message;
- mark action state based on refreshed records;
- do not retry automatically.

- [ ] **Step 7：test deadline and duplicate errors**

Tests must assert:

- expired opportunity action is disabled;
- 409 maps to readable duplicate message;
- offline mode blocks all write methods before transport is called;
- source URL is shown only for policy.

- [ ] **Step 8：build and commit**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add resources and verified growth actions"
```

## Task 7：实现按钮式智能助手和个人中心

**Files:**

- Create: `harmony-app/entry/src/main/ets/repositories/AssistantRepository.ets`
- Create: `harmony-app/entry/src/main/ets/pages/assistant/AssistantPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/assistant/AssistantResultPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/mine/MinePage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/mine/ProfilePage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/mine/RecordsPage.ets`
- Create: `harmony-app/entry/src/main/ets/pages/mine/SettingsPage.ets`
- Create: `harmony-app/entry/src/main/ets/mock/MockFixtures.ets`
- Test: `harmony-app/entry/src/mock/ets/test/Repository.test.ets`

- [ ] **Step 1：定义助手模型**

```ts
export type AssistantAction =
  'profile_analysis' |
  'career_plan' |
  'policy_search' |
  'resource_match' |
  'daily_suggestion';

export interface AssistantCard {
  id: string;
  title: string;
  summary: string;
  reasons: string[];
  actionLabel?: string;
  resourceType?: string;
  resourceId?: number;
}

export interface AssistantResult {
  action: AssistantAction;
  title: string;
  message: string;
  cards: AssistantCard[];
}
```

- [ ] **Step 2：implement five repository methods**

```ts
analyzeProfile(): Promise<AssistantResult>
generateCareerPlan(goal: string): Promise<AssistantResult>
searchPolicies(keyword: string, region: string): Promise<AssistantResult>
matchResources(goal: string): Promise<AssistantResult>
getDailySuggestion(): Promise<AssistantResult>
```

Real paths:

```text
GET /assistant/profile-analysis/
POST /assistant/career-plan/
GET /assistant/policy-search/
POST /assistant/resource-match/
GET /agent/me/dashboard/
```

If the first four endpoints are unavailable, `Environment.MOCK_MODE` may return matching fixture structures only in debug builds.

- [ ] **Step 3：create deterministic mock fixtures**

`MockFixtures.ets` includes one complete response per action. Example:

```ts
export const PROFILE_ANALYSIS_FIXTURE: AssistantResult = {
  action: 'profile_analysis',
  title: '你的青年成长画像',
  message: '你目前更接近就业准备型，目标是县域数字运营。',
  cards: [{
    id: 'strengths',
    title: '当前优势',
    summary: '英语表达和内容创作基础较好。',
    reasons: ['专业背景匹配', '已选择数字运营方向'],
    actionLabel: '查看成长计划'
  }]
};
```

Fixtures contain no real user data.

- [ ] **Step 4：implement assistant page**

Show five large action cards with short explanations. No text input field in first version.

For career plan, collect goal in a modal before request.

For policy search, collect keyword and region.

For resource match, allow goal input and fixed resource types.

- [ ] **Step 5：implement reusable result page**

Render:

- title;
- user-facing message;
- cards;
- reasons;
- next action buttons.

Next actions navigate to plan or resource detail. Never show `bindingToken`, service key or raw backend payload.

- [ ] **Step 6：implement Mine**

Display:

- user summary;
- current goal;
- profile completeness;
- growth progress;
- links to profile, favorites, applications, enrollments, courses, consultations, records, notifications and privacy;
- logout.

Logout order:

1. clear secure token;
2. clear user-specific cache;
3. clear form card private data;
4. cancel user reminders;
5. navigate to login.

- [ ] **Step 7：test mock cannot enter release**

Add a build-time assertion:

```ts
if (!BuildProfile.DEBUG && Environment.MOCK_MODE) {
  throw new Error('Release build cannot enable MOCK_MODE');
}
```

If the project template does not expose `BuildProfile.DEBUG`, create separate `default` and `release` product environment files, with release permanently setting `MOCK_MODE=false`.

- [ ] **Step 8：build and commit**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add structured assistant and profile center"
```

## Task 8：实现离线只读和按用户隔离缓存

**Files:**

- Create: `harmony-app/entry/src/main/ets/core/cache/CacheStore.ets`
- Create: `harmony-app/entry/src/main/ets/core/network/NetworkState.ets`
- Create: `harmony-app/entry/src/mock/ets/test/CacheStore.test.ets`
- Modify: all repositories
- Modify: `harmony-app/entry/src/main/ets/components/AsyncStateView.ets`

- [ ] **Step 1：write cache-key tests**

For user IDs 7 and 9, assert keys differ:

```text
jiqing.cache.user.7.dashboard.v1
jiqing.cache.user.9.dashboard.v1
```

Assert logout for user 7 does not delete user 9 cache.

- [ ] **Step 2：implement CacheStore**

Public interface:

```ts
export class CacheStore {
  put<T>(userId: number, namespace: string, value: T): Promise<void>;
  get<T>(userId: number, namespace: string): Promise<T | null>;
  removeUser(userId: number): Promise<void>;
}
```

Namespaces:

```text
profile.v1
dashboard.v1
plan.v1
resources.v1
records.v1
```

Each payload includes:

```ts
interface CacheEnvelope<T> {
  savedAt: number;
  data: T;
}
```

- [ ] **Step 3：implement network state**

`NetworkState.ets` exposes:

```ts
isOnline(): boolean
subscribe(listener: (online: boolean) => void): () => void
```

It uses Network Kit connectivity callbacks and starts with the current network state.

- [ ] **Step 4：add repository read policy**

For read methods:

1. Try network when online;
2. On 2xx, map and cache;
3. On network failure, return cache with `source='cache'`;
4. If no cache, throw readable offline error.

For write methods:

1. Check online;
2. If offline, throw `ApiError(0, '当前离线，联网后才能完成此操作')`;
3. Never queue or fake the write.

- [ ] **Step 5：show cache timestamp**

Offline banner includes:

```text
当前离线，显示最近保存内容 · 更新于 HH:mm
```

- [ ] **Step 6：run tests and commit**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add user-isolated offline read cache"
```

## Task 9：实现本地通知

**Files:**

- Create: `harmony-app/entry/src/main/ets/core/notification/ReminderService.ets`
- Create: `harmony-app/entry/src/mock/ets/test/ReminderService.test.ets`
- Modify: `harmony-app/entry/src/main/ets/pages/mine/SettingsPage.ets`
- Modify: `harmony-app/entry/src/main/module.json5`

- [ ] **Step 1：define reminder model**

```ts
export interface GrowthReminder {
  id: number;
  type: 'task' | 'activity' | 'opportunity' | 'review';
  title: string;
  message: string;
  triggerAt: number;
  route: string;
}
```

- [ ] **Step 2：write quiet-hours tests**

Rules:

- no reminder scheduled between 22:00 and 08:00;
- a 23:00 reminder moves to 08:00 next day;
- disabling a type cancels matching reminders;
- logout cancels all current-user reminders.

- [ ] **Step 3：implement ReminderService**

Use Notification Kit. Public interface:

```ts
requestPermission(): Promise<boolean>
schedule(reminder: GrowthReminder): Promise<void>
cancel(id: number): Promise<void>
cancelAllForCurrentUser(): Promise<void>
rescheduleFromPlan(plan: GrowthPlan): Promise<void>
```

Use stable notification IDs derived from user ID and domain item ID. Do not include sensitive profile or consultation text.

- [ ] **Step 4：implement settings**

Independent switches:

- daily task;
- activity;
- opportunity deadline;
- plan review.

When permission is denied:

- switches remain off;
- display instructions to system settings;
- do not repeatedly prompt on every app launch.

- [ ] **Step 5：test click routing**

Notification extras include only:

```json
{"route":"task","id":12}
```

Clicking opens the correct detail page after authentication. If session is missing, route to login and preserve a safe pending destination.

- [ ] **Step 6：build and commit**

```bash
./hvigorw test -p product=default -p module=entry@default --no-daemon
git add harmony-app
git commit -m "feat: add local growth reminders"
```

## Task 10：实现桌面成长卡片

**Files:**

- Create: `harmony-app/growthform/`
- Create: `harmony-app/growthform/src/main/ets/widget/pages/GrowthCard.ets`
- Create: `harmony-app/growthform/src/main/ets/widget/GrowthFormExtensionAbility.ets`
- Create: `harmony-app/growthform/src/main/resources/base/profile/form_config.json`
- Create: `harmony-app/entry/src/main/ets/core/form/GrowthFormService.ets`
- Modify: root `harmony-app/build-profile.json5`

- [ ] **Step 1：add form module with DevEco template**

Use:

```text
File → New → Module → Form
Module name: growthform
Form name: GrowthCard
Language: ArkTS
```

Expected: Form Kit module builds before custom business code.

- [ ] **Step 2：define safe card data**

```ts
export interface GrowthFormData {
  loggedIn: boolean;
  taskTitle: string;
  progress: number;
  deadlineText: string;
  route: string;
}
```

No nickname, consultation, application result, token or detailed profile is included.

- [ ] **Step 3：implement card states**

Logged out:

```text
登录冀青智引，查看今日成长任务
```

Logged in without plan:

```text
完成青年画像，生成第一份成长计划
```

Logged in with plan:

- today task;
- progress;
- nearest deadline;
- open app.

- [ ] **Step 4：implement GrowthFormService**

```ts
updateFromDashboard(dashboard: DashboardResponse): Promise<void>
showLoggedOut(): Promise<void>
```

Call update after:

- login;
- dashboard refresh;
- task completion;
- plan regeneration;
- logout.

- [ ] **Step 5：test privacy and navigation**

Inspect serialized card data and assert it does not contain:

```text
token
password
bindingToken
question
applicationResult
```

Click opens app route, but any write action still occurs inside the authenticated app.

- [ ] **Step 6：build and commit**

```bash
./hvigorw assembleHap --mode project -p product=default --no-daemon
git add harmony-app
git commit -m "feat: add daily growth home-screen card"
```

## Task 11：完成真实后台联调

**Files:**

- Modify: `harmony-app/entry/src/main/ets/core/config/Environment.ets`
- Modify: repository adapters as needed
- Modify: `harmony-app/docs/api-contract.md`
- Create: `harmony-app/docs/test-record.md`
- Test: `harmony-app/entry/src/ohosTest/ets/test/UserJourney.test.ets`

- [ ] **Step 1：freeze backend**

Before integration:

```bash
cd demo1/backend
./.venv/bin/python manage.py makemigrations --check
./.venv/bin/python manage.py test -v 1
./.venv/bin/python -m unittest tests.test_entrypoint -v
```

Expected:

- no pending migrations;
- all backend tests pass;
- assistant user-token endpoints exist or are explicitly excluded from the real build.

- [ ] **Step 2：start backend and HTTPS**

Use the deployment or Quick Tunnel instructions already in:

```text
demo1/backend/README.md
```

Verify:

```bash
curl --fail https://实际地址/api/health/
```

Expected HTTP 200.

- [ ] **Step 3：configure local real API**

Set development product:

```text
MOCK_MODE=false
API_BASE_URL=https://实际地址/api
```

Keep the random Quick Tunnel URL out of Git.

- [ ] **Step 4：run contract smoke test**

With a test account, verify:

- register;
- login;
- me;
- save profile;
- dashboard;
- each resource list/detail;
- favorite;
- opportunity apply;
- activity enroll;
- course complete;
- mentor consult;
- growth records;
- five assistant actions.

Record request path, status code and result in `docs/test-record.md`. Never record tokens or passwords.

- [ ] **Step 5：fix only adapter mismatches**

When backend fields differ, update repository mapping. Do not spread raw backend fields into pages.

- [ ] **Step 6：run complete user journey**

Use a clean test account and execute the 18-step acceptance flow from the design specification. Record pass/fail and evidence.

- [ ] **Step 7：commit integration**

```bash
git add harmony-app
git commit -m "feat: integrate HarmonyOS app with live backend"
```

## Task 12：真机、隐私、构建和交付

**Files:**

- Modify: `harmony-app/README.md`
- Modify: `harmony-app/docs/test-record.md`
- Create: `harmony-app/docs/known-issues.md`
- Inspect: all `harmony-app/` source files

- [ ] **Step 1：scan for secrets**

Run:

```bash
rg -n "JIQING_AGENT_SERVICE_KEY|bindingToken|Token [A-Za-z0-9]|trycloudflare\\.com|password\\s*[:=]\\s*['\\\"]" harmony-app
```

Expected:

- no actual secret;
- no temporary tunnel URL;
- only model field names or documentation-safe examples.

- [ ] **Step 2：verify release mock guard**

Build release configuration with `MOCK_MODE=true`.

Expected: build or startup fails with the explicit mock-mode safety message.

Then set release `MOCK_MODE=false` and use the approved stable HTTPS API.

- [ ] **Step 3：run automated tests**

```bash
./hvigorw clean --no-daemon
./hvigorw test -p product=default -p module=entry@default --no-daemon
./hvigorw assembleHap --mode project -p product=default --no-daemon
```

Expected: all tests and build pass.

- [ ] **Step 4：test on simulator**

Record:

- HarmonyOS version/API;
- screen size;
- portrait layout;
- login/profile;
- five tabs;
- offline banner;
- notification permission;
- card installation.

- [ ] **Step 5：test on physical phone**

Verify:

- HTTPS access;
- secure session survives normal restart;
- logout removes private state;
- local notification arrives and routes correctly;
- card updates after task completion;
- app resumes after backgrounding;
- no private information appears on card or notification.

- [ ] **Step 6：accessibility and content review**

Check:

- text scaling;
- contrast;
- button touch targets;
- loading and error messages;
- no raw error code;
- Chinese wording is understandable to non-technical users.

- [ ] **Step 7：complete README**

README must contain:

- required DevEco Studio and SDK;
- project import steps;
- mock and real environment configuration;
- build and test commands;
- backend dependency;
- notification permission;
- form card installation;
- known limitations;
- release checklist.

- [ ] **Step 8：create delivery evidence**

Provide:

- DevEco Studio project;
- source code;
- debug/release HAP as allowed by competition;
- test report;
- simulator screenshots;
- physical-device screenshots;
- 1–3 minute flow recording;
- known issues;
- Git commit history.

- [ ] **Step 9：final commit**

```bash
git add harmony-app
git commit -m "release: complete usable HarmonyOS MVP"
```

## 2. Completion Gate

Do not claim completion unless all checks are true:

- [ ] User can register and log in.
- [ ] New user completes the four-step profile.
- [ ] Home shows a real suggestion.
- [ ] Plan shows 7-day, 1-month and 3-month stages.
- [ ] User can complete a plan task.
- [ ] Five resource types load from real backend.
- [ ] Favorite, apply, enroll, complete and consult actions return real success.
- [ ] Growth records show those actions.
- [ ] Five structured assistant actions work without a client service key.
- [ ] Offline mode is read-only.
- [ ] Cache is isolated per user and cleared on logout.
- [ ] Local reminders work.
- [ ] Home-screen card works without exposing private data.
- [ ] Automated tests pass.
- [ ] Simulator and physical-phone tests are recorded.
- [ ] Release build has mock mode disabled.
- [ ] No secret or expired Quick Tunnel URL is committed.

## 3. Official references to verify at execution time

HarmonyOS APIs and DevEco Studio may update. Before implementing the corresponding module, verify the current API 26 official guide:

- HarmonyOS documentation center: `https://developer.huawei.com/consumer/cn/doc/`
- Application development guide: `https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-v5/application-dev-guide-V5`
- Form Kit: `https://developer.huawei.com/consumer/cn/sdk/form-kit/`
- Asset Store Kit overview: `https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V14/asset-store-kit-overview-V14`

If an API name changed, update only the infrastructure adapter and record the official replacement in `harmony-app/docs/known-issues.md`; do not change the approved product behavior.

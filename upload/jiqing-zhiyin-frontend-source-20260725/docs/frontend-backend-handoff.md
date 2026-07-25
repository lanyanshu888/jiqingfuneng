# 冀青智引前后端交接文档

交接日期：2026-07-25

## 项目边界

本项目当前由前端负责 HarmonyOS 客户端开发，后端同事负责真实 API 服务、数据库、账号体系、智能推荐/助手服务以及线上部署。

前端当前状态：

- 页面和主要交互流程已可本地预览。
- Mock 数据可支撑比赛演示。
- 真实 API 请求通道已接入。
- 安全存储、离线缓存、通知、桌面卡片等 HarmonyOS 系统能力已完成基础接入。
- 正式后端地址、关闭 Mock、关闭 Debug、签名证书属于最终交付配置项，需等后端和证书齐备后完成。

## 前端代码位置

主项目目录：

```text
D:\系统用户目录\桌面\比赛\harmony-app
```

DevEco 构建目录：

```text
D:\JiqingZhiyin\harmony-app
```

由于 DevEco/Hvigor 对中文路径兼容不稳定，构建时使用英文路径副本。

最新构建产物：

```text
D:\JiqingZhiyin\harmony-app\build\outputs\default\harmony-app-default-unsigned.app
```

## 后端需要提供

请后端同事交付以下内容：

1. 稳定 HTTPS API 地址，例如 `https://api.example.com/api`
2. 测试账号用户名
3. 测试账号密码
4. 接口字段与 [api-contract.md](./api-contract.md) 的差异说明
5. 错误码和错误 `message` 文案约定
6. 智能助手服务是否同步返回，还是异步任务返回
7. 资源数据来源说明：政策、机会、课程、活动、导师
8. 正式部署环境和测试环境的地址区分

## 前端已调用的接口清单

认证：

- POST `/auth/login/`
- POST `/auth/register/`
- GET `/auth/me/`

画像：

- GET `/profiles/me/`
- POST `/profiles/me/`

首页和成长：

- GET `/agent/me/dashboard/`
- GET `/me/growth/`

资源：

- GET `/policies/`
- GET `/policies/{id}/`
- GET `/opportunities/`
- GET `/opportunities/{id}/`
- POST `/opportunities/{id}/enroll/`
- GET `/courses/`
- GET `/courses/{id}/`
- POST `/courses/{id}/complete/`
- GET `/activities/`
- GET `/activities/{id}/`
- POST `/activities/{id}/enroll/`
- GET `/mentors/`
- GET `/mentors/{id}/`
- POST `/mentors/{id}/consult/`
- POST `/favorites/toggle/`

智能助手：

- GET `/assistant/profile-analysis/`
- POST `/assistant/career-plan/`
- GET `/assistant/policy-search/`
- POST `/assistant/resource-match/`

## 联调验收方式

后端完成接口后，前端先运行：

```powershell
$env:JIQING_API_BASE_URL="https://api.example.com/api"
$env:JIQING_TEST_USERNAME="test-user"
$env:JIQING_TEST_PASSCODE="test-pass"
node tools\smoke-api.mjs
```

通过后再切换前端配置：

```ts
Environment.API_BASE_URL = 'https://api.example.com/api'
Environment.MOCK_MODE = false
Environment.DEBUG = false
```

然后使用 DevEco 构建安装包并跑完整流程。

## 当前剩余交付项

这些不是前端单独能闭环的事项，需要后端或证书配合：

- 正式 HTTPS 后端地址
- 测试账号
- 真实数据
- 后端接口烟测通过
- 正式签名配置

前端可继续完成的事项：

- 根据后端字段差异调整 repository 适配层
- 真机联调截图和问题记录
- 最终交付包构建
- 更新 `docs/test-record.md` 和 `docs/delivery-status.md`

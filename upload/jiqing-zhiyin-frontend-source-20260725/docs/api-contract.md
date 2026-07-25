# 冀青智引前端 API 契约

本文档描述 HarmonyOS 前端当前已经接入的真实接口路径。所有路径均以 `Environment.API_BASE_URL` 为基准，默认示例为 `/api` 前缀。

除注册、登录外，所有接口请求头均需要：

```http
Authorization: Token <当前登录用户 token>
Accept: application/json
Content-Type: application/json
```

## 认证

### POST `/auth/login/`

请求：

```json
{
  "username": "test-user",
  "password": "test-pass"
}
```

响应：

```json
{
  "token": "token-string",
  "user": {
    "id": 1,
    "username": "test-user",
    "nickname": "小冀"
  }
}
```

### POST `/auth/register/`

请求：

```json
{
  "username": "test-user",
  "password": "test-pass",
  "nickname": "小冀"
}
```

响应同登录接口。

### GET `/auth/me/`

响应：

```json
{
  "id": 1,
  "username": "test-user",
  "nickname": "小冀"
}
```

## 用户画像

### GET `/profiles/me/`

返回当前用户画像。字段需要覆盖前端画像表单使用的数据，建议至少包含：

```json
{
  "nickname": "小冀",
  "region": "河北沧州",
  "education": "本科",
  "major": "数字媒体技术",
  "skills": ["内容运营", "数据分析"],
  "interests": ["政策", "课程", "岗位"],
  "goal": "县域数字运营"
}
```

### POST `/profiles/me/`

请求为完整画像对象，响应为画像生成结果：

```json
{
  "summary": "画像摘要",
  "strengths": ["优势 1", "优势 2"],
  "suggestions": ["建议 1", "建议 2"]
}
```

## 首页与成长计划

### GET `/agent/me/dashboard/`

响应：

```json
{
  "nickname": "小冀",
  "currentGoal": "县域数字运营",
  "profileCompleteness": 86,
  "progress": 42,
  "suggestion": "今日建议文案",
  "plan": {
    "goal": "县域数字运营",
    "progress": 42,
    "todayTask": {
      "id": 1001,
      "title": "完成政策匹配",
      "description": "查看适合你的河北青年政策",
      "stage": "7days",
      "deadlineText": "今天 20:00 前",
      "completed": false
    },
    "tasks": [
      {
        "id": 1001,
        "title": "完成政策匹配",
        "description": "查看适合你的河北青年政策",
        "stage": "7days",
        "deadlineText": "今天 20:00 前",
        "completed": false
      }
    ]
  }
}
```

`stage` 可选值：`7days`、`1month`、`3months`。

### GET `/me/growth/`

响应：

```json
{
  "favorites": 3,
  "applications": 1,
  "enrollments": 2,
  "completedCourses": 4,
  "consultations": 1
}
```

## 资源中心

列表接口可以返回数组，也可以返回 `{ "items": [...] }`，前端真实分支当前按 `{ "items": [...] }` 读取。

### GET `/policies/`
### GET `/opportunities/`
### GET `/courses/`
### GET `/activities/`
### GET `/mentors/`

列表响应：

```json
{
  "items": [
    {
      "id": 1,
      "resourceType": "policy",
      "title": "河北青年就业见习政策",
      "region": "河北",
      "category": "就业",
      "description": "资源简介",
      "deadline": "2026-08-31",
      "startsAt": "2026-08-01 09:00",
      "tags": ["青年", "就业"],
      "reasons": ["与你的目标匹配", "地区匹配"],
      "sourceUrl": "https://example.com",
      "favorited": false,
      "actionState": ""
    }
  ]
}
```

`resourceType` 可选值：`policy`、`opportunity`、`course`、`activity`、`mentor`。

详情接口：

- GET `/policies/{id}/`
- GET `/opportunities/{id}/`
- GET `/courses/{id}/`
- GET `/activities/{id}/`
- GET `/mentors/{id}/`

详情响应为单个资源对象。

资源动作：

- POST `/favorites/toggle/`

```json
{
  "resourceType": "opportunity",
  "resourceId": 1
}
```

响应：

```json
{
  "favorited": true
}
```

- POST `/opportunities/{id}/enroll/`
- POST `/courses/{id}/complete/`
- POST `/activities/{id}/enroll/`
- POST `/mentors/{id}/consult/`

导师咨询请求：

```json
{
  "scheduledAt": "2026-08-01 10:00",
  "question": "我想咨询职业规划"
}
```

这些动作接口成功时可返回空对象 `{}`。

## 智能助手

### GET `/assistant/profile-analysis/`

### POST `/assistant/career-plan/`

请求：

```json
{
  "goal": "县域数字运营"
}
```

### GET `/assistant/policy-search/?keyword=高校毕业生&region=沧州&limit=5`

### POST `/assistant/resource-match/`

请求：

```json
{
  "resourceTypes": ["opportunity", "course", "activity", "mentor"],
  "goal": "数字运营",
  "limit": 3
}
```

助手接口统一响应：

```json
{
  "action": "career_plan",
  "title": "成长规划",
  "message": "分析结果正文",
  "cards": [
    {
      "id": "card-1",
      "title": "卡片标题",
      "summary": "卡片摘要",
      "reasons": ["推荐理由 1", "推荐理由 2"],
      "actionLabel": "查看详情"
    }
  ]
}
```

## 错误格式

建议所有错误响应统一返回：

```json
{
  "message": "可展示给用户的错误说明"
}
```

状态码约定：

- 400：输入不完整或参数错误
- 401：未登录或 token 失效
- 404：资源不存在
- 409：重复报名、重复申请、重复收藏等业务冲突
- 500：服务端错误
- 503：依赖服务暂不可用

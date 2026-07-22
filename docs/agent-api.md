# 冀青智引 Agent API

## 约定

- 基础地址：`https://你的域名/api`
- 小程序个人接口：`Authorization: Token <用户登录令牌>`
- 小艺服务接口：`X-Agent-Service-Key: <服务端密钥>`
- 小艺 Skill 请求中的 `externalUserId` 必须使用平台提供的当前用户标识，不能由对话用户自由指定。

所有 Skills 返回：

```json
{
  "ok": true,
  "message": "面向用户的结果",
  "data": {},
  "sources": [],
  "requiresConfirmation": false,
  "errorCode": null
}
```

## 1. 生成一次性绑定码

`POST /agent/binding-code/`，使用小程序用户 Token。

```bash
curl -X POST https://api.example.com/api/agent/binding-code/ \
  -H 'Authorization: Token example-user-token'
```

成功返回六位 `code`、`expiresAt` 和 `expiresIn=600`。后端只保存摘要，旧码和使用过的码失效。

## 2. 绑定小艺账号

`POST /agent/bind/`，使用服务密钥。

```bash
curl -X POST https://api.example.com/api/agent/bind/ \
  -H 'Content-Type: application/json' \
  -H 'X-Agent-Service-Key: example-agent-service-key' \
  -d '{"externalUserId":"xiaoyi-user-001","code":"482731"}'
```

常见错误：`BINDING_CODE_INVALID`、`BINDING_CODE_EXPIRED`、`EXTERNAL_ID_ALREADY_BOUND`。

## 3. 青年画像

`POST /agent/skills/profile-context/`

读取：

```json
{"externalUserId":"xiaoyi-user-001","operation":"read"}
```

更新分两次。首次发送变更但不确认，响应为 `requiresConfirmation=true`；用户明确同意后发送：

```json
{
  "externalUserId":"xiaoyi-user-001",
  "operation":"update",
  "changes":{"region":"河北省沧州市黄骅市","major":"电子商务"},
  "confirmed":true
}
```

## 4. 职业规划

`POST /agent/skills/career-plan/`

```json
{"externalUserId":"xiaoyi-user-001","goal":"在河北县域从事数字运营"}
```

返回 7 天、1 个月、3 个月任务和生成依据。画像或目标不完整时返回 `PROFILE_INCOMPLETE` 与 `missingFields`。

## 5. 政策检索

`POST /agent/skills/policy-search/`

```json
{
  "externalUserId":"xiaoyi-user-001",
  "keyword":"高校毕业生就业",
  "region":"沧州",
  "limit":5
}
```

只返回已发布且未过期政策。`data.items` 包含适用理由、条件、材料、流程和办理信息；`sources` 包含发布来源、发布日期和有效期。无结果时返回空数组，不生成替代政策。

## 6. 资源匹配

`POST /agent/skills/resource-match/`

```json
{
  "externalUserId":"xiaoyi-user-001",
  "resourceTypes":["opportunity","course","activity","mentor"],
  "goal":"数字运营",
  "limit":3
}
```

每项返回 `resourceType`、`resourceId`、`score` 和 `reasons`。

## 7. 成长行动

`POST /agent/skills/growth-action/`

允许操作：`enroll_activity`、`apply_opportunity`、`favorite_resource`、`complete_course`、`complete_task`。

首次预览：

```json
{"externalUserId":"xiaoyi-user-001","action":"enroll_activity","resourceId":12}
```

响应包含 `requiresConfirmation=true` 和 `data.confirmationToken`。用户明确确认后，第二次调用必须原样携带动作与资源：

```json
{
  "externalUserId":"xiaoyi-user-001",
  "action":"enroll_activity",
  "resourceId":12,
  "confirmed":true,
  "confirmationToken":"首次调用返回的令牌"
}
```

令牌默认 5 分钟有效，并绑定用户、动作和资源。常见错误：`CONFIRMATION_INVALID`、`CONFIRMATION_EXPIRED`、`CONFIRMATION_MISMATCH`、`RESOURCE_UNAVAILABLE`。

## 8. 今日建议

小艺调用 `POST /agent/skills/daily-suggestion/`：

```json
{"externalUserId":"xiaoyi-user-001"}
```

小程序调用 `GET /agent/me/dashboard/`，使用用户 Token。两端复用相同建议逻辑，优先级依次为逾期任务、24 小时内到期任务、画像补全和匹配资源。

## 通用错误

| 错误码 | 含义 |
|---|---|
| `INVALID_SERVICE_CREDENTIAL` | 服务密钥缺失或错误 |
| `AGENT_USER_NOT_BOUND` | 当前小艺身份尚未绑定 |
| `INVALID_JSON` | 请求不是合法 JSON 对象 |
| `PROFILE_INCOMPLETE` | 制定规划所需字段不完整 |
| `ACTION_NOT_SUPPORTED` | 不支持该写操作 |
| `RESOURCE_UNAVAILABLE` | 资源不存在、未发布或已过期 |

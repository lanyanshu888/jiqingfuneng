# 小艺 Agent 配置包

本目录用于把“冀青智引”配置到小艺开放平台测试态。Django 负责真实数据与动作，小艺负责对话和 Skills 编排。

## 配置顺序

1. 将 Django 服务部署为 HTTPS，并把 `openapi.yaml` 的 `servers[0].url` 改成实际 `/api` 地址。
2. 在服务器设置随机生成的 `JIQING_AGENT_SERVICE_KEY`，建议不少于 32 个字符。
3. 在小艺开放平台创建 Agent，将 `system-prompt.md` 内容作为系统提示词。
4. 在平台的工具、插件或 Skills 配置入口导入 `openapi.yaml`。控制台入口名称可能调整，以当前页面显示为准。
5. 将同一个服务密钥安全配置为 `X-Agent-Service-Key`，不要写进提示词或用户可见字段。
6. 将绑定成功返回的 `bindingToken` 保存为当前平台用户的私密状态，后续 Skills 同时传入稳定 `externalUserId` 与该令牌；若当前平台无法安全保存逐用户私密状态，不得上线个人数据 Skills，应改接平台签名身份能力。
7. 按 `test-cases.md` 逐项联调，再按 `conversation-examples.md` 检查自然对话。

## 公网联调

部署完成后先访问 `https://<实际域名>/api/health/`。确认返回 200，再把 `openapi.yaml` 中唯一的 `servers[0].url` 改为 `https://<实际域名>/api`。

服务密钥只配置在平台私密参数中。测试态联调通过后仍需团队成员在小艺开放平台手动确认发布，部署脚本不会自动创建、提交或发布 Agent。

## 发布前检查

- 服务地址为公网 HTTPS，健康检查 `/api/health/` 返回 200。
- 七个 operationId 均可识别：绑定加六项 Skills。
- 未绑定用户不能读取画像；政策结果带来源；所有写动作都会二次确认。
- 平台测试态验证完成前，不在材料中写“已上线”或“已发布”。

本地合约验证：

```bash
cd demo1/backend
.venv/bin/python manage.py test accounts.test_xiaoyi_contract -v 2
```

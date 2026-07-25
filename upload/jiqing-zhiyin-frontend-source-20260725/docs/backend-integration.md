# 后端联调说明

前端当前以 Mock 数据保证本地预览可用，同时已经接入真实 NetworkKit 请求通道。后端准备好接口后，只需要替换 API 地址并关闭 Mock 即可进入联调。

## 前端配置位置

文件：[Environment.ets](../entry/src/main/ets/core/config/Environment.ets)

```ts
static readonly API_BASE_URL: string = 'https://api.example.com/api';
static readonly MOCK_MODE: boolean = false;
static readonly DEBUG: boolean = false;
```

说明：

- `API_BASE_URL` 必须是稳定 HTTPS 地址。
- `MOCK_MODE=true` 时页面使用本地假数据，适合演示和前端开发。
- `MOCK_MODE=false` 时 repository 层会走真实后端接口。
- `DEBUG=false` 用于正式交付构建。

## 前端已经完成的联调基础能力

- 真实请求：`@kit.NetworkKit`
- Token 安全存储：`@kit.AssetStoreKit`
- 离线缓存：`@kit.ArkData` Preferences
- 系统通知：`@kit.NotificationKit`
- 桌面卡片数据更新：`@kit.FormKit`
- 本地校验脚本：`tools/validate-local.mjs`
- 后端烟测脚本：`tools/smoke-api.mjs`

## 烟测脚本

后端同事提供测试账号后，在项目根目录运行：

```powershell
$env:JIQING_API_BASE_URL="https://api.example.com/api"
$env:JIQING_TEST_USERNAME="test-user"
$env:JIQING_TEST_PASSCODE="test-pass"
node tools\smoke-api.mjs
```

脚本会验证：

- 登录
- 当前用户
- 用户画像
- 首页 Dashboard
- 成长记录
- 政策、机会、课程、活动、导师列表
- 智能助手四个动作

脚本只输出路径、状态码和摘要，不输出密码或 token。

## 联调顺序

1. 后端按 [api-contract.md](./api-contract.md) 提供接口。
2. 后端提供 HTTPS API 地址、测试用户名、测试密码。
3. 前端先运行 `tools/smoke-api.mjs` 验证契约。
4. 前端把 `Environment.MOCK_MODE` 改成 `false`，把 `API_BASE_URL` 改成后端地址。
5. 使用 DevEco/Hvigor 构建并在模拟器或真机跑完整流程。
6. 确认无问题后再配置正式签名。

## 注意事项

- 不要把测试密码、token、临时公网隧道地址提交到仓库。
- 后端字段名请尽量与本文档保持一致，减少前端适配成本。
- 如果必须使用不同字段名，请后端同事在交接时列出字段映射表。
- 错误响应请统一返回 `message`，前端会优先展示该字段。

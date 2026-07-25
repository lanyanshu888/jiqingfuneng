# 已知问题

更新日期：2026-07-25

## 当前已知限制

- 默认 `Environment.MOCK_MODE=true`，用于保证前端本地预览和比赛演示稳定；后端接口完成后需要切换为 `false`。
- 默认 `Environment.API_BASE_URL=https://api.jiqing.invalid/api`，这是占位地址，不能用于真实联调。
- 默认 `Environment.DEBUG=true`，正式交付前需要按比赛要求调整。
- 当前构建包未配置正式签名，生成的是 unsigned/debug 产物。
- 桌面卡片已接入 FormKit 更新能力，但仍需要在模拟器桌面或真机上验证“添加卡片、刷新卡片、移除卡片”的完整系统流程。
- 通知服务已接入 NotificationKit，但 DevEco Studio 6.1.1 当前 SDK 未识别原计划中的 `ohos.permission.NOTIFICATION` manifest 权限；如后续目标 SDK 要求显式权限，需要按当时 SDK 文档补充。
- 尚未完成真实后端联调、真机测试、录屏和最终测试报告。

## 已修复或已完成

- 已解决中文路径导致 DevEco/Hvigor 构建不稳定的问题，改用 `D:\JiqingZhiyin\harmony-app` 英文路径构建。
- 已修复只安装 `growthform` 导致主应用入口缺失的问题。
- 已实现真实 `ApiClient`，使用 `@kit.NetworkKit`。
- 已实现 token 安全存储，使用 `@kit.AssetStoreKit`。
- 已实现离线缓存持久化，使用 `@kit.ArkData` Preferences。
- 已实现通知发布/取消能力，使用 `@kit.NotificationKit`。
- 已实现桌面卡片数据更新服务，使用 `@kit.FormKit`。
- 已补充后端交接文档和 API 契约文档。

## 后端联调风险

- 如果后端返回字段名与 `docs/api-contract.md` 不一致，需要前端在 repository 层做字段映射。
- 如果智能助手接口为异步任务模式，需要新增任务轮询或结果页等待状态。
- 如果资源列表返回分页结构，需要前端补充分页适配。
- 如果 token 类型不是 `Token <token>`，需要调整 `ApiClient` 的 Authorization 头。

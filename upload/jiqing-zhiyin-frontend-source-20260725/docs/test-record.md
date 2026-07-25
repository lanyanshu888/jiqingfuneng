# 测试记录

| 日期 | 环境 | 项目 | 结果 | 备注 |
| --- | --- | --- | --- | --- |
| 2026-07-24 | 本地源码生成 | 关键源码路径生成 | 通过 | 生成 `entry` 与 `growthform` 两个模块 |
| 2026-07-24 | 本地源码生成 | 敏感信息扫描 | 通过 | 未发现服务密钥、临时隧道、明文 token |
| 2026-07-24 | 本地源码生成 | 本地自检脚本 | 通过 | `node tools/validate-local.mjs` |
| 2026-07-25 | DevEco Studio 6.1.1 | 英文路径 PackageApp 构建 | 通过 | `D:\JiqingZhiyin\harmony-app` 构建成功 |
| 2026-07-25 | HarmonyOS 模拟器 | 完整 `.app` 安装运行 | 通过 | 修正只安装 `growthform` 的问题后，`EntryAbility` 成功运行 |
| 2026-07-25 | HarmonyOS 模拟器 | 页面截图验证 | 通过 | 已验证首页、规划页、资源页显示正常 |
| 2026-07-25 | 本地环境 | SDK 镜像迁移 | 通过 | `C:\ProgramData\huawei\Sdk` 已连接到 `D:\HuaweiSdk\Sdk` |
| 2026-07-25 | DevEco Studio 6.1.1 | NetworkKit ApiClient 构建 | 通过 | 真实网络层可构建 |
| 2026-07-25 | DevEco Studio 6.1.1 | AssetStoreKit token 存储构建 | 通过 | 安全 token 存储可构建 |
| 2026-07-25 | DevEco Studio 6.1.1 | ArkData Preferences 缓存构建 | 通过 | 离线缓存持久化可构建 |
| 2026-07-25 | DevEco Studio 6.1.1 | NotificationKit 提醒服务构建 | 通过 | 通知发布/取消能力可构建 |
| 2026-07-25 | DevEco Studio 6.1.1 | FormKit 桌面卡片更新构建 | 通过 | 卡片数据更新服务可构建 |
| 2026-07-25 | 本地交付检查 | 本地自检脚本 | 通过 | `node tools/validate-local.mjs`，检查 23 个关键文件 |
| 2026-07-25 | 本地交付检查 | 后端烟测脚本语法 | 通过 | `node --check tools/smoke-api.mjs` |
| 2026-07-25 | 本地交付检查 | 发布审计脚本 | 未通过 | 剩余 4 项：后端地址、关闭 Mock、关闭 Debug、正式签名 |

## 待后端完成后验证

- 使用真实 API 运行 `node tools/smoke-api.mjs`
- 切换 `Environment.MOCK_MODE=false`
- 模拟器完整流程验证
- 真机完整流程验证
- 桌面卡片添加/刷新/移除验证
- 通知权限与通知展示验证
- 最终录屏和截图归档

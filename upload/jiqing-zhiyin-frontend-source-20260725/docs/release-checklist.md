# 正式交付检查清单

## 构建环境

- 使用英文路径打开项目：`D:\JiqingZhiyin\harmony-app`。
- DevEco Studio: 6.1.1。
- HarmonyOS SDK: 6.1.1(API 24)。
- 模拟器或真机可以被 `hdc list targets` 识别。
- SDK 镜像已迁移到 `D:\HuaweiSdk\Sdk`，`C:\ProgramData\huawei\Sdk` 为目录联接。

## 必须通过

- `node tools/validate-local.mjs`
- `PackageApp` 构建成功。
- 完整 `.app` 包安装成功，不只安装 `growthform`。
- 首页、规划、资源、助手、我的五个 Tab 均可打开。
- 完成任务后页面状态更新。
- 资源收藏、申请、报名、完成、预约的真实接口返回 2xx 后才提示成功。
- 离线时写操作被阻止，读操作显示缓存时间。
- 退出登录清除 Token、用户缓存、卡片私有数据和提醒。

## 发布前必须替换

- `Environment.MOCK_MODE` 改为 `false`。
- `Environment.API_BASE_URL` 改为稳定 HTTPS 后端地址。
- `ApiClient.ets` 接入真实 Network Kit 请求。
- `AuthStore.ets` 使用 Asset Store Kit 保存 Token。
- `CacheStore.ets` 使用持久化存储并按用户隔离。
- `ReminderService.ets` 接入 Notification Kit。
- `GrowthFormService.ets` 接入 Form Kit 更新桌面卡片。

## 交付证据

- DevEco 构建截图。
- 模拟器运行截图：首页、规划、资源、助手、我的。
- 真机运行截图。
- 1 到 3 分钟流程录屏。
- 后端联调记录：路径、状态码、结果，不记录 Token 或密码。
- 敏感信息扫描记录。

可以在模拟器启动后运行：

```powershell
powershell -ExecutionPolicy Bypass -File tools\collect-evidence.ps1
```

脚本会保存五个 Tab 截图和应用状态 dump 到 `docs\evidence\时间戳`。

## 发布审计

正式发布前运行：

```bash
node tools/release-audit.mjs
```

当前本地 MVP 预期会失败，因为 Mock、真实网络、正式 Token 存储、持久化缓存、通知、卡片和签名尚未全部替换。审计脚本用于明确剩余工作，不能替代真机验收。

# 冀青智引 HarmonyOS 应用

这是“冀青智引”鸿蒙手机端 MVP 源码骨架，使用 ArkTS/ArkUI Stage 模型组织。当前默认启用 Mock 数据，便于在后端智能助手登录用户接口全部就绪前开发页面和流程。

真实联调前必须确认 `docs/api-contract.md` 的全部接口可用。智能助手四个新增登录用户接口未完成时，应用只允许使用 MockFixtures 开发页面，不得把小艺服务密钥写入客户端。

## 项目参数

- Project name: JiqingZhiyin
- Bundle name: com.jiqing.zhiyin
- Language: ArkTS
- Device type: Phone
- Compile SDK: API 26
- Compatible SDK: API 12
- Model: Stage

## 构建与测试

在 DevEco Studio 中导入 `harmony-app/` 后同步工程，再运行：

```bash
./hvigorw clean --no-daemon
./hvigorw test -p product=default -p module=entry@default --no-daemon
./hvigorw assembleHap --mode project -p product=default --no-daemon
```

当前工作区缺少 DevEco 生成的 hvigor wrapper 与 SDK 环境，命令需要在完整 HarmonyOS 工程环境中执行。

没有 DevEco 环境时，可以先运行本地自检：

```bash
node tools/validate-local.mjs
```

当前可构建副本位于英文路径：

```text
D:\JiqingZhiyin\harmony-app
```

可用脚本：

```powershell
powershell -ExecutionPolicy Bypass -File tools\build-dev.ps1
powershell -ExecutionPolicy Bypass -File tools\install-run-dev.ps1
```

注意：DevEco 运行配置应选择 `entry` 或安装完整 `.app` 包。只安装 `growthform` 会导致只能看到桌面卡片模块，无法打开手机主应用。

## 联调说明

默认配置位于 `entry/src/main/ets/core/config/Environment.ets`：

- `MOCK_MODE=true`：使用本地确定性数据。
- `API_BASE_URL=https://api.jiqing.invalid/api`：占位地址，不能用于真实构建。

真实环境请使用本地忽略配置或产品构建配置覆盖，不要提交临时隧道地址、Token、密码或服务密钥。

## 当前本地能力

- 登录、注册、画像保存使用本地 mock 仓储。
- 首页展示 dashboard、今日任务和进度。
- 规划页支持 7 天、1 个月、3 个月切换和本地完成任务。
- 资源页支持五类资源切换、关键词过滤和资源卡片。
- 智能助手提供画像分析、职业计划、政策搜索、资源匹配和今日建议入口。
- 我的页展示用户、目标、成长记录和提醒设置入口。
- 桌面成长卡片只展示任务、进度、截止时间和安全路由，不包含 Token、密码、咨询问题等隐私内容。

## 浏览器模拟环境

没有 DevEco Studio 或 HarmonyOS SDK 时，可以先打开 `simulator/index.html` 验证产品流程。模拟环境包含手机外观、五个底部入口、任务完成、资源收藏/行动、助手反馈、离线切换和数据重置。

如果浏览器限制本地脚本，可以双击 `simulator/start-simulator.bat`，再访问 `http://127.0.0.1:8787/`。

## 发布前检查

- 关闭 `Environment.MOCK_MODE`。
- 配置稳定 HTTPS API，不提交临时隧道地址。
- 用真实测试账号验证注册、登录、画像、资源行动、助手和成长记录。
- 真机验证通知、离线缓存和桌面卡片。
- 运行敏感信息扫描，覆盖服务密钥、绑定令牌、临时隧道地址、明文 Token 和明文密码模式。

# 冀青智引——青年成长发展 AI Agent

面向河北县域发展意愿青年的成长与就业服务产品。项目由原微信小程序“冀青赋能”升级而来，基于近 3000 份河北县域青年调研和已有用户画像逻辑，形成“画像—规划—政策—资源—行动—记录—建议”闭环。

## 架构

- 小艺 Agent：自然语言交互、意图识别、追问和 Skills 编排。
- Django Agent API：账号绑定、可信数据、权限、规划规则、动作确认和审计。
- 微信小程序：青年档案、资源服务、成长记录、连接小艺和今日建议。
- SQLite：本地开发与比赛演示；生产部署可迁移到 PostgreSQL。

## Agent 能力

1. 青年画像：读取地区、学历、专业、意向、能力和成长行为，确认后更新。
2. 职业规划：生成 7 天、1 个月、3 个月结构化成长路径。
3. 政策理解：只检索已发布、未过期政策，返回材料、流程、来源和不确定条件。
4. 资源匹配：推荐岗位、课程、活动和导师，提供可解释评分。
5. 成长行动：报名、申请、收藏和完成任务必须经过显式确认。
6. 今日建议：结合到期任务、画像和新资源提供主动成长建议。

## 快速启动

```bash
cd demo1/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
JIQING_DEMO_PASSWORD='替换演示密码' .venv/bin/python manage.py seed_demo_data
JIQING_AGENT_SERVICE_KEY='替换为至少32位随机密钥' .venv/bin/python manage.py runserver
```

微信开发者工具导入 `demo1/`。本地调试默认请求 `http://127.0.0.1:8000/api`，生产环境需改为已备案的 HTTPS 合法域名。

## 小艺配置

- 配置说明：[xiaoyi-agent/README.md](xiaoyi-agent/README.md)
- OpenAPI Skills：[xiaoyi-agent/openapi.yaml](xiaoyi-agent/openapi.yaml)
- 系统提示词：[xiaoyi-agent/system-prompt.md](xiaoyi-agent/system-prompt.md)
- 联调用例：[xiaoyi-agent/test-cases.md](xiaoyi-agent/test-cases.md)

实际发布前必须在小艺开放平台测试态完成绑定、画像、政策、推荐、确认行动和建议联调。

## 验证

```bash
cd demo1/backend
.venv/bin/python manage.py makemigrations --check
.venv/bin/python manage.py test -v 2
cd ..
node --test tests/*.test.js
```

接口说明见 [docs/agent-api.md](docs/agent-api.md)，比赛演示见 [docs/demo-script-5min.md](docs/demo-script-5min.md)。

## 安全说明

- 生产环境必须设置独立的 Django Secret Key 和 Agent 服务密钥。
- Agent 服务密钥只存在于服务端和小艺平台安全配置中，不能放入小程序。
- 演示账号默认密码仅用于本地；共享或部署环境必须通过 `JIQING_DEMO_PASSWORD` 覆盖。
- 调研数据只用于脱敏聚合洞察和规则验证，不把原始个人数据送入模型上下文。

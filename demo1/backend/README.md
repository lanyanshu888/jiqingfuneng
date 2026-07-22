# 冀青赋能 Django 后端

这是“冀青赋能 / 冀青智引”的 Django API 后端，提供账号、青年画像、资源目录、报名、课程进度、导师咨询、收藏、成长记录和画像推荐能力。

## 启动

```bash
cd demo1/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo_data
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

小程序端默认请求地址为 `http://127.0.0.1:8000/api`，配置在 `app.js` 的 `globalData.apiBaseUrl`。

Windows 下将 `.venv/bin/python` 替换为 `.venv\Scripts\python.exe`。

## 主要接口

- `POST /api/auth/register/` 注册并返回 token
- `POST /api/auth/login/` 登录并返回 token
- `GET /api/auth/me/` 获取当前用户和画像
- `GET /api/profiles/me/` 获取我的画像
- `POST /api/profiles/me/` 保存我的画像
- `GET /api/policies/`、`opportunities/`、`courses/`、`activities/`、`mentors/` 获取已发布资源
- `POST /api/activities/<id>/enroll/` 报名活动
- `POST /api/opportunities/<id>/enroll/` 申请岗位
- `POST /api/courses/<id>/complete/` 完成课程
- `POST /api/mentors/<id>/consult/` 提交导师咨询
- `POST /api/favorites/toggle/` 收藏/取消收藏
- `GET /api/me/growth/` 获取成长记录
- `GET /api/recommendations/` 获取画像规则推荐

请求登录态接口时加请求头：

```text
Authorization: Token <token>
```

## 部署配置

生产环境至少配置以下环境变量：

```bash
export JIQING_SECRET_KEY="替换为足够长的随机字符串"
export JIQING_DEBUG="false"
export JIQING_ALLOWED_HOSTS="api.example.com"
export JIQING_AGENT_SERVICE_KEY="替换为不少于32个随机字符的服务密钥"
export JIQING_AGENT_CONFIRMATION_MAX_AGE_SECONDS="300"
```

生产环境必须使用 HTTPS。部署后将小程序 `app.js` 中的 `apiBaseUrl` 改为服务器的 HTTPS 地址，并在微信公众平台配置合法 request 域名。

`JIQING_AGENT_SERVICE_KEY` 只允许配置在 Django 服务和小艺 Skills 的服务端认证中，不得写入小程序代码或提交真实生产密钥。

## Docker 部署

容器镜像适用于支持 Docker 的云主机或容器平台。HTTPS 由平台网关或可信反向代理终止，容器内部监听 HTTP。

```bash
cd demo1/backend
docker build -t jiqing-agent:latest .
docker volume create jiqing-agent-data
docker run --rm -p 8000:8000 \
  -v jiqing-agent-data:/data \
  -e JIQING_DEBUG=false \
  -e JIQING_SECRET_KEY='<至少50位随机值>' \
  -e JIQING_AGENT_SERVICE_KEY='<至少32位随机值>' \
  -e JIQING_ALLOWED_HOSTS='agent.example.com' \
  jiqing-agent:latest
curl --fail http://127.0.0.1:8000/api/health/
```

首次需要演示数据时，额外设置 `JIQING_SEED_DEMO=true` 与强随机 `JIQING_DEMO_PASSWORD`；后续启动应移除 `JIQING_SEED_DEMO`。入口脚本每次启动都会执行数据库迁移，但默认不会创建演示账号。

云平台必须把持久磁盘挂载到 `/data`，通过 Secret 管理功能注入密钥，并将实际域名写入 `JIQING_ALLOWED_HOSTS`。如不使用默认数据目录，可通过 `JIQING_SQLITE_PATH` 指定单实例 SQLite 文件；多实例或正式用户环境应迁移 PostgreSQL。

部署完成后访问 `https://<实际域名>/api/health/`。确认返回 200 后，再配置小程序合法域名和小艺测试态。不要把生产密钥写入 Dockerfile、镜像、仓库或 OpenAPI 文件。

## 验证

```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py test -v 1
.venv/bin/python -m unittest tests.test_entrypoint -v
cd ..
node --test tests/*.test.js
```

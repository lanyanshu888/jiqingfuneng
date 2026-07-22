# 冀青赋能 Django 后端

这是小程序的轻量 API 后端，提供用户注册、登录、登录态校验和青年成长画像保存。

## 启动

```powershell
cd E:\codex\demo1\backend
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

小程序端默认请求地址为 `http://127.0.0.1:8000/api`，配置在 `app.js` 的 `globalData.apiBaseUrl`。

## 接口

- `POST /api/auth/register/` 注册并返回 token
- `POST /api/auth/login/` 登录并返回 token
- `GET /api/auth/me/` 获取当前用户和画像
- `GET /api/profiles/me/` 获取我的画像
- `POST /api/profiles/me/` 保存我的画像

请求登录态接口时加请求头：

```text
Authorization: Token <token>
```

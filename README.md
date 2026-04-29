# 乐队管理系统 / MyGO Band Manager

一个基于 Vue 3 + FastAPI + SQLAlchemy + MySQL 的乐队管理系统，包含用户注册登录、乐队职务、练习记录、公共演出活动、岗位匹配报名、个人日程、练习统计和 AI 问答预留接口。

## 项目结构

```text
backend/
  app/
    api/routes/      # auth/users/practices/events/schedule/dashboard/ai
    core/            # 配置与安全
    db/              # SQLAlchemy 会话与初始化
    models/          # 数据模型
    schemas/         # Pydantic schema
    services/        # 活动匹配与 AI 客户端
frontend/
  src/
    components/      # Shell、卡片、空状态等
    views/           # 登录、看板、练习、活动、日程、AI、资料
    stores/          # Pinia auth store
    router/          # Vue Router
```

## 默认管理员

后端启动时会自动创建管理员账号：

- 邮箱：`admin@mygoband.com`
- 密码：`MyGO-Admin-9F3vP8!`

生产环境请在 `backend/.env` 中修改 `ADMIN_EMAIL`、`ADMIN_USERNAME`、`ADMIN_PASSWORD` 和 `SECRET_KEY`。

## 启动 MySQL

```bash
docker compose up -d mysql
```

如果你使用 `docker-compose.yml` 中的数据库用户，可将后端的 `DATABASE_URL` 改成：

```env
DATABASE_URL="mysql+pymysql://mygo:mygo_password@127.0.0.1:3306/mygo_band?charset=utf8mb4"
```

## 启动后端

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

接口文档：

- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## 启动前端

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

前端默认地址：`http://localhost:5173`

## AI 问答配置位

默认不会请求外部 AI 服务。准备接入 OpenAI-compatible 接口时，在 `backend/.env` 填入：

```env
AI_BASE_URL="https://your-provider.example/v1"
AI_MODEL="your-model-name"
AI_API_KEY="your-api-key"
ENABLE_AI_PROXY=true
```

前端会调用 `POST /api/v1/ai/chat`，后端会请求 `${AI_BASE_URL}/chat/completions`。

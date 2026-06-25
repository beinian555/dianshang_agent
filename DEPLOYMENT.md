# 部署指南

## 环境要求

- Python 3.11+
- Node.js 18+ (前端)
- PostgreSQL 16 (持久化模式)

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `STORE_BACKEND` | 存储后端: `memory` / `postgres` | `memory` |
| `DATABASE_URL` | PostgreSQL 连接串 | 空 (需要 postgres 后端时设置) |
| `LLM_PROVIDER` | LLM 提供方: `mock` / `real` | `mock` |
| `LLM_API_KEY` | LLM API Key | 空 |
| `LLM_MODEL` | LLM 模型名 | 空 |

### PostgreSQL 连接串格式

```
postgresql+asyncpg://用户名:密码@主机:端口/数据库名
```

示例: `postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang`

## 部署步骤

### 一键启动 (Docker Compose)

```bash
docker compose up -d
```

这行命令会自动：
1. 拉取 PostgreSQL 16 镜像并启动
2. 构建后端镜像
3. 等待数据库就绪
4. 自动运行 `alembic upgrade head` 数据库迁移
5. 启动 FastAPI 后端 (端口 8000)

停止：`docker compose down`  
保留数据：`docker compose down`（数据卷 `pgdata` 不会被删除）  
清空数据重新来：`docker compose down -v`

### 手动部署

### 1. 克隆代码

```bash
git clone <repo-url> && cd <repo>
```

### 2. 安装后端依赖

```bash
cd backend
pip install -e ".[dev]"
```

### 3. 数据库设置 (PostgreSQL 模式)

```bash
# 创建数据库
createdb dianshang

# 运行迁移
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
alembic upgrade head
```

### 4. 启动后端

```bash
# 内存模式 (不需要 PostgreSQL)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# PostgreSQL 模式
set STORE_BACKEND=postgres
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. 构建部署前端

```bash
cd frontend
npm install
npm run build
# 静态文件在 out/ 目录，可部署到任意静态服务器
# 开发模式: npm run dev
```

### 6. 验证

```bash
curl http://localhost:8000/api/health
# → {"status": "ok"}

curl -X POST http://localhost:8000/api/seed/beauty
# → {"product_id": "...", "competitor_count": 3, "review_count": 8}
```

## Docker 部署

### PostgreSQL

```bash
docker run -d --name dianshang-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=dianshang \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16
```

### 后端

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ .
RUN pip install -e "."
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 生产环境注意事项

1. 设置 `STORE_BACKEND=postgres` 并用强密码
2. 不要使用 MockLLMProvider — 设置 `LLM_PROVIDER=real` 和有效的 API Key
3. 配置反向代理 (Nginx/Caddy) 处理静态文件
4. 设置日志级别为 INFO (非 debug)
5. 定期备份 PostgreSQL 数据库

## 数据库迁移

```bash
# 生成新迁移 (需要运行中的 PostgreSQL)
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1

# 查看迁移 SQL (不需要数据库连接)
alembic upgrade head --sql
```

# 演示指南

## 启动服务

### 内存模式 (快速体验)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### PostgreSQL 持久化模式

```bash
# 1. 启动 PostgreSQL
docker run -d --name dianshang-pg \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=dianshang \
  -p 5432:5432 postgres:16

# 2. 运行迁移
cd backend
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
alembic upgrade head

# 3. 启动后端
set STORE_BACKEND=postgres
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
uvicorn app.main:app --reload --port 8000

# 4. 验证持久化：重启后端，数据不丢失
```

## Web UI 演示流程

1. 浏览器打开 `http://localhost:3000`
2. 点击「新建项目」, 输入项目名称 (如 "美妆精华增长分析")
3. 在项目详情页依次导入 4 个 CSV 文件:
   - 商品数据 (product.csv)
   - 竞品数据 (competitors.csv)
   - 评论数据 (reviews.csv)
   - 运营数据 (metrics.csv)
4. 点击「运行增长分析」
5. 观察进度条实时更新 (15 步分析流程)
6. 完成后报告出现在下方，点击查看完整报告

## API 演示流程

### 1. 内存模式 - Seed 数据

```bash
# 注入美妆测试数据
curl -X POST http://localhost:8000/api/seed/beauty

# 运行分析 (同步返回)
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "product_url": "https://mock.shop/product/beauty-serum-main",
    "competitor_urls": [
      "https://mock.shop/product/competitor-a",
      "https://mock.shop/product/competitor-b",
      "https://mock.shop/product/competitor-c"
    ],
    "category": "beauty_skincare",
    "platform": "mock_tmall",
    "use_seed_data": true
  }'

# 查看报告
curl http://localhost:8000/api/reports/{report_id}
curl http://localhost:8000/api/reports/{report_id}/markdown
```

### 2. CSV 导入 + 异步分析

```bash
# 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "美妆精华分析", "category": "beauty_skincare", "platform": "mock_tmall"}'

# 导入数据
curl -X POST http://localhost:8000/api/projects/{id}/import/product \
  -F "file=@sample_data/beauty_serum/product.csv"
curl -X POST http://localhost:8000/api/projects/{id}/import/competitors \
  -F "file=@sample_data/beauty_serum/competitors.csv"
curl -X POST http://localhost:8000/api/projects/{id}/import/reviews \
  -F "file=@sample_data/beauty_serum/reviews.csv"
curl -X POST http://localhost:8000/api/projects/{id}/import/metrics \
  -F "file=@sample_data/beauty_serum/metrics.csv"

# 启动分析 (返回 202 + job)
curl -X POST http://localhost:8000/api/projects/{id}/analysis
# → {"id": "job-xxx", "status": "pending", "progress": 0, ...}

# 轮询 job 状态
curl http://localhost:8000/api/analysis-jobs/{job_id}
# → {"id": "job-xxx", "status": "running", "progress": 45, "current_step": "标题优化", ...}

# 完成后查看报告
curl http://localhost:8000/api/reports/{report_id}
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
# 打开 http://localhost:3000
```

## 测试

```bash
cd backend
pytest tests/ -v

# 使用 PostgreSQL 后端运行测试 (需要 PostgreSQL)
set STORE_BACKEND=postgres
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
pytest tests/test_postgres_store.py tests/test_job.py -v
```

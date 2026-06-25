# 电商商品增长分析 Agent

面向电商单品运营的商品增长分析 Agent，自动生成结构化增长分析报告。

## 快速开始

```bash
# 安装依赖
cd backend && pip install -e ".[dev]"

# 启动后端 (内存模式，无需数据库)
cd backend && uvicorn app.main:app --reload

# 启动前端 (可选)
cd frontend && npm install && npm run dev
```

### 使用 PostgreSQL (持久化)

```bash
# 设置环境变量
# Linux/macOS:
export STORE_BACKEND=postgres
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang
# Windows:
set STORE_BACKEND=postgres
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang

# 运行数据库迁移
cd backend && alembic upgrade head

# 启动
uvicorn app.main:app --reload
```

详见 [DEPLOYMENT.md](DEPLOYMENT.md) 和 [DEMO_GUIDE.md](DEMO_GUIDE.md)。

## 方式一：Seed 数据 Demo（快速体验）

一键注入美妆测试数据并分析：

```bash
# 1. 注入测试数据
curl -X POST http://localhost:8000/api/seed/beauty

# 2. 创建分析任务
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

# 3. 获取报告（替换为返回的 report_id）
curl http://localhost:8000/api/reports/{report_id}

# 4. 导出 Markdown
curl http://localhost:8000/api/reports/{report_id}/markdown
```

## 方式二：CSV 数据导入 Demo（真实数据流程）

通过 Project + CSV 导入完成完整分析，不依赖 seed 数据：

### 1. 创建项目

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "美妆精华增长分析", "category": "beauty_skincare", "platform": "mock_tmall"}'
# 返回: {"id": "project-xxx", "name": "...", ...}
```

### 2. 导入商品数据

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/import/product \
  -F "file=@sample_data/beauty_serum/product.csv"
```

### 3. 导入竞品数据

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/import/competitors \
  -F "file=@sample_data/beauty_serum/competitors.csv"
```

### 4. 导入评论数据

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/import/reviews \
  -F "file=@sample_data/beauty_serum/reviews.csv"
```

### 5. 导入周报指标

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/import/metrics \
  -F "file=@sample_data/beauty_serum/metrics.csv"
```

### 6. 运行分析 (异步)

```bash
curl -X POST http://localhost:8000/api/projects/{project_id}/analysis
# 返回 202: {"id": "job-xxx", "status": "pending", "progress": 0, ...}

# 轮询分析进度
curl http://localhost:8000/api/analysis-jobs/{job_id}
# 返回: {"id": "job-xxx", "status": "completed", "progress": 100, "report_id": "report-xxx", ...}
```

### 7. 查看报告

```bash
curl http://localhost:8000/api/reports/{report_id}
curl http://localhost:8000/api/reports/{report_id}/markdown
```

## CSV 文件格式说明

示例文件在 `sample_data/beauty_serum/` 目录下：

- `product.csv` — 商品信息（标题、价格、卖点、成分、适用人群等）
- `competitors.csv` — 竞品信息（支持多个竞品，每行一个）
- `reviews.csv` — 差评数据（评分、内容、标签）
- `metrics.csv` — 周报指标（支持 last_week/this_week 两个周期）

多值字段（如卖点、成分、标签等）使用 `|` 分隔。

## 评分体系

报告包含 7 个评分维度，每项附有评分原因(reason)和依据(evidence)：

| 维度 | 说明 | 权重 |
|------|------|------|
| 标题搜索力 | 标题覆盖搜索关键词的能力 | 15% |
| 主图点击力 | 主图文案吸引用户点击的能力 | 20% |
| 详情转化力 | 详情页内容促进下单的能力 | 20% |
| 竞品差异力 | 与竞品的差异化程度 | 15% |
| 差评风险度 | 评价风险高低（越高越危险） | — |
| 评价健康度 | 评价生态整体健康度 | 15% |
| 投流承接力 | 投放素材到落地页的信息一致性 | 15% |

> 综合得分使用评价健康度加权计算，差评风险度作为独立风险信号展示。

## 报告内容

- 核心结论
- SKU 增长评分（含评分依据 evidence）
- 自家商品当前问题
- 竞品卖点拆解
- 标题优化建议（3类）
- 主图文案建议（5张图）
- 详情页结构建议（9屏）
- 差评聚类分析
- 客服 FAQ
- 投流素材建议（4个方向）
- 本周数据复盘
- 下周优化任务

## 技术栈

- Python 3.11+ / FastAPI / Pydantic v2
- 存储后端: 内存 (默认) / PostgreSQL (持久化)，通过 `STORE_BACKEND` 环境变量切换
- SQLAlchemy 2.0 async + asyncpg + Alembic 迁移
- 异步分析: 后台 job 模式，前端轮询进度条
- LLM 调用日志: `LoggingLLMProvider` 透明拦截，记录到 `llm_call_logs` 表
- MockLLMProvider（后续可替换为真实 LLM）
- Next.js 16 / React 19 / TypeScript 前端

## 测试

```bash
cd backend && pytest tests/ -v
```

## 项目结构

```
backend/
  app/
    main.py              # FastAPI 入口
    core/                 # 配置、数据库连接
    models/               # SQLAlchemy ORM 模型
    schemas/              # Pydantic v2 数据模型
    agents/               # Agent 模块 + LLM 日志
    services/             # 评分、报告服务
    repositories/         # StoreBase → MemoryStore / PostgresStore
    seed/                 # 美妆 seed 数据
    api/routes/           # API 路由 (projects, analysis, reports, jobs, seed)
    utils/                # CSV 解析等工具
  alembic/                # 数据库迁移
  tests/                  # pytest 测试 (80+)
sample_data/              # CSV 模板数据 (3 个数据集)
frontend/                 # Next.js 前端
```

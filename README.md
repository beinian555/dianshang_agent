# 电商商品增长分析 Agent

> 输入商品链接与竞品链接，自动生成结构化增长分析报告，让单品运营从「拍脑袋优化」走向「数据驱动决策」。

## 为什么做这个产品

电商单品运营的日常，是在海量信息中做无数个决策：标题怎么写才能被搜到？主图文案怎么提炼卖点？详情页第几屏放什么？竞品比我们强在哪里？差评集中在什么问题？投流素材和落地页是否一致？

这些决策过去高度依赖运营人员的个人经验，存在三个痛点：

1. **分析维度割裂** —— 标题、主图、详情页、竞品、评论、投流各自为战，缺乏一个把所有维度串起来的「全局视图」。
2. **优化方向难量化** —— 「这个标题好不好」「这条差评风险大不大」缺少客观的评估标准，优化优先级全凭感觉。
3. **经验难以沉淀** —— 资深运营的方法论存在脑子里，新人上手慢，团队缺少可复用的分析框架。

这个产品试图解决的核心问题是：**把资深单品运营的分析思维，沉淀为一套可执行、可量化、可复现的 Agent 流水线。**

## 核心价值

- **一份报告，覆盖增长全链路**：从标题搜索力到投流承接力，7 个维度一次性评估，不再东拼西凑。
- **每个评分都有依据**：不是空洞地打分，而是附带评分原因（reason）和事实依据（evidence），让结论可追溯、可讨论。
- **从分析到行动**：不止告诉你「哪里有问题」，还给出标题优化建议、主图文案、详情页结构、投流素材方向、下周任务清单——分析结果直接可执行。
- **结构化输出，而非自然语言堆砌**：所有 Agent 产出均为结构化数据，报告 Markdown 只在最后一层生成，便于下游对接 BI、看板或自动化流程。

## 目标用户与场景

| 角色 | 典型场景 |
|------|----------|
| 单品运营 | 新品上架前做一次全面诊断，找出优化优先级 |
| 品类运营 | 批量分析竞品，提炼品类共性与差异化机会 |
| 投放优化师 | 对齐投流素材与落地页信息，减少「接不住流量」的浪费 |
| 运营新人 | 参照报告结构学习「资深运营是怎么拆解一个单品的」 |

## 产品能力概览

### 7 维增长评分

每项评分附带评分原因与事实依据，综合得分由评价健康度加权：

| 维度 | 解决什么问题 | 权重 |
|------|-------------|------|
| 标题搜索力 | 标题是否覆盖了用户会搜索的关键词 | 15% |
| 主图点击力 | 主图文案能否在信息流中吸引点击 | 20% |
| 详情转化力 | 详情页内容能否打消顾虑、促成下单 | 20% |
| 竞品差异力 | 与竞品相比有没有说清自己的差异化 | 15% |
| 差评风险度 | 差评里有没有高爆炸力的集中问题（越高越危险） | 独立风险信号 |
| 评价健康度 | 评价生态整体是否健康 | 15% |
| 投流承接力 | 投流素材承诺的东西，落地页有没有接住 | 15% |

### 报告产出

一份完整报告包含以下结构化模块：

- 核心结论（一句话讲清增长卡点在哪）
- SKU 增长评分（7 维 + 评分依据）
- 自家商品当前问题清单
- 竞品卖点拆解
- 标题优化建议（搜索型 / 转化型 / 品牌型 三类方向）
- 主图文案建议（5 张图，每张一个核心卖点）
- 详情页结构建议（9 屏，从首屏到尾屏完整规划）
- 差评聚类分析（把零散差评归类为可处理的议题）
- 客服 FAQ（基于差评聚类预判用户高频疑问）
- 投流素材建议（4 个方向，对齐落地页信息一致性）
- 本周数据复盘 + 下周优化任务清单

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+（前端可选）

### 安装与启动

```bash
# 后端依赖
cd backend && pip install -e ".[dev]"

# 启动后端（默认内存模式，无需数据库）
uvicorn app.main:app --reload

# 启动前端（可选）
cd frontend && npm install && npm run dev
```

### 方式一：Seed 数据 Demo（30 秒体验）

```bash
# 1. 一键注入美妆测试数据
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

# 3. 获取报告
curl http://localhost:8000/api/reports/{report_id}
curl http://localhost:8000/api/reports/{report_id}/markdown
```

### 方式二：CSV 导入 Demo（真实数据流程）

通过创建项目 + 导入四类 CSV，走完整的分析流水线：

```bash
# 1. 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "美妆精华增长分析", "category": "beauty_skincare", "platform": "mock_tmall"}'

# 2. 依次导入商品 / 竞品 / 评论 / 周报指标 CSV
curl -X POST http://localhost:8000/api/projects/{project_id}/import/product    -F "file=@sample_data/beauty_serum/product.csv"
curl -X POST http://localhost:8000/api/projects/{project_id}/import/competitors -F "file=@sample_data/beauty_serum/competitors.csv"
curl -X POST http://localhost:8000/api/projects/{project_id}/import/reviews    -F "file=@sample_data/beauty_serum/reviews.csv"
curl -X POST http://localhost:8000/api/projects/{project_id}/import/metrics     -F "file=@sample_data/beauty_serum/metrics.csv"

# 3. 运行分析（异步，返回 job_id 用于轮询进度）
curl -X POST http://localhost:8000/api/projects/{project_id}/analysis

# 4. 查看报告
curl http://localhost:8000/api/reports/{report_id}/markdown
```

CSV 模板在 `sample_data/` 下提供 3 个数据集（beauty_serum / foundation / sunscreen），多值字段用 `|` 分隔。

### 使用 PostgreSQL 持久化

```bash
# Linux/macOS
export STORE_BACKEND=postgres
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang

# Windows
set STORE_BACKEND=postgres
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dianshang

# 运行数据库迁移后启动
cd backend && alembic upgrade head
uvicorn app.main:app --reload
```

也可使用 Docker Compose 一键启动，详见 [DEPLOYMENT.md](DEPLOYMENT.md)。

### 运行测试

```bash
cd backend && pytest tests/ -v
```

## 架构

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| 后端框架 | Python 3.11+ / FastAPI / Pydantic v2 |
| 数据层 | SQLAlchemy 2.0 async + asyncpg + Alembic（内存模式 / PostgreSQL 可切换） |
| Agent 层 | 模块化 Agent + Orchestrator 编排，MockLLMProvider（可替换真实 LLM） |
| 可观测性 | LoggingLLMProvider 透明拦截，LLM 调用全量记录到 `llm_call_logs` 表 |
| 前端 | Next.js 16 / React 19 / TypeScript |
| 异步任务 | 后台 job 模式 + 前端轮询进度条 |

### 系统架构

```mermaid
graph TB
    subgraph 数据输入
        A[商品链接 + 竞品链接] --> B[Orchestrator 编排器]
        CSV[CSV 导入] --> B
        SEED[Seed 测试数据] --> B
    end

    subgraph Agent 流水线
        B --> C1[商品解析 Agent]
        B --> C2[竞品分析 Agent]
        B --> C3[评论聚类 Agent]
        B --> C4[标题优化 Agent]
        B --> C5[主图文案 Agent]
        B --> C6[详情页 Agent]
        B --> C7[广告素材 Agent]
        B --> C8[FAQ Agent]
        B --> C9[周报 Agent]
    end

    subgraph 服务层
        C1 --> D1[GrowthScoringService<br/>7维评分]
        C2 --> D1
        C3 --> D1
        C4 --> D2[ReportService<br/>报告生成]
        C5 --> D2
        C6 --> D2
        C7 --> D2
        C8 --> D2
        C9 --> D2
        D1 --> D2
    end

    D2 --> E[结构化报告 JSON]
    D2 --> F[Markdown 报告]
```

### 项目结构

```
backend/
  app/
    main.py                # FastAPI 入口
    core/                  # 配置、数据库连接、日志
    models/                # SQLAlchemy ORM 模型
    schemas/               # Pydantic v2 数据模型
    agents/                # Agent 模块 + Orchestrator + LLM Provider
    services/              # 评分服务、报告服务
    repositories/          # 存储抽象 (MemoryStore / PostgresStore)
    prompts/               # Agent 提示词模板
    seed/                  # 美妆测试数据
    api/routes/            # API 路由 (projects, analysis, reports, jobs, seed)
    utils/                 # CSV 解析等工具
  alembic/                # 数据库迁移
  tests/                  # pytest 测试 (80+ 用例)
sample_data/              # CSV 模板数据 (3 个数据集)
frontend/                 # Next.js 前端
```

### Agent 流水线设计

系统采用 **Orchestrator 编排 + 独立 Agent** 的架构。每个 Agent 职责单一，输入输出均为结构化数据，互不耦合：

- 所有 Agent 继承自 `BaseAgent`，统一接口约定
- `Orchestrator` 负责按序编排各 Agent，串联分析流水线
- LLM 调用通过 `LoggingLLMProvider` 透明拦截，全量记录请求 / 响应 / 耗时，便于调试与成本分析
- 当前使用 `MockLLMProvider`，后续可无缝替换为真实 LLM，不影响上层逻辑

### 存储抽象

通过 `STORE_BACKEND` 环境变量切换存储后端，业务代码无感知：

- `memory`（默认）：内存存储，零配置快速启动，适合开发与 Demo
- `postgres`：PostgreSQL 持久化，适合生产环境，通过 Alembic 管理迁移

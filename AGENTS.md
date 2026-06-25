# AGENTS.md

## 项目概述

电商单品运营「商品增长分析 Agent」- 输入商品链接和竞品链接，自动生成结构化增长分析报告。

## 技术栈

- Python 3.11+ / FastAPI / Pydantic v2
- MVP 使用内存存储，后续迁移 PostgreSQL
- LLM Provider 使用 MockLLMProvider（后续可替换为真实 LLM）

## 项目结构

```
backend/
  app/
    main.py              # FastAPI 入口
    core/                 # 配置、数据库、日志
    models/               # SQLAlchemy models (后续)
    schemas/              # Pydantic v2 schemas
    repositories/         # 数据访问层 (后续)
    services/             # 业务服务 (GrowthScoringService, ReportService)
    agents/               # Agent 模块 (BaseAgent, 各分析 Agent, Orchestrator)
    seed/                 # 美妆测试数据
    api/routes/           # API 路由
    utils/                # 工具函数
  tests/                  # pytest 测试
```

## 开发约束

- 第一阶段不做真实平台爬虫
- 不做真实店铺授权 API
- 使用美妆行业测试数据模拟
- 所有 Agent 输出必须是结构化数据
- 报告 Markdown 只在 ReportService 最后生成
- 不要在 API route 里写业务流程
- 美妆类文案避免绝对化、医疗化、夸大功效表达

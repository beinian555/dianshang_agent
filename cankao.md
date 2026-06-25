# 电商商品增长分析 Agent 开发文档

## 0. 项目目标

开发一个面向电商单品运营的「商品增长分析 Agent」。

本项目第一版不追求全平台自动化，也不做真实店铺授权 API。MVP 目标是：

1. 输入自家商品链接、竞品链接、店铺类目。
2. 使用美妆行业测试数据模拟商品页、竞品页、评论、差评、后台数据。
3. 自动生成一份结构化增长分析报告。
4. 报告包含：

   * 竞品卖点拆解
   * 标题优化
   * 主图文案
   * 详情页结构
   * 差评聚类
   * 客服 FAQ
   * 投流素材建议
   * 周报摘要
5. 后端接口、数据结构、Agent 编排、报告生成流程必须可扩展。

项目偏开发实现，不做产品包装，不做真实商业介绍。

---

## 1. 技术栈

### 1.1 后端

使用：

* Python 3.11+
* FastAPI
* Pydantic v2
* SQLAlchemy 2.x
* PostgreSQL
* Alembic
* Uvicorn
* pytest
* httpx
* python-dotenv

### 1.2 前端

MVP 前端可以简单实现：

* Next.js
* React
* Tailwind CSS
* shadcn/ui 可选

第一阶段前端不是重点，可以先用 FastAPI Swagger 调接口。

### 1.3 Agent / LLM 层

第一阶段先做可替换的 LLM Provider。

需要支持：

* MockLLMProvider：本地固定输出，方便测试。
* RealLLMProvider：后续接入真实大模型。

不要把业务逻辑写死在 prompt 里，要拆成：

* 数据解析
* 指标计算
* 聚类
* 报告生成
* 文案生成

LLM 只负责语义理解和生成，不负责所有业务判断。

---

## 2. MVP 范围

### 2.1 第一版必须完成

第一版完成以下模块：

1. 商品任务创建
2. 美妆测试数据注入
3. 商品信息结构化
4. 竞品卖点分析
5. 差评聚类
6. 标题优化
7. 主图文案生成
8. 详情页结构生成
9. 客服 FAQ 生成
10. 投流素材建议
11. 周报生成
12. Markdown 报告导出

### 2.2 第一版暂不做

暂不做：

1. 真实平台爬虫
2. 淘宝/抖音/小红书/Amazon API
3. 自动改商品后台
4. 自动投放广告
5. 自动生成图片
6. 自动客服机器人
7. 多租户权限系统
8. 支付系统
9. 复杂看板

---

## 3. 项目目录结构

建议目录：

```text
ecommerce-growth-agent/
  README.md
  CLAUDE.md
  DEV_SPEC.md
  .env.example
  docker-compose.yml
  pyproject.toml

  backend/
    app/
      main.py
      core/
        config.py
        database.py
        logging.py

      models/
        product.py
        competitor.py
        review.py
        analysis.py
        report.py

      schemas/
        product.py
        competitor.py
        review.py
        analysis.py
        report.py

      repositories/
        product_repo.py
        analysis_repo.py
        report_repo.py

      services/
        product_service.py
        competitor_service.py
        review_service.py
        report_service.py

      agents/
        base.py
        llm_provider.py
        mock_llm.py
        product_parser_agent.py
        competitor_analyzer_agent.py
        review_cluster_agent.py
        title_optimizer_agent.py
        image_copy_agent.py
        detail_page_agent.py
        faq_agent.py
        ad_material_agent.py
        weekly_report_agent.py
        orchestrator.py

      seed/
        beauty_products.py
        beauty_reviews.py
        beauty_competitors.py
        beauty_weekly_metrics.py

      api/
        routes/
          analysis.py
          reports.py
          seed.py
          health.py

      utils/
        text.py
        scoring.py
        clustering.py
        markdown.py

    tests/
      test_analysis_flow.py
      test_review_cluster.py
      test_scoring.py
      test_report_generation.py

  frontend/
    app/
      page.tsx
      analysis/
        page.tsx
      reports/
        [id]/
          page.tsx
```

第一阶段重点开发 `backend`。

---

## 4. 核心业务流程

完整流程如下：

```text
用户输入
  ↓
CreateAnalysisRequest
  ↓
读取或注入美妆测试数据
  ↓
ProductParserAgent 商品信息结构化
  ↓
CompetitorAnalyzerAgent 竞品卖点拆解
  ↓
ReviewClusterAgent 差评聚类
  ↓
GrowthScoringService 计算增长评分
  ↓
TitleOptimizerAgent 标题优化
  ↓
ImageCopyAgent 主图文案
  ↓
DetailPageAgent 详情页结构
  ↓
FAQAgent 客服 FAQ
  ↓
AdMaterialAgent 投流素材建议
  ↓
WeeklyReportAgent 周报
  ↓
ReportService 生成 Markdown 报告
  ↓
返回 AnalysisReport
```

---

## 5. 数据模型设计

### 5.1 Product

```python
class Product(BaseModel):
    id: str
    platform: str
    category: str
    url: str
    title: str
    brand: str | None
    price: float | None
    original_price: float | None
    sku_name: str | None
    specs: list[str]
    main_image_texts: list[str]
    detail_sections: list[str]
    selling_points: list[str]
    ingredients: list[str]
    target_users: list[str]
    usage_scenarios: list[str]
    created_at: datetime
```

美妆行业测试商品示例：

```json
{
  "platform": "mock_tmall",
  "category": "beauty_skincare",
  "url": "https://mock.shop/product/beauty-serum-main",
  "title": "植萃修护精华液 熬夜肌补水保湿敏感肌可用 30ml",
  "brand": "LumiSkin",
  "price": 129,
  "original_price": 169,
  "sku_name": "30ml 修护精华",
  "specs": ["30ml", "50ml", "套装"],
  "main_image_texts": [
    "熬夜肌修护精华",
    "补水保湿 提亮肤色",
    "敏感肌可用",
    "植萃成分 温和修护"
  ],
  "detail_sections": [
    "熬夜暗沉、干燥起皮、换季泛红",
    "烟酰胺、泛醇、积雪草提取物",
    "早晚洁面后使用，轻拍吸收",
    "适合干皮、混合皮、敏感肌"
  ],
  "selling_points": [
    "补水保湿",
    "舒缓修护",
    "改善暗沉",
    "敏感肌可用"
  ],
  "ingredients": ["烟酰胺", "泛醇", "积雪草提取物", "透明质酸钠"],
  "target_users": ["熬夜党", "干皮", "换季敏感肌", "初抗老用户"],
  "usage_scenarios": ["熬夜后", "妆前保湿", "换季修护", "日常护肤"]
}
```

---

### 5.2 CompetitorProduct

```python
class CompetitorProduct(BaseModel):
    id: str
    product_id: str
    url: str
    title: str
    brand: str | None
    price: float | None
    sales_hint: str | None
    rating: float | None
    review_count: int | None
    selling_points: list[str]
    main_image_texts: list[str]
    detail_sections: list[str]
    promotions: list[str]
    weakness_hints: list[str]
```

测试竞品建议准备 3 个：

#### 竞品 A：低价走量型

```json
{
  "title": "补水保湿精华液女烟酰胺提亮肤色面部护肤品学生党",
  "brand": "PureGlow",
  "price": 59,
  "sales_hint": "月销1万+",
  "rating": 4.7,
  "review_count": 8600,
  "selling_points": ["低价", "补水", "烟酰胺", "学生党"],
  "main_image_texts": ["平价补水精华", "学生党可入", "提亮保湿"],
  "promotions": ["第二件半价", "买一送一"],
  "weakness_hints": ["包装普通", "成分背书弱", "敏感肌顾虑明显"]
}
```

#### 竞品 B：成分党专业型

```json
{
  "title": "高浓度烟酰胺修护精华液 改善暗沉 提亮肤色 屏障修护",
  "brand": "DermaLab",
  "price": 189,
  "sales_hint": "月销3000+",
  "rating": 4.8,
  "review_count": 4200,
  "selling_points": ["高浓度烟酰胺", "成分专业", "屏障修护", "功效护肤"],
  "main_image_texts": ["5%烟酰胺", "屏障修护", "成分党优选"],
  "promotions": ["赠送小样", "会员专享价"],
  "weakness_hints": ["价格偏高", "刺激性顾虑", "新手理解成本高"]
}
```

#### 竞品 C：敏感肌温和型

```json
{
  "title": "敏感肌舒缓修护精华液 积雪草泛醇补水保湿换季维稳",
  "brand": "CalmCare",
  "price": 149,
  "sales_hint": "月销5000+",
  "rating": 4.9,
  "review_count": 6900,
  "selling_points": ["敏感肌", "舒缓泛红", "积雪草", "换季维稳"],
  "main_image_texts": ["换季维稳", "敏感肌安心用", "舒缓泛红"],
  "promotions": ["满减", "赠化妆棉"],
  "weakness_hints": ["提亮卖点弱", "见效慢", "油皮反馈一般"]
}
```

---

### 5.3 Review

```python
class Review(BaseModel):
    id: str
    product_id: str
    source: str
    rating: int
    content: str
    created_at: datetime
    tags: list[str]
```

测试差评数据：

```json
[
  {
    "rating": 2,
    "content": "用了三天没感觉有提亮，保湿还可以，但是没有详情页说得那么明显。",
    "tags": ["效果预期", "提亮"]
  },
  {
    "rating": 2,
    "content": "我是敏感肌，用完脸有点刺痛，不知道是不是烟酰胺不耐受。",
    "tags": ["敏感肌", "刺激"]
  },
  {
    "rating": 3,
    "content": "瓶子比想象中小，30ml 感觉很快就用完了。",
    "tags": ["规格认知", "性价比"]
  },
  {
    "rating": 2,
    "content": "物流盒子压坏了，虽然里面没漏，但体验不好。",
    "tags": ["物流包装"]
  },
  {
    "rating": 3,
    "content": "质地有点黏，早上用后上妆会搓泥。",
    "tags": ["使用体验", "妆前"]
  },
  {
    "rating": 2,
    "content": "客服说敏感肌可以用，但我用完泛红更明显。",
    "tags": ["客服承诺", "敏感肌"]
  },
  {
    "rating": 3,
    "content": "补水效果还行，但是同价位选择挺多，没有特别惊喜。",
    "tags": ["差异化", "性价比"]
  },
  {
    "rating": 2,
    "content": "详情页写得很高级，实际感觉就是普通保湿精华。",
    "tags": ["预期不符", "卖点表达"]
  }
]
```

---

### 5.4 ReviewCluster

```python
class ReviewCluster(BaseModel):
    id: str
    product_id: str
    cluster_name: str
    problem_type: str
    review_count: int
    ratio: float
    representative_reviews: list[str]
    user_concern: str
    business_impact: str
    suggested_action: str
```

示例输出：

```json
{
  "cluster_name": "敏感肌刺激顾虑",
  "problem_type": "product_expectation_risk",
  "review_count": 2,
  "ratio": 0.25,
  "representative_reviews": [
    "我是敏感肌，用完脸有点刺痛，不知道是不是烟酰胺不耐受。",
    "客服说敏感肌可以用，但我用完泛红更明显。"
  ],
  "user_concern": "用户担心敏感肌可用的承诺过强，实际存在刺痛和泛红风险。",
  "business_impact": "会影响敏感肌人群转化，也可能导致售后和差评增加。",
  "suggested_action": "详情页增加局部测试提示，客服话术避免绝对承诺，将敏感肌可用改为敏感肌建议先局部试用。"
}
```

---

### 5.5 AnalysisReport

```python
class AnalysisReport(BaseModel):
    id: str
    product_id: str
    status: str
    summary: str
    scores: dict[str, int]
    competitor_insights: list[dict]
    title_suggestions: list[dict]
    image_copy_suggestions: list[dict]
    detail_page_structure: list[dict]
    review_clusters: list[ReviewCluster]
    faq_items: list[dict]
    ad_material_suggestions: list[dict]
    weekly_report: dict
    markdown_report: str
    created_at: datetime
```

评分结构：

```json
{
  "title_search_score": 68,
  "main_image_click_score": 62,
  "detail_conversion_score": 58,
  "competitor_diff_score": 55,
  "review_risk_score": 60,
  "ad_landing_score": 64,
  "total_score": 61
}
```

---

## 6. API 设计

### 6.1 健康检查

```http
GET /api/health
```

返回：

```json
{
  "status": "ok"
}
```

---

### 6.2 注入美妆测试数据

```http
POST /api/seed/beauty
```

作用：

* 创建一个测试商品
* 创建 3 个竞品
* 创建评论和差评
* 创建周报测试指标

返回：

```json
{
  "product_id": "beauty-main-001",
  "competitor_count": 3,
  "review_count": 8
}
```

---

### 6.3 创建分析任务

```http
POST /api/analysis
```

请求：

```json
{
  "product_url": "https://mock.shop/product/beauty-serum-main",
  "competitor_urls": [
    "https://mock.shop/product/competitor-a",
    "https://mock.shop/product/competitor-b",
    "https://mock.shop/product/competitor-c"
  ],
  "category": "beauty_skincare",
  "platform": "mock_tmall",
  "use_seed_data": true
}
```

返回：

```json
{
  "analysis_id": "analysis_001",
  "status": "completed",
  "report_id": "report_001"
}
```

第一版可以同步执行，不需要 Celery。后续再改异步任务。

---

### 6.4 获取分析报告

```http
GET /api/reports/{report_id}
```

返回：

```json
{
  "id": "report_001",
  "product_id": "beauty-main-001",
  "summary": "...",
  "scores": {},
  "competitor_insights": [],
  "title_suggestions": [],
  "image_copy_suggestions": [],
  "detail_page_structure": [],
  "review_clusters": [],
  "faq_items": [],
  "ad_material_suggestions": [],
  "weekly_report": {},
  "markdown_report": "..."
}
```

---

### 6.5 导出 Markdown 报告

```http
GET /api/reports/{report_id}/markdown
```

返回：

```json
{
  "filename": "beauty-growth-report.md",
  "content": "..."
}
```

---

## 7. Agent 模块开发说明

### 7.1 BaseAgent

所有 Agent 继承 BaseAgent。

```python
class BaseAgent(ABC):
    name: str

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        pass
```

---

### 7.2 LLMProvider

```python
class LLMProvider(ABC):
    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None
    ) -> dict:
        pass

    @abstractmethod
    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        pass
```

第一阶段实现 `MockLLMProvider`，不要一开始依赖真实 API。

---

### 7.3 ProductParserAgent

职责：

* 根据商品 URL 或 seed 数据生成 Product 结构。
* 第一版不做真实网页解析。
* 如果 `use_seed_data=true`，直接从 seed 数据中读取商品信息。

输入：

```python
ProductParseInput:
    product_url: str
    category: str
    platform: str
    use_seed_data: bool
```

输出：

```python
Product
```

---

### 7.4 CompetitorAnalyzerAgent

职责：

* 分析竞品标题、主图文案、卖点、价格、促销。
* 生成竞品卖点矩阵。
* 找出自家商品与竞品的差异。

输出字段：

```json
[
  {
    "competitor_id": "competitor-a",
    "positioning": "低价走量型",
    "main_selling_points": ["低价", "补水", "学生党"],
    "strengths": ["价格低", "促销强", "搜索词覆盖广"],
    "weaknesses": ["成分背书弱", "敏感肌信任不足"],
    "learnable_points": ["标题中明确覆盖学生党和平价关键词"],
    "avoid_points": ["不要只打低价，否则会削弱品牌感"]
  }
]
```

---

### 7.5 ReviewClusterAgent

职责：

* 对差评做聚类。
* 不要只总结评论，要输出业务动作。
* 第一版可以用规则 + MockLLM。
* 后续可用 embedding + 聚类算法。

聚类规则可以先按关键词：

```python
CLUSTER_RULES = {
    "敏感肌刺激顾虑": ["敏感肌", "刺痛", "泛红", "不耐受"],
    "效果预期不符": ["没感觉", "不明显", "普通", "没有详情页说得"],
    "规格性价比问题": ["小", "30ml", "贵", "性价比"],
    "使用体验问题": ["黏", "搓泥", "不好吸收", "上妆"],
    "物流包装问题": ["物流", "压坏", "包装", "漏"]
}
```

输出必须包含：

* cluster_name
* problem_type
* review_count
* ratio
* representative_reviews
* user_concern
* business_impact
* suggested_action

---

### 7.6 GrowthScoringService

职责：

根据商品、竞品、评论聚类结果计算评分。

评分维度：

```python
scores = {
    "title_search_score": 0,
    "main_image_click_score": 0,
    "detail_conversion_score": 0,
    "competitor_diff_score": 0,
    "review_risk_score": 0,
    "ad_landing_score": 0,
    "total_score": 0
}
```

权重：

```python
WEIGHTS = {
    "title_search_score": 0.15,
    "main_image_click_score": 0.20,
    "detail_conversion_score": 0.20,
    "competitor_diff_score": 0.15,
    "review_risk_score": 0.15,
    "ad_landing_score": 0.15
}
```

第一版可以用规则计算：

* 标题是否包含品类词、成分词、场景词、人群词。
* 主图文案是否有明确利益点。
* 详情页是否包含痛点、成分、使用方法、FAQ、信任背书。
* 是否和竞品有差异化。
* 差评聚类是否集中。
* 投流素材卖点和落地页是否一致。

---

### 7.7 TitleOptimizerAgent

职责：

生成 3 类标题：

1. 搜索流量版
2. 转化卖点版
3. 品牌质感版

输出格式：

```json
[
  {
    "type": "search_traffic",
    "title": "烟酰胺修护精华液女补水保湿提亮肤色敏感肌换季维稳面部精华30ml",
    "reason": "覆盖烟酰胺、修护、补水、提亮、敏感肌、换季维稳等搜索词。",
    "risk_note": "敏感肌表达避免绝对化，可在详情页补充局部测试提示。"
  }
]
```

约束：

* 不允许使用绝对化功效词。
* 不允许写医学治疗承诺。
* 不允许夸大“立刻见效”“根治敏感”等表达。
* 美妆类标题要注意功效合规。

---

### 7.8 ImageCopyAgent

职责：

输出 5 张主图文案方案。

输出格式：

```json
[
  {
    "image_no": 1,
    "goal": "提升点击",
    "visual_focus": "产品瓶身居中，背景为干净浅色，突出熬夜肌修护场景。",
    "main_copy": "熬夜肌修护精华",
    "sub_copy": "补水保湿｜舒缓干燥｜改善暗沉感",
    "notes": "不要写三天变白、立即修复等夸张承诺。"
  }
]
```

5 张图固定结构：

1. 点击主图
2. 核心成分图
3. 使用场景图
4. 敏感肌顾虑解除图
5. 规格和购买建议图

---

### 7.9 DetailPageAgent

职责：

生成详情页结构，不写完整长文。

输出格式：

```json
[
  {
    "section_no": 1,
    "section_name": "首屏利益点",
    "goal": "让用户快速理解产品解决什么问题。",
    "content_points": [
      "熬夜暗沉、干燥起皮、换季不稳定",
      "补水保湿 + 舒缓修护 + 提亮肤色感"
    ],
    "copy_suggestion": "给熬夜肌的日常修护精华"
  }
]
```

建议详情页结构：

1. 首屏利益点
2. 用户痛点
3. 成分方案
4. 使用场景
5. 竞品对比
6. 敏感肌使用提示
7. 使用方法
8. FAQ
9. 规格和成交引导

---

### 7.10 FAQAgent

职责：

根据评论、差评、详情页生成客服 FAQ。

输出格式：

```json
[
  {
    "question": "敏感肌可以用吗？",
    "answer": "可以作为日常修护精华尝试，但不同肤质耐受情况不同，建议先在耳后或局部少量试用，确认无不适后再全脸使用。",
    "type": "pre_sale",
    "risk_level": "high",
    "source": "review_cluster"
  }
]
```

FAQ 类型：

* pre_sale
* usage
* concern
* after_sale

---

### 7.11 AdMaterialAgent

职责：

生成投流素材建议，不生成图片。

输出格式：

```json
[
  {
    "angle": "熬夜肌痛点型",
    "target_user": "经常熬夜、肤色暗沉、妆前卡粉的年轻女性",
    "hook": "熬夜后脸看起来又干又黄？",
    "script_structure": [
      "展示熬夜后皮肤状态",
      "指出干燥、暗沉、上妆不服帖问题",
      "引出修护精华",
      "展示质地和使用场景",
      "引导查看商品详情"
    ],
    "landing_page_requirement": "详情页首屏必须承接熬夜肌、补水保湿、妆前服帖等信息。",
    "risk_note": "不要承诺快速美白或医学修复。"
  }
]
```

素材方向至少输出 4 条：

1. 痛点型
2. 成分型
3. 场景型
4. 对比型

---

### 7.12 WeeklyReportAgent

职责：

根据本周和上周测试数据生成周报。

测试指标：

```json
{
  "last_week": {
    "impressions": 12000,
    "clicks": 480,
    "ctr": 0.04,
    "orders": 38,
    "conversion_rate": 0.079,
    "refund_rate": 0.052,
    "ad_spend": 1800,
    "revenue": 4902,
    "roi": 2.72
  },
  "this_week": {
    "impressions": 15500,
    "clicks": 760,
    "ctr": 0.049,
    "orders": 54,
    "conversion_rate": 0.071,
    "refund_rate": 0.061,
    "ad_spend": 2600,
    "revenue": 6966,
    "roi": 2.68
  }
}
```

周报输出：

```json
{
  "summary": "本周曝光和点击提升，但转化率下降，说明主图吸引力提升后详情页承接不足。",
  "metrics_change": [],
  "problems": [],
  "next_week_actions": [],
  "risk_notes": []
}
```

必须输出下周任务：

* 优先优化详情页前 3 屏。
* 补充敏感肌局部测试提示。
* 调整主图文案，避免过度承诺。
* 新增妆前不搓泥使用说明。
* 投流预算不要盲目放大，先做素材 A/B 测试。

---

## 8. 报告生成格式

Markdown 报告结构：

```markdown
# 美妆单品增长分析报告

## 1. 核心结论

## 2. SKU 增长评分

## 3. 自家商品当前问题

## 4. 竞品卖点拆解

## 5. 标题优化建议

## 6. 主图文案建议

## 7. 详情页结构建议

## 8. 差评聚类分析

## 9. 客服 FAQ

## 10. 投流素材建议

## 11. 本周数据复盘

## 12. 下周优化任务
```

报告生成由 `ReportService` 负责，不要让每个 Agent 自己拼 Markdown。

---

## 9. 开发顺序

Claude Code 开发时，按下面顺序执行。

### Step 1：初始化项目

创建：

* FastAPI 项目
* 基础目录
* pyproject.toml
* docker-compose.yml
* .env.example
* README.md
* CLAUDE.md

要求：

* 后端能启动
* `/api/health` 返回 ok
* pytest 能运行

---

### Step 2：创建 Pydantic Schema

创建以下 schema：

* Product
* CompetitorProduct
* Review
* ReviewCluster
* AnalysisReport
* WeeklyMetrics

要求：

* 所有 schema 有类型注解
* 可以被 FastAPI 自动生成 OpenAPI 文档
* 添加基础单元测试

---

### Step 3：创建美妆 seed 数据

创建：

* `beauty_products.py`
* `beauty_competitors.py`
* `beauty_reviews.py`
* `beauty_weekly_metrics.py`

实现：

```http
POST /api/seed/beauty
```

要求：

* 返回 product_id
* 返回 competitor_count
* 返回 review_count
* 不依赖数据库也可以先跑通
* 后续再接 PostgreSQL

---

### Step 4：开发 ReviewClusterAgent

先开发差评聚类，因为这是最核心的分析模块。

要求：

* 输入 reviews
* 输出 clusters
* 至少识别 5 类问题
* 每类包含业务影响和建议动作
* 写 pytest 测试

---

### Step 5：开发 CompetitorAnalyzerAgent

要求：

* 输入 self product + competitors
* 输出竞品定位、优势、弱点、可借鉴点
* 美妆测试数据必须能跑出低价型、成分党型、敏感肌型三个定位

---

### Step 6：开发 GrowthScoringService

要求：

* 输入 product、competitors、review_clusters
* 输出 6 个维度评分和 total_score
* total_score 使用权重计算
* 写测试验证评分范围为 0-100

---

### Step 7：开发生成类 Agent

依次开发：

* TitleOptimizerAgent
* ImageCopyAgent
* DetailPageAgent
* FAQAgent
* AdMaterialAgent
* WeeklyReportAgent

第一版可以用规则模板生成，后续再替换为 LLM。

---

### Step 8：开发 Orchestrator

创建：

```python
class AnalysisOrchestrator:
    async def run(request: CreateAnalysisRequest) -> AnalysisReport:
        ...
```

Orchestrator 负责串联所有 Agent。

要求：

* 不在 API route 里写业务流程
* route 只负责参数接收和结果返回
* orchestrator 输出 AnalysisReport

---

### Step 9：开发 ReportService

要求：

* 输入 AnalysisReport
* 输出 markdown_report
* 支持 `/api/reports/{report_id}`
* 支持 `/api/reports/{report_id}/markdown`

---

### Step 10：补测试

至少要有：

```text
test_analysis_flow.py
test_review_cluster.py
test_scoring.py
test_report_generation.py
```

测试目标：

* seed 数据能创建
* 分析流程能完整跑通
* 差评能聚类
* 评分在合理范围
* Markdown 报告包含所有必要章节

---

## 10. Claude Code 执行提示词

### 10.1 初始化提示词

```text
请根据 DEV_SPEC.md 初始化项目。

要求：
1. 先创建 backend FastAPI 项目。
2. 只实现后端 MVP，不开发前端。
3. 创建清晰的目录结构。
4. 添加 /api/health 接口。
5. 添加 pyproject.toml、.env.example、README.md。
6. 添加 pytest 配置。
7. 每完成一个阶段请运行测试。
8. 不要引入复杂依赖，不要做真实爬虫，不要接真实平台 API。
```

---

### 10.2 开发 schema 提示词

```text
请根据 DEV_SPEC.md 的数据模型，创建 backend/app/schemas 下的 Pydantic v2 schema。

要求：
1. 创建 Product、CompetitorProduct、Review、ReviewCluster、AnalysisReport、WeeklyMetrics。
2. 所有字段必须有类型注解。
3. 对列表字段使用 default_factory。
4. 对分数字段添加 0-100 范围校验。
5. 添加基础单元测试，验证 schema 可以正常实例化。
```

---

### 10.3 开发 seed 数据提示词

```text
请创建美妆行业测试数据 seed。

要求：
1. 创建 backend/app/seed/beauty_products.py。
2. 创建 backend/app/seed/beauty_competitors.py。
3. 创建 backend/app/seed/beauty_reviews.py。
4. 创建 backend/app/seed/beauty_weekly_metrics.py。
5. 创建 POST /api/seed/beauty 接口。
6. 第一版可以使用内存存储，不强制接数据库。
7. 返回 product_id、competitor_count、review_count。
8. 添加测试验证 seed 接口可用。
```

---

### 10.4 开发差评聚类提示词

```text
请开发 ReviewClusterAgent。

要求：
1. 输入 Review 列表。
2. 使用规则关键词进行聚类。
3. 至少支持以下类目：
   - 敏感肌刺激顾虑
   - 效果预期不符
   - 规格性价比问题
   - 使用体验问题
   - 物流包装问题
4. 输出 ReviewCluster 列表。
5. 每个 cluster 必须包含 user_concern、business_impact、suggested_action。
6. 添加 pytest 测试，确保美妆测试差评可以被正确聚类。
```

---

### 10.5 开发完整分析流程提示词

```text
请开发 AnalysisOrchestrator，并串联全部 Agent。

要求：
1. 输入 CreateAnalysisRequest。
2. 如果 use_seed_data=true，则读取美妆 seed 数据。
3. 依次执行：
   - ProductParserAgent
   - CompetitorAnalyzerAgent
   - ReviewClusterAgent
   - GrowthScoringService
   - TitleOptimizerAgent
   - ImageCopyAgent
   - DetailPageAgent
   - FAQAgent
   - AdMaterialAgent
   - WeeklyReportAgent
   - ReportService
4. 输出 AnalysisReport。
5. 创建 POST /api/analysis 接口。
6. 创建 GET /api/reports/{report_id} 接口。
7. 创建 GET /api/reports/{report_id}/markdown 接口。
8. 添加 test_analysis_flow.py，确保完整流程能跑通。
```

---

## 11. 验收标准

第一版完成后，必须满足以下验收条件：

### 11.1 接口验收

以下接口可用：

```text
GET /api/health
POST /api/seed/beauty
POST /api/analysis
GET /api/reports/{report_id}
GET /api/reports/{report_id}/markdown
```

### 11.2 流程验收

调用：

```http
POST /api/analysis
```

请求：

```json
{
  "product_url": "https://mock.shop/product/beauty-serum-main",
  "competitor_urls": [
    "https://mock.shop/product/competitor-a",
    "https://mock.shop/product/competitor-b",
    "https://mock.shop/product/competitor-c"
  ],
  "category": "beauty_skincare",
  "platform": "mock_tmall",
  "use_seed_data": true
}
```

必须返回完整报告。

### 11.3 报告验收

报告必须包含：

* 核心结论
* SKU 增长评分
* 竞品卖点拆解
* 标题优化
* 主图文案
* 详情页结构
* 差评聚类
* 客服 FAQ
* 投流素材建议
* 周报
* 下周行动计划

### 11.4 测试验收

运行：

```bash
pytest
```

必须全部通过。

---

## 12. 后续扩展方向

第一版完成后，再做以下扩展：

### 12.1 数据层扩展

* 从内存存储切换到 PostgreSQL。
* 增加 Alembic migration。
* 增加历史分析记录。
* 支持多个商品项目。

### 12.2 采集层扩展

* 增加 Playwright 页面抓取。
* 增加 OCR 识别主图文字。
* 增加评论 CSV/Excel 导入。
* 增加客服聊天记录导入。

### 12.3 LLM 层扩展

* MockLLMProvider 替换为真实 LLMProvider。
* 每个 Agent 的 prompt 独立管理。
* 加入 JSON schema 校验。
* LLM 输出失败时自动 fallback 到规则模板。

### 12.4 前端扩展

* 创建分析任务页面。
* 报告详情页。
* 差评聚类可视化。
* 竞品对比表。
* Markdown 报告导出按钮。

---

## 13. 开发注意事项

1. 不要把所有逻辑堆在一个 prompt 里。
2. 不要一开始做真实爬虫。
3. 不要一开始做多平台 API。
4. 不要把报告生成和 Agent 分析混在一起。
5. 不要让 API route 承担业务编排。
6. 所有 Agent 输出都必须是结构化数据。
7. 报告 Markdown 只在 ReportService 最后生成。
8. 测试数据先固定，保证开发流程稳定。
9. 第一版以跑通闭环为目标，不追求模型效果极致。
10. 美妆类文案要避免绝对化、医疗化、夸大功效表达。

---

## 14. 第一阶段完成标志

第一阶段完成后，项目应该可以做到：

1. 启动 FastAPI。
2. 注入美妆测试数据。
3. 调用分析接口。
4. 自动生成一份完整 Markdown 增长报告。
5. 报告中能看到：

   * 自家商品问题
   * 竞品差异
   * 差评聚类
   * 标题优化
   * 主图文案
   * 详情页结构
   * FAQ
   * 投流素材建议
   * 周报复盘
6. 所有测试通过。

这就是 MVP 版本的可交付标准。

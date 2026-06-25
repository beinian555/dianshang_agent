from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.analysis import ReviewCluster, Scores, ScoreDimension

WEIGHTS = {
    "title_search": 0.15,
    "main_image_click": 0.20,
    "detail_conversion": 0.20,
    "competitor_diff": 0.15,
    "review_health": 0.15,
    "ad_landing": 0.15,
}

CATEGORY_TERMS = {
    "beauty_skincare": ["精华", "精华液", "面部", "护肤"],
}

INGREDIENT_TERMS = {
    "beauty_skincare": ["烟酰胺", "泛醇", "积雪草", "透明质酸", "玻尿酸", "胶原"],
}

SCENE_TERMS = {
    "beauty_skincare": ["熬夜", "换季", "妆前", "日常", "维稳", "修护"],
}

USER_TERMS = {
    "beauty_skincare": ["敏感肌", "干皮", "油皮", "混合皮", "学生党", "熬夜党"],
}


class GrowthScoringService:

    def calculate(
        self,
        product: Product,
        competitors: list[CompetitorProduct],
        review_clusters: list[ReviewCluster],
    ) -> Scores:
        title = self._score_title(product)
        image = self._score_main_image(product)
        detail = self._score_detail_page(product)
        diff = self._score_competitor_diff(product, competitors)
        risk = self._score_review_risk(review_clusters)
        health = self._score_review_health(review_clusters)
        ad = self._score_ad_landing(product)

        total = int(
            title.score * WEIGHTS["title_search"]
            + image.score * WEIGHTS["main_image_click"]
            + detail.score * WEIGHTS["detail_conversion"]
            + diff.score * WEIGHTS["competitor_diff"]
            + health.score * WEIGHTS["review_health"]
            + ad.score * WEIGHTS["ad_landing"]
        )

        return Scores(
            title_search=title,
            main_image_click=image,
            detail_conversion=detail,
            competitor_diff=diff,
            review_risk=risk,
            review_health=health,
            ad_landing=ad,
            total_score=total,
        )

    def _score_title(self, product: Product) -> ScoreDimension:
        score = 50
        evidence: list[str] = []
        reason_parts: list[str] = []
        title = product.title.lower()

        cats = CATEGORY_TERMS.get(product.category, [])
        matched_cats = [t for t in cats if t in title]
        if matched_cats:
            score += 10
            evidence.append(f"标题包含品类词: {', '.join(matched_cats)}")
            reason_parts.append("覆盖品类关键词")

        ingredients = INGREDIENT_TERMS.get(product.category, [])
        matched_ing = [ing for ing in ingredients if ing in title]
        if matched_ing:
            bonus = min(len(matched_ing) * 5, 15)
            score += bonus
            evidence.append(f"标题包含成分词: {', '.join(matched_ing)} (+{bonus})")
            reason_parts.append("包含成分词提升搜索曝光")

        scenes = SCENE_TERMS.get(product.category, [])
        matched_scene = [s for s in scenes if s in title]
        if matched_scene:
            bonus = min(len(matched_scene) * 3, 10)
            score += bonus
            evidence.append(f"标题包含场景词: {', '.join(matched_scene)} (+{bonus})")
            reason_parts.append("覆盖使用场景关键词")

        users = USER_TERMS.get(product.category, [])
        matched_user = [u for u in users if u in title]
        if matched_user:
            bonus = min(len(matched_user) * 3, 10)
            score += bonus
            evidence.append(f"标题包含人群词: {', '.join(matched_user)} (+{bonus})")
            reason_parts.append("覆盖目标人群关键词")

        score = min(score, 100)
        reason = "；".join(reason_parts) if reason_parts else "标题关键词覆盖不足，建议补充品类词、成分词、场景词"

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

    def _score_main_image(self, product: Product) -> ScoreDimension:
        score = 40
        evidence: list[str] = []
        reason_parts: list[str] = []
        texts = [t.lower() for t in product.main_image_texts]
        all_text = " ".join(texts)

        benefit_keywords = ["补水", "保湿", "提亮", "修护", "舒缓", "改善"]
        matched_benefits = [kw for kw in benefit_keywords if kw in all_text]
        if matched_benefits:
            score += 20
            evidence.append(f"主图包含利益点: {', '.join(matched_benefits)} (+20)")
            reason_parts.append("主图明确展示产品利益点")

        trust_keywords = ["植萃", "成分", "温和", "敏感肌"]
        matched_trust = [kw for kw in trust_keywords if kw in all_text]
        if matched_trust:
            score += 15
            evidence.append(f"主图包含信任信号: {', '.join(matched_trust)} (+15)")
            reason_parts.append("包含成分/温和等信任信号")

        if len(texts) >= 4:
            score += 10
            evidence.append(f"主图数量充足: {len(texts)}张 (+10)")
            reason_parts.append("主图数量充足(≥4张)")

        scene_keywords = ["熬夜", "换季", "日常"]
        matched_scene = [kw for kw in scene_keywords if kw in all_text]
        if matched_scene:
            score += 15
            evidence.append(f"主图包含场景词: {', '.join(matched_scene)} (+15)")
            reason_parts.append("主图覆盖使用场景")

        score = min(score, 100)
        reason = "；".join(reason_parts) if reason_parts else "主图文案信息不全，建议增加利益点和场景表达"

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

    def _score_detail_page(self, product: Product) -> ScoreDimension:
        score = 40
        evidence: list[str] = []
        reason_parts: list[str] = []
        sections = [s.lower() for s in product.detail_sections]

        has_pain_point = any("熬夜" in s or "暗沉" in s or "干燥" in s or "泛红" in s for s in sections)
        if has_pain_point:
            score += 15
            evidence.append("详情页包含用户痛点描述 (+15)")
            reason_parts.append("覆盖用户痛点")

        has_ingredients = any("烟酰胺" in s or "泛醇" in s or "积雪草" in s or "透明质酸" in s for s in sections)
        if has_ingredients:
            score += 15
            evidence.append("详情页包含成分说明 (+15)")
            reason_parts.append("包含成分说明建立专业感")

        has_usage = any("使用" in s or "洁面后" in s for s in sections)
        if has_usage:
            score += 10
            evidence.append("详情页包含使用方法 (+10)")
            reason_parts.append("包含使用指导")

        has_target = any("干皮" in s or "混合皮" in s or "敏感肌" in s for s in sections)
        if has_target:
            score += 10
            evidence.append("详情页包含适用肤质 (+10)")
            reason_parts.append("明确适用人群")

        if len(sections) >= 4:
            score += 10
            evidence.append(f"详情页板块数: {len(sections)} (+10)")
            reason_parts.append("详情页结构丰富(≥4个板块)")

        score = min(score, 100)
        reason = "；".join(reason_parts) if reason_parts else "详情页信息不足，建议补充痛点、成分、使用方法等板块"

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

    def _score_competitor_diff(
        self, product: Product, competitors: list[CompetitorProduct]
    ) -> ScoreDimension:
        score = 50
        evidence: list[str] = []
        reason_parts: list[str] = []

        if not competitors:
            return ScoreDimension(score=score, reason="无竞品数据，无法计算差异化", evidence=evidence)

        product_price = product.price or 0
        comp_prices = [c.price or 0 for c in competitors]
        avg_comp_price = sum(comp_prices) / len(comp_prices)

        if product_price > avg_comp_price:
            score += 10
            evidence.append(f"自家价格({product_price})高于竞品均价({avg_comp_price:.0f})，有溢价空间 (+10)")
            reason_parts.append("价格定位高于竞品均价，有品牌溢价空间")

        product_points = set(product.selling_points)
        all_comp_points: set[str] = set()
        for c in competitors:
            all_comp_points.update(c.selling_points)

        unique_points = product_points - all_comp_points
        if unique_points:
            bonus = min(len(unique_points) * 8, 20)
            score += bonus
            evidence.append(f"差异卖点: {', '.join(unique_points)} (+{bonus})")
            reason_parts.append(f"拥有{len(unique_points)}个差异化卖点")

        if len(product.ingredients) >= 4:
            score += 10
            evidence.append(f"成分数量: {len(product.ingredients)}种 (+10)")
            reason_parts.append("成分体系完整(≥4种)")

        if product.specs and len(product.specs) >= 2:
            score += 10
            evidence.append(f"规格选择: {len(product.specs)}种 (+10)")
            reason_parts.append("多规格覆盖不同需求")

        score = min(score, 100)
        reason = "；".join(reason_parts) if reason_parts else "与竞品差异化不足，建议强化独特卖点"

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

    def _score_review_risk(self, clusters: list[ReviewCluster]) -> ScoreDimension:
        """Risk assessment score: HIGHER score = MORE risk (0=no risk, 100=extreme risk)."""
        score = 0
        evidence: list[str] = []
        reason_parts: list[str] = []

        if not clusters:
            return ScoreDimension(score=0, reason="无差评数据，风险极低", evidence=["当前无差评数据"])

        total_ratio = sum(c.ratio for c in clusters)
        risk_score = int(total_ratio * 50)

        cluster_names = [c.cluster_name for c in clusters]
        evidence.append(f"差评聚类: {', '.join(cluster_names)}")
        evidence.append(f"总差评占比: {total_ratio:.0%}")

        high_risk_types = {"product_expectation_risk", "product_expectation_gap"}
        high_risk_clusters = [c for c in clusters if c.problem_type in high_risk_types]
        if high_risk_clusters:
            names = [c.cluster_name for c in high_risk_clusters]
            risk_score += 15
            evidence.append(f"高风险聚类({names})，产品预期与实际差距大 (+15)")
            reason_parts.append(f"存在{len(high_risk_clusters)}个高风险预期差聚类")

        risk_score = min(risk_score, 100)
        reason = "；".join(reason_parts) if reason_parts else f"共{len(clusters)}类差评，风险水平适中"

        return ScoreDimension(score=risk_score, reason=reason, evidence=evidence)

    def _score_review_health(self, clusters: list[ReviewCluster]) -> ScoreDimension:
        """Review health score: HIGHER score = HEALTHIER review ecosystem."""
        score = 100
        evidence: list[str] = []
        reason_parts: list[str] = []

        if not clusters:
            return ScoreDimension(
                score=100,
                reason="无差评，评价生态健康",
                evidence=["当前无差评数据"],
            )

        total_ratio = sum(c.ratio for c in clusters)
        deduction = int(total_ratio * 60)
        score -= deduction
        evidence.append(f"差评占比{total_ratio:.0%}，扣分-{deduction}")

        high_risk_types = {"product_expectation_risk", "product_expectation_gap"}
        for c in clusters:
            if c.problem_type in high_risk_types:
                score -= 10
                evidence.append(f"高风险类型[{c.cluster_name}]扣分-10")
                reason_parts.append(f"存在预期不符类差评，影响评价健康度")

        service_types = {"service_commitment_risk", "logistics_experience_risk"}
        for c in clusters:
            if c.problem_type in service_types:
                score -= 5
                evidence.append(f"服务类问题[{c.cluster_name}]扣分-5")
                reason_parts.append(f"存在服务/物流类差评")

        score = max(score, 0)
        if not reason_parts:
            reason_parts.append(f"评价生态整体健康，共{len(clusters)}类差评需要关注")
        reason = "；".join(reason_parts)

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

    def _score_ad_landing(self, product: Product) -> ScoreDimension:
        score = 50
        evidence: list[str] = []
        reason_parts: list[str] = []

        if product.selling_points:
            score += 10
            evidence.append(f"有明确卖点: {len(product.selling_points)}个 (+10)")
            reason_parts.append("卖点清晰，可承接投流素材")

        if product.main_image_texts:
            score += 10
            evidence.append(f"有主图文案: {len(product.main_image_texts)}张 (+10)")
            reason_parts.append("主图文案完备，投流素材可引用")

        if len(product.detail_sections) >= 4:
            score += 10
            evidence.append(f"详情页有{len(product.detail_sections)}个板块 (+10)")
            reason_parts.append("详情页内容丰富，落地页承接力强")

        if product.target_users:
            score += 10
            evidence.append(f"目标人群明确: {', '.join(product.target_users)} (+10)")
            reason_parts.append("目标人群清晰，投放定向精准")

        if product.usage_scenarios:
            score += 10
            evidence.append(f"使用场景明确: {', '.join(product.usage_scenarios)} (+10)")
            reason_parts.append("使用场景清晰，素材方向多元")

        score = min(score, 100)
        reason = "；".join(reason_parts) if reason_parts else "投流素材与落地页信息一致性不足，建议完善商品信息"

        return ScoreDimension(score=score, reason=reason, evidence=evidence)

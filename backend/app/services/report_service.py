from app.schemas.report import AnalysisReport


class ReportService:

    def generate_markdown(self, report: AnalysisReport) -> str:
        lines: list[str] = []
        p = report
        s = p.scores

        lines.append("# 美妆单品增长分析报告\n")

        # 1. Core conclusion
        lines.append("## 1. 核心结论\n")
        lines.append(p.summary or "暂无总结")
        lines.append("")

        # 2. SKU growth scores
        lines.append("## 2. SKU 增长评分\n")

        lines.append("| 评分维度 | 分数 | 说明 |")
        lines.append("|----------|------|------|")
        lines.append(f"| 标题搜索力 | {s.title_search.score} | {s.title_search.reason} |")
        lines.append(f"| 主图点击力 | {s.main_image_click.score} | {s.main_image_click.reason} |")
        lines.append(f"| 详情转化力 | {s.detail_conversion.score} | {s.detail_conversion.reason} |")
        lines.append(f"| 竞品差异力 | {s.competitor_diff.score} | {s.competitor_diff.reason} |")
        lines.append(f"| 差评风险度 | {s.review_risk.score} | 风险越低越好，当前{s.review_risk.reason} |")
        lines.append(f"| 评价健康度 | {s.review_health.score} | {s.review_health.reason} |")
        lines.append(f"| 投流承接力 | {s.ad_landing.score} | {s.ad_landing.reason} |")
        lines.append(f"| **综合得分** | **{s.total_score}** | 加权综合评分 |")
        lines.append("")

        score_comment = self._score_comment(s.total_score)
        lines.append(f"> {score_comment}")
        lines.append("")

        # 2.1 Scoring evidence
        lines.append("### 评分依据\n")
        self._append_evidence(lines, "标题搜索力", s.title_search)
        self._append_evidence(lines, "主图点击力", s.main_image_click)
        self._append_evidence(lines, "详情转化力", s.detail_conversion)
        self._append_evidence(lines, "竞品差异力", s.competitor_diff)
        self._append_evidence(lines, "差评风险度", s.review_risk)
        self._append_evidence(lines, "评价健康度", s.review_health)
        self._append_evidence(lines, "投流承接力", s.ad_landing)

        # 3. Current product issues
        lines.append("## 3. 自家商品当前问题\n")
        issues = self._extract_issues(report)
        if issues:
            for i, issue in enumerate(issues, 1):
                lines.append(f"{i}. {issue}")
        else:
            lines.append("暂未识别到明显问题。")
        lines.append("")

        # 4. Competitor insights
        lines.append("## 4. 竞品卖点拆解\n")
        for ci in p.competitor_insights:
            lines.append(f"### {ci.competitor_id} — {ci.positioning}\n")
            lines.append(f"- **核心卖点**: {', '.join(ci.main_selling_points)}")
            lines.append(f"- **优势**: {', '.join(ci.strengths)}" if ci.strengths else "- **优势**: 无")
            lines.append(f"- **弱点**: {', '.join(ci.weaknesses)}" if ci.weaknesses else "- **弱点**: 无")
            lines.append(f"- **可借鉴点**: {', '.join(ci.learnable_points)}" if ci.learnable_points else "- **可借鉴点**: 无")
            lines.append(f"- **避免点**: {', '.join(ci.avoid_points)}" if ci.avoid_points else "- **避免点**: 无")
            lines.append("")

        # 5. Title suggestions
        lines.append("## 5. 标题优化建议\n")
        for ts in p.title_suggestions:
            lines.append(f"### {ts.type}\n")
            lines.append(f"**标题**: {ts.title}\n")
            lines.append(f"**理由**: {ts.reason}")
            lines.append(f"**风险提示**: {ts.risk_note}")
            lines.append("")

        # 6. Image copy suggestions
        lines.append("## 6. 主图文案建议\n")
        for ic in p.image_copy_suggestions:
            lines.append(f"### 第{ic.image_no}张 — {ic.goal}\n")
            lines.append(f"- **视觉焦点**: {ic.visual_focus}")
            lines.append(f"- **主文案**: {ic.main_copy}")
            lines.append(f"- **副文案**: {ic.sub_copy}")
            lines.append(f"- **注意事项**: {ic.notes}")
            lines.append("")

        # 7. Detail page structure
        lines.append("## 7. 详情页结构建议\n")
        for ds in p.detail_page_structure:
            lines.append(f"### {ds.section_no}. {ds.section_name} ({ds.goal})\n")
            for point in ds.content_points:
                lines.append(f"- {point}")
            lines.append(f"\n**文案建议**: {ds.copy_suggestion}")
            lines.append("")

        # 8. Review clusters
        lines.append("## 8. 差评聚类分析\n")
        for rc in p.review_clusters:
            lines.append(f"### {rc.cluster_name}\n")
            lines.append(f"- **问题类型**: {rc.problem_type}")
            lines.append(f"- **评论数量**: {rc.review_count}（占比 {rc.ratio:.0%}）")
            lines.append(f"- **用户关注点**: {rc.user_concern}")
            lines.append(f"- **业务影响**: {rc.business_impact}")
            lines.append(f"- **建议动作**: {rc.suggested_action}")
            lines.append("")
            lines.append("**代表评论**:")
            for r in rc.representative_reviews:
                lines.append(f"> {r}")
            lines.append("")

        # 9. FAQ
        lines.append("## 9. 客服 FAQ\n")
        for faq in p.faq_items:
            lines.append(f"### Q: {faq.question} `[{faq.type}]` 风险等级: {faq.risk_level}\n")
            lines.append(f"A: {faq.answer}\n")
            lines.append(f"来源: {faq.source}")
            lines.append("")

        # 10. Ad material suggestions
        lines.append("## 10. 投流素材建议\n")
        for ad in p.ad_material_suggestions:
            lines.append(f"### {ad.angle}\n")
            lines.append(f"- **目标用户**: {ad.target_user}")
            lines.append(f"- **钩子**: {ad.hook}")
            lines.append(f"- **脚本结构**:")
            for step in ad.script_structure:
                lines.append(f"  1. {step}")
            lines.append(f"- **落地页要求**: {ad.landing_page_requirement}")
            lines.append(f"- **风险提示**: {ad.risk_note}")
            lines.append("")

        # 11. Weekly report
        lines.append("## 11. 本周数据复盘\n")
        if p.weekly_report:
            wr = p.weekly_report
            lines.append(f"### 总结\n{wr.summary}\n")
            if wr.metrics_change:
                lines.append("### 数据变化\n")
                lines.append("| 指标 | 上周 | 本周 | 变化 |")
                lines.append("|------|------|------|------|")
                for m in wr.metrics_change:
                    lines.append(f"| {m['metric']} | {m['last_week']} | {m['this_week']} | {m['change']} |")
                lines.append("")
            if wr.problems:
                lines.append("### 当前问题\n")
                for prob in wr.problems:
                    lines.append(f"- {prob}")
                lines.append("")
            if wr.risk_notes:
                lines.append("### 风险提示\n")
                for r in wr.risk_notes:
                    lines.append(f"- {r}")
                lines.append("")

        # 12. Next week actions
        lines.append("## 12. 下周优化任务\n")
        if p.weekly_report and p.weekly_report.next_week_actions:
            for i, action in enumerate(p.weekly_report.next_week_actions, 1):
                lines.append(f"{i}. {action}")
        else:
            lines.append("暂无下周计划。")
        lines.append("")

        return "\n".join(lines)

    def _append_evidence(self, lines: list[str], label: str, dim) -> None:
        lines.append(f"#### {label} ({dim.score}分)\n")
        lines.append(f"**原因**: {dim.reason}")
        if dim.evidence:
            lines.append("**依据**:")
            for e in dim.evidence:
                lines.append(f"  - {e}")
        lines.append("")

    def _score_comment(self, total: int) -> str:
        if total >= 80:
            return "整体表现良好，继续保持并做精细化优化。"
        elif total >= 60:
            return "整体表现中等偏上，重点优化详情页和差评风险。"
        elif total >= 40:
            return "整体表现一般，需要在多个维度进行系统优化。"
        else:
            return "整体表现较差，建议从标题和主图开始全面梳理。"

    def _extract_issues(self, report: AnalysisReport) -> list[str]:
        issues: list[str] = []
        s = report.scores

        if s.title_search.score < 70:
            issues.append(f"标题搜索力偏低({s.title_search.score}分)，建议补充品类词和场景词。")
        if s.main_image_click.score < 70:
            issues.append(f"主图点击力偏低({s.main_image_click.score}分)，建议在首图中加入明确利益点。")
        if s.detail_conversion.score < 70:
            issues.append(f"详情转化力偏低({s.detail_conversion.score}分)，建议增加痛点分析和成分说明。")
        if s.competitor_diff.score < 70:
            issues.append(f"竞品差异力偏低({s.competitor_diff.score}分)，建议强化差异化卖点表达。")
        if s.review_health.score < 70:
            issues.append(f"评价健康度偏低({s.review_health.score}分)，差评集中在敏感肌刺激和效果预期。")
        if s.review_risk.score > 30:
            issues.append(f"差评风险较高({s.review_risk.score}分)，需尽快干预。")

        return issues

from app.agents.base import BaseAgent
from app.schemas.analysis import WeeklyMetrics, WeeklyReportData


# ── Metric change helpers ──

def impressions_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    """Raw change ratio for impressions. Positive = growth."""
    if last.impressions == 0:
        return 0.0
    return (this.impressions - last.impressions) / last.impressions


def clicks_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.clicks == 0:
        return 0.0
    return (this.clicks - last.clicks) / last.clicks


def ctr_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.ctr == 0:
        return 0.0
    return (this.ctr - last.ctr) / last.ctr


def orders_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.orders == 0:
        return 0.0
    return (this.orders - last.orders) / last.orders


def conversion_rate_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.conversion_rate == 0:
        return 0.0
    return (this.conversion_rate - last.conversion_rate) / last.conversion_rate


def refund_rate_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.refund_rate == 0:
        return 0.0
    return (this.refund_rate - last.refund_rate) / last.refund_rate


def ad_spend_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.ad_spend == 0:
        return 0.0
    return (this.ad_spend - last.ad_spend) / last.ad_spend


def revenue_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.revenue == 0:
        return 0.0
    return (this.revenue - last.revenue) / last.revenue


def roi_change(last: WeeklyMetrics, this: WeeklyMetrics) -> float:
    if last.roi == 0:
        return 0.0
    return (this.roi - last.roi) / last.roi


# ── Sentiment helpers ──

def metric_sentiment(metric_key: str, raw_change: float, last: WeeklyMetrics, this: WeeklyMetrics) -> str:
    """Return 'positive', 'negative', or 'neutral' for a metric change.

    Positive = desirable direction:
      - CTR, orders, conversion_rate, revenue, ROI up → positive
      - refund_rate down → positive
      - impressions, clicks: directionally informative (more is generally better)
      - ad_spend down AND roi up → positive (efficiency gain)
    """
    if abs(raw_change) < 0.005:  # < 0.5% change is neutral
        return "neutral"

    if metric_key == "refund_rate":
        # refund_rate down is good
        return "positive" if raw_change < 0 else "negative"

    if metric_key == "ad_spend":
        # ad_spend down + roi up = efficiency gain = positive
        roi_raw = roi_change(last, this)
        if raw_change < 0 and roi_raw > 0:
            return "positive"
        # ad_spend up + roi down = wasted spend = negative
        if raw_change > 0 and roi_raw < 0:
            return "negative"
        return "neutral"

    # For all other metrics, up is positive
    return "positive" if raw_change > 0 else "negative"


def _percent_change(previous: float, current: float) -> str:
    if previous == 0:
        return "+0.0%" if current == 0 else "+100.0%"
    return f"{((current - previous) / previous * 100):+.1f}%"


class WeeklyReportAgent(BaseAgent):
    name = "WeeklyReportAgent"

    async def run(self, input_data: dict) -> WeeklyReportData:
        last_week, this_week = self._pick_compare_periods(input_data)

        metrics_change = self._calculate_changes(last_week, this_week)
        summary = self._generate_summary(last_week, this_week)
        problems = self._identify_problems(last_week, this_week)
        actions = self._generate_actions(last_week, this_week, problems)
        risk_notes = self._generate_risks(last_week, this_week)

        return WeeklyReportData(
            summary=summary,
            metrics_change=metrics_change,
            problems=problems,
            next_week_actions=actions,
            risk_notes=risk_notes,
        )

    def _pick_compare_periods(self, input_data: dict) -> tuple[WeeklyMetrics, WeeklyMetrics]:
        if "last_week" in input_data and "this_week" in input_data:
            return self._to_metrics(input_data["last_week"]), self._to_metrics(input_data["this_week"])

        periods = [(period, value) for period, value in input_data.items() if value is not None]
        if len(periods) < 2:
            raise ValueError("weekly metrics requires at least 2 periods")

        periods.sort(key=lambda item: str(item[0]))
        return self._to_metrics(periods[-2][1]), self._to_metrics(periods[-1][1])

    def _to_metrics(self, value) -> WeeklyMetrics:
        if isinstance(value, WeeklyMetrics):
            return value
        return WeeklyMetrics(**value)

    def _make_change_entry(self, metric_key: str, label: str,
                           last_val, this_val,
                           last_fmt: str | None = None,
                           this_fmt: str | None = None,
                           change_fmt: str | None = None) -> dict:
        """Build a metrics_change entry with sentiment."""
        if isinstance(last_val, (int, float)) and isinstance(this_val, (int, float)):
            raw = (this_val - last_val) / last_val if last_val != 0 else 0.0
            change_str = _percent_change(last_val, this_val) if change_fmt is None else change_fmt
        else:
            raw = 0.0
            change_str = change_fmt or "-"

        sentiment = metric_sentiment(metric_key, raw, self._last, self._this) \
            if hasattr(self, '_last') else "neutral"

        return {
            "metric": label,
            "key": metric_key,
            "last_week": last_fmt if last_fmt is not None else last_val,
            "this_week": this_fmt if this_fmt is not None else this_val,
            "change": change_str,
            "sentiment": sentiment,
        }

    def _calculate_changes(self, last: WeeklyMetrics, this: WeeklyMetrics) -> list[dict]:
        # Store for use by _make_change_entry
        self._last = last
        self._this = this

        return [
            self._make_change_entry("impressions", "曝光量",
                                    last.impressions, this.impressions),
            self._make_change_entry("clicks", "点击量",
                                    last.clicks, this.clicks),
            self._make_change_entry("ctr", "点击率(CTR)",
                                    last.ctr, this.ctr,
                                    last_fmt=f"{last.ctr:.2%}",
                                    this_fmt=f"{this.ctr:.2%}"),
            self._make_change_entry("orders", "订单数",
                                    last.orders, this.orders),
            self._make_change_entry("conversion_rate", "转化率",
                                    last.conversion_rate, this.conversion_rate,
                                    last_fmt=f"{last.conversion_rate:.1%}",
                                    this_fmt=f"{this.conversion_rate:.1%}"),
            self._make_change_entry("refund_rate", "退款率",
                                    last.refund_rate, this.refund_rate,
                                    last_fmt=f"{last.refund_rate:.1%}",
                                    this_fmt=f"{this.refund_rate:.1%}"),
            self._make_change_entry("ad_spend", "广告花费",
                                    last.ad_spend, this.ad_spend,
                                    last_fmt=f"¥{last.ad_spend:,.0f}",
                                    this_fmt=f"¥{this.ad_spend:,.0f}"),
            self._make_change_entry("revenue", "销售额",
                                    last.revenue, this.revenue,
                                    last_fmt=f"¥{last.revenue:,.0f}",
                                    this_fmt=f"¥{this.revenue:,.0f}"),
            self._make_change_entry("roi", "ROI",
                                    last.roi, this.roi,
                                    last_fmt=f"{last.roi:.2f}",
                                    this_fmt=f"{this.roi:.2f}"),
        ]

    # ── Dynamic text generators ──

    def _generate_summary(self, last: WeeklyMetrics, this: WeeklyMetrics) -> str:
        """Build summary from actual metric changes. Never hardcode conclusions."""
        parts: list[str] = []

        imp_ch = impressions_change(last, this)
        clk_ch = clicks_change(last, this)
        ctr_ch = ctr_change(last, this)
        ord_ch = orders_change(last, this)
        cvr_ch = conversion_rate_change(last, this)
        ref_ch = refund_rate_change(last, this)
        ads_ch = ad_spend_change(last, this)
        rev_ch = revenue_change(last, this)
        r_ch = roi_change(last, this)

        # Traffic sentence
        traffic_parts: list[str] = []
        if imp_ch > 0.02:
            traffic_parts.append(f"曝光量上升{imp_ch:+.1%}")
        elif imp_ch < -0.02:
            traffic_parts.append(f"曝光量下降{imp_ch:+.1%}")

        if clk_ch > 0.02:
            traffic_parts.append(f"点击量上升{clk_ch:+.1%}")
        elif clk_ch < -0.02:
            traffic_parts.append(f"点击量下降{clk_ch:+.1%}")

        if not traffic_parts:
            traffic_parts.append("曝光和点击量基本持平")

        if ctr_ch > 0.005:
            parts.append("、".join(traffic_parts) + f"，CTR提升{ctr_ch:+.1%}，主图和标题吸引力增强。")
        elif ctr_ch < -0.005:
            parts.append("、".join(traffic_parts) + f"，CTR下降{ctr_ch:+.1%}，主图和标题需要优化。")
        else:
            parts.append("、".join(traffic_parts) + "，CTR基本持平。")

        # Conversion sentence
        if cvr_ch > 0.01:
            parts.append(f"转化率上升{cvr_ch:+.1%}，详情页承接能力提升。")
        elif cvr_ch < -0.01:
            parts.append(f"转化率下降{cvr_ch:+.1%}，详情页承接能力需要优化。")
        else:
            parts.append("转化率基本持平。")

        # Refund sentence
        if ref_ch < -0.05:
            parts.append(f"退款率下降{abs(ref_ch):+.1%}，售后体验改善。")
        elif ref_ch > 0.05:
            parts.append(f"退款率上升{ref_ch:+.1%}，需关注售后体验和产品满意度。")

        # ROI / efficiency sentence
        if r_ch > 0.02:
            if ads_ch < 0:
                parts.append(f"ROI提升{r_ch:+.1%}，广告花费下降{abs(ads_ch):+.1%}，投放效率显著提升。")
            else:
                parts.append(f"ROI提升{r_ch:+.1%}，投放效率持续向好。")
        elif r_ch < -0.02:
            if ads_ch > 0:
                parts.append(f"ROI下降{abs(r_ch):+.1%}，广告花费增长{ads_ch:+.1%}但收入未同步增长，投放效率需要优化。")
            else:
                parts.append(f"ROI下降{abs(r_ch):+.1%}，投放效率需要关注。")

        # Revenue summary
        if rev_ch > 0.02:
            if ord_ch > 0.02:
                parts.append(f"销售额增长{rev_ch:+.1%}，订单量增长{ord_ch:+.1%}，营收趋势良好。")
            else:
                parts.append(f"销售额增长{rev_ch:+.1%}。")
        elif rev_ch < -0.02:
            parts.append(f"销售额下降{abs(rev_ch):+.1%}，需要关注营收趋势。")

        return "".join(parts)

    def _identify_problems(self, last: WeeklyMetrics, this: WeeklyMetrics) -> list[str]:
        """Identify real problems from data. Only include what the data actually shows."""
        problems: list[str] = []

        imp_ch = impressions_change(last, this)
        clk_ch = clicks_change(last, this)
        ctr_ch = ctr_change(last, this)
        cvr_ch = conversion_rate_change(last, this)
        ref_ch = refund_rate_change(last, this)
        r_ch = roi_change(last, this)
        ads_ch = ad_spend_change(last, this)
        rev_ch = revenue_change(last, this)

        # Traffic scale decline
        if imp_ch < -0.02 and clk_ch < -0.02:
            problems.append(
                f"流量规模回落：曝光下降{abs(imp_ch):.1%}、点击下降{abs(clk_ch):.1%}，"
                "需检查是否因竞品提价竞争或素材老化导致流量收缩。"
            )
        elif imp_ch < -0.02:
            problems.append(
                f"曝光量下降{abs(imp_ch):.1%}，流量入口收窄，建议排查投放计划和素材衰退情况。"
            )
        elif clk_ch < -0.02:
            problems.append(
                f"点击量下降{abs(clk_ch):.1%}，主图或标题吸引力可能不足，CTR需优化。"
            )

        # CTR decline
        if ctr_ch < -0.005:
            problems.append(
                f"CTR下降{abs(ctr_ch):.1%}，主图点击吸引力减弱，建议进行A/B测试优化主图。"
            )

        # Conversion decline
        if cvr_ch < -0.01:
            problems.append(
                f"转化率下降{abs(cvr_ch):.1%}，详情页对流量承接不足，用户浏览后未完成购买，"
                "需优化详情页前几屏的利益点和信任背书。"
            )

        # Refund rate increase
        if ref_ch > 0.05:
            problems.append(
                f"退款率上升{ref_ch:+.1%}，需关注产品满意度，检查差评中的高频投诉点，"
                "优化详情页预期管理。"
            )

        # ROI decline
        if r_ch < -0.02:
            if ads_ch > 0.05:
                problems.append(
                    f"广告ROI下降{abs(r_ch):.1%}，广告花费增长{ads_ch:+.1%}但收入增速不匹配，"
                    "投放效率下滑，需优化投放策略。"
                )
            else:
                problems.append(
                    f"广告ROI下降{abs(r_ch):.1%}，投放效率有待提升。"
                )

        # Revenue decline
        if rev_ch < -0.02:
            problems.append(
                f"销售额下降{abs(rev_ch):.1%}，需关注整体经营趋势并排查原因。"
            )

        # If everything is good, note it
        if not problems:
            problems.append(
                "本周各项指标均呈正向趋势，暂无显著问题，建议继续保持当前运营策略。"
            )

        return problems

    def _generate_actions(self, last: WeeklyMetrics, this: WeeklyMetrics,
                          problems: list[str]) -> list[str]:
        """Generate next-week actions that directly address identified problems."""
        actions: list[str] = []

        imp_ch = impressions_change(last, this)
        clk_ch = clicks_change(last, this)
        ctr_ch = ctr_change(last, this)
        cvr_ch = conversion_rate_change(last, this)
        ref_ch = refund_rate_change(last, this)
        r_ch = roi_change(last, this)
        ads_ch = ad_spend_change(last, this)

        # Traffic actions
        if imp_ch < -0.02 or clk_ch < -0.02:
            actions.append(
                "补充新素材并扩大高效投放计划覆盖：对CTR高的素材追加预算，淘汰低效素材。"
            )
            actions.append(
                "进行素材A/B测试：测试不同主图角度和标题组合，找到最优投放素材。"
            )
        else:
            # Traffic is stable or growing — maintain
            actions.append(
                "维持现有高效投放计划，对表现好的素材适度放量测试。"
            )

        # Conversion actions
        if cvr_ch < -0.01:
            actions.append(
                "优先优化详情页前3屏：确保首屏利益点清晰、痛点痛点分析到位、成分方案有说服力。"
            )
        elif cvr_ch > 0.01:
            actions.append(
                "转化率上升趋势良好，保留当前详情页核心结构，可在次级页面小幅测试优化。"
            )

        # Refund actions
        if ref_ch > 0.05:
            actions.append(
                "重点监控退款原因和高频差评，及时同步到详情页和客服话术中做预期管理。"
            )
        elif ref_ch < -0.05:
            actions.append(
                "退款率下降趋势良好，继续监控差评，保持详情页风险提示和售前预期管理。"
            )

        # ROI actions
        if r_ch < -0.02:
            actions.append(
                "优化投放效率：暂停ROI过低的投放计划，将预算集中在转化效率高的渠道。"
            )
        elif r_ch > 0.02 and ads_ch < 0:
            actions.append(
                "投放效率提升明显，广告花费下降同时ROI上升，可在验证素材稳定性后谨慎放量。"
            )
        elif r_ch > 0.02:
            actions.append(
                "ROI持续提升，可在稳定投放基础上扩大高效渠道预算。"
            )

        # CTR actions
        if ctr_ch < -0.005:
            actions.append(
                "主图点击率下降，安排主图文案和视觉A/B测试，优先测试利益点前置的表达方式。"
            )

        # Always add monitoring
        actions.append(
            "下周重点监控核心指标变化趋势，及时根据数据调整运营策略。"
        )

        return actions

    def _generate_risks(self, last: WeeklyMetrics, this: WeeklyMetrics) -> list[str]:
        """Generate risk notes based on actual data trends."""
        risks: list[str] = []

        ref_ch = refund_rate_change(last, this)
        r_ch = roi_change(last, this)
        ads_ch = ad_spend_change(last, this)
        cvr_ch = conversion_rate_change(last, this)

        if ref_ch > 0.05:
            risks.append(
                "退款率持续上升可能导致平台店铺评分下降，影响搜索权重和推荐流量。"
            )

        if r_ch < -0.02 and ads_ch > 0.05:
            risks.append(
                "广告花费增长但ROI下降，如转化率不能同步提升，投放效率可能进一步恶化。"
            )

        if cvr_ch < -0.02:
            risks.append(
                "转化率持续下降可能影响平台算法对商品的权重评估，建议尽快定位原因并优化。"
            )

        if not risks:
            risks.append(
                "当前各项指标风险可控，继续保持数据监控和日常运营维护即可。"
            )

        return risks

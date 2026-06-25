import pytest

from app.agents.mock_llm import MockLLMProvider
from app.agents.weekly_report_agent import (
    WeeklyReportAgent,
    impressions_change,
    clicks_change,
    ctr_change,
    orders_change,
    conversion_rate_change,
    refund_rate_change,
    ad_spend_change,
    revenue_change,
    roi_change,
    metric_sentiment,
    _percent_change,
)
from app.schemas.analysis import WeeklyMetrics


def make_metrics(
    impressions: int = 10000,
    clicks: int = 500,
    ctr: float = 0.05,
    orders: int = 30,
    conversion_rate: float = 0.06,
    refund_rate: float = 0.05,
    ad_spend: float = 2000,
    revenue: float = 5000,
    roi: float = 2.5,
) -> WeeklyMetrics:
    return WeeklyMetrics(
        impressions=impressions,
        clicks=clicks,
        ctr=ctr,
        orders=orders,
        conversion_rate=conversion_rate,
        refund_rate=refund_rate,
        ad_spend=ad_spend,
        revenue=revenue,
        roi=roi,
    )


# ── Percent change tests ──

def test_percent_change_positive():
    assert _percent_change(100, 150) == "+50.0%"


def test_percent_change_negative():
    assert _percent_change(100, 80) == "-20.0%"


def test_percent_change_zero_previous():
    assert _percent_change(0, 0) == "+0.0%"
    assert _percent_change(0, 50) == "+100.0%"


# ── Individual change functions ──

def test_impressions_change_up():
    last = make_metrics(impressions=10000)
    this = make_metrics(impressions=12000)
    assert impressions_change(last, this) == pytest.approx(0.2)


def test_clicks_change_down():
    last = make_metrics(clicks=500)
    this = make_metrics(clicks=400)
    assert clicks_change(last, this) == pytest.approx(-0.2)


def test_ctr_change_up():
    last = make_metrics(ctr=0.04)
    this = make_metrics(ctr=0.05)
    assert ctr_change(last, this) == pytest.approx(0.25)


def test_orders_change_up():
    last = make_metrics(orders=30)
    this = make_metrics(orders=45)
    assert orders_change(last, this) == pytest.approx(0.5)


def test_conversion_rate_change_down():
    last = make_metrics(conversion_rate=0.08)
    this = make_metrics(conversion_rate=0.06)
    assert conversion_rate_change(last, this) == pytest.approx(-0.25)


def test_refund_rate_change_up():
    last = make_metrics(refund_rate=0.04)
    this = make_metrics(refund_rate=0.05)
    assert refund_rate_change(last, this) == pytest.approx(0.25)


def test_refund_rate_change_down():
    last = make_metrics(refund_rate=0.05)
    this = make_metrics(refund_rate=0.04)
    assert refund_rate_change(last, this) == pytest.approx(-0.2)


def test_ad_spend_change():
    last = make_metrics(ad_spend=2000)
    this = make_metrics(ad_spend=1500)
    assert ad_spend_change(last, this) == pytest.approx(-0.25)


def test_revenue_change_up():
    last = make_metrics(revenue=5000)
    this = make_metrics(revenue=6000)
    assert revenue_change(last, this) == pytest.approx(0.2)


def test_roi_change_up():
    last = make_metrics(roi=2.0)
    this = make_metrics(roi=2.5)
    assert roi_change(last, this) == pytest.approx(0.25)


# ── Sentiment / direction tests ──

def test_sentiment_ctr_up_is_positive():
    last = make_metrics(ctr=0.04)
    this = make_metrics(ctr=0.05)
    raw = ctr_change(last, this)
    assert metric_sentiment("ctr", raw, last, this) == "positive"


def test_sentiment_ctr_down_is_negative():
    last = make_metrics(ctr=0.05)
    this = make_metrics(ctr=0.04)
    raw = ctr_change(last, this)
    assert metric_sentiment("ctr", raw, last, this) == "negative"


def test_sentiment_conversion_rate_up_is_positive():
    last = make_metrics(conversion_rate=0.06)
    this = make_metrics(conversion_rate=0.08)
    raw = conversion_rate_change(last, this)
    assert metric_sentiment("conversion_rate", raw, last, this) == "positive"


def test_sentiment_conversion_rate_down_is_negative():
    last = make_metrics(conversion_rate=0.08)
    this = make_metrics(conversion_rate=0.06)
    raw = conversion_rate_change(last, this)
    assert metric_sentiment("conversion_rate", raw, last, this) == "negative"


def test_sentiment_refund_rate_up_is_negative():
    """refund_rate going up is bad → negative sentiment"""
    last = make_metrics(refund_rate=0.04)
    this = make_metrics(refund_rate=0.06)
    raw = refund_rate_change(last, this)
    assert raw > 0  # refund went up
    assert metric_sentiment("refund_rate", raw, last, this) == "negative"


def test_sentiment_refund_rate_down_is_positive():
    """refund_rate going down is good → positive sentiment"""
    last = make_metrics(refund_rate=0.06)
    this = make_metrics(refund_rate=0.04)
    raw = refund_rate_change(last, this)
    assert raw < 0  # refund went down
    assert metric_sentiment("refund_rate", raw, last, this) == "positive"


def test_sentiment_roi_up_is_positive():
    last = make_metrics(roi=2.0)
    this = make_metrics(roi=2.8)
    raw = roi_change(last, this)
    assert metric_sentiment("roi", raw, last, this) == "positive"


def test_sentiment_roi_down_is_negative():
    last = make_metrics(roi=2.8)
    this = make_metrics(roi=2.0)
    raw = roi_change(last, this)
    assert metric_sentiment("roi", raw, last, this) == "negative"


def test_sentiment_ad_spend_down_roi_up_is_positive():
    """ad_spend down while ROI up = efficiency gain → positive"""
    last = make_metrics(ad_spend=3000, roi=2.0)
    this = make_metrics(ad_spend=2000, roi=2.5)
    raw = ad_spend_change(last, this)
    assert raw < 0  # spend went down
    assert metric_sentiment("ad_spend", raw, last, this) == "positive"


def test_sentiment_ad_spend_up_roi_down_is_negative():
    """ad_spend up while ROI down = wasting money → negative"""
    last = make_metrics(ad_spend=2000, roi=2.5)
    this = make_metrics(ad_spend=3000, roi=2.0)
    raw = ad_spend_change(last, this)
    assert raw > 0  # spend went up
    assert metric_sentiment("ad_spend", raw, last, this) == "negative"


def test_sentiment_revenue_up_is_positive():
    last = make_metrics(revenue=5000)
    this = make_metrics(revenue=6000)
    raw = revenue_change(last, this)
    assert metric_sentiment("revenue", raw, last, this) == "positive"


def test_sentiment_neutral_for_small_change():
    last = make_metrics(ctr=0.0500)
    this = make_metrics(ctr=0.0501)
    raw = ctr_change(last, this)
    assert abs(raw) < 0.005
    assert metric_sentiment("ctr", raw, last, this) == "neutral"


# ── Summary consistency tests ──

@pytest.mark.asyncio
async def test_summary_when_conversion_rate_up_does_not_say_down():
    """When conversion_rate goes up, summary must NOT say it went down."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(conversion_rate=0.05, orders=30)
    this = make_metrics(conversion_rate=0.08, orders=45)
    report = await agent.run({"last_week": last, "this_week": this})
    assert "转化率下降" not in report.summary
    assert "下降" not in report.summary or "转化率上升" in report.summary


@pytest.mark.asyncio
async def test_summary_when_refund_rate_down_does_not_say_up():
    """When refund_rate goes down, summary must NOT say it went up."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(refund_rate=0.06)
    this = make_metrics(refund_rate=0.03)
    report = await agent.run({"last_week": last, "this_week": this})
    assert "退款率上升" not in report.summary


@pytest.mark.asyncio
async def test_summary_when_roi_up_does_not_say_down():
    """When ROI goes up, summary must NOT say it went down."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(roi=2.0)
    this = make_metrics(roi=3.0)
    report = await agent.run({"last_week": last, "this_week": this})
    assert "ROI下降" not in report.summary


@pytest.mark.asyncio
async def test_problems_when_refund_rate_down_does_not_say_up():
    """When refund_rate goes down, problems must NOT claim refund_rate is rising."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(refund_rate=0.06)
    this = make_metrics(refund_rate=0.03)
    report = await agent.run({"last_week": last, "this_week": this})
    for p in report.problems:
        assert "退款率上升" not in p


@pytest.mark.asyncio
async def test_problems_when_roi_up_does_not_say_down():
    """When ROI goes up, problems must NOT say ROI is down."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(roi=2.0)
    this = make_metrics(roi=3.0)
    report = await agent.run({"last_week": last, "this_week": this})
    for p in report.problems:
        assert "ROI下降" not in p


@pytest.mark.asyncio
async def test_problems_when_conversion_rate_up_does_not_say_down():
    """When conversion_rate goes up, problems must NOT say conversion is down."""
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(conversion_rate=0.05, orders=30)
    this = make_metrics(conversion_rate=0.08, orders=45)
    report = await agent.run({"last_week": last, "this_week": this})
    for p in report.problems:
        assert "转化率下降" not in p


# ── Original tests (updated) ──

@pytest.mark.asyncio
async def test_weekly_report_accepts_date_range_periods():
    agent = WeeklyReportAgent(MockLLMProvider())

    report = await agent.run({
        "2026-05-01~2026-05-07": make_metrics(impressions=100, clicks=10, orders=1),
        "2026-05-08~2026-05-14": make_metrics(impressions=150, clicks=12, orders=2),
        "2026-05-15~2026-05-21": make_metrics(impressions=180, clicks=18, orders=3),
    })

    assert len(report.metrics_change) == 9
    assert report.metrics_change[0]["last_week"] == 150
    assert report.metrics_change[0]["this_week"] == 180


@pytest.mark.asyncio
async def test_weekly_report_keeps_last_week_aliases():
    agent = WeeklyReportAgent(MockLLMProvider())

    report = await agent.run({
        "last_week": make_metrics(impressions=100, clicks=10, orders=1),
        "this_week": make_metrics(impressions=120, clicks=12, orders=2),
    })

    assert report.metrics_change[0]["last_week"] == 100
    assert report.metrics_change[0]["this_week"] == 120


# ── metrics_change includes sentiment and key ──

@pytest.mark.asyncio
async def test_metrics_change_has_sentiment_and_key():
    agent = WeeklyReportAgent(MockLLMProvider())
    report = await agent.run({
        "last_week": make_metrics(conversion_rate=0.05, refund_rate=0.06, roi=2.0),
        "this_week": make_metrics(conversion_rate=0.08, refund_rate=0.03, roi=2.5),
    })
    for entry in report.metrics_change:
        assert "sentiment" in entry, f"Missing sentiment in {entry['metric']}"
        assert "key" in entry, f"Missing key in {entry['metric']}"
        assert entry["sentiment"] in ("positive", "negative", "neutral")


@pytest.mark.asyncio
async def test_refund_rate_down_has_positive_sentiment():
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(refund_rate=0.06)
    this = make_metrics(refund_rate=0.03)
    report = await agent.run({"last_week": last, "this_week": this})
    refund_entry = [e for e in report.metrics_change if e["key"] == "refund_rate"][0]
    assert refund_entry["sentiment"] == "positive"


@pytest.mark.asyncio
async def test_refund_rate_up_has_negative_sentiment():
    agent = WeeklyReportAgent(MockLLMProvider())
    last = make_metrics(refund_rate=0.03)
    this = make_metrics(refund_rate=0.06)
    report = await agent.run({"last_week": last, "this_week": this})
    refund_entry = [e for e in report.metrics_change if e["key"] == "refund_rate"][0]
    assert refund_entry["sentiment"] == "negative"

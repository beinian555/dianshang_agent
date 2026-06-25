from app.schemas.analysis import WeeklyMetrics

LAST_WEEK = WeeklyMetrics(
    impressions=12000,
    clicks=480,
    ctr=0.04,
    orders=38,
    conversion_rate=0.079,
    refund_rate=0.052,
    ad_spend=1800,
    revenue=4902,
    roi=2.72,
)

THIS_WEEK = WeeklyMetrics(
    impressions=15500,
    clicks=760,
    ctr=0.049,
    orders=54,
    conversion_rate=0.071,
    refund_rate=0.061,
    ad_spend=2600,
    revenue=6966,
    roi=2.68,
)

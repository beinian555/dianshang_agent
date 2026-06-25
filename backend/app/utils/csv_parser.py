import csv
import io
import math
from typing import Callable

from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.analysis import WeeklyMetrics
from app.schemas.project import ImportResult


def _read_csv(csv_content: str) -> tuple[list[str], list[dict]]:
    """Read CSV with UTF-8 BOM support, skip empty rows. Returns (fieldnames, rows)."""
    # Strip BOM
    if csv_content.startswith("﻿"):
        csv_content = csv_content[1:]

    reader = csv.DictReader(io.StringIO(csv_content))
    rows = [row for row in reader if any(v and v.strip() for v in row.values() if v is not None)]
    return reader.fieldnames or [], rows


def _split_field(val: str | None) -> list[str]:
    if not val or not val.strip():
        return []
    return [v.strip() for v in val.split("|") if v.strip()]


def _safe_float(val: str | None) -> float | None:
    if val is None or not val.strip():
        return None
    try:
        return float(val.strip())
    except ValueError:
        raise ValueError(f"无法将 '{val}' 转换为数字")


def _safe_int(val: str | None) -> int | None:
    if val is None or not val.strip():
        return None
    try:
        return int(val.strip())
    except ValueError:
        raise ValueError(f"无法将 '{val}' 转换为整数")


def _validate_rating(val: str | None) -> int:
    rating = _safe_int(val)
    if rating is None:
        raise ValueError("rating 为必填项")
    if rating < 1 or rating > 5:
        raise ValueError(f"rating 必须在 1-5 之间，当前值: {rating}")
    return rating


def _validate_price(val: str | None) -> float | None:
    if val is None or not val.strip():
        return None
    price = _safe_float(val)
    if price is not None and price < 0:
        raise ValueError(f"price 不能为负数: {price}")
    return price


REQUIRED_PRODUCT_COLS = {"platform", "category", "url", "title"}
REQUIRED_COMPETITOR_COLS = {"url", "title"}
REQUIRED_REVIEW_COLS = {"rating", "content"}
REQUIRED_METRICS_COLS = {"period", "impressions", "clicks", "orders"}  # period can also be 'week'
PERIOD_ALIASES = {"period", "week"}


def _check_required_cols(fieldnames: list[str], required: set[str], import_type: str) -> list[str]:
    missing = required - set(fieldnames)
    if missing:
        raise ValueError(f"{import_type} CSV 缺少必填列: {', '.join(sorted(missing))}")


def _make_preview_row(row: dict, columns: list[str]) -> dict:
    return {k: str(row.get(k, ""))[:60] for k in columns[:6]}


# ── Product ──

def parse_product_csv_with_validation(
    csv_content: str, product_id: str
) -> tuple[Product | None, ImportResult]:
    warnings: list[str] = []
    errors: list[str] = []
    preview: list[dict] = []

    try:
        # Decode with BOM support
        if hasattr(csv_content, "startswith") and csv_content.startswith("﻿"):
            csv_content = csv_content[1:]

        fieldnames, rows = _read_csv(csv_content)
        _check_required_cols(fieldnames, REQUIRED_PRODUCT_COLS, "product")

        if not rows:
            errors.append("CSV 无有效数据行")
            return None, ImportResult(
                project_id=product_id, import_type="product",
                success_count=0, failed_count=0, warnings=warnings, errors=errors,
            )

        row = rows[0]  # product CSV only has 1 row
        preview = [_make_preview_row(row, fieldnames)]

        title = (row.get("title") or "").strip()
        url = (row.get("url") or "").strip()
        platform = (row.get("platform") or "mock_tmall").strip()
        category = (row.get("category") or "beauty_skincare").strip()

        price = None
        try:
            price = _validate_price(row.get("price"))
        except ValueError as e:
            warnings.append(f"price 解析失败: {e}，已设为空")

        original_price = None
        try:
            original_price = _validate_price(row.get("original_price"))
        except ValueError as e:
            warnings.append(f"original_price 解析失败: {e}，已设为空")

        product = Product(
            id=product_id,
            platform=platform,
            category=category,
            url=url,
            title=title,
            brand=row.get("brand") or None,
            price=price,
            original_price=original_price,
            sku_name=row.get("sku_name") or None,
            specs=_split_field(row.get("specs")),
            main_image_texts=_split_field(row.get("main_image_texts")),
            detail_sections=_split_field(row.get("detail_sections")),
            selling_points=_split_field(row.get("selling_points")),
            ingredients=_split_field(row.get("ingredients")),
            target_users=_split_field(row.get("target_users")),
            usage_scenarios=_split_field(row.get("usage_scenarios")),
        )

        return product, ImportResult(
            project_id=product_id, import_type="product",
            success_count=1, failed_count=0,
            warnings=warnings, errors=errors, preview=preview,
        )

    except Exception as e:
        errors.append(str(e))
        return None, ImportResult(
            project_id=product_id, import_type="product",
            success_count=0, failed_count=1,
            warnings=warnings, errors=errors, preview=preview,
        )


# ── Competitors ──

def parse_competitors_csv_with_validation(
    csv_content: str, product_id: str
) -> tuple[list[CompetitorProduct], ImportResult]:
    warnings: list[str] = []
    errors: list[str] = []
    preview: list[dict] = []
    competitors: list[CompetitorProduct] = []
    success_count = 0
    failed_count = 0

    try:
        fieldnames, rows = _read_csv(csv_content)
        _check_required_cols(fieldnames, REQUIRED_COMPETITOR_COLS, "competitors")

        for i, row in enumerate(rows):
            line_no = i + 2  # header + 1-indexed
            try:
                url = (row.get("url") or "").strip()
                title = (row.get("title") or "").strip()
                if not url or not title:
                    raise ValueError("url 和 title 为必填项")

                price = None
                try:
                    price = _validate_price(row.get("price"))
                except ValueError:
                    warnings.append(f"第{line_no}行 price 解析失败")

                rating = None
                try:
                    rating = _validate_price(row.get("rating"))
                except ValueError:
                    warnings.append(f"第{line_no}行 rating 解析失败")

                review_count = None
                try:
                    review_count = _safe_int(row.get("review_count"))
                except ValueError:
                    warnings.append(f"第{line_no}行 review_count 解析失败")

                competitors.append(
                    CompetitorProduct(
                        id=row.get("id", f"competitor-{line_no}").strip(),
                        product_id=product_id,
                        url=url,
                        title=title,
                        brand=row.get("brand") or None,
                        price=price,
                        sales_hint=row.get("sales_hint") or None,
                        rating=rating,
                        review_count=review_count,
                        selling_points=_split_field(row.get("selling_points")),
                        main_image_texts=_split_field(row.get("main_image_texts")),
                        detail_sections=_split_field(row.get("detail_sections")),
                        promotions=_split_field(row.get("promotions")),
                        weakness_hints=_split_field(row.get("weakness_hints")),
                    )
                )
                success_count += 1
                if len(preview) < 5:
                    preview.append(_make_preview_row(row, fieldnames))

            except Exception as e:
                failed_count += 1
                errors.append(f"第{line_no}行: {e}")

        if len(competitors) < 1:
            warnings.append("竞品数量少于 1 个，建议至少导入 1 个竞品进行分析")

        return competitors, ImportResult(
            project_id=product_id, import_type="competitors",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )

    except Exception as e:
        errors.append(str(e))
        return competitors, ImportResult(
            project_id=product_id, import_type="competitors",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )


# ── Reviews ──

def parse_reviews_csv_with_validation(
    csv_content: str, product_id: str
) -> tuple[list[Review], ImportResult]:
    warnings: list[str] = []
    errors: list[str] = []
    preview: list[dict] = []
    reviews: list[Review] = []
    success_count = 0
    failed_count = 0

    try:
        fieldnames, rows = _read_csv(csv_content)
        _check_required_cols(fieldnames, REQUIRED_REVIEW_COLS, "reviews")

        for i, row in enumerate(rows):
            line_no = i + 2
            try:
                content = (row.get("content") or "").strip()
                if not content:
                    raise ValueError("content 为必填项")

                rating = _validate_rating(row.get("rating"))

                reviews.append(
                    Review(
                        id=row.get("id", f"review-{line_no}").strip(),
                        product_id=product_id,
                        source=row.get("source", "csv_import").strip(),
                        rating=rating,
                        content=content,
                        tags=_split_field(row.get("tags")),
                    )
                )
                success_count += 1
                if len(preview) < 5:
                    preview.append(_make_preview_row(row, fieldnames))

            except Exception as e:
                failed_count += 1
                errors.append(f"第{line_no}行: {e}")

        if success_count < 5:
            warnings.append(f"评论数量较少({success_count}条)，建议至少导入 5 条评论以保证分析质量")

        return reviews, ImportResult(
            project_id=product_id, import_type="reviews",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )

    except Exception as e:
        errors.append(str(e))
        return reviews, ImportResult(
            project_id=product_id, import_type="reviews",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )


# ── Metrics ──

def parse_metrics_csv_with_validation(
    csv_content: str
) -> tuple[dict[str, WeeklyMetrics], ImportResult]:
    warnings: list[str] = []
    errors: list[str] = []
    preview: list[dict] = []
    metrics: dict[str, WeeklyMetrics] = {}
    success_count = 0
    failed_count = 0
    import_id = "metrics"

    try:
        fieldnames, rows = _read_csv(csv_content)
        # Accept 'week' as alias for 'period'
        if "week" in set(fieldnames) and "period" not in set(fieldnames):
            fieldnames = [("period" if c == "week" else c) for c in fieldnames]
            # Remap rows too
            for row in rows:
                if "week" in row:
                    row["period"] = row.pop("week")
        _check_required_cols(fieldnames, REQUIRED_METRICS_COLS, "metrics")

        for i, row in enumerate(rows):
            line_no = i + 2
            period = (row.get("period") or "").strip()
            if not period:
                continue  # skip empty rows silently

            try:
                metrics[period] = WeeklyMetrics(
                    impressions=_safe_int(row.get("impressions")) or 0,
                    clicks=_safe_int(row.get("clicks")) or 0,
                    ctr=_safe_float(row.get("ctr")) or 0.0,
                    orders=_safe_int(row.get("orders")) or 0,
                    conversion_rate=_safe_float(row.get("conversion_rate")) or 0.0,
                    refund_rate=_safe_float(row.get("refund_rate")) or 0.0,
                    ad_spend=_safe_float(row.get("ad_spend")) or 0.0,
                    revenue=_safe_float(row.get("revenue")) or 0.0,
                    roi=_safe_float(row.get("roi")) or 0.0,
                )
                success_count += 1
                if len(preview) < 5:
                    preview.append(_make_preview_row(row, fieldnames))

            except Exception as e:
                failed_count += 1
                errors.append(f"第{line_no}行(period={period}): {e}")

        return metrics, ImportResult(
            project_id=import_id, import_type="metrics",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )

    except Exception as e:
        errors.append(str(e))
        return metrics, ImportResult(
            project_id=import_id, import_type="metrics",
            success_count=success_count, failed_count=failed_count,
            warnings=warnings, errors=errors, preview=preview,
        )


# ── Backward-compatible wrappers ──

def parse_product_csv(csv_content: str, product_id: str) -> Product:
    product, _ = parse_product_csv_with_validation(csv_content, product_id)
    if product is None:
        raise ValueError("Failed to parse product CSV")
    return product


def parse_competitors_csv(csv_content: str, product_id: str) -> list[CompetitorProduct]:
    competitors, _ = parse_competitors_csv_with_validation(csv_content, product_id)
    return competitors


def parse_reviews_csv(csv_content: str, product_id: str) -> list[Review]:
    reviews, _ = parse_reviews_csv_with_validation(csv_content, product_id)
    return reviews


def parse_metrics_csv(csv_content: str) -> dict[str, WeeklyMetrics]:
    metrics, _ = parse_metrics_csv_with_validation(csv_content)
    return metrics

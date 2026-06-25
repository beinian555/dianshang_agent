"use client";

import { useEffect, useState, useCallback } from "react";
import { use } from "react";
import Link from "next/link";
import { getReport, getReportMarkdown, type AnalysisReport } from "@/lib/api";

const DIMENSION_LABELS: Record<string, string> = {
  title_search: "标题搜索",
  main_image_click: "主图点击",
  detail_conversion: "详情转化",
  competitor_diff: "竞品差异",
  review_risk: "评论风险",
  review_health: "评论健康",
  ad_landing: "广告落地",
};

const RISK_COLORS: Record<string, string> = {
  high: "text-red-600 bg-red-50 border-red-200",
  medium: "text-amber-600 bg-amber-50 border-amber-200",
  low: "text-green-600 bg-green-50 border-green-200",
};

function ScoreBar({ label, dim }: { label: string; dim: { score: number; reason: string; evidence: string[] } }) {
  const color =
    dim.score >= 80
      ? "bg-green-500"
      : dim.score >= 60
      ? "bg-blue-500"
      : dim.score >= 40
      ? "bg-amber-500"
      : "bg-red-500";

  return (
    <div className="p-4 bg-white border border-zinc-200 rounded-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-sm text-zinc-800">{label}</span>
        <span className="font-bold text-lg">{dim.score}</span>
      </div>
      <div className="w-full h-2 bg-zinc-100 rounded-full mb-3">
        <div
          className={`h-2 rounded-full ${color} transition-all`}
          style={{ width: `${dim.score}%` }}
        />
      </div>
      <p className="text-xs text-zinc-600 mb-2">{dim.reason}</p>
      {dim.evidence.length > 0 && (
        <div className="space-y-1">
          {dim.evidence.map((e, i) => (
            <p key={i} className="text-xs text-zinc-500">
              · {e}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}

export default function ReportDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [markdown, setMarkdown] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<
    "scores" | "competitors" | "content" | "reviews" | "ads" | "weekly" | "markdown"
  >("scores");

  const loadReport = useCallback(async () => {
    try {
      setLoading(true);
      const [data, md] = await Promise.all([
        getReport(id),
        getReportMarkdown(id),
      ]);
      setReport(data);
      setMarkdown(md.content);
    } catch {
      setError("报告加载失败");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadReport();
  }, [loadReport]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-10">
        <p className="text-zinc-500">加载报告中...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-10">
        <div className="p-5 bg-red-50 border border-red-200 text-red-700 rounded-xl">
          {error || "报告不存在"}
        </div>
        <Link href="/" className="text-blue-600 text-sm mt-4 inline-block">
          ← 返回项目列表
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10">
      <Link
        href={`/projects/${report.product_id.split("-")[0]}-${report.product_id.split("-")[1]}`}
        className="text-sm text-blue-600 hover:underline mb-4 inline-block"
      >
        ← 返回项目
      </Link>

      <div className="flex items-center justify-between mt-2 mb-2">
        <h1 className="text-2xl font-bold text-zinc-900">增长分析报告</h1>
        <span className="text-sm text-zinc-500">
          {new Date(report.created_at).toLocaleString("zh-CN")}
        </span>
      </div>

      {/* Summary */}
      {report.summary && (
        <div className="p-5 bg-blue-50 border border-blue-200 rounded-xl mb-6 text-sm text-zinc-700">
          <h2 className="font-semibold text-zinc-900 mb-1">概览</h2>
          {report.summary}
        </div>
      )}

      {/* Total Score */}
      <div className="flex items-center gap-4 mb-6 p-5 bg-white border border-zinc-200 rounded-xl">
        <div className="flex-shrink-0 w-20 h-20 rounded-full bg-blue-50 border-4 border-blue-500 flex items-center justify-center">
          <span className="text-2xl font-bold text-blue-600">
            {report.scores.total_score}
          </span>
        </div>
        <div>
          <h2 className="text-lg font-semibold text-zinc-900">综合分数</h2>
          <p className="text-sm text-zinc-500">满分 100，基于7个维度加权计算</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto">
        {[
          { key: "scores", label: "评分详情" },
          { key: "competitors", label: "竞品分析" },
          { key: "content", label: "内容优化" },
          { key: "reviews", label: "评论洞察" },
          { key: "ads", label: "广告素材" },
          { key: "weekly", label: "周报" },
          { key: "markdown", label: "Markdown" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() =>
              setActiveTab(
                tab.key as
                  | "scores"
                  | "competitors"
                  | "content"
                  | "reviews"
                  | "ads"
                  | "weekly"
                  | "markdown"
              )
            }
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              activeTab === tab.key
                ? "bg-blue-600 text-white"
                : "bg-white border border-zinc-200 text-zinc-600 hover:bg-zinc-50"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Scores */}
        {activeTab === "scores" && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              7维度评分
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(DIMENSION_LABELS).map(([key, label]) => {
                const dim =
                  report.scores[key as keyof typeof report.scores];
                if (typeof dim !== "object" || dim === null) return null;
                return (
                  <ScoreBar key={key} label={label} dim={dim as { score: number; reason: string; evidence: string[] }} />
                );
              })}
            </div>
          </div>
        )}

        {/* Competitors */}
        {activeTab === "competitors" && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              竞品对比矩阵
            </h2>
            <div className="space-y-4">
              {report.competitor_insights.map((ci) => (
                <div
                  key={ci.competitor_id}
                  className="p-5 bg-white border border-zinc-200 rounded-xl"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-zinc-900">
                      {ci.competitor_id}
                    </h3>
                    <span className="text-xs text-zinc-500">
                      {ci.positioning}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium text-green-700 mb-1">优势</p>
                      <ul className="space-y-1">
                        {ci.strengths.map((s, i) => (
                          <li key={i} className="text-zinc-600">
                            + {s}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="font-medium text-red-700 mb-1">劣势</p>
                      <ul className="space-y-1">
                        {ci.weaknesses.map((w, i) => (
                          <li key={i} className="text-zinc-600">
                            - {w}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="font-medium text-blue-700 mb-1">值得学习</p>
                      <ul className="space-y-1">
                        {ci.learnable_points.map((p, i) => (
                          <li key={i} className="text-zinc-600">
                            → {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="font-medium text-amber-700 mb-1">需要避免</p>
                      <ul className="space-y-1">
                        {ci.avoid_points.map((p, i) => (
                          <li key={i} className="text-zinc-600">
                            ✕ {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Content */}
        {activeTab === "content" && (
          <div className="space-y-8">
            {/* Titles */}
            <div>
              <h2 className="text-lg font-semibold text-zinc-800 mb-4">
                标题建议 ({report.title_suggestions.length})
              </h2>
              <div className="space-y-3">
                {report.title_suggestions.map((t, i) => (
                  <div
                    key={i}
                    className="p-4 bg-white border border-zinc-200 rounded-xl"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-zinc-100 text-zinc-600">
                        {t.type}
                      </span>
                      <h3 className="font-medium text-zinc-900">
                        {t.title}
                      </h3>
                    </div>
                    <p className="text-xs text-zinc-500">
                      理由：{t.reason}
                    </p>
                    {t.risk_note && (
                      <p className="text-xs text-amber-600 mt-1">
                        风险：{t.risk_note}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Image Copies */}
            <div>
              <h2 className="text-lg font-semibold text-zinc-800 mb-4">
                主图文案 ({report.image_copy_suggestions.length})
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {report.image_copy_suggestions.map((img) => (
                  <div
                    key={img.image_no}
                    className="p-4 bg-white border border-zinc-200 rounded-xl"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-blue-100 text-blue-700">
                        #{img.image_no}
                      </span>
                      <span className="text-xs text-zinc-500">
                        {img.goal}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-zinc-900 mb-1">
                      {img.main_copy}
                    </p>
                    <p className="text-xs text-zinc-600">{img.sub_copy}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Detail Page */}
            <div>
              <h2 className="text-lg font-semibold text-zinc-800 mb-4">
                详情页结构 ({report.detail_page_structure.length})
              </h2>
              <div className="space-y-3">
                {report.detail_page_structure.map((sec) => (
                  <div
                    key={sec.section_no}
                    className="p-4 bg-white border border-zinc-200 rounded-xl"
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs px-2 py-0.5 rounded bg-zinc-100 text-zinc-600">
                        #{sec.section_no}
                      </span>
                      <h3 className="font-medium text-zinc-900">
                        {sec.section_name}
                      </h3>
                      <span className="text-xs text-zinc-500">
                        ({sec.goal})
                      </span>
                    </div>
                    <ul className="space-y-1 mb-2">
                      {sec.content_points.map((p, i) => (
                        <li key={i} className="text-sm text-zinc-600">
                          · {p}
                        </li>
                      ))}
                    </ul>
                    <p className="text-xs text-blue-600 italic">
                      {sec.copy_suggestion}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Reviews */}
        {activeTab === "reviews" && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              评论聚类分析 ({report.review_clusters.length})
            </h2>
            <div className="space-y-4">
              {report.review_clusters.map((cluster) => (
                <div
                  key={cluster.id}
                  className="p-5 bg-white border border-zinc-200 rounded-xl"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="font-semibold text-zinc-900">
                        {cluster.cluster_name}
                      </h3>
                      <span className="text-xs px-2 py-0.5 rounded bg-zinc-100 text-zinc-600">
                        {cluster.problem_type}
                      </span>
                    </div>
                    <span className="text-sm text-zinc-500">
                      {cluster.review_count}条 ({Math.round(cluster.ratio * 100)}%)
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm mb-3">
                    <div>
                      <span className="font-medium text-zinc-700">
                        用户担忧：
                      </span>
                      <span className="text-zinc-600">{cluster.user_concern}</span>
                    </div>
                    <div>
                      <span className="font-medium text-zinc-700">
                        商业影响：
                      </span>
                      <span className="text-zinc-600">{cluster.business_impact}</span>
                    </div>
                  </div>
                  <div className="mb-3">
                    <span className="font-medium text-sm text-zinc-700">
                      建议行动：
                    </span>
                    <span className="text-sm text-zinc-600">
                      {cluster.suggested_action}
                    </span>
                  </div>
                  <div>
                    <p className="text-xs font-medium text-zinc-500 mb-1">
                      代表性评论
                    </p>
                    {cluster.representative_reviews.map((r, i) => (
                      <p
                        key={i}
                        className="text-xs text-zinc-500 italic border-l-2 border-zinc-200 pl-2 mb-1"
                      >
                        &ldquo;{r}&rdquo;
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* FAQ */}
            <h2 className="text-lg font-semibold text-zinc-800 mt-8 mb-4">
              优化FAQ ({report.faq_items.length})
            </h2>
            <div className="space-y-2">
              {report.faq_items.map((faq, i) => (
                <div
                  key={i}
                  className="p-4 bg-white border border-zinc-200 rounded-xl"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-zinc-500">{faq.type}</span>
                    <span
                      className={`text-xs px-2 py-0.5 rounded border ${
                        RISK_COLORS[faq.risk_level] || "text-zinc-600 bg-zinc-50 border-zinc-200"
                      }`}
                    >
                      {faq.risk_level === "high"
                        ? "高风险"
                        : faq.risk_level === "medium"
                        ? "中风险"
                        : "低风险"}
                    </span>
                    <span className="text-xs text-zinc-400">
                      来源：{faq.source}
                    </span>
                  </div>
                  <p className="font-medium text-sm text-zinc-900 mb-1">
                    Q: {faq.question}
                  </p>
                  <p className="text-sm text-zinc-600">A: {faq.answer}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Ads */}
        {activeTab === "ads" && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              广告素材建议 ({report.ad_material_suggestions.length})
            </h2>
            <div className="space-y-4">
              {report.ad_material_suggestions.map((ad, i) => (
                <div
                  key={i}
                  className="p-5 bg-white border border-zinc-200 rounded-xl"
                >
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-sm font-semibold text-blue-600">
                      {ad.angle}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded bg-zinc-100 text-zinc-600">
                      {ad.target_user}
                    </span>
                  </div>
                  <p className="text-sm font-medium text-zinc-900 mb-3">
                    Hook: {ad.hook}
                  </p>
                  <ul className="space-y-1 mb-3">
                    {ad.script_structure.map((s, j) => (
                      <li key={j} className="text-sm text-zinc-600">
                        {j + 1}. {s}
                      </li>
                    ))}
                  </ul>
                  <div className="text-xs space-y-1">
                    <p className="text-zinc-500">
                      落地页要求：{ad.landing_page_requirement}
                    </p>
                    {ad.risk_note && (
                      <p className="text-amber-600">风险提示：{ad.risk_note}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Weekly Report */}
        {activeTab === "weekly" && report.weekly_report && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              周报数据
            </h2>
            <div className="p-5 bg-white border border-zinc-200 rounded-xl mb-4">
              <h3 className="font-semibold text-zinc-900 mb-2">总结</h3>
              <p className="text-sm text-zinc-600">
                {report.weekly_report.summary}
              </p>
            </div>
            {report.weekly_report.metrics_change.length > 0 && (
              <div className="p-5 bg-white border border-zinc-200 rounded-xl mb-4">
                <h3 className="font-semibold text-zinc-900 mb-2">
                  指标变化
                </h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-zinc-200">
                        <th className="text-left py-2 px-3 text-zinc-500 font-medium">
                          指标
                        </th>
                        <th className="text-right py-2 px-3 text-zinc-500 font-medium">
                          上周
                        </th>
                        <th className="text-right py-2 px-3 text-zinc-500 font-medium">
                          本周
                        </th>
                        <th className="text-right py-2 px-3 text-zinc-500 font-medium">
                          变化
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.weekly_report.metrics_change.map(
                        (m, i) => {
                          const sentiment = m.sentiment || "neutral";
                          const changeColor =
                            sentiment === "positive"
                              ? "text-green-600"
                              : sentiment === "negative"
                              ? "text-red-600"
                              : "text-zinc-500";
                          const changeDisplay =
                            m.change && m.change !== "-"
                              ? m.change
                              : "-";
                          return (
                            <tr
                              key={i}
                              className="border-b border-zinc-100"
                            >
                              <td className="py-2 px-3 text-zinc-700">
                                {String(m.metric || "")}
                              </td>
                              <td className="py-2 px-3 text-right text-zinc-600">
                                {String(m.last_week ?? "-")}
                              </td>
                              <td className="py-2 px-3 text-right text-zinc-600">
                                {String(m.this_week ?? "-")}
                              </td>
                              <td
                                className={`py-2 px-3 text-right font-medium ${changeColor}`}
                              >
                                {changeDisplay}
                              </td>
                            </tr>
                          );
                        }
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-5 bg-white border border-zinc-200 rounded-xl">
                <h3 className="font-semibold text-zinc-900 mb-2">
                  现存问题
                </h3>
                <ul className="space-y-1">
                  {report.weekly_report.problems.map((p, i) => (
                    <li key={i} className="text-sm text-red-600">
                      - {p}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-5 bg-white border border-zinc-200 rounded-xl">
                <h3 className="font-semibold text-zinc-900 mb-2">
                  下周行动
                </h3>
                <ul className="space-y-1">
                  {report.weekly_report.next_week_actions.map((a, i) => (
                    <li key={i} className="text-sm text-blue-600">
                      → {a}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Markdown */}
        {activeTab === "markdown" && (
          <div>
            <h2 className="text-lg font-semibold text-zinc-800 mb-4">
              完整报告 (Markdown)
            </h2>
            <div className="p-6 bg-white border border-zinc-200 rounded-xl">
              <pre className="text-xs text-zinc-700 whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto max-h-[70vh] overflow-y-auto">
                {markdown}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

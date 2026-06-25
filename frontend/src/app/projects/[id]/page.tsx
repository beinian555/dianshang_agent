"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { use } from "react";
import Link from "next/link";
import {
  getProject,
  importCSV,
  runAnalysis,
  getAnalysisJob,
  type Project,
  type ImportResult,
  type AnalysisJob,
} from "@/lib/api";

const IMPORT_TYPES = [
  { key: "product" as const, label: "商品数据 (product.csv)" },
  { key: "competitors" as const, label: "竞品数据 (competitors.csv)" },
  { key: "reviews" as const, label: "评论数据 (reviews.csv)" },
  { key: "metrics" as const, label: "运营数据 (metrics.csv)" },
];

export default function ProjectDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [results, setResults] = useState<Record<string, ImportResult>>({});
  const [uploading, setUploading] = useState<string | null>(null);
  const [job, setJob] = useState<AnalysisJob | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadProject = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getProject(id);
      setProject(data);
    } catch {
      setError("项目不存在");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadProject();
  }, [loadProject]);

  async function handleImport(type: (typeof IMPORT_TYPES)[number]["key"], file: File) {
    try {
      setUploading(type);
      const result = await importCSV(id, type, file);
      setResults((prev) => ({ ...prev, [type]: result }));
      await loadProject();
    } catch {
      setError(`导入 ${type} 失败`);
    } finally {
      setUploading(null);
    }
  }

  function stopPolling() {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }

  useEffect(() => {
    return () => stopPolling();
  }, []);

  async function handleAnalyze() {
    try {
      setError("");
      const newJob = await runAnalysis(id);
      setJob(newJob);

      pollingRef.current = setInterval(async () => {
        try {
          const updated = await getAnalysisJob(newJob.id);
          setJob(updated);
          if (updated.status === "completed") {
            stopPolling();
            await loadProject();
          } else if (updated.status === "failed") {
            stopPolling();
            setError(updated.error_message || "分析失败");
          }
        } catch {
          stopPolling();
          setError("查询分析状态失败");
        }
      }, 2000);
    } catch {
      setError("启动分析失败");
    }
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <p className="text-zinc-500">加载中...</p>
      </div>
    );
  }

  if (error && !project) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="p-5 bg-red-50 border border-red-200 text-red-700 rounded-xl">
          {error}
        </div>
        <Link href="/" className="text-blue-600 text-sm mt-4 inline-block">
          ← 返回项目列表
        </Link>
      </div>
    );
  }

  if (!project) return null;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <Link href="/" className="text-sm text-blue-600 hover:underline mb-4 inline-block">
        ← 返回项目列表
      </Link>

      <div className="flex items-start justify-between mt-2 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-zinc-900">{project.name}</h1>
          <p className="text-sm text-zinc-500 mt-1">
            {project.category} · {project.platform} · 创建于{" "}
            {new Date(project.created_at).toLocaleString("zh-CN")}
          </p>
        </div>
        <span
          className={`text-xs px-2 py-1 rounded-full ${
            project.status === "created"
              ? "bg-zinc-100 text-zinc-600"
              : project.status === "data_loaded"
              ? "bg-blue-100 text-blue-700"
              : "bg-green-100 text-green-700"
          }`}
        >
          {project.status === "created"
            ? "已创建"
            : project.status === "data_loaded"
            ? "数据已导入"
            : project.status === "analyzed"
            ? "已分析"
            : project.status}
        </span>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* CSV Import Section */}
      <section className="mb-8">
        <h2 className="text-lg font-semibold text-zinc-800 mb-4">导入数据</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {IMPORT_TYPES.map(({ key, label }) => {
            const isDone = key === "product" ? !!project.product : key === "competitors" ? project.competitors && project.competitors.length > 0 : key === "reviews" ? project.reviews && project.reviews.length > 0 : project.weekly_metrics && Object.keys(project.weekly_metrics).length > 0;
            const result = results[key];
            return (
              <div
                key={key}
                className={`p-4 border rounded-xl bg-white ${
                  isDone
                    ? "border-green-300 bg-green-50"
                    : "border-zinc-200"
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  {isDone && (
                    <svg
                      className="w-4 h-4 text-green-600"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  )}
                  <span className="text-sm font-medium text-zinc-700">
                    {label}
                  </span>
                </div>
                <input
                  type="file"
                  accept=".csv"
                  disabled={uploading === key}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleImport(key, file);
                  }}
                  className="text-xs text-zinc-500 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
                />
                {uploading === key && (
                  <p className="text-xs text-blue-600 mt-1">导入中...</p>
                )}
                {result && (
                  <div className="mt-2 text-xs text-zinc-600">
                    成功 {result.success_count} · 失败 {result.failed_count}
                    {result.warnings.length > 0 && (
                      <span className="text-amber-600">
                        {" "}
                        · {result.warnings.length} 警告
                      </span>
                    )}
                    {result.errors.length > 0 && (
                      <span className="text-red-600">
                        {" "}
                        · {result.errors.length} 错误
                      </span>
                    )}
                    {result.warnings.length > 0 && (
                      <ul className="mt-2 space-y-1 text-amber-700">
                        {result.warnings.slice(0, 3).map((warning, index) => (
                          <li key={`warning-${index}`}>警告：{warning}</li>
                        ))}
                      </ul>
                    )}
                    {result.errors.length > 0 && (
                      <ul className="mt-2 space-y-1 text-red-700">
                        {result.errors.slice(0, 3).map((error, index) => (
                          <li key={`error-${index}`}>错误：{error}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* Product Preview */}
      {project.product && (
        <section className="mb-8 p-5 bg-white border border-zinc-200 rounded-xl">
          <h2 className="text-lg font-semibold text-zinc-800 mb-3">
            商品信息
          </h2>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div>
              <span className="text-zinc-500">标题：</span>
              {project.product.title}
            </div>
            <div>
              <span className="text-zinc-500">品牌：</span>
              {project.product.brand || "-"}
            </div>
            <div>
              <span className="text-zinc-500">价格：</span>
              {project.product.price != null ? `¥${project.product.price}` : "-"}
            </div>
            <div>
              <span className="text-zinc-500">SKU：</span>
              {project.product.sku_name || "-"}
            </div>
            <div className="col-span-2">
              <span className="text-zinc-500">卖点：</span>
              {project.product.selling_points.join(" · ") || "-"}
            </div>
          </div>
        </section>
      )}

      {/* Analysis */}
      <section className="mb-8">
        {job && job.status !== "completed" && job.status !== "failed" ? (
          <div className="p-5 bg-white border border-blue-200 rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-blue-700">
                {job.current_step || "分析中..."}
              </span>
              <span className="text-sm text-blue-600">{job.progress}%</span>
            </div>
            <div className="w-full bg-blue-100 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${job.progress}%` }}
              />
            </div>
            <p className="text-xs text-zinc-500 mt-2">
              分析在后台运行，页面可以关闭，完成后报告将出现在下方
            </p>
          </div>
        ) : job?.status === "failed" ? (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
            <p className="text-sm text-red-700">分析失败</p>
            {job.error_message && (
              <p className="text-xs text-red-500 mt-1">{job.error_message}</p>
            )}
            <button
              onClick={handleAnalyze}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700"
            >
              重新分析
            </button>
          </div>
        ) : (
          <div>
            <button
              onClick={handleAnalyze}
              disabled={!project.product}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-sm"
            >
              运行增长分析
            </button>
            {!project.product && (
              <p className="text-xs text-zinc-500 mt-2">
                请先导入商品数据后才能运行分析
              </p>
            )}
          </div>
        )}
      </section>

      {/* Reports */}
      {project.reports && project.reports.length > 0 && (
        <section>
          <h2 className="text-lg font-semibold text-zinc-800 mb-4">
            分析报告
          </h2>
          <div className="space-y-3">
            {project.reports.map((report) => (
              <Link
                key={report.id}
                href={`/reports/${report.id}`}
                className="block p-4 bg-white border border-zinc-200 rounded-xl hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-zinc-900">
                      增长分析报告
                    </h3>
                    <p className="text-xs text-zinc-500 mt-1">
                      {new Date(report.created_at).toLocaleString("zh-CN")}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-bold text-blue-600">
                      {report.scores.total_score}分
                    </span>
                    <svg
                      className="w-4 h-4 text-zinc-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

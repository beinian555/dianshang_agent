"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  listProjects,
  createProject,
  type Project,
} from "@/lib/api";

export default function HomePage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    category: "beauty_skincare",
    platform: "mock_tmall",
  });
  const [submitting, setSubmitting] = useState(false);

  async function loadProjects() {
    try {
      setLoading(true);
      setError("");
      const data = await listProjects();
      setProjects(data);
    } catch (e) {
      setError("加载项目列表失败，请确认后端已启动");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProjects();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) return;
    try {
      setSubmitting(true);
      await createProject(form);
      setForm({ name: "", category: "beauty_skincare", platform: "mock_tmall" });
      setShowForm(false);
      await loadProjects();
    } catch (e) {
      setError("创建项目失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-zinc-900">项目列表</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
        >
          {showForm ? "取消" : "新建项目"}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {showForm && (
        <form
          onSubmit={handleCreate}
          className="mb-8 p-5 bg-white border border-zinc-200 rounded-xl space-y-4"
        >
          <h2 className="font-semibold text-zinc-800">新建分析项目</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs text-zinc-500 mb-1">
                项目名称
              </label>
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="例如：防晒霜增长分析"
                className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1">品类</label>
              <select
                value={form.category}
                onChange={(e) => setForm({ ...form, category: e.target.value })}
                className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="beauty_skincare">美妆护肤</option>
                <option value="sunscreen">防晒</option>
                <option value="foundation">粉底液/气垫</option>
              </select>
            </div>
            <div>
              <label className="block text-xs text-zinc-500 mb-1">平台</label>
              <select
                value={form.platform}
                onChange={(e) => setForm({ ...form, platform: e.target.value })}
                className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm"
              >
                <option value="mock_tmall">天猫</option>
                <option value="mock_jd">京东</option>
                <option value="mock_douyin">抖音</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={submitting || !form.name.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {submitting ? "创建中..." : "创建项目"}
          </button>
        </form>
      )}

      {loading ? (
        <p className="text-zinc-500 text-sm">加载中...</p>
      ) : projects.length === 0 ? (
        <div className="text-center py-16 text-zinc-500">
          <p className="text-lg mb-2">暂无项目</p>
          <p className="text-sm">
            点击「新建项目」开始分析商品增长潜力
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {projects.map((p) => (
            <Link
              key={p.id}
              href={`/projects/${p.id}`}
              className="block p-5 bg-white border border-zinc-200 rounded-xl hover:border-blue-300 hover:shadow-sm transition-all"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-zinc-900">{p.name}</h3>
                  <p className="text-xs text-zinc-500 mt-1">
                    {p.category} · {p.platform} ·{" "}
                    {new Date(p.created_at).toLocaleString("zh-CN")}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      p.status === "created"
                        ? "bg-zinc-100 text-zinc-600"
                        : p.status === "data_loaded"
                        ? "bg-blue-100 text-blue-700"
                        : "bg-green-100 text-green-700"
                    }`}
                  >
                    {p.status === "created"
                      ? "已创建"
                      : p.status === "data_loaded"
                      ? "数据已导入"
                      : p.status === "analyzed"
                      ? "已分析"
                      : p.status}
                  </span>
                  {p.reports && p.reports.length > 0 && (
                    <span className="text-xs text-zinc-500">
                      {p.reports.length} 份报告
                    </span>
                  )}
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
      )}
    </div>
  );
}

const API_BASE = "/api";

export interface Project {
  id: string;
  name: string;
  category: string;
  platform: string;
  product?: Product | null;
  competitors?: CompetitorProduct[];
  reviews?: Review[];
  weekly_metrics?: Record<string, WeeklyMetrics>;
  reports?: AnalysisReport[];
  created_at: string;
  status: string;
}

export interface Product {
  id: string;
  platform: string;
  category: string;
  url: string;
  title: string;
  brand?: string;
  price?: number;
  original_price?: number;
  sku_name?: string;
  specs: string[];
  main_image_texts: string[];
  detail_sections: string[];
  selling_points: string[];
  ingredients: string[];
  target_users: string[];
  usage_scenarios: string[];
}

export interface CompetitorProduct {
  id: string;
  product_id: string;
  url: string;
  title: string;
  brand?: string;
  price?: number;
  sales_hint?: string;
  rating?: number;
  review_count?: number;
  selling_points: string[];
  main_image_texts: string[];
  detail_sections: string[];
  promotions: string[];
  weakness_hints: string[];
}

export interface Review {
  id: string;
  product_id: string;
  source: string;
  rating: number;
  content: string;
  tags: string[];
}

export interface WeeklyMetrics {
  impressions: number;
  clicks: number;
  ctr: number;
  orders: number;
  conversion_rate: number;
  refund_rate: number;
  ad_spend: number;
  revenue: number;
  roi: number;
}

export interface ImportResult {
  project_id: string;
  import_type: string;
  success_count: number;
  failed_count: number;
  warnings: string[];
  errors: string[];
  preview: Record<string, string>[];
}

export interface ScoreDimension {
  score: number;
  reason: string;
  evidence: string[];
}

export interface Scores {
  title_search: ScoreDimension;
  main_image_click: ScoreDimension;
  detail_conversion: ScoreDimension;
  competitor_diff: ScoreDimension;
  review_risk: ScoreDimension;
  review_health: ScoreDimension;
  ad_landing: ScoreDimension;
  total_score: number;
}

export interface CompetitorInsight {
  competitor_id: string;
  positioning: string;
  main_selling_points: string[];
  strengths: string[];
  weaknesses: string[];
  learnable_points: string[];
  avoid_points: string[];
}

export interface TitleSuggestion {
  type: string;
  title: string;
  reason: string;
  risk_note: string;
}

export interface ImageCopySuggestion {
  image_no: number;
  goal: string;
  visual_focus: string;
  main_copy: string;
  sub_copy: string;
  notes: string;
}

export interface DetailPageSection {
  section_no: number;
  section_name: string;
  goal: string;
  content_points: string[];
  copy_suggestion: string;
}

export interface ReviewCluster {
  id: string;
  cluster_name: string;
  problem_type: string;
  review_count: number;
  ratio: number;
  representative_reviews: string[];
  user_concern: string;
  business_impact: string;
  suggested_action: string;
}

export interface FAQItem {
  question: string;
  answer: string;
  type: string;
  risk_level: string;
  source: string;
}

export interface AdMaterialSuggestion {
  angle: string;
  target_user: string;
  hook: string;
  script_structure: string[];
  landing_page_requirement: string;
  risk_note: string;
}

export interface MetricsChangeEntry {
  metric: string;
  key: string;
  last_week: string | number;
  this_week: string | number;
  change: string;
  sentiment: "positive" | "negative" | "neutral";
}

export interface WeeklyReportData {
  summary: string;
  metrics_change: MetricsChangeEntry[];
  problems: string[];
  next_week_actions: string[];
  risk_notes: string[];
}

export interface AnalysisReport {
  id: string;
  product_id: string;
  status: string;
  summary: string;
  scores: Scores;
  competitor_insights: CompetitorInsight[];
  title_suggestions: TitleSuggestion[];
  image_copy_suggestions: ImageCopySuggestion[];
  detail_page_structure: DetailPageSection[];
  review_clusters: ReviewCluster[];
  faq_items: FAQItem[];
  ad_material_suggestions: AdMaterialSuggestion[];
  weekly_report: WeeklyReportData | null;
  markdown_report: string;
  created_at: string;
}

export interface AnalysisJob {
  id: string;
  project_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  current_step: string | null;
  report_id: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

// Projects
export async function listProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function getProject(id: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects/${id}`);
  if (!res.ok) throw new Error("Project not found");
  return res.json();
}

export async function createProject(data: {
  name: string;
  category: string;
  platform: string;
}): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create project");
  return res.json();
}

// Import
export async function importCSV(
  projectId: string,
  type: "product" | "competitors" | "reviews" | "metrics",
  file: File
): Promise<ImportResult> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(
    `${API_BASE}/projects/${projectId}/import/${type}`,
    { method: "POST", body: formData }
  );
  if (!res.ok) throw new Error(`Failed to import ${type}`);
  return res.json();
}

// Analysis
export async function runAnalysis(projectId: string): Promise<AnalysisJob> {
  const res = await fetch(`${API_BASE}/projects/${projectId}/analysis`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to run analysis");
  return res.json();
}

export async function getAnalysisJob(jobId: string): Promise<AnalysisJob> {
  const res = await fetch(`${API_BASE}/analysis-jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

// Reports
export async function getReport(reportId: string): Promise<AnalysisReport> {
  const res = await fetch(`${API_BASE}/reports/${reportId}`);
  if (!res.ok) throw new Error("Report not found");
  return res.json();
}

export async function getReportMarkdown(
  reportId: string
): Promise<{ filename: string; content: string }> {
  const res = await fetch(`${API_BASE}/reports/${reportId}/markdown`);
  if (!res.ok) throw new Error("Markdown not found");
  return res.json();
}

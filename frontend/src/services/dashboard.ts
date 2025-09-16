// src/services/dashboard.ts
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

function authHeader() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export type Metrics = {
  week_start: string;
  journal_entries: number;
  calendar_syncs: number;
  chat_queries: number;
  notes_syncs: number;
};

export async function fetchMetrics() {
  const res = await axios.get(`${API_URL}/api/dashboard/metrics`, { headers: authHeader() });
  return res.data as Metrics;
}

// New in Phase 2
export type SeriesPoint = { t: string; counts: Record<string, number> };
export type SeriesPayload = {
  bucket: "day" | "hour";
  from: string;
  to: string;
  points: SeriesPoint[];
};

export type Streaks = { current: number; best: number };

export type Summary = {
  from: string;
  to: string;
  totals: { journal_entries: number; chat_queries: number; calendar_syncs: number; notes_syncs: number };
  streaks: Streaks;
};

export async function fetchSeries(params?: { from?: string; to?: string; bucket?: "day" | "hour"; events?: string[] }) {
  const search = new URLSearchParams();
  if (params?.from) search.set("from", params.from);
  if (params?.to) search.set("to", params.to);
  if (params?.bucket) search.set("bucket", params.bucket);
  if (params?.events && params.events.length) search.set("events", params.events.join(","));
  const qs = search.toString();
  const url = `${API_URL}/api/dashboard/series${qs ? `?${qs}` : ""}`;
  const res = await axios.get(url, { headers: authHeader() });
  return res.data as SeriesPayload;
}

export async function fetchStreaks() {
  const res = await axios.get(`${API_URL}/api/dashboard/streaks`, { headers: authHeader() });
  return res.data as Streaks;
}

export async function fetchSummary(windowDays = 7) {
  const res = await axios.get(`${API_URL}/api/dashboard/summary`, {
    headers: authHeader(),
    params: { window: windowDays },
  });
  return res.data as Summary;
}

export type ReflectionResult = {
  summary: string;
  prompts: string[];
  actions: string[];
};

export async function fetchReflection(userGoals?: string): Promise<ReflectionResult> {
  const res = await axios.post(
    `${API_URL}/api/dashboard/reflection`,
    { user_goals: userGoals || "" },
    { headers: { ...authHeader(), "Content-Type": "application/json" } }
  );
  return res.data.result as ReflectionResult;
}

// ---- Phase 4 additions ----
export type HeatmapPoint = { date: string; count: number };
export type HeatmapPayload = { from: string; to: string; points: HeatmapPoint[] };

export async function fetchHeatmap(params?: { window?: number; event?: string }) {
  const search = new URLSearchParams();
  if (params?.window) search.set("window", String(params.window));
  if (params?.event) search.set("event", params.event);
  const url = `${API_URL}/api/dashboard/heatmap${search.toString() ? `?${search.toString()}` : ""}`;
  const res = await axios.get(url, { headers: authHeader() });
  return res.data as HeatmapPayload;
}

// JSON export (returns parsed object)
export async function exportDashboardJson(opts: {
  window?: number;
  include?: string[]; // ["series","streaks"]
  bucket?: "day" | "hour";
  events?: string[]; // ["journal_create", ...]
}) {
  const search = new URLSearchParams();
  search.set("format", "json");
  if (opts.window) search.set("window", String(opts.window));
  if (opts.include?.length) search.set("include", opts.include.join(","));
  if (opts.bucket) search.set("bucket", opts.bucket);
  if (opts.events?.length) search.set("events", opts.events.join(","));
  const url = `${API_URL}/api/dashboard/export?${search.toString()}`;
  const res = await axios.get(url, { headers: authHeader() });
  return res.data;
}

// CSV export (returns Blob)
export async function exportDashboardCsv(opts: {
  window?: number;
  include?: string[];
  bucket?: "day" | "hour";
  events?: string[];
}) {
  const search = new URLSearchParams();
  search.set("format", "csv");
  if (opts.window) search.set("window", String(opts.window));
  if (opts.include?.length) search.set("include", opts.include.join(","));
  if (opts.bucket) search.set("bucket", opts.bucket);
  if (opts.events?.length) search.set("events", opts.events.join(","));
  const url = `${API_URL}/api/dashboard/export?${search.toString()}`;
  const res = await axios.get(url, { headers: authHeader(), responseType: "blob" });
  return res.data as Blob;
}

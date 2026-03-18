import type {
  AnalysisCreateResponse,
  AnalysisResponse,
  HistoryItem,
  ReportResponse,
  ScoredTerm,
  TrendTerm,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchJSON<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export async function startAnalysis(
  keyword: string
): Promise<AnalysisCreateResponse> {
  return fetchJSON("/api/analysis/", {
    method: "POST",
    body: JSON.stringify({ keyword }),
  });
}

export async function getAnalysis(jobId: string): Promise<AnalysisResponse> {
  return fetchJSON(`/api/analysis/${jobId}`);
}

export async function getTrends(jobId: string): Promise<TrendTerm[]> {
  return fetchJSON(`/api/analysis/${jobId}/trends`);
}

export async function getScores(jobId: string): Promise<ScoredTerm[]> {
  return fetchJSON(`/api/analysis/${jobId}/scores`);
}

export async function getReport(jobId: string): Promise<ReportResponse> {
  return fetchJSON(`/api/analysis/${jobId}/report`);
}

export async function getHistory(
  limit = 20,
  offset = 0
): Promise<HistoryItem[]> {
  return fetchJSON(`/api/history/?limit=${limit}&offset=${offset}`);
}

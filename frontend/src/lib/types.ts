export type AnalysisStatus =
  | "pending"
  | "fetching"
  | "scoring"
  | "generating"
  | "completed"
  | "failed";

export interface TrendTerm {
  title: string;
  score: number;
  num_comments: number;
  upvote_ratio: number;
  comment_velocity: number;
  subreddit: string;
  created_utc: number;
  post_url: string;
  source: string;
}

export interface ScoredTerm {
  title: string;
  opportunity_score: number;
  popularity_score: number;
  engagement_score: number;
  sentiment_signal: number;
  commercial_intent: number;
  recommendation: string;
  upvotes: number;
  num_comments: number;
  comment_velocity: number;
  upvote_ratio: number;
  subreddit: string;
  post_url: string;
  source: string;
}

export interface AnalysisResponse {
  job_id: string;
  keyword: string;
  status: AnalysisStatus;
  created_at: string;
  completed_at: string | null;
  trending_terms: TrendTerm[] | null;
  scored_terms: ScoredTerm[] | null;
  final_report: string | null;
  error: string | null;
}

export interface AnalysisCreateResponse {
  job_id: string;
  status: AnalysisStatus;
}

export interface ReportResponse {
  job_id: string;
  keyword: string;
  created_at: string;
  report: string;
}

export interface HistoryItem {
  job_id: string;
  keyword: string;
  status: AnalysisStatus;
  created_at: string;
  completed_at: string | null;
  top_score: number | null;
}

export interface WsMessage {
  stage: string;
  progress: number;
  error?: string;
}

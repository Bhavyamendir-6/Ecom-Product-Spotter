from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    FETCHING = "fetching"
    SCORING = "scoring"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# --- Request schemas ---


class AnalysisRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200)


# --- Response schemas ---


class AnalysisCreateResponse(BaseModel):
    job_id: str
    status: AnalysisStatus


class TrendTermResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    score: int
    num_comments: int
    upvote_ratio: float
    comment_velocity: float
    subreddit: str
    created_utc: float
    post_url: str
    source: str


class ScoredTermResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    opportunity_score: float
    popularity_score: float
    engagement_score: float
    sentiment_signal: float
    commercial_intent: float
    recommendation: str
    upvotes: int
    num_comments: int
    comment_velocity: float
    upvote_ratio: float
    subreddit: str
    post_url: str
    source: str


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    keyword: str
    status: AnalysisStatus
    created_at: datetime
    completed_at: datetime | None = None
    trending_terms: list[TrendTermResponse] | None = None
    scored_terms: list[ScoredTermResponse] | None = None
    final_report: str | None = None
    error: str | None = None


class ReportResponse(BaseModel):
    job_id: str
    keyword: str
    created_at: datetime
    report: str


class HistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    keyword: str
    status: AnalysisStatus
    created_at: datetime
    completed_at: datetime | None = None
    top_score: float | None = None

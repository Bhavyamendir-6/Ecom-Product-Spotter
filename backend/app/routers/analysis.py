import asyncio
import json

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.exceptions import AnalysisNotFoundError, AnalysisNotReadyError
from app.models.schemas import (
    AnalysisCreateResponse,
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    ReportResponse,
    ScoredTermResponse,
    TrendTermResponse,
)
from app.services.analysis import (
    create_analysis,
    get_analysis,
    run_pipeline,
)

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/", response_model=AnalysisCreateResponse, status_code=201)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    job_id = await create_analysis(db, request.keyword)
    background_tasks.add_task(
        run_pipeline, job_id, request.keyword, AsyncSessionLocal
    )
    return AnalysisCreateResponse(
        job_id=job_id, status=AnalysisStatus.PENDING
    )


@router.get("/{job_id}", response_model=AnalysisResponse)
async def get_analysis_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis(db, job_id)
    if not analysis:
        raise AnalysisNotFoundError(job_id)

    trending = None
    if analysis.trending_terms_json:
        trending = json.loads(analysis.trending_terms_json)

    scored = None
    if analysis.scored_terms_json:
        scored = json.loads(analysis.scored_terms_json)

    return AnalysisResponse(
        job_id=analysis.id,
        keyword=analysis.keyword,
        status=analysis.status,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        trending_terms=trending,
        scored_terms=scored,
        final_report=analysis.final_report,
        error=analysis.error,
    )


@router.get("/{job_id}/trends", response_model=list[TrendTermResponse])
async def get_trends(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis(db, job_id)
    if not analysis:
        raise AnalysisNotFoundError(job_id)
    if not analysis.trending_terms_json:
        raise AnalysisNotReadyError(job_id, analysis.status)
    return json.loads(analysis.trending_terms_json)


@router.get("/{job_id}/scores", response_model=list[ScoredTermResponse])
async def get_scores(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis(db, job_id)
    if not analysis:
        raise AnalysisNotFoundError(job_id)
    if not analysis.scored_terms_json:
        raise AnalysisNotReadyError(job_id, analysis.status)
    return json.loads(analysis.scored_terms_json)


@router.get("/{job_id}/report", response_model=ReportResponse)
async def get_report(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    analysis = await get_analysis(db, job_id)
    if not analysis:
        raise AnalysisNotFoundError(job_id)
    if not analysis.final_report:
        raise AnalysisNotReadyError(job_id, analysis.status)
    return ReportResponse(
        job_id=analysis.id,
        keyword=analysis.keyword,
        created_at=analysis.created_at,
        report=analysis.final_report,
    )

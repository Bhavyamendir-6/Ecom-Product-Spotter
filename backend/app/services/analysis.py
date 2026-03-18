import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.db import Analysis
from app.models.schemas import AnalysisStatus
from app.services.ws_manager import manager

logger = logging.getLogger(__name__)

_semaphore: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        settings = get_settings()
        _semaphore = asyncio.Semaphore(settings.max_concurrent_analyses)
    return _semaphore


async def create_analysis(db: AsyncSession, keyword: str) -> str:
    """Create a new analysis record and return the job_id."""
    job_id = str(uuid.uuid4())
    analysis = Analysis(
        id=job_id,
        keyword=keyword,
        status=AnalysisStatus.PENDING,
    )
    db.add(analysis)
    await db.commit()
    return job_id


async def run_pipeline(job_id: str, keyword: str, db_factory):
    """Run the full analysis pipeline as a background task.

    Updates DB status at each stage and broadcasts WebSocket messages.
    """
    sem = _get_semaphore()
    async with sem:
        async with db_factory() as db:
            try:
                await _update_status(db, job_id, AnalysisStatus.FETCHING)
                await manager.broadcast(
                    job_id, {"stage": "fetching", "progress": 20}
                )

                from app.services.trends import fetch_trends

                trending = await fetch_trends(keyword)
                trending_json = json.dumps(trending)

                analysis = await _get_analysis(db, job_id)
                analysis.trending_terms_json = trending_json
                await db.commit()

                await _update_status(db, job_id, AnalysisStatus.SCORING)
                await manager.broadcast(
                    job_id, {"stage": "scoring", "progress": 50}
                )

                from app.services.scorer import score_terms

                scored = await score_terms(trending)
                scored_json = json.dumps(scored)

                analysis = await _get_analysis(db, job_id)
                analysis.scored_terms_json = scored_json
                await db.commit()

                await _update_status(db, job_id, AnalysisStatus.GENERATING)
                await manager.broadcast(
                    job_id, {"stage": "generating", "progress": 75}
                )

                from app.services.report import generate_report

                report = await generate_report(keyword, scored)

                analysis = await _get_analysis(db, job_id)
                analysis.final_report = report
                analysis.status = AnalysisStatus.COMPLETED
                analysis.completed_at = datetime.now(timezone.utc)
                await db.commit()

                await manager.broadcast(
                    job_id, {"stage": "completed", "progress": 100}
                )
                logger.info("Pipeline completed for job %s", job_id)

            except Exception as e:
                logger.error("Pipeline failed for job %s: %s", job_id, str(e))
                try:
                    analysis = await _get_analysis(db, job_id)
                    analysis.status = AnalysisStatus.FAILED
                    analysis.error = str(e)
                    await db.commit()
                except Exception:
                    logger.error("Failed to update error status for %s", job_id)

                await manager.broadcast(
                    job_id,
                    {"stage": "failed", "progress": 0, "error": str(e)},
                )


async def get_analysis(db: AsyncSession, job_id: str) -> Analysis | None:
    """Fetch an analysis by job_id."""
    result = await db.execute(select(Analysis).where(Analysis.id == job_id))
    return result.scalar_one_or_none()


async def list_analyses(
    db: AsyncSession, limit: int = 20, offset: int = 0
) -> list[Analysis]:
    """List analyses ordered by creation date."""
    result = await db.execute(
        select(Analysis)
        .order_by(Analysis.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def _get_analysis(db: AsyncSession, job_id: str) -> Analysis:
    result = await db.execute(select(Analysis).where(Analysis.id == job_id))
    return result.scalar_one()


async def _update_status(
    db: AsyncSession, job_id: str, status: AnalysisStatus
):
    analysis = await _get_analysis(db, job_id)
    analysis.status = status
    await db.commit()

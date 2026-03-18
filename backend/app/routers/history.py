import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.schemas import HistoryItem
from app.services.analysis import list_analyses

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=list[HistoryItem])
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    analyses = await list_analyses(db, limit=limit, offset=offset)
    items = []
    for a in analyses:
        top_score = None
        if a.scored_terms_json:
            scored = json.loads(a.scored_terms_json)
            if scored:
                top_score = max(s["opportunity_score"] for s in scored)

        items.append(
            HistoryItem(
                job_id=a.id,
                keyword=a.keyword,
                status=a.status,
                created_at=a.created_at,
                completed_at=a.completed_at,
                top_score=top_score,
            )
        )
    return items

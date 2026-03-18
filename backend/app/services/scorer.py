import asyncio
import json
import logging

from app.services.fake_context import FakeToolContext

logger = logging.getLogger(__name__)


async def score_terms(trending_terms: list[dict]) -> list[dict]:
    """Score trending terms by e-commerce opportunity.

    Wraps the existing score_opportunities tool.
    """
    from sub_agents.opportunity_scorer.tools.score_opportunities import (
        score_opportunities,
    )

    ctx = FakeToolContext()
    terms_json = json.dumps(trending_terms)
    result = await asyncio.to_thread(score_opportunities, terms_json, ctx)

    logger.info("score_terms result status: %s", result.get("status"))

    raw = ctx.state.get("scored_terms", "[]")
    scored = json.loads(raw) if isinstance(raw, str) else raw
    return scored

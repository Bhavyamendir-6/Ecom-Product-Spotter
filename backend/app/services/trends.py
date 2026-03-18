import asyncio
import json
import logging

from app.services.fake_context import FakeToolContext

logger = logging.getLogger(__name__)


async def fetch_trends(keyword: str) -> list[dict]:
    """Fetch trending Reddit posts for a keyword.

    Wraps the existing fetch_rising_trends tool in asyncio.to_thread
    since it uses blocking HTTP calls and time.sleep.
    """
    from sub_agents.trends_fetcher.tools.fetch_trends import fetch_rising_trends

    ctx = FakeToolContext()
    result = await asyncio.to_thread(fetch_rising_trends, keyword, ctx)

    logger.info("fetch_trends result status: %s", result.get("status"))

    raw = ctx.state.get("trending_terms", "[]")
    terms = json.loads(raw) if isinstance(raw, str) else raw
    return terms

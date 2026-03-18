import json
import logging
from typing import List, Dict, Any

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

COMMERCIAL_KEYWORDS: List[str] = [
    "buy", "best", "price", "review", "cheap", "deal", "discount",
    "sale", "shop", "order", "online", "store", "free shipping",
    "coupon", "affordable", "premium", "top", "rated", "compare",
    "wholesale", "bulk",
]


def _compute_commercial_intent(term: str) -> float:
    """Score commercial intent based on presence of commercial keywords."""
    term_lower = term.lower()
    matches = sum(1 for kw in COMMERCIAL_KEYWORDS if kw in term_lower)
    return min(matches / 3.0, 1.0)


def _compute_keyword_relevance(title: str, keyword: str) -> float:
    """Score how well the post title matches the search keyword (0–1).

    Full phrase match → 1.0. Partial word match → proportional score.
    No match → 0.0 (applied as a multiplier to penalise off-topic posts).
    """
    if not keyword:
        return 1.0
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    if keyword_lower in title_lower:
        return 1.0
    words = [w for w in keyword_lower.split() if len(w) > 2]
    if not words:
        return 1.0
    matches = sum(1 for w in words if w in title_lower)
    return round(matches / len(words), 3)


def _get_recommendation(score: float) -> str:
    """Return recommendation based on opportunity score."""
    if score >= 0.75:
        return "High opportunity - act now"
    elif score >= 0.50:
        return "Moderate opportunity - worth exploring"
    elif score >= 0.25:
        return "Low opportunity - monitor trends"
    else:
        return "Minimal opportunity - skip for now"


def score_opportunities(trending_terms_json: str, tool_context: ToolContext) -> dict:
    """Score trending Reddit posts by e-commerce opportunity.

    Reads trending posts and computes an opportunity score for each based on
    popularity (upvotes), engagement (comment velocity), sentiment (upvote
    ratio), and commercial intent (keyword matching). Results are ranked
    and stored in state for report generation.

    Args:
        trending_terms_json: JSON string of trending posts from Reddit.
        tool_context: ADK tool context for state access.

    Returns:
        Dictionary with status and scored post data.
    """
    try:
        if isinstance(trending_terms_json, list):
            terms = trending_terms_json
        else:
            terms = json.loads(trending_terms_json)
            # Handle double-encoded JSON from LLM
            if isinstance(terms, str):
                try:
                    terms = json.loads(terms)
                except json.JSONDecodeError:
                    pass

        if not isinstance(terms, list):
            logger.warning(f"Expected list of dicts, got: {type(terms)}")
            terms = []

    except (json.JSONDecodeError, TypeError) as e:
        logger.warning("Invalid trending_terms_json input: %s", str(e))
        tool_context.state["scored_terms"] = json.dumps([])
        return {
            "status": "error",
            "message": "Invalid input: could not parse trending terms JSON."
        }

    if not terms:
        tool_context.state["scored_terms"] = json.dumps([])
        return {
            "status": "success",
            "message": "No terms to score.",
            "data": "[]"
        }

    # Read the original search keyword from state to compute relevance
    keyword = tool_context.state.get("user_keyword", "")

    # Normalize upvotes and comment_velocity across the batch
    max_upvotes = max((t.get("score", 0) for t in terms), default=1)
    if max_upvotes == 0:
        max_upvotes = 1

    max_velocity = max((t.get("comment_velocity", 0) for t in terms), default=1)
    if max_velocity == 0:
        max_velocity = 1

    scored: List[Dict[str, Any]] = []
    for t in terms:
        upvotes = t.get("score", 0)
        num_comments = t.get("num_comments", 0)
        upvote_ratio = t.get("upvote_ratio", 0.5)
        comment_velocity = t.get("comment_velocity", 0)
        title = t.get("title", "")

        # Normalized scores (0-1)
        popularity_score = upvotes / max_upvotes
        engagement_score = comment_velocity / max_velocity
        sentiment_signal = upvote_ratio  # Already 0-1
        commercial_intent = _compute_commercial_intent(title)
        keyword_relevance = _compute_keyword_relevance(title, keyword)

        # Weighted base score, then scaled by keyword relevance so off-topic
        # posts (relevance=0) are zeroed out and partially relevant posts are
        # penalised proportionally.
        base_score = (
            0.30 * popularity_score
            + 0.25 * engagement_score
            + 0.20 * sentiment_signal
            + 0.25 * commercial_intent
        )
        opportunity_score = round(base_score * keyword_relevance, 3)

        scored.append({
            "title": title,
            "opportunity_score": opportunity_score,
            "popularity_score": round(popularity_score, 3),
            "engagement_score": round(engagement_score, 3),
            "sentiment_signal": round(sentiment_signal, 3),
            "commercial_intent": round(commercial_intent, 3),
            "upvotes": upvotes,
            "num_comments": num_comments,
            "comment_velocity": comment_velocity,
            "upvote_ratio": upvote_ratio,
            "subreddit": t.get("subreddit", ""),
            "post_url": t.get("post_url", ""),
            "source": t.get("source", "unknown"),
            "recommendation": _get_recommendation(opportunity_score),
        })

    scored.sort(key=lambda x: x["opportunity_score"], reverse=True)

    tool_context.state["scored_terms"] = json.dumps(scored)

    logger.info("Scored %d posts", len(scored))

    return {
        "status": "success",
        "message": f"Scored {len(scored)} posts by e-commerce opportunity.",
        "data": json.dumps(scored)
    }

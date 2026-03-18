import json
import os
import logging
import time
import urllib.request
import urllib.parse
from typing import List, Dict

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

# Subreddits focused on products, deals, and e-commerce
DEFAULT_SUBREDDITS = [
    "shutupandtakemymoney",
    "BuyItForLife",
    "gadgets",
    "AmazonTopRated",
    "deals",
    "ProductPorn",
    "ecommerce",
]

# Maximum posts to return after deduplication
MAX_RESULTS = 25

def _get_headers():
    return {
        "User-Agent": os.getenv("REDDIT_USER_AGENT", "ecommerce_product_spotter/1.0 (Public API Fetcher)")
    }
def _is_title_relevant(title: str, keyword: str) -> bool:
    """Return True if the keyword (or its significant words) appear in the title."""
    title_lower = title.lower()
    keyword_lower = keyword.lower()
    if keyword_lower in title_lower:
        return True
    # For multi-word keywords, accept if any significant word (>3 chars) matches
    words = [w for w in keyword_lower.split() if len(w) > 3]
    return bool(words) and any(w in title_lower for w in words)


def _search_subreddit(subreddit_name: str, keyword: str, limit: int = 10) -> List[dict]:
    """Search a single subreddit for posts matching the keyword using public JSON."""
    results = []
    try:
        query = urllib.parse.quote(keyword)
        url = f"https://www.reddit.com/r/{subreddit_name}/search.json?q={query}&sort=relevance&t=month&limit={limit}&restrict_sr=on"
        req = urllib.request.Request(url, headers=_get_headers())
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                title = post.get("title", "")

                # Only keep posts where the keyword is reflected in the title
                if not _is_title_relevant(title, keyword):
                    continue

                now = time.time()
                created_utc = post.get("created_utc", now)
                hours_since_posted = max((now - created_utc) / 3600.0, 0.1)
                num_comments = post.get("num_comments", 0)
                comment_velocity = round(num_comments / hours_since_posted, 3)

                results.append({
                    "title": title,
                    "score": post.get("score", 0),
                    "num_comments": num_comments,
                    "upvote_ratio": post.get("upvote_ratio", 0.0),
                    "comment_velocity": comment_velocity,
                    "subreddit": subreddit_name,
                    "created_utc": created_utc,
                    "post_url": f"https://reddit.com{post.get('permalink', '')}",
                    "source": "reddit_search",
                })
    except Exception as e:
        logger.warning("Failed to search r/%s: %s", subreddit_name, str(e))

    # Be polite to unauthenticated API rate limits
    time.sleep(1.0)
    return results


def _fetch_hot_posts(subreddit_name: str, keyword: str, limit: int = 15) -> List[dict]:
    """Fetch hot posts from a subreddit and filter by keyword in title only."""
    results = []
    try:
        url = f"https://www.reddit.com/r/{subreddit_name}/hot.json?limit={limit}"
        req = urllib.request.Request(url, headers=_get_headers())
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                title = post.get("title", "")

                # Only match on title — selftext check causes too many false positives
                if _is_title_relevant(title, keyword):
                    now = time.time()
                    created_utc = post.get("created_utc", now)
                    hours_since_posted = max((now - created_utc) / 3600.0, 0.1)
                    num_comments = post.get("num_comments", 0)
                    comment_velocity = round(num_comments / hours_since_posted, 3)

                    results.append({
                        "title": title,
                        "score": post.get("score", 0),
                        "num_comments": num_comments,
                        "upvote_ratio": post.get("upvote_ratio", 0.0),
                        "comment_velocity": comment_velocity,
                        "subreddit": subreddit_name,
                        "created_utc": created_utc,
                        "post_url": f"https://reddit.com{post.get('permalink', '')}",
                        "source": "reddit_hot",
                    })
    except Exception as e:
        logger.warning("Failed to fetch hot from r/%s: %s", subreddit_name, str(e))

    # Be polite to unauthenticated API rate limits
    time.sleep(1.0)
    return results


def _merge_and_deduplicate(all_posts: List[dict]) -> List[dict]:
    """Deduplicate posts by URL, keeping the one with higher score."""
    seen: Dict[str, dict] = {}
    for post in all_posts:
        key = post["post_url"]
        if key not in seen or post["score"] > seen[key]["score"]:
            seen[key] = post

    merged = list(seen.values())
    # Sort by score (upvotes) descending, then by comment_velocity
    merged.sort(
        key=lambda r: (r.get("score", 0), r.get("comment_velocity", 0)),
        reverse=True,
    )
    return merged[:MAX_RESULTS]


def fetch_rising_trends(keyword: str, tool_context: ToolContext) -> dict:
    """Fetch trending product mentions from Reddit using its public JSON API.

    Searches across product-focused subreddits for posts matching the
    keyword, combining search results and hot posts. Returns deduplicated
    results sorted by engagement.

    Args:
        keyword: Product category or search keyword (e.g., "mechanical keyboard").
        tool_context: ADK tool context for state access.

    Returns:
        Dictionary with status and trending post data.
    """
    try:
        all_posts: List[dict] = []

        for sub_name in DEFAULT_SUBREDDITS:
            search_posts = _search_subreddit(sub_name, keyword, limit=10)
            hot_posts = _fetch_hot_posts(sub_name, keyword, limit=15)
            all_posts.extend(search_posts)
            all_posts.extend(hot_posts)

        logger.info(
            "Reddit returned %d raw posts for keyword='%s' across %d subreddits",
            len(all_posts), keyword, len(DEFAULT_SUBREDDITS),
        )

        merged = _merge_and_deduplicate(all_posts)

        if not merged:
            tool_context.state["trending_terms"] = json.dumps([])
            return {
                "status": "success",
                "message": f"No Reddit posts found for '{keyword}'. Try a broader keyword like 'headphones', 'laptop', or 'gaming'.",
                "data": "[]",
            }

        tool_context.state["trending_terms"] = json.dumps(merged, default=str)

        return {
            "status": "success",
            "message": (
                f"Found {len(merged)} trending posts for '{keyword}' "
                f"across {len(DEFAULT_SUBREDDITS)} subreddits."
            ),
            "data": json.dumps(merged, default=str),
        }

    except Exception as e:
        logger.error("Reddit API query failed: %s", str(e))
        tool_context.state["trending_terms"] = json.dumps([])
        return {
            "status": "error",
            "message": f"Reddit API query failed: {str(e)}",
        }

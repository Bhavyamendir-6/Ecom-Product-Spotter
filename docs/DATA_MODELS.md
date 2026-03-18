# DATA MODELS: ecommerce_product_spotter

## State Schema

All data flows between agents via `tool_context.state`. Values must be serializable (str, int, float, bool, list, dict of primitives).

| Key | Type | Written By | Read By | Description |
|-----|------|-----------|---------|-------------|
| `user_keyword` | `str` | root_agent | trends_fetcher | User's product keyword or category |
| `trending_terms` | `str` (JSON) | trends_fetcher | opportunity_scorer | JSON-serialized list of Reddit post dicts |
| `scored_terms` | `str` (JSON) | opportunity_scorer | report_generator | JSON-serialized list of scored post dicts |
| `final_report` | `str` | report_generator (output_key) | root_agent | Formatted markdown seller report |

---

## Data Structures

### TrendTerm
Represents a single trending Reddit post fetched by `fetch_rising_trends`.

```python
{
    "title": str,            # Post title
    "score": int,            # Reddit upvote score
    "num_comments": int,     # Number of comments
    "upvote_ratio": float,   # Upvote ratio (0.0 - 1.0)
    "comment_velocity": float,  # Comments per hour since posting
    "subreddit": str,        # Source subreddit (e.g., "gadgets")
    "post_url": str,         # Direct URL to the Reddit post
    "source": str            # How post was found: "search" or "hot"
}
```

### ScoredTerm
Represents a Reddit post with e-commerce opportunity scoring applied.

```python
{
    "title": str,                # Post title
    "opportunity_score": float,  # Composite opportunity score (0.0 - 1.0)
    "popularity_score": float,   # Normalized upvote score (0.0 - 1.0)
    "engagement_score": float,   # Normalized comment velocity (0.0 - 1.0)
    "sentiment_signal": float,   # Upvote ratio (0.0 - 1.0)
    "commercial_intent": float,  # Commercial keyword match score (0.0 - 1.0)
    "recommendation": str,       # Action recommendation string
    "subreddit": str,            # Source subreddit
    "post_url": str              # Direct URL to the Reddit post
}
```

---

## Scoring Formula

```
opportunity_score = 0.30 * popularity_score
                  + 0.25 * engagement_score   (comment velocity)
                  + 0.20 * sentiment_signal   (upvote ratio)
                  + 0.25 * commercial_intent  (keyword matching)

Where:
  popularity_score  = post.score / max_score_in_batch
  engagement_score  = post.comment_velocity / max_velocity_in_batch
  sentiment_signal  = post.upvote_ratio  (already 0.0-1.0)
  commercial_intent = count(commercial_keywords in title) / max_possible, capped at 1.0
    commercial_keywords = ["buy", "best", "price", "review", "cheap",
                           "deal", "discount", "sale", "shop", "order",
                           "online", "store", "free shipping", "coupon",
                           "affordable", "premium", "top", "rated",
                           "compare", "wholesale", "bulk"]
```

### Recommendation Thresholds
| Score Range | Recommendation |
|------------|----------------|
| >= 0.75 | "High opportunity — act now" |
| >= 0.50 | "Moderate opportunity — worth exploring" |
| >= 0.25 | "Low opportunity — monitor trends" |
| < 0.25  | "Minimal opportunity — skip for now" |

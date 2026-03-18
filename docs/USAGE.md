# Usage Guide: ecommerce_product_spotter

## Prerequisites

1. Python 3.11+
2. Google AI Studio API key ([get one here](https://aistudio.google.com/apikey))

## Run Modes

### 1. Interactive Web UI (recommended)
```bash
cd Ecommerce_product_spotter
.\.venv\Scripts\activate
adk web .
```
Open http://localhost:8000, select `ecommerce_product_spotter` from the agent dropdown, and start chatting.

### 2. Terminal Mode
```bash
adk run .
```
Type your queries directly in the terminal.

### 3. REST API
```bash
cd ..
adk api_server Ecommerce_product_spotter
```
Send requests to `http://localhost:8000`.

## Sample Prompts

| Prompt | Expected Behavior |
|--------|-------------------|
| "Find trending products in fitness equipment" | Fetches trends, scores, returns report |
| "What's hot in smart home?" | Same pipeline with "smart home" keyword |
| "Show me rising demand for organic skincare in US" | Trends for organic skincare |
| "Trending pet accessories" | Pet accessories trends report |
| "What should I sell in electronics?" | Electronics keyword analysis |

## Expected Output

The agent returns a formatted report like:

```
# E-Commerce Opportunity Report

**Keyword researched**: fitness equipment
**Date**: 2026-03-17
**Posts analyzed**: 25

## Top Opportunities

### 1. Best budget fitness tracker — r/AmazonTopRated
- **Opportunity Score**: 0.85/1.0
- **Popularity Score**: 0.95/1.0
- **Engagement Score**: 0.80/1.0
- **Commercial Intent**: 0.667/1.0
- **Recommendation**: High opportunity — act now
- **Source**: https://reddit.com/r/AmazonTopRated/...

...

## Summary & Action Items
- [actionable recommendations]
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Empty results | Keyword too specific or low Reddit activity | Try a broader keyword (e.g., "fitness" instead of "fitness tracker model X") |
| "No trending posts found" | Keyword too niche or subreddits not active for term | Use broader product categories |
| Agent says "I cannot perform..." | Prompt/tool wiring issue | Check that `.env` has a valid `GOOGLE_API_KEY` |
| Network error during fetch | Reddit API unreachable | Check internet connection; Reddit public API requires no auth |

## FAQ

**Q: Does this cost money?**
A: Reddit's public JSON API is free with no account required. Gemini API has a free tier.

**Q: How recent is the data?**
A: Reddit posts are fetched live — data reflects current activity at the time you run the agent.

**Q: Which subreddits are monitored?**
A: r/shutupandtakemymoney, r/BuyItForLife, r/gadgets, r/AmazonTopRated, r/deals, r/ProductPorn, r/ecommerce.

**Q: What does the opportunity score mean?**
A: It's a weighted composite of popularity (30%), engagement/comment velocity (25%), sentiment/upvote ratio (20%), and commercial intent (25%). Higher = better e-commerce opportunity.

**Q: Can I change the scoring formula?**
A: Yes — edit `sub_agents/opportunity_scorer/tools/score_opportunities.py`. The weights and commercial keywords are configurable.

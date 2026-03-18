# REQUIREMENTS: ecommerce_product_spotter

## 1. Executive Summary

An ADK-based agent that scrapes Reddit's public JSON API across 7 product-focused subreddits to identify posts with trending demand, scores each by e-commerce opportunity (popularity, engagement, sentiment, commercial intent), and returns an actionable seller report as a chat message.

## 2. Functional Requirements

| ID   | Requirement |
|------|-------------|
| FR-1 | Accept a product category or niche keyword from the user via chat |
| FR-2 | Fetch trending Reddit posts from 7 subreddits using the public JSON API |
| FR-3 | Deduplicate and rank posts by score and comment velocity, returning top 25 |
| FR-4 | Score each post by e-commerce opportunity using: popularity, engagement, sentiment signal, and commercial intent |
| FR-5 | Rank posts by opportunity score (descending) |
| FR-6 | Generate a formatted seller report as a chat message containing: top posts, scores, subreddit sources, links, and recommended actions |
| FR-7 | Handle cases where no trending posts are found gracefully |

## 3. Non-Functional Requirements

| Category        | Requirement |
|-----------------|-------------|
| Performance     | Fetch and report generation within 30 seconds |
| Reliability     | Graceful error handling for network failures and empty results |
| Security        | No hardcoded credentials; only `GOOGLE_API_KEY` required |
| Usability       | Simple chat interaction — user provides a keyword, agent returns a report |
| Maintainability | Modular tools, prompts in separate `prompt.py`, clear separation of concerns |

## 4. Data Requirements

- **Input**: Product category or keyword string from user
- **Data Source**: Reddit public JSON API (`reddit.com/r/{subreddit}/search.json` and `/hot.json`) — no authentication required
- **Output**: Formatted text report as a chat message (markdown-style)
- **No persistent storage** — results are ephemeral per conversation

## 5. Agent Architecture

**Pattern: Sequential Pipeline (SequentialAgent)**

```
root_agent (Agent)
  └── demand_pipeline (SequentialAgent)
        ├── trends_fetcher (Agent) — fetches trending Reddit posts
        ├── opportunity_scorer (Agent) — scores and ranks posts by e-commerce opportunity
        └── report_generator (Agent) — formats the final seller report
```

- `trends_fetcher` uses a custom Reddit fetch tool (no external SDKs — plain `requests`)
- `opportunity_scorer` uses a custom scoring tool
- `report_generator` uses LLM to compose the final report from scored data
- Data flows between agents via `tool_context.state` and `output_key`

**Why Sequential**: The workflow is strictly ordered — fetch → score → report. No parallelism needed.

## 6. Integration Requirements

| Integration | Details |
|-------------|---------|
| Reddit API | Public JSON endpoints, no auth required, 1s rate limit between requests |
| Google ADK | Agent framework, `adk web .` for local execution |
| Gemini LLM | `gemini-2.0-flash` for sub-agents, `gemini-2.5-flash` for report generation |

## 7. UI Requirements

- **No custom UI** — agent runs via `adk web .` (built-in ADK chat interface)
- Report is returned as a plain chat message (markdown formatted)
- Must also work with `adk run .` and `adk api_server .`

## 8. Technical Stack

| Component | Choice |
|-----------|--------|
| Language  | Python 3.11+ |
| Framework | Google ADK (`google-adk`) |
| LLM       | `gemini-2.0-flash` (sub-agents), `gemini-2.5-flash` (report) |
| Data Source | Reddit public JSON API (via `requests`) |
| Auth      | `GOOGLE_API_KEY` only — no GCP project or ADC required |

## 9. Testing Requirements

- Unit tests for all custom tools (Reddit fetch, scoring logic, report formatting)
- Integration test verifying agent loads correctly (`adk web`, `adk run`, `adk api_server`)
- ADK eval with test cases for typical queries and edge cases
- Target: 100% code coverage

## 10. Security Requirements

- No hardcoded API keys or credentials
- Only `GOOGLE_API_KEY` required in `.env`
- No sensitive data stored in state
- Reddit API used via public endpoints — no OAuth or tokens

## 11. Out of Scope

- Custom web UI (Streamlit, FastAPI frontend, etc.)
- PDF/file report generation
- GCP deployment (local only)
- Real-time monitoring or scheduled runs
- Price tracking or competitor analysis from external e-commerce APIs
- Historical trend persistence or database storage

## 12. Assumptions & Decisions

| Decision | Rationale |
|----------|-----------|
| Use Reddit public JSON API | No auth required, free, covers 7 product-focused communities with real buyer discussions |
| 7 subreddits | Covers tech, lifestyle, deals, gadgets, and general e-commerce niches |
| Top 25 posts per keyword | Balances completeness with API rate limiting |
| Sequential pipeline over single agent | Clean separation of concerns; each stage is independently testable |
| No GCP / ADC required | Simplest local setup — only a Gemini API key needed |
| `gemini-2.5-flash` for report | Good balance of quality and cost for text generation |

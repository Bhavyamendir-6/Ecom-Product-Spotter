# CLAUDE.md — E-Commerce Product Spotter

## Project Overview

Google ADK agent + full-stack web app that discovers trending product opportunities by scraping Reddit's public JSON API across 7 product-focused subreddits, scoring posts by e-commerce opportunity with keyword relevance filtering, and generating actionable seller reports.

**ADK entry point:** `agent.py`
**Backend entry point:** `backend/app/main.py`
**Frontend:** `frontend/` (Next.js App Router)
**Run with:** `docker-compose up` or manually start backend (port 8000) + frontend (port 3000)
**ADK-only mode:** `adk web .` (opens http://localhost:8000)

---

## Architecture

### Full-Stack (Backend + Frontend)

```
Frontend (Next.js :3000)
  ↕ REST + WebSocket (proxied via next.config.ts rewrites)
Backend (FastAPI :8000)
  ├── Routers: analysis, history, ws
  ├── Services: analysis, trends, scorer, report, ws_manager
  ├── Database: SQLite (data/analyses.db) via SQLAlchemy async
  └── Reuses ADK sub-agents for pipeline logic
```

### ADK Pipeline (standalone or reused by backend)

```
root_agent (ecommerce_product_spotter)
    └── demand_pipeline (SequentialAgent)
            ├── trends_fetcher_agent   → state["trending_terms"]
            ├── opportunity_scorer_agent → state["scored_terms"]
            └── report_generator_agent  → state["final_report"]
```

### Key Files

| File | Purpose |
|---|---|
| `agent.py` | Root agent + pipeline wiring |
| `prompt.py` | Root agent instruction |
| `config.py` | ADK model names (`MODEL`, `MODEL_PRO`) |
| `observability.py` | Logging setup + ADK callbacks |
| `sub_agents/trends_fetcher/` | Reddit fetch tool + agent |
| `sub_agents/opportunity_scorer/` | Scoring tool + agent |
| `sub_agents/report_generator/` | LLM-only report agent |
| `backend/app/main.py` | FastAPI app, lifespan, CORS |
| `backend/app/config.py` | Backend pydantic-settings (`Settings`) |
| `backend/app/database.py` | Async SQLAlchemy engine + session factory |
| `backend/app/routers/analysis.py` | CRUD endpoints + pipeline trigger |
| `backend/app/routers/ws.py` | WebSocket progress broadcast |
| `backend/app/services/analysis.py` | Pipeline orchestration, DB status updates |
| `backend/app/services/trends.py` | Async wrapper for `fetch_rising_trends` |
| `backend/app/services/scorer.py` | Async wrapper for `score_opportunities` |
| `backend/app/services/report.py` | Gemini API report generation |
| `frontend/src/components/` | React components (tables, tooltips, report viewer) |
| `frontend/src/actions/analysis.ts` | Server action to create analysis |
| `frontend/src/lib/api.ts` | Backend API client |
| `frontend/next.config.ts` | Proxy rewrites (`/api/*` → backend) |

### State Keys (passed between agents)

```
user_keyword        → set by root agent
trending_terms      → written by trends_fetcher, read by opportunity_scorer
scored_terms        → written by opportunity_scorer, read by report_generator
final_report        → written by report_generator, read by root agent
```

### Backend Pipeline Stages

```
PENDING → FETCHING (20%) → SCORING (50%) → GENERATING (75%) → COMPLETED (100%)
                                                              → FAILED (on error)
```

Status updates broadcast via WebSocket to connected frontend clients.

---

## Models

| Agent | Model | Env var override |
|---|---|---|
| root_agent, trends_fetcher, opportunity_scorer | `gemini-2.0-flash` | `MODEL` / `GEMINI_MODEL` |
| report_generator | `gemini-2.5-flash` | `MODEL_PRO` / `GEMINI_MODEL_PRO` |

---

## Setup

### Docker (full stack)

```bash
cp backend/.env.example backend/.env   # add GOOGLE_API_KEY
docker-compose up --build
# Frontend: http://localhost:3000   Backend: http://localhost:8000
```

### Manual

```bash
# Backend
cd backend && cp .env.example .env  # add GOOGLE_API_KEY
uvicorn app.main:app --port 8000

# Frontend
cd frontend && cp .env.local.example .env.local
npm install && npm run dev
```

### ADK-only (no frontend/backend)

```bash
cp .env.example .env   # add GOOGLE_API_KEY
pip install -r requirements.txt
adk web .
```

**Required env vars:**

| Scope | Variable | Required | Default |
|-------|----------|----------|---------|
| Backend | `GOOGLE_API_KEY` | Yes | — |
| Backend | `DATABASE_URL` | No | `sqlite+aiosqlite:///./data/analyses.db` |
| Backend | `CORS_ORIGINS` | No | `["http://localhost:3000"]` |
| Backend | `MAX_CONCURRENT_ANALYSES` | No | `3` |
| Backend | `ENVIRONMENT` | No | `development` |
| Frontend | `NEXT_PUBLIC_API_URL` | Yes | `http://localhost:8000` |
| Frontend | `NEXT_PUBLIC_WS_URL` | No | `ws://localhost:8000` |
| Both | `REDDIT_USER_AGENT` | No | `ecommerce_product_spotter/1.0 (Public API Fetcher)` |

---

## Reddit Data Source

The agent scrapes Reddit's public JSON API (no auth required):

**Subreddits monitored:** r/shutupandtakemymoney, r/BuyItForLife, r/gadgets, r/AmazonTopRated, r/deals, r/ProductPorn, r/ecommerce

**Per subreddit:** 10 posts via `/search.json?q=keyword` + 15 posts via `/hot.json`
**Relevance filter:** Only posts where the keyword appears in the **title** are kept (applied to both search and hot results)
**Rate limiting:** 1-second delay between requests
**Output:** Top 25 deduplicated posts sorted by score + comment velocity

---

## Scoring Formula

```
base_score = 0.30 * popularity_score       (normalized upvotes)
           + 0.25 * engagement_score       (comment velocity)
           + 0.20 * sentiment_signal       (upvote ratio)
           + 0.25 * commercial_intent      (commercial keyword matching)

opportunity_score = base_score * keyword_relevance
```

- **keyword_relevance** (0–1): multiplier from `_compute_keyword_relevance()` — checks if the user's search keyword appears in the post title. Full phrase match = 1.0, partial word match = proportional, no match = 0.0 (zeroes out irrelevant posts).
- **Recommendations:** ≥0.75 = High, ≥0.50 = Moderate, ≥0.25 = Low, <0.25 = Minimal

---

## Report Format

The report generator uses a structured markdown template producing:
1. **Header table** — keyword, date, post count
2. **Opportunity Rankings** — ranked summary table of all posts
3. **Detailed Breakdown** — top 5 posts with per-metric tables
4. **Key Takeaways** — numbered insights
5. **Action Items for Sellers** — 3 concrete recommendations
6. **Market Insight** — demand landscape analysis

Reports are rendered in the frontend via `ReactMarkdown` with GFM support.

---

## Frontend Features

- **Search form** with keyword input → creates analysis via server action
- **Real-time progress** via WebSocket (`use-ws-progress` hook)
- **Trends table** with raw Reddit data
- **Scores table** with sortable columns
- **Column tooltips** — hover over any column header (`ColumnTooltip` component) to see its definition and how it's calculated (black background, white text popover)
- **Report viewer** with markdown rendering and copy-to-clipboard
- **History page** listing past analyses

---

## Testing

```bash
# Mocked unit/integration tests (no API keys needed) — default
pytest tests/ -v --cov=. --cov-fail-under=100 -m "not live"

# All tests including live (requires real API keys)
pytest tests/ -v

# Coverage HTML report
pytest tests/ -v --cov=. --cov-report=html -m "not live"
```

**Test files:**

| File | What it covers |
|---|---|
| `tests/test_agent.py` | Root agent config, model, tools, callbacks |
| `tests/test_sub_agents.py` | All 3 sub-agent initializations |
| `tests/test_tools.py` | fetch_rising_trends, score_opportunities, helpers |
| `tests/test_observability.py` | Logging, model/agent callbacks, timing |
| `tests/test_integration.py` | State flow, ADK load, pipeline structure |
| `tests/test_import_paths.py` | sys.path robustness across run contexts |
| `tests/conftest.py` | Shared fixtures (mock_tool_context, sample_trending_terms) |

**Coverage target:** 100% (enforced by `--cov-fail-under=100`)

**ADK eval:**
```bash
adk eval . eval/basic_flow.test.json
```

---

## Adding a New Sub-Agent

1. Create `sub_agents/<name>/agent.py` and `sub_agents/<name>/tools.py`
2. Add agent to `demand_pipeline` list in `agent.py`
3. Define a new state key for its output
4. Add tests in `tests/test_sub_agents.py` and `tests/test_tools.py`
5. Update `docs/ARCHITECTURE.md` and `docs/DATA_MODELS.md`

---

## Important Conventions

- All tools receive `tool_context` as second argument and read/write state via `tool_context.state`
- Sub-agent output keys use suffix `_output` (e.g., `trending_terms_output`) — the LLM writes these; the tools write the actual state keys directly
- The report_generator has **no tools** — it reads `scored_terms` from state and generates the report via LLM only
- The opportunity_scorer reads `user_keyword` from `tool_context.state` to compute keyword relevance
- Tests mock `requests.get` / `urllib.request.urlopen` for Reddit calls — never make live Reddit calls in unit tests
- Use `@pytest.mark.live` for any test requiring real API/LLM access
- The backend reuses ADK sub-agent tools/prompts via async wrappers in `backend/app/services/`
- Frontend server components need `NEXT_PUBLIC_API_URL` set to the backend URL (relative URLs don't go through Next.js rewrites in server components)

---

## Docs

| Doc | Content |
|---|---|
| `docs/ARCHITECTURE.md` | System diagram, agent hierarchy, state flow |
| `docs/DATA_MODELS.md` | Full schema for TrendTerm, ScoredTerm, state keys |
| `docs/DESIGN.md` | Agent/tool design decisions, error handling |
| `docs/TESTING.md` | How to run tests, add new tests, CI/CD example |
| `docs/TEST_STRATEGY.md` | Mocking strategy, coverage targets |
| `docs/REQUIREMENTS.md` | Functional/non-functional requirements, out-of-scope |

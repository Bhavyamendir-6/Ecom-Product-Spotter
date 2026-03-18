# E-Commerce Product Demand Spotter

An ADK-based agent that scans Reddit's product-focused subreddits to discover trending product mentions, scores them by e-commerce opportunity, and generates an actionable seller report — served through a Next.js frontend and FastAPI backend.

## Quick Start

### Option 1: Docker (recommended)

```bash
cd Ecommerce_product_spotter
cp backend/.env.example backend/.env   # add GOOGLE_API_KEY
docker-compose up --build
# Frontend at http://localhost:3000
# Backend API at http://localhost:8000
```

### Option 2: Manual

```bash
# Backend
cd backend
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r ../requirements.txt
cp .env.example .env            # add GOOGLE_API_KEY
uvicorn app.main:app --port 8000

# Frontend (new terminal)
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
# Open http://localhost:3000
```

### Option 3: ADK CLI only (no web UI)

```bash
cd Ecommerce_product_spotter
pip install -r requirements.txt
cp .env.example .env            # add GOOGLE_API_KEY
adk web .                       # http://localhost:8000 (ADK UI)
# or: adk run .                 # terminal mode
```

## Features

- Scan 7 product-focused subreddits (r/shutupandtakemymoney, r/BuyItForLife, r/gadgets, r/AmazonTopRated, r/deals, r/ProductPorn, r/ecommerce)
- **Title-based relevance filtering** — only posts where the keyword appears in the title are included, eliminating off-topic noise
- Score posts by e-commerce opportunity (popularity, engagement, sentiment, commercial intent, keyword relevance)
- Generate structured seller reports with ranked tables, detailed breakdowns, and actionable recommendations
- **Interactive column tooltips** — hover over any table column header to see its definition and calculation method
- Full-stack web UI (Next.js + FastAPI) with real-time WebSocket progress updates
- Background pipeline execution with status tracking (Pending → Fetching → Scoring → Generating → Completed)
- Analysis history page
- Also runs standalone via `adk web`, `adk run`, or `adk api_server`

## Configuration

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google AI Studio API key for Gemini |
| `REDDIT_USER_AGENT` | No | Custom user agent (default: `ecommerce_product_spotter/1.0 (Public API Fetcher)`) |
| `GEMINI_MODEL` | No | Model override (default: `gemini-2.0-flash`) |
| `GEMINI_MODEL_PRO` | No | Pro model override (default: `gemini-2.5-flash`) |
| `DATABASE_URL` | No | SQLite URL (default: `sqlite+aiosqlite:///./data/analyses.db`) |
| `CORS_ORIGINS` | No | Allowed origins (default: `["http://localhost:3000"]`) |
| `MAX_CONCURRENT_ANALYSES` | No | Pipeline concurrency limit (default: `3`) |
| `ENVIRONMENT` | No | Environment mode: development, staging, or production (default: `development`) |

### Frontend (`frontend/.env.local`)

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Yes | Backend API URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_WS_URL` | No | WebSocket URL (default: `ws://localhost:8000`) |

### ADK mode (root `.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key |
| `REDDIT_USER_AGENT` | No | Custom Reddit UA |
| `MODEL` | No | Model override for ADK agents |
| `MODEL_PRO` | No | Pro model override for report generator |

*Note: This project uses Reddit's public, unauthenticated JSON feeds (`.json`), so you do NOT need a Reddit API key.*

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (Next.js :3000)                                │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ SearchForm │ │ Trends   │ │ Scores   │ │ Report   │  │
│  │            │ │ Table    │ │ Table    │ │ Viewer   │  │
│  └────────────┘ └──────────┘ └──────────┘ └──────────┘  │
│      ↕ REST + WebSocket (proxied via next.config.ts)     │
├──────────────────────────────────────────────────────────┤
│  Backend (FastAPI :8000)                                 │
│  ┌─────────┐  ┌────────────────────────────────────┐     │
│  │ Routers │→ │ Services (analysis, trends,        │     │
│  │ (REST,  │  │ scorer, report, ws_manager)        │     │
│  │  WS)    │  └────────────────────────────────────┘     │
│  └─────────┘           ↕                                 │
│  ┌─────────────────────────────────────────────────┐     │
│  │ ADK Sub-Agents (reused from root ADK pipeline)  │     │
│  │ trends_fetcher → opportunity_scorer → report_gen │     │
│  └─────────────────────────────────────────────────┘     │
│      ↕ SQLite (data/analyses.db)                         │
├──────────────────────────────────────────────────────────┤
│  External: Reddit Public JSON API (no auth)              │
│  External: Google Gemini API (report generation)         │
└──────────────────────────────────────────────────────────┘
```

### ADK Pipeline (also used standalone)

```
root_agent (ecommerce_product_spotter)
    └── demand_pipeline (SequentialAgent)
            ├── trends_fetcher_agent   → state["trending_terms"]
            ├── opportunity_scorer_agent → state["scored_terms"]
            └── report_generator_agent  → state["final_report"]
```

| Agent | Model | Role |
|-------|-------|------|
| `root_agent` | gemini-2.0-flash | Gathers keyword, delegates to pipeline, returns report |
| `trends_fetcher` | gemini-2.0-flash | Queries Reddit for trending product mentions |
| `opportunity_scorer` | gemini-2.0-flash | Scores posts by e-commerce opportunity |
| `report_generator` | gemini-2.5-flash | Formats the final seller report |

## Scoring Formula

```
base_score = 0.30 × popularity       (normalized upvotes)
           + 0.25 × engagement       (comment velocity)
           + 0.20 × sentiment        (upvote ratio)
           + 0.25 × commercial_intent (keyword matching)

opportunity_score = base_score × keyword_relevance
```

- **keyword_relevance** (0–1): multiplier based on whether the search keyword appears in the post title — off-topic posts are zeroed out
- **Recommendations:** ≥0.75 = High, ≥0.50 = Moderate, ≥0.25 = Low, <0.25 = Minimal

## Example Prompts

- "Find trending products in mechanical keyboards"
- "What's trending in smart home devices?"
- "Show me rising demand for headphones"
- "I'm looking for new tech accessories to sell. Check rising trends for 'phone'"

## Running Tests

```bash
# Mocked tests (no API key needed)
pytest tests/ -v --cov=. --cov-fail-under=100 -m "not live"

# All tests (requires API key in .env)
pytest tests/ -v

# ADK eval
adk eval . eval/basic_flow.test.json
```

## Project Structure

```
Ecommerce_product_spotter/
├── agent.py                  # Root ADK agent + pipeline wiring
├── prompt.py                 # Root agent instructions
├── config.py                 # ADK model configuration
├── observability.py          # Logging + ADK callbacks
├── sub_agents/
│   ├── trends_fetcher/       # Reddit trends fetching (public JSON API)
│   │   ├── agent.py
│   │   ├── prompt.py
│   │   └── tools/fetch_trends.py
│   ├── opportunity_scorer/   # E-commerce scoring logic
│   │   ├── agent.py
│   │   ├── prompt.py
│   │   └── tools/score_opportunities.py
│   └── report_generator/     # Report formatting (LLM-only)
│       ├── agent.py
│       └── prompt.py
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py           # App entry, lifespan, CORS
│   │   ├── config.py         # pydantic-settings config
│   │   ├── database.py       # SQLAlchemy async engine
│   │   ├── exceptions.py     # Custom exception handlers
│   │   ├── models/
│   │   │   ├── db.py         # Analysis SQLAlchemy model
│   │   │   └── schemas.py    # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── analysis.py   # CRUD + pipeline trigger
│   │   │   ├── history.py    # Analysis history list
│   │   │   └── ws.py         # WebSocket progress updates
│   │   └── services/
│   │       ├── analysis.py   # Pipeline orchestration + DB ops
│   │       ├── trends.py     # Async wrapper for fetch_rising_trends
│   │       ├── scorer.py     # Async wrapper for score_opportunities
│   │       ├── report.py     # Gemini API report generation
│   │       └── ws_manager.py # WebSocket broadcast manager
│   └── .env.example
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   │   ├── page.tsx      # Home / search
│   │   │   └── (dashboard)/
│   │   │       ├── analysis/[jobId]/  # Analysis detail + sub-pages
│   │   │       └── history/           # Past analyses
│   │   ├── components/
│   │   │   ├── search-form.tsx
│   │   │   ├── analysis-progress.tsx
│   │   │   ├── trend-table.tsx
│   │   │   ├── score-table.tsx
│   │   │   ├── score-badge.tsx
│   │   │   ├── report-viewer.tsx       # Markdown report renderer
│   │   │   └── column-tooltip.tsx      # Hover tooltips for column defs
│   │   ├── hooks/
│   │   │   ├── use-analysis.ts
│   │   │   └── use-ws-progress.ts
│   │   ├── actions/analysis.ts         # Server action for creating analysis
│   │   └── lib/
│   │       ├── api.ts                  # Backend API client
│   │       ├── types.ts                # TypeScript interfaces
│   │       └── utils.ts
│   ├── next.config.ts        # API proxy rewrites
│   └── .env.local.example
├── tests/                    # Test suite (100% coverage target)
├── eval/                     # ADK evaluation files
├── docs/                     # Architecture & design docs
├── docker-compose.yml        # Full-stack Docker setup
└── requirements.txt          # Python dependencies
```

## License

MIT

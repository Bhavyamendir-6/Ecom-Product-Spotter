# Conversation Log: ecommerce_product_spotter

**Session Date**: 2026-03-13
**Assistant Platform**: Claude Code
**Use Case Source**: inline prompt
**Use Case Summary**: Build an E-Commerce Product Demand Spotter using Google ADK that queries BigQuery's public Google Trends dataset to find rising search terms, scores them by e-commerce opportunity, and generates an actionable seller report.

---

## Phase 0: Session Initialization & Repo Setup

### Interaction Summary
User requested building an "E-Commerce Product Demand Spotter" using Google ADK in Python. The agent should:
1. Query BigQuery's public Google Trends dataset to find search terms with rising demand
2. Score those terms by e-commerce opportunity
3. Generate an actionable seller report

Agent name inferred from working directory: `ecommerce_product_spotter`

### Decisions Made
- **Agent name**: `ecommerce_product_spotter` — matches the existing directory name and follows snake_case convention
- **Use case source**: inline prompt from user conversation

### Learnings
- Project starts from scratch (empty directory)
- Will need BigQuery integration (google-cloud-bigquery) and report generation capabilities

---

## Phase 1: Discovery & Requirements

### Interaction Summary
User confirmed:
- Use case already described inline (BigQuery Google Trends → scoring → seller report)
- Tech stack: Python + Google ADK + Gemini (default accepted)
- Output format: Simple text report returned as a chat message (no PDF/file)
- Auth: Application Default Credentials (gcloud auth)
- Deployment: Local only (`adk web .`)
- UI: No custom UI — use adk web's built-in chat interface only

### Decisions Made
- **Sequential pipeline architecture**: trends_fetcher → opportunity_scorer → report_generator — clean separation, each stage independently testable
- **No custom UI**: User explicitly said "no ui and simple report reply as message"
- **`international_top_terms` table**: Broader coverage than US-only; can filter by country
- **`gemini-2.5-flash` for report generation**: Good quality/cost balance for text output
- **`gemini-2.0-flash` for sub-agents**: Default stable model for simpler tasks

### Learnings
- User prefers minimal setup — no extra UI frameworks, no deployment complexity
- Report as chat message keeps the agent simple and focused

---

## Phase 2: Project Setup

### Interaction Summary
Created full ADK-compliant project structure with sub_agents/, tools/, tests/, eval/, docs/ directories. Set up .venv with all dependencies (google-adk, google-cloud-bigquery, pytest, etc.). Collected API keys from user. Validated Gemini API key successfully. GCP project ID set to `jabdjhbdhbds`.

### Decisions Made
- **Virtual environment**: Local `.venv/` inside agent repo, gitignored
- **Dependencies**: google-adk, google-genai, google-cloud-bigquery, python-dotenv, pydantic, pytest, pytest-asyncio, pytest-cov
- **API keys**: Gemini key validated successfully; GCP project ID provided for BigQuery

### Learnings
- Gemini API key is valid and working
- BigQuery queries will require valid ADC or service account auth at runtime

---

## Phase 3: Architecture & Design

### Interaction Summary
Designed a Conversational + Sequential Pipeline architecture. Root agent gathers keyword via chat, delegates to a 3-stage SequentialAgent pipeline (trends_fetcher → opportunity_scorer → report_generator). Created ARCHITECTURE.md, DESIGN.md, DATA_MODELS.md, and DECISIONS.md.

### Decisions Made
- **ADR-001**: Sequential pipeline — workflow is strictly ordered, no parallelism needed
- **ADR-002**: Conversational root + AgentTool delegation — enables natural conversation before pipeline
- **ADR-003**: BigQuery public dataset — official, stable, free (up to 1TB/month)
- **ADR-004**: JSON-serialized strings in state — ADK state requires primitives
- **ADR-005**: gemini-2.0-flash for sub-agents, gemini-2.5-flash for report generation
- **ADR-006**: No custom UI — adk web only, as user requested

### Learnings
- Tool mixing prohibition (Rule 6) not an issue here — no Google built-in tools used, only custom BigQuery tool
- Report generator needs no tools — pure LLM generation from state data

---

## Phase 4: Core Implementation

### Interaction Summary
Implemented all agents, tools, prompts, config, and observability. Validated all three run modes (adk web, adk run, adk api_server) — all start without import errors.

### Files Created/Updated
- `config.py` — model env vars
- `observability.py` — logging + callbacks with ContextVar stacks
- `prompt.py` — root agent instruction
- `agent.py` — root agent + SequentialAgent pipeline + AgentTool wiring
- `sub_agents/trends_fetcher/` — agent.py, prompt.py, tools/fetch_trends.py
- `sub_agents/opportunity_scorer/` — agent.py, prompt.py, tools/score_opportunities.py
- `sub_agents/report_generator/` — agent.py, prompt.py (no tools, LLM-only)

### Decisions Made
- **Dual-context imports**: try/except pattern in all agent.py files for adk web vs adk run compatibility
- **sys.path insertion**: All sub-agent agent.py files add project root to sys.path
- **Observability**: ContextVar-based stacks for model/agent timing (avoids callback_context identity issues)

### Learnings
- Port-in-use errors during validation are acceptable — import success is the key metric
- All three ADK run modes validated successfully

---

## Phase 5: Testing & Validation

### Interaction Summary
Created comprehensive test suite with 82 tests across 6 test files. Achieved 100% application code coverage. All run modes re-validated.

### Decisions Made
- **Removed tests/__init__.py**: Prevents pytest from treating tests as a subpackage, avoiding double-import of agent.py
- **Double-import guard in agent.py**: Detects if module already loaded under alternate name (agent vs Ecommerce_product_spotter.agent) to prevent SequentialAgent parent conflict
- **.coveragerc excludes**: `except ImportError` and `sys.path` conditional branches excluded — these are ADK structural requirements validated by run mode tests, not coverable in single process
- **No live tests by default**: All tests run with mocked BigQuery client

### Learnings
- ADK SequentialAgent assigns parent to sub-agents; re-creating pipeline with same sub-agents causes ValidationError
- Python treats `agent` and `Ecommerce_product_spotter.agent` as separate modules, requiring import guard
- Windows file locks on log files during tempdir cleanup — use manual cleanup with handler closing

---

## Phase 6: Documentation

### Interaction Summary
Generated all documentation: README.md, USAGE.md, TESTING.md, DEPLOYMENT.md. Final validation confirmed 82 tests passing at 100% coverage and all docs present.

### Files Created
- `README.md` — quick start, features, architecture, usage
- `docs/USAGE.md` — detailed usage, sample prompts, troubleshooting, FAQ
- `docs/TESTING.md` — test guide, mocking strategy, CI/CD config
- `docs/DEPLOYMENT.md` — local deployment, environment variables

---

## Session Summary

### Architecture Patterns Used
- Conversational + Sequential Pipeline (root Agent → SequentialAgent → 3 LlmAgent stages)
- AgentTool delegation for pipeline invocation
- State-based data flow (JSON-serialized strings in tool_context.state)

### Key Technical Decisions
- gemini-2.0-flash for sub-agents (cost-effective), gemini-2.5-flash for report generation (better text quality)
- BigQuery public dataset for trends data (official, free, stable)
- Double-import guard in agent.py for ADK dual-context compatibility
- ContextVar-based stacks for observability timing

### Reusable Patterns Discovered
- Double-import guard pattern for ADK agents using SequentialAgent (prevents parent conflict)
- .coveragerc exclusions for ADK `except ImportError` structural branches
- Removing tests/__init__.py to prevent pytest package auto-import
- Windows-safe logging test pattern (explicit handler cleanup)

### All Issues & Resolutions
1. SequentialAgent parent conflict during testing → double-import guard in agent.py
2. Windows PermissionError on tempdir log files → manual handler close before cleanup
3. sys.path/ImportError branches uncoverable in single process → .coveragerc exclusions

### Recommendations for Future Sessions
- Run `adk eval` with live API key to validate LLM behavior end-to-end
- Run `pytest tests/ -v` without `-m "not live"` to include live Reddit + LLM tests
- Consider adding `@pytest.mark.live` tests for full pipeline validation

---

## Phase 7: Repurposing (BigQuery to Reddit API)

### Interaction Summary
User requested to pivot the project away from BigQuery Google Trends and "repurpose" it with another idea. We chose to use the Reddit API (via PRAW) to find trending product mentions across product-focused subreddits (r/shutupandtakemymoney, r/BuyItForLife, etc.).

### Decisions Made
- **Data Source**: Replaced `google-cloud-bigquery` with `praw` (Python Reddit API Wrapper).
- **Subreddits**: Hardcoded a list of 7 product/deal-focused default subreddits to scan.
- **Data Gathering**: Used both `subreddit.search()` and `subreddit.hot()` to fetch diverse signals, computing a `comment_velocity` custom metric.
- **Scoring Pivot**: Replaced BigQuery's `percent_gained` with Reddit metrics: Upvotes (Popularity), Comment Velocity (Engagement), and Upvote Ratio (Sentiment).
- **Environment**: Replaced `GOOGLE_CLOUD_PROJECT` with `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET`.

### Learnings
- **Tool Swapping**: ADK's sequential pipeline design made this extremely easy; only the fetch and score tools needed internal rewrites. The architecture, testing framework, and core prompt structures remained identical.
- **Coverage Noise**: Extra local python scripts (`cov_check.py`) placed in the root directory break `--cov=.` 100% assertions. Always delete temporary `.py` files before running the strict test suite.

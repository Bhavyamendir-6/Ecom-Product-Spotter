# DECISIONS: ecommerce_product_spotter

## ADR-001: Sequential Pipeline Architecture
**Status**: Accepted
**Context**: The workflow is strictly ordered — fetch trends, then score, then report. No steps can run in parallel since each depends on the previous.
**Decision**: Use `SequentialAgent` wrapping three LlmAgent sub-agents, delegated from a conversational root_agent via `AgentTool`.
**Rationale**: SequentialAgent provides deterministic execution order without LLM overhead for orchestration. The root Agent handles conversation and delegation naturally. Simpler than hierarchical routing since the flow is always the same.
**Consequences**: Adding a parallel research step later would require restructuring. Acceptable since the current use case is inherently sequential.

## ADR-002: Conversational Root + Pipeline Delegation
**Status**: Accepted
**Context**: The agent needs to gather a keyword from the user before processing. A pure SequentialAgent cannot converse.
**Decision**: Root agent is a conversational `Agent` that wraps the `SequentialAgent` pipeline as an `AgentTool`.
**Rationale**: This pattern (Conversational + Pipeline from ADK patterns) lets the root agent gather missing info, validate input, and present the final report naturally. The pipeline runs only when triggered.
**Consequences**: Slightly more complex than a single SequentialAgent, but enables proper conversation handling.

## ADR-003: Reddit Public JSON API for Trends
**Status**: Accepted
**Context**: Need trending product data. Options: Google Trends API (unofficial, rate-limited), Reddit public JSON API (no auth, real buyer discussions), web scraping (fragile).
**Decision**: Use Reddit's public JSON API (`/search.json`, `/hot.json`) across 7 product-focused subreddits.
**Rationale**: No authentication required, free to use, covers real buyer discussions in communities like r/BuyItForLife, r/gadgets, r/shutupandtakemymoney. Captures commercial intent naturally from post titles and engagement metrics.
**Consequences**: Data reflects Reddit community activity, not global search volume. Rate limiting (1 req/sec) keeps fetch time reasonable. Results vary by subreddit activity.

## ADR-004: JSON-Serialized Strings in State
**Status**: Accepted
**Context**: ADK state values must be serializable primitives. Complex data (lists of dicts) cannot be stored directly as Python objects.
**Decision**: Serialize trend and scoring data as JSON strings in state, deserialize when reading.
**Rationale**: JSON strings are valid state values, easily parsed, and human-readable for debugging.
**Consequences**: Slight overhead for serialization/deserialization. Must handle malformed JSON gracefully.

## ADR-005: Model Selection
**Status**: Accepted
**Context**: Need to choose stable Gemini models for each agent role.
**Decision**: `gemini-2.0-flash` for root, trends_fetcher, and opportunity_scorer. `gemini-2.5-flash` for report_generator.
**Rationale**: Flash models are fast and cost-effective for tool-calling tasks. Report generation benefits from the slightly better text quality of 2.5-flash. All are stable (no -exp/-preview).
**Consequences**: If report quality is insufficient, can upgrade to `gemini-2.5-pro` at higher cost.

## ADR-006: No Custom UI
**Status**: Accepted
**Context**: User explicitly requested no custom UI — run on `adk web .` only, report as chat message.
**Decision**: No Streamlit, FastAPI, or CLI frontend. Agent runs via `adk web .`, `adk run .`, and `adk api_server .`.
**Rationale**: Simplest approach, minimal dependencies, fastest to build. ADK's built-in web UI is sufficient for the use case.
**Consequences**: No rich visualizations or charts. Report is text-only markdown in chat.

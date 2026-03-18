# DESIGN: ecommerce_product_spotter

## Agent Details

### root_agent
- **Type**: Agent (LlmAgent)
- **Model**: `gemini-2.0-flash`
- **Purpose**: Conversational entry point. Greets the user, gathers a product keyword/category, delegates to the demand pipeline, and returns the final report.
- **Instruction summary**: "You are an e-commerce demand spotter. Ask the user for a product category or keyword. Save it to state, then delegate to the demand_pipeline. Return the final_report to the user."
- **Tools**: `AgentTool(demand_pipeline)`
- **Input**: User's chat message (keyword/category)
- **Output**: Final seller report from `state['final_report']`

### demand_pipeline
- **Type**: SequentialAgent
- **Purpose**: Runs trends_fetcher → opportunity_scorer → report_generator in order
- **Sub-agents**: [trends_fetcher, opportunity_scorer, report_generator]
- **Input**: State containing `user_keyword`
- **Output**: State containing `final_report`

### trends_fetcher
- **Type**: Agent (LlmAgent)
- **Model**: `gemini-2.0-flash`
- **Purpose**: Calls `fetch_rising_trends` tool with the user's keyword to scrape Reddit for trending posts
- **Instruction summary**: "You fetch trending Reddit posts. Read the keyword from state and call fetch_rising_trends. Store results in state."
- **Tools**: `fetch_rising_trends`
- **Input**: `state['user_keyword']`
- **Output**: Writes `state['trending_terms']`
- **output_key**: `trending_terms_output`

### opportunity_scorer
- **Type**: Agent (LlmAgent)
- **Model**: `gemini-2.0-flash`
- **Purpose**: Reads raw Reddit posts, scores each by e-commerce opportunity
- **Instruction summary**: "Read trending_terms from state. Call score_opportunities to compute scores. Store results."
- **Tools**: `score_opportunities`
- **Input**: `state['trending_terms']`
- **Output**: Writes `state['scored_terms']`
- **output_key**: `scored_terms_output`

### report_generator
- **Type**: Agent (LlmAgent)
- **Model**: `gemini-2.5-flash`
- **Purpose**: Reads scored posts and generates a formatted seller report using LLM
- **Instruction summary**: "Read scored_terms from state. Generate a markdown-formatted e-commerce opportunity report with rankings, scores, and recommended actions."
- **Tools**: None (LLM-only generation)
- **Input**: `state['scored_terms']`
- **Output**: Writes `state['final_report']` via output_key
- **output_key**: `final_report`

---

## Tool Details

### fetch_rising_trends

- **Function name**: `fetch_rising_trends`
- **Parameters**:
  - `keyword: str` — product category or search keyword
  - `tool_context: ToolContext` — ADK tool context
- **Return**: `dict` with keys `status` (str) and `data` (str, JSON-serialized list of post dicts)
- **Data source**: Reddit public JSON API — 7 subreddits: r/shutupandtakemymoney, r/BuyItForLife, r/gadgets, r/AmazonTopRated, r/deals, r/ProductPorn, r/ecommerce
- **Fetch strategy**: 10 posts via `/search.json?q=keyword` + 15 posts via `/hot.json` filtered by keyword, per subreddit. Rate limited at 1 second between requests.
- **State keys written**: `trending_terms` — JSON string of list of post dicts
- **Deduplication**: Same post URL from search and hot deduped (keeps highest score). Returns top 25 sorted by score + comment_velocity.
- **Error handling**: Returns `{"status": "error", "message": "..."}` on network failure. Returns empty list gracefully if no posts found.

### score_opportunities

- **Function name**: `score_opportunities`
- **Parameters**:
  - `trending_terms_json: str` — JSON string of Reddit posts from state
  - `tool_context: ToolContext` — ADK tool context
- **Return**: `dict` with keys `status` (str) and `data` (str, JSON-serialized list of scored dicts)
- **State keys read**: `trending_terms`
- **State keys written**: `scored_terms` — JSON string sorted by `opportunity_score` descending
- **Scoring formula**: `0.30 * popularity + 0.25 * engagement + 0.20 * sentiment + 0.25 * commercial_intent`
- **Error handling**: Returns empty scored list if input is invalid JSON or None

---

## Processing Flow

1. **User sends keyword** → root_agent receives "fitness equipment"
2. **root_agent** saves `state['user_keyword'] = "fitness equipment"`, delegates to `demand_pipeline`
3. **trends_fetcher** reads `state['user_keyword']`, calls `fetch_rising_trends("fitness equipment")` → scrapes Reddit across 7 subreddits → writes `state['trending_terms']` (JSON list of up to 25 posts)
4. **opportunity_scorer** reads `state['trending_terms']`, calls `score_opportunities(...)` → computes scores → writes `state['scored_terms']` (JSON list of scored posts sorted by opportunity_score desc)
5. **report_generator** reads `state['scored_terms']`, uses LLM to format a seller report with rankings, scores, and action items → writes `state['final_report']` via output_key
6. **root_agent** reads `state['final_report']`, returns it to the user as a chat message

---

## Error Handling Strategy

- **Reddit fetch failure**: `fetch_rising_trends` returns error dict → trends_fetcher reports the error to user
- **No results found**: Returns friendly message "No trending posts found for this keyword. Try a broader category."
- **Invalid scored data**: `score_opportunities` returns empty list → report_generator generates a "no data" message
- **Max retries**: Tools do not retry internally. The LLM agent may retry a tool call up to 3 times if it receives an error.

---

## Testing Strategy Overview

- **Unit tests**: Test each tool function in isolation with mocked `requests.get` and sample Reddit post data
- **Integration tests**: Test agent loading (`import root_agent`), verify it works with `adk web`, `adk run`, `adk api_server`
- **Mocking**: Mock `requests.get` for all Reddit fetch tests to avoid real network calls
- **Coverage target**: 100%

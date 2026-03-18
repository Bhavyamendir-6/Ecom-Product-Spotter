# TEST STRATEGY: ecommerce_product_spotter

## Overview
All tests run with mocked external dependencies (Reddit API, LLM). No real network calls in default test suite. Coverage target: 100%.

## Test Categories

### Unit Tests (mocked, no API key)
- **test_tools.py**: `fetch_rising_trends` and `score_opportunities` — happy path, error paths, edge cases
- **test_sub_agents.py**: Each sub-agent initializes correctly with proper model, tools, output_key
- **test_agent.py**: Root agent setup, pipeline wiring, observability callbacks
- **test_observability.py**: Logging setup, model/agent callbacks
- **test_config.py**: Environment variable loading

### Integration Tests (mocked)
- **test_integration.py**: State flow between tools, agent loading from parent dir (adk web context)
- **test_adk_load.py**: Import from parent directory, agent submodule exists for adk eval

### Live Tests (require API key, marked @pytest.mark.live)
- End-to-end pipeline with real LLM and Reddit API calls

## Mocking Strategy
- `requests.get` mocked for all Reddit fetch tests
- `ToolContext` mocked with dict-based state
- LLM calls not exercised in unit tests (testing tool logic only)

## Coverage Target: 100%
Every module, branch, and except block must be covered.

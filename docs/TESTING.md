# Testing Guide: ecommerce_product_spotter

## Running Tests

```bash
# Activate virtual environment
.\.venv\Scripts\activate    # Windows
# source .venv/bin/activate # macOS/Linux

# Mocked tests (no API key needed)
pytest tests/ -v --cov=. --cov-fail-under=100 -m "not live"

# All tests including live
pytest tests/ -v

# Generate HTML coverage report
pytest tests/ -v --cov=. --cov-report=html -m "not live"
# Open htmlcov/index.html
```

## Test Structure

| File | Tests | What it covers |
|------|-------|---------------|
| `test_agent.py` | 13 | Root agent config, model, tools, callbacks |
| `test_sub_agents.py` | 19 | All 3 sub-agents initialization |
| `test_tools.py` | 19 | `fetch_rising_trends` and `score_opportunities` |
| `test_observability.py` | 11 | Logging setup, model/agent callbacks |
| `test_integration.py` | 6 | State flow, ADK load, pipeline structure |
| `test_import_paths.py` | 3 | Dual-context import robustness |

## Adding New Tests

### Naming Convention
```
test_[what]_[condition]
```
Examples: `test_tool_returns_error_on_empty_input`, `test_agent_has_correct_model`

### Pattern (AAA)
```python
def test_my_tool_does_something(mock_tool_context):
    # Arrange
    input_data = "test input"
    mock_tool_context.state["key"] = "value"

    # Act
    result = my_tool(input_data, mock_tool_context)

    # Assert
    assert result["status"] == "success"
    assert mock_tool_context.state.get("output_key") is not None
```

### Using Fixtures
- `mock_tool_context`: MagicMock with dict-based state
- `mock_llm_response`: MagicMock with text/content/parts
- `sample_trending_terms`: List of 5 sample Reddit post dicts

## Mocking Strategy

- **Reddit API**: `@patch("requests.get")` — mock the HTTP call, return fake JSON responses
- **ToolContext**: `mock_tool_context` fixture (dict-based state)
- **Environment**: `@patch.dict("os.environ", {"KEY": "value"})`

## ADK Eval

```bash
pip install "google-adk[eval]"
adk eval . eval/basic_flow.test.json --config_file_path=eval/test_config.json --print_detailed_results
```

Add new eval cases in `eval/basic_flow.test.json` following the existing format.

## CI/CD Integration

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=. --cov-fail-under=100 -m "not live"
```

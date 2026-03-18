import sys
from pathlib import Path


import os
from google.adk.agents.llm_agent import Agent
from google.genai import types


_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


try:
    from sub_agents.trends_fetcher.prompt import TRENDS_FETCHER_INSTRUCTION
    from sub_agents.trends_fetcher.tools.fetch_trends import fetch_rising_trends
except ImportError:
    from .prompt import TRENDS_FETCHER_INSTRUCTION
    from .tools.fetch_trends import fetch_rising_trends

MODEL = os.getenv("MODEL", "gemini-2.0-flash")

trends_fetcher_agent = Agent(
    model=MODEL,
    name="trends_fetcher",
    description="Fetches trending product mentions from Reddit across product-focused subreddits for a given keyword.",
    instruction=TRENDS_FETCHER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    tools=[fetch_rising_trends],
    output_key="trending_terms_output",
)

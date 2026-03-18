import sys
from pathlib import Path



import os
from google.adk.agents.llm_agent import Agent
from google.genai import types


_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


    
try:
    from sub_agents.opportunity_scorer.prompt import OPPORTUNITY_SCORER_INSTRUCTION
    from sub_agents.opportunity_scorer.tools.score_opportunities import score_opportunities
except ImportError:
    from .prompt import OPPORTUNITY_SCORER_INSTRUCTION
    from .tools.score_opportunities import score_opportunities

MODEL = os.getenv("MODEL", "gemini-2.0-flash")

opportunity_scorer_agent = Agent(
    model=MODEL,
    name="opportunity_scorer",
    description="Scores trending search terms by e-commerce opportunity using growth rate, trend strength, and commercial intent.",
    instruction=OPPORTUNITY_SCORER_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.1),
    tools=[score_opportunities],
    output_key="scored_terms_output",
)

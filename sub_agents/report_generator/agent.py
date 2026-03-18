import sys
from pathlib import Path


import os
from google.adk.agents.llm_agent import Agent
from google.genai import types


_root = Path(__file__).resolve().parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))


try:
    from sub_agents.report_generator.prompt import REPORT_GENERATOR_INSTRUCTION
except ImportError:
    from .prompt import REPORT_GENERATOR_INSTRUCTION

MODEL_PRO = os.getenv("MODEL_PRO", "gemini-2.5-flash")

report_generator_agent = Agent(
    model=MODEL_PRO,
    name="report_generator",
    description="Generates a formatted e-commerce seller report from scored trending terms.",
    instruction=REPORT_GENERATOR_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
    tools=[],
    output_key="final_report",
)

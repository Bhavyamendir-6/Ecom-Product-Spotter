import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

# Guard against double-creation when loaded as both 'agent' and
# 'Ecommerce_product_spotter.agent' (adk web vs adk run context).
_alt_name = "Ecommerce_product_spotter.agent" if __name__ == "agent" else "agent"
_alt_mod = sys.modules.get(_alt_name)
if _alt_mod and hasattr(_alt_mod, "root_agent"):
    demand_pipeline = _alt_mod.demand_pipeline
    root_agent = _alt_mod.root_agent
else:
    from google.adk.agents.llm_agent import Agent
    from google.adk.agents.sequential_agent import SequentialAgent
    from google.adk.tools.agent_tool import AgentTool
    from google.genai import types

    try:
        from prompt import ROOT_INSTRUCTION
        from config import MODEL
        from observability import (
            setup_logging,
            before_model_callback,
            after_model_callback,
            before_agent_callback,
            after_agent_callback,
        )
        from sub_agents.trends_fetcher.agent import trends_fetcher_agent
        from sub_agents.opportunity_scorer.agent import opportunity_scorer_agent
        from sub_agents.report_generator.agent import report_generator_agent
    except ImportError:
        from .prompt import ROOT_INSTRUCTION
        from .config import MODEL
        from .observability import (
            setup_logging,
            before_model_callback,
            after_model_callback,
            before_agent_callback,
            after_agent_callback,
        )
        from .sub_agents.trends_fetcher.agent import trends_fetcher_agent
        from .sub_agents.opportunity_scorer.agent import opportunity_scorer_agent
        from .sub_agents.report_generator.agent import report_generator_agent

    setup_logging()

    demand_pipeline = SequentialAgent(
        name="demand_pipeline",
        description="Runs the full demand spotting pipeline: fetch trends → score opportunities → generate report.",
        sub_agents=[trends_fetcher_agent, opportunity_scorer_agent, report_generator_agent],
    )

    root_agent = Agent(
        model=MODEL,
        name="ecommerce_product_spotter",
        description="E-Commerce Product Demand Spotter — discovers trending product opportunities from Reddit data.",
        instruction=ROOT_INSTRUCTION,
        generate_content_config=types.GenerateContentConfig(temperature=0.2),
        tools=[AgentTool(agent=demand_pipeline)],
        before_model_callback=before_model_callback,
        after_model_callback=after_model_callback,
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback,
    )

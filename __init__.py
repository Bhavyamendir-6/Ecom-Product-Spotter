import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from .agent import root_agent
from . import agent  # Required for adk eval: agent_module.agent.root_agent

__all__ = ["root_agent", "agent"]

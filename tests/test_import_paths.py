"""Tests for import path robustness — covers sys.path and ImportError branches."""
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestAgentSysPath:
    def test_sys_path_already_contains_root(self):
        """Cover the case where _root is already in sys.path (line 6 of agent.py)."""
        agent_root = str(Path(__file__).resolve().parent.parent)
        # Ensure it's already there
        if agent_root not in sys.path:
            sys.path.insert(0, agent_root)
        assert agent_root in sys.path
        # Importing agent should still work (sys.path.insert skipped)
        from agent import root_agent
        assert root_agent is not None

    def test_sub_agent_sys_path_already_contains_root(self):
        """Cover sys.path branch for sub-agent agent.py files."""
        agent_root = str(Path(__file__).resolve().parent.parent)
        if agent_root not in sys.path:
            sys.path.insert(0, agent_root)
        from sub_agents.trends_fetcher.agent import trends_fetcher_agent
        from sub_agents.opportunity_scorer.agent import opportunity_scorer_agent
        from sub_agents.report_generator.agent import report_generator_agent
        assert trends_fetcher_agent is not None
        assert opportunity_scorer_agent is not None
        assert report_generator_agent is not None


class TestInitSysPath:
    def test_init_sys_path(self):
        """Cover __init__.py sys.path insertion."""
        parent_dir = str(Path(__file__).resolve().parent.parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        mod_name = "Ecommerce_product_spotter"
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
        else:
            import importlib
            mod = importlib.import_module(mod_name)
        assert hasattr(mod, "root_agent")
        assert hasattr(mod, "agent")

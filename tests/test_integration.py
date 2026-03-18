import json
import sys
from pathlib import Path
import importlib


class TestStateFlow:
    def test_full_state_flow(self, mock_tool_context, sample_trending_terms):
        """Test data flows correctly: fetch → score via state."""
        from sub_agents.opportunity_scorer.tools.score_opportunities import score_opportunities

        # Step 1: Simulate fetch_rising_trends writing to state
        mock_tool_context.state["trending_terms"] = json.dumps(sample_trending_terms)

        # Step 2: Scorer reads from state and scores
        trending_json = mock_tool_context.state["trending_terms"]
        result = score_opportunities(trending_json, mock_tool_context)

        assert result["status"] == "success"
        scored = json.loads(mock_tool_context.state["scored_terms"])
        assert len(scored) == len(sample_trending_terms)

        # Verify scored terms have all required Reddit-specific fields
        for term in scored:
            assert "title" in term
            assert "opportunity_score" in term
            assert "popularity_score" in term
            assert "engagement_score" in term
            assert "sentiment_signal" in term
            assert "commercial_intent" in term
            assert "recommendation" in term
            assert "subreddit" in term
            assert "post_url" in term

    def test_empty_fetch_to_scorer(self, mock_tool_context):
        """Test scorer handles empty fetch result gracefully."""
        from sub_agents.opportunity_scorer.tools.score_opportunities import score_opportunities

        mock_tool_context.state["trending_terms"] = "[]"
        result = score_opportunities("[]", mock_tool_context)

        assert result["status"] == "success"
        assert json.loads(mock_tool_context.state["scored_terms"]) == []


class TestAdkLoad:
    def test_adk_load_from_parent(self):
        """Verify agent loads correctly when imported from parent dir (as adk web does)."""
        parent_dir = str(Path(__file__).resolve().parent.parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Check if already imported to avoid re-creating pipeline
        mod_name = "Ecommerce_product_spotter"
        if mod_name in sys.modules:
            agent_module = sys.modules[mod_name]
        else:
            agent_module = importlib.import_module(mod_name)

        assert hasattr(agent_module, "root_agent"), "root_agent not found in module"
        assert agent_module.root_agent is not None
        assert agent_module.root_agent.name == "ecommerce_product_spotter"

    def test_adk_agent_submodule_exists(self):
        """Verify agent_module.agent.root_agent exists for adk eval."""
        parent_dir = str(Path(__file__).resolve().parent.parent.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        mod_name = "Ecommerce_product_spotter"
        if mod_name in sys.modules:
            agent_module = sys.modules[mod_name]
        else:
            agent_module = importlib.import_module(mod_name)

        assert hasattr(agent_module, "agent"), "agent submodule not found — adk eval will fail"
        assert hasattr(agent_module.agent, "root_agent")


class TestPipelineAgent:
    def test_demand_pipeline_exists(self):
        from agent import root_agent
        assert len(root_agent.tools) >= 1

    def test_sequential_pipeline_has_sub_agents(self):
        from agent import demand_pipeline
        assert len(demand_pipeline.sub_agents) == 3
        names = [a.name for a in demand_pipeline.sub_agents]
        assert "trends_fetcher" in names
        assert "opportunity_scorer" in names
        assert "report_generator" in names

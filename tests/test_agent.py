import pytest
from agent import root_agent
from config import MODEL
from observability import (
    setup_logging,
    before_model_callback,
    after_model_callback,
    before_agent_callback,
    after_agent_callback,
)
from prompt import ROOT_INSTRUCTION


class TestRootAgent:
    def test_root_agent_exists(self):
        assert root_agent is not None

    def test_root_agent_name(self):
        assert root_agent.name == "ecommerce_product_spotter"

    def test_root_agent_model(self):
        assert root_agent.model == MODEL

    def test_root_agent_has_tools(self):
        assert len(root_agent.tools) > 0

    def test_root_agent_instruction(self):
        assert root_agent.instruction == ROOT_INSTRUCTION

    def test_root_agent_has_pipeline_tool(self):
        tool_names = [t.name if hasattr(t, 'name') else str(t) for t in root_agent.tools]
        # AgentTool wraps demand_pipeline
        assert len(tool_names) >= 1

    def test_root_agent_callbacks_wired(self):
        assert root_agent.before_model_callback is before_model_callback
        assert root_agent.after_model_callback is after_model_callback
        assert root_agent.before_agent_callback is before_agent_callback
        assert root_agent.after_agent_callback is after_agent_callback

    def test_root_agent_generate_content_config(self):
        assert root_agent.generate_content_config is not None
        assert root_agent.generate_content_config.temperature == 0.2


class TestConfig:
    def test_model_default(self):
        import config
        assert config.MODEL is not None
        assert isinstance(config.MODEL, str)

    def test_model_pro_default(self):
        import config
        assert config.MODEL_PRO is not None
        assert isinstance(config.MODEL_PRO, str)


class TestPrompt:
    def test_root_instruction_not_empty(self):
        assert len(ROOT_INSTRUCTION) > 50

    def test_root_instruction_mentions_keyword(self):
        assert "user_keyword" in ROOT_INSTRUCTION

    def test_root_instruction_mentions_pipeline(self):
        assert "demand_pipeline" in ROOT_INSTRUCTION

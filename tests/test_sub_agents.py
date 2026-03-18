import pytest
from sub_agents.trends_fetcher.agent import trends_fetcher_agent
from sub_agents.trends_fetcher.prompt import TRENDS_FETCHER_INSTRUCTION
from sub_agents.trends_fetcher.tools.fetch_trends import fetch_rising_trends

from sub_agents.opportunity_scorer.agent import opportunity_scorer_agent
from sub_agents.opportunity_scorer.prompt import OPPORTUNITY_SCORER_INSTRUCTION
from sub_agents.opportunity_scorer.tools.score_opportunities import score_opportunities

from sub_agents.report_generator.agent import report_generator_agent
from sub_agents.report_generator.prompt import REPORT_GENERATOR_INSTRUCTION


class TestTrendsFetcherAgent:
    def test_agent_exists(self):
        assert trends_fetcher_agent is not None

    def test_agent_name(self):
        assert trends_fetcher_agent.name == "trends_fetcher"

    def test_agent_model(self):
        assert "gemini" in trends_fetcher_agent.model

    def test_agent_description_not_empty(self):
        assert len(trends_fetcher_agent.description) > 10

    def test_agent_has_tools(self):
        assert len(trends_fetcher_agent.tools) == 1
        assert trends_fetcher_agent.tools[0] is fetch_rising_trends

    def test_agent_output_key(self):
        assert trends_fetcher_agent.output_key == "trending_terms_output"

    def test_agent_instruction(self):
        assert trends_fetcher_agent.instruction == TRENDS_FETCHER_INSTRUCTION

    def test_prompt_not_empty(self):
        assert len(TRENDS_FETCHER_INSTRUCTION) > 20


class TestOpportunityScorerAgent:
    def test_agent_exists(self):
        assert opportunity_scorer_agent is not None

    def test_agent_name(self):
        assert opportunity_scorer_agent.name == "opportunity_scorer"

    def test_agent_model(self):
        assert "gemini" in opportunity_scorer_agent.model

    def test_agent_description_not_empty(self):
        assert len(opportunity_scorer_agent.description) > 10

    def test_agent_has_tools(self):
        assert len(opportunity_scorer_agent.tools) == 1
        assert opportunity_scorer_agent.tools[0] is score_opportunities

    def test_agent_output_key(self):
        assert opportunity_scorer_agent.output_key == "scored_terms_output"

    def test_agent_instruction(self):
        assert opportunity_scorer_agent.instruction == OPPORTUNITY_SCORER_INSTRUCTION

    def test_prompt_not_empty(self):
        assert len(OPPORTUNITY_SCORER_INSTRUCTION) > 20


class TestReportGeneratorAgent:
    def test_agent_exists(self):
        assert report_generator_agent is not None

    def test_agent_name(self):
        assert report_generator_agent.name == "report_generator"

    def test_agent_model(self):
        assert "gemini" in report_generator_agent.model

    def test_agent_description_not_empty(self):
        assert len(report_generator_agent.description) > 10

    def test_agent_no_tools(self):
        assert len(report_generator_agent.tools) == 0

    def test_agent_output_key(self):
        assert report_generator_agent.output_key == "final_report"

    def test_agent_instruction(self):
        assert report_generator_agent.instruction == REPORT_GENERATOR_INSTRUCTION

    def test_prompt_not_empty(self):
        assert len(REPORT_GENERATOR_INSTRUCTION) > 20

    def test_prompt_mentions_scored_terms(self):
        assert "scored_terms" in REPORT_GENERATOR_INSTRUCTION

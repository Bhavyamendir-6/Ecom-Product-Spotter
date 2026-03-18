import json
import logging

from google import genai

from app.config import get_settings

logger = logging.getLogger(__name__)


async def generate_report(keyword: str, scored_terms: list[dict]) -> str:
    """Generate an e-commerce report using Gemini API directly.

    Uses the same prompt as the ADK report_generator agent but calls
    the Gemini API without going through ADK.
    """
    from sub_agents.report_generator.prompt import REPORT_GENERATOR_INSTRUCTION

    settings = get_settings()

    client = genai.Client(api_key=settings.google_api_key)

    scored_json = json.dumps(scored_terms, indent=2)
    user_message = (
        f"Generate the e-commerce report for keyword '{keyword}'.\n\n"
        f"scored_terms state data:\n{scored_json}"
    )

    response = await client.aio.models.generate_content(
        model=settings.gemini_model_pro,
        contents=[
            {"role": "user", "parts": [{"text": user_message}]},
        ],
        config={
            "system_instruction": REPORT_GENERATOR_INSTRUCTION,
            "temperature": 0.3,
        },
    )

    report_text = response.text or "Report generation returned empty response."
    logger.info("Report generated: %d characters", len(report_text))
    return report_text

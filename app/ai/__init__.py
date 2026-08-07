from typing import Dict

from app.ai.workflow import problem_report_graph
from app.ai.provider import AIProvider
from app.ai.bedrock import BedrockProvider
from app.gpt import GPT
from app.problem_utils import get_problem_type
from app.config import Config


class OpenAIProvider(AIProvider):
    async def summarize_report(self, content: str) -> Dict[str, str]:
        summary = GPT.get_instance().generate_response(content)
        return {"summary": summary, "problem_type": get_problem_type(summary)}


def get_report_provider() -> AIProvider:
    if Config.AI_PROVIDER == "bedrock":
        return BedrockProvider()
    return OpenAIProvider()


__all__ = [
    "problem_report_graph",
    "AIProvider",
    "BedrockProvider",
    "OpenAIProvider",
    "get_report_provider",
]

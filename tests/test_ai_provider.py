import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.ai import OpenAIProvider, get_report_provider


def test_factory_returns_openai_provider_by_default():
    with patch("app.ai.Config.AI_PROVIDER", "openai"), patch(
        "app.ai.OpenAIProvider"
    ) as mock_openai:
        provider = get_report_provider()
        mock_openai.assert_called_once()
        assert provider is mock_openai.return_value


def test_factory_returns_bedrock_provider_when_configured():
    with patch("app.ai.Config.AI_PROVIDER", "bedrock"), patch(
        "app.ai.BedrockProvider"
    ) as mock_bedrock:
        provider = get_report_provider()
        mock_bedrock.assert_called_once()
        assert provider is mock_bedrock.return_value


@pytest.mark.asyncio
async def test_openai_provider_returns_summary_and_problem_type():
    gpt_instance = MagicMock()
    gpt_instance.generate_response.return_value = "hardware problem with the wheels"
    with patch("app.ai.GPT.get_instance", return_value=gpt_instance), patch(
        "app.ai.get_problem_type", return_value="hardware"
    ):
        provider = OpenAIProvider()
        result = await provider.summarize_report("El bot no responde")

    assert result["summary"] == "hardware problem with the wheels"
    assert result["problem_type"] == "hardware"


@pytest.mark.asyncio
async def test_openai_provider_marks_problem_type_undefined_on_error():
    gpt_instance = MagicMock()
    gpt_instance.generate_response.return_value = "summary text"
    with patch("app.ai.GPT.get_instance", return_value=gpt_instance), patch(
        "app.ai.get_problem_type", return_value="undefined"
    ):
        provider = OpenAIProvider()
        result = await provider.summarize_report("report")

    assert result["problem_type"] == "undefined"

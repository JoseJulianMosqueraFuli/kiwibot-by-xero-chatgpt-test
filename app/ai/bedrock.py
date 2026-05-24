import json
import boto3
from typing import Dict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_aws import ChatBedrock
from langchain_core.output_parsers import JsonOutputParser
from app.ai.prompts import problem_report_prompt
from app.config import Config
from app.exceptions import BedrockAPIError
from app.logging_config import get_logger

logger = get_logger(__name__)


class BedrockProvider:
    def __init__(self):
        self.model_id = Config.BEDROCK_MODEL_ID
        self.region = Config.AWS_REGION
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=self.region,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        )
        self.llm = ChatBedrock(
            model_id=self.model_id,
            client=self.client,
            model_kwargs={"temperature": 0.1, "max_tokens": 500},
        )
        self.chain = problem_report_prompt | self.llm | JsonOutputParser()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(BedrockAPIError),
        reraise=True,
    )
    async def summarize_report(self, content: str) -> Dict[str, str]:
        try:
            logger.info("Sending report to Bedrock for analysis")
            result = await self.chain.ainvoke({"content": content})

            summary = result.get("summary", "")
            problem_type = result.get("problem_type", "undefined")

            if problem_type not in ("hardware", "software", "field", "undefined"):
                problem_type = "undefined"

            logger.info(
                "Bedrock analysis complete",
                extra={"problem_type": problem_type},
            )

            return {"summary": summary, "problem_type": problem_type}

        except BedrockAPIError:
            raise
        except Exception as e:
            logger.error(f"Bedrock API error: {e}")
            raise BedrockAPIError(f"Failed to analyze report: {e}")

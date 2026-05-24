from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.ai.bedrock import BedrockProvider
from app.logging_config import get_logger

logger = get_logger(__name__)


class ReportState(TypedDict):
    content: str
    summary: str
    problem_type: str
    error: str


async def summarize_node(state: ReportState) -> ReportState:
    provider = BedrockProvider()
    try:
        result = await provider.summarize_report(state["content"])
        return {
            "summary": result["summary"],
            "problem_type": result["problem_type"],
            "error": "",
        }
    except Exception as e:
        logger.error(f"Workflow summarization failed: {e}")
        return {
            "summary": state["content"],
            "problem_type": "undefined",
            "error": str(e),
        }


def validate_node(state: ReportState) -> ReportState:
    if not state.get("summary") or len(state["summary"]) == 0:
        return {**state, "error": "Empty summary generated"}
    return state


workflow = StateGraph(ReportState)

workflow.add_node("summarize", summarize_node)
workflow.add_node("validate", validate_node)

workflow.set_entry_point("summarize")
workflow.add_edge("summarize", "validate")
workflow.add_edge("validate", END)

problem_report_graph = workflow.compile()

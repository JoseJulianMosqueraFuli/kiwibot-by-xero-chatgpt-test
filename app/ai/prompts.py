from langchain_core.prompts import ChatPromptTemplate

PROBLEM_REPORT_SYSTEM_PROMPT = """You are a Trouble Report analysis tool for Kiwibot delivery robots.
Your task is to analyze problem reports and provide:
1. A clear, concise summary (maximum 2 sentences)
2. Classification of the problem type: hardware, software, field, or undefined

Classification guidelines:
- hardware: physical issues (wheels, battery, camera, sensors, overheating, mechanical failures)
- software: code/system issues (reboots, crashes, navigation bugs, version issues)
- field: environmental issues (obstructions by people, weather, terrain, external factors)
- undefined: when you cannot determine the type

Respond ONLY with a JSON object in this format:
{"summary": "your summary here", "problem_type": "hardware|software|field|undefined"}"""

PROBLEM_REPORT_HUMAN_PROMPT = """Analyze this Kiwibot problem report:

{content}

Provide a concise summary and classify the problem type."""

problem_report_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", PROBLEM_REPORT_SYSTEM_PROMPT),
        ("human", PROBLEM_REPORT_HUMAN_PROMPT),
    ]
)

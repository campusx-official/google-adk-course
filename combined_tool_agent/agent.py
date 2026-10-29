from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.adk.agents.llm_agent import Agent
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools import google_search
from google.adk.tools.langchain_tool import LangchainTool
from google.genai import types
from langchain_tavily import TavilySearch

MODEL = "gemini-3.5-flash"


# 1. Function tool
def get_current_time(timezone: str) -> dict:
    """Get the current date and time in a given time zone.

    Use this whenever the user asks what time or date it is somewhere.

    Args:
        timezone: An IANA time zone name, e.g. "Asia/Kolkata",
            "America/New_York" or "Europe/London".

    Returns:
        A dict with "status" ("success" or "error"). On success it also has
        "timezone", "date", "time" and "weekday". On error it has
        "error_message".
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return {
            "status": "error",
            "error_message": (
                f"Unknown time zone '{timezone}'. "
                "Use an IANA name like 'Asia/Kolkata'."
            ),
        }
    return {
        "status": "success",
        "timezone": timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
    }


# 2. Third-party tool: LangChain's Tavily search, wrapped for ADK
tavily_tool = LangchainTool(
    tool=TavilySearch(max_results=5, topic="general")
)


# 3. One agent with all four tools
root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "A helpful assistant that can search the web, run Python code "
        "and tell the time anywhere."
    ),
    instruction=(
        "Answer user questions accurately.\n"
        "- Use Google Search for current information and quick fact checks.\n"
        "- Use the Tavily search tool when you need more detailed results, "
        "multiple sources, or when Google Search did not give enough.\n"
        "- Write and run Python code for calculations or data analysis.\n"
        "- Use get_current_time whenever the user asks for the time or date "
        "somewhere. Never guess the current time.\n"
        "Cite sources when you use search results."
    ),
    tools=[google_search, tavily_tool, get_current_time],  # built-in + third-party + function
    code_executor=BuiltInCodeExecutor(),                    # code execution goes here, not in tools
    generate_content_config=types.GenerateContentConfig(
        tool_config=types.ToolConfig(include_server_side_tool_invocations=True),
    )
)
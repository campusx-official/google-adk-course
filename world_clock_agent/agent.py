from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from google.adk.agents.llm_agent import Agent


def get_current_time(timezone: str) -> dict:
    """Get the current date and time in a given time zone.

    Use this whenever the user asks what time or date it is somewhere.

    Args:
        timezone: An IANA time zone name, e.g. "Asia/Kolkata",
            "America/New_York" or "Europe/London".

    Returns:
        A dict with "status" ("success" or "error"). On success it also has
        "timezone", "date", "time" and "weekday". On error it has "error_message".
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return {
            "status": "error",
            "error_message": f"Unknown time zone '{timezone}'. Use an IANA name like 'Asia/Kolkata'.",
        }
    return {
        "status": "success",
        "timezone": timezone,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "weekday": now.strftime("%A"),
    }


root_agent = Agent(
    model='gemini-3.5-flash',
    name='clock_agent',
    description="Tells the current time and date anywhere in the world.",
    instruction=(
        "You tell users the current time and date in any city or country. "
        "Translate place names into IANA time zones yourself (e.g. Mumbai -> Asia/Kolkata) "
        "and call get_current_time. If it returns status 'error', explain the problem "
        "and ask the user to clarify."
    ),
    tools=[get_current_time],
)
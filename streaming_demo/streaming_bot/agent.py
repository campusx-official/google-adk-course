import asyncio
from typing import AsyncGenerator

from google.adk.agents import Agent
from google.adk.events import Event


# ---------------------------------------------------------------
# A streaming tool: an async generator instead of a normal function
#    - yield Event(message=...)  -> a progress update, sent to the user right away
#    - yield a dict (only once)  -> the final result, the only thing the model sees
# ---------------------------------------------------------------
async def get_weather(city: str) -> AsyncGenerator[Event | dict, None]:
    """Get the current weather for a city."""
    yield Event(message="(connecting to weather service...)\n", partial=True)
    await asyncio.sleep(1)                                   # pretend this is slow

    yield Event(message=f"(fetching weather for {city}...)\n", partial=True)
    await asyncio.sleep(1)

    yield {"city": city, "temperature_c": 31, "condition": "sunny"}

def show_callback(callback_context, llm_response):
    if llm_response.partial:        # a piece: skip it
        return None
    print(" [cb] ", end="", flush=True)


root_agent = Agent(
    name="streaming_bot",
    model="gemini-3.5-flash",
    description="A simple general-purpose chatbot.",
    instruction="You are a friendly, helpful assistant. "
                "Use the get_weather tool when the user asks about the weather.",
    tools=[get_weather],
    #after_model_callback=show_callback
)
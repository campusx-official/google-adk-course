from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import load_memory


# WRITE: after every reply, save this session into memory.
# adk web never saves to memory on its own.
async def save_to_memory(callback_context: CallbackContext) -> None:
    await callback_context.add_session_to_memory()


# READ: the agent searches memory with the load_memory tool when it decides to.
root_agent = Agent(
    name="memory_agent",
    model="gemini-3.5-flash",
    instruction=(
        "You are the order assistant at CampusX Cafe. "
        "If the customer mentions an earlier visit (their usual order, "
        "preferences or allergies), call load_memory first. "
        "Search with short keywords like 'coffee' or 'peanuts'. "
        "Keep replies short."
    ),
    tools=[load_memory],
    after_agent_callback=save_to_memory,
)
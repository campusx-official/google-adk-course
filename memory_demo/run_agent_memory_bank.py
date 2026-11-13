import asyncio
import os

import agentplatform
from dotenv import load_dotenv
from google.adk.memory import VertexAiMemoryBankService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

load_dotenv("memory_agent/.env")

from memory_agent.agent import root_agent

APP_NAME = "memory_demo"
PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["GOOGLE_CLOUD_LOCATION"]
MEMORY_BANK_ID = os.environ["MEMORY_BANK_ID"]

session_service = InMemorySessionService()
memory_service = VertexAiMemoryBankService(
    project=PROJECT,
    location=LOCATION,
    agent_engine_id=MEMORY_BANK_ID,
)

runner = Runner(agent=root_agent, app_name=APP_NAME,
                session_service=session_service,
                memory_service=memory_service)   # the agent reads memory through the Runner


def chat(session, text):
    message = types.Content(role="user", parts=[types.Part(text=text)])
    print("\nUSER :", text)
    for event in runner.run(user_id=session.user_id, session_id=session.id,
                            new_message=message):
        for call in event.get_function_calls():
            print("TOOL :", call.name, call.args)
        if event.is_final_response() and event.content and event.content.parts:
            print("AGENT:", event.content.parts[0].text)


def save_to_memory(session):
    """The APPLICATION saves the session to Memory Bank."""
    session = asyncio.run(session_service.get_session(
        app_name=APP_NAME, user_id=session.user_id, session_id=session.id))

    # Memory Bank reads the conversation with an LLM and extracts facts.
    # wait_for_completion=True makes this call wait until that is finished.
    asyncio.run(memory_service.add_events_to_memory(
        app_name=APP_NAME,
        user_id=session.user_id,
        session_id=session.id,
        events=session.events,
        custom_metadata={"wait_for_completion": True},
    ))

    print(f"\n>>> saved session {session.id[:8]} to memory")


def show_memory(user_id):
    """Prints the facts Memory Bank has stored for this app and user."""
    client = agentplatform.Client(project=PROJECT, location=LOCATION)
    bank = f"projects/{PROJECT}/locations/{LOCATION}/reasoningEngines/{MEMORY_BANK_ID}"
    print(f"\n----------- MEMORY for {user_id} -----------")
    found = False
    for memory in client.memory_banks.memories.list(name=bank):
        scope = memory.scope or {}
        if scope.get("app_name") == APP_NAME and scope.get("user_id") == user_id:
            print("  -", memory.fact)
            found = True
    if not found:
        print("  (empty)")
    print("--------------------------------------------\n")


# Session 1: Nitish tells the agent about himself.
s1 = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id="nitish"))
chat(s1, "One cold coffee please, less sweet. I'm allergic to peanuts.")
show_memory("nitish")            # empty: chatting doesn't save anything

# The APPLICATION saves session 1 to Memory Bank.
save_to_memory(s1)
show_memory("nitish")            # now Memory Bank has the extracted facts

# Session 2: a new session. The AGENT searches Memory Bank by meaning.
s2 = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id="nitish"))
chat(s2, "Do I have any food restrictions?")
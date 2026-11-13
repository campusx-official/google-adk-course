import asyncio

from dotenv import load_dotenv
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import SqliteMemoryService
from google.genai import types

load_dotenv("memory_agent/.env")

from memory_agent.agent import root_agent

APP_NAME = "memory_demo"

session_service = InMemorySessionService()
# memory_service = InMemoryMemoryService()
memory_service = SqliteMemoryService("sqlite:///cafe_memory.db")

runner = Runner(agent=root_agent, app_name=APP_NAME,
                session_service=session_service, memory_service=memory_service)


def chat(session, text):
    message = types.Content(role="user", parts=[types.Part(text=text)])
    print("\nUSER :", text)
    for event in runner.run(user_id=session.user_id, session_id=session.id,
                            new_message=message):
        if event.is_final_response() and event.content and event.content.parts:
            print("AGENT:", event.content.parts[0].text)


def save_to_memory(session):

    session = asyncio.run(session_service.get_session(
        app_name=APP_NAME, user_id=session.user_id, session_id=session.id))
    
    asyncio.run(memory_service.add_session_to_memory(session))

    print(f"\n>>> saved session {session.id[:8]} to memory")


def save_latest_turn_to_memory(session):
    """Saves only the last 2 events (latest user message + agent reply)."""

    session = asyncio.run(session_service.get_session(
        app_name=APP_NAME, user_id=session.user_id, session_id=session.id))

    asyncio.run(memory_service.add_events_to_memory(
        app_name=APP_NAME,
        user_id=session.user_id,
        session_id=session.id,
        events=session.events[-2:],      # only the most recent 2 events
    ))

    print(f"\n>>> saved latest turn of session {session.id[:8]} to memory")


def show_memory():
    """Prints everything stored in memory, grouped by user and session.
    """
    print("\n----------- MEMORY -----------")
    store = memory_service._session_events   # {(app, user): {session_id: [events]}}
    if not store:
        print("(empty)")
    for (app, user), sessions in store.items():
        print(f"user: {user}")
        for session_id, events in sessions.items():
            print(f"  session {session_id[:8]}:")
            for event in events:
                text = " ".join(p.text for p in event.content.parts if p.text)
                print(f"    [{event.author}] {text}")
    print("------------------------------\n")


s1 = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id="nitish"))
chat(s1, "One cold coffee please, less sweet with no butter as i am allergic.")
save_to_memory(s1)
show_memory()

s2 = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id="nitish"))
chat(s2, "Can i get my usual cold coffeee.")
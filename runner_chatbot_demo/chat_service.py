import asyncio

from dotenv import load_dotenv

load_dotenv("chatbot_agent/.env")  # adk web does this for you; here we do it ourselves

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from chatbot_agent.agent import root_agent

APP_NAME = "chatbot_agent"

# 1. SessionService: where sessions are stored
session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///./sessions.db")

# 2. Runner: connects the agent to the session service
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)


def create_session(user_id: str) -> str:
    session = asyncio.run(
        session_service.create_session(app_name=APP_NAME, user_id=user_id)
    )
    return session.id


def send_message(user_id: str, session_id: str, text: str) -> str:
    message = types.Content(role="user", parts=[types.Part(text=text)])
    reply = ""
    for event in runner.run(user_id=user_id, session_id=session_id, new_message=message):
        if event.is_final_response():
            reply = _event_text(event)
    return reply


def get_messages(user_id: str, session_id: str) -> list[dict]:
    session = asyncio.run(
        session_service.get_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)
    )
    messages = []
    for event in session.events:  # a session's history is a list of events
        text = _event_text(event)
        if text:  # tool calls / tool results have no text, so we skip them
            role = "user" if event.author == "user" else "assistant"
            messages.append({"role": role, "text": text})
    return messages


def list_sessions(user_id: str) -> list[dict]:
    response = asyncio.run(
        session_service.list_sessions(app_name=APP_NAME, user_id=user_id)
    )
    sessions = sorted(response.sessions, key=lambda s: s.last_update_time, reverse=True)

    result = []
    for s in sessions:
        # list_sessions() doesn't include events, so we load each session's history
        messages = get_messages(user_id, s.id)
        title = messages[0]["text"][:40] if messages else "New chat"
        result.append({"id": s.id, "title": title})
    return result


def _event_text(event) -> str:
    if not event.content or not event.content.parts:
        return ""
    return "".join(part.text or "" for part in event.content.parts)
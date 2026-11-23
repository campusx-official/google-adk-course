import warnings
warnings.filterwarnings("ignore", message=r"\[EXPERIMENTAL\]")   # hide ADK's experimental-feature notices

import asyncio

import streamlit as st
from dotenv import load_dotenv

load_dotenv("streaming_bot/.env")

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from streaming_bot.agent import root_agent

APP_NAME = "streaming_bot"
USER_ID = "nitish"


# ---------------------------------------------------------------
# 1. Runner + session (built once, because Streamlit reruns this file on every message)
# ---------------------------------------------------------------
@st.cache_resource
def get_runner():
    session_service = InMemorySessionService()
    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)
    session = asyncio.run(session_service.create_session(app_name=APP_NAME, user_id=USER_ID))
    return runner, session.id

runner, session_id = get_runner()


# ---------------------------------------------------------------
# 2. Stream the reply piece by piece
# ---------------------------------------------------------------
def stream_reply(text: str):
    message = types.Content(role="user", parts=[types.Part(text=text)])

    for event in runner.run(user_id=USER_ID,
                            session_id=session_id,
                            new_message=message,
                            run_config=RunConfig(streaming_mode=StreamingMode.SSE)
                        ):
        # the model decided to call a tool
        if event.get_function_calls() and not event.partial:
            st.toast(f"Calling {event.get_function_calls()[0].name}...")

        # a piece of text
        elif event.partial and event.content:
            piece = event.content.parts[0].text or ""

            if event.author == root_agent.name:     # from the model: part of the reply
                yield piece
            else:                                   # from the tool: a progress update
                st.toast(piece.strip())


# ---------------------------------------------------------------
# 3. Chat UI
# ---------------------------------------------------------------
st.title("Streaming chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

if prompt := st.chat_input("Ask something..."):
    st.chat_message("user").write(prompt)
    reply = st.chat_message("assistant").write_stream(stream_reply(prompt))

    st.session_state.messages.append({"role": "user", "text": prompt})
    st.session_state.messages.append({"role": "assistant", "text": reply})
import warnings
warnings.filterwarnings("ignore", message=r"\[EXPERIMENTAL\]")
import asyncio

from dotenv import load_dotenv

load_dotenv("streaming_bot/.env")  # adk web does this for you; a script must do it itself

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from streaming_bot.agent import root_agent  # <- your existing agent

APP_NAME = "chatbot"
USER_ID = "nitish"

# ---------------------------------------------------------------
# 1. SessionService: where sessions are stored
# ---------------------------------------------------------------
session_service = InMemorySessionService()

# ---------------------------------------------------------------
# 2. Runner: connects the agent to the session service
# ---------------------------------------------------------------
runner = Runner(agent=root_agent,
                app_name=APP_NAME,
                session_service=session_service
            )

# ---------------------------------------------------------------
# 3. Create a session (one conversation)
#    Session services are async, so we wrap the call in asyncio.run()
# ---------------------------------------------------------------
session = asyncio.run(
    session_service.create_session(app_name=APP_NAME,
                                   user_id=USER_ID
                                )
)


# ---------------------------------------------------------------
# 4. Without streaming: wait for the whole reply
# ---------------------------------------------------------------
def ask(session_id: str, text: str):

    print(f"User: {text}")
    message = types.Content(role="user",
                            parts=[types.Part(text=text)]
                        )

    for event in runner.run(user_id=USER_ID,
                            session_id=session_id,
                            new_message=message
                        ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}\n")


# ---------------------------------------------------------------
# 5. With streaming: print each piece as it arrives
# ---------------------------------------------------------------
def ask_streaming(session_id: str, text: str):

    print(f"User: {text}")
    message = types.Content(role="user",
                            parts=[types.Part(text=text)]
                        )

    print("Agent: ", end="")
    for event in runner.run(user_id=USER_ID,
                            session_id=session_id,
                            new_message=message,
                            run_config=RunConfig(streaming_mode=StreamingMode.SSE)     # <- the only new argument
                        ):
        if event.partial and event.content:
            print(event.content.parts[0].text or "", end="", flush=True)
        elif event.get_function_calls():                        # the agent is calling a tool
            print(f"[calling {event.get_function_calls()[0].name}...] ", end="", flush=True)
    print("\n")


# ---------------------------------------------------------------
# Demo
# ---------------------------------------------------------------
print("=== Tool call while streaming ===")
ask_streaming(session.id, "What's the weather in Delhi? Then suggest 3 things to do there today.")
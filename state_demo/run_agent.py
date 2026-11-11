import asyncio

from dotenv import load_dotenv

load_dotenv("state_agent/.env")  # adk web does this for you; a script must do it itself

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from state_agent.agent import root_agent  # <- your existing agent

APP_NAME = "session_agent"
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
def create_session():
    session = asyncio.run(
        session_service.create_session(app_name=APP_NAME,
                                       user_id=USER_ID,
                                       state={"student_name": "Nitish"}
                                    )
    )
    #print(f"STATE at creation: {session.state}")
    return session


# ---------------------------------------------------------------
# 4. Send one message to a session through the Runner
# ---------------------------------------------------------------
def ask(session_id: str, text: str, state_delta: dict | None = None):
    
    print(f"User: {text}")
    message = types.Content(role="user", 
                            parts=[types.Part(text=text)]
                        )

    # event
    for event in runner.run(user_id=USER_ID,
                            session_id=session_id,
                            new_message=message,
                            state_delta=state_delta
                        ):
        if event.is_final_response():
            print(f"Agent: {event.content.parts[0].text}\n")

# ---------------------------------------------------------------
# 5. Look at the session's current state
#    Fetch the session fresh: the object from create_session is a stale copy
# ---------------------------------------------------------------
def show_state(session_id: str):
    session = asyncio.run(
        session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    )
    print(f"STATE: {session.state}\n")

# ---------------------------------------------------------------
# Demo
# ---------------------------------------------------------------
chat_1 = create_session()

ask(chat_1.id, "What is an AI agent?", state_delta={"mode": "beginner"})
ask(chat_1.id, "What is an AI agent?", state_delta={"mode": "advanced"})

show_state(chat_1.id)
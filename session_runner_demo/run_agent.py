import asyncio

from dotenv import load_dotenv

load_dotenv("session_agent/.env")  # adk web does this for you; a script must do it itself

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from session_agent.agent import root_agent  # <- your existing agent

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
        session_service.create_session(app_name=APP_NAME, # session id is automatically generated
                                       user_id=USER_ID
                                    )
    )
    print("New session created")
    print(f"  id:          {session.id}")
    print(f"  app_name:    {session.app_name}")
    print(f"  user_id:     {session.user_id}")
    print(f"  events:      {len(session.events)}\n")
    return session


# ---------------------------------------------------------------
# 4. Send one message to a session through the Runner
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
# Demo
# ---------------------------------------------------------------
print("=== Conversation 1 ===")
chat_1 = create_session()
ask(chat_1.id, "Hi, my name is Nitish")
ask(chat_1.id, "What is my name?")        # same session -> remembers

print("=== Conversation 2 ===")
chat_2 = create_session()
ask(chat_2.id, "What is my name?")        # new session -> doesn't know
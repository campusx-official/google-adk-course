def initialize_student(callback_context):

    print(">>> BEFORE AGENT: INITIALIZING STATE")

    state = callback_context.state

    if not state.get("initialized"):

        state["student_name"] = "Rahul"
        state["student_email"] = "rahul@example.com"

        state["ticket_count"] = 0
        state["last_ticket_id"] = None

        state["initialized"] = True

        print(">>> STUDENT STATE INITIALIZED")

    return None


def inject_personalization(callback_context, llm_request):

    print(">>> INJECTING PERSONALIZATION")

    state = callback_context.state

    name = state.get("student_name", "Student")
    email = state.get("student_email", "Unknown")

    llm_request.append_instructions([
        f"Current student's name: {name}",
        f"Current student's email: {email}"
    ])

    return None


def check_authorization(tool, args, tool_context):

    if tool.name == "get_enrollment_status":

        requested_email = args.get("email", "").lower().strip()

        logged_in_email = tool_context.state.get(
            "student_email", ""
        )

        if requested_email != logged_in_email:

            print(">>> AUTHORIZATION FAILED")

            return {
                "status": "error",
                "message": "You can only access your own enrollment details."
            }

        print(">>> AUTHORIZATION SUCCESSFUL")

    return None



# -----------------------------
# CHECK CACHE - before tool
# -----------------------------

def check_course_cache(tool, args, tool_context):

    if tool.name == "get_courses":

        cached_courses = tool_context.state.get("cached_courses")

        if cached_courses is not None:

            print(">>> CACHE HIT - SKIPPING TOOL")

            return cached_courses

        print(">>> CACHE MISS")

    return None


# -----------------------------
# SAVE TO CACHE - after tool
# -----------------------------

def save_course_cache(tool, args, tool_context, tool_response):

    if tool.name == "get_courses":

        tool_context.state["cached_courses"] = tool_response

        print(">>> COURSE DATA SAVED TO CACHE")

    return None



# -----------------------------
# UPDATE TICKET COUNT
# -----------------------------

def update_ticket_count(tool, args, tool_context, tool_response):

    if tool.name == "create_support_ticket":

        if tool_response.get("status") == "success":

            current_count = tool_context.state.get("ticket_count", 0)

            tool_context.state["ticket_count"] = current_count + 1

            print(">>> TICKET COUNT UPDATED")

    return None



# -----------------------------
# RATE LIMITING
# -----------------------------

def check_ticket_limit(tool, args, tool_context):

    if tool.name == "create_support_ticket":

        ticket_count = tool_context.state.get("ticket_count", 0)

        if ticket_count >= 1:

            print(">>> TICKET LIMIT REACHED")

            return {
                "status": "error",
                "message": "Only 1 support ticket is allowed per session."
            }

        print(">>> TICKET CREATION ALLOWED")

    return None


from google.adk.models import LlmResponse
from google.genai import types


def check_competitor_guardrail(callback_context, llm_request):

    print(">>> CHECKING COMPETITOR GUARDRAIL")

    # Get the latest message
    user_message = llm_request.contents[-1].parts[0].text or ""

    # List of competitors
    competitors = ["andrew ng", "byjus"]

    # Check for competitor names
    if any(name in user_message.lower() for name in competitors):

        print(">>> GUARDRAIL TRIGGERED")

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[
                    types.Part(
                        text="I can only help with CampusX courses and student support."
                    )
                ]
            )
        )

    print(">>> GUARDRAIL PASSED")

    return None



from google.adk.agents import Agent


# -----------------------------------
# TOOL
# -----------------------------------

def get_course_price(course_name: str) -> dict:
    """Get the price of a course."""

    print(f">>> ACTUAL TOOL EXECUTED: {course_name}")

    return {
        "course": course_name,
        "price": 999
    }


# -----------------------------------
# BEFORE TOOL CALLBACK
# -----------------------------------

def before_tool(tool, args, tool_context):

    course = args["course_name"].lower().strip()

    print(f">>> BEFORE TOOL: {course}")

    # CASE 1: SQL - SKIP TOOL
    if course == "sql":
        print(">>> SKIPPING TOOL")

        return {
            "course": "SQL",
            "status": "unavailable",
            "message": "SQL course is currently unavailable"
        }

    # CASE 2: DATA SCIENCE - MODIFY ARGUMENTS
    if course == "data science":
        print(">>> MODIFYING TOOL ARGUMENTS")

        args["course_name"] = "Advanced Data Science"

        return None

    # CASE 3: ALL OTHER COURSES - NORMAL EXECUTION
    print(">>> ALLOWING TOOL EXECUTION")

    return None


# -----------------------------------
# AFTER TOOL CALLBACK
# -----------------------------------

def after_tool(tool, args, tool_context, tool_response):

    print(">>> AFTER TOOL CALLBACK")
    print("Original response:", tool_response)

    course = args["course_name"].lower().strip()

    # CASE 4: MACHINE LEARNING - OVERRIDE RESULT
    if course == "machine learning":
        print(">>> OVERRIDING TOOL RESPONSE")

        return {
            "course": tool_response["course"],
            "price": 799,
            "original_price": 999,
            "discount": 200
        }

    # KEEP ORIGINAL RESPONSE
    return None


# -----------------------------------
# AGENT
# -----------------------------------

root_agent = Agent(
    name="course_agent",
    model="gemini-3.5-flash",
    instruction=(
        "You are a course pricing assistant. "
        "Always call get_course_price when asked "
        "about the price or availability of a course. "
        "Use the tool result to answer the user. "
        "Do not invent prices."
    ),
    tools=[get_course_price],
    before_tool_callback=before_tool,
    after_tool_callback=after_tool
)

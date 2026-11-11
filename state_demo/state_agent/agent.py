from google.adk.agents.llm_agent import Agent
from google.adk.tools import ToolContext

COURSE_FEES = {
    "genai": 4999,
    "google adk": 2999,
    "machine learning": 3999,
}


def save_course_choice(course: str, tool_context: ToolContext) -> dict:
    """Save the course the student wants to take.
    Call this whenever the student chooses a course or changes their choice."""
    tool_context.state["selected_course"] = course.lower()
    return {"status": "saved", "course": course}

def get_fee(tool_context: ToolContext) -> dict:
    """Get the fee of the course the student has selected."""
    course = tool_context.state.get("selected_course")
    if course is None:
        return {"status": "error", "message": "No course selected yet."}
    fee = COURSE_FEES.get(course)
    if fee is None:
        return {"status": "error", "message": f"No fee found for {course}."}
    return {"status": "success", "course": course, "fee_inr": fee}


root_agent = Agent(
    model='gemini-3.5-flash',
    name='state_agent',
    description='A helpful assistant for CampusX students.',
        instruction="""You are the CampusX assistant.
The student's name is {student_name?}.
Greet the student by name.

Explanation level: {mode?}
If an explanation level is set, explain things at that level.

When the student chooses or changes a course, call save_course_choice.
When the student asks about the fee, call get_fee.
Keep answers short.""",
    tools=[save_course_choice, get_fee],
    output_key='final_reply'
)
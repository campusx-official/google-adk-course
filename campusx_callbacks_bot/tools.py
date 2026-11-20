
from google.adk.tools import ToolContext


# -----------------------------
# MOCK DATA
# -----------------------------

COURSES = [
    {"name": "Python", "price": 4999},
    {"name": "Machine Learning", "price": 7999},
    {"name": "AI Engineering", "price": 9999},
]

STUDENTS = {
    "rahul@example.com": {
        "name": "Rahul",
        "enrolled_courses": ["Python", "Machine Learning"]
    },
    "priya@example.com": {
        "name": "Priya",
        "enrolled_courses": ["AI Engineering"]
    }
}


# -----------------------------
# TOOL 1: GET COURSES
# -----------------------------

def get_courses() -> dict:
    """Return available CampusX courses and prices."""

    print(">>> GET COURSES TOOL EXECUTED")

    return {"courses": COURSES}


# -----------------------------
# TOOL 2: CHECK ENROLLMENT
# -----------------------------

def get_enrollment_status(email: str) -> dict:
    """Find student enrollments using their email."""

    print(">>> ENROLLMENT TOOL EXECUTED")

    student = STUDENTS.get(email.lower().strip())

    if not student:
        return {
            "status": "not_found",
            "message": "Student not found"
        }

    return {
        "status": "success",
        "student": student
    }


# -----------------------------
# TOOL 3: CREATE SUPPORT TICKET
# -----------------------------

def create_support_ticket(issue: str,tool_context:ToolContext) -> dict:
    """Create a mock support ticket for an issue."""

    print(">>> CREATE TICKET TOOL EXECUTED")

    count = tool_context.state.get("ticket_count", 0)
    ticket_id = f"TKT-{count + 1:03d}"

    return {
        "status": "success",
        "ticket_id": ticket_id,
        "issue": issue
    }

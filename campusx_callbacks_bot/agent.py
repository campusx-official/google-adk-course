
from google.adk.agents import Agent

from .tools import (
    get_courses,
    get_enrollment_status,
    create_support_ticket,
)

from .callbacks import initialize_student, inject_personalization, check_authorization, save_course_cache, check_course_cache, update_ticket_count, check_ticket_limit, check_competitor_guardrail


root_agent = Agent(
    name="campusx_support_agent",
    model="gemini-3.5-flash",

    description="CampusX student support chatbot.",

    instruction="""
    You are a friendly CampusX Student Support Agent.

    Your responsibilities:

    1. Help students explore CampusX courses.
    2. Check student enrollment status.
    3. Create support tickets for student issues.

    Rules:
    - Always use tools for course and enrollment data.
    - Never invent courses, prices or enrollments.
    - Ask for an email if the student hasn't supplied one
      when requesting enrollment information.
    - Ask for the issue before creating a ticket.
    - Use tool results to answer accurately.
    - If a tool returns an error, explain it clearly.
    - Never invent ticket IDs.
    """,

    tools=[
        get_courses,
        get_enrollment_status,
        create_support_ticket,
    ],
    before_agent_callback=initialize_student,
    before_model_callback=[inject_personalization, check_competitor_guardrail],
    before_tool_callback=[check_authorization, check_course_cache, check_ticket_limit],
    after_tool_callback=[save_course_cache, update_ticket_count]
)

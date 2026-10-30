from typing import Literal
from pydantic import BaseModel, Field
from google.adk import Agent

class Ticket(BaseModel):
    category: Literal["refund", "technical", "course_query", "payment", "other"] = Field(
        description="The main topic of the student's message"
    )
    urgency: Literal["low", "medium", "high"] = Field(
        description="high = blocked right now or upset; medium = needs help soon; low = general question"
    )
    needs_human: bool = Field(
        description="True if a human must handle this: money disputes, anger, or anything unclear"
    )

root_agent = Agent(
    name="ticket_classifier",
    model="gemini-3.5-flash",
    description="Classifies CampusX support messages into tickets.",
    instruction="""You classify support messages sent by CampusX students.
Read the message and fill in the ticket.
Be conservative: if money, anger or confusion is involved, set needs_human to true.""",
    output_schema=Ticket,
    output_key="ticket",
)
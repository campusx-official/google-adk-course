# Google ADK Course

Example agents built with Google's [Agent Development Kit (ADK)](https://google.github.io/adk-docs/) for the CampusX course. Each folder is a standalone agent, starting with a single built-in tool and building up to a multi-tool agent backed by a database.

## Agents

| Folder | What it shows |
| --- | --- |
| `google_agent` | Web search with ADK's built-in `google_search` tool |
| `code_execution_agent` | Writing and running Python with `BuiltInCodeExecutor` |
| `campusx_bot` | Same setup as `code_execution_agent` |
| `world_clock_agent` | A custom function tool (`get_current_time`) for time in any time zone |
| `tavily_search_agent` | Using a LangChain tool (Tavily search) in ADK through `LangchainTool` |
| `combined_tool_agent` | One agent with a function tool, Google Search, code execution and Tavily together |
| `campusx_refund_agent` | A course refund assistant that reads and writes a SQLite database and keeps state between turns |
| `structured_output_agent` | Structured output with `output_schema`: pulls a student's name, email, courses of interest and budget out of an enquiry message |
| `ticket_classifier_agent` | Structured output for classification: sorts support messages into a ticket with category, urgency and whether a human is needed |

All agents use the `gemini-3.5-flash` model.

## Setup

Requires Python 3.11+.

```bash
git clone https://github.com/campusx-official/google-adk-course.git
cd google-adk-course

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### API keys

Each agent folder reads its own `.env` file. These files are not committed, so create one in each agent folder you want to run:

```env
GOOGLE_GENAI_USE_ENTERPRISE=FALSE
GOOGLE_API_KEY=your-gemini-api-key
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

`tavily_search_agent` and `combined_tool_agent` also need a Tavily key from [tavily.com](https://tavily.com):

```env
TAVILY_API_KEY=your-tavily-api-key
```

## Running an agent

From the repository root:

```bash
adk web          # browser UI; pick an agent from the dropdown
adk run world_clock_agent   # chat in the terminal
```

## Refund agent

`campusx_refund_agent` needs its sample database before the first run:

```bash
python campusx_refund_agent/setup_database.py
```

This creates `campusx_refund_agent/campusx.db` with sample courses, students and purchases. The script won't overwrite an existing database; delete `campusx.db` and run it again to reset the data.

Try it with one of the sample student emails, such as `rahul@example.com` or `priya@example.com`.

The agent's tools are in `campusx_refund_agent/tools.py`:

- `get_refund_policy` returns the refund rules: within 7 days of purchase and no more than 20% of the course completed
- `identify_student` looks up a student by email and remembers them for the conversation
- `get_my_enrollments` lists the student's purchases
- `check_refund_eligibility` checks one purchase against the policy
- `request_refund` creates a refund request
- `get_refund_status` shows the status of a refund

This is a demo. No real payments are made.

## Structured output agents

`structured_output_agent` and `ticket_classifier_agent` don't reply in free text. Each one defines a Pydantic model and passes it to the agent as `output_schema`, so every reply is JSON that matches the model. The result is also saved in session state under `output_key`.

| Agent | Schema | State key | Fields |
| --- | --- | --- | --- |
| `structured_output_agent` | `Enquiry` | `enquiry` | `name`, `email`, `interested_in` (GenAI, Data Science, MLOps, Deep Learning, Other), `budget_inr` |
| `ticket_classifier_agent` | `Ticket` | `ticket` | `category` (refund, technical, course_query, payment, other), `urgency` (low, medium, high), `needs_human` |

Example messages to try:

- Enquiry: `Hi, I'm rahul sharma (rahul@example.com). I want to learn GenAI and MLOps, budget around 15k.`
- Ticket: `I paid twice for the Data Science course and nobody is replying. Please fix this now!`
